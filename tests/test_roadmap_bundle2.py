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


def prepare_storyboard_project(project: Path) -> None:
    assert run_cli("scripts/init_project.py", "--name", "레미콘 충돌 예방", "--slug", str(project)).returncode == 0
    assert run_cli("scripts/register_sources.py", "--project", str(project), "--source", str(FIXTURE)).returncode == 0
    assert run_cli("scripts/render_pptx_sources.py", "--project", str(project), "--dry-run", "--mode", "media_extract").returncode == 0
    assert run_cli("scripts/extract_topics.py", "--project", str(project)).returncode == 0
    assert run_cli("scripts/select_topic.py", "--project", str(project), "--topic-id", "topic-001").returncode == 0
    assert run_cli("scripts/extract_style_dna.py", "--project", str(project)).returncode == 0
    assert run_cli("scripts/plan_storyboard.py", "--project", str(project), "--duration", "30").returncode == 0


def allow_upload(project: Path) -> None:
    config_path = project / "project_config.json"
    config = load_json(config_path)
    config["external_upload_allowed"] = True
    config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def test_live_imagegen_jobs_require_gate_and_upload(tmp_path: Path) -> None:
    project = tmp_path / "imagegen-gates"
    prepare_storyboard_project(project)

    missing_gate = run_cli("scripts/generate_images.py", "--project", str(project), "--live")
    assert missing_gate.returncode != 0
    assert "Gate storyboard is not approved" in missing_gate.stderr

    assert run_cli("scripts/approve_gate.py", "--project", str(project), "--gate", "storyboard").returncode == 0
    missing_upload = run_cli("scripts/generate_images.py", "--project", str(project), "--live")
    assert missing_upload.returncode != 0
    assert "external_upload_allowed" in missing_upload.stderr


def test_imagegen_jobs_and_only_filter_are_written_after_approval(tmp_path: Path) -> None:
    project = tmp_path / "imagegen-jobs"
    prepare_storyboard_project(project)
    assert run_cli("scripts/approve_gate.py", "--project", str(project), "--gate", "storyboard").returncode == 0
    allow_upload(project)

    result = run_cli("scripts/generate_images.py", "--project", str(project), "--live", "--only", "sc03")

    assert result.returncode == 0
    jobs = load_json(project / "prompts" / "imagegen_jobs.json")
    assert jobs["execution_mode"] == "codex_cli_imagegen"
    assert len(jobs["jobs"]) == 1
    job = jobs["jobs"][0]
    assert job["scene_id"] == "sc03"
    assert job["status"] == "pending_imagegen"
    assert job["output"] == "images/draft/sc03_v001.png"
    assert "imagegen" in job["tool"]
    assert "OpenAI" not in json.dumps(jobs, ensure_ascii=False)


def test_imagegen_jobs_include_final_end_keyframe_when_generating_all(tmp_path: Path) -> None:
    project = tmp_path / "imagegen-final-keyframe"
    prepare_storyboard_project(project)
    assert run_cli("scripts/approve_gate.py", "--project", str(project), "--gate", "storyboard").returncode == 0
    allow_upload(project)

    result = run_cli("scripts/generate_images.py", "--project", str(project), "--live")

    assert result.returncode == 0
    scenes = load_json(project / "storyboard" / "scenes.json")
    jobs = load_json(project / "prompts" / "imagegen_jobs.json")
    scene_ids = [job["scene_id"] for job in jobs["jobs"]]
    assert len(jobs["jobs"]) == scenes["keyframe_count"]
    assert scene_ids[-1] == "sc07"
    assert jobs["jobs"][-1]["output"] == "images/draft/sc07_v001.png"
    assert "final end keyframe" in jobs["jobs"][-1]["prompt"]


def test_fake_generated_file_is_recorded_without_overwrite_and_regenerate_versions(tmp_path: Path) -> None:
    project = tmp_path / "record-output"
    prepare_storyboard_project(project)
    assert run_cli("scripts/approve_gate.py", "--project", str(project), "--gate", "storyboard").returncode == 0
    allow_upload(project)
    assert run_cli("scripts/generate_images.py", "--project", str(project), "--live", "--only", "sc01").returncode == 0

    fake = tmp_path / "fake-sc01.png"
    fake.write_bytes(b"fake generated image v1")
    recorded = run_cli("scripts/record_image_output.py", "--project", str(project), "--scene-id", "sc01", "--generated-file", str(fake))
    assert recorded.returncode == 0
    assert (project / "images" / "draft" / "sc01_v001.png").read_bytes() == b"fake generated image v1"

    assert run_cli("scripts/generate_images.py", "--project", str(project), "--live", "--only", "sc01", "--regenerate").returncode == 0
    jobs = load_json(project / "prompts" / "imagegen_jobs.json")
    assert jobs["jobs"][0]["output"] == "images/draft/sc01_v002.png"
    assert (project / "images" / "draft" / "sc01_v001.png").read_bytes() == b"fake generated image v1"


def test_image_review_blocks_missing_draft_and_approve_preserves_existing_image(tmp_path: Path) -> None:
    project = tmp_path / "image-qa"
    prepare_storyboard_project(project)
    assert run_cli("scripts/approve_gate.py", "--project", str(project), "--gate", "storyboard").returncode == 0
    allow_upload(project)
    assert run_cli("scripts/generate_images.py", "--project", str(project), "--live", "--only", "sc01").returncode == 0

    blocked = run_cli("scripts/validate_images.py", "--project", str(project), "--only", "sc01")
    assert blocked.returncode == 0
    reviews = load_json(project / "qa" / "image_reviews.json")["reviews"]
    assert reviews[0]["decision"] == "regenerate"
    assert "missing draft image" in reviews[0]["blocking_issues"]

    fake = tmp_path / "fake-sc01.png"
    fake.write_bytes(b"fake generated image")
    assert run_cli("scripts/record_image_output.py", "--project", str(project), "--scene-id", "sc01", "--generated-file", str(fake)).returncode == 0
    approved = run_cli("scripts/approve_image.py", "--project", str(project), "--scene-id", "sc01")
    assert approved.returncode == 0
    assert (project / "images" / "approved" / "sc01.png").exists()

    fake2 = tmp_path / "fake-sc01-v2.png"
    fake2.write_bytes(b"fake generated image v2")
    assert run_cli("scripts/generate_images.py", "--project", str(project), "--live", "--only", "sc01", "--regenerate").returncode == 0
    assert run_cli("scripts/record_image_output.py", "--project", str(project), "--scene-id", "sc01", "--generated-file", str(fake2)).returncode == 0
    assert run_cli("scripts/approve_image.py", "--project", str(project), "--scene-id", "sc01").returncode == 0
    assert (project / "images" / "approved" / "sc01_v001.png").read_bytes() == b"fake generated image"
    assert (project / "images" / "approved" / "sc01.png").read_bytes() == b"fake generated image v2"
