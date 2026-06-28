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
    assert run_cli("scripts/plan_storyboard.py", "--project", str(project), "--duration", "30", "--image-density", "high").returncode == 0


def test_fast_draft_prepares_three_image_jobs_without_gate_or_asset_lock(tmp_path: Path) -> None:
    project = tmp_path / "fast-draft"
    prepare_project(project)

    result = run_cli("scripts/generate_images.py", "--project", str(project), "--fast-draft")

    assert result.returncode == 0, result.stderr
    assert "fast draft prepared 3 image prompt(s)" in result.stdout
    jobs = load_json(project / "story" / "imagegen_jobs.json")
    prompts = load_json(project / "story" / "image_prompts.json")
    assert jobs["execution_mode"] == "fast_draft_manual_imagegen"
    assert [job["scene_id"] for job in jobs["jobs"]] == ["sc01", "sc07", "sc12"]
    assert all(job["fast_draft"] for job in jobs["jobs"])
    assert "asset_lock" not in jobs["jobs"][0]
    assert prompts["fast_draft"] is True
