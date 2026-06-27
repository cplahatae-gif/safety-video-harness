from __future__ import annotations

from pathlib import Path

from safety_video_harness.errors import HarnessError
from safety_video_harness.layout import LayoutKey, layout_for_project


def latest_draft(project: Path, scene_id: str) -> Path:
    drafts = sorted(layout_for_project(project).read_path(LayoutKey.MEDIA_IMAGE_DRAFT).glob(f"{scene_id}_v*.png"))
    if not drafts:
        raise HarnessError(f"draft image missing for {scene_id}")
    return drafts[-1]


def latest_draft_or_none(project: Path, scene_id: str) -> Path | None:
    drafts = sorted(layout_for_project(project).read_path(LayoutKey.MEDIA_IMAGE_DRAFT).glob(f"{scene_id}_v*.png"))
    if not drafts:
        return None
    return drafts[-1]


def next_draft(project: Path, scene_id: str, regenerate: bool) -> Path:
    draft_dir = layout_for_project(project).write_path(LayoutKey.MEDIA_IMAGE_DRAFT)
    draft_dir.mkdir(parents=True, exist_ok=True)
    existing = sorted(draft_dir.glob(f"{scene_id}_v*.png"))
    if existing and not regenerate:
        raise HarnessError(f"draft image already exists for {scene_id}; use --regenerate")
    return draft_dir / f"{scene_id}_v{_next_version(existing):03d}.png"


def next_preserved_approved(project: Path, scene_id: str) -> Path:
    approved_dir = layout_for_project(project).write_path(LayoutKey.MEDIA_IMAGE_APPROVED)
    existing = sorted(approved_dir.glob(f"{scene_id}_v*.png"))
    return approved_dir / f"{scene_id}_v{_next_version(existing):03d}.png"


def project_relative_output(project: Path, relative_path: str) -> Path:
    output = project / relative_path
    project_root = project.resolve()
    resolved = output.resolve()
    if not resolved.is_relative_to(project_root):
        raise HarnessError(f"imagegen output path is outside project: {relative_path}")
    return output


def _next_version(paths: list[Path]) -> int:
    versions = [_version_from_path(path) for path in paths]
    return max(versions, default=0) + 1


def _version_from_path(path: Path) -> int:
    version_text = path.stem.rsplit("_v", 1)[-1]
    try:
        return int(version_text)
    except ValueError:
        return 0
