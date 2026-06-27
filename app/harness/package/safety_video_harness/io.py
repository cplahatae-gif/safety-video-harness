from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import TypeAlias

from safety_video_harness.errors import HarnessError
from safety_video_harness.locks import file_lock

JsonValue: TypeAlias = dict[str, "JsonValue"] | list["JsonValue"] | str | int | float | bool | None
JsonObject: TypeAlias = dict[str, JsonValue]


def read_json(path: Path) -> JsonObject:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise HarnessError(f"unreadable JSON state file: {path}: file not found") from exc
    except json.JSONDecodeError as exc:
        raise HarnessError(f"unreadable JSON state file: {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise HarnessError(f"unreadable JSON state file: {path}: expected object")
    return value


def write_json(path: Path, data: JsonObject) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with file_lock(path):
        tmp_path = path.with_name(f".{path.name}.tmp")
        tmp_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        os.replace(tmp_path, path)


def write_jsonl(path: Path, data: JsonObject) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with file_lock(path):
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(data, ensure_ascii=False) + "\n")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def ensure_dirs(root: Path, relative_paths: list[str]) -> None:
    for relative_path in relative_paths:
        (root / relative_path).mkdir(parents=True, exist_ok=True)
