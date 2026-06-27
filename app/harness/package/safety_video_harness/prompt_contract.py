from __future__ import annotations

from typing import TypedDict

from safety_video_harness.prompt_contract_defaults import (
    continuity_bible,
    image_quality_checklist,
    negative_prompt,
    video_continuity_checklist,
)
from safety_video_harness.ralph_prompt import previous_blocker_prompt_lines


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
    duration_sec: int
    prompt: str
    subtitle_plan_ko: str
    reference_assets: dict[str, list[dict[str, str]]]
    reference_media_pack: list[dict[str, str]]
    asset_lock: dict
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
    continuity = continuity_bible()
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
            (
                "Production warning: if this keyframe is for final Seedance use, do not rely on this text prompt alone. "
                "Use the project asset-lock manifest, approved reference media, or edit/compositing derivation from a prior approved frame."
            ),
            "Approved style guide and reference assets to preserve:",
            reference_block,
            "Safety framing: show a near-miss prevention moment, not an accident impact.",
            "Output must be clean, readable, realistic enough for worker education, and free of generated text.",
            (
                "Prompting reference: follow the local Codex imagegen skill and the official image generation guide; "
                "avoid precise in-image text because image models can struggle with exact text rendering and layout."
            ),
        ]
    )
    return {
        "scene_id": scene_id,
        "output": f"media/images/draft/{scene_id}.png",
        "prompt": prompt,
        "negative_prompt": negative_prompt(),
        "reference_assets": reference_assets,
        "continuity_bible": continuity,
        "quality_checklist": image_quality_checklist(),
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
    continuity = continuity_bible()
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
            (
                "Production warning: this final keyframe must be derived from approved locked assets or reference/edit conditioning; "
                "pure text-to-image generation is draft exploration only."
            ),
            "Approved style guide and reference assets to preserve:",
            reference_block,
            "Safety framing: show a completed near-miss prevention moment, not an accident impact.",
            "Output must be clean, readable, realistic enough for worker education, and free of generated text.",
        ]
    )
    return {
        "scene_id": scene_id,
        "output": f"media/images/draft/{scene_id}.png",
        "prompt": prompt,
        "negative_prompt": negative_prompt(),
        "reference_assets": reference_assets,
        "continuity_bible": continuity,
        "quality_checklist": image_quality_checklist(),
    }


def build_video_prompt_plan(
    scene: dict,
    reference_assets: dict[str, list[dict[str, str]]],
    reference_block: str,
    asset_lock: dict,
) -> VideoPromptPlan:
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
            "Create a Seedance clip for an industrial safety education video.",
            f"Scene ID: {scene_id}.",
            f"Start keyframe: {scene['start_keyframe']}.",
            f"End keyframe: {scene['end_keyframe']}.",
            "Reference media policy: use the approved start keyframe, approved end keyframe, and all available Higgsfield media references as identity, equipment, space, and style locks.",
            "If a Higgsfield Soul ID exists for a worker, use it as the identity lock; otherwise use the cast reference sheet from the media pack.",
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
            "Do not treat the text prompt as the only source of truth; the media references and start/end keyframes are the lock layer.",
            "Camera: slow 35mm documentary training frame, stable tripod or gentle dolly, no stylized cinematic exaggeration.",
        ]
    )
    return {
        "scene_id": scene_id,
        "start_keyframe": str(scene["start_keyframe"]),
        "end_keyframe": str(scene["end_keyframe"]),
        "duration_sec": 5,
        "prompt": prompt,
        "subtitle_plan_ko": subtitle,
        "reference_assets": reference_assets,
        "reference_media_pack": list(asset_lock.get("reference_media_pack", [])),
        "asset_lock": asset_lock,
        "sliding_chain_contract": contract,
        "continuity_checklist": video_continuity_checklist(),
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


def _previous_blocker_prompt_lines(blockers: list[str]) -> list[str]:
    return previous_blocker_prompt_lines(blockers)
