from __future__ import annotations

import json
import subprocess
from pathlib import Path

from PIL import Image

from safety_video_harness.evaluation_arbiter import aggregate_arbiter_decision
from safety_video_harness.role_evaluators import run_role_evaluators_parallel


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "fixtures" / "sources" / "remicon-collision-guide.pptx"


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", *args],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def prepare_project(project: Path) -> None:
    assert run_cli("scripts/init_project.py", "--name", "레미콘 충돌 예방", "--slug", str(project)).returncode == 0
    assert run_cli("scripts/register_sources.py", "--project", str(project), "--source", str(FIXTURE)).returncode == 0
    assert run_cli("scripts/render_pptx_sources.py", "--project", str(project), "--dry-run", "--mode", "media_extract").returncode == 0
    assert run_cli("scripts/extract_topics.py", "--project", str(project)).returncode == 0
    assert run_cli("scripts/select_topic.py", "--project", str(project), "--topic-id", "topic-001").returncode == 0
    assert run_cli("scripts/extract_style_dna.py", "--project", str(project)).returncode == 0
    assert run_cli("scripts/plan_storyboard.py", "--project", str(project), "--duration", "30").returncode == 0


def write_test_png(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (160, 90), "white").save(path)


def test_arbiter_triggers_debate_when_role_scores_disagree(tmp_path: Path) -> None:
    project = tmp_path / "arbiter-disagreement"
    role_reviews = [
        {
            "role": "visual_continuity",
            "scores": {"visual_continuity": 5, "story_match": 5},
            "blocking_issues": [],
        },
        {
            "role": "story_match",
            "scores": {"visual_continuity": 2, "story_match": 5},
            "blocking_issues": ["worker identity changes between frames"],
        },
    ]

    decision = aggregate_arbiter_decision(project, "image", "sc03", 1, role_reviews)

    assert decision["decision"] == "debate_required"
    assert decision["debate_required"] is True
    assert "score_disagreement" in decision["debate_triggers"]
    assert decision["scores"]["visual_continuity"] == 2
    assert (project / "qa" / "arbiter_decisions" / "image" / "sc03" / "round_001.json").exists()
    assert (project / "qa" / "role_evaluations" / "image" / "sc03" / "round_001.json").exists()
    assert (project / "qa" / "debates" / "image" / "sc03" / "round_001.json").exists()


def test_parallel_role_evaluator_outputs_round_files_and_consensus(tmp_path: Path) -> None:
    project = tmp_path / "parallel-consensus"
    role_reviews = run_role_evaluators_parallel(
        [
            ("technical", lambda: {"role": "technical", "scores": {"technical": 5}, "blocking_issues": []}),
            (
                "visual_continuity",
                lambda: {"role": "visual_continuity", "scores": {"visual_continuity": 5}, "blocking_issues": []},
            ),
            ("story_match", lambda: {"role": "story_match", "scores": {"story_match": 5}, "blocking_issues": []}),
            (
                "safety_education",
                lambda: {"role": "safety_education", "scores": {"safety": 5}, "blocking_issues": []},
            ),
            (
                "devils_advocate",
                lambda: {
                    "role": "devils_advocate",
                    "scores": {"risk": 4},
                    "blocking_issues": [],
                    "vote": "conditional",
                },
            ),
        ]
    )

    decision = aggregate_arbiter_decision(project, "image", "sc04", 2, role_reviews)

    assert decision["decision"] == "conditional_approval"
    assert decision["consensus"]["rule_result"] == "conditional_approval"
    assert decision["consensus"]["approve_count"] == 4
    assert decision["consensus"]["conditional_count"] == 1
    round_dir = project / "qa" / "role_evaluations" / "image" / "sc04" / "round_002"
    assert (round_dir / "technical.json").exists()
    assert (round_dir / "technical.md").exists()
    aggregate = load_json(project / "qa" / "role_evaluations" / "image" / "sc04" / "round_002.json")
    assert aggregate["execution_mode"] == "parallel_role_evaluators"


