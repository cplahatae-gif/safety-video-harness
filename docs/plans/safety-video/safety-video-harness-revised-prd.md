# 안전교육 영상 자동제작 하네스 수정 PRD

> 상태: 수정 PRD 후보  
> 기준 문서: `plans/safety-video-harness-final-prd.md`, `plans/safety-video-harness-roadmap.md`  
> 반영 내용: PRD MAS 다중 라운드 토론 구조, PRD MAS Archiver 영속 지식화, 현재 구현 상태, 미구현 항목 전체, 에이전트 품질 강화 요구  
> 핵심 변경: 단일 평가자가 아니라 **역할별 독립 평가자 + Arbiter 집계 + 조건부 토론 + early-stopping RALPH loop** 구조로 전환한다.
> 승격 규칙: 이 문서가 승인되면 `plans/safety-video-harness-final-prd.md`를 대체하는 실행 기준이 된다.

## 1. 제품 정의

`safety-video-harness`는 PPTX, SOP, PDF, DOCX, 이미지 기반 안전교육 자료를 입력받아 한국어 안전교육 영상을 제작하는 Codex 플러그인형 하네스다.

이 제품의 본질은 영상 생성기가 아니라 **유료 영상 생성 전에 실패 가능성을 최대한 줄이는 제작 통제 시스템**이다. 스토리보드는 무료 루프에서 충분히 검증하고, 이미지는 점수 기반으로 선택 재생성하며, 영상은 비용이 크므로 자동 재생성하지 않고 수정 제안만 남긴다.

## 2. 핵심 원칙

- 스토리보드를 먼저 만들고, 스토리보드가 충분히 세밀해진 뒤 이미지와 영상을 만든다.
- 영상 길이는 기본 30초다. 30초는 기술 제한이 아니라 비용과 검수 가드레일이다.
- 나레이션, TTS, Whisper/API 전사는 현재 활성 범위에서 제외한다.
- 전달해야 하는 내용은 자막, 오버레이, 텍스트 카드 산출물로 처리한다.
- 영상 생성은 유료이므로 자동 RALPH 재생성 대상이 아니다.
- 이미지 RALPH loop는 무조건 20회가 아니라 **최대 20회 early-stopping loop**다.
- 같은 blocker가 3회 반복되면 단순 재생성이 아니라 스토리보드, 레퍼런스, 프롬프트 계약 문제로 에스컬레이션한다.
- 생성자와 평가자는 분리한다. 생성한 에이전트가 자기 산출물을 최종 승인하지 않는다.
- 평가자는 전체 대화 맥락이 아니라 필요한 evidence bundle만 보고 채점한다.
- 모든 라운드 결과는 프로젝트 evidence와 `llm-wiki/evaluation-rounds.md`에 누적하고, 다음 라운드 프롬프트 개선에 실제로 사용한다.
- post-run archive와 system rollup은 라이브 루프와 분리한다. 매 라운드마다 무거운 graphify/rollup을 돌리지 않는다.
- 기존 PRD/로드맵에 남아 있는 TTS, 나레이션, native audio 처리 항목은 현 범위에서 비활성화한다. 해당 기능은 향후 옵션으로만 남긴다.

## 3. 현재 구현 상태

### 3.1 구현됨

- 독립형 플러그인 스캐폴딩: `.codex-plugin/plugin.json`
- 기본 에이전트/스킬/훅 파일 구조: `agents/`, `skills/`, `hooks/`
- 프로젝트 초기화와 자료 등록: `init_project.py`, `register_sources.py`
- PPTX 내부 미디어 추출 기반 렌더링: `render_pptx_sources.py --mode media_extract`
- 주제 추출과 명시 선택: `extract_topics.py`, `select_topic.py`
- 스토리보드 생성: `plan_storyboard.py`
- 영상 길이와 이미지 밀도 입력: `--duration`, `--image-density normal|high|very_high`
- Codex 내장 `imagegen` 작업 명세 생성: `imagegen_jobs.py`, `generate_images.py`
- 생성 이미지 수거와 버전 저장: `record_image_output.py`
- 승인 이미지 이동: `approve_image.py`
- Gate 1, Gate 2 기본 승인/차단
- `external_upload_allowed=false` live 차단
- Seedance dry-run과 제한된 live 경로: `generate_seedance.py`, `seedance_live.py`
- 비디오 프레임 검사 manifest 생성: `inspect_video.py`, `video_inspection.py`
- 비디오 QA propose-only 정책: `video_qa.py`
- 자막 계획 산출: `plan_subtitles.py`, `subtitles.py`
- 스토리보드 QA: `storyboard_qa.py`
- 이미지 QA 기본 점수와 RALPH loop 계약: `image_qa.py`
- 평가 라운드 원장과 evidence bundle 기록: `evaluation_rounds.py`
- `llm-wiki/evaluation-rounds.md` 기록
- 실제 fixture: `fixtures/sources/remicon-collision-guide.pptx`
- 실제 10초 Seedance 검증 파일럿 산출물
- 현재 테스트 기반: `uv run pytest -q`

