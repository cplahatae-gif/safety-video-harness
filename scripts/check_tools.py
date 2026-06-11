from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from safety_video_harness.cli import run_boundary
from safety_video_harness.tools import check_tools


def main() -> int:
    return run_boundary(check_tools)


if __name__ == "__main__":
    sys.exit(main())
