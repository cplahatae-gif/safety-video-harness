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


def add_asset_lock_references(project: Path) -> None:
    assets = {
        "refs/people/signal-worker.png": b"fake cast image",
        "refs/equipment/bct-truck.png": b"fake equipment image",
        "refs/approved/spaces/plant-entry.png": b"fake space image",
    }
    for relative_path, content in assets.items():
        path = project / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        path.with_suffix(".md").write_text(f"Lock {path.stem} for production continuity.\n", encoding="utf-8")


def add_approved_keyframes(project: Path, *scene_ids: str) -> None:
    approved_dir = project / "media" / "images" / "approved"
    approved_dir.mkdir(parents=True, exist_ok=True)
    for scene_id in scene_ids:
        (approved_dir / f"{scene_id}.png").write_bytes(f"approved {scene_id}".encode())


def write_passing_image_qa(project: Path, scene_id: str) -> None:
    qa_dir = project / "qa"
    qa_dir.mkdir(parents=True, exist_ok=True)
    review = {
        "scene_id": scene_id,
        "blocking_issues": [],
        "decision": "approve_for_video",
        "manual_visual_review": {"status": "present"},
    }
    (qa_dir / "image_reviews.json").write_text(
        json.dumps({"dry_run": False, "reviews": [review]}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (qa_dir / "image_qa_loop.json").write_text(
        json.dumps({"passed": True}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def test_live_imagegen_jobs_require_storyboard_gate_not_external_upload(tmp_path: Path) -> None:
    project = tmp_path / "imagegen-gates"
    prepare_storyboard_project(project)

    missing_gate = run_cli("scripts/generate_images.py", "--project", str(project), "--live")
    assert missing_gate.returncode != 0
    assert "Gate storyboard is not approved" in missing_gate.stderr

    assert run_cli("scripts/approve_gate.py", "--project", str(project), "--gate", "storyboard").returncode == 0
    result = run_cli("scripts/generate_images.py", "--project", str(project), "--live", "--only", "sc01")
    assert result.returncode == 0
    assert "imagegen job(s) prepared" in result.stdout


def test_imagegen_jobs_and_only_filter_are_written_after_approval(tmp_path: Path) -> None:
    project = tmp_path / "imagegen-jobs"
    prepare_storyboard_project(project)
    assert run_cli("scripts/approve_gate.py", "--project", str(project), "--gate", "storyboard").returncode == 0
    add_approved_keyframes(project, "sc01", "sc02")

    result = run_cli("scripts/generate_images.py", "--project", str(project), "--live", "--only", "sc03")

    assert result.returncode == 0
    jobs = load_json(project / "story" / "imagegen_jobs.json")
    assert jobs["execution_mode"] == "codex_builtin_imagegen"
    assert len(jobs["jobs"]) == 1
    job = jobs["jobs"][0]
    assert job["scene_id"] == "sc03"
    assert job["status"] == "pending_imagegen"
    assert job["output"] == "media/images/draft/sc03_v001.png"
    assert "imagegen" in job["tool"]
    assert job["generation_chain"]["mode"] == "sequential_reference_edit"
    assert job["generation_chain"]["anchor_image"] == "media/images/approved/sc01.png"
    assert job["generation_chain"]["previous_approved_image"] == "media/images/approved/sc02.png"
    assert "media/images/approved/sc01.png" in job["reference_images"]
    assert "media/images/approved/sc02.png" in job["reference_images"]
    assert "OpenAI" not in json.dumps(jobs, ensure_ascii=False)


def test_imagegen_jobs_reject_scene_without_previous_approved_keyframe(tmp_path: Path) -> None:
    project = tmp_path / "imagegen-missing-previous"
    prepare_storyboard_project(project)
    assert run_cli("scripts/approve_gate.py", "--project", str(project), "--gate", "storyboard").returncode == 0
    add_approved_keyframes(project, "sc01")

    result = run_cli("scripts/generate_images.py", "--project", str(project), "--live", "--only", "sc03")

    assert result.returncode != 0
    assert "previous approved keyframe is required" in result.stderr


def test_imagegen_jobs_reject_scene_without_anchor_keyframe(tmp_path: Path) -> None:
    project = tmp_path / "imagegen-missing-anchor"
    prepare_storyboard_project(project)
    assert run_cli("scripts/approve_gate.py", "--project", str(project), "--gate", "storyboard").returncode == 0
    add_approved_keyframes(project, "sc02")

    result = run_cli("scripts/generate_images.py", "--project", str(project), "--live", "--only", "sc03")

    assert result.returncode != 0
    assert "anchor approved keyframe sc01 is required" in result.stderr


def test_imagegen_jobs_include_asset_lock_policy(tmp_path: Path) -> None:
    project = tmp_path / "imagegen-asset-lock"
    prepare_storyboard_project(project)
    add_asset_lock_references(project)
    assert run_cli("scripts/approve_gate.py", "--project", str(project), "--gate", "storyboard").returncode == 0
    allow_upload(project)

    result = run_cli("scripts/generate_images.py", "--project", str(project), "--live", "--only", "sc01")

    assert result.returncode == 0
    jobs = load_json(project / "story" / "imagegen_jobs.json")
    job = jobs["jobs"][0]
    assert job["asset_lock"]["status"] == "production_locked"
    assert job["production_consistency_policy"]["text_only_multi_frame_production_allowed"] is False
    assert "Production consistency policy" in job["prompt"]
    manifest = load_json(project / "refs" / "asset-lock" / "asset_lock_manifest.json")
    assert manifest["higgsfield_seedance_strategy"]["required_inputs"] == ["start_image", "end_image"]


def test_live_imagegen_without_filter_prepares_next_unapproved_keyframe_only(tmp_path: Path) -> None:
    project = tmp_path / "imagegen-next-keyframe"
    prepare_storyboard_project(project)
    assert run_cli("scripts/approve_gate.py", "--project", str(project), "--gate", "storyboard").returncode == 0

    result = run_cli("scripts/generate_images.py", "--project", str(project), "--live")

    assert result.returncode == 0
    jobs = load_json(project / "story" / "imagegen_jobs.json")
    assert len(jobs["jobs"]) == 1
    assert jobs["jobs"][0]["scene_id"] == "sc01"
    assert jobs["jobs"][0]["generation_chain"]["mode"] == "anchor_keyframe"


def test_imagegen_jobs_include_final_end_keyframe_after_prior_keyframes_are_approved(tmp_path: Path) -> None:
    project = tmp_path / "imagegen-final-keyframe"
    prepare_storyboard_project(project)
    assert run_cli("scripts/approve_gate.py", "--project", str(project), "--gate", "storyboard").returncode == 0
    add_approved_keyframes(project, "sc01", "sc02", "sc03", "sc04", "sc05", "sc06")

    result = run_cli("scripts/generate_images.py", "--project", str(project), "--live")

    assert result.returncode == 0
    jobs = load_json(project / "story" / "imagegen_jobs.json")
    job = jobs["jobs"][0]
    assert len(jobs["jobs"]) == 1
    assert job["scene_id"] == "sc07"
    assert job["output"] == "media/images/draft/sc07_v001.png"
    assert job["generation_chain"]["previous_approved_image"] == "media/images/approved/sc06.png"
    assert "final end keyframe" in job["prompt"]


def test_storyboard_dashboard_is_written_for_gate_review(tmp_path: Path) -> None:
    project = tmp_path / "storyboard-dashboard"
    prepare_storyboard_project(project)

    result = run_cli("scripts/build_storyboard_dashboard.py", "--project", str(project))

    assert result.returncode == 0
    dashboard = project / "dashboard" / "storyboard-review.html"
    assert dashboard.exists()
    html = dashboard.read_text(encoding="utf-8")
    assert "Storyboard Review" in html
    assert "sc01" in html
    assert "레미콘" in html


def test_collect_image_outputs_records_matching_generated_files(tmp_path: Path) -> None:
    project = tmp_path / "collect-imagegen"
    prepare_storyboard_project(project)
    assert run_cli("scripts/approve_gate.py", "--project", str(project), "--gate", "storyboard").returncode == 0
    allow_upload(project)
    assert run_cli("scripts/generate_images.py", "--project", str(project), "--live", "--only", "sc01").returncode == 0
    generated_dir = tmp_path / "generated"
    generated_dir.mkdir()
    (generated_dir / "sc01.png").write_bytes(b"fake generated image")

    result = run_cli(
        "scripts/collect_image_outputs.py",
        "--project",
        str(project),
        "--source-dir",
        str(generated_dir),
    )

    assert result.returncode == 0
    assert (project / "media" / "images" / "draft" / "sc01_v001.png").read_bytes() == b"fake generated image"


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
    assert (project / "media" / "images" / "draft" / "sc01_v001.png").read_bytes() == b"fake generated image v1"

    assert run_cli("scripts/generate_images.py", "--project", str(project), "--live", "--only", "sc01", "--regenerate").returncode == 0
    jobs = load_json(project / "story" / "imagegen_jobs.json")
    assert jobs["jobs"][0]["output"] == "media/images/draft/sc01_v002.png"
    assert (project / "media" / "images" / "draft" / "sc01_v001.png").read_bytes() == b"fake generated image v1"


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
    blocked_approval = run_cli("scripts/approve_image.py", "--project", str(project), "--scene-id", "sc01")
    assert blocked_approval.returncode != 0
    assert "image approval requires" in blocked_approval.stderr
    write_passing_image_qa(project, "sc01")
    approved = run_cli("scripts/approve_image.py", "--project", str(project), "--scene-id", "sc01")
    assert approved.returncode == 0
    assert (project / "media" / "images" / "approved" / "sc01.png").exists()

    fake2 = tmp_path / "fake-sc01-v2.png"
    fake2.write_bytes(b"fake generated image v2")
    assert run_cli("scripts/generate_images.py", "--project", str(project), "--live", "--only", "sc01", "--regenerate").returncode == 0
    assert run_cli("scripts/record_image_output.py", "--project", str(project), "--scene-id", "sc01", "--generated-file", str(fake2)).returncode == 0
    write_passing_image_qa(project, "sc01")
    assert run_cli("scripts/approve_image.py", "--project", str(project), "--scene-id", "sc01").returncode == 0
    assert (project / "media" / "images" / "approved" / "sc01_v001.png").read_bytes() == b"fake generated image"
    assert (project / "media" / "images" / "approved" / "sc01.png").read_bytes() == b"fake generated image v2"
