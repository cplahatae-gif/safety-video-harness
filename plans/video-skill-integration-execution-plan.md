# 영상 분석 스킬 통합 실행 계획

## TL;DR
> **Summary**: 설치된 `scenelens`, `video-frame-analysis`, `understand-video`, `seedance-expert`를 현재 안전영상 하네스에 통합해 영상 생성 전후 검증을 강화한다. 나레이션/TTS/전사는 이번 범위에서 제거하고, 전달 문구는 자막/오버레이/텍스트 카드 계약으로만 다룬다.
> **Deliverables**:
> - 영상 길이와 이미지 분량을 묻는 인테이크/설정 알고리즘
> - 영상 분석 스킬 실행 어댑터와 증거 manifest
> - Seedance 프롬프트 보강 및 10초 1회 유료 검증 가드레일
> - 나레이션/TTS 제거 및 자막/화면 텍스트 계약
> - 테스트, 실제 fixture dry-run, 1회 live 영상 QA evidence
> **Effort**: Large
> **Parallel**: YES - 5 waves
> **Critical Path**: Task 1 -> Task 2 -> Task 3 -> Task 5 -> Task 8 -> Task 10 -> Final Verification

## Context

### Original Request
- 다운받은 영상 관련 스킬들을 현재 구현된 안전영상 하네스에 맞춰 통합한다.
- 수정 및 검증 계획을 `$omo:ulw-plan` 방식으로 작성한다.
- 영상 생성 유료 작업은 10초 정도로 1번만 짧게 진행한다.
- 나레이션 관련 작업은 이번 기능에서 제외하고 추후 과제로 둔다.
- 전달이 필요한 사항은 화면 텍스트 장면 또는 자막으로 표기한다.
- 인테이크에 `몇 초짜리 영상을 만드시겠습니까?`와 이미지 분량 선택을 추가한다.

### Interview Summary
- 영상 목표는 “나레이션 없는 안전교육 영상”이다.
- 교육 내용 전달 방식은 음성 설명이 아니라 자막, 화면 오버레이, 또는 별도 텍스트 카드다.
- 이미지 분량 선택지는 `보통`, `많이`, `더 많이`이며 각각 현재 기준, 2배, 4배다.
- 영상 프레임/키프레임을 더 잘게 쪼개는 여부는 사용자가 인테이크에서 선택한다.

### Metis Review
반영한 gap:
- 현재 README/PRD/코드에 남아 있는 TTS, `narration_ko`, `audio_policy`가 새 범위와 충돌한다.
- `validate_video.py`는 수동 리뷰 JSON만 있으면 통과할 수 있어, 분석 스킬이 만든 프레임/OCR evidence manifest를 필수화해야 한다.
- 현재 live Seedance 기본값은 최대 3회 시도라, 이번 유료 검증은 `--max-attempts 1`로 별도 제한해야 한다.
- 이미지 프롬프트는 텍스트 생성을 금지해야 하므로, 교육 문구는 이미지 내부 생성이 아니라 후처리 자막/오버레이/텍스트 카드로 분리해야 한다.
- `understand-video`는 전사 기능이 있으므로 이번 범위에서는 frame/OCR 추출만 허용하고 transcript/audio 산출물은 기본 QA 계약에서 제외한다.

## Work Objectives

### Core Objective
현재 하네스가 영상 생성 전에는 더 촘촘한 이미지/스토리보드 계획을 만들고, 영상 생성 후에는 설치된 로컬 영상 분석 스킬로 프레임 증거를 만든 뒤 스토리보드/이미지/영상 일치 여부를 점수 기반으로 차단하도록 만든다.

### Deliverables
- `target_duration_sec`와 `image_density` 인테이크/설정 필드
- `normal=1`, `high=2`, `very_high=4` 이미지 밀도 알고리즘
- `scripts/inspect_video.py` 또는 동등 CLI
- `safety_video_harness/video_inspection.py` 신규 어댑터
- `qa/video_inspection_manifest.json` 스키마/검증
- `video/inspection/<clip-id>/` evidence bundle
- Seedance prompt 계약에 `seedance-expert` 기반 연속성/시선/교육명확성 규칙 반영
- 나레이션/TTS 제거 및 자막/오버레이 계약 문서화
- 10초 1회 live 검증 실행 절차와 evidence

### Definition of Done
- `uv run pytest -q` 통과
- `python3 scripts/check_tools.py`가 `tesseract`, `higgsfield`, 설치된 영상 스킬 경로 상태를 출력
- `python3 scripts/plan_storyboard.py --project projects/remicon-collision-guide --duration 30 --image-density high`가 정상 실행되고 anchor 수가 증가
- `python3 scripts/generate_seedance.py --project projects/remicon-collision-guide --live --execute-paid --test-seconds 10 --max-attempts 1 --plan-only` 통과
- `python3 scripts/inspect_video.py --project projects/remicon-collision-guide --clip projects/remicon-collision-guide/video/clips/<new-clip>.mp4 --tool scenelens --no-transcript`가 manifest 생성
- `python3 scripts/validate_video.py --project projects/remicon-collision-guide --expected-clips 1`가 영상 분석 evidence 없이는 실패하고, evidence와 수동 리뷰가 있으면 기준에 따라 통과 또는 blocker를 보고
- 실제 Higgsfield live 생성은 전체 작업 중 1회만 실행하고 evidence에 실행 로그 저장

