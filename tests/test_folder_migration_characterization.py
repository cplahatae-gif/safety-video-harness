from __future__ import annotations

import json
import subprocess
from pathlib import Path

from safety_video_harness.reference_catalog import catalog_for_manifest
from safety_video_harness.scene_links import validate_scene_links
from safety_video_harness.validation import validate_project


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


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def prepare_storyboard_project(project: Path) -> None:
    assert run_cli("scripts/init_project.py", "--name", "레미콘 충돌 예방", "--slug", str(project)).returncode == 0
    assert run_cli("scripts/register_sources.py", "--project", str(project), "--source", str(FIXTURE)).returncode == 0
    assert run_cli("scripts/render_pptx_sources.py", "--project", str(project), "--dry-run", "--mode", "media_extract").returncode == 0
    assert run_cli("scripts/extract_topics.py", "--project", str(project)).returncode == 0
    assert run_cli("scripts/select_topic.py", "--project", str(project), "--topic-id", "topic-001").returncode == 0
    assert run_cli("scripts/extract_style_dna.py", "--project", str(project)).returncode == 0
    assert run_cli("scripts/plan_storyboard.py", "--project", str(project), "--duration", "30").returncode == 0


def test_root_script_project_init_creates_new_layout_when_called_directly(tmp_path: Path) -> None:
    project = tmp_path / "new-layout"

    result = run_cli("scripts/init_project.py", "--name", "현재 구조", "--slug", str(project))

    assert result.returncode == 0
    for relative_path in [
        "input/sources/raw",
        "input/sources/rendered",
        "refs/people",
        "refs/ppe",
        "refs/equipment",
        "refs/approved/people",
        "refs/approved/work",
        "refs/approved/spaces",
        "story/versions",
        "media/images/draft",
        "media/images/approved",
        "media/video/clips",
        "qa",
        "qa/evidence",
        "qa/state",
    ]:
        assert (project / relative_path).exists(), relative_path
    assert (project / "qa" / "approvals.json").exists()
    config = read_json(project / "project_config.json")
    assert config["project_layout_version"] == 2


def test_plugin_manifest_and_hook_registration_use_current_root_paths() -> None:
    manifest = read_json(ROOT / ".codex-plugin" / "plugin.json")
    plugin_manifest = read_json(ROOT / "app" / "plugin" / ".codex-plugin" / "plugin.json")
    hooks = read_json(ROOT / "app" / "plugin" / "hooks" / "hooks.json")
    registered_hooks = json.dumps(hooks, ensure_ascii=False)

    assert manifest["compatibilityShim"] is True
    assert manifest["skills"] == "./app/plugin/skills/"
    assert manifest["hooks"] == "./app/plugin/hooks/hooks.json"
    assert plugin_manifest["skills"] == "./skills/"
    assert plugin_manifest["hooks"] == "./hooks/hooks.json"
    assert "hooks/session-start-anchor.py" in registered_hooks
    assert "hooks/pretooluse-live-veto.py" in registered_hooks

    result = subprocess.run(
        ["python3", "hooks/session-start-anchor.py"],
        cwd=ROOT / "app" / "plugin",
        check=False,
        text=True,
        capture_output=True,
    )
    assert result.returncode == 0
    assert "Safety Video Harness Mission Anchor" in result.stdout


def test_reference_catalog_reads_current_old_project_reference_paths(tmp_path: Path) -> None:
    project = tmp_path / "references"
    assets = {
        "model/cast/signal-worker.png": b"cast",
        "model/ppe/safety-gloves.png": b"ppe",
        "product/equipment/bct-truck.png": b"equipment",
        "ref/approved/space/plant-entry.png": b"space",
    }
    for relative_path, content in assets.items():
        path = project / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        path.with_suffix(".md").write_text(f"Use {path.stem} as a locked reference.\n", encoding="utf-8")

    manifest = catalog_for_manifest(project)

    assert {item["role"] for item in manifest} == {"cast", "ppe", "equipment", "space_reference"}
    assert {item["path"] for item in manifest} == set(assets)


def test_reference_catalog_reads_new_project_reference_paths(tmp_path: Path) -> None:
    project = tmp_path / "new-references"
    assert run_cli("scripts/init_project.py", "--name", "refs", "--slug", str(project)).returncode == 0
    assets = {
        "refs/people/signal-worker.png": b"cast",
        "refs/ppe/safety-gloves.png": b"ppe",
        "refs/equipment/bct-truck.png": b"equipment",
        "refs/approved/spaces/plant-entry.png": b"space",
    }
    for relative_path, content in assets.items():
        path = project / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        path.with_suffix(".md").write_text(f"Use {path.stem} as a locked reference.\n", encoding="utf-8")

    manifest = catalog_for_manifest(project)

    assert {item["role"] for item in manifest} == {"cast", "ppe", "equipment", "space_reference"}
    assert {item["path"] for item in manifest} == set(assets)


def test_old_project_storyboard_path_still_validates(tmp_path: Path) -> None:
    project = tmp_path / "old-storyboard"
    scenes_path = project / "storyboard" / "scenes.json"
    scenes_path.parent.mkdir(parents=True)
    scenes_path.write_text(
        json.dumps(
            {
                "scenes": [
                    {
                        "id": "sc01",
                        "source_citations": [
                            {"source_id": "src-001", "page_or_slide": 1, "claim": "작업 전 동선 확인"}
                        ],
                        "subtitle_ko": "동선을 먼저 확인하세요.",
                        "image_prompt_en": "Industrial safety scene, clear route, no text.",
                    }
                ]
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    assert validate_project(project) == "project valid"


def test_old_project_scene_link_paths_are_still_accepted(tmp_path: Path) -> None:
    project = tmp_path / "old-scene-links"
    scenes_path = project / "storyboard" / "scenes.json"
    scenes_path.parent.mkdir(parents=True)
    scenes_path.write_text(
        json.dumps(
            {
                "scenes": [
                    {
                        "id": "sc01",
                        "start_keyframe": "images/approved/sc01.png",
                        "end_keyframe": "images/approved/sc02.png",
                    }
                ]
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    assert validate_scene_links(project) == "validated 1 scene link(s)"


def test_imagegen_job_contract_uses_new_project_paths(tmp_path: Path) -> None:
    project = tmp_path / "imagegen-job-contract"
    prepare_storyboard_project(project)
    assert run_cli("scripts/approve_gate.py", "--project", str(project), "--gate", "storyboard").returncode == 0
    approved_dir = project / "media" / "images" / "approved"
    approved_dir.mkdir(parents=True, exist_ok=True)
    (approved_dir / "sc01.png").write_bytes(b"approved sc01")
    (approved_dir / "sc02.png").write_bytes(b"approved sc02")

    result = run_cli("scripts/generate_images.py", "--project", str(project), "--live", "--only", "sc03")

    assert result.returncode == 0
    jobs = read_json(project / "story" / "imagegen_jobs.json")
    job = jobs["jobs"][0]
    assert job["output"] == "media/images/draft/sc03_v001.png"
    assert job["generation_chain"]["anchor_image"] == "media/images/approved/sc01.png"
    assert job["generation_chain"]["previous_approved_image"] == "media/images/approved/sc02.png"
