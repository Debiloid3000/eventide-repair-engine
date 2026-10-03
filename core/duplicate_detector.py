import re
from pathlib import Path
from typing import Dict, Set
from core.models import DuplicateType

class DuplicateDetector:
    def __init__(self, target_dir: str):
        self.target_dir = Path(target_dir).resolve()
        self.eventide_symbols = self._index_eventide_symbols()

    def _index_eventide_symbols(self) -> Dict[str, Set[str]]:
        indexed = {"classes": set(), "components": set(), "systems": set()}
        for p in self.target_dir.glob("Content.*/**/*.cs"):
            content = p.read_text(encoding="utf-8", errors="ignore")
            classes = re.findall(r'class\s+([A-Za-z0-9_]+)', content)
            for cls in classes:
                indexed["classes"].add(cls)
                if cls.endswith("Component"):
                    indexed["components"].add(cls)
                if cls.endswith("System"):
                    indexed["systems"].add(cls)
        return indexed

    def classify_duplicate(self, symbol_name: str, symbol_code: str) -> DuplicateType:
        if symbol_name in self.eventide_symbols["classes"]:
            return DuplicateType.EXACT_DUPLICATE
        core_concept = re.sub(r'^(Automatic|Genesis|Custom|Legacy)', '', symbol_name)
        for existing in self.eventide_symbols["classes"]:
            if core_concept in existing and len(core_concept) > 5:
                return DuplicateType.FUNCTIONAL_DUPLICATE
        return DuplicateType.MISSING