### Must Have
- 나레이션/TTS/Whisper API/전사 기능은 기본 기능에서 제거
- 교육 문구는 `caption_ko`, `subtitle_ko`, `text_card_ko`, `overlay_text_ko` 계열로만 표현
- 이미지 생성 프롬프트는 계속 “텍스트 생성 금지” 유지
- 영상 분석은 로컬 프레임/OCR evidence를 반드시 남김
- 유료 live 영상 생성은 10초, `max_attempts=1`, 사용자 승인 gate 이후 1회만 허용

### Must NOT Have
- 이번 작업에서 TTS 어댑터 구현 금지
- Whisper/Groq/OpenAI 전사 API 호출 금지
- 기존 `plans/archive` 수정 금지
- 영상 QA가 메타데이터 또는 수동 점수만으로 통과하면 안 됨
- 텍스트를 이미지 모델에게 직접 그리게 시키면 안 됨

## Verification Strategy
> ZERO HUMAN INTERVENTION - all verification is agent-executed except the single explicit paid generation command, which must be gated and logged.
- Test decision: TDD with `pytest`; RED output and GREEN output must be saved under `evidence/`.
- QA policy: every task has CLI/tmux scenarios with exact commands.
- Evidence naming: `evidence/task-N-*.txt`, generated manifests under project `qa/` and `video/inspection/`.
- Paid QA: one live Seedance run only, exact command must include `--test-seconds 10 --max-attempts 1`.

## Execution Strategy

### Parallel Execution Waves
Wave 1: narration removal contract, intake/density schema, tool discovery
Wave 2: video skill adapters, inspection manifest, Seedance prompt enhancement
Wave 3: video QA enforcement, docs/agents/hooks alignment, fixture migration
Wave 4: full dry-run on `projects/remicon-collision-guide`, paid live plan-only preflight
Wave 5: one 10-second live run, inspect generated clip, final QA and review

### Dependency Matrix
- Task 1 blocks Tasks 2, 6, 7.
- Task 2 blocks Tasks 4, 8.
- Task 3 blocks Tasks 5, 8, 10.
- Task 4 blocks Tasks 6, 9.
- Task 5 blocks Tasks 8, 10.
- Task 6 blocks Task 9.
- Task 7 blocks Task 9.
- Task 8 blocks Task 10.
- Task 9 blocks Task 10.
- Task 10 blocks Final Verification.

## TODOs

- [x] 1. 나레이션/TTS 범위 제거 및 자막/오버레이 계약 정의

  **What to do**:
  - `safety_video_harness/storyboard.py`에서 신규 생성 scene에 `narration_ko`와 `narration_char_limit`를 만들지 않는다.
  - scene 텍스트 필드는 `caption_ko`, `subtitle_ko`, `overlay_text_ko`, `text_card_ko` 중 필요한 최소 필드로 정한다.
  - `safety_video_harness/validation.py`에서 narration 길이 검증을 제거하고, caption/subtitle 필드 존재와 길이 검증으로 대체한다.
  - `safety_video_harness/project.py`의 `audio_policy: strip_native_use_tts`를 `audio_policy: no_narration_video_only` 또는 동등 값으로 변경한다.
  - `README.md`, `AGENTS.md`, `projects/remicon-collision-guide/AGENTS.md`, `agents/video-qa.md`, `agents/visual-continuity-director.md`, `skills/story-writer/SKILL.md`의 나레이션/TTS 문구를 제거하거나 “추후 과제”로만 이동한다.
  - 기존 fixture `projects/remicon-collision-guide/storyboard/scenes.json`는 재생성하거나 migration 스크립트로 narration 필드를 제거한다.

  **Must NOT do**:
  - TTS, voiceover, Whisper, transcript 관련 코드를 추가하지 않는다.
  - 이미지 프롬프트에 정확한 한국어 텍스트 생성을 요구하지 않는다.

  **Parallelization**: Can Parallel: YES | Wave 1 | Blocks: 6, 7 | Blocked By: none

  **References**:
  - Pattern: `safety_video_harness/storyboard.py` - 현재 scene 생성 구조
  - Pattern: `safety_video_harness/validation.py` - scene 검증 진입점
  - Pattern: `README.md` - 사용자 실행 문서
  - Pattern: `skills/story-writer/SKILL.md` - 기존 narration 문구 제거 대상

  **Acceptance Criteria**:
  - [ ] `rg -n "TTS|narration_ko|narration_char_limit|나레이션|voiceover|Whisper|transcript" safety_video_harness scripts skills agents AGENTS.md README.md projects/remicon-collision-guide` 결과에서 이번 기능의 활성 경로가 없어야 한다. 단, “추후 과제” 문구는 README의 별도 섹션에만 허용한다.
  - [ ] `uv run pytest -q tests/test_story_flow_quality.py tests/test_remicon_fixture_flow.py` 통과

  **QA Scenarios**:
  ```text
  Scenario: 새 스토리보드에 나레이션 필드가 없다
    Tool: tmux
    Steps:
      tmux new-session -d -s ulw-qa-no-narration 'python3 scripts/plan_storyboard.py --project projects/remicon-collision-guide --duration 30 && python3 - <<PY
      import json
      s=json.load(open("projects/remicon-collision-guide/storyboard/scenes.json"))
      print(any("narration_ko" in x for x in s["scenes"]))
      PY'
      tmux capture-pane -pt ulw-qa-no-narration -S -200
    Expected: stdout contains `False`
    Evidence: evidence/task-1-no-narration.txt

  Scenario: 나레이션 필드가 들어오면 schema/validation에서 실패한다
    Tool: bash
    Steps: pytest test id `tests/test_no_narration_contract.py::test_legacy_narration_field_is_rejected`
    Expected: RED before implementation, GREEN after implementation
    Evidence: evidence/task-1-no-narration-red-green.txt
  ```

  **Commit**: YES | Message: `refactor(storyboard): remove narration from active video contract` | Files: `safety_video_harness/storyboard.py`, `safety_video_harness/validation.py`, docs/agent skill files, tests

