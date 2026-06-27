from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from safety_video_harness.layout import LayoutKey, layout_for_project


IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}
ASSET_DIRS = {
    "cast": "refs/people",
    "ppe": "refs/ppe",
    "equipment": "refs/equipment",
    "approved_reference": "refs/approved",
    "person_reference": "refs/approved/people",
    "work_situation_reference": "refs/approved/work",
    "space_reference": "refs/approved/spaces",
    "style_reference": "refs/approved/style",
    "camera_reference": "refs/approved/camera",
    "lighting_reference": "refs/approved/lighting",
}
APPROVED_REFERENCE_ROLES = {
    "root": "refs/approved",
    "person": "refs/approved/people",
    "work": "refs/approved/work",
    "space": "refs/approved/spaces",
    "style": "refs/approved/style",
    "camera": "refs/approved/camera",
    "lighting": "refs/approved/lighting",
}
ROLE_KEYS = {
    "cast": LayoutKey.REFS_CAST,
    "ppe": LayoutKey.REFS_PPE,
    "equipment": LayoutKey.REFS_EQUIPMENT,
    "approved_reference": LayoutKey.REFS_APPROVED,
    "person_reference": LayoutKey.REFS_PERSON,
    "work_situation_reference": LayoutKey.REFS_WORK,
    "space_reference": LayoutKey.REFS_SPACE,
    "style_reference": LayoutKey.REFS_STYLE,
    "camera_reference": LayoutKey.REFS_CAMERA,
    "lighting_reference": LayoutKey.REFS_LIGHTING,
}
APPROVED_ROLE_KEYS = {
    "root": LayoutKey.REFS_APPROVED,
    "person": LayoutKey.REFS_PERSON,
    "work": LayoutKey.REFS_WORK,
    "space": LayoutKey.REFS_SPACE,
    "style": LayoutKey.REFS_STYLE,
    "camera": LayoutKey.REFS_CAMERA,
    "lighting": LayoutKey.REFS_LIGHTING,
}
OLD_APPROVED_REFERENCE_ROLES = {
    "root": "ref/approved",
    "person": "ref/approved/person",
    "work": "ref/approved/work",
    "space": "ref/approved/space",
    "style": "ref/approved/style",
    "camera": "ref/approved/camera",
    "lighting": "ref/approved/lighting",
}


@dataclass(frozen=True, slots=True)
class ReferenceAsset:
    role: str
    path: str
    description: str
    locked_traits: list[str]
    usage: str


def load_catalog(project: Path) -> dict[str, list[ReferenceAsset]]:
    layout = layout_for_project(project)
    return {
        role: _assets_from_dir(project, role, layout.read_path(key))
        for role, key in ROLE_KEYS.items()
    }


def catalog_for_prompt(project: Path) -> dict[str, list[dict[str, str]]]:
    return {
        role: [
            {
                "role": asset.role,
                "path": asset.path,
                "description": asset.description,
            }
            for asset in assets
        ]
        for role, assets in load_catalog(project).items()
    }


def catalog_for_manifest(project: Path) -> list[dict[str, str | list[str]]]:
    manifest_assets: list[dict[str, str | list[str]]] = []
    for assets in load_catalog(project).values():
        for asset in assets:
            manifest_assets.append(
                {
                    "asset_id": Path(asset.path).stem,
                    "role": asset.role,
                    "path": asset.path,
                    "description": asset.description or f"visual reference from {Path(asset.path).name}; manual description not provided",
                    "locked_traits": asset.locked_traits,
                    "usage": asset.usage,
                }
            )
    return manifest_assets


def approved_reference_dir(project: Path, role: str) -> Path:
    if role not in APPROVED_ROLE_KEYS:
        allowed = ", ".join(sorted(APPROVED_ROLE_KEYS))
        raise ValueError(f"role must be one of: {allowed}")
    layout = layout_for_project(project)
    if layout.version == 1:
        return project / OLD_APPROVED_REFERENCE_ROLES[role]
    return layout.write_path(APPROVED_ROLE_KEYS[role])


def _assets_from_dir(project: Path, role: str, asset_dir: Path) -> list[ReferenceAsset]:
    if not asset_dir.exists():
        return []
    image_assets = [
        _asset(project, role, path)
        for path in sorted(asset_dir.iterdir())
        if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES
    ]
    profile_assets = [
        _profile_asset(project, role, path)
        for path in sorted(asset_dir.glob("*.md"))
        if not _has_matching_image(asset_dir, path) and path.name.endswith(".profile.md") is False
    ]
    return image_assets + profile_assets


def _asset(project: Path, role: str, path: Path) -> ReferenceAsset:
    return ReferenceAsset(
        role=role,
        path=str(path.relative_to(project)),
        description=_sidecar_description(path),
        locked_traits=_locked_traits(role),
        usage=_usage_for(role),
    )


def _profile_asset(project: Path, role: str, path: Path) -> ReferenceAsset:
    return ReferenceAsset(
        role=role,
        path=str(path.relative_to(project)),
        description=_read_text(path),
        locked_traits=_locked_traits(role),
        usage=_usage_for(role),
    )


def _sidecar_description(path: Path) -> str:
    sidecar = path.with_suffix(".md")
    if sidecar.exists():
        return _read_text(sidecar)
    profile = _exact_profile_sidecar(path)
    if profile.exists():
        return _read_text(profile)
    return ""


def _exact_profile_sidecar(path: Path) -> Path:
    stem = path.stem
    for suffix in ["-front", "-back", "-left", "-right", "-side"]:
        if stem.endswith(suffix):
            stem = stem.removesuffix(suffix)
            break
    return path.parent / f"{stem}.profile.md"


def _read_text(path: Path) -> str:
    text = path.read_text(encoding="utf-8").strip()
    return " ".join(text.split())


def _has_matching_image(asset_dir: Path, path: Path) -> bool:
    return any((asset_dir / f"{path.stem}{suffix}").exists() for suffix in IMAGE_SUFFIXES)


def _locked_traits(role: str) -> list[str]:
    match role:
        case "cast":
            return ["face", "body proportion", "ppe colors", "workwear"]
        case "ppe":
            return ["color", "shape", "placement"]
        case "equipment":
            return ["vehicle shape", "scale", "color", "wheel count"]
        case "approved_reference":
            return ["style", "camera", "lighting", "texture"]
        case "person_reference":
            return ["pose", "gaze", "ppe", "role action"]
        case "work_situation_reference":
            return ["hazard control", "safe route", "worker placement", "vehicle state"]
        case "space_reference":
            return ["site layout", "lane markings", "pedestrian route", "hazard zone"]
        case "style_reference":
            return ["visual style", "line quality", "color palette", "rendering texture"]
        case "camera_reference":
            return ["framing", "angle", "lens feel", "camera distance"]
        case "lighting_reference":
            return ["lighting direction", "exposure", "shadow softness", "time of day"]
        case _:
            return ["visual identity"]


def _usage_for(role: str) -> str:
    match role:
        case "cast":
            return "identity_reference"
        case "ppe":
            return "ppe_reference"
        case "equipment":
            return "equipment_reference"
        case "approved_reference":
            return "style_reference"
        case "person_reference":
            return "person_reference"
        case "work_situation_reference":
            return "work_situation_reference"
        case "space_reference":
            return "space_reference"
        case "style_reference":
            return "style_reference"
        case "camera_reference":
            return "camera_reference"
        case "lighting_reference":
            return "lighting_reference"
        case _:
            return "visual_reference"
