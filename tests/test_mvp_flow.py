from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run_cli(*args: str, cwd: Path = ROOT) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", *args],
        cwd=cwd,
        check=False,
        text=True,
        capture_output=True,
    )


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_mvp_happy_path_dry_run_when_project_created(tmp_path: Path) -> None:
    project = tmp_path / "demo"
    source = tmp_path / "guide.pptx"
    source.write_bytes(b"fake pptx")

    assert run_cli("scripts/init_project.py", "--name", "추락 예방", "--slug", str(project)).returncode == 0
    handoff = project / "HANDOFF.md"
    assert handoff.exists()
    handoff_text = handoff.read_text(encoding="utf-8")
    assert "AGENTS.md" in handoff_text
    assert "docs/evaluation-rubrics.md" in handoff_text
    assert "live Seedance" in handoff_text
    assert run_cli("scripts/validate_plan.py", str(project / "PLAN.md")).returncode == 0
    assert run_cli("scripts/register_sources.py", "--project", str(project), "--source", str(source)).returncode == 0
    assert run_cli("scripts/render_pptx_sources.py", "--project", str(project), "--dry-run").returncode == 0
    assert run_cli("scripts/extract_topics.py", "--project", str(project)).returncode == 0
    assert run_cli("scripts/intake_project.py", "--project", str(project), "--defaults").returncode == 0
    assert run_cli("scripts/search_references.py", "--project", str(project), "--dry-run").returncode == 0
    assert run_cli("scripts/extract_style_dna.py", "--project", str(project)).returncode == 0
    assert run_cli("scripts/plan_storyboard.py", "--project", str(project), "--duration", "30").returncode == 0
    assert run_cli("scripts/validate_project.py", str(project)).returncode == 0
    assert run_cli("scripts/approve_gate.py", "--project", str(project), "--gate", "storyboard").returncode == 0
    assert run_cli("scripts/generate_images.py", "--project", str(project), "--dry-run").returncode == 0
    assert run_cli("scripts/validate_images.py", "--project", str(project), "--dry-run").returncode == 0

    scenes = read_json(project / "story" / "scenes.json")
    assert len(scenes["scenes"]) == 6
    assert scenes["keyframe_count"] == 7


def test_validate_project_rejects_missing_citation_when_scene_invalid(tmp_path: Path) -> None:
    project = tmp_path / "invalid"
    assert run_cli("scripts/init_project.py", "--name", "invalid", "--slug", str(project)).returncode == 0
    assert run_cli("scripts/plan_storyboard.py", "--project", str(project), "--duration", "30").returncode == 0

    scenes_path = project / "story" / "scenes.json"
    scenes = read_json(scenes_path)
    scenes["scenes"][0]["source_citations"] = []
    scenes_path.write_text(json.dumps(scenes, ensure_ascii=False, indent=2), encoding="utf-8")

    result = run_cli("scripts/validate_project.py", str(project))
    assert result.returncode != 0
    assert "source citation" in result.stderr


def test_validate_project_rejects_korean_image_prompt_when_scene_invalid(tmp_path: Path) -> None:
    project = tmp_path / "invalid-prompt"
    assert run_cli("scripts/init_project.py", "--name", "invalid", "--slug", str(project)).returncode == 0
    assert run_cli("scripts/plan_storyboard.py", "--project", str(project), "--duration", "30").returncode == 0

    scenes_path = project / "story" / "scenes.json"
    scenes = read_json(scenes_path)
    scenes["scenes"][0]["image_prompt_en"] = "작업자가 안전모를 착용한다"
    scenes_path.write_text(json.dumps(scenes, ensure_ascii=False, indent=2), encoding="utf-8")

    result = run_cli("scripts/validate_project.py", str(project))
    assert result.returncode != 0
    assert "Korean text" in result.stderr


def test_live_generation_blocked_before_gate_when_not_approved(tmp_path: Path) -> None:
    project = tmp_path / "blocked"
    assert run_cli("scripts/init_project.py", "--name", "blocked", "--slug", str(project)).returncode == 0
    assert run_cli("scripts/plan_storyboard.py", "--project", str(project), "--duration", "30").returncode == 0

    image_result = run_cli("scripts/generate_images.py", "--project", str(project), "--live")
    video_result = run_cli("scripts/generate_seedance.py", "--project", str(project), "--live")

    assert image_result.returncode != 0
    assert "Gate storyboard is not approved" in image_result.stderr
    assert video_result.returncode != 0
    assert "live Seedance requires --execute-paid" in video_result.stderr


def test_approve_gate_rejects_image_to_video_without_cost_disclosure(tmp_path: Path) -> None:
    project = tmp_path / "gate-cost"
    assert run_cli("scripts/init_project.py", "--name", "gate", "--slug", str(project)).returncode == 0

    result = run_cli("scripts/approve_gate.py", "--project", str(project), "--gate", "image_to_video")

    assert result.returncode != 0
    assert "cost disclosure" in result.stderr


def test_live_image_generation_allows_external_upload_disabled_after_gate(tmp_path: Path) -> None:
    project = tmp_path / "upload-blocked"
    assert run_cli("scripts/init_project.py", "--name", "upload", "--slug", str(project)).returncode == 0
    assert run_cli("scripts/plan_storyboard.py", "--project", str(project), "--duration", "30").returncode == 0
    assert run_cli("scripts/approve_gate.py", "--project", str(project), "--gate", "storyboard").returncode == 0

    result = run_cli("scripts/generate_images.py", "--project", str(project), "--live")

    assert result.returncode == 0
    assert "imagegen job(s) prepared" in result.stdout
