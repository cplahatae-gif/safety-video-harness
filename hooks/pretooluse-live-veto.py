from __future__ import annotations

import json
import sys
from pathlib import Path


def _project_path(args: list[str]) -> Path | None:
    if "--project" not in args:
        return None
    index = args.index("--project") + 1
    if index >= len(args):
        return None
    return Path(args[index])


def _approved(project: Path, gate: str) -> bool:
    approvals_path = project / "approvals.json"
    if not approvals_path.exists():
        return False
    approvals = json.loads(approvals_path.read_text(encoding="utf-8"))
    gates = approvals.get("gates", {})
    if not isinstance(gates, dict):
        return False
    record = gates.get(gate, {})
    return isinstance(record, dict) and bool(record.get("approved", False))


def _upload_allowed(project: Path) -> bool:
    config_path = project / "project_config.json"
    if not config_path.exists():
        return False
    config = json.loads(config_path.read_text(encoding="utf-8"))
    return bool(config.get("external_upload_allowed", False))


def _required_gate(args: list[str]) -> str:
    command = " ".join(args)
    if "generate_seedance.py" in command:
        return "image_to_video"
    return "storyboard"


def main() -> int:
    args = sys.argv[1:]
    if "--live" not in args:
        print("allow")
        return 0
    project = _project_path(args)
    if project is None:
        print("deny: live generation requires --project")
        return 2
    gate = _required_gate(args)
    if not _approved(project, gate):
        print(f"deny: live generation requires approved gate {gate}")
        return 2
    if not _upload_allowed(project):
        print("deny: live generation requires external_upload_allowed=true")
        return 2
    print("allow")
    return 0


if __name__ == "__main__":
    sys.exit(main())
