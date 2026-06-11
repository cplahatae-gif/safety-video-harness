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
    if marker.exists():
        raise HarnessError(f"single-writer lock is held: {marker}")
    marker.write_text("held by current process\n", encoding="utf-8")
    try:
        yield
    finally:
        marker.unlink(missing_ok=True)
