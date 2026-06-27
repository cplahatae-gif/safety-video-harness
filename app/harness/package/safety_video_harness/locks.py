from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from safety_video_harness.errors import HarnessError


def lock_path(path: Path) -> Path:
    return path.with_name(f"{path.name}.lock")


def assert_unlocked(path: Path) -> None:
    marker = lock_path(path)
    if marker.exists():
        raise HarnessError(f"single-writer lock is held: {marker}")


@contextmanager
def file_lock(path: Path) -> Iterator[None]:
    marker = lock_path(path)
    marker.parent.mkdir(parents=True, exist_ok=True)
    try:
        with marker.open("x", encoding="utf-8") as handle:
            handle.write("held by current process\n")
    except FileExistsError as exc:
        raise HarnessError(f"single-writer lock is held: {marker}") from exc
    try:
        yield
    finally:
        marker.unlink(missing_ok=True)
