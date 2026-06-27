from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from shutil import copyfile

from safety_video_harness.errors import HarnessError
from safety_video_harness.io import read_json, write_json, write_jsonl


def build_imagegen_jobs(project: Path, plans: list[dict], scene_filter: str | None, regenerate: bool) -> dict:
    selected = [_plan for _plan in plans if scene_filter is None or _plan["scene_id"] == scene_filter]
    if scene_filter is not None and not selected:
        raise HarnessError(f"unknown scene_id: {scene_filter}")
    jobs = [_job_for_plan(project, plan, regenerate) for plan in selected]
    return {
        "execution_mode": "codex_cli_imagegen",
        "status": "pending_imagegen",
        "created_at": datetime.now(UTC).isoformat(),
        "instruction": (
            "Run scripts/codex_image.sh <output> \"<prompt>\" [reference images...] for each job. "
            "Save the output directly at the job output path. Use scripts/gemini_image.sh only when the user explicitly requests the Gemini fallback."
        ),
        "jobs": jobs,
    }


def record_image_output(project: Path, scene_id: str, generated_file: Path) -> str:
    if not generated_file.exists():
        raise HarnessError(f"generated file does not exist: {generated_file}")
    jobs_path = project / "prompts" / "imagegen_jobs.json"
    if not jobs_path.exists():
        raise HarnessError("imagegen_jobs.json is missing")
    jobs_payload = read_json(jobs_path)
    jobs = list(jobs_payload.get("jobs", []))
    job = next((item for item in jobs if item.get("scene_id") == scene_id), None)
    if job is None:
        raise HarnessError(f"imagegen job not found for {scene_id}")
    output = _project_relative_output(project, str(job["output"]))
    if output.exists():
        raise HarnessError(f"draft image already exists: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    copyfile(generated_file, output)
    job["status"] = "recorded"
    job["recorded_at"] = datetime.now(UTC).isoformat()
    job["source_file"] = str(generated_file)
    write_json(jobs_path, jobs_payload)
    write_jsonl(
        project / "qa" / "image_generation_runs.jsonl",
        {"event": "recorded", "scene_id": scene_id, "output": str(output.relative_to(project))},
    )
    return f"recorded image output {scene_id} -> {output.relative_to(project)}"


def approve_image(project: Path, scene_id: str) -> str:
    draft = _latest_draft(project, scene_id)
    approved = project / "images" / "approved" / f"{scene_id}.png"
    approved.parent.mkdir(parents=True, exist_ok=True)
    if approved.exists():
        preserved = _next_preserved_approved(project, scene_id)
        approved.replace(preserved)
    copyfile(draft, approved)
    write_jsonl(
        project / "qa" / "image_generation_runs.jsonl",
        {"event": "approved", "scene_id": scene_id, "source": str(draft.relative_to(project)), "output": str(approved.relative_to(project))},
    )
    return f"approved image {scene_id}"


def _job_for_plan(project: Path, plan: dict, regenerate: bool) -> dict:
    scene_id = str(plan["scene_id"])
    output = _next_draft_path(project, scene_id, regenerate)
    return {
        "scene_id": scene_id,
        "tool": "codex_cli_imagegen",
        "status": "pending_imagegen",
        "prompt": plan["prompt"],
        "negative_prompt": plan.get("negative_prompt", ""),
        "reference_assets": plan.get("reference_assets", {}),
        "output": str(output.relative_to(project)),
        "version": output.stem.removeprefix(f"{scene_id}_v"),
        "preserve_project_output": True,
    }


def _project_relative_output(project: Path, relative: str) -> Path:
    output = project / relative
    try:
        output.resolve().relative_to(project.resolve())
    except ValueError as exc:
        raise HarnessError(f"imagegen output path is outside project: {output}") from exc
    return output


def _max_version(paths: list[Path], scene_id: str) -> int:
    versions = []
    for path in paths:
        suffix = path.stem.removeprefix(f"{scene_id}_v")
        if suffix.isdigit():
            versions.append(int(suffix))
    return max(versions, default=0)


def _next_draft_path(project: Path, scene_id: str, regenerate: bool) -> Path:
    draft_dir = project / "images" / "draft"
    draft_dir.mkdir(parents=True, exist_ok=True)
    existing = sorted(draft_dir.glob(f"{scene_id}_v*.png"))
    if existing and not regenerate:
        raise HarnessError(f"draft image already exists for {scene_id}; use --regenerate")
    version = _max_version(existing, scene_id) + 1
    return draft_dir / f"{scene_id}_v{version:03d}.png"


def _latest_draft(project: Path, scene_id: str) -> Path:
    drafts = sorted((project / "images" / "draft").glob(f"{scene_id}_v*.png"))
    if not drafts:
        raise HarnessError(f"draft image missing for {scene_id}")
    return drafts[-1]


def _next_preserved_approved(project: Path, scene_id: str) -> Path:
    approved_dir = project / "images" / "approved"
    existing = sorted(approved_dir.glob(f"{scene_id}_v*.png"))
    version = _max_version(existing, scene_id) + 1
    return approved_dir / f"{scene_id}_v{version:03d}.png"
