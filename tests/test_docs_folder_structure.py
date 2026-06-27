from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_docs_describe_moved_root_and_project_layout() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    onepager = (ROOT / "docs" / "repository-folder-structure-onepager.html").read_text(encoding="utf-8")

    for required in [
        "app/plugin/.codex-plugin/plugin.json",
        "app/plugin/agents/",
        "app/harness/package/safety_video_harness/",
        "app/harness/cli/",
        "projects/<slug>/input/",
        "projects/<slug>/refs/",
        "projects/<slug>/story/",
        "projects/<slug>/media/",
        "projects/<slug>/qa/",
    ]:
        assert required in readme

    assert "app/plugin/agents/<agent-id>/references/*.md" in readme
    assert "app/plugin/skills/<skill-id>/references/*.md" in readme
    assert "refs/people" in agents
    assert "refs/approved/spaces" in agents
    assert "app/plugin" in onepager
    assert "app/harness" in onepager
