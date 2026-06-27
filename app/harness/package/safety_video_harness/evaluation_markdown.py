from __future__ import annotations

from safety_video_harness.io import JsonValue


def string_dict(value: JsonValue) -> dict[str, str]:
    if not isinstance(value, dict):
        return {}
    return {str(key): str(item) for key, item in value.items()}


def markdown_key_values(values: dict[str, str]) -> list[str]:
    if not values:
        return ["- 없음"]
    return [f"- {key}: `{value}`" for key, value in values.items()]


def markdown_artifacts(paths: dict[str, str]) -> list[str]:
    if not paths:
        return ["- 없음"]
    return [f"- {label}: `{path}`" for label, path in paths.items()]


def markdown_list(values: list[str]) -> list[str]:
    if not values:
        return ["- 없음"]
    return [f"- {value}" for value in values]


def markdown_repeated(values: dict[str, str]) -> list[str]:
    if not values:
        return ["- 없음"]
    return [f"- {signature}: `{count}x`" for signature, count in values.items()]
