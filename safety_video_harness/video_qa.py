from __future__ import annotations

import json
import subprocess
from pathlib import Path

from safety_video_harness.evaluation_arbiter import aggregate_arbiter_decision
from safety_video_harness.evaluation_rounds import (
    completed_iterations,
    record_evaluation_round,
    write_evaluation_bundle,
)
from safety_video_harness.errors import HarnessError
from safety_video_harness.io import read_json, write_json
from safety_video_harness.stage_role_reviews import video_role_reviews


MINIMUM_TOTAL_SCORE = 20


def validate_video_outputs(project: Path, expected_clips: int, clip_name: str | None = None) -> str:
    clip_dir = project / "video" / "clips"
    clips = sorted(clip_dir.glob("*.mp4"))
    if clip_name is not None:
        clips = [clip for clip in clips if clip.name == clip_name]
    manual_reviews = _manual_reviews(project)
    reviews = [_review_clip(project, clip, manual_reviews.get(clip.name)) for clip in clips]
    _record_video_evaluation_rounds(project, reviews)
    blockers = []
    if len(clips) < expected_clips:
        blockers.append(f"expected {expected_clips} clip(s), found {len(clips)}")
    blockers.extend(issue for review in reviews for issue in review["blocking_issues"])
    passed = not blockers and all(int(review["total_score"]) >= MINIMUM_TOTAL_SCORE for review in reviews)
    report = {
        "passed": passed,
        "thresholds": {
            "minimum_total_score": MINIMUM_TOTAL_SCORE,
            "expected_duration_sec": "5_or_10_validation",
            "expected_width": 1280,
            "expected_height": 720,
        },
        "reviews": reviews,
        "blockers": blockers,
        "next_action": "accept_or_manual_story_review" if passed else "regenerate_or_reinspect",
    }
    write_json(project / "qa" / "video_reviews.json", report)
    write_json(project / "qa" / "video_regeneration_proposals.json", _regeneration_proposals(reviews, passed))
    if not passed:
        detail = "; ".join(blockers) if blockers else "score below threshold"
        raise HarnessError(f"video QA blockers: {detail}")
    return f"validated {len(reviews)} video clip(s)"


def _regeneration_proposals(reviews: list[dict], passed: bool) -> dict:
    proposals = [
        {
            "clip": review["clip"],
            "deficiencies": list(review["blocking_issues"]),
            "proposal": _video_proposal(list(review["blocking_issues"])),
        }
        for review in reviews
        if review["blocking_issues"]
    ]
    return {
        "mode": "none" if passed else "propose_only",
        "paid_generation_allowed": False,
        "reason": (
            "Video generation is paid. The harness only proposes fixes; user approval is required before another live run."
        ),
        "proposals": proposals,
    }


def _video_proposal(deficiencies: list[str]) -> str:
    if not deficiencies:
        return ""
    return (
        "Do not regenerate automatically. Proposed next paid-run changes: "
        + "; ".join(deficiencies)
        + ". First tighten storyboard/keyframes, then ask the user before any Seedance call."
    )


def _review_clip(project: Path, path: Path, manual_review: dict | None) -> dict:
    metadata = _probe(path)
    duration = float(metadata["format"]["duration"])
    video_stream = next(stream for stream in metadata["streams"] if stream.get("codec_name") == "h264")
    width = int(video_stream["width"])
    height = int(video_stream["height"])
    duration_ok = 4.5 <= duration <= 6.5 or 9.5 <= duration <= 10.6
    technical_score = 5 if duration_ok and width == 1280 and height == 720 else 3
    inspection = _inspection_review(project, path, manual_review)
    visual = _visual_scores(manual_review)
    continuity_score = visual["character_continuity_score"]
    gaze_score = visual["gaze_motivation_score"]
    story_match_score = visual["storyboard_alignment_score"]
    safety_score = visual["education_clarity_score"]
    total_score = technical_score + continuity_score + gaze_score + story_match_score + safety_score
    blockers = [] if technical_score >= 4 else [f"technical metadata mismatch for {path.name}"]
    blockers.extend(inspection["blocking_issues"])
    blockers.extend(visual["blocking_issues"])
    return {
        "clip": str(path),
        "duration_sec": round(duration, 3),
        "width": width,
        "height": height,
        "technical_score": technical_score,
        "continuity_score": continuity_score,
        "gaze_motivation_score": gaze_score,
        "story_match_score": story_match_score,
        "safety_score": safety_score,
        "manual_review_required": manual_review is None,
        "inspection_manifest": inspection["manifest"],
        "inspection_frame_count": inspection["frame_count"],
        "total_score": total_score,
        "blocking_issues": blockers,
        "scoring_rubric": {
            "technical_score": "Duration and resolution match the bounded Seedance test contract.",
            "continuity_score": "People and vehicles do not appear, disappear, or change roles without story motivation.",
            "gaze_motivation_score": "Character gaze points toward the active hazard, signal person, driver, or route cue.",
            "story_match_score": "Motion supports the intended prevention beat.",
            "safety_score": "The clip communicates the safety lesson without relying on hidden context.",
        },
    }


