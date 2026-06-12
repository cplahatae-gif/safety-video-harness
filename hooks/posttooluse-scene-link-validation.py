"""PostToolUse hook (matcher: Write|Edit|MultiEdit).

When storyboard/scenes.json or prompts/video_prompts.json changes, runs the
sliding-chain scene-link validation for that project. A failure exits 2 so the
violation is fed back to Claude.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from safety_video_harness.errors import HarnessError
from safety_video_harness.scene_links import validate_scene_links

WATCHED = {"scenes.json", "video_prompts.json"}


def _project_root(file_path: Path) -> Path | None:
    for parent in file_path.parents:
        if (parent / "project_config.json").exists():
            return parent
    return None


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    file_path = Path(str(payload.get("tool_input", {}).get("file_path", "")))
    if file_path.name not in WATCHED:
        return 0
    project = _project_root(file_path)
    if project is None:
        return 0
    if not (project / "prompts" / "video_prompts.json").exists():
        return 0
    try:
        validate_scene_links(project)
    except HarnessError as exc:
        print(f"scene-link-validation failed: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
