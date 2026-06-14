from __future__ import annotations

import json
import subprocess
from pathlib import Path

from PIL import Image


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
    review = loop["reviews"][0]
    assert review["rubric_source"] == "docs/evaluation-rubrics.md"
    assert review["few_shot_source"] == "docs/few-shot-examples.md"
    assert review["artifact_path"] == "images/draft/sc01_v*.png"
    assert review["critical_blockers"] == ["missing draft image"]
    assert review["blocker_categories"][0]["category"] == "missing_artifact"
    assert "Regenerate sc01" in review["regeneration_delta"]
    assert review["previous_blockers_applied"] is False


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


def test_validate_images_does_not_increment_iterations_for_passing_scenes(tmp_path: Path) -> None:
    project = tmp_path / "image-ralph-passing"
    prepare_project(project)
    draft = project / "images" / "draft" / "sc01_v001.png"
    draft.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (1600, 900), color=(120, 140, 160)).save(draft)

    first = run_cli("scripts/validate_images.py", "--project", str(project), "--only", "sc01")
    second = run_cli("scripts/validate_images.py", "--project", str(project), "--only", "sc01")

    assert first.returncode == 0
    assert second.returncode == 0
    rounds_path = project / "qa" / "evaluation_rounds.jsonl"
    rounds = rounds_path.read_text(encoding="utf-8") if rounds_path.exists() else ""
    assert '"item_id": "sc01"' not in rounds
    loop = json.loads((project / "qa" / "image_qa_loop.json").read_text(encoding="utf-8"))
    assert loop["ralph_loop"]["status"] == "passed"
