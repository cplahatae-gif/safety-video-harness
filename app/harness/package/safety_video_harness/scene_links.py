from __future__ import annotations

from pathlib import Path

from safety_video_harness.errors import HarnessError
from safety_video_harness.io import read_json, write_json
from safety_video_harness.layout import LayoutKey, layout_for_project


def validate_scene_links(project: Path) -> str:
    scenes_payload = read_json(layout_for_project(project).read_path(LayoutKey.STORY_SCENES))
    scenes = list(scenes_payload.get("scenes", []))
    if not scenes:
        report = {
            "passed": False,
            "reviews": [],
            "rule": "Each clip must use scNN as start and scNN+1 as end so adjacent clips share keyframes.",
            "blockers": ["no storyboard scenes"],
        }
        write_json(project / "qa" / "scene_link_reviews.json", report)
        raise HarnessError("no storyboard scenes for sliding chain validation")
    reviews = [_review_scene_link(index, scene) for index, scene in enumerate(scenes, start=1)]
    blockers = [review for review in reviews if review["blocking_issues"]]
    report = {
        "passed": not blockers,
        "reviews": reviews,
        "rule": "Each clip must use scNN as start and scNN+1 as end so adjacent clips share keyframes.",
    }
    write_json(project / "qa" / "scene_link_reviews.json", report)
    if blockers:
        first = blockers[0]
        raise HarnessError(f"sliding chain mismatch: {first['scene_id']}")
    return f"validated {len(reviews)} scene link(s)"


def _review_scene_link(index: int, scene: dict) -> dict:
    scene_id = str(scene.get("id", f"sc{index:02d}"))
    expected_scene_id = f"sc{index:02d}"
    expected_start = f"media/images/approved/sc{index:02d}.png"
    expected_end = f"media/images/approved/sc{index + 1:02d}.png"
    old_start = f"images/approved/sc{index:02d}.png"
    old_end = f"images/approved/sc{index + 1:02d}.png"
    issues = []
    if scene_id != expected_scene_id:
        issues.append(f"expected scene id {expected_scene_id}, got {scene_id}")
    if scene.get("start_keyframe") not in {expected_start, old_start}:
        issues.append(f"expected start_keyframe {expected_start} or {old_start}, got {scene.get('start_keyframe')}")
    if scene.get("end_keyframe") not in {expected_end, old_end}:
        issues.append(f"expected end_keyframe {expected_end} or {old_end}, got {scene.get('end_keyframe')}")
    score = 5 if not issues else 0
    return {
        "scene_id": scene_id,
        "start_keyframe_score": score,
        "end_keyframe_score": score,
        "story_flow_score": score,
        "blocking_issues": issues,
        "decision": "pass" if not issues else "fix_storyboard_chain",
    }
