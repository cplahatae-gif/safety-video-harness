from __future__ import annotations

from pathlib import Path

from safety_video_harness.image_manual_review import (
    MANUAL_REVIEW_RELATIVE_PATH,
    VISUAL_LOCK_SCORE_FIELDS,
    empty_visual_scores,
    load_image_manual_review,
    manual_review_payload,
    missing_manual_review_issue,
)
from safety_video_harness.io import write_json


def test_load_missing_manual_review_returns_none(tmp_path: Path) -> None:
    assert load_image_manual_review(tmp_path, "sc01") is None


def test_empty_visual_scores_zero_for_all_lock_fields() -> None:
    scores = empty_visual_scores()
    assert set(scores) == set(VISUAL_LOCK_SCORE_FIELDS)
    assert all(value == 0 for value in scores.values())


def test_missing_payload_lists_required_scores() -> None:
    payload = manual_review_payload(None)
    assert payload["status"] == "missing"
    assert payload["required_scores"] == list(VISUAL_LOCK_SCORE_FIELDS)
    assert "consistency" in missing_manual_review_issue()


def test_load_present_manual_review_parses_scores(tmp_path: Path) -> None:
    write_json(
        tmp_path / MANUAL_REVIEW_RELATIVE_PATH,
        {
            "reviews": {
                "sc01": {
                    "floor_lane_consistency_score": 9,
                    "blocking_issues": ["lane color drift"],
                    "reviewer": "qa",
                    "notes": "ok",
                }
            }
        },
    )
    review = load_image_manual_review(tmp_path, "sc01")
    assert review is not None
    assert review.scores["floor_lane_consistency_score"] == 9
    assert review.blocking_issues == ["lane color drift"]
    payload = manual_review_payload(review)
    assert payload["status"] == "present"
    assert payload["reviewer"] == "qa"
