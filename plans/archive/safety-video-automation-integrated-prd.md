# 안전교육 영상 자동제작 통합 PRD

> 기준 PRD A: `plans/safety-video-automation-prd.ko.md`
> 비교 PRD B: `/Users/hatae/Downloads/safety-video-harness-prd-v2.md`
> 작성일: 2026-06-10
> 상태: 통합 실행 기준 초안
> 기존 소스 PRD는 비교 입력일 뿐이며, 이 파일이 다음 구현 계획의 기준이다.

## 0. 결론

최종 통합 방향은 **B를 실행 하네스의 뼈대로 채택하고, A를 제품 요구사항과 품질 검증 범위로 흡수**하는 것이다.

A는 사용자가 실제로 원하는 영상 제작 흐름, 이미지 검색, 전문 에이전트, 스토리보드-이미지-영상 3자 검증을 넓게 잡았다. B는 그 요구를 실제로 안전하게 실행하기 위한 하네스 제어면, PLAN.md 계약, 훅, 청정수 구역, 비용순 검증 사다리, 재현성 조건이 훨씬 강하다.

따라서 최종 PRD는 다음을 따른다.

- 제품 목적과 산출 범위는 A에서 가져온다.
- 하네스 구조와 실행 통제는 B에서 가져온다.
- 에이전트는 A처럼 많이 만들지 않고, B의 3개 격리 에이전트 안에 A의 전문 역할을 스킬로 배치한다.
- 영상 생성은 스토리보드와 이미지 검증 이후에만 실행한다.
- 30초는 기술 제한이 아니라 기본 비용/검수 가드레일로 유지한다.
- Higgsfield CLI, Seedance, OpenAI 이미지 생성의 정확한 명령 문법은 구현 첫 단계에서 `--help`와 공식 문서로 고정한다.
- canonical 플러그인 ID는 `safety-video-harness`로 한다. `safety-video-automation`은 표시 이름이나 문서 제목에서만 사용할 수 있다.

## 1. 두 PRD 비교 결과

### 1.1 A가 더 나은 점

1. **제품 요구가 사용자 의도에 더 가깝다.**
   - 교육자료에 여러 주제가 있을 수 있다는 점을 명확히 반영한다.
   - 주제 추출, 주제 선택, 이미지 검색, 스타일 DNA, 스토리보드, 이미지, 영상까지 사용자의 실제 제작 흐름을 자연스럽게 설명한다.

2. **전문 검증 역할이 더 세분화되어 있다.**
   - 이미지 일관성 검증.
   - 스토리-이미지 일치 검증.
   - 영상 인식.
   - 스토리보드-이미지-영상 3자 일치 검증.
   - 프롬프트 전문 에이전트.

3. **이미지 검색과 스타일 레퍼런스 단계가 더 분명하다.**
   - 애니메이션 안전교육 영상처럼 사용자가 원하는 스타일과 관련된 사례를 찾고 승인한 뒤 스타일 DNA에 반영하는 흐름이 구체적이다.

4. **영상 결과물 피드백 루프의 필요성을 잘 잡았다.**
   - Codex가 비디오 파일을 직접 이해한다고 가정하지 않고, 프레임 샘플링으로 분석해야 한다는 문제의식이 명확하다.

5. **비개발자 사용자 관점의 설명이 좋다.**
   - 어떤 단계에서 사용자가 승인해야 하는지, 왜 영상 생성은 조심해야 하는지 이해하기 쉽다.

### 1.2 B가 더 나은 점

1. **실제 구현 가능성이 높다.**
   - PLAN.md 계약, End Conditions, Budgets, sentinel, `validate_plan.py`가 있어 자동 실행의 종료 조건이 분명하다.
   - 훅이 7개로 구체화되어 있고 각 훅의 책임이 좁다.

2. **하네스 구조가 더 강하다.**
   - 엔진과 가드레일을 분리한다.
   - OmO가 없어도 수동 모드로 파이프라인이 동작해야 한다는 엔진 독립성 요구가 좋다.
   - 드리프트, 조기정지, 데이터파괴, 예산소진의 4대 이탈 패턴과 대책이 직접 매핑되어 있다.

3. **비용 관리가 더 실전적이다.**
   - L0 정적 검증, L1 도메인 자가검증, L2 이미지, L3 영상, L4 사람 검수의 비용순 사다리가 명확하다.
   - 루프 중 유료 호출 금지, Gate 2 비용 명세 필수, `--live` 이중 게이트가 강하다.

4. **데이터 보호와 재현성이 좋다.**
   - 청정수 구역을 정의해 승인 산출물, 스키마, 훅, PLAN.md 핵심 필드를 보호한다.
   - 승인된 산출물 덮어쓰기 금지, regenerate 시 버전 보존, append-only 상태 관리가 더 안전하다.

