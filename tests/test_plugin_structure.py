from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

SKILL_IDS = [
    "topic-extractor",
    "story-writer",
    "seedance-prompting",
    "image-consistency-check",
    "video-inspect",
    "style-ref-search",
]

AGENT_IDS = [
    "storyteller",
    "lead-style-agent",
    "scene-prompt-agent",
    "visual-director-arbiter",
    "continuity-qa",
    "video-qa",
    "visual-continuity-director",
]


def test_claude_settings_and_harness_assets_exist() -> None:
    settings = json.loads((ROOT / ".claude" / "settings.json").read_text(encoding="utf-8"))
    hooks = settings["hooks"]
    for event in ["SessionStart", "PreToolUse", "PostToolUse", "Stop"]:
        assert event in hooks, event

    assert (ROOT / "CLAUDE.md").exists()
    assert (ROOT / "AGENTS.md").exists()
    for path in [
        *[f".claude/skills/{skill_id}/SKILL.md" for skill_id in SKILL_IDS],
        *[f".claude/agents/{agent_id}.md" for agent_id in AGENT_IDS],
        "agents/storyteller/references/storyteller-reference.md",
        "agents/lead-style-agent/references/lead-style-reference.md",
        "agents/scene-prompt-agent/references/scene-prompt-reference.md",
        "agents/visual-director-arbiter/references/visual-director-arbiter-reference.md",
        "agents/continuity-qa/references/continuity-qa-reference.md",
        "agents/video-qa/references/video-qa-reference.md",
        "agents/visual-continuity-director/references/visual-continuity-reference.md",
        "hooks/pretooluse-live-veto.py",
        "hooks/protected_paths.json",
        "schemas/project_config.schema.json",
        "schemas/scenes.schema.json",
        "scripts/codex_image.sh",
        "scripts/gemini_image.sh",
        "style-guides/catalog.json",
        "style-guides/korean-industrial-webtoon/STYLE_GUIDE.md",
        "templates/project/PLAN.md",
        "templates/project/AGENTS.safety.md",
        "templates/project/HANDOFF.md",
        "docs/generative-media-reference-index.md",
        "docs/reference-sources.md",
        "docs/evaluation-rubrics.md",
        "docs/few-shot-examples.md",
        "docs/higgsfield-seedance-local-reference.md",
        "docs/agent-skill-reference-onepager.html",
        "scripts/plan_image_prompt_team.py",
    ]:
        assert (ROOT / path).exists(), path


def test_skills_and_agents_have_frontmatter() -> None:
    for skill_id in SKILL_IDS:
        text = (ROOT / ".claude" / "skills" / skill_id / "SKILL.md").read_text(encoding="utf-8")
        assert text.startswith("---\n"), skill_id
        frontmatter = text.split("---", 2)[1]
        assert f"name: {skill_id}" in frontmatter, skill_id
        assert "description:" in frontmatter, skill_id
    for agent_id in AGENT_IDS:
        text = (ROOT / ".claude" / "agents" / f"{agent_id}.md").read_text(encoding="utf-8")
        assert text.startswith("---\n"), agent_id
        frontmatter = text.split("---", 2)[1]
        assert f"name: {agent_id}" in frontmatter, agent_id
        assert "description:" in frontmatter, agent_id


def test_skills_package_local_references_exist() -> None:
    for skill_id in SKILL_IDS:
        references = sorted((ROOT / ".claude" / "skills" / skill_id / "references").glob("*.md"))
        assert references, skill_id


def test_agent_and_skill_references_contain_local_operating_notes() -> None:
    reference_paths = sorted((ROOT / "agents").glob("*/references/*.md")) + sorted(
        (ROOT / ".claude" / "skills").glob("*/references/*.md")
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
    docs = sorted((ROOT / ".claude" / "agents").glob("*.md")) + sorted(
        (ROOT / ".claude" / "skills").glob("*/SKILL.md")
    )

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


def _run_live_veto(command: str) -> subprocess.CompletedProcess[str]:
    payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": command}})
    return subprocess.run(
        ["python3", "hooks/pretooluse-live-veto.py"],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
        input=payload,
    )


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

    result = _run_live_veto(f"uv run python scripts/generate_images.py --project {project} --live")

    assert result.returncode == 0


def test_live_veto_hook_blocks_unapproved_live_command(tmp_path: Path) -> None:
    project = tmp_path / "unapproved-live-hook"
    project.mkdir()
    (project / "project_config.json").write_text('{"external_upload_allowed": true}', encoding="utf-8")
    (project / "approvals.json").write_text(
        json.dumps({"gates": {"storyboard": {"approved": False}}}, ensure_ascii=False),
        encoding="utf-8",
    )

    result = _run_live_veto(f"uv run python scripts/generate_images.py --project {project} --live")

    assert result.returncode == 2
    assert "approved gate storyboard" in result.stderr