- [x] 2. 영상 길이와 이미지 분량 인테이크 알고리즘 추가

  **What to do**:
  - `project_config.json`에 `target_duration_sec`와 `image_density`를 저장한다.
  - 인테이크 질문 문구를 문서화한다:
    - `몇 초짜리 영상을 만드시겠습니까?`
    - `이미지의 분량을 어떻게 하시겠습니까? 보통 / 많이 / 더 많이`
  - CLI는 `scripts/plan_storyboard.py --duration <sec> --image-density normal|high|very_high`를 지원한다.
  - 기본값은 `target_duration_sec=30`, `image_density=normal`.
  - 알고리즘:
    - `base_segments = ceil(target_duration_sec / 5)`
    - `density_factor = {"normal": 1, "high": 2, "very_high": 4}[image_density]`
    - `anchor_count = base_segments * density_factor + 1`
    - `story_beats = anchor_count - 1`
    - `planned_anchor_interval_sec = target_duration_sec / story_beats`
  - scene id는 `sc01`, `sc02`가 아니라 anchor/beat 증가에 맞춰 기존 호환성을 유지한다. 예: normal 30초는 기존과 같이 6 scenes, 7 keyframes. high 30초는 12 beats, 13 anchors.
  - Seedance 5초 atomic clip 정책과 충돌하지 않도록 `video_generation_mode`를 기록한다:
    - `normal`: 모든 5초 transition을 live 후보로 사용 가능
    - `high|very_high`: 중간 anchor는 프롬프트/QA 강화용이며, live 10초 테스트에서는 첫 10초 macro transition만 1회 생성

  **Must NOT do**:
  - 밀도 선택 때문에 유료 영상 호출 횟수를 자동으로 늘리지 않는다.
  - `high|very_high` 선택 시 Seedance를 여러 번 자동 실행하지 않는다.

  **Parallelization**: Can Parallel: YES | Wave 1 | Blocks: 4, 8 | Blocked By: none

  **References**:
  - Pattern: `safety_video_harness/storyboard.py` - 현재 `ceil(duration / seconds_per_clip)` 로직
  - Pattern: `scripts/plan_storyboard.py` - CLI 인자 확장
  - Pattern: `tests/test_seedance_live_guardrails.py` - duration 기반 fixture 준비

  **Acceptance Criteria**:
  - [ ] `python3 scripts/plan_storyboard.py --project projects/remicon-collision-guide --duration 30 --image-density normal` 결과 `clip_count=6`, `keyframe_count=7`
  - [ ] `python3 scripts/plan_storyboard.py --project projects/remicon-collision-guide --duration 30 --image-density high` 결과 `story_beats=12`, `keyframe_count=13`
  - [ ] `python3 scripts/plan_storyboard.py --project projects/remicon-collision-guide --duration 30 --image-density very_high` 결과 `story_beats=24`, `keyframe_count=25`
  - [ ] invalid density는 실패하고 허용값을 출력

  **QA Scenarios**:
  ```text
  Scenario: 보통/많이/더 많이 계산이 기대값과 일치한다
    Tool: bash
    Steps: uv run pytest -q tests/test_storyboard_density.py
    Expected: all density tests pass
    Evidence: evidence/task-2-density-tests.txt

  Scenario: 실제 fixture에서 high density dry-run이 작동한다
    Tool: tmux
    Steps:
      tmux new-session -d -s ulw-qa-density 'python3 scripts/plan_storyboard.py --project projects/remicon-collision-guide --duration 30 --image-density high && python3 scripts/generate_images.py --project projects/remicon-collision-guide --dry-run'
      tmux capture-pane -pt ulw-qa-density -S -300
    Expected: output contains `planned 12` or equivalent and `image dry-run prepared 12`
    Evidence: evidence/task-2-density-fixture.txt
  ```

  **Commit**: YES | Message: `feat(storyboard): add duration and image density planning` | Files: `safety_video_harness/storyboard.py`, `scripts/plan_storyboard.py`, tests, README

