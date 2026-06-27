# 안전교육 영상 자동제작 하네스 최종 PRD

> 상태: 최종 실행 기준
> 작성일: 2026-06-10
> 플러그인 ID: `safety-video-harness`
> 표시 이름: `Safety Video Automation`

## 1. 제품 요약

`safety-video-harness`는 SOP, PPTX, PDF, DOCX, 이미지 기반 교육자료를 입력받아 한국어 안전교육 영상을 제작하기 위한 Codex 플러그인형 하네스다.

핵심 목표는 영상 생성 자체가 아니라 **유료 생성 전에 오류를 최대한 제거하는 제작 통제 시스템**을 만드는 것이다. 스토리보드는 비용 부담 없이 반복 수정하고, 이미지와 영상 생성은 승인 게이트와 비용 명세 뒤에서만 실행한다.

## 2. 핵심 원칙

- 기존 특정 샘플 프로젝트와 독립적으로 동작한다.
- 단, 개발/검증 fixture는 실제 교육자료인 `fixtures/sources/remicon-collision-guide.pptx`를 사용한다.
- 교육자료에는 여러 주제가 있을 수 있으므로 먼저 주제 후보를 추출한다.
- 사용자가 주제를 선택한 뒤에만 스토리보드를 만든다.
- 스토리보드는 무제한 수정 가능하지만, 유료 이미지/영상 생성은 승인 후에만 실행한다.
- 모든 안전 관련 문구는 교육자료, SOP, 사용자 승인 메모 중 하나로 추적 가능해야 한다.
- Codex가 MP4를 직접 이해한다고 가정하지 않는다. 영상 검증은 `ffprobe`/`ffmpeg`로 메타와 프레임을 추출한 뒤 수행한다.
- 30초는 기술 한계가 아니라 기본 비용/검수 가드레일이다.
- 하네스는 작고 명확해야 한다. 에이전트는 3개, 스킬은 6개, 훅은 7개를 기본 구조로 한다.

## 3. 사용자와 사용 시나리오

### 3.1 주요 사용자

- 워크플로우 소유자: 프로젝트 생성, 게이트 승인, 최종 결과물 검수.
- 안전교육 제작자: 스토리보드와 최종 영상을 교육자료로 사용.
- 검토자: 출처 정확성, 시각적 안전성, 최종 교육 적합성을 확인.

### 3.2 기본 시나리오

1. 사용자가 안전교육 PPTX 또는 SOP 자료를 등록한다.
2. 시스템이 자료를 렌더링하고 주제 후보를 추출한다.
3. 사용자가 제작할 주제를 선택한다.
4. 시스템이 스타일 레퍼런스 후보와 인테이크 질문을 제시한다.
5. 승인된 레퍼런스와 교육자료에서 스타일 DNA를 추출한다.
6. 스토리보드를 생성하고 출처, 컷 구성, 자막, 나레이션을 검증한다.
7. Gate 1 승인 후 키프레임 이미지를 생성한다.
8. 이미지 일관성과 스토리-이미지 일치 여부를 검증한다.
9. Gate 2 승인과 비용 명세 확인 후 Seedance 영상을 생성한다.
10. 영상 프레임을 추출해 스토리보드, 이미지, 영상의 3자 일치 여부를 검증한다.
11. TTS, 자막, ffmpeg 합성으로 최종 MP4와 검수 패키지를 만든다.

## 4. 범위

### 4.1 포함

- Codex 플러그인 스캐폴딩.
- 프로젝트 초기화.
- 교육자료 등록, 렌더링, 해시 기록.
- 이미지 기반 PPTX 대응.
- 복수 주제 후보 추출.
- 번호형 인테이크.
- 스타일 레퍼런스 검색과 승인.
- 스타일 DNA 추출.
- 출처 기반 스토리보드 생성.
- 이미지/영상 프롬프트 고도화.
- Codex 내장 `imagegen` skill/tool 기반 키프레임 이미지 생성.
- OpenAI Image API/CLI 기반 생성은 사용자가 명시 요청한 fallback으로만 둔다.
- Higgsfield CLI / Seedance 기반 영상 생성.
- 영상 프레임 샘플링 기반 검증.
- 한국어 TTS, 자막 번인, ffmpeg 합성.
- 승인 게이트, 비용 명세, dry-run, evidence 기록.

