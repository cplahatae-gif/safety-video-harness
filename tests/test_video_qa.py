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


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_video_qa_blocks_when_clip_folder_is_empty(tmp_path: Path) -> None:
    project = tmp_path / "empty-video"
    (project / "media" / "video" / "clips").mkdir(parents=True)

    result = run_cli("scripts/validate_video.py", "--project", str(project), "--expected-clips", "2")

    assert result.returncode != 0
    assert "video QA blockers" in result.stderr
    report = load_json(project / "qa" / "video_reviews.json")
    assert report["passed"] is False
    assert report["next_action"] == "regenerate_or_reinspect"
    assert report["rubric_source"] == "docs/evaluation-rubrics.md"
    assert report["few_shot_source"] == "docs/few-shot-examples.md"


def test_video_qa_scores_existing_clips(tmp_path: Path) -> None:
    project = tmp_path / "video-ok"
    clips = project / "media" / "video" / "clips"
    clips.mkdir(parents=True)
    source = ROOT / "projects" / "remicon-collision-guide" / "video" / "clips" / "sc01_sc02_seedance.mp4"
    if not source.exists():
        return
    (clips / "sc01_sc02_seedance.mp4").write_bytes(source.read_bytes())

    result = run_cli("scripts/validate_video.py", "--project", str(project), "--expected-clips", "1")

    assert result.returncode != 0
    assert "manual visual review required" in result.stderr


