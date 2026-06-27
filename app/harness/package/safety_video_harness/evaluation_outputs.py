from __future__ import annotations

from pathlib import Path

from safety_video_harness.evaluation_consensus import vote
from safety_video_harness.io import JsonObject, write_json
from safety_video_harness.locks import assert_unlocked


def write_role_reviews(
    project: Path,
    stage: str,
    item_id: str,
    iteration: int,
    role_reviews: list[dict],
) -> None:
    base = project / "qa" / "role_evaluations" / stage / item_id
    write_json(
        base / f"round_{iteration:03d}.json",
        {
            "stage": stage,
            "item_id": item_id,
            "round": iteration,
            "output_contract": "role_evaluator_reviews_v1",
            "execution_mode": "parallel_role_evaluators",
            "role_reviews": role_reviews,
        },
    )
    round_dir = base / f"round_{iteration:03d}"
    for review in role_reviews:
        role = safe_role_name(str(review.get("role", "unknown")))
        write_json(round_dir / f"{role}.json", review)
        write_markdown(round_dir / f"{role}.md", role_review_markdown(review))


def write_debate_record(
    project: Path,
    stage: str,
    item_id: str,
    iteration: int,
    arbiter_decision: JsonObject,
) -> None:
    base = project / "qa" / "debates" / stage / item_id
    write_json(
        base / f"round_{iteration:03d}.json",
        {
            "stage": stage,
            "item_id": item_id,
            "round": iteration,
            "trigger": arbiter_decision["debate_triggers"],
            "mode": "conditional_debate",
            "paid_generation_allowed": False,
            "positions": debate_positions(arbiter_decision),
            "arbiter_decision": arbiter_decision["decision"],
            "next_action": arbiter_decision["next_action"],
        },
    )
    round_dir = base / f"round_{iteration:03d}"
    write_markdown(round_dir / "moderator-brief.md", moderator_brief(arbiter_decision))
    for position in debate_positions(arbiter_decision):
        role = safe_role_name(str(position.get("role", "unknown")))
        write_markdown(round_dir / f"{role}.md", position_markdown(position))
    write_markdown(round_dir / "consensus.md", consensus_markdown(arbiter_decision))


def debate_positions(arbiter_decision: JsonObject) -> list[JsonObject]:
    positions: list[JsonObject] = []
    for review in list(arbiter_decision.get("role_reviews", [])):
        if not isinstance(review, dict):
            continue
        role = str(review.get("role", "unknown"))
        issues = [str(issue) for issue in list(review.get("blocking_issues", []))]
        scores = review.get("scores", {})
        positions.append(
            {
                "role": role,
                "position": position_text(role, scores, issues),
                "blocking_issues": issues,
            }
        )
    return positions


def safe_role_name(role: str) -> str:
    safe = "".join(char if char.isalnum() or char in {"-", "_"} else "-" for char in role.lower())
    return safe.strip("-") or "unknown"


def write_markdown(path: Path, content: str) -> None:
    assert_unlocked(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def role_review_markdown(review: dict) -> str:
    role = str(review.get("role", "unknown"))
    issues = [str(issue) for issue in list(review.get("blocking_issues", []))]
    critical = [str(issue) for issue in list(review.get("critical_blockers", []))]
    return "\n".join(
        [
            f"# {role}",
            "",
            f"- vote: `{vote(review)}`",
            f"- execution_mode: `{review.get('execution_mode', '')}`",
            f"- scores: `{review.get('scores', {})}`",
            f"- blocking_issues: {issue_text(issues)}",
            f"- critical_blockers: {issue_text(critical)}",
            "",
        ]
    )


def moderator_brief(arbiter_decision: JsonObject) -> str:
    return "\n".join(
        [
            "# Moderator Brief",
            "",
            f"- stage: `{arbiter_decision['stage']}`",
            f"- item_id: `{arbiter_decision['item_id']}`",
            f"- round: `{arbiter_decision['round']}`",
            f"- debate_triggers: `{arbiter_decision['debate_triggers']}`",
            f"- decision: `{arbiter_decision['decision']}`",
            f"- next_action: `{arbiter_decision['next_action']}`",
            "",
            "Evaluate the disagreement, critical vetoes, or repeated blockers without generating new media.",
            "",
        ]
    )


def position_markdown(position: JsonObject) -> str:
    return "\n".join([f"# {position['role']}", "", str(position["position"]), ""])


def consensus_markdown(arbiter_decision: JsonObject) -> str:
    return "\n".join(
        [
            "# Consensus",
            "",
            f"- result: `{arbiter_decision['consensus']['rule_result']}`",
            f"- approve_count: `{arbiter_decision['consensus']['approve_count']}`",
            f"- conditional_count: `{arbiter_decision['consensus']['conditional_count']}`",
            f"- reject_count: `{arbiter_decision['consensus']['reject_count']}`",
            f"- critical_vetoes: {issue_text(list(arbiter_decision['critical_vetoes']))}",
            f"- final_decision: `{arbiter_decision['decision']}`",
            "",
        ]
    )


def position_text(role: str, scores: object, issues: list[str]) -> str:
    if issues:
        return f"{role} blocks approval because: " + "; ".join(issues)
    return f"{role} finds no blocking issue in its assigned evidence slice. Scores: {scores}"


def issue_text(issues: list[str]) -> str:
    return "none" if not issues else "; ".join(issues)
