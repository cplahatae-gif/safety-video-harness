from __future__ import annotations

import shutil
from pathlib import Path

from safety_video_harness.external_tools import run_tool


def check_tools(skills_root: Path | None = None) -> str:
    root = skills_root or Path.home() / ".codex" / "skills"
    required = ["python3", "ffmpeg", "ffprobe", "node", "npm", "tesseract"]
    statuses = [f"{tool}: {'found' if shutil.which(tool) else 'missing'}" for tool in required]
    optional = "higgsfield: found" if shutil.which("higgsfield") else "higgsfield: missing"
    statuses.append(optional)
    statuses.append(_ocr_language_status("kor"))
    statuses.append(_ocr_language_status("eng"))
    for skill in ["scenelens", "video-frame-analysis", "understand-video", "seedance-expert"]:
        status = "found" if (root / skill / "SKILL.md").exists() else "missing"
        statuses.append(f"{skill}: {status}")
    return "\n".join(statuses)


def _ocr_language_status(language: str) -> str:
    if shutil.which("tesseract") is None:
        return f"ocr_lang_{language}: missing"
    result = run_tool(["tesseract", "--list-langs"], 30, "tesseract language check")
    languages = result.stdout.splitlines()
    status = "found" if language in languages else "missing"
    return f"ocr_lang_{language}: {status}"
