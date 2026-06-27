from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from shutil import copy2

from safety_video_harness.errors import HarnessError
from safety_video_harness.io import read_json, write_json
from safety_video_harness.layout import CANONICAL_PROJECT_DIRS, PROJECT_LAYOUT_VERSION


@dataclass(frozen=True, slots=True)
class PathMapping:
    source: str
    destination: str
    recursive: bool = True


PROJECT_MIGRATION_MAP: tuple[PathMapping, ...] = (
    PathMapping("sources/raw", "input/sources/raw"),
    PathMapping("sources/rendered", "input/sources/rendered"),
    PathMapping("sources/sources.json", "input/sources.json", recursive=False),
    PathMapping("sources/extracted_topics.json", "input/extracted_topics.json", recursive=False),
    PathMapping("sources/source_facts.json", "input/source_facts.json", recursive=False),
    PathMapping("model/cast", "refs/people"),
    PathMapping("model/ppe", "refs/ppe"),
    PathMapping("product/equipment", "refs/equipment"),
    PathMapping("ref/candidates", "refs/candidates"),
    PathMapping("ref/approved", "refs/approved", recursive=False),
    PathMapping("ref/approved/person", "refs/approved/people"),
    PathMapping("ref/approved/work", "refs/approved/work"),
    PathMapping("ref/approved/space", "refs/approved/spaces"),
    PathMapping("ref/approved/style", "refs/approved/style"),
    PathMapping("ref/approved/camera", "refs/approved/camera"),
    PathMapping("ref/approved/lighting", "refs/approved/lighting"),
    PathMapping("style", "refs/approved/style"),
    PathMapping("asset-lock", "refs/asset-lock"),
    PathMapping("storyboard/versions", "story/versions"),
    PathMapping("storyboard/scenes.json", "story/scenes.json", recursive=False),
    PathMapping("prompts/image_prompts.json", "story/image_prompts.json", recursive=False),
    PathMapping("prompts/video_prompts.json", "story/video_prompts.json", recursive=False),
    PathMapping("prompts/image_prompt_team_plan.json", "story/image_prompt_team_plan.json", recursive=False),
    PathMapping("prompts/imagegen_jobs.json", "story/imagegen_jobs.json", recursive=False),
    PathMapping("images/draft", "media/images/draft"),
    PathMapping("images/approved", "media/images/approved"),
    PathMapping("images/rejected", "media/images/rejected"),
    PathMapping("video/clips", "media/video/clips"),
    PathMapping("video/sampled_frames", "media/video/sampled_frames"),
    PathMapping("video/inspection", "media/video/inspection"),
    PathMapping("audio", "media/audio"),
    PathMapping("subtitles", "media/subtitles"),
    PathMapping("output", "media/output"),
    PathMapping("approvals.json", "qa/approvals.json", recursive=False),
    PathMapping(".harness", "qa/state"),
    PathMapping("evidence", "qa/evidence"),
)


def migrate_project_structure(
    project: Path,
    *,
    dry_run: bool,
    write: bool,
    evidence_dir: Path | None = None,
    allow_overwrite_unapproved: bool = False,
) -> str:
    if dry_run == write:
        raise HarnessError("choose exactly one of --dry-run or --write")
    if not project.exists():
        raise HarnessError(f"project does not exist: {project}")
    changes, conflicts = _planned_file_changes(project, allow_overwrite_unapproved)
    if conflicts:
        raise HarnessError(conflicts[0]["message"])
    copied_count = 0
    if write:
        _create_canonical_dirs(project)
        for change in changes:
            if change["action"] == "copy":
                _copy_file(project / change["source"], project / change["destination"])
                copied_count += 1
        _write_project_config(project)
    report = {
        "dry_run": dry_run,
        "write": write,
        "project": str(project),
        "planned_changes": changes,
        "conflicts": conflicts,
        "copied_count": copied_count,
        "canonical_dirs": list(CANONICAL_PROJECT_DIRS),
    }
    report_dir = evidence_dir or Path("projects/_runs/folder-migration")
    write_json(report_dir / "migration_report.json", report)
    return f"migration {'dry-run' if dry_run else 'write'} complete: {copied_count} copied"


def _planned_file_changes(project: Path, allow_overwrite_unapproved: bool) -> tuple[list[dict], list[dict]]:
    changes: list[dict] = []
    conflicts: list[dict] = []
    for mapping in PROJECT_MIGRATION_MAP:
        source = project / mapping.source
        if not source.exists():
            continue
        for source_file, destination in _iter_mapping_files(source, project / mapping.destination, mapping.recursive):
            relative_source = str(source_file.relative_to(project))
            relative_destination = str(destination.relative_to(project))
            action, message = _copy_decision(source_file, destination, relative_destination, allow_overwrite_unapproved)
            if message:
                conflicts.append({"source": relative_source, "destination": relative_destination, "message": message})
            else:
                changes.append({"source": relative_source, "destination": relative_destination, "action": action})
    return changes, conflicts


def _iter_mapping_files(source: Path, destination: Path, recursive: bool) -> list[tuple[Path, Path]]:
    if source.is_file():
        return [(source, destination)]
    if not recursive:
        return [(path, destination / path.name) for path in sorted(source.iterdir()) if path.is_file()]
    return [(path, destination / path.relative_to(source)) for path in sorted(source.rglob("*")) if path.is_file()]


def _copy_decision(source: Path, destination: Path, relative_destination: str, allow_overwrite_unapproved: bool) -> tuple[str, str]:
    if not destination.exists():
        return "copy", ""
    if source.read_bytes() == destination.read_bytes():
        return "unchanged", ""
    if _is_approved_asset(relative_destination):
        return "conflict", f"refusing to overwrite approved asset: {relative_destination}"
    if not allow_overwrite_unapproved:
        return "conflict", f"destination already exists: {relative_destination}"
    return "copy", ""


def _is_approved_asset(relative_path: str) -> bool:
    return relative_path.startswith("media/images/approved/") or relative_path.startswith("media/video/clips/")


def _copy_file(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    copy2(source, destination)


def _create_canonical_dirs(project: Path) -> None:
    for relative_path in CANONICAL_PROJECT_DIRS:
        (project / relative_path).mkdir(parents=True, exist_ok=True)


def _write_project_config(project: Path) -> None:
    config_path = project / "project_config.json"
    config = read_json(config_path) if config_path.exists() else {}
    config["project_layout_version"] = PROJECT_LAYOUT_VERSION
    write_json(config_path, config)