### 4.2 제외

- 승인 없는 완전 자동 게시.
- 법률 또는 SHE 전문가 검토의 대체.
- 사실적 유혈, 부상 순간, 선정적 사고 장면 생성.
- 승인 없는 웹 이미지 다운로드 및 사용.
- 루프 중 유료 이미지/영상/TTS 호출.
- 외부 업로드가 금지된 자료의 live 생성.

## 5. 하네스 아키텍처

### 5.1 레이어

| 레이어 | 책임 | 구현 |
|---|---|---|
| 실행 엔진 | 반복 실행, 지속성 | OmO `ulw-loop` 또는 수동 계속 실행 |
| 가드레일 | 방향, 차단, 검증 | `AGENTS.md`, `PLAN.md`, hooks, schemas, validators |
| 도메인 스킬 | 주제 추출, 스토리, 프롬프트, 검증 | 6개 스킬 |
| 격리 에이전트 | 생성/검증 컨텍스트 분리 | 3개 에이전트 |
| 어댑터 | 외부 도구 연결 | Codex built-in imagegen, Higgsfield CLI, Gemini TTS, ffmpeg |

### 5.2 플러그인 구조

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
    sources.schema.json
    extracted_topics.schema.json
    style_dna.schema.json
    scenes.schema.json
    approvals.schema.json
  templates/
    project/
      PLAN.md
      AGENTS.safety.md
  references/
    codex-imagegen.md
    higgsfield-cli.md
    higgsfield-seedance.md
    harness-engineering.md
