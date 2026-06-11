from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", *args],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )


def test_video_qa_writes_propose_only_regeneration_plan(tmp_path: Path) -> None:
    source = ROOT / "projects" / "remicon-collision-guide" / "video" / "clips" / "sc01_sc02_seedance.mp4"
    if not source.exists():
        return
    project = tmp_path / "video-proposal"
    clips = project / "video" / "clips"
    clips.mkdir(parents=True)
    (clips / source.name).write_bytes(source.read_bytes())
    inspection = project / "video" / "inspection" / source.stem
    inspection.mkdir(parents=True)
    for index in range(1, 4):
        (inspection / f"frame_{index:02d}.jpg").write_bytes(b"fake-frame")
    (inspection / "manifest.json").write_text(
        json.dumps(
            {
                "clip": f"video/clips/{source.name}",
                "tool": "video-frame-analysis",
                "transcript_enabled": False,
                "ocr_lang": "kor+eng",
                "frame_count": 3,
                "frame_paths": ["frame_01.jpg", "frame_02.jpg", "frame_03.jpg"],
                "contact_sheet": None,
                "inspection_questions": ["continuity", "gaze", "education_clarity", "storyboard_alignment"],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    qa_dir = project / "qa"
    qa_dir.mkdir(parents=True)
    (qa_dir / "video_manual_review.json").write_text(
        json.dumps(
            {
                "reviews": [
                    {
                        "clip": source.name,
                        "inspection_manifest": f"video/inspection/{source.stem}/manifest.json",
                        "character_continuity_score": 2,
                        "gaze_motivation_score": 2,
                        "education_clarity_score": 2,
                        "storyboard_alignment_score": 2,
                        "blocking_issues": ["gaze direction is not motivated"],
                    }
                ]
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    result = run_cli("scripts/validate_video.py", "--project", str(project), "--expected-clips", "1")

    assert result.returncode != 0
    proposals = json.loads((project / "qa" / "video_regeneration_proposals.json").read_text(encoding="utf-8"))
    assert proposals["mode"] == "propose_only"
    assert proposals["paid_generation_allowed"] is False
    assert "gaze direction is not motivated" in proposals["proposals"][0]["deficiencies"]
