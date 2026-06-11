from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_plugin_manifest_and_harness_assets_exist() -> None:
    manifest = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))

    assert manifest["name"] == "safety-video-harness"
    assert (ROOT / "AGENTS.md").exists()
    for path in [
        "skills/topic-extractor/SKILL.md",
        "skills/story-writer/SKILL.md",
        "skills/seedance-prompting/SKILL.md",
        "skills/image-consistency-check/SKILL.md",
        "skills/video-inspect/SKILL.md",
        "skills/style-ref-search/SKILL.md",
        "agents/storyteller.md",
        "agents/continuity-qa.md",
        "agents/video-qa.md",
        "hooks/pretooluse-live-veto.py",
        "hooks/protected_paths.json",
        "schemas/project_config.schema.json",
        "schemas/scenes.schema.json",
        "style-guides/catalog.json",
        "style-guides/korean-industrial-webtoon/STYLE_GUIDE.md",
        "templates/project/PLAN.md",
        "templates/project/AGENTS.safety.md",
    ]:
        assert (ROOT / path).exists(), path


def test_schema_files_are_valid_json() -> None:
    for path in (ROOT / "schemas").glob("*.json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["type"] == "object"


def test_session_start_anchor_reloads_nonnegotiable_mission_rules() -> None:
    result = subprocess.run(
        ["python3", "hooks/session-start-anchor.py"],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0
    output = result.stdout
    assert "Safety Video Harness Mission Anchor" in output
    assert "No live imagegen, live Seedance, live TTS, or paid calls" in output
    assert "parallel role evaluators" in output
    assert "critical veto" in output
    assert "Video failures are propose-only" in output
    assert "Start with an intake interview" in output
    assert "reference images" in output
    assert "selected style guide" in output


def test_live_veto_hook_allows_approved_project_live_command(tmp_path: Path) -> None:
    project = tmp_path / "approved-live-hook"
    project.mkdir()
    (project / "project_config.json").write_text('{"external_upload_allowed": true}', encoding="utf-8")
    (project / "approvals.json").write_text(
        json.dumps(
            {
                "gates": {
                    "storyboard": {"approved": True},
                    "image_to_video": {"approved": False},
                }
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            "python3",
            "hooks/pretooluse-live-veto.py",
            "uv",
            "run",
            "python",
            "scripts/generate_images.py",
            "--project",
            str(project),
            "--live",
        ],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0
    assert "allow" in result.stdout
