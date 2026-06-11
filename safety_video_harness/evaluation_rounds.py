from __future__ import annotations

import json
from pathlib import Path

from safety_video_harness.blocker_signatures import blocker_signature
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
    record: JsonObject = {
        "stage": stage,
        "item_id": item_id,
        "iteration": iteration,
        "decision": str(review.get("decision", "")),
        "total_score": int(review.get("total_score", 0)),
        "blocking_issues": blocking_issues,
        "blocker_signatures": blocker_signatures,
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
        ]
    )
    with path.open("a", encoding="utf-8") as handle:
        handle.write(block)
