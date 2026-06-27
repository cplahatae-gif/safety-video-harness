from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HOOKS = ROOT / "app" / "plugin" / "hooks"


def run_live_veto(payload: dict | None = None, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", "hooks/pretooluse-live-veto.py", *args],
        cwd=ROOT / "app" / "plugin",
        check=False,
        text=True,
        input=json.dumps(payload) if payload is not None else None,
        capture_output=True,
    )


def test_live_veto_blocks_direct_imagegen_tool_without_project() -> None:
    payload = {
        "hook_event_name": "PreToolUse",
        "tool_name": "image_gen.imagegen",
        "tool_input": {"prompt": "generate sc07 keyframe"},
    }

    result = run_live_veto(payload)

    assert result.returncode == 2
    assert "direct imagegen" in result.stdout


def test_live_veto_allows_direct_imagegen_when_one_approved_job_is_pending(tmp_path: Path) -> None:
    project = tmp_path / "approved-imagegen"
    (project / "story").mkdir(parents=True)
    (project / "qa").mkdir()
    (project / "project_config.json").write_text("{}", encoding="utf-8")
    (project / "qa" / "approvals.json").write_text(
        json.dumps({"gates": {"storyboard": {"approved": True}}}, ensure_ascii=False),
        encoding="utf-8",
    )
    (project / "story" / "imagegen_jobs.json").write_text(
        json.dumps({"jobs": [{"scene_id": "sc01", "status": "pending_imagegen"}]}, ensure_ascii=False),
        encoding="utf-8",
    )
    payload = {
        "hook_event_name": "PreToolUse",
        "tool_name": "image_gen.imagegen",
        "tool_input": {"prompt": "generate approved pending imagegen job"},
    }

    result = subprocess.run(
        ["python3", str(HOOKS / "pretooluse-live-veto.py")],
        cwd=tmp_path,
        check=False,
        text=True,
        input=json.dumps(payload),
        capture_output=True,
    )

    assert result.returncode == 0
    assert "allow" in result.stdout


def test_live_veto_allows_edit_payload_that_mentions_blocked_media_terms() -> None:
    payload = {
        "hook_event_name": "PreToolUse",
        "tool_name": "Write",
        "tool_input": {"file_path": "docs/notes.md", "content": "Seedance and TTS stay blocked."},
    }

    result = run_live_veto(payload)

    assert result.returncode == 0
    assert "allow" in result.stdout


def test_live_veto_allows_search_commands_that_mention_imagegen() -> None:
    payload = {
        "hook_event_name": "PreToolUse",
        "tool_name": "Bash",
        "tool_input": {"command": "rg imagegen README.md"},
    }

    result = run_live_veto(payload)

    assert result.returncode == 0
    assert "allow" in result.stdout


def test_protected_path_veto_allows_read_only_search_of_protected_terms() -> None:
    payload = {
        "hook_event_name": "PreToolUse",
        "tool_name": "Bash",
        "tool_input": {"command": "rg hooks README.md"},
    }

    result = subprocess.run(
        ["python3", "hooks/pretooluse-protected-path-veto.py"],
        cwd=ROOT / "app" / "plugin",
        check=False,
        text=True,
        input=json.dumps(payload),
        capture_output=True,
    )

    assert result.returncode == 0
    assert "allow" in result.stdout


def test_live_veto_denies_tts_commands_even_with_storyboard_approval(tmp_path: Path) -> None:
    project = tmp_path / "tts-project"
    project.mkdir()
    (project / "project_config.json").write_text('{"external_upload_allowed": true}', encoding="utf-8")
    (project / "qa").mkdir()
    (project / "qa" / "approvals.json").write_text(
        json.dumps({"gates": {"storyboard": {"approved": True}}}, ensure_ascii=False),
        encoding="utf-8",
    )

    result = run_live_veto(None, "uv", "run", "python", "scripts/tts.py", "--project", str(project))

    assert result.returncode == 2
    assert "live TTS" in result.stdout


def test_live_veto_requires_external_upload_for_higgsfield_upload(tmp_path: Path) -> None:
    project = tmp_path / "upload-project"
    project.mkdir()
    (project / "project_config.json").write_text('{"external_upload_allowed": false}', encoding="utf-8")
    (project / "qa").mkdir()
    (project / "qa" / "approvals.json").write_text(
        json.dumps({"gates": {"image_to_video": {"approved": True}}}, ensure_ascii=False),
        encoding="utf-8",
    )

    result = run_live_veto(None, "higgsfield", "upload", "image", "--project", str(project))

    assert result.returncode == 2
    assert "external_upload_allowed" in result.stdout


def test_live_veto_denies_malformed_approval_state_without_traceback(tmp_path: Path) -> None:
    project = tmp_path / "broken-approval-project"
    project.mkdir()
    (project / "qa").mkdir()
    (project / "qa" / "approvals.json").write_text('{"gates": {', encoding="utf-8")

    result = run_live_veto(None, "uv", "run", "python", "scripts/generate_images.py", "--project", str(project), "--live")

    assert result.returncode == 2
    assert "requires approved gate storyboard" in result.stdout
    assert "Traceback" not in result.stderr


def test_secret_veto_blocks_secret_key_names_in_codex_payload() -> None:
    payload = {
        "hook_event_name": "PreToolUse",
        "tool_name": "Bash",
        "tool_input": {"env": {"OPENAI_API_KEY": "redacted-value"}},
    }

    result = subprocess.run(
        ["python3", "hooks/pretooluse-secret-veto.py"],
        cwd=ROOT / "app" / "plugin",
        check=False,
        text=True,
        input=json.dumps(payload),
        capture_output=True,
    )

    assert result.returncode == 2
    assert "deny" in result.stdout
