from __future__ import annotations

import sys
from collections.abc import Callable

from safety_video_harness.errors import HarnessError


def run_boundary(action: Callable[[], str]) -> int:
    try:
        message = action()
    except HarnessError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(message)
    return 0

