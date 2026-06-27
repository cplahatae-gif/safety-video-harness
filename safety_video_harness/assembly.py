from __future__ import annotations

from pathlib import Path

from safety_video_harness.errors import HarnessError
from safety_video_harness.external_tools import run_tool
from safety_video_harness.io import write_json


def assemble_video(project: Path, dry_run: bool) -> str:
    clip_dir = project / "video" / "clips"
    clips = sorted(clip_dir.glob("*.mp4"))
    if not clips:
        raise HarnessError("no video clips found for assembly")
    output_dir = project / "video" / "final"
    output_dir.mkdir(parents=True, exist_ok=True)
    concat_list = output_dir / "concat.txt"
    concat_list.write_text("\n".join(_concat_line(path) for path in clips) + "\n", encoding="utf-8")
    output = output_dir / "final.mp4"
    command = [
        "ffmpeg",
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(concat_list),
        "-c",
        "copy",
        str(output),
    ]
    write_json(
        output_dir / "assembly_plan.json",
        {
            "clips": [str(path.relative_to(project)) for path in clips],
            "concat_list": str(concat_list.relative_to(project)),
            "output": str(output.relative_to(project)),
            "command": command,
            "dry_run": dry_run,
            "subtitle_overlay_policy": "planned separately; subtitles/subtitles.srt can be burned in a post-processing pass",
        },
    )
    if dry_run:
        return f"dry-run assembly plan written: {output_dir / 'assembly_plan.json'}"
    run_tool(command, 300, "ffmpeg assembly failed")
    return f"assembled final video: {output}"


def _concat_line(path: Path) -> str:
    escaped = str(path).replace("'", "'\\''")
    return f"file '{escaped}'"
