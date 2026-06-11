from __future__ import annotations

from pathlib import Path

from safety_video_harness.errors import HarnessError
from safety_video_harness.assets import load_reference_assets, reference_assets_prompt_block
from safety_video_harness.evaluation_arbiter import aggregate_arbiter_decision
from safety_video_harness.evaluation_rounds import (
    completed_iterations,
    previous_blocking_issues,
    record_evaluation_round,
    write_evaluation_bundle,
)
from safety_video_harness.gates import require_gate
from safety_video_harness.image_qa import (
    MAX_RALPH_ITERATIONS,
    build_loop_summary,
    dry_run_review,
    review_scene_image,
)
from safety_video_harness.imagegen_jobs import build_imagegen_jobs
from safety_video_harness.io import read_json, write_json
from safety_video_harness.prompt_contract import build_image_prompt_plan, build_video_prompt_plan
from safety_video_harness.scene_links import validate_scene_links
from safety_video_harness.seedance_live import SeedanceLiveOptions, build_seedance_live_plan, run_seedance_live_plan
from safety_video_harness.stage_role_reviews import image_role_reviews


def generate_images(project: Path, dry_run: bool, live: bool, scene_filter: str | None, regenerate: bool) -> str:
    if live:
        require_gate(project, "storyboard")
        _require_external_upload(project)
    scenes = read_json(project / "storyboard" / "scenes.json")
    reference_assets = load_reference_assets(project)
    reference_block = reference_assets_prompt_block(reference_assets)
    scene_items = list(scenes.get("scenes", []))
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
        if scene_filter is None or scene["id"] == scene_filter
    ]
    if scene_filter is not None and not plans:
        raise HarnessError(f"unknown scene_id: {scene_filter}")
    write_json(project / "prompts" / "image_prompts.json", {"dry_run": dry_run, "plans": plans})
    if live:
        jobs = build_imagegen_jobs(project, plans, scene_filter, regenerate)
        write_json(project / "prompts" / "imagegen_jobs.json", jobs)
        return f"imagegen job(s) prepared {len(plans)}; expected imagegen call(s): {len(plans)}"
    return f"image dry-run prepared {len(plans)} prompt(s)"


def validate_images(project: Path, dry_run: bool, scene_filter: str | None) -> str:
    scenes = read_json(project / "storyboard" / "scenes.json")
    selected = [
        scene
        for scene in scenes.get("scenes", [])
        if scene_filter is None or scene["id"] == scene_filter
    ]
    if scene_filter is not None and not selected:
        raise HarnessError(f"unknown scene_id: {scene_filter}")
    reviews = [dry_run_review(scene) if dry_run else review_scene_image(project, scene) for scene in selected]
    iteration_counts, escalated_scenes = _record_image_evaluation_rounds(project, selected, reviews)
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
    if live:
        if not execute_paid:
            raise HarnessError("live Seedance requires --execute-paid")
        options = SeedanceLiveOptions(
            test_seconds=test_seconds,
            max_attempts=max_attempts,
            plan_only=plan_only,
            validation_run=validation_run,
        )
        plan = build_seedance_live_plan(project, options)
        if plan_only:
            return f"Seedance live plan prepared {len(plan['jobs'])} job(s)"
        require_gate(project, "image_to_video")
        _require_external_upload(project)
        validate_scene_links(project)
        return run_seedance_live_plan(project, plan)
    scenes = read_json(project / "storyboard" / "scenes.json")
    reference_assets = load_reference_assets(project)
    reference_block = reference_assets_prompt_block(reference_assets)
    plans = [
        build_video_prompt_plan(scene, reference_assets, reference_block)
        for scene in scenes.get("scenes", [])
    ]
    write_json(project / "prompts" / "video_prompts.json", {"dry_run": dry_run, "plans": plans})
    return f"Seedance dry-run prepared {len(plans)} clip plan(s)"


def _require_external_upload(project: Path) -> None:
    config = read_json(project / "project_config.json")
    if not bool(config.get("external_upload_allowed", False)):
        raise HarnessError("live generation requires external_upload_allowed=true")


def _record_image_evaluation_rounds(
    project: Path,
    scenes: list[dict],
    reviews: list[dict],
) -> tuple[dict[str, int], list[str]]:
    counts: dict[str, int] = {}
    escalated_scenes: list[str] = []
    scene_by_id = {str(scene["id"]): scene for scene in scenes}
    for review in reviews:
        scene_id = str(review["scene_id"])
        prior_iterations = completed_iterations(project, "image", scene_id)
        blocked = bool(review.get("blocking_issues"))
        if blocked and prior_iterations >= MAX_RALPH_ITERATIONS:
            counts[scene_id] = prior_iterations
            continue
        iteration = prior_iterations + 1
        counts[scene_id] = iteration
        role_reviews = image_role_reviews(review)
        arbiter_decision = aggregate_arbiter_decision(
            project,
            "image",
            scene_id,
            iteration,
            role_reviews,
        )
        review["arbiter_decision"] = arbiter_decision
        review["blocker_signatures"] = list(arbiter_decision.get("blocker_signatures", []))
        if arbiter_decision.get("decision") == "revise_storyboard":
            escalated_scenes.append(scene_id)
        bundle = _image_evaluation_bundle(scene_by_id[scene_id], review, iteration)
        bundle_path = write_evaluation_bundle(project, "image", scene_id, iteration, bundle)
        record_evaluation_round(project, "image", scene_id, iteration, review, bundle_path)
    return counts, escalated_scenes


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


def _image_evaluation_bundle(scene: dict, review: dict, iteration: int) -> dict:
    return {
        "stage": "image",
        "iteration": iteration,
        "evaluator_context_policy": "isolated_evaluator_with_evidence_bundle",
        "evaluator_instruction": (
            "Evaluate only the supplied evidence. Do not rely on the generator's intent. "
            "Score the produced image against storyboard, references, continuity, and QA rubric."
        ),
        "scene": scene,
        "review": review,
        "required_evidence": [
            "selected education topic",
            "current scene",
            "previous and next scene continuity",
            "approved reference assets and character profiles",
            "draft image path or missing-image blocker",
            "scoring rubric",
        ],
    }
