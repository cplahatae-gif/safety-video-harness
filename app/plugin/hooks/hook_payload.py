from __future__ import annotations

import json
import shlex
import sys

JsonValue = str | int | float | bool | None | list["JsonValue"] | dict[str, "JsonValue"]


def hook_tokens(args: list[str]) -> list[str]:
    tokens = list(args)
    raw = sys.stdin.read()
    if not raw.strip():
        return tokens
    try:
        payload: JsonValue = json.loads(raw)
    except json.JSONDecodeError:
        tokens.append(raw)
        return tokens
    tokens.extend(_tokens_from_json(payload))
    return tokens


def hook_command_tokens(args: list[str]) -> list[str]:
    raw = sys.stdin.read()
    if not raw.strip():
        return list(args)
    try:
        payload: JsonValue = json.loads(raw)
    except json.JSONDecodeError:
        return [*args, raw]
    if not isinstance(payload, dict):
        return _tokens_from_json(payload)
    tool_name = str(payload.get("tool_name", ""))
    tool_input = payload.get("tool_input", {})
    if "imagegen" in tool_name.lower() or "image_gen" in tool_name.lower():
        tokens = [tool_name]
        if isinstance(tool_input, dict):
            project = tool_input.get("project", tool_input.get("project_path", ""))
            if isinstance(project, str) and project.strip():
                tokens.extend(["--project", project])
        return tokens
    if not isinstance(tool_input, dict):
        return [tool_name]
    command = tool_input.get("command", tool_input.get("cmd", ""))
    if isinstance(command, str) and command.strip():
        return [tool_name, *_tokens_from_json(command)]
    return [tool_name]


def _tokens_from_json(value: JsonValue) -> list[str]:
    match value:
        case str():
            try:
                return shlex.split(value)
            except ValueError:
                return [value]
        case int() | float() | bool() | None:
            return []
        case list():
            return [token for item in value for token in _tokens_from_json(item)]
        case dict():
            return [
                token
                for pair in value.items()
                for item in pair
                for token in _tokens_from_json(item)
            ]
