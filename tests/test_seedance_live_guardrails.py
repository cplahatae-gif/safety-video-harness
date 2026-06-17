from __future__ import annotations

import json
import subprocess
from pathlib import Path

import safety_video_harness.seedance_live as seedance_live


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


def approve_video_gate_for_plan(project: Path) -> None:
    config_path = project / "project_config.json"
    config = load_json(config_path)
    config["external_upload_allowed"] = True
    config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    approvals_path = project / "approvals.json"
    approvals = load_json(approvals_path)
    approvals["gates"]["image_to_video"]["approved"] = True
    approvals["gates"]["image_to_video"]["approved_at"] = "test"
    approvals["gates"]["image_to_video"]["approved_by"] = "test"
    approvals_path.write_text(json.dumps(approvals, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def add_seedance_reference_pack(project: Path) -> None:
    assets = {
        "model/cast/signal-worker.png": b"fake cast image",
        "product/equipment/bct-truck.png": b"fake equipment image",
        "ref/approved/space/plant-entry.png": b"fake space image",
    }
    for relative_path, content in assets.items():
        path = project / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        path.with_suffix(".md").write_text(f"Use {path.stem} as a locked reference.\n", encoding="utf-8")


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


def test_seedance_plan_only_requires_gate(tmp_path: Path) -> None:
    project = tmp_path / "seedance-plan-missing-gate"
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

    assert result.returncode != 0
    assert "Gate image_to_video is not approved" in result.stderr
    assert not (project / "video" / "seedance_live_plan.json").exists()


def test_seedance_live_plan_uses_two_five_second_clips_for_10s(tmp_path: Path) -> None:
    project = tmp_path / "seedance-plan"
    prepare_project(project)
    approve_video_gate_for_plan(project)

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


def test_seedance_plan_includes_reference_media_pack_when_available(tmp_path: Path) -> None:
    project = tmp_path / "seedance-reference-pack"
    prepare_project(project)
    add_seedance_reference_pack(project)
    assert run_cli("scripts/generate_seedance.py", "--project", str(project), "--dry-run").returncode == 0
    approve_video_gate_for_plan(project)

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
    job = plan["jobs"][0]
    assert len(job["reference_media_pack"]) == 3
    assert job["media_lock_policy"]["text_only_seedance_allowed"] is False
    assert "--image" in job["create_command"]
    assert any(item.endswith("model/cast/signal-worker.png") for item in job["reference_images"])


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
    approve_video_gate_for_plan(project)

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
    assert "Generate a 5 second Seedance clip" not in prompt


def test_seedance_live_run_log_redacts_public_output_url(tmp_path: Path, monkeypatch) -> None:
    project = tmp_path / "seedance-redaction"
    prepare_project(project)
    approve_video_gate_for_plan(project)
    assert run_cli(
        "scripts/generate_seedance.py",
        "--project",
        str(project),
        "--live",
        "--execute-paid",
        "--test-seconds",
        "10",
        "--plan-only",
    ).returncode == 0
    plan = load_json(project / "video" / "seedance_live_plan.json")

    def fake_run_cli(command: list[str]) -> subprocess.CompletedProcess[str]:
        if "cost" in command:
            return subprocess.CompletedProcess(command, 0, "17.5 credits\n", "")
        return subprocess.CompletedProcess(
            command,
            0,
            "https://d8j0ntlcm91z4.cloudfront.net/user_abc/hf_example.mp4\n",
            "",
        )

    monkeypatch.setattr(seedance_live, "_run_cli", fake_run_cli)

    result = seedance_live.run_seedance_live_plan(project, {"jobs": plan["jobs"][:1]})

    assert result == "created 1 Seedance live job(s)"
    log = (project / "video" / "seedance_live_runs.jsonl").read_text(encoding="utf-8")
    assert "cloudfront.net" not in log
    assert "[redacted-url]" in log
