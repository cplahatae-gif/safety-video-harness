from __future__ import annotations

import os
import shutil
from dataclasses import dataclass
from pathlib import Path

from safety_video_harness.errors import HarnessError
from safety_video_harness.external_tools import run_tool
from safety_video_harness.io import write_json


DEFAULT_SKILLS_ROOT = Path.home() / ".codex" / "skills"


@dataclass(frozen=True, slots=True)
class InspectionResult:
    message: str
    manifest_path: Path


def inspect_video(
    project: Path,
    clip: Path,
    tool: str,
    no_transcript: bool,
    skills_root: Path | None = None,
) -> str:
    if not clip.exists():
        raise HarnessError(f"clip does not exist: {clip}")
    if not no_transcript:
        raise HarnessError("video inspection must use --no-transcript in this no-narration workflow")
    root = skills_root or DEFAULT_SKILLS_ROOT
    output = project / "video" / "inspection" / clip.stem
    output.mkdir(parents=True, exist_ok=True)
    match tool:
        case "scenelens":
            _run_scenelens(root, clip, output)
        case "video-frame-analysis":
            _run_video_frame_analysis(root, clip, output)
        case "understand-video":
            _run_understand_video(root, clip, output)
        case _:
            raise HarnessError("tool must be one of: scenelens, video-frame-analysis, understand-video")
    manifest = _write_manifest(project, clip, tool, output)
    return f"manifest written: {manifest}"


def _run_scenelens(skills_root: Path, clip: Path, output: Path) -> None:
    script = skills_root / "scenelens" / "scripts" / "scenelens.py"
    if not script.exists():
        raise HarnessError("scenelens skill is missing")
    _run(
        [
            "python3",
            str(script),
            str(clip),
            "--no-whisper",
            "--ocr-lang",
            "kor+eng",
            "--max-frames",
            "8",
            "--out-dir",
            str(output),
        ],
    )


def _run_video_frame_analysis(skills_root: Path, clip: Path, output: Path) -> None:
    script = skills_root / "video-frame-analysis" / "scripts" / "video-frame-analysis.sh"
    if not script.exists():
        raise HarnessError("video-frame-analysis skill is missing")
    env = os.environ.copy()
    env["OCR_LANG"] = "kor+eng"
    env["FRAME_INTERVAL_SECONDS"] = "2"
    env["FRAME_WIDTH"] = "420"
    _run(["bash", str(script), str(clip), str(output)], env)


def _run_understand_video(skills_root: Path, clip: Path, output: Path) -> None:
    script = skills_root / "understand-video" / "extract.sh"
    if not script.exists():
        raise HarnessError("understand-video skill is missing")
    _run(["bash", str(script), str(clip)])
    generated = clip.with_name(f"{clip.stem}-breakdown")
    if not generated.exists():
        raise HarnessError("understand-video did not create a breakdown folder")
    staged = output.with_name(f"{output.name}.new")
    if staged.exists():
        shutil.rmtree(staged)
    shutil.move(str(generated), str(staged))
    if output.exists():
        shutil.rmtree(output)
    shutil.move(str(staged), str(output))


def _write_manifest(project: Path, clip: Path, tool: str, output: Path) -> Path:
    frames = sorted([*output.glob("frame_*.jpg"), *output.glob("frames/*.jpg")])
    contact = output / "contact.png"
    manifest_path = output / "manifest.json"
    data = {
        "clip": str(clip.relative_to(project)) if clip.is_relative_to(project) else str(clip),
        "tool": tool,
        "transcript_enabled": False,
        "ocr_lang": "kor+eng",
        "frame_count": len(frames),
        "frame_paths": [str(path.relative_to(output)) for path in frames],
        "contact_sheet": str(contact.relative_to(output)) if contact.exists() else None,
        "inspection_questions": [
            "continuity",
            "gaze",
            "education_clarity",
            "storyboard_alignment",
        ],
    }
    write_json(manifest_path, data)
    write_json(project / "qa" / "video_inspection_manifest.json", {"manifests": [str(manifest_path.relative_to(project))]})
    return manifest_path


def _run(command: list[str], env: dict[str, str] | None = None) -> None:
    run_tool(command, 300, "video inspection failed", env=env, start_new_session=True)
