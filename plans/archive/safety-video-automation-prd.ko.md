# 안전교육 영상 자동제작 플러그인 PRD

## 0. 결론

이 프로젝트는 기존에 진행하던 특정 안전영상 샘플과 무관한 **독립 플러그인형 하네스**다.
목표는 사용자가 교육자료를 올리면 AI가 교육주제 후보를 뽑고, 사용자가 주제를 고르면
스토리보드를 먼저 충분히 만들고 검증한 뒤, 신중하게 이미지와 영상을 생성하는 것이다.

핵심 방향은 다음과 같다.

- **형태**: Codex 플러그인.
- **구성**: skills, hooks, scripts, optional MCP adapter, project templates.
- **이미지 생성**: Codex 내장 이미지 생성 또는 OpenAI Image API.
- **영상 생성**: Higgsfield CLI의 Seedance 2.0.
- **영상 길이**: 30초는 기술적 한계가 아니라 기본 비용/품질 가드레일이다.
- **제작 순서**: 교육자료 분석 -> 주제 선택 -> 스타일/레퍼런스 조사 -> 스토리보드 -> 이미지 생성 -> 이미지 검증 -> 영상 생성 -> 영상 검증 -> 최종 합성.
- **검증 철학**: 스토리보드는 무제한 반복 가능하지만, 영상 생성은 유료/느림/수정비용이 크므로 게이트를 강하게 둔다.
- **하네스 원칙**: 지속과 수렴을 분리하고, 단방향 파이프라인, 비용순 검증 사다리, 파일 상태 저장, 훅 기반 veto/검증/정지를 사용한다.

## 1. 배경과 문제

안전교육 영상은 일반 홍보영상보다 실패 비용이 크다.
장면이 조금 어색한 것은 수정할 수 있지만, 교육자료의 주제나 위험요인이 잘못 해석되거나
PPE, 장비, 작업순서, 접근금지 구역이 틀리면 교육자료로 사용할 수 없다.

현재 AI 영상 제작에서 반복적으로 생기는 문제는 다음이다.

- 교육자료 안에 여러 주제가 있는데 AI가 하나로 뭉개서 처리한다.
- 이미지 생성 프롬프트가 부실해 원하는 장면이 나오지 않는다.
- 여러 컷의 인물, 장비, 배경, PPE가 제각각 달라진다.
- 스토리보드와 생성 이미지가 다르다.
- 생성 영상이 스토리보드 이미지와 다르다.
- 영상 결과물을 Codex가 직접 이해하지 못하면 피드백 루프가 끊긴다.
- 영상 생성은 비용이 들기 때문에 무작정 반복하면 예산을 태운다.
- 하네스가 없으면 에이전트가 중간에 멈추거나, 엉뚱한 작업을 추가하거나, 오래된 상태를 덮어쓴다.

따라서 이 PRD는 단순한 스크립트 목록이 아니라 **영상 제작 전용 하네스**를 정의한다.

## 2. 제품 목표

사용자가 교육자료를 넣으면 다음을 수행하는 Codex 플러그인을 만든다.

1. 교육자료에서 여러 교육주제 후보를 추출한다.
2. 사용자가 주제를 선택하게 한다.
3. 선택한 주제에 맞는 스타일 이미지와 안전교육 영상 레퍼런스를 찾는다.
4. 레퍼런스에서 스타일 DNA를 추출한다.
5. 전문 스토리 에이전트가 교육용 스토리보드를 만든다.
6. 프롬프트 전문 에이전트가 이미지/영상 프롬프트를 고도화한다.
7. 스토리보드 검증 에이전트가 교육자료, 주제, 컷 구성, 자막, 나레이션을 검토한다.
8. Codex 이미지 생성으로 스토리보드 이미지를 만든다.
9. 이미지 일관성 검증 에이전트가 인물, PPE, 장비, 배경, 구도, 위험요인 표현을 점검한다.
10. 이미지-스토리 일치 검증 에이전트가 각 이미지가 스토리보드 컷 의도와 맞는지 검토한다.
11. 승인된 이미지만 Seedance 영상 생성으로 넘긴다.
12. 영상 결과물을 프레임 샘플링해 다시 인식하고, 스토리보드/이미지/영상의 3자 일치 여부를 검증한다.
13. 필요하면 영상 생성 전 단계로 되돌아가되, 유료 영상 재생성은 명시 승인 후에만 한다.

## 3. 비목표

- 풀오토 영상 생성.
- 교육자료 출처 없는 안전 주장 생성.
- 사고 충돌/부상/유혈을 사실적으로 묘사하는 영상.
- 영상 생성 비용을 무시한 무제한 재시도.
- 웹에서 찾은 이미지의 무단 상업 사용.
- 기존 특정 프로젝트 파일을 전제로 하는 구현.
- 단일 거대 프롬프트 하나로 모든 작업을 처리하는 구조.

