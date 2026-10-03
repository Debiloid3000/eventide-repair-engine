import subprocess
import shutil
import time
from pathlib import Path
from typing import List

class WorkspaceManager:
    def __init__(self, target_dir: str, work_dir: str = ".repair_workspace"):
        self.target_dir = Path(target_dir).resolve()
        self.workspace_dir = self.target_dir / work_dir
        self.sources_dir = self.workspace_dir / "sources"
        self.checkpoints_dir = self.workspace_dir / "checkpoints"
        self.reports_dir = self.target_dir / "reports"
        self._ensure_dirs()

    def _ensure_dirs(self):
        self.sources_dir.mkdir(parents=True, exist_ok=True)
        self.checkpoints_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def get_git_status(self) -> List[str]:
        res = subprocess.run(["git", "status", "--porcelain"], cwd=self.target_dir, capture_output=True, text=True)
        if res.returncode == 0:
            return [line.strip() for line in res.stdout.splitlines() if line.strip()]
        return []

    def create_checkpoint(self, tag: str) -> Path:
        timestamp = int(time.time())
        cp_path = self.checkpoints_dir / f"checkpoint_{tag}_{timestamp}"
        cp_path.mkdir(parents=True, exist_ok=True)
        
        modified_files = self.get_dirty_files()
        for rel_file in modified_files:
            src = self.target_dir / rel_file
            if src.is_file():
                dst = cp_path / rel_file
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
        return cp_path

    def get_dirty_files(self) -> List[str]:
        status_lines = self.get_git_status()
        dirty = []
        for line in status_lines:
            parts = line.split(maxsplit=1)
            if len(parts) == 2:
                dirty.append(parts[1])
        return dirty
