from pathlib import Path
from typing import Dict, Any, List
from core.config import EngineConfig
from core.models import ExecutionMode, ExecutionStatus, FailedAdaptation
from core.workspace import WorkspaceManager
from core.builder import SolutionBuilder
from core.diagnostics import DiagnosticParser
from core.repair import AutoRepairEngine
from core.duplicate_detector import DuplicateDetector
from core.genesis_porter import GenesisPorter
from core.adaptation_engine import AdaptationEngine
from core.resource_resolver import ResourceReferenceResolver
from core.rollback_manager import RollbackManager
from core.report_manager import ReportManager

class CoreEngineOrchestrator:
    def __init__(self, config: EngineConfig):
        self.config = config
        self.workspace = WorkspaceManager(config.target_dir)
        self.builder = SolutionBuilder(config.target_dir, config.configuration)
        self.diag_parser = DiagnosticParser()
        self.repair_engine = AutoRepairEngine(config.target_dir)
        self.dup_detector = DuplicateDetector(config.target_dir)
        self.adapter = AdaptationEngine()
        self.porter = GenesisPorter(self.workspace, self.dup_detector, self.adapter)
        self.res_resolver = ResourceReferenceResolver(config.target_dir)
        self.rollback_mgr = RollbackManager(self.workspace)
        self.report_mgr = ReportManager(self.workspace.reports_dir)

    def execute(self) -> Dict[str, Any]:
        mode = ExecutionMode(self.config.mode)
        checkpoint = self.workspace.create_checkpoint(f"mode_{mode.value}")

        build_success, stdout = self.builder.build()
        diagnostics = self.diag_parser.parse_output(stdout)
        initial_errors = len([d for d in diagnostics if d.severity == "error"])
        fixed_errors = 0

        failed_adaptations = []
        provenance_records = []
        resource_records = []

        for diag in diagnostics:
            if diag.severity == "error":
                repaired, patch = self.repair_engine.apply_repair(diag)
                if repaired: fixed_errors += 1

        if mode == ExecutionMode.REPAIR_CLONE_ADAPT:
            prov, failed = self.porter.port_feature("TargetFeature", [])
            provenance_records.extend(prov)
            failed_adaptations.extend(failed)
            
            for proto_file in Path(self.config.target_dir).glob("Resources/Prototypes/**/*.yml"):
                resource_records.extend(self.res_resolver.fix_prototype_file_resources(proto_file))

        final_success, final_stdout = self.builder.build()
        final_diagnostics = self.diag_parser.parse_output(final_stdout)
        remaining_errors = len([d for d in final_diagnostics if d.severity == "error"])

        status = ExecutionStatus.SUCCESS
        if remaining_errors > 0:
            status = ExecutionStatus.PARTIAL_SUCCESS if fixed_errors > 0 else ExecutionStatus.FAILED

        reports = self.report_mgr.generate_all_reports(
            mode, status, initial_errors, fixed_errors, remaining_errors, 
            failed_adaptations, resource_records, provenance_records
        )

        return {
            "status": status, "initial_errors": initial_errors, "fixed_errors": fixed_errors,
            "remaining_errors": remaining_errors, "reports": reports,
            "failed_adaptations_count": len(failed_adaptations)
        }