5. **MVP 실행성이 좋다.**
   - 18개 Task와 Wave 구조가 있어 바로 개발 순서를 잡을 수 있다.
   - dry-run 중심이라 유료 생성 없이 대부분 검증 가능하다.

6. **영상 품질 및 재현가능성 요구가 더 명확하다.**
   - 나레이션 자수 제한, 한글 프롬프트 금지, 한국어 폰트 점검, `ffprobe`/`ffmpeg` 프레임 검증, 도구 사전 점검이 포함되어 있다.

## 2. 기준별 판정

| 기준 | 판정 | 이유 |
|---|---|---|
| 1. 구현 가능성 | B 우세 | B가 PLAN.md, 훅, 스키마, 검증 명령, dry-run을 구체화했다. |
| 2. 자동화 범위 | A 우세 | A가 이미지 검색, 전문 에이전트, 3자 검증 등 사용자 요구 전체를 더 넓게 담았다. |
| 3. 하네스 구조 | B 우세 | B의 엔진/가드레일 분리, 청정수 구역, sentinel, 훅 캐시 규칙이 더 실행 가능하다. |
| 4. 에이전트/스킬/훅/MCP | B 우세 | B는 7 hooks, 6 skills, 3 agents로 최소 구조를 제안한다. A는 역할은 좋지만 과분화 위험이 있다. |
| 5. 이미지 품질 관리 | 통합 필요 | A의 전문 검증 축 + B의 A2 격리 QA와 선택 재생성을 합쳐야 한다. |
| 6. 영상 생성 비용 관리 | B 우세 | B의 L0-L4 사다리와 `--live` 차단이 더 강하다. |
| 7. 검증 루프 | B 우세 | B는 루프 종료 조건, self_score, H6/H7, 침투 테스트까지 있다. |
| 8. 데이터 구조 | B 우세 | B의 `approvals.json`, `PLAN.md`, `.harness/self_score.json`, 스키마 하드 룰이 더 좋다. |
| 9. MVP 실행성 | B 우세 | B는 Wave 0-4로 개발 순서가 잡혀 있다. |
| 10. 장기 확장성 | 통합 필요 | B의 미니멀 하네스에 A의 제품 유형 확장성을 붙이는 방식이 좋다. |
| 11. 영상 품질 및 재현가능성 | B 우세 | B가 도구 버전, dry-run, 폰트, 프레임 샘플링, 버전 보존을 포함한다. |
| 12. 현재 프로젝트 목적 적합성 | 통합 필요 | 안전교육 영상이라는 목적은 A가 더 직접적이고, 독립 플러그인 실행은 B가 더 적합하다. |

## 3. 충돌하는 설계

### 3.1 에이전트 수

- A: 10개 이상의 전문 에이전트/스킬을 제안한다.
- B: 3개 격리 에이전트와 6개 스킬로 제한한다.

판정:

- B 방식을 채택한다.
- A의 전문 역할은 별도 에이전트가 아니라 스킬과 체크리스트로 흡수한다.

이유:

- 에이전트가 많아지면 컨텍스트, 권한, 책임 경계가 흐려진다.
- 안전교육 자동화에서는 창의성보다 재현 가능한 검증이 중요하다.

### 3.2 Ralph Loop 20회 vs PLAN.md max_turns

- A: Ralph Loop 20회를 고정 요구한다.
- B: PLAN.md `max_turns: 20`과 self-score 기반 종료를 둔다.

판정:

- 통합한다.
- "20회"는 중요한 PRD/스토리보드/하네스 검토의 기본값으로 두되, 유료 생성 루프에는 적용하지 않는다.
- 루프 중 유료 호출은 항상 금지한다.

### 3.3 영상 길이 정책

- A: 30초는 기본 가드레일, 초과 가능.
- B: 30초 내외, 60/90초 프리셋은 비용 경고와 승인.

판정:

- 통합한다.
- 기본은 30초, 31-60초는 확장 모드, 61초 이상은 챕터 모드로 분리한다.

### 3.4 MCP 위치

- A: optional MCP adapter.
- B: CLI 우선, MCP는 선택.

판정:

- B를 채택한다.
- Higgsfield는 CLI가 1차 경로, MCP는 선택 어댑터다.

### 3.5 Seedance/CLI 세부 문법

- A/B 모두 일부 기술 전제를 포함한다.
- 외부 CLI 문법은 변경될 수 있다.

판정:

- 명령 파라미터를 PRD에서 확정하지 않는다.
- 구현 Task 0에서 `higgsfield --help`, `higgsfield generate --help`, 공식 문서, 실제 dry-run 출력으로 고정한다.

### 3.6 게이트 수

- A: Gate A-E를 둔다.
- B: `storyboard`, `image_to_video` 두 승인 레코드를 둔다.

