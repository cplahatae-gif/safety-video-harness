from __future__ import annotations

from pathlib import Path

from safety_video_harness.errors import HarnessError
from safety_video_harness.io import read_json
from safety_video_harness.layout import LayoutKey, layout_for_project


def validate_image_to_video_gate(project: Path, estimated_credits: int | None) -> None:
    if estimated_credits is None:
        raise HarnessError("image_to_video approval requires cost disclosure")
    config = read_json(project / "project_config.json")
    if not bool(config.get("external_upload_allowed", False)):
        raise HarnessError("image_to_video approval requires external_upload_allowed=true")
    scenes = _scenes(project)
    if int(scenes.get("clip_count", 0)) <= 0:
        raise HarnessError("image_to_video approval requires clip count greater than 0")
    layout = layout_for_project(project)
    if not layout.read_path(LayoutKey.STORY_VIDEO_PROMPTS).exists():
        raise HarnessError("image_to_video approval requires video_prompts.json")
    _require_approved_images(project, int(scenes.get("keyframe_count", 0)))
    _require_image_qa(project, scenes)


def _scenes(project: Path) -> dict:
    path = layout_for_project(project).read_path(LayoutKey.STORY_SCENES)
    if not path.exists():
        raise HarnessError("image_to_video approval requires story/scenes.json")
    return read_json(path)


def _require_approved_images(project: Path, keyframe_count: int) -> None:
    approved_dir = layout_for_project(project).read_path(LayoutKey.MEDIA_IMAGE_APPROVED)
    missing = [
        f"media/images/approved/sc{index:02d}.png"
        for index in range(1, keyframe_count + 1)
        if not (approved_dir / f"sc{index:02d}.png").exists()
    ]
    if missing:
        raise HarnessError(f"image_to_video approval requires approved image(s): {', '.join(missing)}")


def _require_image_qa(project: Path, scenes: dict) -> None:
    path = layout_for_project(project).read_path(LayoutKey.QA_ROOT) / "image_reviews.json"
    if not path.exists():
        raise HarnessError("image_to_video approval requires image QA")
    payload = read_json(path)
    if bool(payload.get("dry_run", False)):
        raise HarnessError("image_to_video approval requires live image QA, not dry-run image QA")
    reviews = list(payload.get("reviews", []))
    expected = {f"sc{index:02d}" for index in range(1, int(scenes.get("keyframe_count", 0)) + 1)}
    reviewed = {str(review.get("scene_id", "")) for review in reviews}
    missing = sorted(expected - reviewed)
    if missing:
        raise HarnessError(f"image_to_video approval requires image QA coverage for scene(s): {', '.join(missing)}")
    manual_missing = sorted(
        str(review.get("scene_id", ""))
        for review in reviews
        if not _has_manual_visual_review(review)
    )
    if manual_missing:
        raise HarnessError(
            "image_to_video approval requires manual visual image QA for scene(s): "
            + ", ".join(manual_missing)
        )
    blockers = [review for review in reviews if review.get("blocking_issues")]
    if blockers:
        raise HarnessError("image_to_video approval requires image QA without blockers")
    loop_path = layout_for_project(project).read_path(LayoutKey.QA_ROOT) / "image_qa_loop.json"
    if not loop_path.exists():
        raise HarnessError("image_to_video approval requires image QA loop summary")
    loop = read_json(loop_path)
    if not bool(loop.get("passed", False)):
        raise HarnessError("image_to_video approval requires passing image QA loop")


def _has_manual_visual_review(review: dict) -> bool:
    manual = review.get("manual_visual_review")
    return isinstance(manual, dict) and manual.get("status") == "present"
