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


def test_operational_storyboard_requires_selected_topic_when_topics_exist(tmp_path: Path) -> None:
    project = tmp_path / "topic-required"
    prepare_project(project)

    missing = run_cli("scripts/plan_storyboard.py", "--project", str(project), "--duration", "30")
    assert missing.returncode != 0
    assert "topic must be selected" in missing.stderr

    selected = run_cli("scripts/select_topic.py", "--project", str(project), "--topic-id", "topic-002")
    assert selected.returncode == 0

    config = load_json(project / "project_config.json")
    assert config["selected_topic_id"] == "topic-002"
    assert config["topic"] == "신호수 배치와 후방카메라 확인 절차"

    planned = run_cli("scripts/plan_storyboard.py", "--project", str(project), "--duration", "30")
    assert planned.returncode == 0


def test_rendering_mode_is_recorded_for_media_extract_fallback(tmp_path: Path) -> None:
    project = tmp_path / "render-mode"
    prepare_project(project)

    sources = load_json(project / "sources" / "sources.json")["sources"]
    assert sources[0]["rendering_mode"] == "media_extract"
    assert sources[0]["render_warning"] == ""
    assert len(sources[0]["rendered_assets"]) == 12


def test_reference_profile_manifest_and_approval_workflow(tmp_path: Path) -> None:
    project = tmp_path / "reference-profile"
    prepare_project(project)

    cast_dir = project / "model" / "cast"
    candidate_dir = project / "ref" / "candidates"
    (cast_dir / "worker-001-front.png").write_bytes(b"fake image")
    (cast_dir / "worker-001.profile.md").write_text("manual worker profile wins", encoding="utf-8")
    (candidate_dir / "style-candidate.png").write_bytes(b"fake image")
    (candidate_dir / "style-candidate.md").write_text("candidate style reference", encoding="utf-8")

    analyzed = run_cli("scripts/analyze_reference_assets.py", "--project", str(project), "--dry-run")
    assert analyzed.returncode == 0

    manifest = load_json(project / "ref" / "approved" / "reference_assets.json")
    asset_blob = json.dumps(manifest, ensure_ascii=False)
    assert "worker-001-front.png" in asset_blob
    assert "manual worker profile wins" in asset_blob
    assert "style-candidate.png" not in asset_blob

    approved = run_cli(
        "scripts/approve_reference.py",
        "--project",
        str(project),
        "--candidate",
        "style-candidate.png",
    )
    assert approved.returncode == 0
    assert (project / "ref" / "approved" / "style-candidate.png").exists()
    provenance = load_json(project / "ref" / "approved" / "reference_approvals.json")
    assert provenance["approvals"][0]["source"] == "ref/candidates/style-candidate.png"


def test_reference_profile_manifest_includes_categorized_approved_references(tmp_path: Path) -> None:
    project = tmp_path / "reference-profile-categories"
    prepare_project(project)

    work_dir = project / "ref" / "approved" / "work"
    space_dir = project / "ref" / "approved" / "space"
    work_dir.mkdir(parents=True, exist_ok=True)
    space_dir.mkdir(parents=True, exist_ok=True)
    (work_dir / "loading-zone-control.png").write_bytes(b"fake image")
    (work_dir / "loading-zone-control.md").write_text(
        "work situation shows a controlled loading zone with a visible stop action",
        encoding="utf-8",
    )
    (work_dir / "manual-signal-rule.md").write_text(
        "md-only reference describes a signal worker gaze rule",
        encoding="utf-8",
    )
    (space_dir / "plant-route-map.png").write_bytes(b"fake image")
    (space_dir / "plant-route-map.md").write_text(
        "space reference shows separated vehicle lanes and pedestrian route",
        encoding="utf-8",
    )

    analyzed = run_cli("scripts/analyze_reference_assets.py", "--project", str(project), "--dry-run")
    assert analyzed.returncode == 0

    manifest = load_json(project / "ref" / "approved" / "reference_assets.json")
    asset_blob = json.dumps(manifest, ensure_ascii=False)
    assert "work_situation_reference" in asset_blob
    assert "controlled loading zone" in asset_blob
    assert "md-only reference describes a signal worker gaze rule" in asset_blob
    assert "space_reference" in asset_blob
    assert "separated vehicle lanes" in asset_blob


def test_reference_profile_sidecar_matches_exact_cast_identity(tmp_path: Path) -> None:
    project = tmp_path / "reference-profile-exact-sidecar"
    prepare_project(project)

    cast_dir = project / "model" / "cast"
    (cast_dir / "worker-001-front.png").write_bytes(b"fake image")
    (cast_dir / "worker-0010.profile.md").write_text("wrong worker profile", encoding="utf-8")
    (cast_dir / "worker-001.profile.md").write_text("correct worker profile", encoding="utf-8")

    analyzed = run_cli("scripts/analyze_reference_assets.py", "--project", str(project), "--dry-run")

    assert analyzed.returncode == 0
    manifest = load_json(project / "ref" / "approved" / "reference_assets.json")
    asset_blob = json.dumps(manifest, ensure_ascii=False)
    assert "correct worker profile" in asset_blob
    assert "wrong worker profile" not in asset_blob