- [x] 3. 영상 분석 스킬 발견과 도구 상태 점검 강화

  **What to do**:
  - `safety_video_harness/tools.py`와 `scripts/check_tools.py`에 다음 상태를 추가한다:
    - `tesseract`
    - `higgsfield`
    - `~/.codex/skills/scenelens/SKILL.md`
    - `~/.codex/skills/video-frame-analysis/SKILL.md`
    - `~/.codex/skills/understand-video/SKILL.md`
    - `~/.codex/skills/seedance-expert/SKILL.md`
  - `tesseract --list-langs`에 `kor`와 `eng`가 있는지 표시한다.
  - 스킬이 없으면 fatal이 아니라 `missing`으로 표시하되, `inspect_video.py --tool <name>` 실행 시에는 명확히 실패한다.

  **Must NOT do**:
  - 설치 스크립트에서 자동으로 외부 repo를 내려받지 않는다.
  - API key나 secret 상태를 출력하지 않는다.

  **Parallelization**: Can Parallel: YES | Wave 1 | Blocks: 5, 10 | Blocked By: none

  **References**:
  - Pattern: `safety_video_harness/tools.py` - 현재 간단한 tool check
  - Installed skill paths: `/Users/hatae/.codex/skills/scenelens/SKILL.md`, `/Users/hatae/.codex/skills/video-frame-analysis/SKILL.md`

  **Acceptance Criteria**:
  - [ ] `python3 scripts/check_tools.py`가 `tesseract: found`, `ocr_lang_kor: found`, 네 스킬 상태를 출력
  - [ ] 테스트에서 임시 HOME/CODEX_HOME을 써서 missing skill 상태를 검증

  **QA Scenarios**:
  ```text
  Scenario: 현재 머신에서 영상 스킬과 OCR 상태가 보인다
    Tool: bash
    Steps: python3 scripts/check_tools.py | tee evidence/task-3-check-tools.txt
    Expected: output contains `scenelens: found`, `video-frame-analysis: found`, `tesseract: found`, `ocr_lang_kor: found`
    Evidence: evidence/task-3-check-tools.txt

  Scenario: 누락된 skill 경로는 missing으로 표시된다
    Tool: bash
    Steps: uv run pytest -q tests/test_tools.py::test_video_skill_missing_status_is_reported
    Expected: RED before implementation, GREEN after
    Evidence: evidence/task-3-missing-skill-red-green.txt
  ```

  **Commit**: YES | Message: `feat(tools): report local video skill availability` | Files: `safety_video_harness/tools.py`, `tests/test_tools.py`

- [x] 4. Seedance 프롬프트 계약을 `seedance-expert` 기준으로 보강

  **What to do**:
  - `safety_video_harness/prompt_contract.py`의 `build_video_prompt_plan`에 다음 필수 슬롯을 넣는다:
    - material diagnosis: start/end keyframe 역할
    - subject continuity: 인물 수, PPE, 위치, 시선 대상
    - camera motion: slow instructional motion, no sudden cut
    - action causality: 왜 사람이 보는지, 왜 멈추는지, 무엇을 피하는지
    - subtitle/overlay plan: 후처리 자막/오버레이 문구는 별도 필드로 전달
  - `seedance-expert/references/prompt-examples.md`와 `platform-constraints.md`를 참고했음을 `docs/`에 기록한다.
  - `video_prompts.json`에 `subtitle_plan_ko` 또는 `overlay_plan_ko`를 추가하되, prompt 본문에는 “do not render exact text inside generated frames; subtitles are added in post-production”를 명시한다.

  **Must NOT do**:
  - 이미지/영상 모델에 정확한 한국어 텍스트를 직접 그리라고 지시하지 않는다.
  - prompt에 나레이션 문구를 만들지 않는다.

  **Parallelization**: Can Parallel: YES | Wave 2 | Blocks: 6, 9 | Blocked By: 2

  **References**:
  - Pattern: `safety_video_harness/prompt_contract.py` - 현재 video prompt 구조
  - External local: `/Users/hatae/.codex/skills/seedance-expert/references/prompt-examples.md`
  - External local: `/Users/hatae/.codex/skills/seedance-expert/references/platform-constraints.md`

  **Acceptance Criteria**:
  - [ ] `prompts/video_prompts.json`의 각 plan에 `continuity_checklist`, `sliding_chain_contract`, `subtitle_plan_ko`가 있음
  - [ ] video prompt에 gaze/role/continuity/action causality 지시가 포함됨
  - [ ] video prompt에 narration/TTS/voiceover가 없음

  **QA Scenarios**:
  ```text
  Scenario: Seedance prompt가 연속성/시선/자막 계약을 포함한다
    Tool: bash
    Steps: uv run pytest -q tests/test_seedance_prompt_contract.py
    Expected: prompt contract assertions pass
    Evidence: evidence/task-4-seedance-prompt-tests.txt

  Scenario: 실제 fixture video prompt dry-run
    Tool: tmux
    Steps:
      tmux new-session -d -s ulw-qa-video-prompt 'python3 scripts/generate_seedance.py --project projects/remicon-collision-guide --dry-run && python3 -m json.tool projects/remicon-collision-guide/prompts/video_prompts.json | rg "subtitle_plan_ko|gaze|continuity|narration"'
      tmux capture-pane -pt ulw-qa-video-prompt -S -300
    Expected: contains subtitle/gaze/continuity, does not contain narration
    Evidence: evidence/task-4-video-prompt-fixture.txt
  ```

  **Commit**: YES | Message: `feat(prompts): strengthen seedance continuity contract` | Files: `safety_video_harness/prompt_contract.py`, docs, tests

