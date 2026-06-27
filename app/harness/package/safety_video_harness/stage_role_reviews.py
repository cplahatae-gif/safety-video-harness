from __future__ import annotations

from safety_video_harness.role_evaluators import run_role_evaluators_parallel


def image_role_reviews(review: dict) -> list[dict]:
    return run_role_evaluators_parallel(
        [
            ("technical", lambda: _image_technical_review(review)),
            ("visual_continuity", lambda: _image_visual_review(review)),
            ("story_match", lambda: _image_story_review(review)),
            ("safety_education", lambda: _image_safety_review(review)),
            ("devils_advocate", lambda: _devil_review(review)),
        ]
    )


def storyboard_role_reviews(review: dict, minimum_field_score: int) -> list[dict]:
    return run_role_evaluators_parallel(
        [
            ("source_grounding", lambda: _storyboard_criterion(review, "source_grounding_score", minimum_field_score)),
            ("causal_flow", lambda: _storyboard_criterion(review, "causal_flow_score", minimum_field_score)),
            ("generation_readiness", lambda: _storyboard_criterion(review, "granularity_score", minimum_field_score)),
            ("education_delivery", lambda: _storyboard_criterion(review, "text_delivery_score", minimum_field_score)),
            ("devils_advocate", lambda: _storyboard_devil_review(review)),
        ]
    )


def video_role_reviews(review: dict) -> list[dict]:
    return run_role_evaluators_parallel(
        [
            ("technical", lambda: _video_score_review(review, "technical_score", "technical")),
            ("continuity", lambda: _video_score_review(review, "continuity_score", "continuity")),
            ("gaze_motivation", lambda: _video_score_review(review, "gaze_motivation_score", "gaze_motivation")),
            ("education_clarity", lambda: _video_score_review(review, "safety_score", "education_clarity")),
            ("devils_advocate", lambda: _devil_review(review)),
        ]
    )


def _image_technical_review(review: dict) -> dict:
    blockers = list(review.get("blocking_issues", []))
    return {"role": "technical", "scores": {"technical": int(review.get("technical_score", 0))}, "blocking_issues": blockers}


def _image_visual_review(review: dict) -> dict:
    blockers = list(review.get("blocking_issues", []))
    return {
        "role": "visual_continuity",
        "scores": {
            "identity_consistency": int(review.get("identity_consistency_score", 0)),
            "ppe": int(review.get("ppe_score", 0)),
            "equipment": int(review.get("equipment_score", 0)),
        },
        "blocking_issues": blockers,
    }


def _image_story_review(review: dict) -> dict:
    blockers = list(review.get("blocking_issues", []))
    return {
        "role": "story_match",
        "scores": {
            "story_match": int(review.get("story_match_score", 0)),
            "story_flow": int(review.get("story_flow_score", 0)),
        },
        "blocking_issues": blockers,
    }


def _image_safety_review(review: dict) -> dict:
    blockers = list(review.get("blocking_issues", []))
    critical = [issue for issue in blockers if "unsafe" in str(issue).lower()]
    return {
        "role": "safety_education",
        "scores": {"safety": int(review.get("ppe_score", 0))},
        "blocking_issues": blockers,
        "critical_blockers": critical,
    }


def _storyboard_criterion(review: dict, score_name: str, minimum_field_score: int) -> dict:
    criteria = dict(review.get("criteria", {}))
    blockers = list(review.get("blocking_issues", []))
    score = int(criteria.get(score_name, 0))
    role = score_name.replace("_score", "")
    return {
        "role": role,
        "scores": {role: score},
        "blocking_issues": blockers if score < minimum_field_score else [],
    }


def _storyboard_devil_review(review: dict) -> dict:
    blockers = list(review.get("blocking_issues", []))
    critical = [issue for issue in blockers if "missing source citation" in str(issue)]
    return _devil_review(review, critical)


def _video_score_review(review: dict, source_score: str, role: str) -> dict:
    blockers = list(review.get("blocking_issues", []))
    score = int(review.get(source_score, 0))
    critical = blockers if role in {"continuity", "gaze_motivation", "education_clarity"} and score < 4 else []
    return {
        "role": role,
        "scores": {role: score},
        "blocking_issues": blockers if score < 4 else [],
        "critical_blockers": critical,
    }


def _devil_review(review: dict, critical: list[str] | None = None) -> dict:
    blockers = list(review.get("blocking_issues", []))
    return {
        "role": "devils_advocate",
        "scores": {"risk": 5 if not blockers else 2},
        "blocking_issues": blockers,
        "critical_blockers": critical or [],
        "vote": "approve" if not blockers else "reject",
    }
