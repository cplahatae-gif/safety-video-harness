from __future__ import annotations

from pathlib import Path

from safety_video_harness.evaluation_rounds import (
    completed_iterations,
    record_evaluation_round,
    write_evaluation_bundle,
)
from safety_video_harness.errors import HarnessError
from safety_video_harness.io import read_json, write_json


MINIMUM_FIELD_SCORE = 4
MINIMUM_TOTAL_SCORE = 20


def evaluate_storyboard(project: Path) -> str:
    payload = read_json(project / "storyboard" / "scenes.json")
    scenes = list(payload.get("scenes", []))
    reviews = [_review_scene(scene) for scene in scenes]
    _record_storyboard_evaluation_rounds(project, scenes, reviews)
    blockers = [issue for review in reviews for issue in review["blocking_issues"]]
    total_scores = [int(review["total_score"]) for review in reviews]
    report = {
        "passed": not blockers and all(score >= MINIMUM_TOTAL_SCORE for score in total_scores),
        "thresholds": {
            "minimum_field_score": MINIMUM_FIELD_SCORE,
            "minimum_total_score": MINIMUM_TOTAL_SCORE,
        },
        "reviews": reviews,
        "blockers": blockers,
        "algorithm": {
            "source_grounding": "Every scene must cite source facts.",
            "causal_flow": "Every scene must show a prevention cause/effect beat.",
            "granularity": "Scene duration must be short enough for controllable keyframes.",
            "text_delivery": "Teaching point must be expressed as subtitle/overlay, not narration.",
            "continuity": "Start/end keyframes and continuity constraints must be present.",
        },
    }
    write_json(project / "qa" / "storyboard_quality_reviews.json", report)
    if not bool(report["passed"]):
        raise HarnessError("storyboard QA blockers: " + "; ".join(blockers))
    return f"storyboard QA passed {len(reviews)} scene(s)"


def _review_scene(scene: dict) -> dict:
    scene_id = str(scene.get("id", "unknown"))
    criteria = {
        "source_grounding_score": _score(bool(scene.get("source_citations"))),
        "causal_flow_score": _score(_has_text(scene, "visual_action_ko") and _has_text(scene, "educational_goal_ko")),
        "granularity_score": _score(1 <= int(scene.get("duration_sec", 0)) <= 5),
        "text_delivery_score": _score(_has_text(scene, "subtitle_ko") and "narration_ko" not in scene),
        "continuity_score": _score(
            _has_text(scene, "start_keyframe")
            and _has_text(scene, "end_keyframe")
            and bool(scene.get("continuity_constraints"))
        ),
    }
    blockers = _blockers(scene, criteria)
    return {
        "scene_id": scene_id,
        "criteria": criteria,
        "total_score": sum(criteria.values()),
        "blocking_issues": blockers,
        "decision": "approve_storyboard" if not blockers else "revise_storyboard",
        "revision_prompt": _revision_prompt(scene_id, blockers),
    }


def _has_text(scene: dict, key: str) -> bool:
    return bool(str(scene.get(key, "")).strip())


def _score(passed: bool) -> int:
    return 5 if passed else 0


def _blockers(scene: dict, criteria: dict[str, int]) -> list[str]:
    scene_id = str(scene.get("id", "unknown"))
    issues = []
    if criteria["source_grounding_score"] < MINIMUM_FIELD_SCORE:
        issues.append(f"{scene_id}: missing source citation")
    if criteria["causal_flow_score"] < MINIMUM_FIELD_SCORE:
        issues.append(f"{scene_id}: weak causal prevention beat")
    if criteria["granularity_score"] < MINIMUM_FIELD_SCORE:
        issues.append(f"{scene_id}: scene duration is too broad for controlled generation")
    if criteria["text_delivery_score"] < MINIMUM_FIELD_SCORE:
        issues.append(f"{scene_id}: subtitle/overlay text contract is missing or narration is present")
    if criteria["continuity_score"] < MINIMUM_FIELD_SCORE:
        issues.append(f"{scene_id}: start/end keyframe continuity contract is incomplete")
    return issues


def _revision_prompt(scene_id: str, blockers: list[str]) -> str:
    if not blockers:
        return ""
    return (
        f"Revise storyboard scene {scene_id}. Fix these blockers: "
        + "; ".join(blockers)
        + ". Keep the safety lesson source-grounded, visually causal, and ready for image generation."
    )


def _record_storyboard_evaluation_rounds(
    project: Path,
    scenes: list[dict],
    reviews: list[dict],
) -> None:
    scene_by_id = {str(scene.get("id", "unknown")): scene for scene in scenes}
    for review in reviews:
        scene_id = str(review["scene_id"])
        iteration = completed_iterations(project, "storyboard", scene_id) + 1
        bundle = {
            "stage": "storyboard",
            "iteration": iteration,
            "evaluator_context_policy": "isolated_evaluator_with_evidence_bundle",
            "scene": scene_by_id.get(scene_id, {}),
            "review": review,
            "required_evidence": [
                "source citations",
                "selected education topic",
                "current scene",
                "subtitle or overlay contract",
                "start/end keyframe continuity contract",
            ],
        }
        bundle_path = write_evaluation_bundle(project, "storyboard", scene_id, iteration, bundle)
        record_evaluation_round(project, "storyboard", scene_id, iteration, review, bundle_path)
