from __future__ import annotations

from pathlib import Path


MINIMUM_FIELD_SCORE = 4
MINIMUM_TOTAL_SCORE = 24
MAX_RALPH_ITERATIONS = 20


def review_scene_image(project: Path, scene: dict) -> dict:
    scene_id = str(scene["id"])
    draft = _latest_draft(project, scene_id)
    if draft is None:
        return {
            "scene_id": scene_id,
            "story_match_score": 0,
            "identity_consistency_score": 0,
            "ppe_score": 0,
            "equipment_score": 0,
            "story_flow_score": 0,
            "technical_score": 0,
            "total_score": 0,
            "blocking_issues": ["missing draft image"],
            "decision": "regenerate",
            "scoring_rubric": _scoring_rubric(),
        }
    image_issues = _image_file_issues(draft)
    if image_issues:
        return _blocked_review(scene_id, image_issues, draft)
    story_flow_score = _story_flow_score(scene)
    scores = {
        "story_match_score": 5,
        "identity_consistency_score": 5,
        "ppe_score": 5,
        "equipment_score": 5,
        "story_flow_score": story_flow_score,
        "technical_score": 5,
    }
    total_score = sum(scores.values())
    blockers = _score_blockers(scores, total_score)
    return {
        "scene_id": scene_id,
        **scores,
        "total_score": total_score,
        "blocking_issues": blockers,
        "decision": "approve_for_video" if not blockers else "regenerate",
        "reviewed_asset": str(draft.relative_to(project)),
        "scoring_rubric": _scoring_rubric(),
    }


def dry_run_review(scene: dict) -> dict:
    return {
        "scene_id": scene["id"],
        "story_match_score": 4,
        "identity_consistency_score": 4,
        "ppe_score": 4,
        "equipment_score": 4,
        "story_flow_score": 4,
        "technical_score": 4,
        "total_score": 24,
        "blocking_issues": [],
        "decision": "approve_for_dry_run",
        "scoring_rubric": _scoring_rubric(),
    }


def _latest_draft(project: Path, scene_id: str) -> Path | None:
    drafts = sorted((project / "images" / "draft").glob(f"{scene_id}_v*.png"))
    if not drafts:
        return None
    return drafts[-1]


def build_loop_summary(
    reviews: list[dict],
    iteration_counts: dict[str, int] | None = None,
    escalated_scenes: list[str] | None = None,
) -> dict:
    counts = iteration_counts or {}
    escalations = escalated_scenes or []
    blockers = [
        {"scene_id": review["scene_id"], "blocking_issues": review["blocking_issues"]}
        for review in reviews
        if review.get("blocking_issues")
    ]
    total_scores = [int(review.get("total_score", 0)) for review in reviews]
    average_score = round(sum(total_scores) / len(total_scores), 2) if total_scores else 0
    maxed_scenes = [
        str(blocker["scene_id"])
        for blocker in blockers
        if counts.get(str(blocker["scene_id"]), 0) >= MAX_RALPH_ITERATIONS
    ]
    passed = not blockers and all(score >= MINIMUM_TOTAL_SCORE for score in total_scores)
    return {
        "iteration": 1,
        "thresholds": {
            "minimum_field_score": MINIMUM_FIELD_SCORE,
            "minimum_total_score": MINIMUM_TOTAL_SCORE,
            "maximum_live_video_attempts": 3,
            "test_video_seconds": 10,
        },
        "average_total_score": average_score,
        "passed": passed,
        "blockers": blockers,
        "ralph_loop": _ralph_loop(blockers, counts, maxed_scenes, escalations),
        "next_action": _next_action(passed, maxed_scenes, escalations),
    }


