from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "fixtures" / "sources" / "remicon-collision-guide.pptx"


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


def test_remicon_fixture_generates_source_specific_topics_and_storyboard(tmp_path: Path) -> None:
    project = tmp_path / "remicon"

    assert FIXTURE.exists()
    assert run_cli("scripts/init_project.py", "--name", "레미콘 충돌 예방", "--slug", str(project)).returncode == 0
    assert run_cli("scripts/register_sources.py", "--project", str(project), "--source", str(FIXTURE)).returncode == 0
    assert run_cli("scripts/render_pptx_sources.py", "--project", str(project), "--dry-run").returncode == 0
    rendered_assets = sorted((project / "sources" / "rendered").glob("*.png"))
    assert len(rendered_assets) == 12
    assert run_cli("scripts/extract_topics.py", "--project", str(project)).returncode == 0

    topics = load_json(project / "sources" / "extracted_topics.json")["topics"]
    topic_blob = json.dumps(topics, ensure_ascii=False)
    assert "레미콘" in topic_blob
    assert "충돌" in topic_blob
    assert "사각지대" in topic_blob
    assert "신호수" in topic_blob

    assert run_cli("scripts/intake_project.py", "--project", str(project), "--defaults").returncode == 0
    assert run_cli("scripts/extract_style_dna.py", "--project", str(project)).returncode == 0
    assert run_cli("scripts/plan_storyboard.py", "--project", str(project), "--duration", "30").returncode == 0
    assert run_cli("scripts/validate_project.py", str(project)).returncode == 0

    scenes = load_json(project / "storyboard" / "scenes.json")["scenes"]
    storyboard_blob = json.dumps(scenes, ensure_ascii=False)
    assert "BCT" in storyboard_blob
    assert "덤프트럭" in storyboard_blob
    assert "신호수" in storyboard_blob
    assert "후진" in storyboard_blob
    assert "사각지대" in storyboard_blob


def test_remicon_fixture_generates_detailed_image_and_video_prompt_contracts(tmp_path: Path) -> None:
    project = tmp_path / "remicon-prompts"

    assert run_cli("scripts/init_project.py", "--name", "레미콘 충돌 예방", "--slug", str(project)).returncode == 0
    assert run_cli("scripts/register_sources.py", "--project", str(project), "--source", str(FIXTURE)).returncode == 0
    assert run_cli("scripts/render_pptx_sources.py", "--project", str(project), "--dry-run").returncode == 0
    assert run_cli("scripts/extract_topics.py", "--project", str(project)).returncode == 0
    assert run_cli("scripts/intake_project.py", "--project", str(project), "--defaults").returncode == 0
    assert run_cli("scripts/extract_style_dna.py", "--project", str(project)).returncode == 0
    assert run_cli("scripts/plan_storyboard.py", "--project", str(project), "--duration", "30").returncode == 0
    assert run_cli("scripts/approve_gate.py", "--project", str(project), "--gate", "storyboard").returncode == 0

    assert run_cli("scripts/generate_images.py", "--project", str(project), "--dry-run").returncode == 0
    assert run_cli("scripts/validate_images.py", "--project", str(project), "--dry-run").returncode == 0
    assert run_cli("scripts/generate_seedance.py", "--project", str(project), "--dry-run").returncode == 0

    image_plans = load_json(project / "prompts" / "image_prompts.json")["plans"]
    video_plans = load_json(project / "prompts" / "video_prompts.json")["plans"]
    image_blob = json.dumps(image_plans, ensure_ascii=False)
    video_blob = json.dumps(video_plans, ensure_ascii=False)

    assert "continuity_bible" in image_blob
    assert "fixed_character_lock" in image_blob
    assert "fixed_site_lock" in image_blob
    assert "negative_prompt" in image_blob
    assert "same worker-001" in image_blob
    assert "same BCT bulk cement trailer" in image_blob
    assert "35mm documentary training frame" in image_blob

    assert "sliding_chain_contract" in video_blob
    assert "start keyframe" in video_blob
    assert "end keyframe" in video_blob
    assert "do not redesign" in video_blob
    assert "preserve exact PPE colors" in video_blob


