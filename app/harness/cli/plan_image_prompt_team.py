from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PACKAGE = ROOT / "app" / "harness" / "package"
sys.path.insert(0, str(PACKAGE))
sys.path.insert(0, str(ROOT))

from safety_video_harness.cli import run_boundary
from safety_video_harness.prompt_team import ensure_image_prompt_team_plan


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True)
    args = parser.parse_args()
    return run_boundary(lambda: _plan(Path(args.project)))


def _plan(project: Path) -> str:
    plan = ensure_image_prompt_team_plan(project)
    agents = dict(plan["agent_team"])
    scene_briefs = list(agents["scene_prompt_agents"])
    return f"prepared image prompt team plan for {len(scene_briefs)} scene brief(s)"


if __name__ == "__main__":
    sys.exit(main())