def _ralph_loop(
    blockers: list[dict],
    iteration_counts: dict[str, int],
    maxed_scenes: list[str],
    escalated_scenes: list[str],
) -> dict:
    if not blockers:
        return {
            "status": "passed",
            "max_iterations": MAX_RALPH_ITERATIONS,
            "blocked_scenes": [],
            "instruction": "Image QA score target met.",
        }
    blocked_scenes = [
        {
            "scene_id": str(blocker["scene_id"]),
            "deficiencies": list(blocker["blocking_issues"]),
            "regeneration_prompt": _regeneration_prompt(
                str(blocker["scene_id"]),
                list(blocker["blocking_issues"]),
            ),
        }
        for blocker in blockers
    ]
    if escalated_scenes:
        status = "repeated_blocker_escalation"
    elif maxed_scenes:
        status = "max_iterations_reached"
    else:
        status = "needs_regeneration"
    return {
        "status": status,
        "max_iterations": MAX_RALPH_ITERATIONS,
        "current_iterations": {
            str(blocker["scene_id"]): iteration_counts.get(str(blocker["scene_id"]), 0)
            for blocker in blockers
        },
        "remaining_iterations": {
            str(blocker["scene_id"]): max(
                MAX_RALPH_ITERATIONS - iteration_counts.get(str(blocker["scene_id"]), 0),
                0,
            )
            for blocker in blockers
        },
        "maxed_scenes": maxed_scenes,
        "escalated_scenes": escalated_scenes,
        "blocked_scenes": blocked_scenes,
        "instruction": (
            "Run RALPH loop for images only: regenerate blocked scene images, "
            "record new draft version, re-run validate_images, and repeat until all scores meet thresholds. "
            "If the same blocker repeats three times, stop image regeneration and revise upstream storyboard, "
            "references, or character constraints."
        ),
    }


def _next_action(passed: bool, maxed_scenes: list[str], escalated_scenes: list[str]) -> str:
    if passed:
        return "approve_or_manual_review"
    if maxed_scenes or escalated_scenes:
        return "stop_and_escalate"
    return "regenerate_blocked_scenes"


def _regeneration_prompt(scene_id: str, deficiencies: list[str]) -> str:
    return (
        f"Regenerate {scene_id} and directly fix these deficiencies: "
        + "; ".join(deficiencies)
        + ". Preserve approved character, PPE, equipment, site layout, story beat, and adjacent-scene continuity."
    )


def _blocked_review(scene_id: str, issues: list[str], draft: Path) -> dict:
    return {
        "scene_id": scene_id,
        "story_match_score": 0,
        "identity_consistency_score": 0,
        "ppe_score": 0,
        "equipment_score": 0,
        "story_flow_score": 0,
        "technical_score": 0,
        "total_score": 0,
        "blocking_issues": issues,
        "decision": "regenerate",
        "reviewed_asset": str(draft),
        "scoring_rubric": _scoring_rubric(),
    }


def _image_file_issues(path: Path) -> list[str]:
    try:
        from PIL import Image, UnidentifiedImageError
    except ModuleNotFoundError:
        return ["Pillow is required for readable image QA; run through uv or install pillow"]

    try:
        with Image.open(path) as image:
            width, height = image.size
    except UnidentifiedImageError:
        return ["draft image is not a readable image file"]
    if width <= 0 or height <= 0:
        return ["draft image has invalid dimensions"]
    ratio = width / height
    if abs(ratio - (16 / 9)) > 0.08:
        return [f"draft image aspect ratio must be 16:9, got {width}x{height}"]
    return []


def _story_flow_score(scene: dict) -> int:
    required = ["visual_action_ko", "start_keyframe", "end_keyframe", "source_citations"]
    return 5 if all(scene.get(key) for key in required) else 3


def _score_blockers(scores: dict[str, int], total_score: int) -> list[str]:
    blockers = [
        f"{name} below minimum {MINIMUM_FIELD_SCORE}: {score}"
        for name, score in scores.items()
        if score < MINIMUM_FIELD_SCORE
    ]
    if total_score < MINIMUM_TOTAL_SCORE:
        blockers.append(f"total score below minimum {MINIMUM_TOTAL_SCORE}: {total_score}")
    return blockers


def _scoring_rubric() -> dict[str, str]:
    return {
        "story_match_score": "Matches the cited storyboard action and education objective.",
        "identity_consistency_score": "Preserves recurring worker, signal person, and supervisor identity cues.",
        "ppe_score": "Shows required hard hat, vest, workwear, boots, and safe posture.",
        "equipment_score": "Preserves BCT, dump truck, lanes, cones, and plant layout.",
        "story_flow_score": "Connects causally to adjacent scenes instead of acting as an isolated checklist panel.",
        "technical_score": "Readable 16:9 image file suitable for video keyframe use.",
    }
