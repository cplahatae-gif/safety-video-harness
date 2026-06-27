from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PACKAGE = ROOT / "app" / "harness" / "package"
sys.path.insert(0, str(PACKAGE))
sys.path.insert(0, str(ROOT))

from safety_video_harness.cli import run_boundary
from safety_video_harness.storyboard_qa import evaluate_storyboard


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True)
    args = parser.parse_args()
    return run_boundary(lambda: evaluate_storyboard(Path(args.project)))


if __name__ == "__main__":
    sys.exit(main())
