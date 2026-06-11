from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from safety_video_harness.cli import run_boundary
from safety_video_harness.costs import estimate_video_cost


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True)
    parser.add_argument("--estimated-credits", required=True, type=int)
    args = parser.parse_args()
    return run_boundary(lambda: estimate_video_cost(Path(args.project), int(args.estimated_credits)))


if __name__ == "__main__":
    sys.exit(main())