판정:

- B의 두 승인 레코드를 canonical로 채택한다.
- A의 Gate A, C, E는 별도 승인 레코드가 아니라 workflow checkpoint와 L0-L4 검증 단계로 흡수한다.

매핑:

| A 게이트 | 통합 PRD 위치 |
|---|---|
| Gate A 주제 선택 | `topic_selected` checkpoint |
| Gate B 스토리보드 승인 | `approvals.json.gates.storyboard` |
| Gate C 이미지 승인 | L2 이미지 QA checkpoint |
| Gate D 영상 생성 승인 | `approvals.json.gates.image_to_video` |
| Gate E 영상-스토리 일치 | L3/L4 영상 QA checkpoint |

### 3.7 데이터 구조

- A: `storyboard/storyboard.json`, `image_reviews.json`, `video_reviews.json`, `state/gates.json` 중심.
- B: `scenes.json`, `approvals.json`, `.harness/*` 중심.

판정:

- B의 구조를 canonical로 채택한다.
- A의 리뷰 파일 개념은 `evidence/`와 `qa/*.json` 산출물로 흡수한다.
- 기존 루트의 `scenes.json`, `storyboard/*.png` 같은 과거 산출물은 입력으로 사용하지 않는다.

## 4. 합쳐야 할 설계

1. A의 제품 파이프라인 + B의 단방향 배수관.
2. A의 이미지 검색 정책 + B의 승인된 웹 검색 정책.
3. A의 프롬프트 디렉터 + B의 `seedance-prompting` 스킬.
4. A의 이미지 일관성 검증 + B의 A2 `continuity-qa`.
5. A의 영상 인식 에이전트 + B의 A3 `video-qa`.
6. A의 3자 일치 검증 + B의 `inspect_video.py`.
7. A의 30초 정책 정정 + B의 비용 사다리.
8. A의 다양한 상태 파일 + B의 `PLAN.md`, `approvals.json`, `.harness/*`.
9. A의 외부 레퍼런스 명시 + B의 구현 시 실제 CLI 문법 고정 원칙.

## 5. 버려야 할 설계

1. **전문 역할마다 별도 에이전트를 만드는 구조**
   - 역할은 유지하되 에이전트 수는 3개로 제한한다.

2. **유료 생성까지 Ralph Loop 안에 넣는 구조**
   - 루프는 L0/L1 무료 검증까지.
   - 이미지/영상/TTS live 생성은 사람 승인 후 루프 밖.

3. **웹 레퍼런스를 자동 사용하거나 다운로드하는 흐름**
   - 검색은 후보 수집까지만.
   - 사용은 승인과 출처 기록 후에만.

4. **OpenAI/Codex/Higgsfield 명령 문법을 추측해 고정하는 문서**
   - 공식 문서와 `--help` 확인 전까지는 adapter contract만 정의한다.

5. **영상 검증을 "Codex가 비디오를 본다"로 가정하는 구조**
   - MP4는 `ffmpeg`/`ffprobe`로 프레임과 메타를 추출해 검증한다.

## 6. 최종 통합 제품 목표

SOP, PPTX, PDF, DOCX, 이미지 기반 교육자료를 입력하면 Codex 플러그인이 다음을 수행한다.

1. 자료를 등록하고 렌더링한다.
2. 여러 교육 주제 후보를 추출한다.
3. 사용자가 주제를 선택한다.
4. 번호형 인테이크로 길이, 톤, 화면비, 레퍼런스 정책, 나레이션, 자막, 안전 표현 경계를 확정한다.
5. 승인된 레퍼런스와 자료 스타일에서 스타일 DNA를 추출한다.
6. 출처 기반 스토리보드를 만든다.
7. L0/L1 무료 검증 루프를 통과할 때까지 스토리보드를 수정한다.
8. Gate 1 승인 후 키프레임 이미지를 생성한다.
9. 이미지 일관성과 스토리-이미지 일치성을 검증한다.
10. Gate 2 승인과 비용 명세 확인 후 Seedance 영상을 생성한다.
11. MP4를 프레임 샘플링해 스토리보드/이미지/영상 3자 일치 검증을 수행한다.
12. TTS, 자막, ffmpeg 합성으로 최종 MP4와 검수 패키지를 만든다.

## 7. 통합 하네스 아키텍처

### 7.1 레이어

| 레이어 | 책임 | 구현 |
|---|---|---|
| 실행 엔진 | 반복 실행, 지속성 | OmO `ulw-loop` 또는 수동 계속 실행 |
| 가드레일 | 방향, 차단, 검증 | AGENTS.md, PLAN.md, hooks, schemas, validators |
| 도메인 스킬 | 주제 추출, 스토리, 프롬프트, 검증 | 6개 스킬 |
| 격리 에이전트 | 생성/검증 컨텍스트 분리 | 3개 에이전트 |
| 어댑터 | 외부 도구 연결 | OpenAI/Codex image, Higgsfield CLI, Gemini TTS, ffmpeg |

