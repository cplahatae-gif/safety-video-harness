"""Stop hook.

Loop-run guard: when a harness loop has been initialized (.harness/ exists),
block stopping until .harness/DONE is written. Interactive sessions without a
.harness directory are unaffected. Respects stop_hook_active to avoid loops.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        payload = {}
    if payload.get("stop_hook_active"):
        return 0
    harness_dir = ROOT / ".harness"
    if not harness_dir.exists():
        return 0
    if (harness_dir / "DONE").exists():
        return 0
    print("block stop: .harness/DONE is missing — finish the loop or write the sentinel", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
