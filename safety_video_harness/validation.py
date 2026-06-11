from __future__ import annotations

import re
from pathlib import Path

from safety_video_harness.errors import HarnessError
from safety_video_harness.io import read_json

KOREAN_RE = re.compile(r"[가-힣]")


def validate_plan(path: Path) -> str:
    content = path.read_text(encoding="utf-8")
    missing = [section for section in ["## Mission", "## End Conditions", "## Budgets"] if section not in content]
    if missing:
        raise HarnessError(f"PLAN.md missing required section(s): {', '.join(missing)}")
    if "paid_calls_in_loop: 0" not in content:
        raise HarnessError("PLAN.md must set paid_calls_in_loop: 0")
    return "plan valid"


def validate_project(project: Path) -> str:
    scenes_path = project / "storyboard" / "scenes.json"
    if not scenes_path.exists():
        raise HarnessError("storyboard/scenes.json is missing")
    scenes = read_json(scenes_path)
    errors: list[str] = []
    for scene in scenes.get("scenes", []):
        scene_id = str(scene.get("id", "unknown"))
        _validate_scene(scene_id, scene, errors)
    if errors:
        raise HarnessError("\n".join(errors))
    return "project valid"


def _validate_scene(scene_id: str, scene: dict, errors: list[str]) -> None:
    citations = scene.get("source_citations", [])
    if not citations:
        errors.append(f"{scene_id}: missing source citation")
    if "narration_ko" in scene:
        errors.append(f"{scene_id}: narration_ko is not allowed")
    if "narration_char_limit" in scene:
        errors.append(f"{scene_id}: narration_char_limit is not allowed")
    subtitle = str(scene.get("subtitle_ko", ""))
    if not subtitle:
        errors.append(f"{scene_id}: subtitle_ko is required")
    if len(subtitle) > 32:
        errors.append(f"{scene_id}: subtitle_ko exceeds 32 characters")
    prompt = str(scene.get("image_prompt_en", ""))
    if KOREAN_RE.search(prompt):
        errors.append(f"{scene_id}: image_prompt_en contains Korean text")
    if "text" not in prompt.lower():
        errors.append(f"{scene_id}: image prompt must explicitly forbid text")
