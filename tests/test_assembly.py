from __future__ import annotations

from pathlib import Path

import pytest

from safety_video_harness.assembly import assemble_video
from safety_video_harness.errors import HarnessError
from safety_video_harness.io import read_json


def test_dry_run_writes_plan_and_concat_list(tmp_path: Path) -> None:
    project = tmp_path / "project"
    clips = project / "video" / "clips"
    clips.mkdir(parents=True)
    (clips / "sc01_sc02.mp4").write_bytes(b"a")
    (clips / "sc02_sc03.mp4").write_bytes(b"b")

    assemble_video(project, dry_run=True)

    plan = read_json(project / "video" / "final" / "assembly_plan.json")
    assert plan["output"] == "video/final/final.mp4"
    assert plan["clips"] == ["video/clips/sc01_sc02.mp4", "video/clips/sc02_sc03.mp4"]
    concat = (project / "video" / "final" / "concat.txt").read_text()
    assert concat.count("file '") == 2
    assert not (project / "video" / "final" / "final.mp4").exists()


def test_no_clips_raises(tmp_path: Path) -> None:
    project = tmp_path / "project"
    (project / "video" / "clips").mkdir(parents=True)
    with pytest.raises(HarnessError, match="no video clips"):
        assemble_video(project, dry_run=True)
