from __future__ import annotations

from safety_video_harness.asset_lock import (
    asset_lock_prompt_block,
    build_asset_lock_manifest,
    build_reference_media_pack,
    media_paths,
)


def _locked_refs() -> dict[str, list[dict[str, str]]]:
    return {
        "cast": [{"path": "ref/approved/person/cast.png", "description": "worker"}],
        "equipment": [{"path": "ref/approved/work/bct.png"}],
        "space_reference": [{"path": "ref/approved/space/plate.jpg"}],
    }


def test_manifest_is_draft_when_lock_roles_missing() -> None:
    manifest = build_asset_lock_manifest({})
    assert manifest["status"] == "draft_exploration_only"
    assert set(manifest["missing_roles"]) == {"cast", "equipment", "space_reference"}


def test_manifest_is_production_locked_when_required_roles_present() -> None:
    manifest = build_asset_lock_manifest(_locked_refs())
    assert manifest["status"] == "production_locked"
    assert manifest["missing_roles"] == []
    assert manifest["reference_media_pack"][0]["role"] == "cast"


def test_reference_media_pack_skips_non_image_assets() -> None:
    pack = build_reference_media_pack({"cast": [{"path": "a.png"}, {"path": "notes.md"}]})
    assert [media["path"] for media in pack] == ["a.png"]
    assert pack[0]["usage"] == "character_identity_or_soul_id_source"


def test_prompt_block_reports_status_and_policy() -> None:
    block = asset_lock_prompt_block(build_asset_lock_manifest(_locked_refs()))
    assert "Production consistency policy" in block
    assert "production_locked" in block


def test_media_paths_extracts_existing_paths() -> None:
    assert media_paths([{"path": "a.png"}, {"path": ""}, {"role": "x"}]) == ["a.png"]
