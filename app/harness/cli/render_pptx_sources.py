from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PACKAGE = ROOT / "app" / "harness" / "package"
sys.path.insert(0, str(PACKAGE))
sys.path.insert(0, str(ROOT))

from safety_video_harness.cli import run_boundary
from safety_video_harness.project import render_sources


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--mode", choices=["media_extract", "slide_render"], default="media_extract")
    args = parser.parse_args()
    return run_boundary(lambda: render_sources(Path(args.project), bool(args.dry_run), str(args.mode)))


if __name__ == "__main__":
    sys.exit(main())
