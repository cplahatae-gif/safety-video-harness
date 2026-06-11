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


def test_image_qa_writes_ralph_loop_regeneration_prompts(tmp_path: Path) -> None:
    project = tmp_path / "image-ralph"
    prepare_project(project)

    result = run_cli("scripts/validate_images.py", "--project", str(project), "--only", "sc01")

    assert result.returncode == 0
    loop = json.loads((project / "qa" / "image_qa_loop.json").read_text(encoding="utf-8"))
    assert loop["ralph_loop"]["status"] == "needs_regeneration"
    assert loop["ralph_loop"]["max_iterations"] == 20
    assert loop["ralph_loop"]["current_iterations"]["sc01"] == 1
    assert loop["ralph_loop"]["remaining_iterations"]["sc01"] == 19
    assert loop["ralph_loop"]["blocked_scenes"][0]["scene_id"] == "sc01"
    assert "missing draft image" in loop["ralph_loop"]["blocked_scenes"][0]["deficiencies"]
    assert "Regenerate sc01" in loop["ralph_loop"]["blocked_scenes"][0]["regeneration_prompt"]


def test_image_qa_records_round_bundle_and_wiki_summary(tmp_path: Path) -> None:
    project = tmp_path / "image-round-ledger"
    prepare_project(project)

    result = run_cli("scripts/validate_images.py", "--project", str(project), "--only", "sc01")

    assert result.returncode == 0
    rounds = (project / "qa" / "evaluation_rounds.jsonl").read_text(encoding="utf-8")
    assert '"stage": "image"' in rounds
    assert '"item_id": "sc01"' in rounds
    bundle = project / "qa" / "evaluation_bundles" / "image" / "sc01" / "round_001.json"
    assert bundle.exists()
    payload = json.loads(bundle.read_text(encoding="utf-8"))
    assert payload["evaluator_context_policy"] == "isolated_evaluator_with_evidence_bundle"
    assert payload["scene"]["id"] == "sc01"
    wiki = (project / "llm-wiki" / "evaluation-rounds.md").read_text(encoding="utf-8")
    assert "## image / sc01 / round 1" in wiki
    assert "missing draft image" in wiki


def test_image_qa_stops_ralph_after_max_iterations(tmp_path: Path) -> None:
    project = tmp_path / "image-ralph-max"
    prepare_project(project)
    qa_dir = project / "qa"
    qa_dir.mkdir(parents=True, exist_ok=True)
    with (qa_dir / "evaluation_rounds.jsonl").open("w", encoding="utf-8") as handle:
        for iteration in range(1, 21):
            handle.write(
                json.dumps(
                    {
                        "stage": "image",
                        "item_id": "sc01",
                        "iteration": iteration,
                        "decision": "regenerate",
                        "blocking_issues": ["missing draft image"],
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )

    result = run_cli("scripts/validate_images.py", "--project", str(project), "--only", "sc01")

    assert result.returncode == 0
    loop = json.loads((project / "qa" / "image_qa_loop.json").read_text(encoding="utf-8"))
    assert loop["ralph_loop"]["status"] == "max_iterations_reached"
    assert loop["ralph_loop"]["current_iterations"]["sc01"] == 20
    assert loop["ralph_loop"]["remaining_iterations"]["sc01"] == 0
    assert loop["next_action"] == "stop_and_escalate"
