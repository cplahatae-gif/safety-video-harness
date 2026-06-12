from __future__ import annotations

from pathlib import Path

from safety_video_harness.reference_catalog import ASSET_DIRS, IMAGE_SUFFIXES, catalog_for_prompt


def load_reference_assets(project: Path) -> dict[str, list[dict[str, str]]]:
    return catalog_for_prompt(project)


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
