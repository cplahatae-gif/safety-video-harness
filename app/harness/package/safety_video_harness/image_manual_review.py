from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Final

from safety_video_harness.io import JsonValue, read_json

MANUAL_REVIEW_RELATIVE_PATH: Final = Path("qa") / "image_manual_reviews.json"
VISUAL_LOCK_SCORE_FIELDS: Final[dict[str, str]] = {
    "floor_lane_consistency_score": "Concrete floor, lane colors, walk path, cones, and bollards match the locked site layout.",
    "background_consistency_score": "Plant structures, gates, mirrors, signage, and camera-side geometry remain stable.",
    "character_identity_lock_score": "Recurring workers keep the same body type, helmet, vest, role, and visual identity cues.",
    "vehicle_geometry_lock_score": "BCT mixer, dump truck, mirrors, wheels, scale, and relative positions remain stable.",
    "hazard_zone_consistency_score": "The red danger zone, pedestrian route, stop line, and control point stay consistent and visible.",
}


@dataclass(frozen=True, slots=True)
class ImageManualReview:
    scene_id: str
    scores: dict[str, int]
    blocking_issues: list[str]
    reviewer: str
    notes: str
    source_path: str


def load_image_manual_review(project: Path, scene_id: str) -> ImageManualReview | None:
    path = project / MANUAL_REVIEW_RELATIVE_PATH
    if not path.exists():
        return None
    payload = read_json(path)
    entry = _review_entry(payload.get("reviews"), scene_id)
    if entry is None:
        return None
    return ImageManualReview(
        scene_id=scene_id,
        scores=_scores(entry),
        blocking_issues=_string_list(entry.get("blocking_issues")),
        reviewer=_string_value(entry.get("reviewer"), "manual_visual_qa"),
        notes=_string_value(entry.get("notes"), ""),
        source_path=str(MANUAL_REVIEW_RELATIVE_PATH),
    )


def missing_manual_review_issue() -> str:
    return (
        "manual visual consistency review is required before image approval: "
        "score floor/lane, background, character identity, vehicle geometry, and hazard-zone consistency"
    )


def empty_visual_scores() -> dict[str, int]:
    return {field: 0 for field in VISUAL_LOCK_SCORE_FIELDS}


def manual_review_payload(review: ImageManualReview | None) -> dict[str, JsonValue]:
    if review is None:
        return {
            "status": "missing",
            "required_path": str(MANUAL_REVIEW_RELATIVE_PATH),
            "required_scores": list(VISUAL_LOCK_SCORE_FIELDS),
        }
    return {
        "status": "present",
        "source_path": review.source_path,
        "reviewer": review.reviewer,
        "notes": review.notes,
        "scores": review.scores,
        "blocking_issues": review.blocking_issues,
    }


def _review_entry(value: JsonValue, scene_id: str) -> dict[str, JsonValue] | None:
    if isinstance(value, dict):
        candidate = value.get(scene_id)
        return candidate if isinstance(candidate, dict) else None
    if isinstance(value, list):
        for item in value:
            if isinstance(item, dict) and item.get("scene_id") == scene_id:
                return item
    return None


def _scores(entry: dict[str, JsonValue]) -> dict[str, int]:
    return {field: _score(entry.get(field)) for field in VISUAL_LOCK_SCORE_FIELDS}


def _score(value: JsonValue) -> int:
    if isinstance(value, bool):
        return 0
    if isinstance(value, int):
        return value
    return 0


def _string_list(value: JsonValue) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str) and item.strip()]


def _string_value(value: JsonValue, default: str) -> str:
    if isinstance(value, str):
        return value
    return default
