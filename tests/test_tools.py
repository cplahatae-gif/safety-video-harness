from __future__ import annotations

from pathlib import Path

from safety_video_harness.tools import check_tools


def test_video_skill_missing_status_is_reported(tmp_path: Path) -> None:
    output = check_tools(skills_root=tmp_path / "missing-skills")

    assert "scenelens: missing" in output
    assert "video-frame-analysis: missing" in output
    assert "understand-video: missing" in output
    assert "seedance-expert: missing" in output
    assert "opencv-mcp-server:" in output
