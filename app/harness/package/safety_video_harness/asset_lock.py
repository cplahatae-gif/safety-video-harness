from __future__ import annotations

from pathlib import Path

IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}
LOCK_REQUIRED_ROLES = ("cast", "equipment", "space_reference")
VIDEO_REFERENCE_ROLES = (
    "cast",
    "equipment",
    "space_reference",
    "work_situation_reference",
    "style_reference",
    "person_reference",
)


def build_asset_lock_manifest(reference_assets: dict[str, list[dict[str, str]]]) -> dict:
    missing_roles = [role for role in LOCK_REQUIRED_ROLES if not _has_image_asset(reference_assets, role)]
    return {
        "version": "1.0",
        "status": "production_locked" if not missing_roles else "draft_exploration_only",
        "missing_roles": missing_roles,
        "text_only_multi_frame_production_allowed": False,
        "independent_text_to_image_generation_allowed": "draft_exploration_only",
        "production_frame_strategy": [
            "create fixed background/space plate before scene keyframes",
            "create fixed cast character sheets or Higgsfield Soul ID references before scene keyframes",
            "create fixed equipment references for BCT, dump truck, PPE, and hazard-zone markings",
            "derive later keyframes from approved prior frames by edit/reference conditioning or deterministic compositing",
            "use approved start/end keyframes plus reference media pack for Seedance clips",
        ],
        "higgsfield_seedance_strategy": {
            "mode": "image_to_video",
            "required_inputs": ["start_image", "end_image"],
            "recommended_reference_inputs": [
                "cast/Soul ID or character sheet",
                "equipment reference",
                "space/background plate",
                "style reference",
            ],
            "forbidden": [
                "text-only multi-shot production",
                "independent scene keyframes without asset lock",
                "Seedance clip generation from prompt only",
            ],
        },
        "reference_media_pack": build_reference_media_pack(reference_assets),
    }


def build_reference_media_pack(reference_assets: dict[str, list[dict[str, str]]]) -> list[dict[str, str]]:
    media: list[dict[str, str]] = []
    for role in VIDEO_REFERENCE_ROLES:
        for asset in reference_assets.get(role, []):
            path = str(asset.get("path", ""))
            if Path(path).suffix.lower() not in IMAGE_SUFFIXES:
                continue
            media.append(
                {
                    "role": role,
                    "path": path,
                    "usage": _media_usage(role),
                    "description": str(asset.get("description", "")),
                }
            )
    return media


def asset_lock_prompt_block(asset_lock: dict) -> str:
    lines = [
        "Production consistency policy:",
        "- Text-only multi-frame production is not allowed for final keyframes.",
        "- Independent scene keyframe generation is draft exploration only.",
        "- Production keyframes require asset lock or reference/edit-based derivation.",
        f"- Current asset lock status: {asset_lock['status']}.",
    ]
    missing = list(asset_lock.get("missing_roles", []))
    if missing:
        lines.append(f"- Missing production lock roles: {', '.join(missing)}.")
    media_pack = list(asset_lock.get("reference_media_pack", []))
    if media_pack:
        lines.append("- Higgsfield/Seedance reference media pack:")
        for media in media_pack:
            lines.append(f"  - {media['role']}: {media['path']} ({media['usage']})")
    else:
        lines.append("- Higgsfield/Seedance reference media pack: none yet; create locked assets before production.")
    return "\n".join(lines)


def media_paths(reference_media_pack: list[dict[str, str]]) -> list[str]:
    return [str(item["path"]) for item in reference_media_pack if item.get("path")]


def _has_image_asset(reference_assets: dict[str, list[dict[str, str]]], role: str) -> bool:
    return any(Path(str(asset.get("path", ""))).suffix.lower() in IMAGE_SUFFIXES for asset in reference_assets.get(role, []))


def _media_usage(role: str) -> str:
    match role:
        case "cast":
            return "character_identity_or_soul_id_source"
        case "equipment":
            return "vehicle_and_equipment_shape_lock"
        case "space_reference":
            return "background_plate_and_lane_geometry_lock"
        case "work_situation_reference":
            return "hazard_control_and_worker_placement_lock"
        case "style_reference":
            return "rendering_style_lock"
        case "person_reference":
            return "pose_gaze_and_signal_action_lock"
        case _:
            return "visual_reference"