def _manual_reviews(project: Path) -> dict[str, dict]:
    path = project / "qa" / "video_manual_review.json"
    if not path.exists():
        return {}
    reviews = read_json(path).get("reviews", [])
    return {str(review["clip"]): review for review in reviews}


def _visual_scores(manual_review: dict | None) -> dict:
    if manual_review is None:
        return {
            "character_continuity_score": 0,
            "gaze_motivation_score": 0,
            "education_clarity_score": 0,
            "storyboard_alignment_score": 0,
            "blocking_issues": ["manual visual review required"],
        }
    issues = list(manual_review.get("blocking_issues", []))
    for key in [
        "character_continuity_score",
        "gaze_motivation_score",
        "education_clarity_score",
        "storyboard_alignment_score",
    ]:
        if int(manual_review.get(key, 0)) < 4:
            issues.append(f"{key} below minimum 4")
    return {
        "character_continuity_score": int(manual_review.get("character_continuity_score", 0)),
        "gaze_motivation_score": int(manual_review.get("gaze_motivation_score", 0)),
        "education_clarity_score": int(manual_review.get("education_clarity_score", 0)),
        "storyboard_alignment_score": int(manual_review.get("storyboard_alignment_score", 0)),
        "blocking_issues": issues,
    }


def _inspection_review(project: Path, clip: Path, manual_review: dict | None) -> dict:
    if manual_review is None:
        return {"manifest": "", "frame_count": 0, "blocking_issues": ["inspection manifest required"]}
    raw_manifest = str(manual_review.get("inspection_manifest", ""))
    manifest_path = project / raw_manifest if raw_manifest else project / "video" / "inspection" / clip.stem / "manifest.json"
    if not manifest_path.exists():
        return {"manifest": str(manifest_path), "frame_count": 0, "blocking_issues": ["inspection manifest required"]}
    manifest = read_json(manifest_path)
    frame_count = int(manifest.get("frame_count", 0))
    issues = []
    if frame_count < 3:
        issues.append("inspection manifest must contain at least 3 frames")
    if bool(manifest.get("transcript_enabled", True)):
        issues.append("inspection transcript must be disabled")
    return {"manifest": str(manifest_path), "frame_count": frame_count, "blocking_issues": issues}


def _probe(path: Path) -> dict:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-show_entries",
            "stream=width,height,codec_name",
            "-of",
            "json",
            str(path),
        ],
        check=False,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        raise HarnessError(result.stderr.strip() or f"ffprobe failed for {path}")
    return json.loads(result.stdout)


def _record_video_evaluation_rounds(project: Path, reviews: list[dict]) -> None:
    for review in reviews:
        clip_path = Path(str(review["clip"]))
        item_id = clip_path.name
        iteration = completed_iterations(project, "video", item_id) + 1
        role_reviews = video_role_reviews(review)
        review["arbiter_decision"] = aggregate_arbiter_decision(
            project,
            "video",
            item_id,
            iteration,
            role_reviews,
        )
        bundle = {
            "stage": "video",
            "iteration": iteration,
            "evaluator_context_policy": "isolated_evaluator_with_evidence_bundle",
            "review": review,
            "required_evidence": [
                "video clip metadata",
                "local inspection manifest",
                "sampled frames or contact sheet",
                "manual visual review scores",
                "storyboard and approved keyframe references",
            ],
            "paid_regeneration_policy": "propose_only_user_approval_required",
        }
        bundle_path = write_evaluation_bundle(project, "video", item_id, iteration, bundle)
        record_evaluation_round(project, "video", item_id, iteration, review, bundle_path)

