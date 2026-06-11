from __future__ import annotations

from pathlib import Path

IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}
ASSET_DIRS = {
    "cast": "model/cast",
    "ppe": "model/ppe",
    "equipment": "product/equipment",
    "approved_reference": "ref/approved",
}


def load_reference_assets(project: Path) -> dict[str, list[dict[str, str]]]:
    return {
        role: _assets_from_dir(project, role, relative_dir)
        for role, relative_dir in ASSET_DIRS.items()
    }


def reference_assets_prompt_block(reference_assets: dict[str, list[dict[str, str]]]) -> str:
    lines: list[str] = []
    for role, assets in reference_assets.items():
        if not assets:
            continue
        lines.append(f"{role}:")
        for asset in assets:
            description = asset["description"] or "use visual details from this reference exactly when relevant"
            lines.append(f"- {asset['path']}: {description}")
    if not lines:
        return "No approved visual reference assets provided; use the continuity bible only."
    return "\n".join(lines)


def _assets_from_dir(project: Path, role: str, relative_dir: str) -> list[dict[str, str]]:
    asset_dir = project / relative_dir
    image_assets = [_asset(project, role, path) for path in sorted(asset_dir.glob("*")) if path.suffix.lower() in IMAGE_SUFFIXES]
    profile_assets = [
        _profile_asset(project, role, path)
        for path in sorted(asset_dir.glob("*.md"))
        if not _has_matching_image(asset_dir, path)
    ]
    return image_assets + profile_assets


def _asset(project: Path, role: str, path: Path) -> dict[str, str]:
    return {
        "role": role,
        "path": str(path.relative_to(project)),
        "description": _sidecar_description(path),
    }


def _profile_asset(project: Path, role: str, path: Path) -> dict[str, str]:
    return {
        "role": role,
        "path": str(path.relative_to(project)),
        "description": _read_text(path),
    }


def _sidecar_description(path: Path) -> str:
    sidecar = path.with_suffix(".md")
    if sidecar.exists():
        return _read_text(sidecar)
    profile_sidecars = sorted(path.parent.glob(f"{path.stem.split('-front')[0]}*.profile.md"))
    if profile_sidecars:
        return _read_text(profile_sidecars[0])
    return ""


def _read_text(path: Path) -> str:
    text = path.read_text(encoding="utf-8").strip()
    return " ".join(text.split())


def _has_matching_image(asset_dir: Path, path: Path) -> bool:
    return any((asset_dir / f"{path.stem}{suffix}").exists() for suffix in IMAGE_SUFFIXES)
