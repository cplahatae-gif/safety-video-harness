from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from safety_video_harness.cli import run_boundary
from safety_video_harness.storyboard import plan_storyboard


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True)
    parser.add_argument("--duration", type=int, default=30)
    parser.add_argument("--image-density", choices=["normal", "high", "very_high"], default="normal")
    args = parser.parse_args()
    return run_boundary(lambda: plan_storyboard(Path(args.project), int(args.duration), str(args.image_density)))


if __name__ == "__main__":
    sys.exit(main())