## 4. 30초 정책 정정

### 4.1 30초는 기술적 한계가 아니다

30초 초과 영상이 기술적으로 불가능한 것은 아니다.
Higgsfield의 Seedance 2.0 안내 기준으로 한 번의 생성은 **클립/샷 단위 최대 15초**에 가깝고,
긴 영상은 여러 클립을 연결해 만들 수 있다.

따라서 제한은 다음처럼 정의해야 한다.

| 구간 | 정책 | 이유 |
|---|---|---|
| 0-30초 | 기본 권장 | 비용, 검수, 메시지 집중도 관리 |
| 31-60초 | 확장 모드 | 컷 수와 비용 추정 후 추가 승인 |
| 61-180초 | 챕터 모드 | 여러 30-45초 챕터로 분할 제작 |
| 180초 초과 | 코스/시리즈 모드 | 단일 영상이 아니라 교육 모듈 묶음으로 관리 |

### 4.2 새 기본값

- 기본 영상 길이: 30초.
- 기본 컷 길이: 4-6초.
- 기본 컷 수: `ceil(target_seconds / seconds_per_clip)`.
- 슬라이딩 체인 사용 시 키프레임 수: `clip_count + 1`.
- 독립 컷 사용 시 키프레임 수: `clip_count`.
- 30초 초과는 금지가 아니라 **비용/검수 게이트 강화**다.

## 5. 플러그인 제품 구조

플러그인 이름 후보:

```text
safety-video-harness
```

목표 디렉토리:

```text
safety-video-harness/
  .codex-plugin/
    plugin.json
  skills/
    source-topic-extractor/
      SKILL.md
    visual-reference-researcher/
      SKILL.md
    style-dna-extractor/
      SKILL.md
    storyboard-writer/
      SKILL.md
    prompt-director/
      SKILL.md
    image-consistency-reviewer/
      SKILL.md
    story-image-alignment-reviewer/
      SKILL.md
    video-frame-analyzer/
      SKILL.md
    triad-alignment-reviewer/
      SKILL.md
    ralph-quality-loop/
      SKILL.md
  hooks/
    session-start-anchor.py
    pretooluse-veto.py
    posttooluse-quality-feedback.py
    stop-loop-guard.py
  scripts/
    init_project.py
    extract_topics.py
    search_references.py
    extract_style_dna.py
    plan_storyboard.py
    validate_storyboard.py
    build_image_prompts.py
    validate_images.py
    sample_video_frames.py
    validate_video_alignment.py
    ralph_loop.py
  templates/
    project/
    AGENTS.safety-video.md
    project_config.schema.json
    topics.schema.json
    storyboard.schema.json
    visual_references.schema.json
    image_reviews.schema.json
    video_reviews.schema.json
  references/
    openai-image-generation.md
    higgsfield-seedance.md
    harness-engineering.md
```

## 6. 외부·내부 레퍼런스

### 6.1 공식 OpenAI/Codex 레퍼런스

- Codex CLI image generation:
  - Codex CLI에서 이미지 생성/편집 가능.
  - 레퍼런스 이미지를 첨부해 기존 자산을 변형하거나 확장 가능.
  - 내장 이미지 생성은 `gpt-image-2`를 사용한다.
  - 대량 생성은 `OPENAI_API_KEY`와 API 경로가 더 적합할 수 있다.
  - 출처: `https://developers.openai.com/codex/cli/features#image-generation`
- OpenAI Image generation guide:
  - `gpt-image-2`는 이미지 생성과 편집을 지원한다.
  - 여러 이미지를 레퍼런스로 넣어 새 이미지를 생성할 수 있다.
  - 출력 크기, 품질, 포맷을 조정할 수 있다.
  - 한계로 지연, 텍스트 렌더링, 반복 캐릭터/브랜드 일관성, 정밀 구도 제어 문제가 명시되어 있다.
  - 출처: `https://developers.openai.com/api/docs/guides/image-generation`
- OpenAI video understanding cookbook:
  - 모델이 비디오 파일을 직접 입력으로 받지 않는 경우에도 OpenCV/ffmpeg로 프레임을 추출해 비전 입력으로 분석할 수 있다.
  - 출처: `https://developers.openai.com/cookbook/examples/gpt_with_vision_for_video_understanding`

### 6.2 Higgsfield/Seedance 레퍼런스

- Higgsfield CLI:
  - 설치: `npm install -g @higgsfield/cli`
  - 로그인: `higgsfield auth login`
  - CLI가 인증, 업로드, 폴링을 처리한다.
  - 명령군: `auth`, `account`, `workspace`, `model`, `generate`, `upload`, `soul-id`.
  - 출처: `https://higgsfield.ai/cli`