```

### 5.3 부트스트랩 예외

`hooks/`, `schemas/`, `templates/`는 완성 후 청정수 구역이다. 초기 구현 Wave에서는 bootstrap mode로 생성할 수 있지만, bootstrap 종료 후에는 보호 목록에 편입한다. 이후 수정은 `.harness/retro.md` 제안과 사용자 승인 후에만 수행한다.

## 6. 에이전트와 스킬

### 6.1 에이전트 3종

| 에이전트 | 책임 |
|---|---|
| `storyteller` | 선택 주제, source facts, style DNA를 바탕으로 스토리와 씬 초안을 만든다. |
| `continuity-qa` | 스토리보드, 프롬프트, 이미지의 도메인 정합성과 시각 일관성을 검증한다. |
| `video-qa` | 영상 메타와 샘플 프레임을 분석하고 스토리보드/이미지/영상 3자 일치를 검증한다. |

규칙:

- 생성과 검증 컨텍스트는 분리한다.
- 검증 에이전트는 증거 없는 감상평을 금지한다.
- 리뷰는 점수, blocker, 근거, 수정 제안을 포함한다.

### 6.2 스킬 6종

| 스킬 | 책임 |
|---|---|
| `topic-extractor` | 교육자료에서 복수 주제 후보를 추출하고 사용자 선택용 표를 만든다. |
| `story-writer` | 안전교육용 서사 구조, 컷 분해, 나레이션 자수 제한을 적용한다. |
| `seedance-prompting` | 이미지/영상 프롬프트를 영어로 고도화하고 start/end frame 조건을 명시한다. |
| `image-consistency-check` | 인물, PPE, 장비, 배경, 위험요인, 금지 표현을 채점한다. |
| `video-inspect` | `ffprobe`, `ffmpeg`, 프레임 샘플링, 3자 일치 검증을 수행한다. |
| `style-ref-search` | 승인된 웹 검색/사용자 제공 자료에서 스타일 레퍼런스 후보를 수집한다. |

## 7. 훅 설계

| ID | 훅 | 이벤트 | 책임 |
|---|---|---|---|
| H1 | SessionStart anchor | SessionStart | `PLAN.md`, approvals, AGENTS 핵심 금지사항 주입 |
| H2 | Live generation veto | PreToolUse | Gate 승인 없는 `--live` 이미지/영상/TTS 차단 |
| H3 | Protected path veto | PreToolUse | 청정수 구역 쓰기/삭제 차단 |
| H4 | Secret veto | PreToolUse | API key, token, bearer 문자열 파일 기록 차단 |
| H5 | Schema validation feedback | PostToolUse | 스키마/상태 파일 변경 시 검증 실행 결과 주입 |
| H6 | Evidence feedback | PostToolUse | 증거 없는 완료 주장, 점수 없는 감상평 차단 피드백 |
| H7 | Stop sentinel guard | Stop | `.harness/DONE` 없으면 조기정지 차단 |

## 8. 단방향 제작 파이프라인

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

규칙:

- 이전 단계로 되돌아갈 수는 있지만 임의 단계로 점프하지 않는다.
- 유료 단계는 승인 없이 진입하지 않는다.
- 완료 주장 전 write-read-back과 evidence가 필요하다.

## 9. 비용순 검증 사다리

| 레벨 | 비용 | 내용 | 반복 정책 |
|---|---|---|---|
| L0 | 무료/초 단위 | schema, pytest, dry-run, 파일 존재 | 무제한 |
| L1 | 무료/분 단위 | 출처, 나레이션 길이, 스토리 정합, 프롬프트 누락 | 무제한 |
| L2 | 유료-저 | Codex 내장 imagegen 이미지 생성 | Gate 1 이후, 선택 재생성 |
| L3 | 유료-고 | Higgsfield CLI / Seedance 영상 생성 | Gate 2 이후, 1회 지향 |
| L4 | 사람 비용 | Gate 승인, 최종 교육자료 적합성 검수 | 80% 이후 필수 |

## 10. 프로젝트 폴더 구조

```text
projects/<slug>/
  PLAN.md
  AGENTS.md
  project_config.json
  sources/
    raw/
    rendered/
    sources.json
    extracted_topics.json
    source_facts.json
  model/
    cast/
    ppe/
  product/
    equipment/
  ref/
    candidates/
    approved/
  style/
    style_dna.json
  storyboard/
    scenes.json
    versions/
  prompts/
    image_prompts.json
    video_prompts.json
  images/
    draft/
    approved/
    rejected/
  video/
    clips/
    sampled_frames/
  audio/
  subtitles/
  output/
  qa/
    image_reviews.json
    video_reviews.json
    triad_reviews.json
  evidence/
  .harness/
    DONE
    retro.md
    self_score.json
    turn_count
    errors.jsonl
```

## 11. 데이터 계약

### 11.1 `project_config.json`

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
  "external_upload_allowed": false,
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
    "image": "codex_builtin_imagegen",
    "image_fallback": "explicit_openai_api_or_cli",
    "video": "higgsfield_cli_seedance",
    "tts": "gemini_tts",
    "compose": "ffmpeg"
  }
}
```

### 11.2 `sources.json`

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

### 11.3 `extracted_topics.json`

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

### 11.4 `scenes.json`

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

- `source_citations`는 씬마다 1개 이상이어야 한다.
- `len(narration_ko) <= duration_sec * 5`를 만족해야 한다.
- `image_prompt_en`에는 한글, 자막 생성 지시, 임의 텍스트 삽입 지시가 없어야 한다.
- 승인 상태는 enum으로만 허용한다.

### 11.5 `approvals.json`

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

## 12. 승인 게이트

### 12.1 Gate 1: Storyboard

선행 조건:

- source facts가 존재한다.
- 모든 씬에 source citation이 있다.
- 나레이션 자수 제한을 통과한다.
- 프롬프트 필수 필드가 채워져 있다.
- L0/L1 검증이 통과한다.

