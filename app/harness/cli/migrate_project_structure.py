from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PACKAGE = ROOT / "app" / "harness" / "package"
sys.path.insert(0, str(PACKAGE))
sys.path.insert(0, str(ROOT))

from safety_video_harness.cli import run_boundary
from safety_video_harness.project_migration import migrate_project_structure


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--evidence-dir")
    parser.add_argument("--allow-overwrite-unapproved", action="store_true")
    args = parser.parse_args()
    evidence_dir = Path(args.evidence_dir) if args.evidence_dir else None
    return run_boundary(
        lambda: migrate_project_structure(
            Path(args.project),
            dry_run=bool(args.dry_run),
            write=bool(args.write),
            evidence_dir=evidence_dir,
            allow_overwrite_unapproved=bool(args.allow_overwrite_unapproved),
        )
    )


if __name__ == "__main__":
    sys.exit(main())
