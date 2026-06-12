"""PreToolUse hook (matcher: Write|Edit|MultiEdit).

Denies writing secret-looking values (assigned keys/tokens, Bearer tokens)
into project files. Environment-variable references like $GEMINI_API_KEY are
allowed; only literal secret values are blocked.
"""

from __future__ import annotations

import json
import re
import sys

SECRET_RE = re.compile(
    r"(?:API_KEY|SECRET|TOKEN|PASSWORD)\s*[=:]\s*['\"]?[A-Za-z0-9_\-]{16,}"
    r"|Bearer\s+[A-Za-z0-9_\-.]{16,}"
)


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    tool_input = payload.get("tool_input", {})
    content = " ".join(
        str(tool_input.get(key, ""))
        for key in ("content", "new_string", "command")
    )
    if SECRET_RE.search(content):
        print("deny: secret-like literal value must not be written; keep keys in Bitwarden", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
