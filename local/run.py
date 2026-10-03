import argparse, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from core.config import EngineConfig
from core.orchestrator import CoreEngineOrchestrator

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", type=int, choices=[1, 2], default=1)
    parser.add_argument("--target", type=str, default=".")
    parser.add_argument("--config", type=str, default="repair_config.json")
    parser.add_argument("--max-iterations", type=int, default=10)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    cfg = EngineConfig.load_from_file(args.config)
    cfg.mode = args.mode; cfg.target_dir = args.target; cfg.max_iterations = args.max_iterations; cfg.dry_run = args.dry_run

    print(f"[LOCAL] Running in MODE {cfg.mode}")
    orchestrator = CoreEngineOrchestrator(cfg)
    results = orchestrator.execute()
    print(f"Status: {results['status'].value} | Fixed: {results['fixed_errors']} | Remaining: {results['remaining_errors']}")
    sys.exit(0 if results["remaining_errors"] == 0 else 1)

if __name__ == "__main__":
    main()
