from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from safety_video_harness.errors import HarnessError
from safety_video_harness.validation import validate_project


def _project_path(args: list[str]) -> Path | None:
    if "--project" not in args:
        return None
    index = args.index("--project") + 1
    if index >= len(args):
        return None
    return Path(args[index])


def main() -> int:
    project = _project_path(sys.argv[1:])
    if project is None:
        print("schema-validation: no --project supplied")
        return 0
    try:
        message = validate_project(project)
    except HarnessError as exc:
        print(str(exc))
        return 2
    print(f"schema-validation: {message}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