### 3.2 부분 구현

- 이미지 QA는 파일/비율/스토리 필드 기반 검증은 가능하지만, 실제 이미지 의미 이해는 약하다.
- 영상 QA는 프레임 manifest와 수동 점수 계약은 있으나, 자동 시각 평가자는 아직 없다.
- `llm-wiki/evaluation-rounds.md`는 기록되지만, 다음 프롬프트 생성에 자동 주입되지는 않는다.
- RALPH loop는 카운트와 최대치 계약은 있으나, 이미지 생성-검증-재생성의 완전 자동 오케스트레이터는 없다.
- Seedance live 경로는 존재하지만, 최종 운영용 비용/실패/재시도 정책과 CLI 버전 고정은 더 강화해야 한다.
- 훅 파일은 존재하지만, Codex 플러그인 런타임에서 실제 등록/차단 동작 검증이 충분하지 않다.
- 에이전트 파일은 역할 이름은 있으나 전문 평가자로 쓰기에는 지침, rubric, 사례, 공식 레퍼런스가 부족하다.

### 3.3 미구현 또는 다음 구현 대상

- 실제 슬라이드 렌더링: `soffice` 기반 PPTX→PNG
- PDF/DOCX/OCR 정식 파이프라인
- 이미지 레퍼런스의 실제 비전 분석 기반 인물/장비 자동 프로파일링
- 역할별 독립 평가자 산출물 분리
- Arbiter 점수 집계와 최종 decision engine
- 조건부 토론 엔진
- 반복 blocker 3회 감지와 upstream escalation
- `llm-wiki/evaluation-rounds.md`를 다음 이미지/영상 프롬프트에 자동 반영
- PRD MAS Archiver 방식의 post-run session archive
- graphify 또는 대체 도구 기반 system wiki/graph rollup
- agent quality pack: 공식 문서, 외부 플러그인/스킬, 예시 리뷰, 금지 패턴, 평가 rubric 번들
- video QA의 자동 프레임 기반 평가 보강
- 스토리보드/이미지/영상 3자 일치 전용 `triad_reviews.json`
- 최종 MP4 합성
- 자막 burn-in 또는 대체 subtitle package 정책
- 승인 이미지 reject 이동 정책 완성
- rollback 명령
- 모든 adapter 실패의 append-only `errors.jsonl` 기록
- 플러그인 설치/재설치/패키징 smoke test
- 새 Codex 세션에서 hook runtime smoke test

## 4. 사용자 시나리오

### 4.1 기본 안전교육 제작

1. 사용자가 교육자료를 등록한다.
2. 시스템이 자료를 렌더링하고 복수 주제를 추출한다.
3. 사용자가 주제를 선택한다.
4. 사용자가 영상 길이와 이미지 분량을 선택한다.
5. 사용자가 인물, PPE, 장비, 작업상황, 스타일 레퍼런스를 넣는다.
6. 시스템이 스토리보드를 생성한다.
7. 역할별 평가자가 스토리보드를 평가한다.
8. Arbiter가 통과 또는 수정 방향을 확정한다.
9. Gate 1 승인 후 이미지 job spec을 만든다.
10. Codex `imagegen` skill/tool로 이미지를 생성하고 프로젝트에 수거한다.
11. 역할별 이미지 평가자가 채점한다.
12. Arbiter가 승인, 재생성, upstream escalation을 결정한다.
13. Gate 2에서 비용과 외부 업로드 허용을 확인한다.
14. Seedance 영상 생성은 짧은 검증 실행부터 한다.
15. 영상은 프레임 검사와 역할별 평가를 거쳐 최종본 후보가 된다.
16. 실패하면 자동 재생성하지 않고 수정 제안만 남긴다.

### 4.2 반복 실패 처리

