from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PACKAGE = ROOT / "app" / "harness" / "package"
sys.path.insert(0, str(PACKAGE))
sys.path.insert(0, str(ROOT))

from safety_video_harness.cli import run_boundary
from safety_video_harness.generation import generate_seedance


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--execute-paid", action="store_true")
    parser.add_argument("--test-seconds", type=int, default=10)
    parser.add_argument("--max-attempts", type=int, default=3)
    parser.add_argument("--plan-only", action="store_true")
    parser.add_argument("--validation-run", action="store_true")
    args = parser.parse_args()
    return run_boundary(
        lambda: generate_seedance(
            Path(args.project),
            bool(args.dry_run),
            bool(args.live),
            bool(args.execute_paid),
            int(args.test_seconds),
            int(args.max_attempts),
            bool(args.plan_only),
            bool(args.validation_run),
        )
    )


if __name__ == "__main__":
    sys.exit(main())
