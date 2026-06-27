from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from safety_video_harness.errors import HarnessError
from safety_video_harness.gate_validation import validate_image_to_video_gate
from safety_video_harness.io import read_json, write_json
from safety_video_harness.layout import LayoutKey, layout_for_project
from safety_video_harness.locks import assert_unlocked
from safety_video_harness.storyboard_qa import evaluate_storyboard
from safety_video_harness.validation import validate_project


def approve_gate(project: Path, gate: str, estimated_credits: int | None) -> str:
    layout = layout_for_project(project)
    approvals_path = layout.read_path(LayoutKey.QA_APPROVALS)
    assert_unlocked(approvals_path)
    approvals = read_json(approvals_path)
    gates = approvals["gates"]
    if gate not in gates:
        raise HarnessError(f"unknown gate: {gate}")
    if gate == "storyboard":
        validate_project(project)
        _require_storyboard_qa(project)
    if gate == "image_to_video":
        validate_image_to_video_gate(project, estimated_credits)
    record = gates[gate]
    record["approved"] = True
    record["approved_by"] = "local-user"
    record["approved_at"] = datetime.now(UTC).isoformat()
    record["approved_items"] = _approved_items(project, gate)
    if gate == "image_to_video":
        record["cost_disclosure"] = {
            "estimated_credits": estimated_credits,
            "clip_count": _clip_count(project),
            "seconds_per_clip": _seconds_per_clip(project),
            "total_seconds": _target_seconds(project),
            "regeneration_risk": "medium",
            "pricing_source": "manual_estimate",
            "estimated_at": record["approved_at"],
        }
    write_json(approvals_path, approvals)
    return f"approved gate {gate}"


def _require_storyboard_qa(project: Path) -> None:
    try:
        evaluate_storyboard(project)
    except HarnessError as error:
        raise HarnessError(f"storyboard QA must pass before Gate 1 approval: {error}") from error


def require_gate(project: Path, gate: str) -> None:
    approvals = read_json(layout_for_project(project).read_path(LayoutKey.QA_APPROVALS))
    record = approvals["gates"][gate]
    if not record.get("approved", False):
        raise HarnessError(f"Gate {gate} is not approved")


def _clip_count(project: Path) -> int:
    scenes_path = layout_for_project(project).read_path(LayoutKey.STORY_SCENES)
    if not scenes_path.exists():
        return 0
    return int(read_json(scenes_path).get("clip_count", 0))


def _seconds_per_clip(project: Path) -> int:
    scenes_path = layout_for_project(project).read_path(LayoutKey.STORY_SCENES)
    if not scenes_path.exists():
        return 0
    return int(read_json(scenes_path).get("seconds_per_clip", 0))


def _target_seconds(project: Path) -> int:
    scenes_path = layout_for_project(project).read_path(LayoutKey.STORY_SCENES)
    if not scenes_path.exists():
        return 0
    return int(read_json(scenes_path).get("target_seconds", 0))


def _approved_items(project: Path, gate: str) -> list[str]:
    if gate == "storyboard":
        return ["story/scenes.json"]
    return [f"video-plan-clips:{_clip_count(project)}"]
