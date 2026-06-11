from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from safety_video_harness.cli import run_boundary
from safety_video_harness.video_inspection import inspect_video


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True)
    parser.add_argument("--clip", required=True)
    parser.add_argument("--tool", choices=["scenelens", "video-frame-analysis", "understand-video"], required=True)
    parser.add_argument("--no-transcript", action="store_true")
    args = parser.parse_args()
    return run_boundary(
        lambda: inspect_video(
            Path(args.project),
            Path(args.clip),
            str(args.tool),
            bool(args.no_transcript),
        )
    )


if __name__ == "__main__":
    sys.exit(main())
