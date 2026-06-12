"""PreToolUse hook (matcher: Write|Edit|MultiEdit|Bash).

Asks for user approval before modifying bootstrap-protected paths listed in
hooks/protected_paths.json. Set SAFETY_HARNESS_BOOTSTRAP=1 to allow
intentional maintenance edits without prompting.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

PROTECTED_CONFIG = Path(__file__).resolve().parent / "protected_paths.json"

# 공백으로 구분된 셸 토큰만 변형 명령으로 간주한다 ("<id>" 같은 문자열 오탐 방지)
MUTATING_TOKENS = ("rm ", "mv ", "cp ", " > ", " >> ", "sed -i", "tee ", "truncate ")


def _protected_paths() -> list[str]:
    config = json.loads(PROTECTED_CONFIG.read_text(encoding="utf-8"))
    return list(config.get("protected_after_bootstrap", []))


def _ask(reason: str) -> int:
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "ask",
                    "permissionDecisionReason": reason,
                }
            }
        )
    )
    return 0


def main() -> int:
    if os.environ.get("SAFETY_HARNESS_BOOTSTRAP") == "1":
        return 0
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    tool_name = payload.get("tool_name", "")
    tool_input = payload.get("tool_input", {})
    if tool_name == "Bash":
        target = str(tool_input.get("command", ""))
        if not any(token in target for token in MUTATING_TOKENS):
            return 0
    else:
        target = str(tool_input.get("file_path", ""))
    for protected in _protected_paths():
        if protected in target:
            return _ask(
                f"protected path '{protected}' — bootstrap-protected file. "
                "Approve only for intentional maintenance."
            )
    return 0


if __name__ == "__main__":
    sys.exit(main())
