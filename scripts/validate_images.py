from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from safety_video_harness.cli import run_boundary
from safety_video_harness.generation import validate_images


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--only")
    args = parser.parse_args()
    return run_boundary(lambda: validate_images(Path(args.project), bool(args.dry_run), args.only))


if __name__ == "__main__":
    sys.exit(main())
