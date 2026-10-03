import subprocess
from pathlib import Path
from typing import Tuple

class SolutionBuilder:
    def __init__(self, target_dir: str, configuration: str = "Debug"):
        self.target_dir = Path(target_dir).resolve()
        self.configuration = configuration

    def build(self) -> Tuple[bool, str]:
        sln_files = list(self.target_dir.glob("*.sln")) + list(self.target_dir.glob("*.slnx"))
        if not sln_files:
            return False, "Error: No .sln or .slnx file found in target directory."
        cmd = ["dotnet", "build", str(sln_files[0]), "-c", self.configuration, "--nologo", "-v", "m"]
        res = subprocess.run(cmd, cwd=self.target_dir, capture_output=True, text=True)
        return res.returncode == 0, res.stdout
