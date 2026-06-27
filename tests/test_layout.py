from __future__ import annotations

import json
from pathlib import Path

from safety_video_harness.layout import (
    CANONICAL_PROJECT_DIRS,
    OLD_PROJECT_DIRS,
    LayoutKey,
    layout_for_project,
)


def test_layout_resolves_new_canonical_project_paths(tmp_path: Path) -> None:
    project = tmp_path / "layout-v2"
    project.mkdir()
    (project / "project_config.json").write_text(
        json.dumps({"project_layout_version": 2}, ensure_ascii=False),
        encoding="utf-8",
    )

    layout = layout_for_project(project)

    assert layout.version == 2
    assert layout.write_path(LayoutKey.SOURCE_RAW) == project / "input" / "sources" / "raw"
    assert layout.write_path(LayoutKey.STORY_SCENES) == project / "story" / "scenes.json"
    assert layout.write_path(LayoutKey.MEDIA_IMAGE_DRAFT) == project / "media" / "images" / "draft"
    assert layout.write_path(LayoutKey.QA_STATE) == project / "qa" / "state"
    assert "input/sources/raw" in CANONICAL_PROJECT_DIRS
    assert "media/images/approved" in CANONICAL_PROJECT_DIRS


def test_layout_detects_old_project_when_version_missing(tmp_path: Path) -> None:
    project = tmp_path / "layout-v1"
    project.mkdir()
    (project / "project_config.json").write_text("{}", encoding="utf-8")

    layout = layout_for_project(project)

    assert layout.version == 1
    assert layout.write_path(LayoutKey.STORY_SCENES) == project / "story" / "scenes.json"


def test_layout_read_path_prefers_existing_old_alias_for_legacy_project(tmp_path: Path) -> None:
    project = tmp_path / "legacy"
    old_scenes = project / "storyboard" / "scenes.json"
    old_scenes.parent.mkdir(parents=True)
    old_scenes.write_text('{"scenes": []}', encoding="utf-8")

    layout = layout_for_project(project)

    assert layout.version == 1
    assert layout.read_path(LayoutKey.STORY_SCENES) == old_scenes
    assert layout.read_path(LayoutKey.MEDIA_IMAGE_APPROVED) == project / "media" / "images" / "approved"


def test_layout_old_aliases_cover_existing_project_dirs() -> None:
    expected_old_dirs = [
        "sources/raw",
        "sources/rendered",
        "model/cast",
        "model/ppe",
        "product/equipment",
        "ref/candidates",
        "ref/approved",
        "ref/approved/person",
        "ref/approved/work",
        "ref/approved/space",
        "ref/approved/style",
        "ref/approved/camera",
        "ref/approved/lighting",
        "style",
        "asset-lock",
        "storyboard/versions",
        "prompts",
        "images/draft",
        "images/approved",
        "images/rejected",
        "video/clips",
        "video/sampled_frames",
        "video/inspection",
        "audio",
        "subtitles",
        "output",
        "qa",
        "evidence",
        ".harness",
    ]
    missing = [relative_path for relative_path in expected_old_dirs if relative_path not in OLD_PROJECT_DIRS]

    assert missing == []