def test_reference_assets_are_loaded_into_prompt_contracts(tmp_path: Path) -> None:
    project = tmp_path / "remicon-reference-assets"

    assert run_cli("scripts/init_project.py", "--name", "레미콘 충돌 예방", "--slug", str(project)).returncode == 0
    assert run_cli("scripts/register_sources.py", "--project", str(project), "--source", str(FIXTURE)).returncode == 0
    assert run_cli("scripts/render_pptx_sources.py", "--project", str(project), "--dry-run").returncode == 0
    assert run_cli("scripts/extract_topics.py", "--project", str(project)).returncode == 0
    assert run_cli("scripts/intake_project.py", "--project", str(project), "--defaults").returncode == 0
    assert run_cli("scripts/extract_style_dna.py", "--project", str(project)).returncode == 0
    assert run_cli("scripts/plan_storyboard.py", "--project", str(project), "--duration", "30").returncode == 0
    assert run_cli("scripts/approve_gate.py", "--project", str(project), "--gate", "storyboard").returncode == 0

    cast_dir = project / "model" / "cast"
    equipment_dir = project / "product" / "equipment"
    approved_ref_dir = project / "ref" / "approved"
    (cast_dir / "worker-001-front.png").write_bytes(b"fake image")
    (cast_dir / "worker-001.profile.md").write_text(
        "worker-001: oval face, short black hair mostly hidden by helmet, orange vest, navy pants",
        encoding="utf-8",
    )
    (equipment_dir / "bct-trailer.png").write_bytes(b"fake image")
    (equipment_dir / "bct-trailer.md").write_text(
        "white BCT bulk cement trailer with cylindrical tank and three rear axles",
        encoding="utf-8",
    )
    (approved_ref_dir / "animation-style.png").write_bytes(b"fake image")
    (approved_ref_dir / "animation-style.md").write_text(
        "flat but realistic Korean safety animation, clean factory daylight",
        encoding="utf-8",
    )

    assert run_cli("scripts/generate_images.py", "--project", str(project), "--dry-run").returncode == 0
    assert run_cli("scripts/generate_seedance.py", "--project", str(project), "--dry-run").returncode == 0

    image_blob = json.dumps(load_json(project / "prompts" / "image_prompts.json"), ensure_ascii=False)
    video_blob = json.dumps(load_json(project / "prompts" / "video_prompts.json"), ensure_ascii=False)

    assert "reference_assets" in image_blob
    assert "worker-001-front.png" in image_blob
    assert "oval face, short black hair" in image_blob
    assert "bct-trailer.png" in image_blob
    assert "white BCT bulk cement trailer" in image_blob
    assert "animation-style.png" in image_blob
    assert "flat but realistic Korean safety animation" in image_blob
    assert "worker-001-front.png" in video_blob


def test_categorized_approved_references_are_loaded_into_prompt_contracts(tmp_path: Path) -> None:
    project = tmp_path / "remicon-categorized-references"

    assert run_cli("scripts/init_project.py", "--name", "레미콘 충돌 예방", "--slug", str(project)).returncode == 0
    assert run_cli("scripts/register_sources.py", "--project", str(project), "--source", str(FIXTURE)).returncode == 0
    assert run_cli("scripts/render_pptx_sources.py", "--project", str(project), "--dry-run").returncode == 0
    assert run_cli("scripts/extract_topics.py", "--project", str(project)).returncode == 0
    assert run_cli("scripts/intake_project.py", "--project", str(project), "--defaults").returncode == 0
    assert run_cli("scripts/extract_style_dna.py", "--project", str(project)).returncode == 0
    assert run_cli("scripts/plan_storyboard.py", "--project", str(project), "--duration", "30").returncode == 0
    assert run_cli("scripts/approve_gate.py", "--project", str(project), "--gate", "storyboard").returncode == 0

    person_dir = project / "ref" / "approved" / "person"
    work_dir = project / "ref" / "approved" / "work"
    space_dir = project / "ref" / "approved" / "space"
    person_dir.mkdir(parents=True, exist_ok=True)
    work_dir.mkdir(parents=True, exist_ok=True)
    space_dir.mkdir(parents=True, exist_ok=True)
    (person_dir / "signal-person-reference.png").write_bytes(b"fake image")
    (person_dir / "signal-person-reference.md").write_text(
        "person reference: signal person stance, baton hand, radio hand, calm gaze toward truck route",
        encoding="utf-8",
    )
    (work_dir / "blind-spot-workflow.png").write_bytes(b"fake image")
    (work_dir / "blind-spot-workflow.md").write_text(
        "work situation reference: pedestrian remains outside the red blind-spot zone while truck waits",
        encoding="utf-8",
    )
    (space_dir / "plant-entry-layout.png").write_bytes(b"fake image")
    (space_dir / "plant-entry-layout.md").write_text(
        "space reference: ready-mix plant entry lanes, green pedestrian path, red exclusion zone",
        encoding="utf-8",
    )

    assert run_cli("scripts/generate_images.py", "--project", str(project), "--dry-run").returncode == 0
    assert run_cli("scripts/generate_seedance.py", "--project", str(project), "--dry-run").returncode == 0

    image_blob = json.dumps(load_json(project / "prompts" / "image_prompts.json"), ensure_ascii=False)
    video_blob = json.dumps(load_json(project / "prompts" / "video_prompts.json"), ensure_ascii=False)

    assert "person_reference" in image_blob
    assert "signal person stance" in image_blob
    assert "work_situation_reference" in image_blob
    assert "pedestrian remains outside the red blind-spot zone" in image_blob
    assert "space_reference" in image_blob
    assert "ready-mix plant entry lanes" in image_blob
    assert "plant-entry-layout.png" in video_blob
