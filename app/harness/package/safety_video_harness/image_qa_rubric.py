from __future__ import annotations

from safety_video_harness.image_manual_review import VISUAL_LOCK_SCORE_FIELDS


MINIMUM_FIELD_SCORE = 4
MINIMUM_TOTAL_SCORE = 44
MAX_RALPH_ITERATIONS = 10


def scoring_rubric() -> dict[str, str]:
    return {
        "story_match_score": "Matches the cited storyboard action and education objective.",
        "identity_consistency_score": "Preserves recurring worker, signal person, and supervisor identity cues.",
        "ppe_score": "Shows required hard hat, vest, workwear, boots, and safe posture.",
        "equipment_score": "Preserves BCT, dump truck, lanes, cones, and plant layout.",
        "story_flow_score": "Connects causally to adjacent scenes instead of acting as an isolated checklist panel.",
        "technical_score": "Readable 16:9 image file suitable for video keyframe use.",
        **VISUAL_LOCK_SCORE_FIELDS,
    }
