from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from safety_video_harness.cli import run_boundary
from safety_video_harness.project import apply_default_intake, apply_intake


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True)
    parser.add_argument("--defaults", action="store_true")
    parser.add_argument("--target-seconds", type=int)
    parser.add_argument("--image-density", choices=["normal", "high", "very_high"])
    parser.add_argument("--style-guide-id")
    parser.add_argument("--aspect-ratio")
    parser.add_argument("--resolution")
    parser.add_argument("--text-delivery")
    parser.add_argument("--approval-scope")
    parser.add_argument("--reference-notes")
    args = parser.parse_args()
    if args.defaults:
        return run_boundary(lambda: apply_default_intake(Path(args.project)))
    return run_boundary(
        lambda: apply_intake(
            Path(args.project),
            args.target_seconds,
            args.image_density,
            args.style_guide_id,
            args.aspect_ratio,
            args.resolution,
            args.text_delivery,
            args.approval_scope,
            args.reference_notes,
        )
    )


if __name__ == "__main__":
    sys.exit(main())
