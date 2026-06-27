from __future__ import annotations

import sys

from hook_paths import repo_root


def main() -> int:
    root = repo_root()
    sentinel = root / ".harness" / "DONE"
    if sentinel.exists():
        print("allow stop")
        return 0
    print("block stop: .harness/DONE is missing")
    return 2


if __name__ == "__main__":
    sys.exit(main())
