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


def planned_counts(project: Path, density: str) -> tuple[int, int, int]:
    result = run_cli(
        "scripts/plan_storyboard.py",
        "--project",
        str(project),
        "--duration",
        "30",
        "--image-density",
        density,
    )
    assert result.returncode == 0, result.stderr
    scenes = json.loads((project / "story" / "scenes.json").read_text(encoding="utf-8"))
    return int(scenes["clip_count"]), int(scenes["story_beats"]), int(scenes["keyframe_count"])


def test_density_controls_story_beats_and_keyframes(tmp_path: Path) -> None:
    project = tmp_path / "density"
    prepare_project(project)

    assert planned_counts(project, "normal") == (6, 6, 7)
    assert planned_counts(project, "high") == (6, 12, 13)
    assert planned_counts(project, "very_high") == (6, 24, 25)


def test_invalid_density_fails(tmp_path: Path) -> None:
    project = tmp_path / "density-invalid"
    prepare_project(project)

    result = run_cli(
        "scripts/plan_storyboard.py",
        "--project",
        str(project),
        "--duration",
        "30",
        "--image-density",
        "extreme",
    )

    assert result.returncode != 0
    assert "invalid choice" in result.stderr or "image-density" in result.stderr