- Seedance 2.0:
  - 이미지 레퍼런스를 받아 영상 생성 가능.
  - 클립은 최대 15초 단위에 가깝다.
  - 긴 영상은 여러 샷/클립 연결 방식으로 구성한다.
  - 여러 이미지, 비디오, 오디오, 텍스트를 입력으로 받을 수 있다.
  - 출처: `https://higgsfield.ai/seedance/2.0`
- Higgsfield MCP:
  - MCP로 연결할 수 있지만, 이 플러그인의 1차 실행 경로는 Codex와 잘 맞는 CLI다.
  - MCP는 향후 선택 어댑터로 둔다.
  - 출처: `https://higgsfield.ai/mcp`

### 6.3 하네스 엔지니어링 레퍼런스

반영한 내부 문서:

- `/Users/hatae/Documents/Obsidian/obsidian-vault/20. Literature Notes/25. AI 학습/25-2. 패스트캠퍼스/하네스엔지니어링(오프라인)/하네스 엔지니어링 일반론 정리.md`
- `하네스 엔지니어링 강의 1주차(최종본).md`
- `하네스 엔지니어링 강의 2주차(최종본).md`
- `polysona-harness-case-study (1).md`
- `win-hooks-harness-case-study.md`

핵심 반영 원칙:

- 지속과 수렴은 다르다.
- SessionStart는 앵커, PreToolUse는 veto, PostToolUse는 검증, Stop은 지속이다.
- 단방향 파이프라인으로 드리프트 면적을 줄인다.
- 상태는 파일과 git에 둔다.
- 존재, 정확, 동작은 다르며, 검증은 실행 증거까지 올라가야 한다.
- 감정 언어는 조향, 수치 언어는 고정 장치다.
- 하네스는 작고 명확해야 하며, 스킬 인플레이션을 피해야 한다.

## 7. 단방향 제작 파이프라인

```text
자료 등록
  -> 주제 후보 추출
  -> 사용자 주제 선택
  -> 레퍼런스 조사
  -> 스타일 DNA 추출
  -> 스토리보드 작성
  -> 스토리보드 검증
  -> 이미지 프롬프트 고도화
  -> Codex 이미지 생성
  -> 이미지 일관성 검증
  -> 스토리-이미지 일치 검증
  -> 영상 생성 승인
  -> Higgsfield/Seedance 영상 생성
  -> 영상 프레임 샘플링
  -> 스토리보드/이미지/영상 3자 일치 검증
  -> 자막/나레이션/합성
  -> 최종 검수 패키지
```

이 순서는 반드시 단방향이다.
이전 단계로 돌아갈 수는 있지만, 임의 단계로 점프하지 않는다.

## 8. 프로젝트 작업 폴더

프로젝트 하나는 다음 구조를 가진다.

```text
projects/<project-slug>/
  AGENTS.md
  project_config.json
  sources/
    raw/
    rendered_pages/
    extracted_topics.json
    source_facts.json
  references/
    search_queries.json
    candidates/
    approved/
    rejected/
  style/
    style_dna.json
  storyboard/
    storyboard.json
    versions/
  prompts/
    image_prompts.json
    video_prompts.json
  images/
    draft/
    approved/
    rejected/
    reviews.json
  video/
    clips/
    sampled_frames/
    reviews.json
  audio/
  subtitles/
  output/
  evidence/
  state/
    pipeline_state.json
    ralph_loop.jsonl
    decisions.jsonl
```

## 9. 핵심 데이터 계약

### 9.1 `project_config.json`

```json
{
  "schema_version": "1.0",
  "project_type": "safety_training_video",
  "project_name": "",
  "target_audience": "",
  "target_duration_sec": 30,
  "duration_policy": "default_30_extend_with_approval",
  "aspect_ratio": "16:9",
  "resolution": "1080p",
  "style_mode": "auto_from_references",
  "video_generation_policy": "storyboard_first_video_after_gate",
  "live_generation_requires_approval": true
}
```

### 9.2 `extracted_topics.json`

```json
{
  "source_ids": [],
  "topics": [
    {
      "topic_id": "topic-001",
      "title_ko": "",
      "risk_type": "",
      "target_worker": "",
      "why_it_matters": "",
      "source_citations": [
        {
          "source_id": "",
          "page_or_slide": 1,
          "evidence_text_or_visual": ""
        }
      ],
      "video_fit_score": 0,
      "priority_score": 0,
      "recommended": false
    }
  ]
}
```

### 9.3 `storyboard.json`

