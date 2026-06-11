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
    assert run_cli("scripts/extract_style_dna.py", "--project", str(project)).returncode == 0
    assert run_cli("scripts/plan_storyboard.py", "--project", str(project), "--duration", "30").returncode == 0


def test_seedance_prompt_includes_continuity_gaze_and_subtitle_contract(tmp_path: Path) -> None:
    project = tmp_path / "prompt-contract"
    prepare_project(project)

    result = run_cli("scripts/generate_seedance.py", "--project", str(project), "--dry-run")

    assert result.returncode == 0
    prompts = json.loads((project / "prompts" / "video_prompts.json").read_text(encoding="utf-8"))
    first = prompts["plans"][0]
    prompt = first["prompt"].lower()
    assert first["subtitle_plan_ko"]
    assert "gaze" in prompt
    assert "post-production" in prompt
    assert "narration" not in prompt
