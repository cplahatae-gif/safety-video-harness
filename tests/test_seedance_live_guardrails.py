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
    assert run_cli("scripts/generate_seedance.py", "--project", str(project), "--dry-run").returncode == 0


def test_live_seedance_requires_paid_execute_flag(tmp_path: Path) -> None:
    project = tmp_path / "seedance-no-execute"
    prepare_project(project)

    result = run_cli("scripts/generate_seedance.py", "--project", str(project), "--live", "--test-seconds", "10")

    assert result.returncode != 0
    assert "--execute-paid" in result.stderr


def test_live_seedance_enforces_10_second_and_3_attempt_caps(tmp_path: Path) -> None:
    project = tmp_path / "seedance-caps"
    prepare_project(project)

    too_long = run_cli(
        "scripts/generate_seedance.py",
        "--project",
        str(project),
        "--live",
        "--execute-paid",
        "--test-seconds",
        "15",
    )
    too_many = run_cli(
        "scripts/generate_seedance.py",
        "--project",
        str(project),
        "--live",
        "--execute-paid",
        "--test-seconds",
        "10",
        "--max-attempts",
        "4",
    )

    assert too_long.returncode != 0
    assert "test-seconds must be <= 10" in too_long.stderr
    assert too_many.returncode != 0
    assert "max-attempts must be <= 3" in too_many.stderr


def test_seedance_live_plan_uses_two_five_second_clips_for_10s(tmp_path: Path) -> None:
    project = tmp_path / "seedance-plan"
    prepare_project(project)
    result = run_cli(
        "scripts/generate_seedance.py",
        "--project",
        str(project),
        "--live",
        "--execute-paid",
        "--test-seconds",
        "10",
        "--plan-only",
    )

    assert result.returncode == 0
    plan = load_json(project / "video" / "seedance_live_plan.json")
    assert plan["test_seconds"] == 10
    assert plan["max_attempts"] == 3
    assert len(plan["jobs"]) == 2
    assert plan["jobs"][0]["duration"] == 5
    assert plan["jobs"][0]["start_image"].endswith("images/approved/sc01.png")
    assert plan["jobs"][1]["end_image"].endswith("images/approved/sc03.png")


def test_validation_run_requires_one_attempt(tmp_path: Path) -> None:
    project = tmp_path / "seedance-validation-run"
    prepare_project(project)

    result = run_cli(
        "scripts/generate_seedance.py",
        "--project",
        str(project),
        "--live",
        "--execute-paid",
        "--test-seconds",
        "10",
        "--max-attempts",
        "2",
        "--validation-run",
        "--plan-only",
    )

    assert result.returncode != 0
    assert "validation-run requires max-attempts=1" in result.stderr


def test_validation_run_prompt_matches_10_second_duration(tmp_path: Path) -> None:
    project = tmp_path / "seedance-validation-duration"
    prepare_project(project)

    result = run_cli(
        "scripts/generate_seedance.py",
        "--project",
        str(project),
        "--live",
        "--execute-paid",
        "--test-seconds",
        "10",
        "--max-attempts",
        "1",
        "--validation-run",
        "--plan-only",
    )

    assert result.returncode == 0
    plan = load_json(project / "video" / "seedance_live_plan.json")
    assert plan["jobs"][0]["duration"] == 10
    command = plan["jobs"][0]["create_command"]
    prompt = command[command.index("--prompt") + 1]
    assert "Generate a 10 second Seedance clip" in prompt
