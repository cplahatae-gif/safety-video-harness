from __future__ import annotations

from safety_video_harness.io import JsonObject


DISAGREEMENT_THRESHOLD = 2


def consensus(role_reviews: list[dict]) -> JsonObject:
    votes = [vote(review) for review in role_reviews]
    critical_vetoes = critical_vetoes_for(role_reviews)
    approve_count = votes.count("approve")
    conditional_count = votes.count("conditional")
    reject_count = votes.count("reject")
    return {
        "rule": "5/5 approve or 4/5 approve plus conditional; critical veto overrides majority",
        "total_roles": len(role_reviews),
        "approve_count": approve_count,
        "conditional_count": conditional_count,
        "reject_count": reject_count,
        "critical_vetoes": critical_vetoes,
        "rule_result": consensus_result(len(role_reviews), approve_count, conditional_count, critical_vetoes),
    }


def vote(review: dict) -> str:
    explicit = str(review.get("vote", ""))
    if explicit in {"approve", "conditional", "reject"}:
        return explicit
    if list(review.get("critical_blockers", [])):
        return "reject"
    if list(review.get("blocking_issues", [])):
        return "reject"
    scores = review.get("scores", {})
    if isinstance(scores, dict) and all(isinstance(score, int) and score >= 4 for score in scores.values()):
        return "approve"
    return "reject"


def critical_vetoes_for(role_reviews: list[dict]) -> list[str]:
    vetoes: list[str] = []
    for review in role_reviews:
        role = str(review.get("role", "unknown"))
        for blocker in list(review.get("critical_blockers", [])):
            vetoes.append(f"{role}: {blocker}")
    return vetoes


def consensus_result(
    total_roles: int,
    approve_count: int,
    conditional_count: int,
    critical_vetoes: list[str],
) -> str:
    if critical_vetoes:
        return "critical_veto"
    if total_roles > 0 and approve_count == total_roles:
        return "approved"
    if total_roles >= 2 and approve_count >= total_roles - 1 and conditional_count >= 1:
        return "conditional_approval"
    return "rejected"


def debate_triggers(role_reviews: list[dict], consensus_result_value: str) -> list[str]:
    score_values: dict[str, list[int]] = {}
    for review in role_reviews:
        scores = review.get("scores", {})
        if not isinstance(scores, dict):
            continue
        for name, value in scores.items():
            if isinstance(value, int):
                score_values.setdefault(str(name), []).append(value)
    triggers = [
        "score_disagreement"
        for values in score_values.values()
        if values and max(values) - min(values) >= DISAGREEMENT_THRESHOLD
    ]
    if consensus_result_value == "critical_veto":
        triggers.append("critical_veto")
    return sorted(set(triggers))


def decision(
    stage: str,
    blocking_issues: list[str],
    repeated_blockers: list[str],
    debate_required: bool,
    consensus_result_value: str,
) -> str:
    if consensus_result_value == "critical_veto":
        return "propose_only" if stage == "video" else "revise_storyboard"
    if repeated_blockers:
        return "revise_storyboard"
    if debate_required:
        return "debate_required"
    if consensus_result_value == "conditional_approval":
        return "conditional_approval"
    if blocking_issues:
        if stage == "video":
            return "propose_only"
        if stage == "storyboard":
            return "revise_storyboard"
        return "regenerate"
    if stage == "image":
        return "approve_for_video"
    if stage == "storyboard":
        return "approve_for_image"
    return "approve"


def next_action(decision_value: str) -> str:
    if decision_value == "revise_storyboard":
        return "stop_and_escalate"
    if decision_value == "conditional_approval":
        return "continue_with_conditions"
    if decision_value == "debate_required":
        return "run_conditional_debate"
    if decision_value == "regenerate":
        return "regenerate_blocked_scenes"
    if decision_value == "propose_only":
        return "request_user_approval_for_paid_retry"
    return "continue"
