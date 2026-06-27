from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "app" / "plugin"


def test_plugin_manifest_and_harness_assets_exist() -> None:
    manifest = json.loads((PLUGIN / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
    root_manifest = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))

    assert manifest["name"] == "safety-video-harness"
    assert manifest["hooks"] == "./hooks/hooks.json"
    assert root_manifest["compatibilityShim"] is True
    assert root_manifest["hooks"] == "./app/plugin/hooks/hooks.json"
    assert (ROOT / "AGENTS.md").exists()
    for path in [
        "app/plugin/skills/topic-extractor/SKILL.md",
        "app/plugin/skills/story-writer/SKILL.md",
        "app/plugin/skills/seedance-prompting/SKILL.md",
        "app/plugin/skills/image-consistency-check/SKILL.md",
        "app/plugin/skills/video-inspect/SKILL.md",
        "app/plugin/skills/style-ref-search/SKILL.md",
        "app/plugin/agents/storyteller/AGENT.md",
        "app/plugin/agents/storyteller/references/storyteller-reference.md",
        "app/plugin/agents/lead-style-agent/AGENT.md",
        "app/plugin/agents/lead-style-agent/references/lead-style-reference.md",
        "app/plugin/agents/scene-prompt-agent/AGENT.md",
        "app/plugin/agents/scene-prompt-agent/references/scene-prompt-reference.md",
        "app/plugin/agents/visual-director-arbiter/AGENT.md",
        "app/plugin/agents/visual-director-arbiter/references/visual-director-arbiter-reference.md",
        "app/plugin/agents/continuity-qa/AGENT.md",
        "app/plugin/agents/continuity-qa/references/continuity-qa-reference.md",
        "app/plugin/agents/video-qa/AGENT.md",
        "app/plugin/agents/video-qa/references/video-qa-reference.md",
        "app/plugin/agents/visual-continuity-director/AGENT.md",
        "app/plugin/agents/visual-continuity-director/references/visual-continuity-reference.md",
        "app/plugin/hooks/hooks.json",
        "app/plugin/hooks/pretooluse-live-veto.py",
        "app/plugin/hooks/protected_paths.json",
        "app/harness/schemas/project_config.schema.json",
        "app/harness/schemas/scenes.schema.json",
        "references/style/catalog.json",
        "references/style/korean-industrial-webtoon/STYLE_GUIDE.md",
        "references/examples/storyboard-drafts/scenes.json",
        "references/examples/storyboard-drafts/sc01.png",
        "app/harness/templates/project/PLAN.md",
        "app/harness/templates/project/AGENTS.safety.md",
        "app/harness/templates/project/HANDOFF.md",
        "docs/generative-media-reference-index.md",
        "docs/reference-sources.md",
        "docs/evaluation-rubrics.md",
        "docs/few-shot-examples.md",
        "docs/higgsfield-seedance-local-reference.md",
        "docs/agent-skill-reference-onepager.html",
        "scripts/plan_image_prompt_team.py",
    ]:
        assert (ROOT / path).exists(), path


def test_root_keeps_only_current_top_level_buckets() -> None:
    for obsolete_path in [
        "plans",
        "project-review",
        "storyboard",
        "scenarios",
        "scenes.json",
    ]:
        assert not (ROOT / obsolete_path).exists(), obsolete_path

    for current_path in [
        "app",
        "projects",
        "references",
        "docs",
        "tests",
        "fixtures",
        "scripts",
        "docs/plans/safety-video",
        "docs/reviews/project",
        "references/examples/storyboard-drafts",
    ]:
        assert (ROOT / current_path).exists(), current_path


