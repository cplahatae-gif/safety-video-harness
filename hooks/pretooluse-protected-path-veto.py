from __future__ import annotations

import sys


def main() -> int:
    command = " ".join(sys.argv[1:])
    protected = ["AGENTS.md", "hooks/", "schemas/", "templates/"]
    if any(path in command for path in protected):
        print("deny: protected path requires bootstrap mode or approval")
        return 2
    print("allow")
    return 0


if __name__ == "__main__":
    sys.exit(main())

