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


def prepare_storyboard_project(project: Path) -> None:
    assert run_cli("scripts/init_project.py", "--name", "레미콘 웹툰 스타일", "--slug", str(project)).returncode == 0
    assert run_cli("scripts/register_sources.py", "--project", str(project), "--source", str(FIXTURE)).returncode == 0
    assert run_cli("scripts/render_pptx_sources.py", "--project", str(project), "--dry-run").returncode == 0
    assert run_cli("scripts/extract_topics.py", "--project", str(project)).returncode == 0
    assert run_cli("scripts/intake_project.py", "--project", str(project), "--defaults").returncode == 0
    assert run_cli("scripts/extract_style_dna.py", "--project", str(project)).returncode == 0
    assert run_cli("scripts/plan_storyboard.py", "--project", str(project), "--duration", "30").returncode == 0


def test_reusable_style_guide_catalog_and_reference_assets_exist() -> None:
    catalog = load_json(ROOT / "style-guides" / "catalog.json")

    assert catalog["default_style_guide_id"] == "korean-industrial-webtoon"
    assert len(catalog["options"]) == 5
    assert (ROOT / "style-guides" / "README.md").exists()
    assert (ROOT / "style-guides" / "korean-industrial-webtoon" / "STYLE_GUIDE.md").exists()
    assert (ROOT / "style-guides" / "korean-industrial-webtoon" / "references" / "reference-001.png").exists()
    assert (ROOT / "style-guides" / "korean-industrial-webtoon" / "references" / "reference-001.md").exists()


def test_project_config_records_reference_and_style_interview_defaults(tmp_path: Path) -> None:
    project = tmp_path / "style-interview"

    assert run_cli("scripts/init_project.py", "--name", "스타일 인터뷰", "--slug", str(project)).returncode == 0
    config = load_json(project / "project_config.json")

    assert config["style_guide_id"] == "korean-industrial-webtoon"
    assert config["reference_intake"]["question_ko"] == "레퍼런스 이미지가 있으십니까?"
    assert config["style_interview"]["question_ko"] == "어떤 스타일을 원하십니까?"
    assert config["style_interview"]["selected_style_guide_id"] == "korean-industrial-webtoon"
    assert len(config["style_interview"]["options"]) == 5
    assert (project / "ref" / "approved" / "person").exists()
    assert (project / "ref" / "approved" / "style").exists()


def test_selected_style_guide_is_injected_into_image_prompts(tmp_path: Path) -> None:
    project = tmp_path / "style-prompt"
    prepare_storyboard_project(project)

    result = run_cli("scripts/generate_images.py", "--project", str(project), "--dry-run", "--only", "sc01")

    assert result.returncode == 0
    prompt = load_json(project / "prompts" / "image_prompts.json")["plans"][0]["prompt"]
    assert "Selected style guide: korean-industrial-webtoon" in prompt
    assert "modern Korean webtoon safety-training style" in prompt
    assert "crisp clean line art" in prompt
    assert "Approved style guide and reference assets to preserve:" in prompt
