from __future__ import annotations

from typing import TypedDict

from safety_video_harness.ralph_prompt import QUALITY_PRESSURE


class ImagePromptPlan(TypedDict):
    scene_id: str
    output: str
    prompt: str
    negative_prompt: str
    reference_assets: dict[str, list[dict[str, str]]]
    continuity_bible: dict[str, str]
    quality_checklist: list[str]


class VideoPromptPlan(TypedDict):
    scene_id: str
    start_keyframe: str
    end_keyframe: str
    prompt: str
    subtitle_plan_ko: str
    reference_assets: dict[str, list[dict[str, str]]]
    sliding_chain_contract: dict[str, str]
    continuity_checklist: list[str]


def build_image_prompt_plan(
    scene: dict,
    reference_assets: dict[str, list[dict[str, str]]],
    reference_block: str,
    previous_scene: dict | None = None,
    next_scene: dict | None = None,
    scene_index: int = 1,
    scene_total: int = 1,
    previous_qa_blockers: list[str] | None = None,
) -> ImagePromptPlan:
    scene_id = str(scene["id"])
    action = str(scene["image_prompt_en"])
    continuity = _continuity_bible()
    story_flow = _story_flow_context(scene, previous_scene, next_scene, scene_index, scene_total)
    prompt = "\n".join(
        [
            "Create one keyframe for a Korean industrial safety training animation.",
            f"Scene ID: {scene_id}.",
            f"Story flow role: {story_flow['role']}",
            f"Previous scene continuity: {story_flow['previous']}",
            f"Current story beat: {story_flow['current']}",
            f"Next scene setup: {story_flow['next']}",
            (
                "Narrative requirement: this keyframe must feel like part of one continuous incident-prevention "
                "story, not a disconnected checklist panel."
            ),
            *_previous_blocker_prompt_lines(previous_qa_blockers or []),
            f"Primary action: {action}",
            f"Fixed character lock: {continuity['fixed_character_lock']}",
            f"Fixed equipment lock: {continuity['fixed_equipment_lock']}",
            f"Fixed site lock: {continuity['fixed_site_lock']}",
            f"Camera and composition: {continuity['camera_lock']}",
            f"Lighting and color: {continuity['lighting_color_lock']}",
            "Visual style contract: obey the selected reusable style guide while preserving storyboard continuity.",
            "Approved style guide and reference assets to preserve:",
            reference_block,
            "Safety framing: show a near-miss prevention moment, not an accident impact.",
            "Output must be clean, readable, realistic enough for worker education, and free of generated text.",
            (
                "Prompting reference: follow scripts/codex_image.sh (Codex CLI image generation) and the official image generation guide; "
                "avoid precise in-image text because image models can struggle with exact text rendering and layout."
            ),
        ]
    )
    return {
        "scene_id": scene_id,
        "output": f"images/draft/{scene_id}.png",
        "prompt": prompt,
        "negative_prompt": _negative_prompt(),
        "reference_assets": reference_assets,
        "continuity_bible": continuity,
        "quality_checklist": _image_quality_checklist(),
    }


def build_final_image_prompt_plan(
    scene_id: str,
    previous_scene: dict,
    reference_assets: dict[str, list[dict[str, str]]],
    reference_block: str,
    scene_index: int,
    scene_total: int,
    previous_qa_blockers: list[str] | None = None,
) -> ImagePromptPlan:
    continuity = _continuity_bible()
    previous = str(previous_scene.get("visual_action_ko", "Continue directly from the previous prevention beat."))
    prompt = "\n".join(
        [
            "Create the final end keyframe for a Korean industrial safety training animation.",
            f"Scene ID: {scene_id}.",
            f"Story flow role: final end keyframe {scene_index} of {scene_total}; this is the last frame of the sliding chain.",
            f"Previous scene continuity: {previous}",
            "Current story beat: leave the same ready-mix concrete plant visibly controlled, with vehicles stopped or moving safely, workers outside hazard zones, and the signal workflow complete.",
            "Next scene setup: closing frame; no new incident, no new character, no new vehicle, and no visual jump.",
            (
                "Narrative requirement: this final end keyframe must resolve the prevention story and serve as "
                "the exact end frame for the last Seedance clip."
            ),
            *_previous_blocker_prompt_lines(previous_qa_blockers or []),
            "Primary action: use the selected reusable style guide for the same ready-mix concrete plant, same BCT bulk cement trailer, same yellow dump truck, same signal person and worker, separated traffic lanes, visible safe pedestrian route, controlled blind spot zone, no text, no injury, no impact frame.",
            f"Fixed character lock: {continuity['fixed_character_lock']}",
            f"Fixed equipment lock: {continuity['fixed_equipment_lock']}",
            f"Fixed site lock: {continuity['fixed_site_lock']}",
            f"Camera and composition: {continuity['camera_lock']}",
            f"Lighting and color: {continuity['lighting_color_lock']}",
            "Visual style contract: obey the selected reusable style guide while preserving storyboard continuity.",
            "Approved style guide and reference assets to preserve:",
            reference_block,
            "Safety framing: show a completed near-miss prevention moment, not an accident impact.",
            "Output must be clean, readable, realistic enough for worker education, and free of generated text.",
        ]
    )
    return {
        "scene_id": scene_id,
        "output": f"images/draft/{scene_id}.png",
        "prompt": prompt,
        "negative_prompt": _negative_prompt(),
        "reference_assets": reference_assets,
        "continuity_bible": continuity,
        "quality_checklist": _image_quality_checklist(),
    }


