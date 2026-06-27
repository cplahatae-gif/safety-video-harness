from __future__ import annotations

import re
import sys

from hook_payload import hook_tokens

SECRET_RE = re.compile(r"(?i)(api[_-]?key|secret|token|bearer\s+|sk-[A-Za-z0-9_-]+|eyJ[A-Za-z0-9_-]+\.)")


def main() -> int:
    payload = " ".join(hook_tokens(sys.argv[1:]))
    if SECRET_RE.search(payload):
        print("deny: secret-like content must not be written")
        return 2
    print("allow")
    return 0


if __name__ == "__main__":
    sys.exit(main())