def test_video_qa_blocks_visual_review_findings(tmp_path: Path) -> None:
    project = tmp_path / "video-blocked"
    clips = project / "media" / "video" / "clips"
    clips.mkdir(parents=True)
    source = ROOT / "projects" / "remicon-collision-guide" / "video" / "clips" / "sc01_sc02_seedance.mp4"
    if not source.exists():
        return
    (clips / "sc01_sc02_seedance.mp4").write_bytes(source.read_bytes())
    qa_dir = project / "qa"
    qa_dir.mkdir(parents=True)
    (qa_dir / "video_manual_review.json").write_text(
        json.dumps(
            {
                "reviews": [
                    {
                        "clip": "sc01_sc02_seedance.mp4",
                        "character_continuity_score": 2,
                        "gaze_motivation_score": 2,
                        "education_clarity_score": 2,
                        "storyboard_alignment_score": 3,
                        "blocking_issues": ["person appears or disappears without motivation"],
                    }
                ]
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    result = run_cli("scripts/validate_video.py", "--project", str(project), "--expected-clips", "1")

    assert result.returncode != 0
    report = load_json(project / "qa" / "video_reviews.json")
    assert report["passed"] is False
    review = report["reviews"][0]
    assert review["rubric_source"] == "docs/evaluation-rubrics.md"
    assert review["few_shot_source"] == "docs/few-shot-examples.md"
    assert review["artifact_path"].endswith("media/video/clips/sc01_sc02_seedance.mp4")
    assert review["blocker_categories"]
    assert "Do not regenerate automatically" in review["regeneration_delta"]
    assert "person appears or disappears without motivation" in json.dumps(report, ensure_ascii=False)


def test_video_qa_passes_with_clean_visual_review(tmp_path: Path) -> None:
    project = tmp_path / "video-ok"
    clips = project / "media" / "video" / "clips"
    clips.mkdir(parents=True)
    source = ROOT / "projects" / "remicon-collision-guide" / "video" / "clips" / "sc01_sc02_seedance.mp4"
    if not source.exists():
        return
    (clips / "sc01_sc02_seedance.mp4").write_bytes(source.read_bytes())
    inspection = project / "media" / "video" / "inspection" / "sc01_sc02_seedance"
    inspection.mkdir(parents=True)
    for index in range(1, 4):
        (inspection / f"frame_{index:02d}.jpg").write_bytes(b"fake-frame")
    manifest = inspection / "manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "clip": "media/video/clips/sc01_sc02_seedance.mp4",
                "tool": "video-frame-analysis",
                "transcript_enabled": False,
                "ocr_lang": "kor+eng",
                "frame_count": 3,
                "frame_paths": ["frame_01.jpg", "frame_02.jpg", "frame_03.jpg"],
                "contact_sheet": None,
                "inspection_questions": [
                    "continuity",
                    "gaze",
                    "education_clarity",
                    "storyboard_alignment",
                ],
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
                        "clip": "sc01_sc02_seedance.mp4",
                        "character_continuity_score": 5,
                        "gaze_motivation_score": 5,
                        "education_clarity_score": 5,
                        "storyboard_alignment_score": 5,
                        "inspection_manifest": "media/video/inspection/sc01_sc02_seedance/manifest.json",
                        "blocking_issues": [],
                    }
                ]
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    result = run_cli("scripts/validate_video.py", "--project", str(project), "--expected-clips", "1")

    assert result.returncode == 0
    report = load_json(project / "qa" / "video_reviews.json")
    assert report["passed"] is True
    assert report["reviews"][0]["technical_score"] == 5
    assert report["thresholds"]["minimum_total_score"] == 20
    rounds = (project / "qa" / "evaluation_rounds.jsonl").read_text(encoding="utf-8")
    assert '"stage": "video"' in rounds
    assert '"item_id": "sc01_sc02_seedance.mp4"' in rounds
    bundle = (
        project
        / "qa"
        / "evaluation_bundles"
        / "video"
        / "sc01_sc02_seedance.mp4"
        / "round_001.json"
    )
    assert bundle.exists()
    role_dir = project / "qa" / "role_evaluations" / "video" / "sc01_sc02_seedance.mp4" / "round_001"
    assert (role_dir / "technical.json").exists()
    assert (project / "qa" / "arbiter_decisions" / "video" / "sc01_sc02_seedance.mp4" / "round_001.json").exists()
    wiki = (project / "llm-wiki" / "evaluation-rounds.md").read_text(encoding="utf-8")
    assert "## video / sc01_sc02_seedance.mp4 / round 1" in wiki


def test_video_qa_requires_inspection_manifest(tmp_path: Path) -> None:
    project = tmp_path / "video-no-inspection"
    clips = project / "media" / "video" / "clips"
    clips.mkdir(parents=True)
    source = ROOT / "projects" / "remicon-collision-guide" / "video" / "clips" / "sc01_sc02_seedance.mp4"
    if not source.exists():
        return
    (clips / "sc01_sc02_seedance.mp4").write_bytes(source.read_bytes())
    qa_dir = project / "qa"
    qa_dir.mkdir(parents=True)
    (qa_dir / "video_manual_review.json").write_text(
        json.dumps(
            {
                "reviews": [
                    {
                        "clip": "sc01_sc02_seedance.mp4",
                        "character_continuity_score": 5,
                        "gaze_motivation_score": 5,
                        "education_clarity_score": 5,
                        "storyboard_alignment_score": 5,
                        "blocking_issues": [],
                    }
                ]
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    result = run_cli("scripts/validate_video.py", "--project", str(project), "--expected-clips", "1")

    assert result.returncode != 0
    assert "inspection manifest required" in result.stderr


def test_video_qa_can_validate_one_named_clip(tmp_path: Path) -> None:
    project = tmp_path / "video-one-clip"
    clips = project / "media" / "video" / "clips"
    clips.mkdir(parents=True)
    source = ROOT / "projects" / "remicon-collision-guide" / "video" / "clips" / "sc01_sc02_seedance.mp4"
    if not source.exists():
        return
    (clips / "accepted.mp4").write_bytes(source.read_bytes())
    (clips / "blocked.mp4").write_bytes(source.read_bytes())
    inspection = project / "media" / "video" / "inspection" / "accepted"
    inspection.mkdir(parents=True)
    for index in range(1, 4):
        (inspection / f"frame_{index:02d}.jpg").write_bytes(b"fake-frame")
    (inspection / "manifest.json").write_text(
        json.dumps(
            {
                "clip": "media/video/clips/accepted.mp4",
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
                        "clip": "accepted.mp4",
                        "inspection_manifest": "media/video/inspection/accepted/manifest.json",
                        "character_continuity_score": 5,
                        "gaze_motivation_score": 5,
                        "education_clarity_score": 5,
                        "storyboard_alignment_score": 5,
                        "blocking_issues": [],
                    },
                    {
                        "clip": "blocked.mp4",
                        "character_continuity_score": 1,
                        "gaze_motivation_score": 1,
                        "education_clarity_score": 1,
                        "storyboard_alignment_score": 1,
                        "blocking_issues": ["ignore when filtering accepted clip"],
                    },
                ]
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    result = run_cli(
        "scripts/validate_video.py",
        "--project",
        str(project),
        "--expected-clips",
        "1",
        "--clip",
        "accepted.mp4",
    )

    assert result.returncode == 0


def test_video_qa_accepts_10_second_validation_clip_when_present(tmp_path: Path) -> None:
    source = (
        ROOT
        / "projects"
        / "remicon-collision-guide"
        / "video"
        / "clips"
        / "sc01_sc02_seedance_validation_10s.mp4"
    )
    if not source.exists():
        return
    project = tmp_path / "video-10s"
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
                        "character_continuity_score": 4,
                        "gaze_motivation_score": 4,
                        "education_clarity_score": 4,
                        "storyboard_alignment_score": 4,
                        "blocking_issues": [],
                    }
                ]
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    result = run_cli(
        "scripts/validate_video.py",
        "--project",
        str(project),
        "--expected-clips",
        "1",
        "--clip",
        source.name,
    )

    assert result.returncode == 0
