from __future__ import annotations

import json
import subprocess

from safety_video_harness.errors import HarnessError
from safety_video_harness.io import JsonObject


def run_tool(
    command: list[str],
    timeout_seconds: int,
    failure_message: str,
    env: dict[str, str] | None = None,
    start_new_session: bool = False,
) -> subprocess.CompletedProcess[str]:
    try:
        result = subprocess.run(
            command,
            check=False,
            text=True,
            capture_output=True,
            env=env,
            timeout=timeout_seconds,
            start_new_session=start_new_session,
        )
    except subprocess.TimeoutExpired as exc:
        raise HarnessError(f"{failure_message} timed out") from exc
    if result.returncode != 0:
        raise HarnessError(result.stderr.strip() or result.stdout.strip() or failure_message)
    return result


def run_tool_json(command: list[str], timeout_seconds: int, failure_message: str) -> JsonObject:
    result = run_tool(command, timeout_seconds, failure_message)
    try:
        value = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise HarnessError(f"{failure_message} returned invalid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise HarnessError(f"{failure_message} returned invalid JSON object")
    return value
