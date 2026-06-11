from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from safety_video_harness.cli import run_boundary
from safety_video_harness.validation import validate_plan


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("plan")
    args = parser.parse_args()
    return run_boundary(lambda: validate_plan(Path(args.plan)))


if __name__ == "__main__":
    sys.exit(main())
