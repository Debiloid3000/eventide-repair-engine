# core/genesis_porter.py
from pathlib import Path
from typing import List, Tuple
from core.models import ProvenanceRecord, FailedAdaptation, DuplicateType
from core.duplicate_detector import DuplicateDetector
from core.adaptation_engine import AdaptationEngine

class GenesisPorter:
    """
    FEATURE-CENTRIC PORTING ENGINE.
    Переносит минимально необходимый набор файлов под конкретную фичу.
    Запрещено копировать Genesis целиком!
    """
    def __init__(self, workspace, duplicate_detector: DuplicateDetector, adaptation_engine: AdaptationEngine):
        self.workspace = workspace
        self.dup_detector = duplicate_detector
        self.adapter = adaptation_engine

    def port_feature(self, feature_name: str, genesis_files: List[str]) -> Tuple[List[ProvenanceRecord], List[FailedAdaptation]]:
        provenance_list = []
        failed_list = []

        genesis_root = self.workspace.sources_dir / "genesis"
        
        for rel_path in genesis_files:
            src_file = genesis_root / rel_path
            dst_file = Path(self.workspace.target_dir) / rel_path

            if not src_file.exists():
                failed_list.append(FailedAdaptation(
                    file_path=rel_path,
                    source_path=str(src_file),
                    target_path=str(dst_file),
                    operation="PORT",
                    problem="SOURCE_FILE_NOT_FOUND",
                    failed_code="",
                    target_context="",
                    expected_adaptation="Copy file from Genesis",
                    reason="Genesis source repository is missing the requested file."
                ))
                continue

            symbol_name = src_file.stem
            symbol_content = src_file.read_text(encoding="utf-8", errors="ignore")
            dup_type = self.dup_detector.classify_duplicate(symbol_name, symbol_content)

            if dup_type in (DuplicateType.EXACT_DUPLICATE, DuplicateType.FUNCTIONAL_DUPLICATE):
                # Пропускаем перенос дубликата
                continue

            # Адаптация кода Genesis под актуальный API Eventide
            adapted_code, success, reason = self.adapter.adapt_code(symbol_content, rel_path)

            if not success:
                failed_list.append(FailedAdaptation(
                    file_path=rel_path,
                    source_path=str(src_file),
                    target_path=str(dst_file),
                    operation="ADAPT_AND_PORT",
                    problem="API_ADAPTATION_FAILED",
                    failed_code=symbol_content[:300],
                    target_context=adapted_code[:300],
                    expected_adaptation="Adapt obsolete Genesis API calls to current Eventide RobustToolbox API",
                    reason=reason
                ))
                continue

            # Записываем адаптированный файл в Eventide
            dst_file.parent.mkdir(parents=True, exist_ok=True)
            dst_file.write_text(adapted_code, encoding="utf-8")

            provenance_list.append(ProvenanceRecord(
                source_repo="BrigChill3000/genesis-station-14",
                source_commit="HEAD",
                source_path=rel_path,
                source_symbol=symbol_name,
                target_path=rel_path,
                target_symbol=symbol_name,
                operation="PORT_AND_ADAPT",
                adaptation_details="Adapted Genesis API to Eventide/Space-Syndicate baseline",
                dependencies=[],
                validated=True
            ))

        return provenance_list, failed_list
