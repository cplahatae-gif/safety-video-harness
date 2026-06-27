from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

import safety_video_harness.seedance_live as seedance_live
from safety_video_harness.errors import HarnessError
from safety_video_harness.evaluation_rounds import completed_iterations
from safety_video_harness.imagegen_jobs import build_imagegen_jobs, record_image_output
from safety_video_harness.io import read_json, write_json
from safety_video_harness.scene_links import validate_scene_links
from safety_video_harness.video_qa import _review_clip


ROOT = Path(__file__).resolve().parents[1]


def test_read_json_wraps_decode_errors_with_file_path(tmp_path: Path) -> None:
    # Given: a corrupted state file.
    path = tmp_path / "approvals.json"
    path.write_text('{"gates": {', encoding="utf-8")

    # When / Then: reading it fails through the harness boundary with a useful path.
    with pytest.raises(HarnessError, match="unreadable JSON state file"):
        read_json(path)


def test_completed_iterations_tolerates_torn_final_jsonl_line(tmp_path: Path) -> None:
    # Given: a ledger with one valid row followed by a torn append.
    project = tmp_path / "project"
    ledger = project / "qa" / "evaluation_rounds.jsonl"
    ledger.parent.mkdir(parents=True)
    ledger.write_text(
        json.dumps(
            {"stage": "image", "item_id": "sc01", "iteration": 1, "blocking_issues": []},
            ensure_ascii=False,
        )
        + "\n"
        + '{"stage": "image",',
        encoding="utf-8",
    )

    # When / Then: the complete row remains readable.
    assert completed_iterations(project, "image", "sc01") == 1


def test_write_json_rejects_existing_lock_marker(tmp_path: Path) -> None:
    # Given: a lock marker for a state file.
    path = tmp_path / "project_config.json"
    path.with_name("project_config.json.lock").write_text("held\n", encoding="utf-8")

    # When / Then: the write is blocked before touching the state file.
    with pytest.raises(HarnessError, match="single-writer lock is held"):
        write_json(path, {"blocked": True})
    assert not path.exists()


def test_record_image_output_rejects_paths_outside_project(tmp_path: Path) -> None:
    # Given: a tampered imagegen job whose output escapes the project directory.
    project = tmp_path / "project"
    jobs_path = project / "story" / "imagegen_jobs.json"
    jobs_path.parent.mkdir(parents=True)
    write_json(
        jobs_path,
        {
            "jobs": [
                {
                    "scene_id": "sc01",
                    "output": "../escaped.png",
                }
            ]
        },
    )
    generated = tmp_path / "generated.png"
    generated.write_bytes(b"fake")

    # When / Then: recording refuses the escaped path.
    with pytest.raises(HarnessError, match="outside project"):
        record_image_output(project, "sc01", generated)


def test_next_draft_path_skips_version_gaps(tmp_path: Path) -> None:
    # Given: existing drafts with a missing v001.
    project = tmp_path / "project"
    draft_dir = project / "media" / "images" / "draft"
    draft_dir.mkdir(parents=True)
    (draft_dir / "sc01_v002.png").write_bytes(b"v2")
    (draft_dir / "sc01_v003.png").write_bytes(b"v3")

    # When: a regenerate job is built.
    jobs = build_imagegen_jobs(
        project,
        [{"scene_id": "sc01", "prompt": "prompt"}],
        scene_filter="sc01",
        regenerate=True,
    )

    # Then: the next path is max-version + 1, not len(existing) + 1.
    assert jobs["jobs"][0]["output"] == "media/images/draft/sc01_v004.png"


def test_protected_path_veto_uses_config_and_is_case_insensitive() -> None:
    # Given / When: a protected path listed only in protected_paths.json is edited.
    result = subprocess.run(
        ["python3", "hooks/pretooluse-protected-path-veto.py", "write", "APPROVALS.JSON"],
        cwd=ROOT / "app" / "plugin",
        check=False,
        text=True,
        capture_output=True,
    )

    # Then: the hook denies it case-insensitively.
    assert result.returncode == 2
    assert "deny" in result.stdout


