from __future__ import annotations

import re
import sys

SECRET_RE = re.compile(r"API_KEY|SECRET|TOKEN|Bearer ")


def main() -> int:
    payload = " ".join(sys.argv[1:])
    if SECRET_RE.search(payload):
        print("deny: secret-like content must not be written")
        return 2
    print("allow")
    return 0


if __name__ == "__main__":
    sys.exit(main())

