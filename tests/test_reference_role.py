from __future__ import annotations

from pathlib import Path

import pytest

from safety_video_harness.errors import HarnessError
from safety_video_harness.io import read_json
from safety_video_harness.reference_profile import approve_reference, approved_reference_dir


def _make_candidate(project: Path, name: str) -> None:
    candidate = project / "ref" / "candidates" / name
    candidate.parent.mkdir(parents=True, exist_ok=True)
    candidate.write_bytes(b"fake-image")


def test_approve_reference_defaults_to_root_for_backward_compat(tmp_path: Path) -> None:
    project = tmp_path / "project"
    _make_candidate(project, "cast01.png")

    approve_reference(project, "cast01.png")

    assert (project / "ref" / "approved" / "cast01.png").exists()
    entry = read_json(project / "ref" / "approved" / "reference_approvals.json")["approvals"][0]
    assert entry["target"] == "ref/approved/cast01.png"


def test_approve_reference_routes_to_role_subdir(tmp_path: Path) -> None:
    project = tmp_path / "project"
    _make_candidate(project, "worker.png")

    approve_reference(project, "worker.png", "person")

    assert (project / "ref" / "approved" / "person" / "worker.png").exists()
    entry = read_json(project / "ref" / "approved" / "reference_approvals.json")["approvals"][0]
    assert entry["target"] == "ref/approved/person/worker.png"


def test_approve_reference_rejects_unknown_role(tmp_path: Path) -> None:
    project = tmp_path / "project"
    _make_candidate(project, "x.png")

    with pytest.raises(HarnessError, match="role must be one of"):
        approve_reference(project, "x.png", "bogus")


def test_approved_reference_dir_maps_known_roles(tmp_path: Path) -> None:
    project = tmp_path / "project"
    assert approved_reference_dir(project, "root") == project / "ref" / "approved"
    assert approved_reference_dir(project, "style") == project / "ref" / "approved" / "style"
