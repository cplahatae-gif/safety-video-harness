from __future__ import annotations

from pathlib import Path

from safety_video_harness.asset_lock import asset_lock_prompt_block, build_asset_lock_manifest
from safety_video_harness.errors import HarnessError
from safety_video_harness.assets import load_reference_assets, reference_assets_prompt_block
from safety_video_harness.evaluation_rounds import previous_blocking_issues
from safety_video_harness.gates import require_gate
from safety_video_harness.image_qa import (
    build_loop_summary,
    dry_run_review,
    review_scene_image,
)
from safety_video_harness.image_evaluation_flow import record_image_evaluation_rounds
from safety_video_harness.imagegen_jobs import build_imagegen_jobs
from safety_video_harness.io import read_json, write_json
from safety_video_harness.layout import LayoutKey, layout_for_project
from safety_video_harness.prompt_contract import build_final_image_prompt_plan, build_image_prompt_plan, build_video_prompt_plan
from safety_video_harness.prompt_team import ensure_image_prompt_team_plan, prompt_team_prompt_block
from safety_video_harness.scene_links import validate_scene_links
from safety_video_harness.seedance_live import (
    SeedanceLiveOptions,
    build_seedance_live_plan,
    run_seedance_live_plan,
    validate_seedance_live_options,
)
from safety_video_harness.style_guides import selected_style_prompt_block


def generate_images(project: Path, dry_run: bool, live: bool, scene_filter: str | None, regenerate: bool) -> str:
    layout = layout_for_project(project)
    if live:
        require_gate(project, "storyboard")
    scenes = read_json(layout.read_path(LayoutKey.STORY_SCENES))
    ensure_image_prompt_team_plan(project)
    reference_assets = load_reference_assets(project)
    asset_lock = build_asset_lock_manifest(reference_assets)
    reference_block = _style_and_reference_prompt_block(project, reference_assets, asset_lock)
    scene_items = list(scenes.get("scenes", []))
    plans = _image_prompt_plans(project, scenes, scene_items, reference_assets, reference_block, scene_filter)
    for plan in plans:
        plan["asset_lock"] = asset_lock
    if scene_filter is not None and not plans:
        raise HarnessError(f"unknown scene_id: {scene_filter}")
    write_json(layout.write_path(LayoutKey.STORY_IMAGE_PROMPTS), {"dry_run": dry_run, "plans": plans})
    if live:
        jobs = build_imagegen_jobs(project, plans, scene_filter, regenerate)
        write_json(layout.write_path(LayoutKey.REFS_ASSET_LOCK) / "asset_lock_manifest.json", asset_lock)
        write_json(layout.write_path(LayoutKey.STORY_IMAGEGEN_JOBS), jobs)
        job_count = len(jobs["jobs"])
        return f"imagegen job(s) prepared {job_count}; expected imagegen call(s): {job_count}"
    return f"image dry-run prepared {len(plans)} prompt(s)"


def _image_prompt_plans(
    project: Path,
    scenes: dict,
    scene_items: list[dict],
    reference_assets: dict[str, list[dict[str, str]]],
    reference_block: str,
    scene_filter: str | None,
) -> list[dict]:
    plans = [
        _build_image_prompt_with_memory(
            project,
            scene,
            reference_assets,
            reference_block,
            scene_items,
            index,
        )
        for index, scene in enumerate(scene_items)
    ]
    final_plan = _final_keyframe_plan(project, scenes, scene_items, reference_assets, reference_block)
    if final_plan is not None:
        plans.append(final_plan)
    if scene_filter is None:
        return plans
    return [plan for plan in plans if plan["scene_id"] == scene_filter]


def validate_images(project: Path, dry_run: bool, scene_filter: str | None) -> str:
    scenes = read_json(layout_for_project(project).read_path(LayoutKey.STORY_SCENES))
    review_items = _image_review_items(scenes)
    selected = [
        item
        for item in review_items
        if scene_filter is None or item["id"] == scene_filter
    ]
    if scene_filter is not None and not selected:
        raise HarnessError(f"unknown scene_id: {scene_filter}")
    reviews = [dry_run_review(scene) if dry_run else review_scene_image(project, scene) for scene in selected]
    iteration_counts, escalated_scenes = record_image_evaluation_rounds(project, selected, reviews)
    story_image_reviews = {
        "dry_run": dry_run,
        "reviews": [
            {
                "scene_id": review["scene_id"],
                "story_match_score": review["story_match_score"],
                "story_flow_score": review["story_flow_score"],
                "total_score": review["total_score"],
                "decision": review["decision"],
                "blocking_issues": review["blocking_issues"],
            }
            for review in reviews
        ],
    }
    write_json(project / "qa" / "image_reviews.json", {"dry_run": dry_run, "reviews": reviews})
    write_json(project / "qa" / "story_image_reviews.json", story_image_reviews)
    write_json(
        project / "qa" / "image_qa_loop.json",
        build_loop_summary(reviews, iteration_counts, escalated_scenes),
    )
    return f"validated {len(reviews)} image plan(s)"