승인 효과:

- 이미지 생성 dry-run과 live 실행이 가능해진다.
- 승인된 스토리보드는 청정수 구역이 된다.

### 12.2 Gate 2: Image to Video

선행 조건:

- 승인된 키프레임 이미지가 있다.
- 이미지 일관성 리뷰가 통과했다.
- 스토리-이미지 일치 리뷰가 통과했다.
- Seedance 프롬프트와 start/end frame 매핑이 있다.
- 비용 명세가 있다.

승인 효과:

- Seedance live 영상 생성이 가능해진다.
- 승인된 이미지와 비용 명세는 청정수 구역이 된다.

## 13. 30초 및 컷 정책

- 기본 영상 길이: 30초.
- 30초는 기술 한계가 아니라 비용/검수 기본값이다.
- 31-60초: 확장 모드. 예상 비용과 검수 시간을 보여주고 승인받는다.
- 61초 이상: 챕터 모드. 여러 30-45초 단위 영상으로 분할한다.
- 기본 컷 길이: 5초.
- 30초 기준 기본 컷 수: 6클립.
- sliding-chain 기준 키프레임 수: `clip_count + 1`.
- independent 기준 키프레임 수: `clip_count`.
- hybrid 기준: 동일 장소/동작은 sliding, 장면 전환은 independent.

## 14. 이미지 생성 정책

이미지 생성 전:

- Gate 1이 승인되어야 한다.
- 이미지 프롬프트는 영어로 작성한다.
- 프롬프트는 PPE, 장비, 위험요인, 카메라, 조명, 배경, negative constraints를 포함해야 한다.
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

## 15. 영상 생성 정책

영상 생성 전:

- Gate 2가 승인되어야 한다.
- 승인 레코드에는 비용 명세가 있어야 한다.
- `--live` 명령은 Gate 2 승인 없이는 훅에서 차단한다.
- Higgsfield CLI 실제 파라미터는 구현 첫 단계에서 `higgsfield --help`와 공식 문서로 고정한다.

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
- `video-qa`가 프레임과 승인 이미지, `scenes.json`을 대조한다.
- 영상이 멋있어도 교육 목표와 다르면 reject한다.

## 16. 공식 문서 기준 기술 앵커

### 16.1 Codex 내장 imagegen

- 기본 이미지 생성 경로는 Codex 내장 `imagegen` skill/tool이다.
- 이 경로는 사용자가 별도 `OPENAI_API_KEY`를 제공하지 않아도 된다.
- 플러그인 CLI가 직접 내장 도구를 호출하는 것이 아니라, `image_prompts.json`과 `imagegen_jobs.json`을 만들고 Codex 에이전트가 `imagegen` skill을 사용해 이미지를 생성한 뒤 프로젝트 폴더에 저장한다.
- 생성된 이미지는 `$CODEX_HOME/generated_images/...`에 남겨두지 않고 `projects/<slug>/images/draft/scNN_vNNN.png`로 이동 또는 복사한다.
- OpenAI Image API 또는 CLI fallback은 사용자가 명시적으로 API/CLI 경로를 요청한 경우에만 사용한다.
- 반복 캐릭터/장비 일관성, 정밀 구도, 텍스트 렌더링은 모델에 맡기지 않고 reference profile, prompt contract, 이미지 QA, 선택 재생성으로 관리한다.

반영:

- `generate_images.py --dry-run`은 Codex `imagegen`용 job spec을 생성한다.
- 실제 이미지 생성 단계에서는 Codex 에이전트가 `imagegen` skill을 호출한다.
- live 이미지 생성에도 Gate 1, `external_upload_allowed`, 버전 보존, evidence 기록이 필요하다.

### 16.2 Higgsfield CLI / Seedance