def test_hooks_json_registers_all_entrypoint_hooks() -> None:
    payload = json.loads((PLUGIN / "hooks" / "hooks.json").read_text(encoding="utf-8"))
    registered = json.dumps(payload, ensure_ascii=False)

    for path in [
        "hooks/session-start-anchor.py",
        "hooks/pretooluse-live-veto.py",
        "hooks/pretooluse-secret-veto.py",
        "hooks/pretooluse-protected-path-veto.py",
        "hooks/posttooluse-schema-validation.py",
        "hooks/posttooluse-scene-link-validation.py",
        "hooks/posttooluse-evidence-feedback.py",
        "hooks/stop-sentinel-guard.py",
    ]:
        assert path in registered

    for hook_group in ["SessionStart", "PreToolUse", "PostToolUse", "Stop"]:
        assert hook_group in payload["hooks"]
    assert "functions.apply_patch" in registered
    assert "image_gen.imagegen" in registered


def test_skills_package_local_references_exist() -> None:
    for path in [
        "app/plugin/skills/topic-extractor/references/topic-extractor-reference.md",
        "app/plugin/skills/story-writer/references/story-writer-reference.md",
        "app/plugin/skills/style-ref-search/references/style-ref-search-reference.md",
        "app/plugin/skills/seedance-prompting/references/seedance-prompting-reference.md",
        "app/plugin/skills/image-consistency-check/references/image-consistency-reference.md",
        "app/plugin/skills/video-inspect/references/video-inspect-reference.md",
    ]:
        assert (ROOT / path).exists(), path


def test_agent_and_skill_references_contain_local_operating_notes() -> None:
    reference_paths = sorted((PLUGIN / "agents").glob("*/references/*.md")) + sorted(
        (PLUGIN / "skills").glob("*/references/*.md")
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
    docs = sorted((PLUGIN / "agents").glob("*/AGENT.md")) + sorted((PLUGIN / "skills").glob("*/SKILL.md"))

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
    for path in (ROOT / "app" / "harness" / "schemas").glob("*.json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["type"] == "object"


def test_session_start_anchor_reloads_nonnegotiable_mission_rules() -> None:
    result = subprocess.run(
        ["python3", "hooks/session-start-anchor.py"],
        cwd=PLUGIN,
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
    (project / "qa").mkdir()
    (project / "qa" / "approvals.json").write_text(
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
            "app/plugin/hooks/pretooluse-live-veto.py",
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


def test_live_veto_hook_reads_codex_stdin_payload_for_imagegen(tmp_path: Path) -> None:
    project = tmp_path / "approved-imagegen-hook"
    project.mkdir()
    (project / "project_config.json").write_text('{"external_upload_allowed": false}', encoding="utf-8")
    (project / "qa").mkdir()
    (project / "qa" / "approvals.json").write_text(
        json.dumps({"gates": {"storyboard": {"approved": True}}}, ensure_ascii=False),
        encoding="utf-8",
    )
    payload = {
        "hook_event_name": "PreToolUse",
        "tool_name": "Bash",
        "tool_input": {
            "command": f"uv run python scripts/generate_images.py --project {project} --live --only sc01"
        },
    }

    result = subprocess.run(
        ["python3", "app/plugin/hooks/pretooluse-live-veto.py"],
        cwd=ROOT,
        check=False,
        text=True,
        input=json.dumps(payload),
        capture_output=True,
    )

    assert result.returncode == 0
    assert "allow" in result.stdout


def test_live_veto_hook_requires_upload_for_seedance_stdin_payload(tmp_path: Path) -> None:
    project = tmp_path / "approved-seedance-hook"
    project.mkdir()
    (project / "project_config.json").write_text('{"external_upload_allowed": false}', encoding="utf-8")
    (project / "qa").mkdir()
    (project / "qa" / "approvals.json").write_text(
        json.dumps({"gates": {"image_to_video": {"approved": True}}}, ensure_ascii=False),
        encoding="utf-8",
    )
    payload = {
        "hook_event_name": "PreToolUse",
        "tool_name": "Bash",
        "tool_input": {
            "command": f"uv run python scripts/generate_seedance.py --project {project} --live --execute-paid"
        },
    }

    result = subprocess.run(
        ["python3", "app/plugin/hooks/pretooluse-live-veto.py"],
        cwd=ROOT,
        check=False,
        text=True,
        input=json.dumps(payload),
        capture_output=True,
    )

    assert result.returncode == 2
    assert "external_upload_allowed" in result.stdout
