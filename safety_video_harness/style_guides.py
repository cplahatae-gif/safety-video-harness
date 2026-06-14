from __future__ import annotations

from pathlib import Path
from typing import Final, TypedDict

from safety_video_harness.io import read_json


class StyleOption(TypedDict):
    style_guide_id: str
    label_ko: str
    description_ko: str
    recommended_for_ko: str


ROOT: Final = Path(__file__).resolve().parents[1]
STYLE_GUIDE_ROOT: Final = ROOT / "style-guides"
CATALOG_PATH: Final = STYLE_GUIDE_ROOT / "catalog.json"
DEFAULT_STYLE_GUIDE_ID: Final = "korean-industrial-webtoon"

FALLBACK_STYLE_OPTIONS: Final[list[StyleOption]] = [
    {
        "style_guide_id": "korean-industrial-webtoon",
        "label_ko": "한국 웹툰풍 안전교육",
        "description_ko": "현대 한국 웹툰풍 선화와 셀 셰이딩으로 산업안전 장면을 설명한다.",
        "recommended_for_ko": "교육 몰입감과 장면 이해도를 동시에 높이고 싶을 때",
    },
    {
        "style_guide_id": "clean-instructional-3d",
        "label_ko": "깔끔한 3D 교육 렌더",
        "description_ko": "밝고 정돈된 3D 렌더로 공간 관계와 장비 배치를 설명한다.",
        "recommended_for_ko": "동선, 사각지대, 장비 배치를 입체적으로 보여줄 때",
    },
    {
        "style_guide_id": "flat-vector-safety",
        "label_ko": "플랫 벡터 안전교육",
        "description_ko": "단순 도형과 높은 대비로 위험구역과 예방행동을 보여준다.",
        "recommended_for_ko": "절차 요약이나 사내 안내 카드에 가까운 톤이 필요할 때",
    },
    {
        "style_guide_id": "semi-realistic-industrial",
        "label_ko": "준실사 산업현장",
        "description_ko": "실제 현장감은 유지하되 교육용으로 노이즈를 줄인 스타일이다.",
        "recommended_for_ko": "현장 유사성이 중요한 교육에 사용할 때",
    },
    {
        "style_guide_id": "minimal-pictogram-training",
        "label_ko": "미니멀 픽토그램",
        "description_ko": "상징화된 인물과 장비로 핵심 행동만 전달한다.",
        "recommended_for_ko": "언어 의존도를 낮추고 금지/허용 행동만 보여줄 때",
    },
]


def style_options() -> list[StyleOption]:
    if not CATALOG_PATH.exists():
        return list(FALLBACK_STYLE_OPTIONS)
    catalog = read_json(CATALOG_PATH)
    options = catalog.get("options", [])
    if not isinstance(options, list):
        return list(FALLBACK_STYLE_OPTIONS)
    parsed: list[StyleOption] = []
    for option in options:
        if not isinstance(option, dict):
            continue
        parsed.append(
            {
                "style_guide_id": str(option.get("style_guide_id", "")),
                "label_ko": str(option.get("label_ko", "")),
                "description_ko": str(option.get("description_ko", "")),
                "recommended_for_ko": str(option.get("recommended_for_ko", "")),
            }
        )
    return parsed or list(FALLBACK_STYLE_OPTIONS)


def default_style_guide_id() -> str:
    if not CATALOG_PATH.exists():
        return DEFAULT_STYLE_GUIDE_ID
    catalog = read_json(CATALOG_PATH)
    return str(catalog.get("default_style_guide_id", DEFAULT_STYLE_GUIDE_ID))


def reference_intake_defaults() -> dict:
    return {
        "question_ko": "레퍼런스 이미지가 있으십니까?",
        "has_reference_images": None,
        "accepted_reference_roles": [
            "model/cast",
            "model/ppe",
            "product/equipment",
            "ref/approved/person",
            "ref/approved/work",
            "ref/approved/space",
            "ref/approved/style",
            "ref/approved/camera",
            "ref/approved/lighting",
        ],
        "note_ko": "레퍼런스가 있으면 먼저 역할별 폴더에 배치하고, 없으면 style-guides 카탈로그에서 스타일을 선택한다.",
    }


def style_interview_defaults(style_guide_id: str) -> dict:
    return {
        "question_ko": "어떤 스타일을 원하십니까?",
        "selected_style_guide_id": style_guide_id,
        "options": style_options(),
    }


def selected_style_guide_id(project: Path) -> str:
    config_path = project / "project_config.json"
    if not config_path.exists():
        return default_style_guide_id()
    config = read_json(config_path)
    return str(config.get("style_guide_id", default_style_guide_id()))


def selected_style_prompt_block(project: Path) -> str:
    style_guide_id = selected_style_guide_id(project)
    guide_path = STYLE_GUIDE_ROOT / style_guide_id / "STYLE_GUIDE.md"
    if not guide_path.exists():
        return "\n".join(
            [
                f"Selected style guide: {style_guide_id}",
                "Style guide file is missing; use the project continuity bible and approved references only.",
            ]
        )
    return "\n".join(
        [
            f"Selected style guide: {style_guide_id}",
            f"Style guide source: {guide_path.relative_to(ROOT)}",
            guide_path.read_text(encoding="utf-8"),
        ]
    )