- CLI 설치는 `npm install -g @higgsfield/cli` 경로를 우선 확인한다.
- 인증은 `higgsfield auth login` 경로를 우선 확인한다.
- Codex 같은 에이전트 실행에서는 CLI를 1차 경로로 둔다.
- MCP는 선택 어댑터로만 둔다.
- Seedance는 샷/클립 단위로 생성하고, 긴 영상은 여러 클립 연결로 만든다.
- Seedance native audio는 기본 제거하고, 한국어 TTS와 자막을 별도 합성한다.

## 17. 운영 제약

### 17.1 비밀키와 인증

- `OPENAI_API_KEY`, `GEMINI_API_KEY`, Higgsfield 인증 토큰은 파일, 로그, markdown, evidence에 기록하지 않는다.
- API 키는 환경변수 또는 각 CLI의 공식 인증 저장소만 사용한다.
- `rg "API_KEY|SECRET|TOKEN|Bearer " projects scripts AGENTS.md README.md evidence`가 결과를 내면 릴리스 불가다.

### 17.2 외부 업로드

- 회사 SOP, 사고예방 가이드, 교육 PPTX는 외부 AI 서비스로 업로드될 수 있으므로 `external_upload_allowed`를 둔다.
- `external_upload_allowed=false`이면 이미지/영상/TTS live 생성은 차단하고, 로컬 dry-run과 스토리보드까지만 수행한다.
- 웹 레퍼런스는 후보 URL과 메타만 저장하고, 원본 파일 저장은 승인 후에만 한다.

### 17.3 동시성

- `scenes.json`, `approvals.json`, `.harness/self_score.json`, `.harness/turn_count`는 single-writer 파일이다.
- 스크립트는 쓰기 전 lock file을 획득해야 한다.
- lock 획득 실패 시 명확한 오류를 반환한다.

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

## 18. MVP

MVP는 유료 영상 생성 전까지의 품질을 최대한 끌어올리는 것을 목표로 한다.

### 18.1 MVP 포함

1. 플러그인 스캐폴딩.
2. `AGENTS.md`와 `PLAN.md` 템플릿.
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

### 18.2 MVP 제외

1. 실제 유료 Seedance 생성.
2. 실제 TTS live 생성.
3. 최종 MP4 대량 생성.
4. 웹 레퍼런스 자동 다운로드.
5. 여러 프로젝트 유형 확장.

## 19. 구현 Wave

### Wave 0: 기술 앵커 확인

- Codex 내장 `imagegen` skill/tool 실행 경로 확인.
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

- `AGENTS.md` 작성.
- `PLAN.md` 템플릿 작성.
- `validate_plan.py` 구현.
- 훅 7종 구현.
- 청정수 구역과 protected paths 구현.
- single-writer lock 정책 구현.

수용 기준:

- 종료조건 없는 `PLAN.md`가 거부된다.
- Gate 승인 없는 `--live`가 차단된다.
- 청정수 구역 쓰기가 차단된다.
- sentinel 없는 Stop이 조기 완료를 막는다.

### Wave 2: 데이터 계약과 프로젝트 스캐폴드

- 스키마 작성.
- `validate_project.py` 구현.
- `init_project.py` 구현.
- 상태 파일과 evidence 구조 생성.
- `external_upload_allowed` 정책과 `errors.jsonl` 생성.

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
- 실제 기준 PPTX fixture를 작업폴더에 보관하고, 해당 파일로 주제 추출과 스토리보드 생성을 검증한다.
- fixture 기반 테스트는 레미콘, 충돌, 사각지대, 신호수, BCT, 덤프트럭, 후진이 산출물에 반영되는지 확인한다.
- 플러그인 설치 후 새 프로젝트를 생성할 수 있다.
- `PLAN.md` 종료조건이 없으면 실행이 거부된다.
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

## 21. 최종 방향

안전교육 영상 자동화는 많은 에이전트가 자유롭게 판단하는 시스템이 아니라, 작은 수의 격리 에이전트와 강한 훅, 스키마, 게이트가 유료 생성 전 오류를 제거하는 플러그인형 하네스로 구현한다.
