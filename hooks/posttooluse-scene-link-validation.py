from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from safety_video_harness.errors import HarnessError
from safety_video_harness.scene_links import validate_scene_links


def main() -> int:
    if len(sys.argv) < 2:
        print("scene-link-validation: run scripts/validate_scene_links.py --project <project>")
        return 0
    project = Path(sys.argv[1])
    try:
        print(validate_scene_links(project))
    except HarnessError as exc:
        print(f"scene-link-validation failed: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
