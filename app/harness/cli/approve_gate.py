from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PACKAGE = ROOT / "app" / "harness" / "package"
sys.path.insert(0, str(PACKAGE))
sys.path.insert(0, str(ROOT))

from safety_video_harness.cli import run_boundary
from safety_video_harness.gates import approve_gate


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True)
    parser.add_argument("--gate", required=True)
    parser.add_argument("--estimated-credits", type=int)
    args = parser.parse_args()
    return run_boundary(
        lambda: approve_gate(Path(args.project), str(args.gate), args.estimated_credits)
    )


if __name__ == "__main__":
    sys.exit(main())
