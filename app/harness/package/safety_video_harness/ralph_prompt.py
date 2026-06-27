from __future__ import annotations

from typing import Final

QUALITY_PRESSURE: Final = (
    "This result is not acceptable for a safety training video until the listed blockers are visibly fixed. "
    "Re-check the failed frame before generating again; do not make a cosmetic variation that repeats the same issue."
)


def regeneration_prompt(scene_id: str, deficiencies: list[str]) -> str:
    if not deficiencies:
        return ""
    return "\n".join(
        [
            f"RALPH critique for {scene_id}:",
            f"Quality pressure: {QUALITY_PRESSURE}",
            "Failed criteria and required fixes:",
            *_bullets(deficiencies),
            "Must preserve:",
            "- approved character identity, helmet, vest, body proportion, and role",
            "- approved BCT/dump-truck geometry, scale, wheel count, mirrors, and relative position",
            "- approved site layout, concrete floor, lane colors, pedestrian route, cones, bollards, and hazard zone",
            "- current storyboard beat and previous/next scene continuity",
            "Must change this round:",
            "- make every listed blocker visually impossible to miss",
            "- remove unexplained gaze, character drift, vehicle drift, floor/lane drift, or generic factory framing",
            "Do not repeat:",
            *_bullets(deficiencies),
        ]
    )


def previous_blocker_prompt_lines(blockers: list[str]) -> list[str]:
    if not blockers:
        return ["Previous QA blockers for this scene: none recorded."]
    return [
        "RALPH previous-round critique:",
        f"Quality pressure: {QUALITY_PRESSURE}",
        "Previous QA blockers for this scene:",
        *_bullets(blockers),
        "Do not repeat these failures:",
        *_bullets(blockers),
        (
            "Required correction this round: fix the blockers in the visible image content, not only in wording. "
            "Preserve the locked cast, PPE, equipment, floor/lane layout, hazard zone, camera angle, and adjacent-scene continuity."
        ),
    ]


def _bullets(items: list[str]) -> list[str]:
    return [f"- {item}" for item in items]
