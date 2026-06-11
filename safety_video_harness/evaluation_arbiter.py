from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from safety_video_harness.blocker_signatures import blocker_signature
from safety_video_harness.evaluation_consensus import consensus, debate_triggers, decision, next_action
from safety_video_harness.evaluation_outputs import write_debate_record, write_role_reviews
from safety_video_harness.io import JsonObject, write_json


REPEATED_BLOCKER_THRESHOLD = 3


def aggregate_arbiter_decision(
    project: Path,
    stage: str,
    item_id: str,
    iteration: int,
    role_reviews: list[dict],
) -> JsonObject:
    scores = _minimum_scores(role_reviews)
    blocking_issues = _blocking_issues(role_reviews)
    signatures = _blocker_signatures(stage, item_id, role_reviews, blocking_issues)
    repeated_blockers = _repeated_blockers(project, stage, item_id, signatures)
    consensus_result = consensus(role_reviews)
    triggers = debate_triggers(role_reviews, str(consensus_result["rule_result"]))
    if repeated_blockers and "repeated_blocker" not in triggers:
        triggers.append("repeated_blocker")
    debate_required = bool(triggers)
    final_decision = decision(
        stage,
        blocking_issues,
        repeated_blockers,
        debate_required,
        str(consensus_result["rule_result"]),
    )
    write_role_reviews(project, stage, item_id, iteration, role_reviews)
    result: JsonObject = {
        "stage": stage,
        "item_id": item_id,
        "round": iteration,
        "iteration": iteration,
        "decision": final_decision,
        "role_reviews": role_reviews,
        "scores": scores,
        "blocking_issues": blocking_issues,
        "blocker_signatures": signatures,
        "repeated_blockers": repeated_blockers,
        "critical_vetoes": consensus_result["critical_vetoes"],
        "consensus": consensus_result,
        "debate_required": debate_required,
        "debate_triggers": triggers,
        "repeated_blocker_threshold": REPEATED_BLOCKER_THRESHOLD,
        "next_action": next_action(final_decision),
        "regeneration_delta": _regeneration_delta(blocking_issues, repeated_blockers),
        "evidence_bundle": str(
            Path("qa")
            / "evaluation_bundles"
            / stage
            / item_id
            / f"round_{iteration:03d}.json"
        ),
    }
    write_json(
        project / "qa" / "arbiter_decisions" / stage / item_id / f"round_{iteration:03d}.json",
        result,
    )
    if debate_required:
        write_debate_record(project, stage, item_id, iteration, result)
    return result


def _minimum_scores(role_reviews: list[dict]) -> dict[str, int]:
    scores_by_name: dict[str, list[int]] = {}
    for review in role_reviews:
        scores = review.get("scores", {})
        if not isinstance(scores, dict):
            continue
        for name, value in scores.items():
            if isinstance(value, int):
                scores_by_name.setdefault(str(name), []).append(value)
    return {name: min(values) for name, values in scores_by_name.items() if values}


def _blocking_issues(role_reviews: list[dict]) -> list[str]:
    issues: list[str] = []
    for review in role_reviews:
        for issue in list(review.get("blocking_issues", [])):
            text = str(issue)
            if text not in issues:
                issues.append(text)
    return issues


def _blocker_signatures(
    stage: str,
    item_id: str,
    role_reviews: list[dict],
    blocking_issues: list[str],
) -> list[str]:
    signatures: list[str] = []
    for review in role_reviews:
        for signature in list(review.get("blocker_signatures", [])):
            text = str(signature)
            if text not in signatures:
                signatures.append(text)
    for issue in blocking_issues:
        signature = blocker_signature(stage, item_id, issue)
        if signature not in signatures:
            signatures.append(signature)
    return signatures


def _repeated_blockers(project: Path, stage: str, item_id: str, signatures: list[str]) -> list[str]:
    if not signatures:
        return []
    prior_counts = _prior_signature_counts(project, stage, item_id)
    current_counts = Counter(signatures)
    return [
        signature
        for signature, count in current_counts.items()
        if prior_counts.get(signature, 0) + count >= REPEATED_BLOCKER_THRESHOLD
    ]


def _prior_signature_counts(project: Path, stage: str, item_id: str) -> Counter[str]:
    counts: Counter[str] = Counter()
    ledger = project / "qa" / "evaluation_rounds.jsonl"
    if not ledger.exists():
        return counts
    for line in ledger.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        entry = json.loads(line)
        if not isinstance(entry, dict):
            continue
        if entry.get("stage") != stage or entry.get("item_id") != item_id:
            continue
        for signature in list(entry.get("blocker_signatures", [])):
            counts[str(signature)] += 1
    return counts


def _regeneration_delta(blocking_issues: list[str], repeated_blockers: list[str]) -> str:
    if repeated_blockers:
        return (
            "Do not regenerate the same image again. Escalate upstream: clarify storyboard causality, "
            "add or correct reference evidence, then rebuild the prompt contract for these repeated blockers: "
            + "; ".join(repeated_blockers)
            + "."
        )
    if blocking_issues:
        return (
            "Regenerate only after directly addressing these visible deficiencies: "
            + "; ".join(blocking_issues)
            + ". Preserve approved continuity locks."
        )
    return ""
