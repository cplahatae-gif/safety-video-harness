from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from safety_video_harness.errors import HarnessError
from safety_video_harness.io import read_json, write_json


def estimate_video_cost(project: Path, estimated_credits: int) -> str:
    if estimated_credits < 0:
        raise HarnessError("estimated credits must be zero or greater")
    scenes_path = project / "storyboard" / "scenes.json"
    if not scenes_path.exists():
        raise HarnessError("video cost estimate requires storyboard/scenes.json")
    scenes = read_json(scenes_path)
    clip_count = int(scenes.get("clip_count", 0))
    if clip_count <= 0:
        raise HarnessError("video cost estimate requires clip count greater than 0")
    payload = {
        "estimated_credits": estimated_credits,
        "clip_count": clip_count,
        "seconds_per_clip": int(scenes.get("seconds_per_clip", 0)),
        "total_seconds": int(scenes.get("target_seconds", 0)),
        "regeneration_risk": "medium",
        "pricing_source": "manual_estimate",
        "estimated_at": datetime.now(UTC).isoformat(),
    }
    write_json(project / "qa" / "video_cost_estimate.json", payload)
    return f"estimated video cost {estimated_credits} credit(s)"
