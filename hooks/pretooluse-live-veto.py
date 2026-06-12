"""PreToolUse hook (matcher: Bash).

Blocks --live generation commands unless the project gate is approved and
external upload is allowed. Reads the Claude Code hook JSON payload from stdin
and denies by exiting 2 with the reason on stderr.
"""

from __future__ import annotations

import json
import shlex
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


def _required_gate(command: str) -> str:
    if "generate_seedance.py" in command:
        return "image_to_video"
    return "storyboard"


def _deny(reason: str) -> int:
    print(f"deny: {reason}", file=sys.stderr)
    return 2


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    if payload.get("tool_name") != "Bash":
        return 0
    command = str(payload.get("tool_input", {}).get("command", ""))
    if "--live" not in command:
        return 0
    try:
        args = shlex.split(command)
    except ValueError:
        args = command.split()
    project = _project_path(args)
    if project is None:
        return _deny("live generation requires --project")
    gate = _required_gate(command)
    if not _approved(project, gate):
        return _deny(f"live generation requires approved gate {gate}")
    if not _upload_allowed(project):
        return _deny("live generation requires external_upload_allowed=true")
    return 0


if __name__ == "__main__":
    sys.exit(main())