```json
{
  "storyboard_version": 1,
  "selected_topic_id": "",
  "target_duration_sec": 30,
  "chain_policy": "hybrid",
  "scenes": [
    {
      "scene_id": "sc01",
      "duration_sec": 5,
      "educational_goal_ko": "",
      "visual_action_ko": "",
      "caption_ko": "",
      "narration_ko": "",
      "image_prompt_en": "",
      "video_prompt_en": "",
      "required_assets": [],
      "safety_claims": [],
      "source_citations": [],
      "continuity_constraints": {
        "character_ids": [],
        "equipment_ids": [],
        "ppe_requirements": [],
        "background_id": ""
      },
      "approval_state": "draft"
    }
  ]
}
```

### 9.4 `image_reviews.json`

```json
{
  "image_id": "",
  "scene_id": "",
  "story_match_score": 0,
  "character_consistency_score": 0,
  "ppe_consistency_score": 0,
  "equipment_consistency_score": 0,
  "background_consistency_score": 0,
  "safety_accuracy_score": 0,
  "blocking_issues": [],
  "regeneration_prompt_delta": "",
  "decision": "approve|revise|reject"
}
```

### 9.5 `video_reviews.json`

```json
{
  "clip_id": "",
  "scene_id": "",
  "sampled_frames": [],
  "matches_storyboard": false,
  "matches_approved_image": false,
  "motion_matches_prompt": false,
  "safety_claims_preserved": false,
  "blocking_issues": [],
  "regeneration_cost_warning": "",
  "decision": "approve|revise_prompt|regenerate_with_approval|reject"
}
```

## 10. 필수 에이전트/스킬

### 10.1 교육자료 주제 추출 에이전트

역할:

- PPTX, PDF, DOCX, 이미지 슬라이드, 텍스트 자료를 읽는다.
- 자료 안의 교육주제를 여러 개로 분해한다.
- 각 주제마다 위험유형, 대상자, 핵심 메시지, 영상화 적합성, 출처를 붙인다.
- 하나의 자료에 하나의 주제만 있다고 가정하지 않는다.

출력:

- `extracted_topics.json`
- 사용자에게 제시할 주제 후보 표.

### 10.2 이미지/스타일 레퍼런스 조사 에이전트

역할:

- 사용자가 원하는 스타일과 관련된 이미지/영상 사례를 찾는다.
- 예: "애니메이션 안전교육 영상"이면 실제 애니메이션 안전교육 사례, 산업안전 애니메이션, OSHA/Napo류 교육영상 스타일 등을 찾는다.
- 검색어를 한국어/영어로 확장한다.
- 저작권/사용가능성/회사자료 여부를 표시한다.
- 자동 사용이 아니라 **후보 제시 후 승인**을 요구한다.

출력:

- `references/search_queries.json`
- `references/candidates/*.json`
- 승인된 레퍼런스만 `references/approved/`로 이동.

### 10.3 스타일 DNA 추출 에이전트

역할:

- 승인된 레퍼런스 이미지/영상에서 공통 스타일을 추출한다.
- 색감, 질감, 카메라, 캐릭터 비율, 배경 단순도, 자막 방식, 위험요인 표현 방식을 구조화한다.
- 교육자료 슬라이드의 도식/색상도 함께 반영한다.

출력:

- `style/style_dna.json`
- 이미지 프롬프트용 `prompt_style_suffix_en`.
- 영상 프롬프트용 `motion_style_suffix_en`.

### 10.4 스토리 전문 에이전트

역할:

- 선택된 교육주제로 교육용 스토리 구조를 만든다.
- 스토리는 오락적 반전보다 학습 목표, 위험 인지, 안전 행동 전환을 우선한다.
- 초반 3초 hook, 위험상황, 잘못된 행동, 올바른 행동, 요약 메시지를 설계한다.
- 영상 길이에 맞춰 컷 수를 계산한다.
- 영상 생성 전까지 스토리보드는 무제한 수정 가능해야 한다.

출력:

- `storyboard/storyboard.json`
- 컷별 자막, 나레이션, 이미지 프롬프트 초안, 영상 프롬프트 초안.

### 10.5 프롬프트 디렉터 에이전트

역할:

- 이미지 프롬프트를 매우 구체적으로 고도화한다.
- 인물의 PPE, 위치, 자세, 손동작, 장비 위치, 카메라 앵글, 배경, 위험요인, 금지 요소를 명시한다.
- Seedance용 영상 프롬프트에는 카메라 이동, 피사체 움직임, 시간 흐름, start/end frame 연결 조건을 명시한다.
- OpenAI 이미지 생성 가이드와 Seedance 공식 가이드를 references로 사용한다.

프롬프트 필수 구성:

```text
Subject
Scene
Safety context
Camera
Lighting
Composition
Character/PPE continuity
Equipment continuity
Action
Negative constraints
Style DNA suffix
```

### 10.6 이미지 일관성 검증 에이전트

역할:

- 여러 이미지가 같은 영상의 컷으로 보이는지 검증한다.
- 인물 얼굴/체형/PPE, 장비 색상/형태, 배경, 자막 없음 여부, 스타일, 카메라 톤을 점검한다.
- 불일치가 있으면 단순 비판이 아니라 재생성 프롬프트 delta를 제공한다.

차단 기준:

- PPE 색상/종류가 바뀜.
- 작업자 수가 스토리보드와 다름.
- 장비 종류가 바뀜.
- 위험요인이 사라짐.
- 금지한 부상/충돌 묘사가 들어감.

### 10.7 스토리-이미지 일치 검증 에이전트

역할:

- 각 이미지가 해당 컷의 교육 목표와 맞는지 검토한다.
- 스토리보드의 "무슨 일이 일어나야 하는가"와 이미지의 실제 내용이 일치하는지 본다.
- 이미지가 멋있어도 교육목표와 다르면 reject한다.

### 10.8 영상 인식 에이전트

역할:

- 생성된 MP4를 직접 한 덩어리로 믿지 않는다.
- `ffmpeg` 또는 OpenCV로 프레임을 샘플링한다.
- 시작, 중간, 끝 프레임을 추출한다.
- 추출 프레임을 비전 모델 또는 Codex 이미지 인식 루프로 분석한다.
- 영상 안의 인물, PPE, 장비, 행동, 위험요인, 자막 오류를 기록한다.

기술 가능성:

- Codex가 비디오 파일 자체를 항상 직접 이해한다고 가정하지 않는다.
- 대신 `sample_video_frames.py`가 영상을 이미지 프레임으로 바꾼다.
- 이미지 프레임은 비전 모델/이미지 검토 루프에 넣을 수 있다.
- 이 방식은 OpenAI의 video understanding cookbook에서 설명하는 프레임 추출 접근과 일치한다.

### 10.9 스토리보드-이미지-영상 3자 일치 검증 에이전트

역할:

- 최종적으로 세 가지가 맞는지 검증한다.
  - 원래 스토리보드
  - 승인된 이미지
  - 생성된 영상 프레임
- 셋 중 하나라도 다르면 영상 재생성 또는 이전 단계 수정을 제안한다.

검증 축:

| 축 | 설명 | 통과 기준 |
|---|---|---|
| 의미 | 교육 목표와 장면 의미 | 4/5 이상 |
| 시각 | 이미지와 영상 프레임 일치 | 4/5 이상 |
| 연속성 | 인물/PPE/장비/배경 유지 | 4/5 이상 |
| 안전성 | 안전 사실과 금지 표현 준수 | 5/5 |
| 사용성 | 교육자료로 이해 가능 | 4/5 이상 |

### 10.10 Ralph 품질 루프 스킬

역할:

- 계획 실행 또는 산출물 고도화 시 20회 루프를 돌린다.
- 단순 반복이 아니라 매 회차마다 감정 언어와 수치 언어를 함께 주입해 보완점을 강제로 찾는다.
- 루프 결과는 `state/ralph_loop.jsonl`에 append-only로 저장한다.

Ralph Loop 1회 구조:

```text
R - Review: 현재 산출물에서 가장 불안하고 어색한 지점을 찾는다.
A - Analyze: 0-5 점수로 문제 심각도와 근거를 매긴다.
L - Locate: 어느 파일/컷/프롬프트/검증 단계가 원인인지 특정한다.
P - Patch: 수정안을 낸다. 영상 재생성이 필요한 수정은 별도 승인으로 분리한다.
H - Harden: 같은 문제가 재발하지 않도록 스키마, 훅, 체크리스트, 테스트를 강화한다.
```

감정 언어 예시:

- "이 장면은 교육자료로 쓰기에는 불안하다."
- "현장 작업자가 보면 어색하다고 느낄 가능성이 높다."
- "이 프롬프트는 모델에게 너무 많은 빈칸을 남긴다."
- "영상 생성 비용을 쓰기 전에 여기서 반드시 잡아야 한다."

수치 언어 예시:

- `story_match_score: 3/5`
- `ppe_consistency_score: 2/5`
- `video_regeneration_risk: 4/5`
- `cost_risk: high`
- `approval_readiness: 71/100`

루프 종료 조건:

- 정확히 20회 실행한다.
- 단, 안전성 5/5 미만인 blocker가 있으면 20회 이후에도 완료로 보지 않는다.
- 영상 생성이 필요한 수정은 자동 실행하지 않고 사용자 승인 큐에 넣는다.

