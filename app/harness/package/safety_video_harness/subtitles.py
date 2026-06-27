from __future__ import annotations

from pathlib import Path

from safety_video_harness.io import read_json
from safety_video_harness.layout import LayoutKey, layout_for_project


def plan_subtitles(project: Path, dry_run: bool) -> str:
    layout = layout_for_project(project)
    scenes = read_json(layout.read_path(LayoutKey.STORY_SCENES))
    entries = []
    cursor = 0
    for index, scene in enumerate(scenes.get("scenes", []), start=1):
        duration = int(scene.get("duration_sec", 5))
        text = str(scene.get("subtitle_ko", scene.get("caption_ko", "")))
        start = cursor
        end = cursor + duration
        entries.append(_srt_entry(index, start, end, text))
        cursor = end
    output = layout.write_path(LayoutKey.MEDIA_SUBTITLES) / "subtitles.srt"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(entries) + "\n", encoding="utf-8")
    mode = "dry-run" if dry_run else "planned"
    return f"{mode} subtitle plan written: {output}"


def _srt_entry(index: int, start: int, end: int, text: str) -> str:
    return "\n".join(
        [
            str(index),
            f"{_timestamp(start)} --> {_timestamp(end)}",
            text,
            "",
        ]
    )


def _timestamp(seconds: int) -> str:
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d},000"
