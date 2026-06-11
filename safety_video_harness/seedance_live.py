from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

from safety_video_harness.errors import HarnessError
from safety_video_harness.io import read_json, write_json, write_jsonl


MAX_TEST_SECONDS = 10
MAX_ATTEMPTS = 3
SECONDS_PER_CLIP = 5


@dataclass(frozen=True, slots=True)
class SeedanceLiveOptions:
    test_seconds: int
    max_attempts: int
    plan_only: bool
    validation_run: bool = False


def build_seedance_live_plan(project: Path, options: SeedanceLiveOptions) -> dict:
    _validate_options(options)
    prompts_path = project / "prompts" / "video_prompts.json"
    if not prompts_path.exists():
        raise HarnessError("live Seedance requires prompts/video_prompts.json")
    prompts = list(read_json(prompts_path).get("plans", []))
    clip_count = 1 if options.validation_run else options.test_seconds // SECONDS_PER_CLIP
    selected = prompts[:clip_count]
    if len(selected) < clip_count:
        raise HarnessError(f"not enough video prompt plans for {options.test_seconds}s test")
    job_duration = options.test_seconds if options.validation_run else SECONDS_PER_CLIP
    jobs = [_build_job(project, plan, job_duration) for plan in selected]
    payload = {
        "model": "seedance_2_0",
        "test_seconds": options.test_seconds,
        "max_attempts": options.max_attempts,
        "plan_only": options.plan_only,
        "paid_run_policy": {
            "validation_run": options.validation_run,
            "allowed_live_invocations": 1 if options.validation_run else MAX_ATTEMPTS,
            "requires_gate": "image_to_video",
        },
        "jobs": jobs,
    }
    write_json(project / "video" / "seedance_live_plan.json", payload)
    return payload


def run_seedance_live_plan(project: Path, plan: dict) -> str:
    runs = []
    for job in plan["jobs"]:
        cost = _run_cli(job["cost_command"])
        created = _run_cli(job["create_command"])
        runs.append(
            {
                "scene_id": job["scene_id"],
                "cost_stdout": cost.stdout.strip(),
                "create_stdout": created.stdout.strip(),
            }
        )
    for run in runs:
        write_jsonl(project / "video" / "seedance_live_runs.jsonl", run)
    return f"created {len(runs)} Seedance live job(s)"


def _validate_options(options: SeedanceLiveOptions) -> None:
    if options.test_seconds > MAX_TEST_SECONDS:
        raise HarnessError("test-seconds must be <= 10")
    if options.test_seconds < SECONDS_PER_CLIP or options.test_seconds % SECONDS_PER_CLIP != 0:
        raise HarnessError("test-seconds must be 5 or 10")
    if options.max_attempts > MAX_ATTEMPTS:
        raise HarnessError("max-attempts must be <= 3")
    if options.max_attempts < 1:
        raise HarnessError("max-attempts must be >= 1")
    if options.validation_run and options.max_attempts != 1:
        raise HarnessError("validation-run requires max-attempts=1")
    if not options.validation_run and options.test_seconds // SECONDS_PER_CLIP > options.max_attempts:
        raise HarnessError("max-attempts must cover the requested test clips")


def _build_job(project: Path, plan: dict, duration: int) -> dict:
    prompt = str(plan["prompt"]).replace(
        "Generate a 5 second Seedance clip",
        f"Generate a {duration} second Seedance clip",
        1,
    )
    start_image = str(project / str(plan["start_keyframe"]))
    end_image = str(project / str(plan["end_keyframe"]))
    common = [
        "higgsfield",
        "generate",
        "create",
        "seedance_2_0",
        "--prompt",
        prompt,
        "--start-image",
        start_image,
        "--end-image",
        end_image,
        "--duration",
        str(duration),
        "--aspect_ratio",
        "16:9",
        "--resolution",
        "720p",
        "--mode",
        "fast",
        "--no-color",
    ]
    cost_command = common.copy()
    cost_command[2] = "cost"
    create_command = [*common, "--wait", "--wait-timeout", "20m", "--wait-interval", "10s"]
    return {
        "scene_id": plan["scene_id"],
        "duration": duration,
        "start_image": start_image,
        "end_image": end_image,
        "cost_command": cost_command,
        "create_command": create_command,
    }


def _run_cli(command: list[str]) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(command, check=False, text=True, capture_output=True)
    if result.returncode != 0:
        raise HarnessError(result.stderr.strip() or result.stdout.strip() or "higgsfield command failed")
    return result