## 11. 훅 설계

### 11.1 SessionStart 앵커

목적:

- 미션, 금지사항, 현재 pipeline_state, 마지막 승인 게이트를 세션 시작마다 주입한다.
- 드리프트를 막는다.

주입 내용:

- 이 프로젝트는 안전교육 영상 플러그인이다.
- 기존 특정 샘플 프로젝트를 전제로 하지 않는다.
- 스토리보드 먼저, 영상은 승인 후.
- 출처 없는 안전 주장 금지.
- 영상 생성은 유료/고비용이므로 승인 없이는 실행 금지.
- 현재 단계와 다음 단계.

### 11.2 PreToolUse veto

목적:

- 파괴적 쓰기와 비용 발생 명령을 사전에 차단한다.

차단 조건:

- 승인 전 영상 생성 명령 실행.
- 승인된 이미지/영상 덮어쓰기.
- `state/*.jsonl` append-only 파일을 truncate.
- 출처 없는 안전 주장으로 `storyboard.json` 승인 상태 변경.
- 비밀키를 markdown/json/log에 쓰려는 시도.
- 사용자 승인 없는 웹 이미지 사용.

### 11.3 PostToolUse 품질 피드백

목적:

- 생성 직후 다음 턴에 검증 피드백을 주입한다.

감지 조건:

- "완벽", "확실", "문제 없음"처럼 근거 없는 과신 표현.
- evidence 파일 없이 완료 주장.
- 점수 없는 감상평.
- 이미지/영상 생성 후 리뷰 파일 누락.
- 스토리보드와 산출물 경로 불일치.

### 11.4 Stop 루프 가드

목적:

- 조기정지를 막고 완료 조건을 재검증한다.

Stop 차단 조건:

- pipeline_state가 `complete`가 아님.
- 현재 단계의 required evidence가 없음.
- Ralph Loop가 20회 미만.
- Gate 1/2/3 중 필요한 게이트가 승인되지 않음.
- 영상 생성 후 프레임 샘플링 리뷰가 없음.

## 12. 게이트 정책

### Gate A: 주제 선택 게이트

입력:

- 교육자료.
- 추출된 주제 후보.

사용자 승인:

- 어떤 주제로 만들지 선택.
- 여러 주제를 시리즈로 만들지 여부 선택.

### Gate B: 스토리보드 승인 게이트

입력:

- `storyboard.json`
- 출처 인용.
- 컷별 자막/나레이션.
- 이미지/영상 프롬프트 초안.

통과 조건:

- 모든 안전 주장이 출처를 가진다.
- 컷 순서가 교육 논리와 맞다.
- 유혈/충돌 묘사가 없다.
- 영상 생성 전 단계로 충분하다.

### Gate C: 이미지 승인 게이트

입력:

- 생성된 스토리보드 이미지.
- 이미지 일관성 리뷰.
- 스토리-이미지 일치 리뷰.

통과 조건:

- 모든 승인 이미지가 scene_id와 매핑된다.
- 불일치 blocker가 없다.
- 영상 프롬프트가 승인 이미지 기준으로 보정되어 있다.

### Gate D: 영상 생성 승인 게이트

입력:

- 승인 이미지.
- 최종 Seedance 프롬프트.
- 예상 클립 수.
- 예상 비용/크레딧.
- 재생성 리스크.

통과 조건:

- 사용자가 명시적으로 영상 생성을 승인한다.
- 30초 초과 시 추가 비용/검수 경고를 확인한다.

### Gate E: 영상-스토리 일치 게이트

입력:

- 생성된 영상.
- 샘플링 프레임.
- 영상 리뷰.
- 3자 일치 리뷰.

통과 조건:

- 영상이 스토리보드 및 승인 이미지와 맞는다.
- 안전상 blocker가 없다.
- 최종 합성으로 넘어갈 수 있다.

## 13. 이미지 검색 정책

이미지 검색은 자동 사용이 아니라 **레퍼런스 후보 수집**이다.

절차:

1. 사용자가 원하는 스타일을 묻는다.
2. 교육자료 주제에 맞는 검색어를 생성한다.
3. 한국어/영어 검색어를 모두 만든다.
4. 웹 검색, 이미지 검색, 공개 안전교육 영상 사례를 찾는다.
5. 후보를 저장한다.
6. 저작권/출처/사용가능성/민감정보를 표시한다.
7. 사용자가 승인한 것만 스타일 DNA에 반영한다.

검색어 예시:

```text
animated safety training video industrial accident prevention
construction safety animation near miss training
forklift blind spot safety training animation
Napo safety animation construction vehicle
산업안전 애니메이션 교육 영상
건설장비 협착 사고 예방 교육 애니메이션
```

