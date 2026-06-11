from __future__ import annotations

import json
from pathlib import Path

from safety_video_harness.blocker_signatures import blocker_signature
from safety_video_harness.evaluation_markdown import (
    markdown_artifacts,
    markdown_key_values,
    markdown_list,
    markdown_repeated,
    string_dict,
)
from safety_video_harness.io import JsonObject, write_json, write_jsonl
from safety_video_harness.locks import assert_unlocked


LEDGER_PATH = Path("qa") / "evaluation_rounds.jsonl"
WIKI_PATH = Path("llm-wiki") / "evaluation-rounds.md"


def completed_iterations(project: Path, stage: str, item_id: str) -> int:
    return sum(
        1
        for entry in _read_round_entries(project)
        if entry.get("stage") == stage and entry.get("item_id") == item_id
    )


def previous_blocking_issues(project: Path, stage: str, item_id: str, limit: int = 5) -> list[str]:
    issues: list[str] = []
    for entry in reversed(_read_round_entries(project)):
        if entry.get("stage") != stage or entry.get("item_id") != item_id:
            continue
        for issue in list(entry.get("blocking_issues", [])):
            text = str(issue)
            if text not in issues:
                issues.append(text)
            if len(issues) >= limit:
                return issues
    return issues


def write_evaluation_bundle(
    project: Path,
    stage: str,
    item_id: str,
    iteration: int,
    payload: JsonObject,
) -> Path:
    bundle_path = (
        project
        / "qa"
        / "evaluation_bundles"
        / stage
        / item_id
        / f"round_{iteration:03d}.json"
    )
    write_json(bundle_path, payload)
    return bundle_path


def record_evaluation_round(
    project: Path,
    stage: str,
    item_id: str,
    iteration: int,
    review: JsonObject,
    bundle_path: Path,
) -> None:
    blocking_issues = [str(issue) for issue in list(review.get("blocking_issues", []))]
    blocker_signatures = _review_blocker_signatures(stage, item_id, review, blocking_issues)
    bundle = _read_bundle(bundle_path)
    score_breakdown = _score_breakdown(review)
    artifact_map = _artifact_map(review, bundle)
    artifact_paths = list(artifact_map.values())
    improvement_notes = _improvement_notes(review)
    next_prompt_memory = _next_prompt_memory(blocking_issues, improvement_notes)
    repeated_blockers = _repeated_blockers(project, stage, item_id, blocker_signatures)
    record: JsonObject = {
        "stage": stage,
        "item_id": item_id,
        "iteration": iteration,
        "decision": str(review.get("decision", "")),
        "total_score": int(review.get("total_score", 0)),
        "score_breakdown": score_breakdown,
        "artifact_map": artifact_map,
        "artifact_paths": artifact_paths,
        "blocking_issues": blocking_issues,
        "blocker_signatures": blocker_signatures,
        "improvement_notes": improvement_notes,
        "next_prompt_memory": next_prompt_memory,
        "repeated_blockers": repeated_blockers,
        "bundle_path": str(bundle_path.relative_to(project)),
    }
    write_jsonl(project / LEDGER_PATH, record)
    _append_wiki_summary(project, record)


def _read_round_entries(project: Path) -> list[JsonObject]:
    ledger = project / LEDGER_PATH
    if not ledger.exists():
        return []
    entries: list[JsonObject] = []
    for line in ledger.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        value = json.loads(line)
        if isinstance(value, dict):
            entries.append(value)
    return entries


def _review_blocker_signatures(
    stage: str,
    item_id: str,
    review: JsonObject,
    blocking_issues: list[str],
) -> list[str]:
    signatures: list[str] = []
    for signature in list(review.get("blocker_signatures", [])):
        text = str(signature)
        if text not in signatures:
            signatures.append(text)
    for issue in blocking_issues:
        signature = blocker_signature(stage, item_id, issue)
        if signature not in signatures:
            signatures.append(signature)
    return signatures


