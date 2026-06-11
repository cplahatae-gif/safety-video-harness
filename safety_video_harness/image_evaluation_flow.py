from __future__ import annotations

from pathlib import Path

from safety_video_harness.evaluation_arbiter import aggregate_arbiter_decision
from safety_video_harness.evaluation_rounds import completed_iterations, record_evaluation_round, write_evaluation_bundle
from safety_video_harness.image_qa import MAX_RALPH_ITERATIONS
from safety_video_harness.stage_role_reviews import image_role_reviews


def record_image_evaluation_rounds(
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
        arbiter_decision = aggregate_arbiter_decision(project, "image", scene_id, iteration, role_reviews)
        review["arbiter_decision"] = arbiter_decision
        review["blocker_signatures"] = list(arbiter_decision.get("blocker_signatures", []))
        if arbiter_decision.get("decision") == "revise_storyboard":
            escalated_scenes.append(scene_id)
        bundle = _image_evaluation_bundle(scene_by_id[scene_id], review, iteration)
        bundle_path = write_evaluation_bundle(project, "image", scene_id, iteration, bundle)
        record_evaluation_round(project, "image", scene_id, iteration, review, bundle_path)
    return counts, escalated_scenes


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
