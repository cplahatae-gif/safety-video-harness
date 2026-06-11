from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from safety_video_harness.assets import ASSET_DIRS, IMAGE_SUFFIXES
from safety_video_harness.errors import HarnessError
from safety_video_harness.io import read_json, write_json


def analyze_reference_assets(project: Path, dry_run: bool) -> str:
    assets = []
    for role, relative_dir in ASSET_DIRS.items():
        if role == "approved_reference":
            scan_dir = project / "ref" / "approved"
        else:
            scan_dir = project / relative_dir
        assets.extend(_profile_assets(project, role, scan_dir))
    write_json(
        project / "ref" / "approved" / "reference_assets.json",
        {"dry_run": dry_run, "assets": assets},
    )
    return f"profiled {len(assets)} reference asset(s)"


def approve_reference(project: Path, candidate: str) -> str:
    source = project / "ref" / "candidates" / candidate
    if not source.exists():
        raise HarnessError(f"candidate does not exist: {candidate}")
    target = project / "ref" / "approved" / source.name
    target.parent.mkdir(parents=True, exist_ok=True)
    source.replace(target)
    _move_sidecar(source, target)
    approvals_path = project / "ref" / "approved" / "reference_approvals.json"
    approvals = read_json(approvals_path) if approvals_path.exists() else {"approvals": []}
    entries = list(approvals.get("approvals", []))
    entries.append(
        {
            "source": f"ref/candidates/{candidate}",
            "target": f"ref/approved/{target.name}",
            "approved_at": datetime.now(UTC).isoformat(),
            "approved_by": "local-user",
        }
    )
    write_json(approvals_path, {"approvals": entries})
    return f"approved reference {candidate}"


def _profile_assets(project: Path, role: str, scan_dir: Path) -> list[dict[str, str | list[str]]]:
    if not scan_dir.exists():
        return []
    return [
        {
            "asset_id": path.stem,
            "role": role,
            "path": str(path.relative_to(project)),
            "description": _description_for(path),
            "locked_traits": _locked_traits(role),
            "usage": _usage_for(role),
        }
        for path in sorted(scan_dir.glob("*"))
        if path.suffix.lower() in IMAGE_SUFFIXES
    ]


def _description_for(path: Path) -> str:
    sidecar = path.with_suffix(".md")
    if sidecar.exists():
        return " ".join(sidecar.read_text(encoding="utf-8").split())
    profile = sorted(path.parent.glob(f"{path.stem.split('-front')[0]}*.profile.md"))
    if profile:
        return " ".join(profile[0].read_text(encoding="utf-8").split())
    return f"visual reference from {path.name}; manual description not provided"


def _locked_traits(role: str) -> list[str]:
    match role:
        case "cast":
            return ["face", "body proportion", "ppe colors", "workwear"]
        case "ppe":
            return ["color", "shape", "placement"]
        case "equipment":
            return ["vehicle shape", "scale", "color", "wheel count"]
        case "approved_reference":
            return ["style", "camera", "lighting", "texture"]
        case _:
            return ["visual identity"]


def _usage_for(role: str) -> str:
    match role:
        case "cast":
            return "identity_reference"
        case "ppe":
            return "ppe_reference"
        case "equipment":
            return "equipment_reference"
        case "approved_reference":
            return "style_reference"
        case _:
            return "visual_reference"


def _move_sidecar(source: Path, target: Path) -> None:
    sidecar = source.with_suffix(".md")
    if sidecar.exists():
        sidecar.replace(target.with_suffix(".md"))