1. `sc03` 이미지가 인물 시선 문제로 1회 실패한다.
2. RALPH는 blocker를 `llm-wiki/evaluation-rounds.md`에 기록한다.
3. 다음 재생성 프롬프트는 “신호수를 바라보는 이유와 시선 대상”을 더 강하게 고정한다.
4. 같은 시선 blocker가 3회 반복되면 이미지 재생성을 멈춘다.
5. Arbiter는 스토리보드가 모호한지, 레퍼런스가 부족한지, 프롬프트 계약이 약한지 분류한다.
6. 시스템은 영상 생성으로 넘어가지 않고 스토리보드/레퍼런스 수정 제안을 만든다.

## 5. 에이전트 품질 강화 요구

현재 에이전트 문서는 역할 이름과 기본 규칙 수준이다. 제품 품질을 높이려면 에이전트를 단순 md 파일이 아니라 **전문 평가 패키지**로 확장해야 한다.

### 5.1 Agent Quality Pack

각 에이전트는 다음 파일 구조를 가진다.

```text
agents/<agent-name>.md
agent_quality/
  references/
    codex-imagegen.md
    seedance-prompting.md
    higgsfield-cli.md
    safety-training-storyboard.md
    visual-continuity.md
    industrial-ppe-and-equipment.md
  rubrics/
    storyboard-rubric.md
    image-rubric.md
    video-rubric.md
    triad-rubric.md
  examples/
    good-storyboard-review.md
    bad-storyboard-review.md
    good-image-review.md
    bad-image-review.md
    video-failure-cases.md
  external-skills/
    installed-skills.md
    reuse-policy.md
```

### 5.2 공식 레퍼런스 수집

다음 레퍼런스를 로컬 문서로 저장하고 에이전트가 참조하게 한다.

- Codex 내장 `imagegen` skill 사용 규칙
- OpenAI 이미지 생성 가이드 중 프롬프트 구성과 한계
- Seedance/Higgsfield CLI 사용법과 start/end frame 요구사항
- 안전교육 영상 스토리보드 작성 기준
- 한국 산업안전 교육용 PPE, 신호수, 중장비 주변 보행자 동선 기준
- 현재 설치된 영상 분석 스킬: `scenelens`, `video-frame-analysis`, `understand-video`
- 현재 설치된 영상 생성/프롬프트 스킬: `seedance-expert`

공식 문서가 없거나 불안정한 경우:

- 다운로드 문서와 수집일을 기록한다.
- 출처 URL 또는 파일 경로를 남긴다.
- 모델/도구 버전이 바뀔 수 있음을 명시한다.
- 문서 기반 규칙과 프로젝트 로컬 경험 규칙을 분리한다.

### 5.3 외부 스킬/플러그인 재사용 정책

이미 설치된 스킬은 재구현하지 않고 활용한다.

| 기능 | 우선 활용 |
|---|---|
| 이미지 생성 | Codex built-in `imagegen` |
| Seedance 프롬프트 | `seedance-expert` |
| 비디오 프레임 분석 | `video-frame-analysis` |
| 비디오 이해 보조 | `understand-video` |
| 장면/OCR/캡션 추출 | `scenelens` |
| Remotion 기반 향후 합성 | Remotion 플러그인 후보 |

외부 스킬은 다음 조건을 만족해야 한다.

- 입력/출력 계약을 프로젝트 evidence에 남긴다.
- 유료 호출 또는 외부 업로드 여부를 명확히 표시한다.
- 실패 시 fallback을 정의한다.
- 프로젝트 원본 자료를 승인 없이 외부 업로드하지 않는다.

### 5.4 에이전트별 품질 기준

#### `storyteller`

- 교육자료 출처 없는 안전 주장을 만들 수 없다.
- 각 장면은 이전 장면의 결과와 다음 장면의 원인을 연결해야 한다.
- 자막/오버레이로 전달 가능한 문구를 설계해야 한다.
- 나레이션을 쓰지 않는다.

#### `visual-continuity-director`

- 인물, PPE, 장비, 배경, 시선 대상, 위험원 위치를 장면별로 고정한다.
- “갑자기 사람이 생김/사라짐”을 blocker로 판정한다.
- 시선이 무엇을 향하는지 설명되지 않으면 blocker로 판정한다.

#### `continuity-qa`

- 스토리보드, 이미지, 프롬프트가 서로 맞는지 평가한다.
- 생성자의 의도 설명을 믿지 않고 evidence bundle만 본다.
- 점수와 blocker, 재생성 delta를 반드시 남긴다.

#### `video-qa`