- [x] 5. 영상 분석 어댑터와 evidence manifest 구현

  **What to do**:
  - 신규 `safety_video_harness/video_inspection.py`를 만든다.
  - 신규 `scripts/inspect_video.py`를 만든다.
  - 지원 도구:
    - `--tool scenelens`: `python3 ~/.codex/skills/scenelens/scripts/scenelens.py <clip> --no-whisper --ocr-lang kor+eng --max-frames <N> --out-dir <out>`
    - `--tool video-frame-analysis`: `OCR_LANG=kor+eng FRAME_INTERVAL_SECONDS=<N> FRAME_WIDTH=420 bash ~/.codex/skills/video-frame-analysis/scripts/video-frame-analysis.sh <clip> <out>`
    - `--tool understand-video`: 이번 범위에서는 `--frames-only`로만 허용한다. transcript/audio output은 manifest에서 `ignored` 처리하거나 생성하지 않는 방식으로 감싼다.
  - 출력:
    - `video/inspection/<clip-stem>/manifest.json`
    - `video/inspection/<clip-stem>/frames/*`
    - `video/inspection/<clip-stem>/contact.png` 가능 시
    - `video/inspection/<clip-stem>/ocr.json` 가능 시
  - manifest 필수 필드:
    - `clip`
    - `tool`
    - `transcript_enabled: false`
    - `ocr_lang: kor+eng`
    - `frame_count`
    - `frame_paths`
    - `contact_sheet`
    - `created_at`
    - `inspection_questions`: continuity, gaze, education clarity, storyboard alignment

  **Must NOT do**:
  - Whisper/Groq/OpenAI API key를 요구하거나 호출하지 않는다.
  - audio/transcript를 QA 필수 산출물로 만들지 않는다.

  **Parallelization**: Can Parallel: YES | Wave 2 | Blocks: 8, 10 | Blocked By: 3

  **References**:
  - Pattern: `safety_video_harness/video_qa.py` - video QA report writing pattern
  - Local skill: `/Users/hatae/.codex/skills/scenelens/SKILL.md`
  - Local skill: `/Users/hatae/.codex/skills/video-frame-analysis/scripts/video-frame-analysis.sh`
  - Local skill: `/Users/hatae/.codex/skills/understand-video/extract.sh`

  **Acceptance Criteria**:
  - [ ] `inspect_video.py`가 기존 `sc01_sc02_seedance.mp4`에서 manifest와 프레임을 생성
  - [ ] `--tool scenelens --no-transcript` 실행 시 `transcript_enabled=false`
  - [ ] missing tool은 명확한 에러로 실패
  - [ ] generated evidence는 `qa/video_inspection_manifest.json` 또는 clip별 manifest path로 연결됨

  **QA Scenarios**:
  ```text
  Scenario: scenelens 로컬 frame/OCR evidence 생성
    Tool: tmux
    Steps:
      tmux new-session -d -s ulw-qa-inspect-scenelens 'python3 scripts/inspect_video.py --project projects/remicon-collision-guide --clip projects/remicon-collision-guide/video/clips/sc01_sc02_seedance.mp4 --tool scenelens --no-transcript'
      tmux capture-pane -pt ulw-qa-inspect-scenelens -S -300
    Expected: output contains `manifest written`; manifest has `transcript_enabled: false` and `frame_count > 0`
    Evidence: evidence/task-5-scenelens-inspect.txt

  Scenario: missing tool path fails cleanly
    Tool: bash
    Steps: uv run pytest -q tests/test_video_inspection.py::test_missing_video_skill_fails_cleanly
    Expected: RED before implementation, GREEN after
    Evidence: evidence/task-5-missing-tool-red-green.txt
  ```

  **Commit**: YES | Message: `feat(video): add local inspection skill adapters` | Files: `safety_video_harness/video_inspection.py`, `scripts/inspect_video.py`, tests

- [x] 6. 영상 QA가 분석 evidence 없이는 통과하지 못하게 강화

  **What to do**:
  - `safety_video_harness/video_qa.py`가 `qa/video_manual_review.json` 외에 clip별 inspection manifest를 요구하도록 변경한다.
  - manual review 항목에 `inspection_manifest` 또는 `inspection_id`를 요구한다.
  - manifest에 실제 frame이 없거나 `frame_count < 3`이면 실패한다.
  - `education_clarity_score` 문구를 “나레이션 없이”가 아니라 “자막/오버레이 또는 화면 문구와 영상만으로”로 변경한다.
  - blocker 기준:
    - 인물 수가 start/end/manifest frame에서 이유 없이 변함
    - 시선 대상이 위험원/신호수/운전원/동선 중 하나로 설명되지 않음
    - 안전교육 주제가 frame sequence에서 보이지 않음
    - subtitle/overlay plan과 영상 장면이 맞지 않음

  **Must NOT do**:
  - 사람이 적은 수동 리뷰 JSON만으로 통과시키지 않는다.

  **Parallelization**: Can Parallel: YES | Wave 3 | Blocks: 10 | Blocked By: 1, 4, 5

  **References**:
  - Pattern: `safety_video_harness/video_qa.py` - current manual review scoring
  - Test: `tests/test_video_qa.py` - current pass/fail tests
  - Agent: `agents/video-qa.md` - QA rubric wording

  **Acceptance Criteria**:
  - [ ] clip은 있어도 inspection manifest가 없으면 `validate_video.py` 실패
  - [ ] manifest는 있어도 manual review가 없으면 실패
  - [ ] 둘 다 있고 점수가 기준 이상이면 통과
  - [ ] blocker가 있으면 점수와 무관하게 실패

  **QA Scenarios**:
  ```text
  Scenario: manual review만 있고 inspection evidence가 없으면 실패
    Tool: bash
    Steps: uv run pytest -q tests/test_video_qa.py::test_video_qa_requires_inspection_manifest
    Expected: RED before implementation, GREEN after
    Evidence: evidence/task-6-video-qa-manifest-red-green.txt

  Scenario: 실제 fixture clip + inspection + blocking manual review는 실패한다
    Tool: tmux
    Steps:
      tmux new-session -d -s ulw-qa-video-block 'python3 scripts/inspect_video.py --project projects/remicon-collision-guide --clip projects/remicon-collision-guide/video/clips/sc01_sc02_seedance.mp4 --tool video-frame-analysis --no-transcript && python3 scripts/validate_video.py --project projects/remicon-collision-guide --expected-clips 1'
      tmux capture-pane -pt ulw-qa-video-block -S -300
    Expected: output contains current blocker messages, not a false pass
    Evidence: evidence/task-6-video-qa-blocker.txt
  ```

  **Commit**: YES | Message: `fix(video-qa): require extracted frame evidence` | Files: `safety_video_harness/video_qa.py`, tests, agents

