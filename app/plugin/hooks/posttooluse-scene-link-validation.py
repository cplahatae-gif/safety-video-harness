from __future__ import annotations

import sys
from pathlib import Path

from hook_payload import hook_tokens
from hook_paths import repo_root

ROOT = repo_root()
sys.path.insert(0, str(ROOT / "app" / "harness" / "package"))
sys.path.insert(0, str(ROOT))

from safety_video_harness.errors import HarnessError
from safety_video_harness.scene_links import validate_scene_links


def _project_path(args: list[str]) -> Path | None:
    if "--project" in args:
        index = args.index("--project") + 1
        if index < len(args):
            return Path(args[index])
        return None
    if args:
        return Path(args[0])
    return None


def main() -> int:
    project = _project_path(hook_tokens(sys.argv[1:]))
    if project is None:
        print("scene-link-validation: run scripts/validate_scene_links.py --project <project>")
        return 0
    try:
        print(validate_scene_links(project))
    except HarnessError as exc:
        print(f"scene-link-validation failed: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
