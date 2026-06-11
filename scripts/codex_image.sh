#!/usr/bin/env bash
# codex_image.sh — 스토리보드 이미지 1장 생성 (Codex image_gen / gpt-image-2, ChatGPT 구독 인증)
#
# 사용법:
#   scripts/codex_image.sh <출력경로.png> "<영문 이미지 프롬프트>" [참조이미지1.png] [참조이미지2.png] ...
#
# 예:
#   scripts/codex_image.sh storyboard/sc01.png "A reversing concrete truck..."
#   scripts/codex_image.sh storyboard/sc03.png "Same site, same worker..." storyboard/sc01.png storyboard/character.png
#
# 참조이미지를 여러 장 넘기면 현장·캐릭터·톤 일관성 유지에 사용된다(gpt-image-2 레퍼런스 다중 입력).
set -euo pipefail

OUT="${1:?출력 경로 필요}"
PROMPT="${2:?프롬프트 필요}"
shift 2 || true
REFS=("$@")   # 남은 인자 = 참조 이미지들

FULL_PROMPT="Use the built-in image generation tool to generate exactly one image and save it as '$OUT' (relative to the current working directory). Do not write any other files. ${PROMPT} After saving, print the absolute path of the saved image."

# -i(--image)는 가변 인자라 위치 인자 프롬프트를 삼킨다.
# 참조 이미지가 있을 때는 프롬프트를 stdin으로 전달한다.
if [ ${#REFS[@]} -gt 0 ]; then
  printf '%s' "$FULL_PROMPT" | codex exec --skip-git-repo-check -s workspace-write -i "${REFS[@]}"
else
  codex exec --skip-git-repo-check -s workspace-write "$FULL_PROMPT" < /dev/null
fi