def _append_wiki_summary(project: Path, record: JsonObject) -> None:
    path = project / WIKI_PATH
    assert_unlocked(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text("# Evaluation Rounds\n\n", encoding="utf-8")
    issues = list(record.get("blocking_issues", []))
    signatures = list(record.get("blocker_signatures", []))
    score_breakdown = string_dict(record.get("score_breakdown", {}))
    artifact_map = string_dict(record.get("artifact_map", {}))
    improvement_notes = [str(note) for note in list(record.get("improvement_notes", []))]
    next_prompt_memory = [str(note) for note in list(record.get("next_prompt_memory", []))]
    repeated_blockers = string_dict(record.get("repeated_blockers", {}))
    issue_text = "없음" if not issues else "; ".join(str(issue) for issue in issues)
    signature_text = "없음" if not signatures else "; ".join(str(signature) for signature in signatures)
    block = "\n".join(
        [
            f"## {record['stage']} / {record['item_id']} / round {record['iteration']}",
            "",
            f"- decision: `{record['decision']}`",
            f"- total_score: `{record['total_score']}`",
            f"- blocking_issues: {issue_text}",
            f"- blocker_signatures: {signature_text}",
            f"- bundle: `{record['bundle_path']}`",
            "",
            "### Scores",
            *markdown_key_values(score_breakdown),
            "",
            "### Round Outputs",
            *markdown_artifacts(artifact_map),
            "",
            "### Improvement Notes",
            *markdown_list(improvement_notes),
            "",
            "### Next Prompt Memory",
            *markdown_list(next_prompt_memory),
            "",
            "### Repeated Blockers",
            *markdown_repeated(repeated_blockers),
            "",
        ]
    )
    with path.open("a", encoding="utf-8") as handle:
        handle.write(block)


def _read_bundle(bundle_path: Path) -> JsonObject:
    if not bundle_path.exists():
        return {}
    value = json.loads(bundle_path.read_text(encoding="utf-8"))
    return value if isinstance(value, dict) else {}


def _score_breakdown(review: JsonObject) -> JsonObject:
    scores: JsonObject = {}
    for key, value in review.items():
        if key.endswith("_score") and isinstance(value, int):
            scores[key] = value
    total_score = review.get("total_score")
    if isinstance(total_score, int):
        scores["total_score"] = total_score
    return scores


def _artifact_map(review: JsonObject, bundle: JsonObject) -> JsonObject:
    paths: JsonObject = {}
    _append_artifact(paths, review.get("reviewed_asset"), "reviewed_asset")
    _append_artifact(paths, review.get("clip"), "clip")
    _append_artifact(paths, review.get("inspection_manifest"), "inspection_manifest")
    scene = bundle.get("scene")
    if isinstance(scene, dict):
        _append_artifact(paths, scene.get("start_keyframe"), "start_keyframe")
        _append_artifact(paths, scene.get("end_keyframe"), "end_keyframe")
        _append_artifact(paths, scene.get("clip_path"), "clip_path")
    bundle_review = bundle.get("review")
    if isinstance(bundle_review, dict):
        _append_artifact(paths, bundle_review.get("reviewed_asset"), "reviewed_asset")
        _append_artifact(paths, bundle_review.get("clip"), "clip")
        _append_artifact(paths, bundle_review.get("inspection_manifest"), "inspection_manifest")
    return paths


def _append_artifact(paths: JsonObject, value: JsonObject | object, label: str) -> None:
    if not isinstance(value, str) or not value:
        return
    if label not in paths:
        paths[label] = value


def _improvement_notes(review: JsonObject) -> list[str]:
    notes: list[str] = []
    _extend_text_list(notes, review.get("regeneration_delta"))
    _extend_text_list(notes, review.get("review_notes"))
    arbiter = review.get("arbiter_decision")
    if isinstance(arbiter, dict):
        _extend_text_list(notes, arbiter.get("regeneration_delta"))
        next_action = arbiter.get("next_action")
        if isinstance(next_action, str) and next_action:
            notes.append(f"Arbiter next action: {next_action}")
    return notes


def _extend_text_list(target: list[str], value: JsonObject | object) -> None:
    if isinstance(value, str) and value:
        target.append(value)
        return
    if not isinstance(value, list):
        return
    for item in value:
        if isinstance(item, str) and item and item not in target:
            target.append(item)


def _next_prompt_memory(blocking_issues: list[str], improvement_notes: list[str]) -> list[str]:
    memory = [f"Do not repeat: {issue}" for issue in blocking_issues]
    for note in improvement_notes:
        memory.append(f"Apply next: {note}")
    if not memory:
        return ["No blockers; preserve the current successful pattern."]
    return memory


def _repeated_blockers(
    project: Path,
    stage: str,
    item_id: str,
    blocker_signatures: list[str],
) -> JsonObject:
    repeated: JsonObject = {}
    entries = _read_round_entries(project)
    for signature in blocker_signatures:
        count = 1 + sum(
            1
            for entry in entries
            if entry.get("stage") == stage
            and entry.get("item_id") == item_id
            and signature in list(entry.get("blocker_signatures", []))
        )
        if count >= 2:
            repeated[signature] = count
    return repeated