- [x] 7. 자막/오버레이/텍스트 카드 산출물 계약 추가

  **What to do**:
  - `storyboard/scenes.json`에 장면별 `subtitle_ko` 또는 `overlay_text_ko`를 포함한다.
  - `prompts/video_prompts.json`에는 `subtitle_plan_ko`를 포함하지만, Seedance prompt는 “text added in post-production”로 처리한다.
  - 필요하면 신규 `scripts/generate_subtitles.py --dry-run` 또는 `scripts/plan_subtitles.py`를 만든다. 이번 범위는 dry-run manifest까지이며 실제 ffmpeg burn-in은 선택 구현으로 둔다.
  - 출력 예:
    - `subtitles/subtitles.srt`
    - `subtitles/subtitle_plan.json`
  - 자막은 한국어로 짧고 교육자료 출처와 연결되어야 한다.

  **Must NOT do**:
  - TTS를 만들지 않는다.
  - 이미지 안에 텍스트를 생성하게 하지 않는다.

  **Parallelization**: Can Parallel: YES | Wave 3 | Blocks: 9 | Blocked By: 1, 2

  **References**:
  - Pattern: `safety_video_harness/storyboard.py` - caption generation
  - Pattern: `projects/remicon-collision-guide/storyboard/scenes.json` - current scene structure
  - Pattern: `safety_video_harness/prompt_contract.py` - prompt data contract

  **Acceptance Criteria**:
  - [ ] `subtitle_plan.json` 또는 SRT dry-run 생성
  - [ ] 자막 문구는 narration/TTS가 아니라 subtitle/overlay 필드에서만 옴
  - [ ] `validate_project.py`가 자막 길이와 출처 존재를 검사

  **QA Scenarios**:
  ```text
  Scenario: fixture에서 자막 계획 dry-run 생성
    Tool: bash
    Steps: python3 scripts/plan_subtitles.py --project projects/remicon-collision-guide --dry-run | tee evidence/task-7-subtitle-plan.txt
    Expected: output names subtitle plan file, file contains Korean subtitle entries
    Evidence: evidence/task-7-subtitle-plan.txt

  Scenario: 자막 필드가 비어 있으면 validate_project 실패
    Tool: bash
    Steps: uv run pytest -q tests/test_subtitle_contract.py::test_missing_subtitle_text_fails_validation
    Expected: RED before implementation, GREEN after
    Evidence: evidence/task-7-subtitle-validation-red-green.txt
  ```

  **Commit**: YES | Message: `feat(subtitles): add no-narration text delivery contract` | Files: storyboard/prompt/subtitle modules, scripts, tests

- [x] 8. Live Seedance 10초 1회 검증 가드레일 강화

  **What to do**:
  - 이번 검증 경로에서는 `--max-attempts 1`을 요구한다.
  - 기존 제품 가드레일 `MAX_ATTEMPTS=3`는 장기 운영 상한으로 남길 수 있으나, live validation command에는 `max_attempts=1` mode를 추가한다.
  - `scripts/generate_seedance.py`에 `--validation-run` 같은 명시 flag를 추가하거나, README/계획 실행에서는 `--max-attempts 1`를 강제한다.
  - `build_seedance_live_plan`에 `paid_run_policy` 필드를 기록한다:
    - `test_seconds: 10`
    - `max_attempts: 1`
    - `allowed_live_invocations: 1`
    - `requires_gate: image_to_video`
  - live 실행 전 `higgsfield generate cost` 결과를 evidence에 저장한다.
  - live 실행 후 어떤 결과가 나와도 동일 작업 묶음에서 두 번째 유료 호출은 금지한다.

  **Must NOT do**:
  - 실패했다고 자동으로 재시도하지 않는다.
  - 10초를 초과하거나 2회 이상 paid call을 실행하지 않는다.

  **Parallelization**: Can Parallel: NO | Wave 4 | Blocks: 10 | Blocked By: 2, 4

  **References**:
  - Pattern: `safety_video_harness/seedance_live.py` - current live plan and max attempts
  - Pattern: `scripts/generate_seedance.py` - CLI flags
  - Tests: `tests/test_seedance_live_guardrails.py`

  **Acceptance Criteria**:
  - [ ] `--validation-run --test-seconds 10 --max-attempts 1 --plan-only` 통과
  - [ ] `--validation-run --max-attempts 2` 실패
  - [ ] `--validation-run --test-seconds 15` 실패
  - [ ] plan JSON에 paid policy가 기록

  **QA Scenarios**:
  ```text
  Scenario: 10초 1회 validation plan 생성
    Tool: bash
    Steps: python3 scripts/generate_seedance.py --project projects/remicon-collision-guide --live --execute-paid --test-seconds 10 --max-attempts 1 --validation-run --plan-only | tee evidence/task-8-live-plan.txt
    Expected: output contains `Seedance live plan prepared`; plan has `max_attempts: 1`
    Evidence: evidence/task-8-live-plan.txt

  Scenario: validation mode에서 2회 시도는 차단
    Tool: bash
    Steps: uv run pytest -q tests/test_seedance_live_guardrails.py::test_validation_run_requires_one_attempt
    Expected: RED before implementation, GREEN after
    Evidence: evidence/task-8-one-attempt-red-green.txt
  ```

  **Commit**: YES | Message: `feat(seedance): add one-shot paid validation guardrail` | Files: `safety_video_harness/seedance_live.py`, `scripts/generate_seedance.py`, tests, README