- MP4 존재, 길이, 해상도만으로 통과시키지 않는다.
- inspection manifest와 sampled frame evidence를 요구한다.
- 영상이 교육자료를 전달하지 못하면 미학적으로 좋아도 reject한다.

#### 신규 `arbiter`

- 역할별 평가 점수를 집계한다.
- 토론이 필요한 조건을 판단한다.
- 재생성, upstream escalation, Gate 통과, 사용자 승인 요청을 결정한다.
- 영상에 대해서는 자동 재생성 명령을 만들지 않고 proposal만 만든다.

## 6. 평가 아키텍처

### 6.1 전체 구조

```text
Generator
  -> Deterministic Validator
  -> Role Evaluators
  -> Arbiter
  -> Decision
  -> RALPH / Escalation / Gate
```

### 6.2 단일 에이전트 채점 금지

단일 에이전트가 모든 것을 채점하면 다음 위험이 있다.

- 생성 의도를 실제 결과보다 과대평가한다.
- 이미지/영상의 시각적 문제를 텍스트 설계로 보정해서 해석한다.
- 안전교육 관점, 시각 연속성 관점, 비용 관점이 섞인다.

따라서 핵심 산출물 평가는 역할별 평가자와 Arbiter를 거친다.

### 6.3 역할별 평가자

#### 스토리보드 평가자

| 평가자 | 책임 |
|---|---|
| Safety SME Evaluator | 교육자료 근거, 안전수칙 정확성, 위험 표현 적정성 |
| Story/Pedagogy Evaluator | 30초 교육 흐름, 이해 가능성, 자막/오버레이 전달성 |
| Visual Continuity Evaluator | 인물, 장비, 동선, 시선, start/end keyframe |
| Production Arbiter | 점수 집계, 수정/통과/토론 결정 |

#### 이미지 평가자

| 평가자 | 책임 |
|---|---|
| Technical Validator | 파일 존재, 해상도, 비율, 손상 여부 |
| Visual Continuity Evaluator | 인물, PPE, 장비, 배경, 시선 일관성 |
| Story Match Evaluator | scene의 교육 목적과 이미지 내용 일치 |
| Safety Visual Evaluator | 충돌/부상/로고/생성 텍스트/위험 미화 금지 |
| Arbiter | 승인, 재생성, upstream escalation 결정 |

#### 영상 평가자

| 평가자 | 책임 |
|---|---|
| Frame Inspector | ffprobe/ffmpeg/scenelens/video-frame-analysis evidence 생성 |
| Video Continuity Evaluator | 인물 등장/퇴장, 장비 유지, start/end keyframe 보존 |
| Gaze/Motivation Evaluator | 시선 대상과 행동 동기 |
| Education Clarity Evaluator | 영상+자막만으로 교육 주제 이해 가능 여부 |
| Arbiter | accept/propose-only/reject 결정 |

### 6.4 토론 발생 조건

항상 풀 토론을 돌리지 않는다. 다음 조건에서만 조건부 토론을 실행한다.

- 평가자 간 동일 항목 점수 차이가 2점 이상
- 같은 blocker가 같은 scene에서 3회 이상 반복
- 이미지 RALPH가 5회 이상 실패
- Gate 2 직전 비용 큰 영상 생성 판단
- 영상 생성 후 기준 미달
- 안전수칙 해석이 교육자료만으로 애매함

토론은 새로운 생성이 아니라 **판단을 정리하는 과정**이다. 토론 결과는 다음 중 하나여야 한다.

- regenerate image
- revise storyboard
- add or replace reference
- strengthen prompt contract
- accept risk with user approval
- stop and escalate

### 6.5 구현 표면

이 평가 아키텍처는 다음 구현 표면을 요구한다.

```text
safety_video_harness/evaluator_reviews.py
safety_video_harness/evaluation_arbiter.py
safety_video_harness/debate.py
safety_video_harness/blocker_signatures.py
scripts/run_evaluators.py
scripts/run_arbiter.py
scripts/run_debate.py
```

각 스크립트는 dry-run 가능해야 하며 유료 호출을 하지 않는다.

### 6.6 Arbiter 집계 규칙

Arbiter는 평균 점수만 보지 않는다.

