from __future__ import annotations


def continuity_bible() -> dict[str, str]:
    return {
        "fixed_character_lock": (
            "same worker-001 across every keyframe: Korean adult industrial worker, average build, "
            "white hard hat, orange reflective safety vest, navy work pants, black safety boots, neutral focused expression"
        ),
        "fixed_signal_person_lock": (
            "same signal person across every keyframe: orange vest, white hard hat, red signal baton in right hand, handheld radio in left hand"
        ),
        "fixed_equipment_lock": (
            "same BCT bulk cement trailer and same yellow dump truck across every keyframe; keep vehicle scale, wheel count, cab color, and trailer silhouette consistent"
        ),
        "fixed_site_lock": (
            "same ready-mix concrete plant entrance, concrete yard, marked pedestrian route, vehicle lane markings, blind spot hazard zone, daylight overcast sky"
        ),
        "camera_lock": (
            "35mm documentary training frame, eye-level wide shot, clear foreground worker, visible vehicle path, no extreme close-up, no Dutch angle"
        ),
        "lighting_color_lock": (
            "neutral daylight, clean industrial palette, safety orange and yellow accents, moderate contrast, no dramatic shadows"
        ),
    }


def negative_prompt() -> str:
    return (
        "No Korean text, no English text, no logos, no brand marks, no gore, no injury, no collision impact, "
        "no crushed body, no distorted hands, no extra limbs, no duplicate workers, no inconsistent helmet color, "
        "no different vehicle model, no fantasy style, no dark horror lighting, no blurry low-resolution frame."
    )


def image_quality_checklist() -> list[str]:
    return [
        "worker-001 PPE matches the continuity bible",
        "BCT and dump truck match previous keyframes",
        "hazard zone and safe pedestrian route are visible",
        "scene action matches the storyboard citation",
        "frame contains no generated text or logo",
    ]


def video_continuity_checklist() -> list[str]:
    return [
        "first frame matches start keyframe",
        "last frame matches end keyframe",
        "no character, PPE, vehicle, or site redesign occurs",
        "motion illustrates prevention rather than accident impact",
        "clip can connect to the next scene without a jump cut",
    ]
