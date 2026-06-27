from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PACKAGE = ROOT / "app" / "harness" / "package"
sys.path.insert(0, str(PACKAGE))
sys.path.insert(0, str(ROOT))

from safety_video_harness.cli import run_boundary
from safety_video_harness.image_visual_review import build_visual_review
from safety_video_harness.io import read_json
from safety_video_harness.layout import LayoutKey, layout_for_project


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True)
    parser.add_argument("--only")
    parser.add_argument("--write-review", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    def run() -> str:
        project = Path(args.project)
        scenes = read_json(layout_for_project(project).read_path(LayoutKey.STORY_SCENES))
        return build_visual_review(
            project,
            list(scenes.get("scenes", [])),
            args.only,
            bool(args.write_review),
            bool(args.force),
        )

    return run_boundary(run)


if __name__ == "__main__":
    sys.exit(main())