### 7.2 플러그인 이름

```text
safety-video-harness
```

표시 이름:

```text
Safety Video Automation
```

### 7.3 플러그인 구조

```text
safety-video-harness/
  .codex-plugin/
    plugin.json
  AGENTS.md
  skills/
    topic-extractor/
    story-writer/
    seedance-prompting/
    image-consistency-check/
    video-inspect/
    style-ref-search/
  agents/
    storyteller.md
    continuity-qa.md
    video-qa.md
  hooks/
    session-start-anchor.py
    pretooluse-live-veto.py
    pretooluse-protected-path-veto.py
    pretooluse-secret-veto.py
    posttooluse-schema-validation.py
    posttooluse-evidence-feedback.py
    stop-sentinel-guard.py
    protected_paths.json
  scripts/
    check_tools.py
    validate_plan.py
    init_project.py
    register_sources.py
    render_pptx_sources.py
    extract_topics.py
    intake_project.py
    search_references.py
    extract_style_dna.py
    plan_storyboard.py
    validate_project.py
    approve_gate.py
    generate_images.py
    validate_images.py
    generate_seedance.py
    generate_tts.py
    compose_video.py
    inspect_video.py
  schemas/
    project_config.schema.json
    scenes.schema.json
    style_dna.schema.json
    approvals.schema.json
    sources.schema.json
  templates/
    project/
      PLAN.md
      AGENTS.safety.md
  references/
    openai-image-generation.md
    higgsfield-cli.md
    higgsfield-seedance.md
    harness-engineering.md
```

부트스트랩 예외:

- `hooks/`, `schemas/`, `projects/_templates/`는 완성 후 청정수 구역이다.
- Wave 1-2에서 해당 파일을 처음 생성하는 동안에는 bootstrap mode를 사용한다.
- bootstrap mode 종료 후에는 보호 목록에 편입하고, 이후 수정은 `.harness/retro.md` 제안과 사람 승인 후에만 허용한다.

## 8. 에이전트/스킬 설계

### 8.1 에이전트 3종

| 에이전트 | 책임 | 포함하는 A의 역할 |
|---|---|---|
| `storyteller` | 주제, 사실, 스타일 DNA를 받아 스토리와 씬 초안을 만든다. | 교육자료 주제 추출 보조, 스토리 전문, 스토리보드 작성 |
| `continuity-qa` | 스토리보드, 프롬프트, 이미지의 도메인 정합성과 일관성을 검증한다. | 이미지 일관성 검증, 스토리-이미지 일치, 프롬프트 검토 |
| `video-qa` | 영상 메타/프레임을 샘플링하고 스토리보드/이미지/영상 3자 일치를 검증한다. | 영상 인식, 3자 일치 검증 |

원칙:

- 생성과 검증 컨텍스트를 분리한다.
- 검증 에이전트는 증거 없는 감상평을 금지한다.
- 모든 리뷰는 점수, blocker, 근거, 수정 제안을 포함한다.

### 8.2 스킬 6종

| 스킬 | 책임 |
|---|---|
| `topic-extractor` | 교육자료에서 복수 주제 후보를 추출하고 사용자 선택용 표를 만든다. |
| `story-writer` | 안전교육용 서사 구조, 컷 분해, 나레이션 자수 제한을 적용한다. |
| `seedance-prompting` | 이미지/영상 프롬프트를 영어로 고도화하고 start/end frame 조건을 명시한다. |
| `image-consistency-check` | 인물, PPE, 장비, 배경, 위험요인, 금지 표현을 채점한다. |
| `video-inspect` | `ffprobe`, `ffmpeg`, 프레임 샘플링, 3자 일치 검증을 수행한다. |
| `style-ref-search` | 승인된 웹 검색/사용자 제공 자료에서 스타일 레퍼런스 후보를 수집한다. |

## 9. 훅 설계

| ID | 훅 | 이벤트 | 책임 |
|---|---|---|---|
| H1 | SessionStart anchor | SessionStart | PLAN.md, approvals, AGENTS 핵심 금지사항 주입 |
| H2 | Live generation veto | PreToolUse | Gate 승인 없는 `--live` 이미지/영상/TTS 차단 |
| H3 | Protected path veto | PreToolUse | 청정수 구역 쓰기/삭제 차단 |
| H4 | Secret veto | PreToolUse | API key, token, bearer 문자열 파일 기록 차단 |
| H5 | Schema validation feedback | PostToolUse | 스키마/상태 파일 변경 시 검증 실행 결과 주입 |
| H6 | Evidence feedback | PostToolUse | 증거 없는 완료 주장, 점수 없는 감상평 차단 피드백 |
| H7 | Stop sentinel guard | Stop | `.harness/DONE` 없으면 조기정지 차단 |

