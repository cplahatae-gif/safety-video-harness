"""PostToolUse hook (matcher: Write|Edit|MultiEdit).

After a project state file changes, reminds Claude to re-run
scripts/validate_project.py via additionalContext.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

STATE_FILES = {"project_config.json", "approvals.json", "scenes.json", "sources.json"}


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    file_path = str(payload.get("tool_input", {}).get("file_path", ""))
    if Path(file_path).name not in STATE_FILES:
        return 0
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PostToolUse",
                    "additionalContext": (
                        f"schema-validation: {Path(file_path).name} changed. "
                        "Run scripts/validate_project.py <project> before continuing."
                    ),
                }
            }
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
