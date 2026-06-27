from __future__ import annotations

from pathlib import Path

from safety_video_harness.io import read_json, write_json
from safety_video_harness.layout import LayoutKey, layout_for_project


def write_story_video_alignment(project: Path) -> str:
    layout = layout_for_project(project)
    scenes = read_json(layout.read_path(LayoutKey.STORY_SCENES))
    reviews = []
    for scene in list(scenes.get("scenes", [])):
        scene_id = str(scene.get("id", ""))
        clip = layout.read_path(LayoutKey.MEDIA_VIDEO_CLIPS) / f"{scene_id}_{_next_scene_id(scene_id)}.mp4"
        start = project / str(scene.get("start_keyframe", ""))
        end = project / str(scene.get("end_keyframe", ""))
        blockers = []
        if not start.exists():
            blockers.append(f"missing start keyframe: {scene.get('start_keyframe', '')}")
        if not end.exists():
            blockers.append(f"missing end keyframe: {scene.get('end_keyframe', '')}")
        if not clip.exists():
            blockers.append(f"missing clip: {clip.relative_to(project)}")
        reviews.append(
            {
                "scene_id": scene_id,
                "clip": str(clip.relative_to(project)),
                "start_keyframe": str(scene.get("start_keyframe", "")),
                "end_keyframe": str(scene.get("end_keyframe", "")),
                "subtitle_ko": str(scene.get("subtitle_ko", scene.get("caption_ko", ""))),
                "blocking_issues": blockers,
                "decision": "ready_for_visual_review" if not blockers else "missing_alignment_artifact",
            }
        )
    report = {"passed": all(not item["blocking_issues"] for item in reviews), "reviews": reviews}
    write_json(project / "qa" / "story_video_alignment.json", report)
    return f"wrote story-video alignment review for {len(reviews)} scene(s)"


def _next_scene_id(scene_id: str) -> str:
    if not scene_id.startswith("sc"):
        return "next"
    try:
        return f"sc{int(scene_id[2:]) + 1:02d}"
    except ValueError:
        return "next"
