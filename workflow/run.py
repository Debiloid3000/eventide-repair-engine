import os, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from core.config import EngineConfig
from core.orchestrator import CoreEngineOrchestrator
from core.models import ExecutionStatus

def write_github_output(name: str, value: str):
    if gh_output := os.getenv("GITHUB_OUTPUT"):
        with open(gh_output, "a", encoding="utf-8") as f: f.write(f"{name}={value}\n")

def emit_github_annotation(severity: str, file: str, line: int, title: str, message: str):
    print(f"::{severity} file={file},line={line},title={title}::{message}")

def main():
    print("[WORKFLOW] Initializing...")
    cfg = EngineConfig()
    cfg.mode = int(os.getenv("INPUT_MODE", "1"))
    cfg.target_dir = os.getenv("INPUT_TARGET", ".")
    cfg.max_iterations = int(os.getenv("INPUT_MAX_ITERATIONS", "10"))
    cfg.dry_run = os.getenv("INPUT_DRY_RUN", "false").lower() == "true"
    cfg.configuration = os.getenv("INPUT_CONFIGURATION", "Debug")

    orchestrator = CoreEngineOrchestrator(cfg)
    results = orchestrator.execute()

    write_github_output("status", results["status"].value)
    write_github_output("fixed_errors", str(results["fixed_errors"]))
    write_github_output("remaining_errors", str(results["remaining_errors"]))

    if results["remaining_errors"] > 0:
        emit_github_annotation("error", "Solution", 1, "Build Failures", f"Errors remaining: {results['remaining_errors']}")

    sys.exit(0 if results["status"] in (ExecutionStatus.SUCCESS, ExecutionStatus.SUCCESS_WITH_REVIEW) else (1 if results["status"] == ExecutionStatus.PARTIAL_SUCCESS else 2))

if __name__ == "__main__":
    main()