def test_protected_path_veto_blocks_project_config_changes() -> None:
    result = subprocess.run(
        ["python3", "hooks/pretooluse-protected-path-veto.py", "write", "project_config.json"],
        cwd=ROOT / "app" / "plugin",
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 2
    assert "deny" in result.stdout


def test_secret_veto_reads_codex_stdin_payload() -> None:
    payload = {
        "hook_event_name": "PreToolUse",
        "tool_name": "Write",
        "tool_input": {"file_path": ".env", "content": "OPENAI_API_KEY=sk-test"},
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


def test_secret_veto_is_case_insensitive_for_common_secret_shapes() -> None:
    # Given / When: lower-case secret-like content is passed to the hook.
    result = subprocess.run(
        ["python3", "hooks/pretooluse-secret-veto.py", "write", "api_key=sk-test"],
        cwd=ROOT / "app" / "plugin",
        check=False,
        text=True,
        capture_output=True,
    )

    # Then: the hook denies it.
    assert result.returncode == 2
    assert "deny" in result.stdout


def test_stop_sentinel_uses_repository_root_not_cwd(tmp_path: Path) -> None:
    # Given: the repository has the done sentinel but the caller CWD is elsewhere.
    sentinel = ROOT / ".harness" / "DONE"
    sentinel.parent.mkdir(exist_ok=True)
    sentinel.write_text("done\n", encoding="utf-8")
    try:
        # When: the hook is executed from a different CWD.
        result = subprocess.run(
            ["python3", str(ROOT / "app" / "plugin" / "hooks" / "stop-sentinel-guard.py")],
            cwd=tmp_path,
            check=False,
            text=True,
            capture_output=True,
        )
    finally:
        sentinel.unlink(missing_ok=True)

    # Then: it still sees the repository-level sentinel.
    assert result.returncode == 0
    assert "allow stop" in result.stdout


def test_schema_validation_hook_runs_project_validation(tmp_path: Path) -> None:
    project = tmp_path / "project"
    (project / "storyboard").mkdir(parents=True)

    result = subprocess.run(
        ["python3", "hooks/posttooluse-schema-validation.py", "--project", str(project)],
        cwd=ROOT / "app" / "plugin",
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 2
    assert "story/scenes.json is missing" in result.stdout


def test_evidence_feedback_blocks_completion_without_evidence() -> None:
    result = subprocess.run(
        ["python3", "hooks/posttooluse-evidence-feedback.py", "complete", "all done"],
        cwd=ROOT / "app" / "plugin",
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 2
    assert "evidence" in result.stdout


def test_video_review_reports_missing_h264_as_harness_error(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # Given: ffprobe metadata without an h264 video stream.
    project = tmp_path / "project"
    clip = project / "video" / "clip.webm"
    clip.parent.mkdir(parents=True)
    clip.write_bytes(b"fake")

    def fake_probe(path: Path) -> dict:
        return {
            "format": {"duration": "5.0"},
            "streams": [{"codec_name": "vp9", "width": 1280, "height": 720}],
        }

    monkeypatch.setattr("safety_video_harness.video_qa._probe", fake_probe)

    # When / Then: QA fails cleanly instead of raising StopIteration.
    with pytest.raises(HarnessError, match="no h264 video stream"):
        _review_clip(project, clip, manual_review={})


def test_seedance_cli_timeout_raises_harness_error(monkeypatch: pytest.MonkeyPatch) -> None:
    # Given: a Higgsfield CLI call that times out.
    def fake_run(*args, **kwargs) -> subprocess.CompletedProcess[str]:
        raise subprocess.TimeoutExpired(cmd=["higgsfield"], timeout=1)

    monkeypatch.setattr(subprocess, "run", fake_run)

    # When / Then: the timeout is converted to a harness error.
    with pytest.raises(HarnessError, match="timed out"):
        seedance_live._run_cli(["higgsfield", "generate", "create"])


def test_scene_link_validation_rejects_empty_storyboard(tmp_path: Path) -> None:
    # Given: a storyboard with no scenes.
    project = tmp_path / "project"
    storyboard = project / "story" / "scenes.json"
    storyboard.parent.mkdir(parents=True)
    write_json(storyboard, {"scenes": []})

    # When / Then: scene-link validation fails instead of passing an empty chain.
    with pytest.raises(HarnessError, match="no storyboard scenes"):
        validate_scene_links(project)


def test_scene_link_validation_checks_scene_id_order(tmp_path: Path) -> None:
    # Given: a scene whose id does not match its sliding-chain position.
    project = tmp_path / "project"
    storyboard = project / "story" / "scenes.json"
    storyboard.parent.mkdir(parents=True)
    write_json(
        storyboard,
        {
            "scenes": [
                {
                    "id": "sc02",
                    "start_keyframe": "media/images/approved/sc01.png",
                    "end_keyframe": "media/images/approved/sc02.png",
                }
            ]
        },
    )

    # When / Then: the mismatch is a storyboard blocker.
    with pytest.raises(HarnessError, match="sliding chain mismatch"):
        validate_scene_links(project)
