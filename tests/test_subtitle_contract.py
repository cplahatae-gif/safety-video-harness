from __future__ import annotations

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


def test_subtitle_plan_generates_srt_from_storyboard(tmp_path: Path) -> None:
    project = tmp_path / "subtitle-plan"
    prepare_project(project)

    result = run_cli("scripts/plan_subtitles.py", "--project", str(project), "--dry-run")

    assert result.returncode == 0
    srt = (project / "subtitles" / "subtitles.srt").read_text(encoding="utf-8")
    assert "차량 동선을 먼저 확인하세요." in srt
    assert "-->" in srt