- blocker veto: 안전, 생성 텍스트, 인물 급변, 시선 불명확, 교육자료 불일치는 단일 평가자라도 blocker가 될 수 있다.
- minimum field score: 각 핵심 필드는 4점 이상이어야 한다.
- disagreement trigger: 동일 필드에서 평가자 간 점수 차이가 2점 이상이면 debate_required가 된다.
- repeated blocker trigger: 같은 blocker signature가 같은 item에서 3회 이상 반복되면 `revise_storyboard`, `update_reference`, `strengthen_prompt_contract` 중 하나로 에스컬레이션한다.
- video cost veto: 영상 단계의 실패는 자동 재생성이 아니라 proposal-only로 종료한다.

### 6.7 Blocker signature 규칙

같은 blocker인지 판단하기 위해 문자열 그대로 비교하지 않는다. Arbiter는 blocker를 정규화한 signature로 저장한다.

```text
<stage>:<item_id>:<rubric_field>:<normalized_issue_type>
```

예시:

```text
image:sc03:gaze_motivation:unclear_target
image:sc03:identity_consistency:worker_changed
video:sc01_sc02:character_continuity:person_disappears
storyboard:sc04:source_grounding:missing_citation
```

반복 횟수는 `qa/evaluation_rounds.jsonl`와 `qa/arbiter_decisions/*`를 함께 읽어 계산한다.

## 7. RALPH loop 정책

### 7.1 기본 알고리즘

```text
1. 이미지 생성 또는 draft 수거
2. deterministic validation
3. 역할별 평가
4. Arbiter 집계
5. 통과하면 종료
6. 미달이면 deficiency와 regeneration_delta 기록
7. 같은 blocker 반복 횟수 확인
8. 3회 반복이면 upstream escalation
9. 20회 도달이면 stop_and_escalate
```

### 7.2 반복 중단 조건

- 모든 필드가 기준 이상이면 즉시 종료
- scene별 최대 20회 도달
- 같은 blocker 3회 반복
- 레퍼런스 부족 판정
- 스토리보드 모호 판정
- 사용자 중단
- 영상 단계 진입 필요성 상실

### 7.3 반복 기록

각 반복은 다음 위치에 남긴다.

```text
qa/evaluation_rounds.jsonl
qa/evaluation_bundles/image/scNN/round_NNN.json
llm-wiki/evaluation-rounds.md
images/draft/scNN_vNNN.png
```

### 7.4 반복 blocker 분류

| 분류 | 의미 | 다음 조치 |
|---|---|---|
| prompt_gap | 지시가 부족함 | prompt contract 강화 |
| reference_gap | 기준 이미지/설명이 부족함 | ref/model/product 추가 |
| storyboard_gap | scene 자체가 모호함 | storyboard 수정 |
| model_limit | 이미지 모델이 반복 실패 | 구도 단순화 또는 분할 |
| safety_conflict | 교육자료/안전수칙 해석 충돌 | 사용자 또는 안전 담당자 확인 |

## 8. llm-wiki 활용 정책

### 8.1 라이브 메모리

`llm-wiki/evaluation-rounds.md`는 원본 evidence가 아니라 다음 라운드 의사결정을 돕는 요약 인덱스다.

다음 작업 전에 반드시 읽는다.

- 같은 scene의 이미지 재생성 프롬프트 작성
- RALPH 2회차 이상 실행
- Gate 2 승인 전
- 영상 프롬프트 작성
- 영상 QA 실패 후 수정 제안 작성

### 8.2 프롬프트 주입 규칙

다음 이미지 프롬프트에는 이전 실패 요약이 포함되어야 한다.

```text
Previous QA blockers for this scene:
- ...

Do not repeat:
- ...

Required correction this round:
- ...
```

### 8.3 에스컬레이션 판단

`llm-wiki/evaluation-rounds.md`에서 같은 blocker가 3회 이상 발견되면 Arbiter는 재생성을 멈추고 다음 중 하나를 선택한다.

- scene split
- storyboard rewrite
- reference update
- prompt contract update
- user review required

### 8.4 post-run archive

프로젝트 종료 또는 major Gate 통과 후, 다음 구조로 영속 아카이브를 만든다.

```text
~/.safety-video-harness/
  sessions/
    <YYYY-MM-DD>-<slug>/
      project-summary.md
      sources-summary.md
      storyboard/
      prompts/
      qa/
      llm-wiki/
      final-package/
      transcript.md
      meta.md
  wiki/
  graph/
  index.md
```

라이브 루프 중에는 무거운 graph/rollup을 돌리지 않는다. post-run archive는 additive 계층이며 현재 프로젝트 산출물을 수정하지 않는다.

## 9. 데이터 계약

### 9.0 기존 schema 정리