def test_approve_reference_can_target_categorized_reference_folder(tmp_path: Path) -> None:
    project = tmp_path / "reference-approval-role"
    prepare_project(project)

    candidate_dir = project / "ref" / "candidates"
    (candidate_dir / "work-scene.png").write_bytes(b"fake image")
    (candidate_dir / "work-scene.md").write_text("work scene reference", encoding="utf-8")

    approved = run_cli(
        "scripts/approve_reference.py",
        "--project",
        str(project),
        "--candidate",
        "work-scene.png",
        "--role",
        "work",
    )

    assert approved.returncode == 0
    assert (project / "ref" / "approved" / "work" / "work-scene.png").exists()
    assert (project / "ref" / "approved" / "work" / "work-scene.md").exists()
    provenance = load_json(project / "ref" / "approved" / "reference_approvals.json")
    assert provenance["approvals"][0]["target"] == "ref/approved/work/work-scene.png"


def test_gate2_requires_cost_images_video_plan_upload_and_qa(tmp_path: Path) -> None:
    project = tmp_path / "gate2"
    prepare_project(project)
    assert run_cli("scripts/select_topic.py", "--project", str(project), "--topic-id", "topic-001").returncode == 0
    assert run_cli("scripts/extract_style_dna.py", "--project", str(project)).returncode == 0
    assert run_cli("scripts/plan_storyboard.py", "--project", str(project), "--duration", "30").returncode == 0
    assert run_cli("scripts/approve_gate.py", "--project", str(project), "--gate", "storyboard").returncode == 0
    assert run_cli("scripts/generate_images.py", "--project", str(project), "--dry-run").returncode == 0
    assert run_cli("scripts/generate_seedance.py", "--project", str(project), "--dry-run").returncode == 0

    blocked = run_cli("scripts/approve_gate.py", "--project", str(project), "--gate", "image_to_video", "--estimated-credits", "12")
    assert blocked.returncode != 0
    assert "external_upload_allowed" in blocked.stderr

    config_path = project / "project_config.json"
    config = load_json(config_path)
    config["external_upload_allowed"] = True
    config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    blocked = run_cli("scripts/approve_gate.py", "--project", str(project), "--gate", "image_to_video", "--estimated-credits", "12")
    assert blocked.returncode != 0
    assert "approved image" in blocked.stderr

    for index in range(1, 8):
        (project / "images" / "approved" / f"sc{index:02d}.png").write_bytes(b"fake image")

    blocked = run_cli("scripts/approve_gate.py", "--project", str(project), "--gate", "image_to_video", "--estimated-credits", "12")
    assert blocked.returncode != 0
    assert "image QA" in blocked.stderr

    assert run_cli("scripts/validate_images.py", "--project", str(project), "--dry-run").returncode == 0
    estimated = run_cli("scripts/estimate_video_cost.py", "--project", str(project), "--estimated-credits", "12")
    assert estimated.returncode == 0
    estimate = load_json(project / "qa" / "video_cost_estimate.json")
    assert estimate["estimated_credits"] == 12
    assert estimate["clip_count"] == 6

    approved = run_cli("scripts/approve_gate.py", "--project", str(project), "--gate", "image_to_video", "--estimated-credits", "12")
    assert approved.returncode == 0


def test_gate2_rejects_partial_image_qa_coverage(tmp_path: Path) -> None:
    project = tmp_path / "gate2-partial-qa"
    prepare_project(project)
    assert run_cli("scripts/select_topic.py", "--project", str(project), "--topic-id", "topic-001").returncode == 0
    assert run_cli("scripts/extract_style_dna.py", "--project", str(project)).returncode == 0
    assert run_cli("scripts/plan_storyboard.py", "--project", str(project), "--duration", "30").returncode == 0
    assert run_cli("scripts/evaluate_storyboard.py", "--project", str(project)).returncode == 0
    assert run_cli("scripts/approve_gate.py", "--project", str(project), "--gate", "storyboard").returncode == 0
    assert run_cli("scripts/generate_seedance.py", "--project", str(project), "--dry-run").returncode == 0

    config_path = project / "project_config.json"
    config = load_json(config_path)
    config["external_upload_allowed"] = True
    config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for index in range(1, 8):
        (project / "images" / "approved" / f"sc{index:02d}.png").write_bytes(b"fake image")
    (project / "qa" / "image_reviews.json").write_text(
        json.dumps(
            {
                "dry_run": False,
                "reviews": [{"scene_id": "sc01", "blocking_issues": [], "total_score": 25}],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    result = run_cli("scripts/approve_gate.py", "--project", str(project), "--gate", "image_to_video", "--estimated-credits", "12")

    assert result.returncode != 0
    assert "image QA coverage" in result.stderr


def test_approval_write_respects_single_writer_lock(tmp_path: Path) -> None:
    project = tmp_path / "locked"
    assert run_cli("scripts/init_project.py", "--name", "locked", "--slug", str(project)).returncode == 0
    (project / "approvals.json.lock").write_text("held by test\n", encoding="utf-8")

    result = run_cli("scripts/approve_gate.py", "--project", str(project), "--gate", "storyboard")

    assert result.returncode != 0
    assert "lock is held" in result.stderr
