from __future__ import annotations

from pathlib import Path

from safety_video_harness.io import read_json, write_json
from safety_video_harness.layout import LayoutKey, layout_for_project
from safety_video_harness.style_guides import selected_style_prompt_block


def prepare_fast_image_draft(project: Path) -> str:
    layout = layout_for_project(project)
    scenes_payload = read_json(layout.read_path(LayoutKey.STORY_SCENES))
    scenes = list(scenes_payload.get("scenes", []))
    selected = _selected_scenes(scenes)
    style = selected_style_prompt_block(project)
    jobs = [_job(scene, style) for scene in selected]
    payload = {
        "execution_mode": "fast_draft_manual_imagegen",
        "status": "pending_imagegen",
        "instruction": (
            "Fast draft only. Generate these few keyframes with Codex built-in imagegen, "
            "copy outputs into each output path, then make a contact sheet. "
            "Skip Gate approval, RALPH, asset-lock production checks, and video approval until the user accepts the direction."
        ),
        "jobs": jobs,
    }
    write_json(layout.write_path(LayoutKey.STORY_IMAGEGEN_JOBS), payload)
    write_json(layout.write_path(LayoutKey.STORY_IMAGE_PROMPTS), {"dry_run": True, "fast_draft": True, "plans": jobs})
    return f"fast draft prepared {len(jobs)} image prompt(s)"


def _selected_scenes(scenes: list[dict]) -> list[dict]:
    if len(scenes) <= 3:
        return scenes
    indexes = sorted({0, len(scenes) // 2, len(scenes) - 1})
    return [scenes[index] for index in indexes]


def _job(scene: dict, style: str) -> dict:
    scene_id = str(scene["id"])
    prompt = "\n".join(
        [
            "Create one fast draft keyframe for a safety training video.",
            f"Scene ID: {scene_id}.",
            f"Visual action: {scene.get('visual_action_ko', '')}",
            f"Image prompt: {scene.get('image_prompt_en', '')}",
            "Style reference:",
            style,
            "Draft constraints: 16:9, no readable generated text, no logos, no injury, no gore.",
        ]
    )
    return {
        "scene_id": scene_id,
        "tool": "codex_builtin_imagegen",
        "status": "pending_imagegen",
        "prompt": prompt,
        "output": f"media/images/draft/{scene_id}_v001.png",
        "preserve_project_output": True,
        "fast_draft": True,
    }
