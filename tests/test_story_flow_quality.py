from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "fixtures" / "sources" / "remicon-collision-guide.pptx"


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_test_png(path: Path) -> None:
    image = Image.new("RGB", (160, 90), "white")
    image.save(path)


def prepare_project(project: Path) -> None:
    assert run_cli("scripts/init_project.py", "--name", "레미콘 충돌 예방", "--slug", str(project)).returncode == 0
    assert run_cli("scripts/register_sources.py", "--project", str(project), "--source", str(FIXTURE)).returncode == 0
    assert run_cli("scripts/render_pptx_sources.py", "--project", str(project), "--dry-run", "--mode", "media_extract").returncode == 0
    assert run_cli("scripts/extract_topics.py", "--project", str(project)).returncode == 0
    assert run_cli("scripts/select_topic.py", "--project", str(project), "--topic-id", "topic-001").returncode == 0
    assert run_cli("scripts/extract_style_dna.py", "--project", str(project)).returncode == 0
    assert run_cli("scripts/plan_storyboard.py", "--project", str(project), "--duration", "30").returncode == 0


def test_image_prompts_include_story_flow_context(tmp_path: Path) -> None:
    project = tmp_path / "story-flow-prompts"
    prepare_project(project)

    result = run_cli("scripts/generate_images.py", "--project", str(project), "--dry-run")

    assert result.returncode == 0
    plans = load_json(project / "prompts" / "image_prompts.json")["plans"]
    first_prompt = plans[0]["prompt"]
    second_prompt = plans[1]["prompt"]
    assert "Story flow role:" in first_prompt
    assert "Next scene setup:" in first_prompt
    assert "Previous scene continuity:" in second_prompt
    assert "not a disconnected checklist panel" in first_prompt
    assert "official image generation guide" in first_prompt


def test_validate_images_writes_scored_loop_summary(tmp_path: Path) -> None:
    project = tmp_path / "scored-loop"
    prepare_project(project)
    assert run_cli("scripts/generate_images.py", "--project", str(project), "--dry-run").returncode == 0
    draft_dir = project / "images" / "draft"
    draft_dir.mkdir(parents=True, exist_ok=True)
    for index in range(1, 8):
        write_test_png(draft_dir / f"sc{index:02d}_v001.png")
    manual = {
        f"sc{index:02d}": {
            "floor_lane_consistency_score": 9,
            "background_consistency_score": 9,
            "character_identity_lock_score": 9,
            "vehicle_geometry_lock_score": 9,
            "hazard_zone_consistency_score": 9,
            "blocking_issues": [],
            "reviewer": "test",
        }
        for index in range(1, 9)
    }
    qa_dir = project / "qa"
    qa_dir.mkdir(parents=True, exist_ok=True)
    (qa_dir / "image_manual_reviews.json").write_text(json.dumps({"reviews": manual}), encoding="utf-8")

    result = run_cli("scripts/validate_images.py", "--project", str(project))

    assert result.returncode == 0
    loop = load_json(project / "qa" / "image_qa_loop.json")
    assert loop["passed"] is True
    assert loop["next_action"] == "approve_or_manual_review"
    assert loop["thresholds"]["minimum_total_score"] == 44
    review = load_json(project / "qa" / "image_reviews.json")["reviews"][0]
    assert review["total_score"] >= 44
    assert review["story_flow_score"] == 5
    assert "scoring_rubric" in review


def test_scene_link_validator_blocks_broken_sliding_chain(tmp_path: Path) -> None:
    project = tmp_path / "broken-chain"
    prepare_project(project)
    scenes_path = project / "storyboard" / "scenes.json"
    scenes = load_json(scenes_path)
    scenes["scenes"][1]["start_keyframe"] = "images/approved/not-sc02.png"
    scenes_path.write_text(json.dumps(scenes, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    result = run_cli("scripts/validate_scene_links.py", "--project", str(project))

    assert result.returncode != 0
    assert "sliding chain mismatch" in result.stderr
    report = load_json(project / "qa" / "scene_link_reviews.json")
    assert report["passed"] is False
    assert report["reviews"][1]["blocking_issues"]