- [x] 9. 문서, 에이전트, 훅을 새 정책에 맞게 정렬

  **What to do**:
  - `README.md`에서 현재 상태의 `실제 TTS 생성 어댑터` 체크박스를 제거하거나 “추후 과제: 현재 범위 제외”로 이동한다.
  - 빠른 시작에 `--image-density`와 `plan_subtitles.py`/`inspect_video.py` 흐름을 추가한다.
  - `agents/video-qa.md`, `agents/visual-continuity-director.md`, `agents/continuity-qa.md`에 다음을 명시한다:
    - 영상 QA는 frame evidence manifest 없이는 불가
    - 자막/오버레이는 후처리 텍스트 계약
    - 나레이션/전사는 이번 범위 밖
  - `skills/video-inspect/SKILL.md`에 설치 스킬 3개 사용 우선순위를 기록한다:
    1. `scenelens --no-whisper`
    2. `video-frame-analysis`
    3. `understand-video` frames-only
  - live veto hook 문구에서 TTS 관련 활성 경로를 제거한다. 단, 과거 안전 차단 문구는 삭제하지 말고 “현재 미사용”으로 정리한다.

  **Must NOT do**:
  - `plans/archive`를 수정하지 않는다.

  **Parallelization**: Can Parallel: YES | Wave 3 | Blocks: 10 | Blocked By: 1, 5, 6, 7, 8

  **References**:
  - Pattern: `README.md` - current user workflow
  - Pattern: `agents/video-qa.md`
  - Pattern: `skills/video-inspect/SKILL.md`
  - Hook: `hooks/pretooluse-live-veto.py`

  **Acceptance Criteria**:
  - [ ] README에 나레이션/TTS가 활성 목표로 남지 않음
  - [ ] README에 `inspect_video.py`, `validate_video.py`, 10초 1회 live 검증 순서가 있음
  - [ ] agent docs가 frame evidence manifest를 필수로 요구

  **QA Scenarios**:
  ```text
  Scenario: 문서에서 활성 narration/TTS 경로가 제거됨
    Tool: bash
    Steps: rg -n "실제 TTS 생성 어댑터|narration_ko|나레이션" README.md AGENTS.md agents skills | tee evidence/task-9-doc-search.txt
    Expected: no active workflow references; only future-work section if present
    Evidence: evidence/task-9-doc-search.txt

  Scenario: README 빠른 시작 명령이 실제 CLI와 일치
    Tool: bash
    Steps: uv run pytest -q tests/test_docs_commands.py
    Expected: documented commands parse or are explicitly marked paid/manual
    Evidence: evidence/task-9-doc-command-tests.txt
  ```

  **Commit**: YES | Message: `docs(video): align workflow with no-narration inspection policy` | Files: README, agents, skills, hooks/docs tests

