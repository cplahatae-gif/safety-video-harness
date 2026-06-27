# Safety Video Harness

삼표 안전교육 영상 자동제작 하네스. Claude Code 기준 구성이다.

작업 규칙 전체는 아래 파일을 따른다.

@AGENTS.md

## Claude Code 구성 위치

- 스킬: `.claude/skills/<skill-id>/SKILL.md` (references 동봉)
- 서브에이전트: `.claude/agents/<agent-id>.md` (운영 레퍼런스는 `agents/<agent-id>/references/`)
- 훅: `hooks/*.py`, 등록은 `.claude/settings.json`
- 이미지 생성: `scripts/codex_image.sh` (Codex CLI 기본) / `scripts/gemini_image.sh` (Gemini Nano Banana fallback, 명시 요청 시만)

## 작업 전 필수 문서

- 도메인 용어집·비협상 정책·구조 오리엔테이션: `CONTEXT.md`
- 평가 기준: `docs/evaluation-rubrics.md`
- 산출물 예시: `docs/few-shot-examples.md`
- Higgsfield/Seedance 운영: `docs/higgsfield-seedance-local-reference.md`
