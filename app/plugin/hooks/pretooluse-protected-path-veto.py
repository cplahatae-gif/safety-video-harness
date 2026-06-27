from __future__ import annotations

import json
import shlex
import sys
from pathlib import Path

from hook_payload import JsonValue, hook_tokens


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
    tokens, command_tokens = _payload_tokens(sys.argv[1:])
    if _is_read_only_shell(command_tokens):
        print("allow")
        return 0
    if any(token_matches_protected_path(token, path) for token in tokens for path in protected):
        print("deny: protected path requires bootstrap mode or approval")
        return 2
    print("allow")
    return 0


def _payload_tokens(args: list[str]) -> tuple[list[str], list[str]]:
    raw = sys.stdin.read()
    if not raw.strip():
        return list(args), list(args)
    try:
        payload: JsonValue = json.loads(raw)
    except json.JSONDecodeError:
        tokens = hook_tokens(args)
        return tokens, tokens
    tokens = [*args, *_tokens_from_json(payload)]
    if not isinstance(payload, dict):
        return tokens, tokens
    tool_name = str(payload.get("tool_name", ""))
    tool_input = payload.get("tool_input", {})
    if not isinstance(tool_input, dict):
        return tokens, [tool_name]
    command = tool_input.get("command", tool_input.get("cmd", ""))
    if isinstance(command, str) and command.strip():
        return tokens, [tool_name, *_split(command)]
    return tokens, [tool_name]


def _tokens_from_json(value: JsonValue) -> list[str]:
    match value:
        case str():
            return _split(value)
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


def _split(value: str) -> list[str]:
    try:
        return shlex.split(value)
    except ValueError:
        return [value]


def _is_read_only_shell(tokens: list[str]) -> bool:
    if not tokens:
        return False
    words = tokens[1:] if tokens[0] in {"Bash", "exec_command", "functions.exec_command"} else tokens
    if not words:
        return False
    first = Path(words[0]).name.lower()
    if first == "sed":
        return "-i" not in words
    if first == "find":
        return "-delete" not in words
    if first == "git":
        return len(words) > 1 and words[1] in {"status", "diff", "show", "log", "grep", "ls-files"}
    return first in {"rg", "grep", "cat", "ls", "nl", "wc", "head", "tail"}


if __name__ == "__main__":
    sys.exit(main())
