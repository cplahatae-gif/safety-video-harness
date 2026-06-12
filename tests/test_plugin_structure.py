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
        "agents/storyteller/AGENT.md",
        "agents/storyteller/references/storyteller-reference.md",
        "agents/lead-style-agent/AGENT.md",
        "agents/lead-style-agent/references/lead-style-reference.md",
        "agents/scene-prompt-agent/AGENT.md",
        "agents/scene-prompt-agent/references/scene-prompt-reference.md",
        "agents/visual-director-arbiter/AGENT.md",
        "agents/visual-director-arbiter/references/visual-director-arbiter-reference.md",
        "agents/continuity-qa/AGENT.md",
        "agents/continuity-qa/references/continuity-qa-reference.md",
        "agents/video-qa/AGENT.md",
        "agents/video-qa/references/video-qa-reference.md",
        "agents/visual-continuity-director/AGENT.md",
        "agents/visual-continuity-director/references/visual-continuity-reference.md",
        "hooks/pretooluse-live-veto.py",
        "hooks/protected_paths.json",
        "schemas/project_config.schema.json",
        "schemas/scenes.schema.json",
        "style-guides/catalog.json",
        "style-guides/korean-industrial-webtoon/STYLE_GUIDE.md",
        "templates/project/PLAN.md",
        "templates/project/AGENTS.safety.md",
        "docs/generative-media-reference-index.md",
        "docs/reference-sources.md",
        "docs/evaluation-rubrics.md",
        "docs/few-shot-examples.md",
        "docs/higgsfield-seedance-local-reference.md",
        "docs/agent-skill-reference-onepager.html",
        "scripts/plan_image_prompt_team.py",
    ]:
        assert (ROOT / path).exists(), path


def test_skills_package_local_references_exist() -> None:
    for path in [
        "skills/topic-extractor/references/topic-extractor-reference.md",
        "skills/story-writer/references/story-writer-reference.md",
        "skills/style-ref-search/references/style-ref-search-reference.md",
        "skills/seedance-prompting/references/seedance-prompting-reference.md",
        "skills/image-consistency-check/references/image-consistency-reference.md",
        "skills/video-inspect/references/video-inspect-reference.md",
    ]:
        assert (ROOT / path).exists(), path


def test_agent_and_skill_references_contain_local_operating_notes() -> None:
    reference_paths = sorted((ROOT / "agents").glob("*/references/*.md")) + sorted(
        (ROOT / "skills").glob("*/references/*.md")
    )

    assert len(reference_paths) == 13
    for path in reference_paths:
        text = path.read_text(encoding="utf-8")
        assert "Source links:" in text, path
        assert "## Local Reference Notes" in text, path
        assert "## Use In This Harness" in text, path
        assert "## Operational Rules" in text, path
        assert "## Output Expectations" in text, path
        local_notes = text.split("## Local Reference Notes", 1)[1].split("## Use In This Harness", 1)[0]
        assert len(local_notes.split()) >= 140, path


def test_project_rules_force_local_guides_before_execution() -> None:
    rules = (ROOT / "AGENTS.md").read_text(encoding="utf-8")

    assert "Before using any local agent or skill" in rules
    assert "package-local `references/*.md`" in rules
    assert "docs/evaluation-rubrics.md" in rules
    assert "docs/few-shot-examples.md" in rules
    assert "docs/higgsfield-seedance-local-reference.md" in rules


def test_agent_and_skill_docs_link_required_local_guides() -> None:
    docs = sorted((ROOT / "agents").glob("*/AGENT.md")) + sorted((ROOT / "skills").glob("*/SKILL.md"))

    assert len(docs) == 13
    for path in docs:
        text = path.read_text(encoding="utf-8")
        assert "references/" in text, path
        assert "docs/evaluation-rubrics.md" in text, path
        assert "docs/few-shot-examples.md" in text, path


def test_local_guides_are_actionable_not_link_only() -> None:
    guide_paths = [
        ROOT / "docs" / "evaluation-rubrics.md",
        ROOT / "docs" / "few-shot-examples.md",
        ROOT / "docs" / "higgsfield-seedance-local-reference.md",
    ]

    for path in guide_paths:
        text = path.read_text(encoding="utf-8")
        assert len(text.split()) >= 250, path
    assert "Critical blockers" in (ROOT / "docs" / "evaluation-rubrics.md").read_text(encoding="utf-8")
    assert "Bad:" in (ROOT / "docs" / "few-shot-examples.md").read_text(encoding="utf-8")
    assert "Good:" in (ROOT / "docs" / "few-shot-examples.md").read_text(encoding="utf-8")
    assert "generate cost" in (ROOT / "docs" / "higgsfield-seedance-local-reference.md").read_text(
        encoding="utf-8"
    )


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
