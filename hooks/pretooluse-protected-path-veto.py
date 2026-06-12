from __future__ import annotations

import json
import sys
from pathlib import Path


CONFIG = Path(__file__).with_name("protected_paths.json")


def protected_paths() -> list[str]:
    payload = json.loads(CONFIG.read_text(encoding="utf-8"))
    return [str(path).lower().strip("/") for path in payload.get("protected_after_bootstrap", [])]


def token_matches_protected_path(token: str, protected: str) -> bool:
    normalized = token.replace("\\", "/").lower().strip("/")
    if not normalized:
        return False
    if normalized == protected or normalized.endswith(f"/{protected}"):
        return True
    return f"/{protected}/" in f"/{normalized}/"


def main() -> int:
    protected = protected_paths()
    tokens = sys.argv[1:]
    if any(token_matches_protected_path(token, path) for token in tokens for path in protected):
        print("deny: protected path requires bootstrap mode or approval")
        return 2
    print("allow")
    return 0


if __name__ == "__main__":
    sys.exit(main())
