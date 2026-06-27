from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from safety_video_harness.errors import HarnessError
from safety_video_harness.io import read_json, write_json
from safety_video_harness.layout import LayoutKey, layout_for_project
from safety_video_harness.reference_catalog import approved_reference_dir, catalog_for_manifest


def analyze_reference_assets(project: Path, dry_run: bool) -> str:
    layout = layout_for_project(project)
    assets = catalog_for_manifest(project)
    write_json(
        layout.read_path(LayoutKey.REFS_APPROVED) / "reference_assets.json",
        {"dry_run": dry_run, "assets": assets},
    )
    return f"profiled {len(assets)} reference asset(s)"


def approve_reference(project: Path, candidate: str, role: str = "root") -> str:
    layout = layout_for_project(project)
    source = layout.read_path(LayoutKey.REFS_CANDIDATES) / candidate
    if not source.exists():
        raise HarnessError(f"candidate does not exist: {candidate}")
    try:
        target_dir = approved_reference_dir(project, role)
    except ValueError as exc:
        raise HarnessError(str(exc)) from exc
    target = target_dir / source.name
    target.parent.mkdir(parents=True, exist_ok=True)
    source.replace(target)
    _move_sidecar(source, target)
    approvals_path = layout.read_path(LayoutKey.REFS_APPROVED) / "reference_approvals.json"
    approvals = read_json(approvals_path) if approvals_path.exists() else {"approvals": []}
    entries = list(approvals.get("approvals", []))
    entries.append(
        {
            "source": str(source.relative_to(project)),
            "target": str(target.relative_to(project)),
            "approved_at": datetime.now(UTC).isoformat(),
            "approved_by": "local-user",
            "role": role,
        }
    )
    write_json(approvals_path, {"approvals": entries})
    return f"approved reference {candidate}"


def _move_sidecar(source: Path, target: Path) -> None:
    sidecar = source.with_suffix(".md")
    if sidecar.exists():
        sidecar.replace(target.with_suffix(".md"))