## 10. 단방향 파이프라인

```text
init
  -> source registration
  -> source rendering
  -> topic extraction
  -> intake
  -> reference search and approval
  -> style DNA
  -> storyboard
  -> L0/L1 validation loop
  -> Gate 1 storyboard approval
  -> image generation
  -> image consistency QA
  -> Gate 2 image-to-video approval with cost disclosure
  -> Seedance generation
  -> video frame inspection
  -> TTS
  -> subtitle burn-in and composition
  -> final QA package
```

단방향 원칙:

- 이전 단계로 되돌아갈 수는 있지만 임의 단계로 점프하지 않는다.
- 유료 단계는 승인 없이 진입하지 않는다.
- 성공한 척하지 않는다. 완료 전 write-read-back과 evidence가 필요하다.

## 11. 비용순 검증 사다리

| 레벨 | 비용 | 내용 | 반복 정책 |
|---|---|---|---|
| L0 | 무료/초 단위 | schema, pytest, dry-run, 파일 존재 | 무제한 |
| L1 | 무료/분 단위 | 출처, 나레이션 길이, 스토리 정합, 프롬프트 누락 | 무제한 |
| L2 | 유료-저 | Codex/OpenAI 이미지 생성 | Gate 1 이후, 선택 재생성 |
| L3 | 유료-고 | Higgsfield CLI / Seedance 영상 생성 | Gate 2 이후, 1회 지향 |
| L4 | 사람 비용 | Gate 승인, 최종 교육자료 적합성 검수 | 80% 이후 필수 |

## 12. 데이터 계약

### 12.1 `project_config.json`

```json
{
  "schema_version": "2.1",
  "project_type": "safety",
  "project_name": "",
  "slug": "",
  "topic": "",
  "target_seconds": 30,
  "duration_policy": "default_30_extend_with_approval",
  "seconds_per_clip": 5,
  "aspect_ratio": "16:9",
  "resolution": "1080p",
  "chain_policy": "hybrid",
  "source_policy": "company_approved_or_generated",
  "reference_policy": "approved_candidates_only",
  "safety_boundary": "near_miss_prevention_only",
  "audio_policy": "strip_native_use_tts",
  "live_generation_requires_approval": true,
  "credit_budget": {
    "total": 0,
    "estimated": 0,
    "spent": 0,
    "unit": "credits"
  },
  "tools": {
    "image": "codex_or_openai_image",
    "video": "higgsfield_cli_seedance",
    "tts": "gemini_tts",
    "compose": "ffmpeg"
  }
}
```

### 12.2 `sources.json`

```json
{
  "sources": [
    {
      "source_id": "src-001",
      "path": "",
      "type": "pptx|pdf|docx|image|text",
      "sha256": "",
      "page_count": 0,
      "rendered_assets": [],
      "registered_at": ""
    }
  ]
}
```

### 12.3 `extracted_topics.json`

```json
{
  "topics": [
    {
      "topic_id": "topic-001",
      "title_ko": "",
      "risk_type": "",
      "target_worker": "",
      "source_citations": [],
      "video_fit_score": 0,
      "priority_score": 0,
      "recommended": false
    }
  ]
}
```

### 12.4 `scenes.json`

```json
{
  "schema_version": "2.1",
  "target_seconds": 30,
  "seconds_per_clip": 5,
  "chain_policy": "hybrid",
  "scenes": [
    {
      "id": "sc01",
      "duration_sec": 5,
      "educational_goal_ko": "",
      "source_citations": [
        {
          "source_id": "",
          "page_or_slide": 1,
          "claim": ""
        }
      ],
      "visual_action_ko": "",
      "caption_ko": "",
      "narration_ko": "",
      "narration_char_limit": 25,
      "image_prompt_en": "",
      "motion_prompt_en": "",
      "start_keyframe": "",
      "end_keyframe": "",
      "clip_path": "",
      "continuity_constraints": {
        "character_ids": [],
        "equipment_ids": [],
        "ppe_requirements": [],
        "background_id": ""
      },
      "approval_state": "draft",
      "asset_version": 1
    }
  ]
}
```

하드 룰:

- `source_citations`는 씬마다 1개 이상.
- `len(narration_ko) <= duration_sec * 5`.
- `image_prompt_en`에는 한글, 자막 생성 지시, 임의 텍스트 삽입 지시 금지.
- 승인 상태는 enum으로만 허용한다.

### 12.5 `approvals.json`

