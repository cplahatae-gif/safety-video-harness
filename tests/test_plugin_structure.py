from __future__ import annotations

import json
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
        "templates/project/PLAN.md",
        "templates/project/AGENTS.safety.md",
    ]:
        assert (ROOT / path).exists(), path


def test_schema_files_are_valid_json() -> None:
    for path in (ROOT / "schemas").glob("*.json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["type"] == "object"
