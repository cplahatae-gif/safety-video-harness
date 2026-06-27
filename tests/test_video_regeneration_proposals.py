from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", *args],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )


def test_assembly_plan_is_written_from_existing_clips(tmp_path: Path) -> None:
    project = tmp_path / "assembly"
    clips = project / "media" / "video" / "clips"
    clips.mkdir(parents=True)
    (clips / "sc01_sc02.mp4").write_bytes(b"fake")
    (clips / "sc02_sc03.mp4").write_bytes(b"fake")

    result = run_cli("scripts/assemble_video.py", "--project", str(project), "--dry-run")

    assert result.returncode == 0
    plan = load_json(project / "media" / "output" / "assembly_plan.json")
    assert plan["dry_run"] is True
    assert plan["clips"] == ["media/video/clips/sc01_sc02.mp4", "media/video/clips/sc02_sc03.mp4"]
    assert plan["output"] == "media/output/final.mp4"


def test_story_video_alignment_reports_missing_artifacts(tmp_path: Path) -> None:
    project = tmp_path / "alignment"
    storyboard = project / "storyboard" / "scenes.json"
    storyboard.parent.mkdir(parents=True)
    storyboard.write_text(
        json.dumps(
            {
                "scenes": [
                    {
                        "id": "sc01",
                        "start_keyframe": "media/images/approved/sc01.png",
                        "end_keyframe": "media/images/approved/sc02.png",
                        "subtitle_ko": "정지 후 확인",
                    }
                ]
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    result = run_cli("scripts/check_story_video_alignment.py", "--project", str(project))

    assert result.returncode == 0
    report = load_json(project / "qa" / "story_video_alignment.json")
    assert report["passed"] is False
    assert "missing start keyframe" in report["reviews"][0]["blocking_issues"][0]


def test_video_qa_writes_propose_only_regeneration_plan(tmp_path: Path) -> None:
    source = ROOT / "projects" / "remicon-collision-guide" / "video" / "clips" / "sc01_sc02_seedance.mp4"
    if not source.exists():
        return
    project = tmp_path / "video-proposal"
    clips = project / "media" / "video" / "clips"
    clips.mkdir(parents=True)
    (clips / source.name).write_bytes(source.read_bytes())
    inspection = project / "media" / "video" / "inspection" / source.stem
    inspection.mkdir(parents=True)
    for index in range(1, 4):
        (inspection / f"frame_{index:02d}.jpg").write_bytes(b"fake-frame")
    (inspection / "manifest.json").write_text(
        json.dumps(
            {
                "clip": f"media/video/clips/{source.name}",
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
                        "inspection_manifest": f"media/video/inspection/{source.stem}/manifest.json",
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