```json
{
  "gates": {
    "storyboard": {
      "approved": false,
      "approved_by": "",
      "approved_at": "",
      "approved_items": [],
      "notes": ""
    },
    "image_to_video": {
      "approved": false,
      "approved_by": "",
      "approved_at": "",
      "approved_items": [],
      "cost_disclosure": {
        "estimated_credits": 0,
        "clip_count": 0,
        "regeneration_risk": ""
      },
      "notes": ""
    }
  }
}
```

### 12.6 `.harness/self_score.json`

```json
{
  "turn": 1,
  "scores": {
    "functional": 0,
    "technical": 0,
    "completeness": 0,
    "harness": 0
  },
  "p0_issues": [],
  "p1_issues": [],
  "evidence": "evidence/loop-001.md"
}
```

## 13. 30초 및 컷 정책

- 기본 영상 길이: 30초.
- 30초는 기술 한계가 아니라 비용/검수 기본값이다.
- 31-60초: 확장 모드. 예상 비용과 검수 시간을 보여주고 승인받는다.
- 61초 이상: 챕터 모드. 여러 30-45초 단위 영상으로 분할한다.
- Seedance는 샷/클립 단위로 생성하고, 긴 영상은 여러 클립 연결로 만든다.
- 기본 컷 길이: 5초.
- 30초 기준: 6클립.
- sliding-chain 기준 키프레임 수: 7개.
- independent 기준 키프레임 수: 6개.
- hybrid 기준: 동일 장소/동작은 sliding, 장면 전환은 independent.

## 14. 이미지 생성 품질 관리

이미지 생성 전:

- 스토리보드가 Gate 1을 통과해야 한다.
- 이미지 프롬프트는 `seedance-prompting` 스킬의 필수 필드를 모두 채워야 한다.
- 레퍼런스 이미지는 승인된 후보만 사용한다.

이미지 프롬프트 필수 필드:

```text
Subject
Scene purpose
Worker count
PPE details
Equipment identity
Spatial relationship
Hazard location
Safe or unsafe action
Camera angle
Lighting
Background
Style DNA
Continuity anchors
Negative constraints
No text unless explicitly approved
```

이미지 생성 후:

- `continuity-qa`가 인물, PPE, 장비, 배경, 스타일, 위험요인, 금지 표현을 5점 척도로 채점한다.
- blocker가 있는 씬만 `--only scNN --regenerate` 대상으로 만든다.
- 기존 승인 이미지는 덮어쓰지 않고 버전 보존한다.

## 15. 영상 생성 품질 관리

영상 생성 전:

- Gate 2가 승인되어야 한다.
- 승인 레코드에는 비용 명세가 있어야 한다.
- `--live` 명령은 Gate 2 승인 없이는 훅에서 차단한다.
- Seedance CLI 실제 파라미터는 구현 첫 단계에서 `higgsfield --help`와 공식 문서로 고정한다.

영상 프롬프트 필수 필드:

```text
Start frame role
End frame role
Camera movement
Subject motion
Timing
Transition intention
What must remain unchanged
What must not appear
Native audio policy
```

영상 생성 후:

- `ffprobe`로 길이, fps, 해상도, 오디오 트랙을 확인한다.
- `ffmpeg`로 시작/중간/끝 프레임과 1fps 샘플을 추출한다.
- `video-qa`가 프레임과 승인 이미지, scenes.json을 대조한다.
- 영상이 멋있어도 교육 목표와 다르면 reject한다.

## 16. 공식 문서 기준 기술 앵커

### 16.1 OpenAI 이미지 생성

OpenAI 공식 문서 기준:

- `gpt-image-2`는 이미지 생성과 편집을 지원한다.
- Image API와 Responses API 모두 이미지 생성 경로를 제공한다.
- 여러 reference image를 사용한 새 이미지 생성이 가능하다.
- 출력 크기, 품질, 포맷을 조정할 수 있다.
- 지연, 텍스트 렌더링, 반복 캐릭터/브랜드 일관성, 정밀 구도 제어는 한계로 관리해야 한다.

통합 PRD 반영:

- 빠른 초안은 낮은 품질/작은 크기로 생성한다.
- 최종 키프레임은 품질을 올린다.
- 이미지 일관성은 모델에 맡기지 않고 별도 QA와 선택 재생성으로 관리한다.

### 16.2 Higgsfield CLI / Seedance

Higgsfield 공식 문서 기준:

- CLI 설치는 `npm install -g @higgsfield/cli` 경로가 제공된다.
- 인증은 `higgsfield auth login` 경로가 제공된다.
- CLI는 업로드, 생성, 비용 추정, 대기, 조회 계열 명령을 제공한다.
- Higgsfield 문서는 Codex 같은 에이전트에는 MCP보다 CLI 사용을 권장한다.
- Seedance 2.0은 샷당 최대 15초 수준이며 긴 영상은 여러 샷 연결로 만든다.
- Seedance는 네이티브 오디오를 생성할 수 있다.