- [x] 10. 실제 fixture dry-run과 10초 1회 live 검증

  **What to do**:
  - 작업 전 full dry-run:
    - `uv run pytest -q`
    - `python3 scripts/check_tools.py`
    - `python3 scripts/validate_project.py projects/remicon-collision-guide`
    - `python3 scripts/generate_images.py --project projects/remicon-collision-guide --dry-run`
    - `python3 scripts/generate_seedance.py --project projects/remicon-collision-guide --dry-run`
  - live 전 preflight:
    - Gate 2 승인 상태 확인
    - `external_upload_allowed=true` 확인
    - `python3 scripts/validate_scene_links.py --project projects/remicon-collision-guide`
    - `python3 scripts/generate_seedance.py --project projects/remicon-collision-guide --live --execute-paid --test-seconds 10 --max-attempts 1 --validation-run --plan-only`
  - live 실행은 정확히 1회:
    - `python3 scripts/generate_seedance.py --project projects/remicon-collision-guide --live --execute-paid --test-seconds 10 --max-attempts 1 --validation-run`
  - 생성된 clip을 다운로드/등록한 뒤:
    - `python3 scripts/inspect_video.py --project projects/remicon-collision-guide --clip <clip> --tool scenelens --no-transcript`
    - 필요한 경우 `--tool video-frame-analysis`로 보조 evidence 생성
    - `qa/video_manual_review.json` 작성 또는 갱신
    - `python3 scripts/validate_video.py --project projects/remicon-collision-guide --expected-clips 1`

  **Must NOT do**:
  - live가 실패해도 같은 작업에서 두 번째 paid call을 하지 않는다.
  - 영상 퀄리티가 낮으면 재시도하지 말고 blocker와 수정 프롬프트를 evidence로 남긴다.

  **Parallelization**: Can Parallel: NO | Wave 5 | Blocks: Final Verification | Blocked By: 5, 6, 8, 9

  **References**:
  - Project: `projects/remicon-collision-guide`
  - Existing clips: `projects/remicon-collision-guide/video/clips/*.mp4`
  - Existing evidence examples: `evidence/story-flow-video-live-2026-06-11.md`
  - Script: `scripts/generate_seedance.py`
  - Script: `scripts/inspect_video.py`
  - Script: `scripts/validate_video.py`

  **Acceptance Criteria**:
  - [ ] full test suite passes before live
  - [ ] live plan-only evidence saved
  - [ ] exactly one paid live execution log saved
  - [ ] generated clip has inspection manifest and manual review
  - [ ] video QA either passes or fails with concrete blocker evidence; false pass is not allowed

  **QA Scenarios**:
  ```text
  Scenario: full dry-run before paid execution
    Tool: tmux
    Steps:
      tmux new-session -d -s ulw-qa-full-dry 'uv run pytest -q && python3 scripts/check_tools.py && python3 scripts/generate_seedance.py --project projects/remicon-collision-guide --dry-run'
      tmux capture-pane -pt ulw-qa-full-dry -S -500
    Expected: pytest green and dry-run prepared
    Evidence: evidence/task-10-full-dry-run.txt

  Scenario: one paid 10-second validation run
    Tool: tmux
    Steps:
      tmux new-session -d -s ulw-qa-one-paid 'python3 scripts/generate_seedance.py --project projects/remicon-collision-guide --live --execute-paid --test-seconds 10 --max-attempts 1 --validation-run'
      tmux capture-pane -pt ulw-qa-one-paid -S -500
    Expected: exactly one live execution attempt recorded in `video/seedance_live_runs.jsonl`
    Evidence: evidence/task-10-one-paid-live.txt

  Scenario: generated clip inspection and QA
    Tool: tmux
    Steps:
      tmux new-session -d -s ulw-qa-final-video 'python3 scripts/inspect_video.py --project projects/remicon-collision-guide --clip <new-clip-path> --tool scenelens --no-transcript && python3 scripts/validate_video.py --project projects/remicon-collision-guide --expected-clips 1'
      tmux capture-pane -pt ulw-qa-final-video -S -500
    Expected: pass only if frame evidence and review meet thresholds; otherwise blocker report
    Evidence: evidence/task-10-final-video-qa.txt
  ```

  **Commit**: NO | Message: N/A | Files: generated evidence/project artifacts only

## Final Verification Wave
> ALL must APPROVE. Present consolidated results to user and get explicit "okay" before completing.

- [x] F1. Plan Compliance Audit
  - Verify no task implemented TTS, narration, voiceover, Whisper API, or transcript path.
  - Command: `rg -n "TTS|voiceover|Whisper|transcript|narration_ko|narration_char_limit|나레이션" safety_video_harness scripts README.md AGENTS.md agents skills`
  - Evidence: `evidence/final-no-narration-audit.txt`

- [x] F2. Code Quality Review
  - Run `uv run pytest -q`.
  - Run LSP diagnostics if available for changed Python files.
  - Evidence: `evidence/final-pytest-video-skill-integration.txt`

- [x] F3. Real Manual QA
  - Run actual fixture workflow through CLI/tmux.
  - Include one paid 10-second validation run only if all preflight checks pass.
  - Evidence: `evidence/final-manual-qa-video-skill-integration.txt`

- [x] F4. Scope Fidelity Check
  - Confirm `plans/archive` unchanged.
  - Confirm live run count is exactly one for the validation run.
  - Confirm video QA requires inspection manifest.
  - Evidence: `evidence/final-scope-fidelity-video-skill-integration.txt`

## Commit Strategy
- Use small commits per task where source/docs/tests changed.
- Do not commit generated paid video files unless the user explicitly asks.
- Suggested final commit order:
  1. `refactor(storyboard): remove narration from active video contract`
  2. `feat(storyboard): add duration and image density planning`
  3. `feat(tools): report local video skill availability`
  4. `feat(video): add local inspection skill adapters`
  5. `feat(prompts): strengthen seedance continuity contract`
  6. `fix(video-qa): require extracted frame evidence`
  7. `feat(subtitles): add no-narration text delivery contract`
  8. `feat(seedance): add one-shot paid validation guardrail`
  9. `docs(video): align workflow with no-narration inspection policy`

## Success Criteria
- Installed video skills are not just documented; they are callable through the harness or a harness wrapper.
- Video QA cannot pass without real extracted frame evidence.
- No active narration/TTS/Whisper/transcript workflow remains in this implementation scope.
- User can select video duration and image density before storyboard generation.
- Seedance live validation is limited to exactly one 10-second paid run.
- The final result either passes QA or produces concrete blocker evidence and next prompt/storyboard corrections.