기존 PRD와 일부 초기 schema에는 `narration_ko`, `narration_char_limit`, `audio_policy`, `tts` 관련 항목이 남아 있다. 수정 PRD 기준에서는 다음처럼 처리한다.

- `narration_ko`: 신규 산출물에서는 금지한다.
- `narration_char_limit`: 신규 산출물에서는 사용하지 않는다.
- `audio_policy`: `no_narration_video_only`로 고정한다.
- `tts` adapter: MVP와 활성 범위에서 제외한다.
- 기존 파일에 narration 필드가 있으면 validator는 경고 또는 실패를 반환해야 한다.
- 교육 문구는 `subtitle_ko`, `overlay_ko`, `title_card_ko` 중 하나로 표현한다.

### 9.1 신규/강화 산출물

```text
qa/evaluator_reviews/
  storyboard/scNN/round_NNN/<role>.json
  image/scNN/round_NNN/<role>.json
  video/<clip>/round_NNN/<role>.json

qa/arbiter_decisions/
  storyboard/scNN/round_NNN.json
  image/scNN/round_NNN.json
  video/<clip>/round_NNN.json

qa/debate/
  image/scNN/round_NNN.md
  video/<clip>/round_NNN.md

qa/triad_reviews.json
qa/evaluation_rounds.jsonl
llm-wiki/evaluation-rounds.md
```

### 9.2 Arbiter decision schema

```json
{
  "stage": "image",
  "item_id": "sc03",
  "round": 4,
  "decision": "regenerate|approve|revise_storyboard|update_reference|stop_and_escalate",
  "scores": {
    "technical": 5,
    "visual_continuity": 3,
    "story_match": 4,
    "safety": 5
  },
  "blocking_issues": [],
  "repeated_blockers": [],
  "debate_required": false,
  "next_action": "",
  "regeneration_delta": "",
  "evidence_bundle": "qa/evaluation_bundles/image/sc03/round_004.json"
}
```

### 9.3 Evaluation bundle schema

```json
{
  "stage": "image",
  "item_id": "sc03",
  "round": 4,
  "evaluator_context_policy": "isolated_evaluator_with_evidence_bundle",
  "source_summary": {},
  "selected_topic": {},
  "current_scene": {},
  "previous_scene": {},
  "next_scene": {},
  "reference_assets": {},
  "generated_asset": "",
  "previous_round_summary": [],
  "rubric": {},
  "forbidden_assumptions": [
    "Do not infer intent from the generator's prompt if the image does not show it."
  ]
}
```

## 10. 이미지 생성 정책

### 10.1 기본 경로

- 기본 이미지는 Codex 내장 `imagegen` skill/tool로 생성한다.
- Python CLI는 직접 유료 API를 호출하지 않고 job spec을 만든다.
- OpenAI Image API/CLI adapter는 기본 구현 금지다.

### 10.2 프롬프트 필수 구성

각 이미지 프롬프트는 다음을 포함한다.

- scene id
- previous scene continuity
- current story beat
- next scene setup
- fixed character lock
- fixed PPE lock
- fixed equipment lock
- fixed site lock
- camera and composition
- gaze target and motivation
- safety teaching point
- negative constraints
- previous QA blockers from `llm-wiki/evaluation-rounds.md`

### 10.3 이미지 QA 통과 기준

| 항목 | 기준 |
|---|---|
| technical | 16:9, readable image, expected file path |
| visual continuity | 인물/PPE/장비/배경 유지 |
| story match | scene의 교육 목표와 일치 |
| gaze motivation | 시선 대상과 이유가 보임 |
| safety visual | 사고 충돌/부상/위험 미화 없음 |
| no generated text | 이미지 안에 생성 텍스트 없음 |

각 항목 4점 이상, 총점 기준 이상, blocker 없음이 통과 조건이다.

## 11. 영상 생성 정책

### 11.1 기본 경로

- 영상은 Higgsfield CLI / Seedance를 사용한다.
- Gate 2와 `--execute-paid` 없이는 live 실행 불가다.
- 검증 실행은 10초, 최대 1회가 기본이다.
- full run은 검증 실행 통과 후 사용자 승인으로만 진행한다.

### 11.2 영상 QA

영상 QA는 다음 증거 없이는 통과할 수 없다.

- ffprobe metadata
- local inspection manifest
- sampled frames 또는 contact sheet
- storyboards
- approved keyframes
- manual or agent visual scores

### 11.3 영상 실패 처리