통합 PRD 반영:

- CLI exact syntax는 추측하지 않고 Task 0에서 실제 `--help`로 고정한다.
- 본 파이프라인은 한국어 TTS와 자막 제어를 위해 native audio를 기본 제거한다.
- 효과음 유지가 필요한 경우 별도 옵션으로 덕킹 처리한다.

## 17. 운영 제약

### 17.1 비밀키와 인증

- `OPENAI_API_KEY`, `GEMINI_API_KEY`, Higgsfield 인증 토큰은 파일, 로그, markdown, evidence에 기록하지 않는다.
- API 키는 환경변수 또는 각 CLI의 공식 인증 저장소만 사용한다.
- `rg "API_KEY|SECRET|TOKEN|Bearer " projects scripts AGENTS.md README.md evidence`가 결과를 내면 릴리스 불가다.
- Higgsfield 로그인 상태는 `higgsfield auth login`과 `account` 계열 명령으로 확인하되 토큰 본문을 출력하지 않는다.

### 17.2 외부 업로드와 자료 보안

- 회사 SOP, 사고예방 가이드, 교육 PPTX는 외부 AI 서비스로 업로드될 수 있으므로 `source_policy`에 자료 등급을 둔다.
- `external_upload_allowed=false`이면 이미지/영상/TTS live 생성은 차단하고, 로컬 dry-run과 스토리보드까지만 수행한다.
- 웹 레퍼런스는 후보 URL과 썸네일 메타만 저장하고, 원본 파일 저장은 승인 후에만 한다.

### 17.3 동시성

- `scenes.json`, `approvals.json`, `.harness/self_score.json`, `.harness/turn_count`는 single-writer 파일이다.
- 스크립트는 쓰기 전 lock file을 획득해야 한다.
- lock 획득 실패 시 재시도하지 말고 명확한 오류를 반환한다.

### 17.4 실패 처리

- 네트워크 오류, OCR 실패, `soffice` 실패, `ffmpeg` 실패, Higgsfield polling timeout은 모두 `errors.jsonl`에 append-only로 기록한다.
- 자동 재시도는 무료 dry-run과 transient 네트워크 오류에만 허용한다.
- 유료 생성 실패는 자동 재시도하지 않고 사용자 승인 큐에 넣는다.

### 17.5 롤백과 재생성

- `--regenerate`는 기존 파일을 삭제하지 않는다.
- 기존 산출물은 `<name>_v<N>`으로 보존한다.
- 승인된 산출물 재생성은 승인 게이트를 reopen 상태로 바꾼 뒤에만 가능하다.
- rollback은 새 파일 생성 방식으로만 수행하고, 승인 이력은 삭제하지 않는다.

### 17.6 훅 호스트 계약

- Codex hook 이벤트 payload, exit code 의미, config 위치는 구현 첫 단계에서 실제 환경으로 검증한다.
- 훅 변경 후 검증은 같은 세션이 아니라 새 세션에서 수행한다.
- 디스크의 훅 파일 존재와 런타임 적용은 별개로 검증한다.

## 18. MVP 범위

MVP는 유료 영상 생성 전까지의 품질을 최대한 끌어올리는 것을 목표로 한다.

### MVP 포함

1. 플러그인 스캐폴딩.
2. AGENTS.md와 PLAN.md 템플릿.
3. `validate_plan.py`.
4. 프로젝트 초기화.
5. 교육자료 등록과 PPTX 렌더링.
6. 주제 후보 추출.
7. 인테이크.
8. 스타일 DNA 추출.
9. 스토리보드 생성.
10. `validate_project.py`.
11. Gate 1 승인.
12. 이미지 생성 dry-run.
13. 영상 생성 dry-run.
14. 비용 명세 생성.
15. 훅의 미승인 `--live` 차단.

### MVP 제외

1. 실제 유료 Seedance 생성.
2. 실제 TTS 라이브 생성.
3. 최종 MP4 대량 생성.
4. 웹 레퍼런스 자동 다운로드.
5. 여러 프로젝트 유형 확장.

## 19. 구현 Wave

### Wave 0: 기술 앵커 확인

- OpenAI 이미지 생성 경로 확인.
- Higgsfield CLI 설치 여부 확인.
- `higgsfield --help`, `higgsfield generate --help` 출력 저장.
- Seedance 모델명, 필수 파라미터, 업로드 방식 확인.
- ffmpeg, ffprobe, soffice, node, npm, python3, 한글 폰트 확인.
- Codex hook payload와 exit code 의미 확인.
- bootstrap mode와 protected mode 전환 조건 확인.

수용 기준:

