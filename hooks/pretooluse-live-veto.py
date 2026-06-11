from __future__ import annotations

import sys


def main() -> int:
    command = " ".join(sys.argv[1:])
    if "--live" in command:
        print("deny: live generation requires approved gate")
        return 2
    print("allow")
    return 0


if __name__ == "__main__":
    sys.exit(main())

