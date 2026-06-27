from __future__ import annotations

import sys

from hook_payload import hook_tokens


COMPLETION_TERMS = ["complete", "completed", "done", "finished", "완료", "끝"]
EVIDENCE_TERMS = ["evidence", "pytest", "dry-run", "검증", "증거"]


def main() -> int:
    payload = " ".join(hook_tokens(sys.argv[1:])).lower()
    claims_completion = any(term in payload for term in COMPLETION_TERMS)
    cites_evidence = any(term in payload for term in EVIDENCE_TERMS)
    if claims_completion and not cites_evidence:
        print("evidence-feedback: completion claims require command output or an evidence path")
        return 2
    print("evidence-feedback: evidence policy satisfied")
    return 0


if __name__ == "__main__":
    sys.exit(main())
