from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from safety_video_harness.cli import run_boundary
from safety_video_harness.generation import generate_images


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--only")
    parser.add_argument("--regenerate", action="store_true")
    args = parser.parse_args()
    return run_boundary(
        lambda: generate_images(
            Path(args.project),
            bool(args.dry_run),
            bool(args.live),
            args.only,
            bool(args.regenerate),
        )
    )


if __name__ == "__main__":
    sys.exit(main())