영상은 유료이므로 자동 재생성하지 않는다.

실패 시 생성한다.

```text
qa/video_regeneration_proposals.json
```

내용:

- 부족한 장면
- 어떤 keyframe/스토리보드/프롬프트를 먼저 고칠지
- 다음 유료 실행 예상 비용
- 사용자 승인 필요 여부

## 12. 소스 자료 처리 정책

### 12.1 현재 지원

- PPTX 내부 이미지 미디어 추출
- 파일 해시 기록
- source facts 생성
- 주제 후보 생성

### 12.2 미구현 요구

- `soffice` 기반 슬라이드 렌더링
- PDF 페이지 렌더링
- DOCX 텍스트와 이미지 추출
- OCR
- 슬라이드별 텍스트와 이미지의 source citation 연결
- 교육자료 내 복수 주제 클러스터링

### 12.3 수용 기준

- 원본 파일은 `sources/raw/`에 보존한다.
- 렌더링 결과는 `sources/rendered/`에 저장한다.
- source fact는 어느 파일, 어느 슬라이드/페이지에서 왔는지 추적 가능해야 한다.
- 외부 업로드가 필요한 분석은 `external_upload_allowed=true` 없이는 실행하지 않는다.

## 13. 레퍼런스 처리 정책

### 13.1 폴더

```text
model/cast/
model/ppe/
product/equipment/
ref/candidates/
ref/approved/
```

### 13.2 미구현 요구

- 이미지 자체를 비전 모델로 읽어 `.profile.md` 초안 생성
- 사람/장비/작업상황/스타일 분류
- reference 부족 감지
- approved reference만 프롬프트에 반영
- reference 변경 시 기존 승인 이미지의 영향 범위 표시

## 14. Hook과 비용 가드레일

### 14.1 필수 차단

- Gate 1 전 live imagegen 금지
- Gate 2 전 Seedance live 금지
- `--execute-paid` 없는 Seedance live 금지
- `external_upload_allowed=false` live 업로드 금지
- API key/token/Bearer 문자열 파일 기록 금지
- `plans/archive` 수정 금지
- 승인 산출물 overwrite 금지

### 14.2 미구현 요구

- 실제 Codex 새 세션에서 hook 등록 smoke test
- hook이 project config와 approval state를 읽어 조건부로 통과/차단
- `.harness/DONE` 없는 완료 차단
- hook 실패 3회 상한과 pending/done 상태기계

## 15. Post-run Archive와 System Rollup

PRD MAS Archiver 구조를 차용하되, 라이브 제작 루프는 건드리지 않는다.

### 15.1 archive 트리거

- 프로젝트 최종 QA 통과
- Gate 2 통과 후 유료 생성 전 snapshot
- 사용자가 명시적으로 `archive` 요청

### 15.2 archive 입력

- project config
- sources summary
- selected topic
- scenes
- prompts
- image/video QA
- evaluation rounds
- llm-wiki
- final output paths
- transcript summary

### 15.3 archive 출력

- session wiki
- system wiki
- optional graph
- index
- 반복 실패/성공 패턴 요약

### 15.4 구현 주의

- archive는 additive다.
- 프로젝트 내부 원본 evidence를 수정하지 않는다.
- graphify가 없으면 markdown archive만 만든다.
- system rollup은 자동 증분 또는 수동 rebuild로 분리한다.

## 16. MVP 재정의

### 16.1 MVP에 반드시 포함

- 역할별 독립 평가자 output contract
- Arbiter decision contract
- 조건부 토론 트리거
- 이미지 RALPH early-stopping max 20
- 같은 blocker 3회 반복 escalation
- `llm-wiki/evaluation-rounds.md`의 다음 프롬프트 주입
- Gate 2 전 영상 비용 proposal
- 영상 propose-only 실패 처리
- no narration/TTS 정책
- agent quality pack 최소 1차 버전
- 실제 fixture 기준 dry-run full chain

### 16.2 MVP에서 제외

- full 자동 유료 영상 재생성
- full TTS/나레이션
- 모든 PDF/DOCX 완전 지원
- 모든 공식 문서 자동 최신화
- graphify 필수 의존성
- 자동 게시

## 17. 구현 우선순위

### Wave 1. 문서와 계약 정리

- 이 PRD를 기준 문서로 채택
- README에서 기존 TTS/나레이션 표현 제거
- 현재 구현 상태표 갱신
- agent quality pack 구조 생성

### Wave 2. 평가자와 Arbiter