def test_critical_safety_veto_overrides_consensus(tmp_path: Path) -> None:
    project = tmp_path / "critical-veto"
    role_reviews = [
        {"role": "technical", "scores": {"technical": 5}, "blocking_issues": [], "vote": "approve"},
        {"role": "visual_continuity", "scores": {"visual_continuity": 5}, "blocking_issues": [], "vote": "approve"},
        {"role": "story_match", "scores": {"story_match": 5}, "blocking_issues": [], "vote": "approve"},
        {
            "role": "safety_education",
            "scores": {"safety": 2},
            "blocking_issues": ["hazard prevention is not visible"],
            "critical_blockers": ["hazard prevention is not visible"],
            "vote": "reject",
        },
        {"role": "devils_advocate", "scores": {"risk": 5}, "blocking_issues": [], "vote": "approve"},
    ]

    decision = aggregate_arbiter_decision(project, "image", "sc05", 1, role_reviews)

    assert decision["decision"] == "revise_storyboard"
    assert decision["consensus"]["rule_result"] == "critical_veto"
    assert "critical_veto" in decision["debate_triggers"]
    assert decision["next_action"] == "stop_and_escalate"
    debate_dir = project / "qa" / "debates" / "image" / "sc05" / "round_001"
    assert (debate_dir / "moderator-brief.md").exists()
    assert (debate_dir / "consensus.md").exists()


def test_validate_images_escalates_after_three_repeated_blockers(tmp_path: Path) -> None:
    project = tmp_path / "repeated-blocker"
    prepare_project(project)
    qa_dir = project / "qa"
    qa_dir.mkdir(parents=True, exist_ok=True)
    with (qa_dir / "evaluation_rounds.jsonl").open("w", encoding="utf-8") as handle:
        for iteration in [1, 2]:
            handle.write(
                json.dumps(
                    {
                        "stage": "image",
                        "item_id": "sc01",
                        "iteration": iteration,
                        "decision": "regenerate",
                        "blocking_issues": ["missing draft image"],
                        "blocker_signatures": ["image:sc01:technical:missing_draft_image"],
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )

    result = run_cli("scripts/validate_images.py", "--project", str(project), "--only", "sc01")

    assert result.returncode == 0
    loop = load_json(project / "qa" / "image_qa_loop.json")
    assert loop["ralph_loop"]["status"] == "repeated_blocker_escalation"
    assert loop["next_action"] == "stop_and_escalate"
    decision = load_json(project / "qa" / "arbiter_decisions" / "image" / "sc01" / "round_003.json")
    assert decision["decision"] == "revise_storyboard"
    assert decision["next_action"] == "stop_and_escalate"
    assert "Do not regenerate the same image again" in decision["regeneration_delta"]
    assert "image:sc01:technical:missing_draft_image" in decision["repeated_blockers"]


def test_image_prompt_includes_previous_qa_blockers_from_llm_wiki(tmp_path: Path) -> None:
    project = tmp_path / "wiki-prompt-memory"
    prepare_project(project)
    write_test_png(project / "images" / "draft" / "sc01_v001.png")
    qa_dir = project / "qa"
    qa_dir.mkdir(parents=True, exist_ok=True)
    (qa_dir / "evaluation_rounds.jsonl").write_text(
        json.dumps(
            {
                "stage": "image",
                "item_id": "sc01",
                "iteration": 1,
                "decision": "regenerate",
                "blocking_issues": ["gaze target is unclear"],
                "blocker_signatures": ["image:sc01:gaze_motivation:unclear_target"],
            },
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    (project / "llm-wiki").mkdir(parents=True, exist_ok=True)
    (project / "llm-wiki" / "evaluation-rounds.md").write_text(
        "# Evaluation Rounds\n\n## image / sc01 / round 1\n- blocking_issues: gaze target is unclear\n",
        encoding="utf-8",
    )

    result = run_cli("scripts/generate_images.py", "--project", str(project), "--dry-run", "--only", "sc01")

    assert result.returncode == 0
    prompt = load_json(project / "prompts" / "image_prompts.json")["plans"][0]["prompt"]
    assert "RALPH previous-round critique:" in prompt
    assert "Previous QA blockers for this scene:" in prompt
    assert "gaze target is unclear" in prompt
    assert "Quality pressure" in prompt
    assert "Do not repeat these failures:" in prompt
