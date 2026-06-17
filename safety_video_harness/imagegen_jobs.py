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
            "the selected output into the job output path. Do not use an API or CLI fallback unless explicitly requested. "
            "For production keyframes, do not rely on independent text-only generation; use asset-lock references, "
            "edit/reference conditioning, or deterministic compositing."
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


def collect_image_outputs(project: Path, source_dir: Path) -> str:
    if not source_dir.exists():
        raise HarnessError(f"generated image directory does not exist: {source_dir}")
    jobs_path = project / "prompts" / "imagegen_jobs.json"
    if not jobs_path.exists():
        raise HarnessError("imagegen_jobs.json is missing")
    jobs_payload = read_json(jobs_path)
    recorded: list[str] = []
    for job in list(jobs_payload.get("jobs", [])):
        scene_id = str(job.get("scene_id", ""))
        candidate = _generated_candidate(source_dir, scene_id)
        if candidate is None:
            continue
        record_image_output(project, scene_id, candidate)
        recorded.append(scene_id)
    if not recorded:
        raise HarnessError(f"no generated image files matched pending jobs in {source_dir}")
    return f"collected {len(recorded)} generated image output(s): {', '.join(recorded)}"


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


def _generated_candidate(source_dir: Path, scene_id: str) -> Path | None:
    suffixes = [".png", ".jpg", ".jpeg", ".webp"]
    exact = [source_dir / f"{scene_id}{suffix}" for suffix in suffixes]
    for path in exact:
        if path.exists():
            return path
    matches = sorted(
        path
        for path in source_dir.iterdir()
        if path.is_file() and path.suffix.lower() in suffixes and scene_id in path.stem
    )
    if not matches:
        return None
    return matches[0]


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
        "asset_lock": plan.get("asset_lock", {}),
        "production_consistency_policy": {
            "text_only_multi_frame_production_allowed": False,
            "independent_text_to_image_generation": "draft_exploration_only",
            "final_keyframes_require": "asset lock, reference/edit chain, or deterministic compositing",
            "preferred_generation_order": [
                "use approved cast/equipment/space/style references as inputs",
                "derive from the previous approved keyframe when continuity is more important than novelty",
                "use deterministic compositing for fixed background plates, lane markings, hazard zones, and stable vehicle placement",
                "run build_image_visual_review.py before Gate 2 and fix any visual-lock blocker",
            ],
        },
        "output": str(output.relative_to(project)),
        "version": output.stem.removeprefix(f"{scene_id}_v"),
        "preserve_project_output": True,
    }
