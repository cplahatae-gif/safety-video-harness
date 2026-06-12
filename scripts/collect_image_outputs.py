from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from safety_video_harness.cli import run_boundary
from safety_video_harness.imagegen_jobs import collect_image_outputs


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True)
    parser.add_argument("--source-dir", required=True)
    args = parser.parse_args()
    return run_boundary(lambda: collect_image_outputs(Path(args.project), Path(args.source_dir)))


if __name__ == "__main__":
    sys.exit(main())
