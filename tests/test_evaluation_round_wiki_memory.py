from __future__ import annotations

import json
from pathlib import Path

from safety_video_harness.evaluation_rounds import record_evaluation_round, write_evaluation_bundle


def test_llm_wiki_records_round_outputs_scores_and_next_prompt_memory(tmp_path: Path) -> None:
    project = tmp_path / "wiki-round-memory"
    bundle = write_evaluation_bundle(
        project,
        "image",
        "sc01",
        1,
        {
            "stage": "image",
            "iteration": 1,
            "scene": {
                "id": "sc01",
                "start_keyframe": "images/approved/sc01.png",
                "end_keyframe": "images/approved/sc02.png",
                "clip_path": "video/clips/sc01_sc02.mp4",
            },
            "review": {
                "reviewed_asset": "images/draft/sc01_v001.png",
            },
        },
    )
    review = {
        "decision": "regenerate",
        "story_match_score": 3,
        "identity_consistency_score": 5,
        "technical_score": 5,
        "total_score": 18,
        "reviewed_asset": "images/draft/sc01_v001.png",
        "blocking_issues": ["worker gaze is not motivated"],
        "regeneration_delta": ["make every worker look toward the visible truck route"],
        "arbiter_decision": {
            "decision": "revise",
            "regeneration_delta": ["tighten storyboard gaze cue before another image run"],
        },
    }

    record_evaluation_round(project, "image", "sc01", 1, review, bundle)

    wiki = (project / "llm-wiki" / "evaluation-rounds.md").read_text(encoding="utf-8")
    assert "## image / sc01 / round 1" in wiki
    assert "### Scores" in wiki
    assert "- story_match_score: `3`" in wiki
    assert "- identity_consistency_score: `5`" in wiki
    assert "### Round Outputs" in wiki
    assert "- reviewed_asset: `images/draft/sc01_v001.png`" in wiki
    assert "- start_keyframe: `images/approved/sc01.png`" in wiki
    assert "- end_keyframe: `images/approved/sc02.png`" in wiki
    assert "### Improvement Notes" in wiki
    assert "make every worker look toward the visible truck route" in wiki
    assert "tighten storyboard gaze cue before another image run" in wiki
    assert "### Next Prompt Memory" in wiki
    assert "Do not repeat: worker gaze is not motivated" in wiki

    ledger = (project / "qa" / "evaluation_rounds.jsonl").read_text(encoding="utf-8")
    record = json.loads(ledger.splitlines()[0])
    assert record["score_breakdown"]["story_match_score"] == 3
    assert "images/draft/sc01_v001.png" in record["artifact_paths"]
    assert "Do not repeat: worker gaze is not motivated" in record["next_prompt_memory"]


def test_llm_wiki_marks_repeated_blockers_for_upstream_learning(tmp_path: Path) -> None:
    project = tmp_path / "wiki-repeated-blocker"

    for iteration in range(1, 4):
        bundle = write_evaluation_bundle(project, "image", "sc01", iteration, {"stage": "image"})
        record_evaluation_round(
            project,
            "image",
            "sc01",
            iteration,
            {
                "decision": "regenerate",
                "total_score": 12,
                "blocking_issues": ["worker gaze is not motivated"],
            },
            bundle,
        )

    wiki = (project / "llm-wiki" / "evaluation-rounds.md").read_text(encoding="utf-8")
    assert "### Repeated Blockers" in wiki
    assert "worker gaze is not motivated" in wiki
    assert "3x" in wiki
