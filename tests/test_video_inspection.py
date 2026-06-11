from __future__ import annotations

import subprocess
from pathlib import Path

from safety_video_harness.errors import HarnessError
from safety_video_harness.video_inspection import inspect_video


ROOT = Path(__file__).resolve().parents[1]


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", *args],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )


def test_missing_video_skill_fails_cleanly(tmp_path: Path) -> None:
    clip = ROOT / "projects" / "remicon-collision-guide" / "video" / "clips" / "sc01_sc02_seedance.mp4"
    if not clip.exists():
        return

    try:
        inspect_video(tmp_path, clip, "scenelens", no_transcript=True, skills_root=tmp_path / "missing")
    except HarnessError as exc:
        assert "scenelens skill is missing" in str(exc)
    else:
        raise AssertionError("expected missing skill to fail")


def test_video_frame_analysis_manifest_is_created(tmp_path: Path) -> None:
    clip = ROOT / "projects" / "remicon-collision-guide" / "video" / "clips" / "sc01_sc02_seedance.mp4"
    if not clip.exists():
        return
    project = tmp_path / "project"

    result = run_cli(
        "scripts/inspect_video.py",
        "--project",
        str(project),
        "--clip",
        str(clip),
        "--tool",
        "video-frame-analysis",
        "--no-transcript",
    )

    assert result.returncode == 0, result.stderr
    manifest = project / "video" / "inspection" / "sc01_sc02_seedance" / "manifest.json"
    assert manifest.exists()