- role evaluator review schema
- arbiter decision schema
- evaluator output 저장 경로
- 기존 `validate_images.py`, `evaluate_storyboard.py`, `validate_video.py`와 연결

### Wave 3. RALPH escalation

- 같은 blocker 3회 반복 감지
- `llm-wiki` previous blockers prompt 주입
- regeneration delta 강화
- `stop_and_escalate` 분기 구현

### Wave 4. 조건부 토론

- disagreement 감지
- repeated blocker 토론
- Gate 2 preflight 토론
- debate 결과를 Arbiter decision으로 반영

### Wave 5. 에이전트 품질 강화

- 공식/로컬 reference 문서 수집
- 외부 스킬 재사용 정책 문서화
- 에이전트별 rubric과 good/bad 예시 작성
- agent prompt를 evidence-only 평가자로 강화

### Wave 6. 영상 QA 강화

- triad review
- video frame agent scoring
- gaze motivation scoring
- education clarity scoring
- propose-only regeneration plan 보강

### Wave 7. 자료 처리와 archive

- slide_render/OCR/PDF/DOCX 확장
- post-run archive
- system wiki/graph rollup
- plugin packaging smoke test

## 18. 성공 지표

### 18.1 기능 지표

- 새 프로젝트에서 자료 등록부터 스토리보드 QA까지 dry-run 성공
- Gate 1 전 live imagegen 차단
- Gate 1 후 imagegen job spec 생성
- 이미지 QA 실패 시 regeneration delta 생성
- 같은 blocker 3회 반복 시 upstream escalation
- Gate 2 전 비용과 위험 명세 생성
- 영상 실패 시 `propose_only` plan 생성

### 18.2 품질 지표

- 스토리보드 모든 scene이 source citation을 가진다.
- 이미지 프롬프트 모든 scene이 previous/current/next continuity를 가진다.
- approved image는 덮어쓰기 없이 버전 보존된다.
- video QA는 metadata-only로 통과하지 않는다.
- 평가자는 evidence bundle 없이 통과 판정을 내릴 수 없다.
- `llm-wiki/evaluation-rounds.md`가 다음 프롬프트에 반영된다.

### 18.3 비용 지표

- 유료 영상 생성은 기본 10초 검증 1회로 제한된다.
- 자동 유료 재생성은 없다.
- full run은 사용자 승인 후에만 가능하다.

## 19. 검증 기준

### 19.1 자동 테스트

최소 테스트:

- role evaluator schema validation
- arbiter aggregation happy path
- evaluator disagreement triggers debate
- repeated blocker 3회 escalation
- max 20 RALPH early stop
- llm-wiki previous blocker injection into image prompt
- video propose-only regeneration plan
- Gate 1/Gate 2 live blocking
- archive markdown fallback without graphify

### 19.2 실제 fixture QA

fixture:

```text
projects/remicon-collision-guide
fixtures/sources/remicon-collision-guide.pptx
```

필수 실행:

```bash
uv run pytest -q
python3 scripts/evaluate_storyboard.py --project projects/remicon-collision-guide
python3 scripts/generate_images.py --project projects/remicon-collision-guide --dry-run
python3 scripts/validate_images.py --project projects/remicon-collision-guide --only sc01
python3 scripts/validate_scene_links.py --project projects/remicon-collision-guide
python3 scripts/generate_seedance.py --project projects/remicon-collision-guide --dry-run
```

유료 실행은 별도 승인 없이는 검증 기준에 포함하지 않는다.

## 20. 명시적 비범위

- 법률/SHE 전문가 검토 대체
- 사고 충돌 순간, 부상, 유혈 표현
- 승인 없는 외부 업로드
- 승인 없는 유료 호출
- 자동 유튜브 업로드
- 나레이션/TTS 활성 기능
- API key를 파일에 저장하는 방식

## 21. 최종 결정

채택:

- 역할별 독립 평가자
- Arbiter 집계
- 조건부 토론
- early-stopping RALPH
- 반복 blocker escalation
- `llm-wiki` live memory
- post-run archive
- agent quality pack
- 외부 스킬 재사용

폐기:

- 단일 에이전트 단독 채점
- 매 라운드 풀 토론
- 영상 자동 재생성
- 현재 범위의 나레이션/TTS
- 이미지/영상 생성 API adapter 기본 구현

보류:

- graphify 필수 의존성
- Remotion 기반 최종 합성
- PDF/DOCX 완전 지원
- full 자동 archive hook