- `evidence/task-0-tool-contracts.txt`에 실제 명령 출력이 있다.
- 확인 전에는 외부 CLI 파라미터를 코드에 하드코딩하지 않는다.

### Wave 1: 하네스 기반

- AGENTS.md 작성.
- PLAN.md 템플릿 작성.
- `validate_plan.py` 구현.
- 훅 7종 구현.
- 청정수 구역과 protected paths 구현.
- single-writer lock 정책 구현.

수용 기준:

- 종료조건 없는 PLAN.md가 거부된다.
- Gate 승인 없는 `--live`가 차단된다.
- 청정수 구역 쓰기가 차단된다.
- sentinel 없는 Stop이 조기 완료를 막는다.

### Wave 2: 데이터 계약과 프로젝트 스캐폴드

- 스키마 5종 작성.
- `validate_project.py` 구현.
- `init_project.py` 구현.
- 상태 파일과 evidence 구조 생성.
- `external_upload_allowed` 정책과 errors.jsonl 생성.

수용 기준:

- valid fixture는 PASS.
- 인용 누락, 자수 초과, 연속성 모순, 한글 이미지 프롬프트는 FAIL.

### Wave 3: 자료 수집과 기획

- `register_sources.py`.
- `render_pptx_sources.py`.
- `extract_topics.py`.
- `intake_project.py`.
- `search_references.py`.
- `extract_style_dna.py`.

수용 기준:

- 이미지 기반 PPTX도 렌더링 산출물을 가진다.
- 여러 주제 후보가 생성된다.
- 승인 없는 웹 레퍼런스 사용은 거부된다.

### Wave 4: 스토리보드와 이미지

- `plan_storyboard.py`.
- `approve_gate.py`.
- `generate_images.py`.
- `validate_images.py`.

수용 기준:

- 30초 hybrid 기본값에서 컷 수와 키프레임 수가 계산된다.
- Gate 1 전 이미지 live 생성은 차단된다.
- blocker가 있는 이미지만 선택 재생성 대상으로 표시된다.

### Wave 5: 영상, TTS, 합성, 최종 QA

- `generate_seedance.py`.
- `generate_tts.py`.
- `compose_video.py`.
- `inspect_video.py`.
- 플러그인 패키징.

수용 기준:

- Gate 2 전 영상 live 생성은 차단된다.
- 비용 명세 없는 Gate 2 승인은 거부된다.
- `inspect_video.py`가 영상 메타와 샘플 프레임을 evidence로 남긴다.
- 최종 MP4에는 한국어 폰트 기반 자막이 번인된다.

## 20. 최종 수용 기준

- 기존 특정 프로젝트 파일을 참조하지 않는다.
- 플러그인 설치 후 새 프로젝트를 생성할 수 있다.
- PLAN.md 종료조건이 없으면 실행이 거부된다.
- 교육자료에서 여러 주제 후보를 뽑고 사용자가 선택할 수 있다.
- 모든 안전 주장은 출처를 가진다.
- 스토리보드는 영상 생성 전까지 무료 루프로 수정 가능하다.
- Gate 1 전 이미지 live 생성이 차단된다.
- Gate 2 전 영상 live 생성이 차단된다.
- 비용 명세 없는 Gate 2 승인이 차단된다.
- 이미지 일관성 검증이 있다.
- 영상 프레임 샘플링 검증이 있다.
- 스토리보드/이미지/영상 3자 일치 검증이 있다.
- `--regenerate` 시 기존 산출물을 보존한다.
- 비밀키가 파일, 로그, markdown에 남지 않는다.
- dry-run 전체 체인이 통과한다.
- 실제 유료 생성은 명시 승인 후에만 가능하다.
- 외부 업로드 불가 프로젝트에서는 live 생성이 차단된다.
- single-writer 대상 파일은 lock 없이 쓰지 않는다.
- 훅 변경은 새 세션에서 검증된다.
- rollback과 regenerate는 기존 승인 이력을 삭제하지 않는다.

## 21. 최종 판단

현재 프로젝트 목적에는 **B 단독보다 A+B 통합안이 더 적합**하다.

B는 실행 하네스로는 훌륭하지만, A에 있던 이미지 검색, 프롬프트 전문성, 스토리-이미지-영상 3자 검증의 제품적 필요를 일부 축약했다. 반대로 A는 제품 요구는 잘 잡았지만 에이전트가 과분화되어 실제 구현 시 드리프트와 운영 복잡도가 커질 수 있다.

따라서 최종 PRD는 다음 문장으로 요약된다.

> 안전교육 영상 자동화는 "많은 에이전트가 알아서 만드는 시스템"이 아니라, "작은 수의 격리 에이전트와 강한 훅/스키마/게이트가 유료 생성 전 오류를 최대한 제거하는 플러그인형 하네스"로 구현한다.
