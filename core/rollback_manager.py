from pathlib import Path
from typing import List
from core.models import PatchRecord

class RollbackManager:
    def __init__(self, workspace):
        self.workspace = workspace

    def revert_patch(self, patch: PatchRecord) -> bool:
        target_file = Path(self.workspace.target_dir) / patch.file_path
        if not target_file.exists():
            return False
        try:
            target_file.write_text(patch.before_content, encoding="utf-8")
            patch.validation = "rolled_back"
            return True
        except Exception:
            return False

    def revert_iteration_patches(self, patches: List[PatchRecord]) -> None:
        for patch in reversed(patches):
            self.revert_patch(patch)