def build_video_prompt_plan(scene: dict, reference_assets: dict[str, list[dict[str, str]]], reference_block: str) -> VideoPromptPlan:
    scene_id = str(scene["id"])
    motion = str(scene["motion_prompt_en"])
    contract = {
        "start_frame_rule": "Use the start keyframe as the exact first frame; do not redesign characters, PPE, vehicles, or site layout.",
        "end_frame_rule": "Land on the end keyframe as the exact final frame so the next clip can continue without a visual jump.",
        "identity_rule": "preserve exact PPE colors, body proportions, BCT shape, dump truck shape, road markings, and plant background.",
        "gaze_rule": "Every character gaze must point toward a visible hazard, signal person, driver, route cue, mirror, or camera display.",
        "causality_rule": "Every movement must have a safety reason visible on screen: stop, check, signal, yield, or stay outside the hazard zone.",
        "motion_rule": "Use slow instructional motion only; no crash, no sudden impact, no dramatic shake, no unsafe action shown as successful.",
    }
    subtitle = str(scene.get("subtitle_ko", scene.get("caption_ko", "")))
    prompt = "\n".join(
        [
            "Generate a 5 second Seedance clip for an industrial safety education video.",
            f"Scene ID: {scene_id}.",
            f"Start keyframe: {scene['start_keyframe']}.",
            f"End keyframe: {scene['end_keyframe']}.",
            f"Motion objective: {motion}",
            f"Sliding chain contract: {contract['start_frame_rule']} {contract['end_frame_rule']}",
            f"Continuity lock: {contract['identity_rule']}",
            f"Gaze motivation: {contract['gaze_rule']}",
            f"Action causality: {contract['causality_rule']}",
            "Text delivery: do not render exact Korean or English text inside generated frames; subtitles and overlays are added in post-production.",
            f"Forbidden motion: {contract['motion_rule']}",
            "Visual style contract: preserve the selected reusable style guide from the keyframes.",
            "Approved style guide and reference assets to preserve:",
            reference_block,
            "Camera: slow 35mm documentary training frame, stable tripod or gentle dolly, no stylized cinematic exaggeration.",
        ]
    )
    return {
        "scene_id": scene_id,
        "start_keyframe": str(scene["start_keyframe"]),
        "end_keyframe": str(scene["end_keyframe"]),
        "prompt": prompt,
        "subtitle_plan_ko": subtitle,
        "reference_assets": reference_assets,
        "sliding_chain_contract": contract,
        "continuity_checklist": _video_continuity_checklist(),
    }


def _continuity_bible() -> dict[str, str]:
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


def _story_flow_context(
    scene: dict,
    previous_scene: dict | None,
    next_scene: dict | None,
    scene_index: int,
    scene_total: int,
) -> dict[str, str]:
    previous = (
        "Opening frame; establish the same site, vehicle lanes, pedestrian route, PPE, and hazard context."
        if previous_scene is None
        else str(previous_scene.get("visual_action_ko", "Continue directly from the previous prevention beat."))
    )
    next_value = (
        "Closing frame; leave the site visibly controlled and ready for a safe ending."
        if next_scene is None
        else str(next_scene.get("visual_action_ko", "Set up the next prevention beat without a visual jump."))
    )
    current = str(scene.get("visual_action_ko", scene.get("educational_goal_ko", "Show the current prevention beat.")))
    return {
        "role": f"keyframe {scene_index} of {scene_total}; preserve causal continuity across adjacent frames",
        "previous": previous,
        "current": current,
        "next": next_value,
    }


def _negative_prompt() -> str:
    return (
        "No Korean text, no English text, no logos, no brand marks, no gore, no injury, no collision impact, "
        "no crushed body, no distorted hands, no extra limbs, no duplicate workers, no inconsistent helmet color, "
        "no different vehicle model, no fantasy style, no dark horror lighting, no blurry low-resolution frame."
    )


def _image_quality_checklist() -> list[str]:
    return [
        "worker-001 PPE matches the continuity bible",
        "BCT and dump truck match previous keyframes",
        "hazard zone and safe pedestrian route are visible",
        "scene action matches the storyboard citation",
        "frame contains no generated text or logo",
    ]


def _previous_blocker_prompt_lines(blockers: list[str]) -> list[str]:
    if not blockers:
        return ["Previous QA blockers for this scene: none recorded."]
    blocker_lines = [f"- {blocker}" for blocker in blockers]
    return [
        "Previous QA blockers for this scene:",
        f"Quality pressure: {QUALITY_PRESSURE}",
        *blocker_lines,
        "Do not repeat:",
        *blocker_lines,
        (
            "Required correction this round: make the blocker visibly impossible to miss while preserving "
            "character identity, PPE, equipment layout, and adjacent-scene continuity."
        ),
    ]


def _video_continuity_checklist() -> list[str]:
    return [
        "first frame matches start keyframe",
        "last frame matches end keyframe",
        "no character, PPE, vehicle, or site redesign occurs",
        "motion illustrates prevention rather than accident impact",
        "clip can connect to the next scene without a jump cut",
    ]
