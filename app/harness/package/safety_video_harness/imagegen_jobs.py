from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
import re
from shutil import copyfile

from safety_video_harness.errors import HarnessError
from safety_video_harness.image_versions import (
    latest_draft,
    next_draft,
    next_preserved_approved,
    project_relative_output,
)
from safety_video_harness.io import read_json, write_json, write_jsonl
from safety_video_harness.layout import LayoutKey, layout_for_project


def build_imagegen_jobs(project: Path, plans: list[dict], scene_filter: str | None, regenerate: bool) -> dict:
    selected = _select_chain_ready_plans(project, plans, scene_filter)
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
            "For sc01, create the anchor keyframe first. For sc02 and later, use the job's anchor_image, "
            "previous_approved_image, reference_images, and allowed_change_only fields as hard inputs. "
            "Do not prepare or run independent text-only multi-frame generation for production keyframes."
        ),
        "jobs": jobs,
    }


def record_image_output(project: Path, scene_id: str, generated_file: Path) -> str:
    if not generated_file.exists():
        raise HarnessError(f"generated file does not exist: {generated_file}")
    jobs_path = layout_for_project(project).read_path(LayoutKey.STORY_IMAGEGEN_JOBS)
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
    jobs_path = layout_for_project(project).read_path(LayoutKey.STORY_IMAGEGEN_JOBS)
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
    _require_scene_image_qa(project, scene_id)
    draft = latest_draft(project, scene_id)
    approved = layout_for_project(project).write_path(LayoutKey.MEDIA_IMAGE_APPROVED) / f"{scene_id}.png"
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


def _require_scene_image_qa(project: Path, scene_id: str) -> None:
    reviews_path = layout_for_project(project).read_path(LayoutKey.QA_ROOT) / "image_reviews.json"
    loop_path = layout_for_project(project).read_path(LayoutKey.QA_ROOT) / "image_qa_loop.json"
    if not reviews_path.exists() or not loop_path.exists():
        raise HarnessError(f"image approval requires passing image QA for {scene_id}")
    payload = read_json(reviews_path)
    if bool(payload.get("dry_run", False)):
        raise HarnessError(f"image approval requires live image QA for {scene_id}, not dry-run image QA")
    review = next(
        (
            item
            for item in list(payload.get("reviews", []))
            if isinstance(item, dict) and item.get("scene_id") == scene_id
        ),
        None,
    )
    if review is None:
        raise HarnessError(f"image approval requires image QA coverage for {scene_id}")
    manual = review.get("manual_visual_review")
    if not isinstance(manual, dict) or manual.get("status") != "present":
        raise HarnessError(f"image approval requires manual visual image QA for {scene_id}")
    if review.get("blocking_issues"):
        raise HarnessError(f"image approval requires image QA without blockers for {scene_id}")
    loop = read_json(loop_path)
    if not bool(loop.get("passed", False)):
        raise HarnessError(f"image approval requires passing image QA loop for {scene_id}")


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
    generation_chain = _generation_chain(project, scene_id, plan)
    return {
        "scene_id": scene_id,
        "tool": "codex_builtin_imagegen",
        "status": "pending_imagegen",
        "prompt": plan["prompt"],
        "negative_prompt": plan.get("negative_prompt", ""),
        "reference_assets": plan.get("reference_assets", {}),
        "asset_lock": plan.get("asset_lock", {}),
        "generation_chain": generation_chain,
        "anchor_image": generation_chain["anchor_image"],
        "previous_approved_image": generation_chain["previous_approved_image"],
        "reference_images": generation_chain["reference_images"],
        "allowed_change_only": generation_chain["allowed_change_only"],
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


def _select_chain_ready_plans(project: Path, plans: list[dict], scene_filter: str | None) -> list[dict]:
    if scene_filter is not None:
        selected = [_plan for _plan in plans if _plan["scene_id"] == scene_filter]
        if selected:
            _require_previous_keyframe(project, str(selected[0]["scene_id"]))
        return selected
    for plan in plans:
        scene_id = str(plan["scene_id"])
        if _approved_keyframe(project, scene_id).exists():
            continue
        _require_previous_keyframe(project, scene_id)
        return [plan]
    return []


def _generation_chain(project: Path, scene_id: str, plan: dict) -> dict[str, object]:
    anchor = _approved_keyframe(project, "sc01")
    previous = _previous_approved_keyframe(project, scene_id)
    mode = "anchor_keyframe" if scene_id == "sc01" else "sequential_reference_edit"
    reference_images = _reference_images(project, anchor, previous, plan)
    return {
        "mode": mode,
        "anchor_image": _project_relative_if_exists(project, anchor),
        "previous_approved_image": _project_relative_if_exists(project, previous),
        "reference_images": reference_images,
        "allowed_change_only": (
            "Change only the current storyboard beat. Preserve character identity, PPE, vehicle geometry, "
            "plant background, floor/lane markings, pedestrian route, hazard-zone location, camera grammar, and style."
        ),
        "stop_if_missing_reference": (
            "For sc02 and later, stop before generation if previous_approved_image is empty. "
            "For sc03 and later, also preserve anchor_image from sc01."
        ),
    }


def _reference_images(project: Path, anchor: Path, previous: Path | None, plan: dict) -> list[str]:
    paths = [_project_relative_if_exists(project, anchor), _project_relative_if_exists(project, previous)]
    asset_lock = plan.get("asset_lock", {})
    if isinstance(asset_lock, dict):
        for item in asset_lock.get("reference_media_pack", []):
            if isinstance(item, dict):
                paths.append(str(item.get("path", "")))
    return [path for index, path in enumerate(paths) if path and path not in paths[:index]]


def _require_previous_keyframe(project: Path, scene_id: str) -> None:
    if scene_id == "sc01":
        return
    index = _scene_index(scene_id)
    if index is not None and index >= 3 and not _approved_keyframe(project, "sc01").exists():
        raise HarnessError(f"anchor approved keyframe sc01 is required before preparing {scene_id}")
    previous = _previous_approved_keyframe(project, scene_id)
    if previous is None or not previous.exists():
        raise HarnessError(f"previous approved keyframe is required before preparing {scene_id}")


def _previous_approved_keyframe(project: Path, scene_id: str) -> Path | None:
    index = _scene_index(scene_id)
    if index is None or index <= 1:
        return None
    return _approved_keyframe(project, f"sc{index - 1:02d}")


def _approved_keyframe(project: Path, scene_id: str) -> Path:
    return layout_for_project(project).read_path(LayoutKey.MEDIA_IMAGE_APPROVED) / f"{scene_id}.png"


def _project_relative_if_exists(project: Path, path: Path | None) -> str:
    if path is None or not path.exists():
        return ""
    return str(path.relative_to(project))


def _scene_index(scene_id: str) -> int | None:
    match = re.fullmatch(r"sc(\d+)", scene_id)
    if match is None:
        return None
    return int(match.group(1))
