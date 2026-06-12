from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from shutil import copyfile

from safety_video_harness.errors import HarnessError
from safety_video_harness.image_versions import (
    latest_draft,
    next_draft,
    next_preserved_approved,
    project_relative_output,
)
from safety_video_harness.io import read_json, write_json, write_jsonl


def build_imagegen_jobs(project: Path, plans: list[dict], scene_filter: str | None, regenerate: bool) -> dict:
    selected = [_plan for _plan in plans if scene_filter is None or _plan["scene_id"] == scene_filter]
    if scene_filter is not None and not selected:
        raise HarnessError(f"unknown scene_id: {scene_filter}")
    jobs = [_job_for_plan(project, plan, regenerate) for plan in selected]
    return {
        "execution_mode": "codex_builtin_imagegen",
        "status": "pending_imagegen",
        "created_at": datetime.now(UTC).isoformat(),
        "instruction": (
            "Use Codex built-in imagegen skill/tool for each job. After generation, move or copy "
            "the selected output into the job output path. Do not use an API or CLI fallback unless explicitly requested."
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
    output = project_relative_output(project, str(job["output"]))
    if output.exists():
        output = next_draft(project, scene_id, regenerate=True)
        job["output"] = str(output.relative_to(project))
        job["version"] = output.stem.removeprefix(f"{scene_id}_v")
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
    draft = latest_draft(project, scene_id)
    approved = project / "images" / "approved" / f"{scene_id}.png"
    approved.parent.mkdir(parents=True, exist_ok=True)
    if approved.exists():
        preserved = next_preserved_approved(project, scene_id)
        approved.replace(preserved)
    copyfile(draft, approved)
    write_jsonl(
        project / "qa" / "image_generation_runs.jsonl",
        {"event": "approved", "scene_id": scene_id, "source": str(draft.relative_to(project)), "output": str(approved.relative_to(project))},
    )
    return f"approved image {scene_id}"


def _job_for_plan(project: Path, plan: dict, regenerate: bool) -> dict:
    scene_id = str(plan["scene_id"])
    output = next_draft(project, scene_id, regenerate)
    return {
        "scene_id": scene_id,
        "tool": "codex_builtin_imagegen",
        "status": "pending_imagegen",
        "prompt": plan["prompt"],
        "negative_prompt": plan.get("negative_prompt", ""),
        "reference_assets": plan.get("reference_assets", {}),
        "output": str(output.relative_to(project)),
        "version": output.stem.removeprefix(f"{scene_id}_v"),
        "preserve_project_output": True,
    }
