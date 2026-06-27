from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PACKAGE = ROOT / "app" / "harness" / "package"
sys.path.insert(0, str(PACKAGE))
sys.path.insert(0, str(ROOT))

from safety_video_harness.cli import run_boundary
from safety_video_harness.omo_ralph import build_omo_image_ralph_plan


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True)
    parser.add_argument("--only")
    args = parser.parse_args()
    return run_boundary(lambda: build_omo_image_ralph_plan(Path(args.project), args.only))


if __name__ == "__main__":
    sys.exit(main())