## 14. 프롬프트 품질 정책

이미지 프롬프트는 짧으면 실패한다.
프롬프트 디렉터는 다음을 반드시 채운다.

```text
1. Scene purpose
2. Main subject
3. Worker count
4. PPE details
5. Equipment identity
6. Spatial relationship
7. Hazard location
8. Safe/unsafe action
9. Camera angle
10. Lighting
11. Background
12. Style DNA
13. Negative constraints
14. No text unless explicitly requested
15. Continuity anchors
```

영상 프롬프트는 추가로 다음을 포함한다.

```text
1. Start frame role
2. End frame role
3. Camera movement
4. Subject motion
5. Timing
6. Transition intention
7. What must remain unchanged
8. What must not appear
```

## 15. 영상 인식과 피드백 루프

영상 결과물 인식은 다음 방식으로 구현한다.

1. `ffprobe`로 길이, fps, 해상도 확인.
2. `ffmpeg`로 각 클립에서 시작/중간/끝 프레임 추출.
3. 긴 클립은 1초 또는 2초 간격으로 추가 샘플링.
4. 프레임 이미지를 이미지 검증 에이전트에 전달.
5. 각 프레임을 storyboard scene과 비교한다.
6. 움직임 문제는 프레임 차이와 영상 프롬프트를 같이 보고 판단한다.
7. 결과를 `video/reviews.json`에 저장한다.

한계:

- 프레임 샘플링은 모든 순간을 보지는 못한다.
- 중요한 안전 동작이 중간에만 잠깐 틀어질 수 있다.
- 따라서 최종 영상은 사람 검수 게이트를 반드시 둔다.

## 16. 남의 플러그인/스킬 활용 정책

가능하면 이미 있는 플러그인/스킬을 사용한다.

우선 활용 대상:

- `imagegen`: Codex 이미지 생성 또는 이미지 수정.
- `openai-docs`: OpenAI 공식 문서 확인.
- `plugin-creator`: Codex 플러그인 스캐폴딩.
- `pdf`, `doc`: 교육자료 추출/렌더링.
- `playwright`: 웹 레퍼런스 조사 또는 결과 UI 검증.
- `omo:review-work`: 큰 구현 후 외부 검증.
- `omo:ulw-plan`: 큰 설계 변경 전 계획화.
- `superpowers:test-driven-development`: 구현 시 TDD.
- `superpowers:verification-before-completion`: 완료 주장 전 검증.

직접 만들 대상:

- 안전교육 주제 추출.
- 안전영상 스토리보드 작성.
- 이미지 일관성 검증.
- 스토리-이미지 일치 검증.
- 영상 프레임 분석.
- 3자 일치 검증.
- Ralph 품질 루프.

## 17. 하네스 상태 저장

세션이 중간에 끊겨도 이어받을 수 있도록 상태는 파일에 둔다.

필수 상태 파일:

```text
state/pipeline_state.json
state/ralph_loop.jsonl
state/decisions.jsonl
state/gates.json
state/cost_estimates.jsonl
state/errors.jsonl
```

원칙:

- `.jsonl`은 append-only.
- 승인 상태는 명시적 timestamp와 승인자를 가진다.
- 영상 생성 관련 cost estimate는 삭제하지 않는다.
- 실패도 기록한다.
- 성공한 척하지 않는다.

## 18. 비용순 검증 사다리

검증은 싼 것부터 비싼 것 순서로 진행한다.

| 단계 | 검증 | 비용 | 예 |
|---|---|---|---|
| 1 | 정적 구조 검증 | 낮음 | JSON schema, 파일 존재, 출처 필드 |
| 2 | 텍스트/스토리 검증 | 낮음 | 주제-스토리-출처 일치 |
| 3 | 이미지 프롬프트 검증 | 낮음 | 누락 필드, 금지 요소 |
| 4 | 이미지 생성 | 중간 | Codex 이미지 |
| 5 | 이미지 리뷰 | 중간 | 일관성/스토리 일치 |
| 6 | 영상 프롬프트 검증 | 낮음 | start/end, motion |
| 7 | 영상 생성 | 높음 | Seedance |
| 8 | 영상 프레임 검증 | 중간 | ffmpeg sampling |
| 9 | 최종 사람 검수 | 높음 | 교육자료 사용 가능성 |

## 19. Ralph Loop 20회 요구사항

계획 실행 또는 중요한 산출물 검증 시 다음을 강제한다.

```json
{
  "ralph_loop_required": true,
  "iterations": 20,
  "each_iteration_requires": [
    "emotional_steering_sentence",
    "numeric_scores",
    "blocking_issue_search",
    "evidence_path",
    "patch_or_reason_no_patch"
  ]
}
```

