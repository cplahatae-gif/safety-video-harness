from __future__ import annotations

import json
import subprocess
from pathlib import Path


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


def prepare_project(project: Path) -> None:
    assert run_cli("scripts/init_project.py", "--name", "레미콘 충돌 예방", "--slug", str(project)).returncode == 0
    assert run_cli("scripts/register_sources.py", "--project", str(project), "--source", str(FIXTURE)).returncode == 0
    assert run_cli("scripts/render_pptx_sources.py", "--project", str(project), "--dry-run", "--mode", "media_extract").returncode == 0
    assert run_cli("scripts/extract_topics.py", "--project", str(project)).returncode == 0
    assert run_cli("scripts/select_topic.py", "--project", str(project), "--topic-id", "topic-001").returncode == 0
    assert run_cli("scripts/plan_storyboard.py", "--project", str(project), "--duration", "30").returncode == 0


def test_storyboard_quality_passes_complete_fixture(tmp_path: Path) -> None:
    project = tmp_path / "storyboard-quality"
    prepare_project(project)

    result = run_cli("scripts/evaluate_storyboard.py", "--project", str(project))

    assert result.returncode == 0
    report = json.loads((project / "qa" / "storyboard_quality_reviews.json").read_text(encoding="utf-8"))
    assert report["passed"] is True
    assert report["thresholds"]["minimum_total_score"] == 20
    assert report["reviews"][0]["criteria"]["source_grounding_score"] >= 4
    rounds = (project / "qa" / "evaluation_rounds.jsonl").read_text(encoding="utf-8")
    assert '"stage": "storyboard"' in rounds
    assert '"item_id": "sc01"' in rounds
    bundle = project / "qa" / "evaluation_bundles" / "storyboard" / "sc01" / "round_001.json"
    assert bundle.exists()
    assert (project / "qa" / "role_evaluations" / "storyboard" / "sc01" / "round_001" / "source_grounding.json").exists()
    assert (project / "qa" / "arbiter_decisions" / "storyboard" / "sc01" / "round_001.json").exists()
    wiki = (project / "llm-wiki" / "evaluation-rounds.md").read_text(encoding="utf-8")
    assert "## storyboard / sc01 / round 1" in wiki


def test_storyboard_quality_blocks_missing_citations(tmp_path: Path) -> None:
    project = tmp_path / "storyboard-quality-block"
    prepare_project(project)
    path = project / "storyboard" / "scenes.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["scenes"][0]["source_citations"] = []
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    result = run_cli("scripts/evaluate_storyboard.py", "--project", str(project))

    assert result.returncode != 0
    assert "storyboard QA blockers" in result.stderr
    report = json.loads((project / "qa" / "storyboard_quality_reviews.json").read_text(encoding="utf-8"))
    assert report["passed"] is False


def test_storyboard_gate_requires_passing_storyboard_qa(tmp_path: Path) -> None:
    project = tmp_path / "storyboard-gate-qa"
    prepare_project(project)
    path = project / "storyboard" / "scenes.json"
    scenes = json.loads(path.read_text(encoding="utf-8"))
    scenes["scenes"][0]["visual_action_ko"] = ""
    path.write_text(json.dumps(scenes, ensure_ascii=False, indent=2), encoding="utf-8")

    qa = run_cli("scripts/evaluate_storyboard.py", "--project", str(project))
    approved = run_cli("scripts/approve_gate.py", "--project", str(project), "--gate", "storyboard")

    assert qa.returncode != 0
    assert approved.returncode != 0
    assert "storyboard QA" in approved.stderr
    assert "weak causal prevention beat" in approved.stderr
