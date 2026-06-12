from __future__ import annotations

import subprocess
import shutil
from pathlib import Path


def check_tools(skills_root: Path | None = None) -> str:
    root = skills_root or Path.home() / ".claude" / "skills"
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
    result = subprocess.run(
        ["tesseract", "--list-langs"],
        check=False,
        text=True,
        capture_output=True,
    )
    languages = result.stdout.splitlines()
    status = "found" if language in languages else "missing"
    return f"ocr_lang_{language}: {status}"
