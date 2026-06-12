from __future__ import annotations

import sys
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    sentinel = root / ".harness" / "DONE"
    if sentinel.exists():
        print("allow stop")
        return 0
    print("block stop: .harness/DONE is missing")
    return 2


if __name__ == "__main__":
    sys.exit(main())
