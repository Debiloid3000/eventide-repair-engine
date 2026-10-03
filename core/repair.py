import re
from pathlib import Path
from typing import List, Tuple, Optional
from core.models import DiagnosticItem, PatchRecord

class AutoRepairEngine:
    def __init__(self, target_dir: str):
        self.target_dir = Path(target_dir).resolve()

    def apply_repair(self, diagnostic: DiagnosticItem) -> Tuple[bool, Optional[PatchRecord]]:
        full_path = Path(diagnostic.file_path)
        if not full_path.is_absolute():
            full_path = self.target_dir / diagnostic.file_path

        if not full_path.exists():
            return False, None

        before_content = full_path.read_text(encoding="utf-8", errors="ignore")

        if diagnostic.code == "CS0246":
            type_name = self._extract_type_from_cs0246(diagnostic.message)
            if type_name:
                suggested_using = self._infer_using_statement(type_name)
                if suggested_using and suggested_using not in before_content:
                    after_content = f"using {suggested_using};\n" + before_content
                    full_path.write_text(after_content, encoding="utf-8")
                    
                    patch = PatchRecord(
                        file_path=str(diagnostic.file_path), operation="ADD_USING",
                        reason=f"Fix {diagnostic.code}: missing type {type_name}",
                        source="AutoRepairEngine", before_content=before_content,
                        after_content=after_content, confidence=0.95
                    )
                    return True, patch

        return False, None

    def _extract_type_from_cs0246(self, msg: str) -> Optional[str]:
        m = re.search(r"'([^']+)'", msg)
        return m.group(1) if m else None

    def _infer_using_statement(self, type_name: str) -> Optional[str]:
        common_map = {
            "EntityUid": "Robust.Shared.GameObjects",
            "Component": "Robust.Shared.GameObjects",
            "EntitySystem": "Robust.Shared.GameObjects",
            "IEntityManager": "Robust.Shared.GameObjects",
            "DataDefinition": "Robust.Shared.Serialization.Manager.Attributes",
            "ViewVariables": "Robust.Shared.ViewVariables",
            "Prototypes": "Robust.Shared.Prototypes",
        }
        return common_map.get(type_name)