def generate_seedance(
    project: Path,
    dry_run: bool,
    live: bool,
    execute_paid: bool,
    test_seconds: int,
    max_attempts: int,
    plan_only: bool,
    validation_run: bool = False,
) -> str:
    layout = layout_for_project(project)
    if live:
        if not execute_paid:
            raise HarnessError("live Seedance requires --execute-paid")
        options = SeedanceLiveOptions(
            test_seconds=test_seconds,
            max_attempts=max_attempts,
            plan_only=plan_only,
            validation_run=validation_run,
        )
        validate_seedance_live_options(options)
        require_gate(project, "image_to_video")
        _require_external_upload(project)
        plan = build_seedance_live_plan(project, options)
        if plan_only:
            return f"Seedance live plan prepared {len(plan['jobs'])} job(s)"
        validate_scene_links(project)
        return run_seedance_live_plan(project, plan)
    scenes = read_json(layout.read_path(LayoutKey.STORY_SCENES))
    reference_assets = load_reference_assets(project)
    asset_lock = build_asset_lock_manifest(reference_assets)
    reference_block = _style_and_reference_prompt_block(project, reference_assets, asset_lock)
    plans = [
        build_video_prompt_plan(scene, reference_assets, reference_block, asset_lock)
        for scene in scenes.get("scenes", [])
    ]
    write_json(layout.write_path(LayoutKey.REFS_ASSET_LOCK) / "asset_lock_manifest.json", asset_lock)
    write_json(layout.write_path(LayoutKey.STORY_VIDEO_PROMPTS), {"dry_run": dry_run, "asset_lock": asset_lock, "plans": plans})
    return f"Seedance dry-run prepared {len(plans)} clip plan(s)"


def _require_external_upload(project: Path) -> None:
    config = read_json(project / "project_config.json")
    if not bool(config.get("external_upload_allowed", False)):
        raise HarnessError("live generation requires external_upload_allowed=true")


def _style_and_reference_prompt_block(project: Path, reference_assets: dict[str, list[dict[str, str]]], asset_lock: dict) -> str:
    return "\n\n".join(
        [
            "Selected reusable style guide:",
            selected_style_prompt_block(project),
            "Asset lock and production consistency policy:",
            asset_lock_prompt_block(asset_lock),
            "Image prompt production team:",
            prompt_team_prompt_block(project),
            "Project-approved visual reference assets:",
            reference_assets_prompt_block(reference_assets),
        ]
    )


def _final_keyframe_plan(
    project: Path,
    scenes: dict,
    scene_items: list[dict],
    reference_assets: dict[str, list[dict[str, str]]],
    reference_block: str,
) -> dict | None:
    keyframe_count = int(scenes.get("keyframe_count", len(scene_items)))
    if keyframe_count <= len(scene_items) or not scene_items:
        return None
    scene_id = f"sc{keyframe_count:02d}"
    return build_final_image_prompt_plan(
        scene_id,
        scene_items[-1],
        reference_assets,
        reference_block,
        keyframe_count,
        keyframe_count,
        previous_blocking_issues(project, "image", scene_id),
    )


def _image_review_items(scenes: dict) -> list[dict]:
    scene_items = list(scenes.get("scenes", []))
    final_scene = _final_keyframe_scene(scenes, scene_items)
    if final_scene is None:
        return scene_items
    return [*scene_items, final_scene]


def _final_keyframe_scene(scenes: dict, scene_items: list[dict]) -> dict | None:
    keyframe_count = int(scenes.get("keyframe_count", len(scene_items)))
    if keyframe_count <= len(scene_items) or not scene_items:
        return None
    scene_id = f"sc{keyframe_count:02d}"
    previous = scene_items[-1]
    citation = list(previous.get("source_citations", []))
    return {
        "id": scene_id,
        "duration_sec": 1,
        "educational_goal_ko": "마지막 장면을 안전하게 종료한다.",
        "source_citations": citation,
        "visual_action_ko": "차량 동선과 보행자 동선이 통제된 상태로 교육 장면이 종료된다.",
        "caption_ko": "최종 안전 상태",
        "subtitle_ko": "통제된 상태로 작업을 마무리하세요.",
        "start_keyframe": previous.get("end_keyframe", f"media/images/approved/{scene_id}.png"),
        "end_keyframe": f"media/images/approved/{scene_id}.png",
        "continuity_constraints": previous.get("continuity_constraints", {}),
        "approval_state": "draft",
        "asset_version": 1,
    }


def _build_image_prompt_with_memory(
    project: Path,
    scene: dict,
    reference_assets: dict[str, list[dict[str, str]]],
    reference_block: str,
    scene_items: list[dict],
    index: int,
) -> dict:
    scene_id = str(scene["id"])
    return build_image_prompt_plan(
        scene,
        reference_assets,
        reference_block,
        scene_items[index - 1] if index > 0 else None,
        scene_items[index + 1] if index + 1 < len(scene_items) else None,
        index + 1,
        len(scene_items),
        previous_blocking_issues(project, "image", scene_id),
    )