각 회차 산출물:

```json
{
  "iteration": 1,
  "emotional_probe_ko": "이 결과는 현장 교육자료로 쓰기엔 아직 불안하다.",
  "numeric_probe": {
    "source_traceability": 4,
    "story_clarity": 3,
    "visual_consistency": 2,
    "video_risk": 5
  },
  "found_gap": "",
  "patch": "",
  "remaining_risk": ""
}
```

## 20. 구현 작업 목록

### Task 1. 플러그인 스캐폴딩

- `plugin-creator`를 사용해 `safety-video-harness` 플러그인을 만든다.
- skills/hooks/scripts/templates/references 폴더를 포함한다.
- `.codex-plugin/plugin.json`을 검증한다.

### Task 2. 프로젝트 초기화 스크립트

- `scripts/init_project.py` 구현.
- 프로젝트 폴더와 상태 파일을 만든다.
- 기존 프로젝트를 덮어쓰지 않는다.

### Task 3. 교육자료 주제 추출

- PPTX/PDF/DOCX/이미지 자료를 등록한다.
- 이미지 기반 슬라이드는 렌더링 후 OCR/비전 분석한다.
- 여러 주제 후보를 추출한다.

### Task 4. 레퍼런스 조사

- 스타일별 검색어를 만든다.
- 후보 레퍼런스를 수집한다.
- 승인된 레퍼런스만 스타일 DNA에 사용한다.

### Task 5. 스토리보드 생성

- 선택 주제와 교육자료 출처에 기반해 스토리보드를 만든다.
- 스토리보드는 영상 생성 전까지 무제한 수정 가능하다.

### Task 6. 프롬프트 디렉팅

- 이미지/영상 프롬프트를 전문 에이전트가 보완한다.
- 공식 가이드 기반 필수 필드를 채운다.

### Task 7. 이미지 생성과 검증

- Codex 이미지 생성.
- 이미지 일관성 검증.
- 스토리-이미지 일치 검증.

### Task 8. 영상 생성과 검증

- Gate D 승인 후 Higgsfield CLI로 Seedance 생성.
- ffmpeg 프레임 샘플링.
- 영상 인식/검증.
- 3자 일치 검증.

### Task 9. Ralph Loop

- 주요 산출물마다 20회 품질 루프 실행.
- 루프 로그를 파일로 저장한다.

### Task 10. 훅 구현

- SessionStart, PreToolUse, PostToolUse, Stop 훅 구현.
- 비용 발생/파괴적 쓰기/조기완료를 차단한다.

### Task 11. 최종 합성

- 자막, 나레이션, 클립 합성.
- 최종 영상 검수 패키지를 만든다.

### Task 12. 플러그인 검증

- 플러그인 manifest 검증.
- dry-run 전체 실행.
- 샘플 프로젝트 E2E 검증.

## 21. 수용 기준

- 기존 특정 프로젝트 파일을 참조하지 않는다.
- `AGENTS.md` 기반 프로젝트 메모리만 사용한다.
- 교육자료에서 여러 주제 후보를 뽑는다.
- 사용자가 주제를 선택한다.
- 스토리보드를 먼저 만들고, 영상 생성은 후반 게이트 이후에만 한다.
- 이미지 검색/레퍼런스 수집 단계가 있다.
- 프롬프트 전문 에이전트가 있다.
- 이미지 일관성 검증 에이전트가 있다.
- 스토리-이미지 일치 검증 에이전트가 있다.
- 영상 프레임 분석 에이전트가 있다.
- 스토리보드-이미지-영상 3자 일치 검증이 있다.
- 30초 초과 영상은 가능하지만 추가 비용/검수 게이트를 통과해야 한다.
- Ralph Loop는 20회 실행된다.
- 감정 언어와 수치 언어가 매 루프에 모두 포함된다.
- 영상 생성 전 예상 비용과 재생성 리스크를 사용자에게 보여준다.
- 유료 영상 재생성은 자동으로 하지 않는다.

## 22. 최종 판단

이 PRD는 단순 자동화가 아니라 안전교육 영상 제작용 전용 하네스를 요구한다.
가장 중요한 설계 결정은 다음이다.

1. 스토리보드는 마음껏 반복한다.
2. 영상 생성은 게이트 뒤로 미룬다.
3. 이미지와 영상의 일관성은 별도 에이전트가 검증한다.
4. 영상은 프레임으로 쪼개 인식한다.
5. 30초는 한계가 아니라 기본 가드레일이다.
6. 플러그인 안에 skills, hooks, scripts, references를 모두 넣는다.
7. 하네스는 루프를 계속 돌리는 장치가 아니라 목표로 수렴시키는 장치다.
