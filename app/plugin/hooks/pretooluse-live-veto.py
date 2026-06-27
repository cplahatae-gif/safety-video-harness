from __future__ import annotations

import json
import sys
from pathlib import Path

from hook_payload import hook_command_tokens


def _project_path(args: list[str]) -> Path | None:
    if "--project" not in args:
        return None
    index = args.index("--project") + 1
    if index >= len(args):
        return None
    return Path(args[index])


def _approved(project: Path, gate: str) -> bool:
    approvals_path = project / "qa" / "approvals.json"
    if not approvals_path.exists():
        approvals_path = project / "approvals.json"
    if not approvals_path.exists():
        return False
    try:
        approvals = json.loads(approvals_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    gates = approvals.get("gates", {})
    if not isinstance(gates, dict):
        return False
    record = gates.get(gate, {})
    return isinstance(record, dict) and bool(record.get("approved", False))


def _upload_allowed(project: Path) -> bool:
    config_path = project / "project_config.json"
    if not config_path.exists():
        return False
    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    return bool(config.get("external_upload_allowed", False))


def _required_gate(args: list[str]) -> str:
    command = " ".join(args)
    if _is_video_or_external_command(command):
        return "image_to_video"
    return "storyboard"


def _is_live_or_paid_command(args: list[str]) -> bool:
    if "--live" in args:
        return True
    command_words = _command_words(args)
    if not command_words:
        return False
    first = Path(command_words[0]).name.lower()
    if "imagegen" in first or "image_gen" in first:
        return True
    if first == "higgsfield" and len(command_words) > 1 and command_words[1].lower() in {"upload", "generate"}:
        return True
    script_names = {Path(word).name.lower() for word in command_words}
    return bool(
        script_names
        & {
            "generate_seedance.py",
            "seedance_2_0",
            "tts.py",
            "generate_tts.py",
        }
    ) or _is_openai_speech_command(command_words)


def _is_video_or_external_command(command: str) -> bool:
    normalized = command.lower()
    video_terms = ["generate_seedance.py", "higgsfield", "seedance_2_0"]
    return any(term in normalized for term in video_terms)


def _is_tts_command(command: str) -> bool:
    normalized = command.lower()
    tts_terms = ["tts.py", " tts ", "text-to-speech", "audio.speech"]
    return any(term in normalized for term in tts_terms)


def _command_words(args: list[str]) -> list[str]:
    if args and args[0] in {"Bash", "exec_command", "functions.exec_command"}:
        return args[1:]
    return args


def _is_openai_speech_command(words: list[str]) -> bool:
    lowered = [word.lower() for word in words]
    return "openai" in lowered and "audio" in lowered and "speech" in lowered


def _has_pending_direct_imagegen_job(root: Path) -> bool:
    matches: list[Path] = []
    for pattern in ("story/imagegen_jobs.json", "prompts/imagegen_jobs.json"):
        for jobs_path in root.rglob(pattern):
            if any(part in {".git", ".venv", "__pycache__"} for part in jobs_path.parts):
                continue
            project = jobs_path.parent.parent
            if _approved(project, "storyboard") and _has_pending_job(jobs_path):
                matches.append(jobs_path)
                if len(matches) > 1:
                    return False
    return len(matches) == 1


def _has_pending_job(jobs_path: Path) -> bool:
    try:
        payload = json.loads(jobs_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    jobs = payload.get("jobs", [])
    return isinstance(jobs, list) and any(
        isinstance(job, dict) and job.get("status") == "pending_imagegen"
        for job in jobs
    )


def main() -> int:
    args = hook_command_tokens(sys.argv[1:])
    if not _is_live_or_paid_command(args):
        print("allow")
        return 0
    command = " ".join(args)
    if _is_tts_command(f" {command} "):
        print("deny: live TTS is not in the approved workflow")
        return 2
    project = _project_path(args)
    if project is None:
        if args and ("imagegen" in args[0].lower() or "image_gen" in args[0].lower()):
            if _has_pending_direct_imagegen_job(Path.cwd()):
                print("allow")
                return 0
            print("deny: direct imagegen requires --project or exactly one pending approved imagegen job")
            return 2
        print("deny: live generation requires --project")
        return 2
    gate = _required_gate(args)
    if not _approved(project, gate):
        print(f"deny: live generation requires approved gate {gate}")
        return 2
    if _is_video_or_external_command(command) and not _upload_allowed(project):
        print("deny: live generation requires external_upload_allowed=true")
        return 2
    print("allow")
    return 0


if __name__ == "__main__":
    sys.exit(main())
