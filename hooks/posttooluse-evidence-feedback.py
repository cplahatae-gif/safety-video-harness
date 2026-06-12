"""PostToolUse hook (matcher: Bash).

After harness generate/validate/approve commands, reminds Claude that
completion claims require command output and an evidence path.
"""

from __future__ import annotations

import json
import sys

HARNESS_SCRIPTS = ("generate_", "validate_", "approve_", "inspect_video")


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    command = str(payload.get("tool_input", {}).get("command", ""))
    if "scripts/" not in command or not any(name in command for name in HARNESS_SCRIPTS):
        return 0
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PostToolUse",
                    "additionalContext": (
                        "evidence-feedback: completion claims require command output "
                        "and an evidence path under qa/, evidence/, or llm-wiki/."
                    ),
                }
            }
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
