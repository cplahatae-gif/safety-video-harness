from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PACKAGE = ROOT / "app" / "harness" / "package"
sys.path.insert(0, str(PACKAGE))
sys.path.insert(0, str(ROOT))

from safety_video_harness.cli import run_boundary
from safety_video_harness.video_qa import validate_video_outputs


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True)
    parser.add_argument("--expected-clips", type=int, required=True)
    parser.add_argument("--clip")
    args = parser.parse_args()
    return run_boundary(lambda: validate_video_outputs(Path(args.project), int(args.expected_clips), args.clip))


if __name__ == "__main__":
    sys.exit(main())
