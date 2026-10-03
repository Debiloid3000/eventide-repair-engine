import json
import time
from pathlib import Path
from typing import List, Dict
from core.models import (
    ExecutionMode, ExecutionStatus, FailedAdaptation, 
    ResourceResolutionRecord, ProvenanceRecord
)

class ReportManager:
    def __init__(self, reports_dir: Path):
        self.reports_dir = reports_dir
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.timestamp = int(time.time())

    def generate_all_reports(self, mode: ExecutionMode, status: ExecutionStatus, initial_errors: int,
                             fixed_errors: int, remaining_errors: int, failed_adaptations: List[FailedAdaptation],
                             resource_records: List[ResourceResolutionRecord], provenance_records: List[ProvenanceRecord]) -> Dict[str, Path]:
        generated = {}
        
        # Summary MD
        summary_md_path = self.reports_dir / f"repair_summary_{self.timestamp}.md"
        summary_md_path.write_text(f"""# REPAIR SUMMARY
- Mode: {mode.name}
- Status: {status.value}
- Init Errors: {initial_errors}
- Fixed: {fixed_errors}
- Remaining: {remaining_errors}
""", encoding="utf-8")
        generated["summary_md"] = summary_md_path

        # Failed Adaptations MD
        failed_md_path = self.reports_dir / f"failed_adaptations_{self.timestamp}.md"
        lines = ["# FAILED ADAPTATIONS"]
        for fa in failed_adaptations:
            lines.append(f"\nFILE: `{fa.file_path}`\nPROBLEM: {fa.problem}\nREASON: {fa.reason}\nCODE:\n{fa.failed_code}\n")
        failed_md_path.write_text("\n".join(lines), encoding="utf-8")
        generated["failed_adaptations_md"] = failed_md_path

        # Resource Resolution MD
        res_md_path = self.reports_dir / f"resource_resolution_{self.timestamp}.md"
        rlines = ["# RESOURCE RESOLUTION"]
        for r in resource_records:
            rlines.append(f"\nFILE: {r.file_path}\nREF: {r.original_reference}\nRESULT: {r.result}\nACTION: {r.action_taken}")
        res_md_path.write_text("\n".join(rlines), encoding="utf-8")
        generated["resource_resolution_md"] = res_md_path

        # JSONs
        json_path = self.reports_dir / f"repair_summary_{self.timestamp}.json"
        json_path.write_text(json.dumps({
            "status": status.value, "initial": initial_errors, "fixed": fixed_errors, "rem": remaining_errors
        }, indent=2), encoding="utf-8")
        generated["summary_json"] = json_path

        prov_path = self.reports_dir / f"port_provenance_{self.timestamp}.json"
        prov_path.write_text(json.dumps([{"path": p.target_path, "op": p.operation} for p in provenance_records], indent=2), encoding="utf-8")
        generated["provenance_json"] = prov_path

        return generated
