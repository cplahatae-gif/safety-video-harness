#!/usr/bin/env bash
# gemini_image.sh — Nano Banana(Gemini) fallback 이미지 1장 생성
#
# 사용자가 명시적으로 Gemini fallback을 요청한 경우에만 사용한다. 기본 경로는 codex_image.sh.
#
# 사용법:
#   scripts/gemini_image.sh <출력경로.png> "<영문 이미지 프롬프트>" [참조이미지1.png] [참조이미지2.png] ...
#
# 사전 준비:
#   load-keys   # Bitwarden에서 GEMINI_API_KEY 주입 (유료 키는 GEMINI_API_KEY_PAID)
#
# 모델 변경: GEMINI_IMAGE_MODEL 환경변수 (기본 gemini-2.5-flash-image)
set -euo pipefail

OUT="${1:?출력 경로 필요}"
PROMPT="${2:?프롬프트 필요}"
shift 2 || true

: "${GEMINI_API_KEY:?GEMINI_API_KEY가 비어 있습니다. load-keys를 먼저 실행하세요}"

python3 - "$OUT" "$PROMPT" "$@" <<'PY'
import base64
import json
import mimetypes
import os
import sys
import urllib.request

out, prompt, *refs = sys.argv[1:]
parts = [{"text": prompt}]
for ref in refs:
    mime = mimetypes.guess_type(ref)[0] or "image/png"
    with open(ref, "rb") as handle:
        data = base64.b64encode(handle.read()).decode()
    parts.append({"inline_data": {"mime_type": mime, "data": data}})

model = os.environ.get("GEMINI_IMAGE_MODEL", "gemini-2.5-flash-image")
request = urllib.request.Request(
    f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
    data=json.dumps({"contents": [{"parts": parts}]}).encode(),
    headers={
        "Content-Type": "application/json",
        "x-goog-api-key": os.environ["GEMINI_API_KEY"],
    },
)
with urllib.request.urlopen(request, timeout=300) as response:
    payload = json.load(response)

for part in payload["candidates"][0]["content"]["parts"]:
    inline = part.get("inlineData") or part.get("inline_data")
    if inline:
        os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
        with open(out, "wb") as handle:
            handle.write(base64.b64decode(inline["data"]))
        print(os.path.abspath(out))
        break
else:
    raise SystemExit(f"no image in response: {json.dumps(payload, ensure_ascii=False)[:500]}")
PY
