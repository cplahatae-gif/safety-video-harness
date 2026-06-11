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


def test_new_storyboard_contains_no_narration_fields(tmp_path: Path) -> None:
    project = tmp_path / "no-narration"
    prepare_project(project)

    result = run_cli("scripts/plan_storyboard.py", "--project", str(project), "--duration", "30")

    assert result.returncode == 0
    scenes = json.loads((project / "storyboard" / "scenes.json").read_text(encoding="utf-8"))
    assert all("narration_ko" not in scene for scene in scenes["scenes"])
    assert all("narration_char_limit" not in scene for scene in scenes["scenes"])
    assert all(str(scene.get("subtitle_ko", "")) for scene in scenes["scenes"])


def test_legacy_narration_field_is_rejected(tmp_path: Path) -> None:
    project = tmp_path / "legacy-narration"
    prepare_project(project)
    assert run_cli("scripts/plan_storyboard.py", "--project", str(project), "--duration", "30").returncode == 0
    path = project / "storyboard" / "scenes.json"
    scenes = json.loads(path.read_text(encoding="utf-8"))
    scenes["scenes"][0]["narration_ko"] = "금지된 나레이션"
    path.write_text(json.dumps(scenes, ensure_ascii=False), encoding="utf-8")

    result = run_cli("scripts/validate_project.py", str(project))

    assert result.returncode != 0
    assert "narration_ko is not allowed" in result.stderr
