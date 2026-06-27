from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from safety_video_harness.io import write_jsonl


def append_error(project: Path, stage: str, message: str) -> None:
    write_jsonl(
        project / ".harness" / "errors.jsonl",
        {
            "at": datetime.now(UTC).isoformat(),
            "stage": stage,
            "message": message,
        },
    )
