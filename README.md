# 안전교육 영상 자동제작 하네스

이 폴더는 독립형 Codex 플러그인 `safety-video-harness`의 PRD와 실행 설계를 관리한다.

현재 실행 기준 문서는 [docs/plans/safety-video/safety-video-harness-final-prd.md](./docs/plans/safety-video/safety-video-harness-final-prd.md)이다.

이전 PRD와 비교 검토 문서는 [docs/plans/safety-video/archive](./docs/plans/safety-video/archive)에 보관되어 있다.

## 핵심 방향

- 교육자료, SOP, PPTX를 입력하면 주제 후보를 추출하고 사용자가 제작 주제를 선택한다.
- 영상 제작 전 스토리보드를 먼저 만들고, 스토리보드는 비용 부담 없이 반복 수정한다.
- 승인된 스토리보드 기준으로 Codex 내장 `imagegen` skill/tool로 이미지를 생성한다.
- 승인된 이미지 키프레임을 Higgsfield CLI / Seedance 영상 생성에 사용한다.
- 스토리보드, 이미지, 영상의 3자 일치 여부를 검증한 뒤 최종 합본으로 이동한다.
- 하네스는 `app/plugin/`의 플러그인 자산과 `app/harness/`의 실행 하네스를 명시적으로 나눈다.

## 작업 전 필수 가이드

에이전트나 스킬을 실행하기 전에는 링크 원장만 보지 말고, 아래 로컬 운영 문서를 먼저 읽는다.

- 전체 규칙: [AGENTS.md](./AGENTS.md)
- 점수 기준과 blocker 기준: [docs/evaluation-rubrics.md](./docs/evaluation-rubrics.md)
- 좋은/나쁜 산출물 예시: [docs/few-shot-examples.md](./docs/few-shot-examples.md)
- Higgsfield/Seedance 로컬 운영 기준: [docs/higgsfield-seedance-local-reference.md](./docs/higgsfield-seedance-local-reference.md)
- 각 역할별 운영 레퍼런스: `app/plugin/agents/<agent-id>/references/*.md`
- 각 스킬별 운영 레퍼런스: `app/plugin/skills/<skill-id>/references/*.md`

이 문서들은 공식문서를 매번 열어 확인하지 않아도 작업을 진행할 수 있도록, 프로젝트에서 실제로 써야 하는 판단 기준을 로컬화한 것이다.

## 다음번에 사용하는 방법

이 저장소는 Codex 플러그인 매니페스트를 포함한다.

```text
.codex-plugin/plugin.json
```

실제 플러그인 자산은 `app/plugin/.codex-plugin/plugin.json`, `app/plugin/agents/`,
`app/plugin/skills/`, `app/plugin/hooks/`에 있다. root `.codex-plugin/plugin.json`은
Codex가 root manifest를 요구하는 경우를 위한 compatibility shim이다.

다음 세션에서 가장 안정적인 사용 방식은 이 저장소 폴더를 작업 폴더로 열고 아래처럼 요청하는 것이다.

```text
AGENTS.md, CONTEXT.md, docs/evaluation-rubrics.md, docs/few-shot-examples.md를 읽고
safety-video-harness 방식으로 새 안전교육 영상 프로젝트를 시작해줘.
먼저 intake interview부터 진행하고, live imagegen/live Seedance/live TTS는 승인 전 금지야.
```

운영 시작 시 Codex는 바로 이미지를 만들지 않고 다음 순서로 진행해야 한다.

```text
1. intake interview
2. 교육자료 등록
3. 주제 후보 추출과 사용자 선택
4. 스타일 가이드와 레퍼런스 분류
5. 스토리보드 작성
6. 스토리보드 QA와 Gate 1 승인
7. 이미지 프롬프트/job spec 작성
8. 승인 후 Codex imagegen 실행과 이미지 QA
9. Gate 2 승인 후 Seedance dry-run 또는 짧은 validation-run
```

실제 live 작업은 별도 승인 문구가 필요하다. 특히 Seedance는 유료 호출이므로 영상 길이,
최대 시도 횟수, 예상 크레딧, 외부 업로드 허용 여부가 함께 정해져야 한다.

## 현재 상태

- [x] 독립형 한국어 PRD 작성
- [x] 기존 프로젝트 전용 메모리 파일 제거
- [x] 30초 정책을 기술 한계가 아닌 기본 비용/품질 가드레일로 재정의
- [x] 하네스 엔지니어링 문서의 루프, 훅, 검증 사다리, 상태 파일 원칙 반영
- [x] MVP dry-run CLI 구현
- [x] 플러그인 스캐폴딩 생성
- [x] 스킬/훅/에이전트 뼈대 구현
- [x] Gate 승인 전 live 생성 차단 테스트
- [x] 실제 교육자료 기반 dry-run 파일럿 실행
- [x] 레퍼런스 이미지/프로필을 프롬프트 계약에 자동 반영
- [x] Codex 내장 `imagegen` skill/tool 기반 실제 이미지 생성 흐름
- [x] 스토리 흐름 중심 이미지 프롬프트 규칙
- [x] 점수 기반 이미지 QA 루프
- [x] 씬 링크 검증 훅/에이전트 기준
- [x] Higgsfield CLI / Seedance 10초 제한 테스트 경로
- [x] 실제 이미지 파일럿과 Seedance 검증 경로 구현
- [x] 나레이션/TTS 제외 정책: 현재 목표는 영상+자막/오버레이 전달
- [x] 에이전트/스킬별 로컬 운영 레퍼런스, 점수 루브릭, few-shot 예시, Higgsfield/Seedance 운영 노트 보강

## 플러그인 구조

이 저장소는 “교육자료를 넣으면 스토리보드, 이미지 키프레임, 짧은 Seedance 검증 영상까지 만드는” Codex 플러그인 하네스다. 하네스는 생성 자체보다 순서, 증거, 승인, 품질 루프를 통제한다.

```text
.
├── .codex-plugin/plugin.json          # Codex 플러그인 manifest
├── AGENTS.md                          # 전체 작업 규칙, no narration, 게이트, evidence 정책
├── README.md                          # 운영자용 플러그인 설명서
├── app/
│   ├── plugin/
│   │   ├── .codex-plugin/plugin.json  # 실제 플러그인 manifest
│   │   ├── agents/                    # 역할별 평가자/기획자 지침
│   │   ├── hooks/                     # Codex lifecycle hooks
│   │   └── skills/                    # 플러그인 내부 skill 설명
│   └── harness/
│       ├── package/safety_video_harness/ # 핵심 파이썬 하네스 로직
│       ├── cli/                       # canonical CLI 엔트리포인트
│       ├── schemas/                   # JSON contract/schema
│       └── templates/project/         # 새 프로젝트 기본 파일
├── references/                        # 재사용 스타일/레퍼런스/샘플
├── scripts/                           # root compatibility CLI wrappers
├── docs/                              # 원페이저, 프롬프트 가이드, 계획, 리뷰
│   ├── plans/safety-video/            # PRD, 로드맵, 구현 계획
│   └── reviews/project/               # 프로젝트 구조/품질 리뷰
├── projects/_runs/                    # 루트 단위 실행 증거
└── projects/<slug>/                   # 실제 영상 프로젝트 산출물
```

프로젝트 폴더는 아래 계약을 따른다.

```text
projects/<slug>/
├── AGENTS.md                          # 프로젝트 전용 규칙
├── PLAN.md                            # 프로젝트 작업계획
├── project_config.json                # 길이, 비율, 게이트, 도구, 비용 정책
├── input/                             # source registry, rendered source facts, topic candidates
├── refs/                              # people, PPE, equipment, approved spaces/style/camera refs
├── story/                             # scenes, image prompts, video prompts, prompt-team plans
├── media/                             # images, video, audio, subtitles, final outputs
│   ├── images/draft/                  # 생성 직후 이미지와 버전 파일
│   ├── images/approved/               # 영상 생성에 사용할 승인 이미지
│   ├── video/clips/                   # Seedance 생성/다운로드 MP4
│   └── video/inspection/              # 프레임 추출, OCR, contact sheet
├── qa/                                # approvals, state, evidence, 평가 결과와 Arbiter 결정
├── llm-wiki/evaluation-rounds.md      # 반복 blocker와 라운드 요약
└── HANDOFF.md                         # 다음 세션 인계 문서
```

구 프로젝트의 `sources/`, `storyboard/`, `prompts/`, `images/`, `video/`,
`model/`, `product/`, `ref/`, root `approvals.json`, `.harness/`는 한 migration window 동안
read fallback으로 지원된다. 새 쓰기는 `input/`, `refs/`, `story/`, `media/`, `qa/`로만 한다.

Canonical project roots are `projects/<slug>/input/`, `projects/<slug>/refs/`,
`projects/<slug>/story/`, `projects/<slug>/media/`, and `projects/<slug>/qa/`.
The harness package lives at `app/harness/package/safety_video_harness/`; canonical CLI files live at
`app/harness/cli/`.

## 알고리즘 구조

전체 순서는 고정이다.

```text
1. 시작 인터뷰
2. 프로젝트 생성 및 교육자료 등록
3. PPTX/SOP 렌더링과 주제 후보 추출
4. 사용자가 주제 선택
5. 레퍼런스 배치/승인
6. 스타일 DNA 및 자료 근거 정리
7. 스토리보드 생성
8. 스토리보드 QA와 Gate 1 승인
9. Asset lock 생성: 고정 배경 plate, 인물/장비/PPE/공간 레퍼런스, 필요 시 Higgsfield Soul ID
10. 이미지 프롬프트 제작팀 preflight 생성
11. 이미지 프롬프트 또는 reference/edit/compositing 계획 생성
12. Codex imagegen으로 draft 이미지 생성 또는 승인 asset 기반 편집/조립
13. 이미지 QA와 RALPH loop
14. 승인 이미지를 start/end keyframe으로 연결
15. Seedance dry-run, reference media pack, 비용 산정, Gate 2 승인
16. 짧은 live Seedance 검증 영상 생성
17. 프레임 추출, 영상 QA, 재생성 제안
18. 최종 합본/자막/오버레이는 별도 후처리 단계
```

핵심 제약:

- 스토리보드가 기준 계약이다. 이미지나 영상이 스토리보드를 앞서가면 안 된다.
- 이미지 RALPH loop는 최대 20회지만 기준 통과 시 즉시 멈춘다.
- 같은 blocker가 3회 반복되면 이미지 재생성이 아니라 스토리보드/레퍼런스/프롬프트 수정으로 에스컬레이션한다.
- 영상은 유료이므로 자동 RALPH 재생성을 하지 않는다. 하네스는 `propose_only`로 수정 제안만 남긴다.
- 나레이션/TTS는 현재 범위에서 제외한다. 전달 문구는 자막, 오버레이, 텍스트 카드로 처리한다.
- OMO는 반복 실행자/작업 관리자이고, 점수 판정은 하네스 role evaluator와 Arbiter가 한다.
- 이미지 병렬화는 장면별 프롬프트 초안과 검토까지만 허용한다. 실제 imagegen 호출은 한 coordinator가 순차 통제한다.
- production keyframe은 텍스트 프롬프트만으로 여러 장을 독립 생성하지 않는다. 순수 text-to-image 다중 컷 생성은 draft exploration으로만 취급한다.
- production keyframe은 asset lock, reference/edit chain, 또는 Pillow/ImageMagick 등 deterministic compositing을 통해 같은 인물·장비·배경·위험구역을 유지해야 한다.
- Seedance/Higgsfield 영상은 prompt-only로 생성하지 않는다. 승인된 `start_image`, `end_image`, 가능하면 cast/equipment/space/style reference media pack 또는 Soul ID를 함께 사용한다.

## 시작 인터뷰

새 프로젝트를 시작할 때 Codex는 바로 생성하지 말고 먼저 아래 질문을 한다. 답변이 일부 비어 있어도 진행은 가능하지만, 비어 있는 항목은 하네스가 보수적인 기본값을 적용한다.

1. 어떤 교육자료를 기준으로 만들까요?
   - PPTX, PDF, SOP, 사내 가이드 파일 경로를 받는다.
   - 여러 파일이면 우선순위도 받는다.

2. 어떤 주제로 만들까요?
   - 사용자가 직접 주제를 말할 수 있다.
   - 모르면 `extract_topics.py`로 후보를 뽑고 선택하게 한다.

3. 몇 초짜리 영상을 만들까요?
   - 기본값은 30초다.
   - 영상 생성 테스트는 비용 때문에 5초 또는 10초 validation-run부터 한다.

4. 이미지 분량을 어떻게 할까요?
   - `보통`: 기준 컷 수 유지
   - `많이`: 기준보다 2배 많은 키프레임
   - `더 많이`: 기준보다 4배 많은 키프레임

5. 영상 비율과 해상도는 무엇인가요?
   - 기본값은 `16:9`, `1080p` 계획, Seedance 검증은 `720p`.

6. 참고 레퍼런스 이미지가 있습니까?
   - 사람/작업자/신호수
   - 작업상황/위험상황/예방행동
   - 공간/현장/동선
   - 장비/차량/제품
   - PPE/복장
   - 스타일/카메라/조명

7. 어떤 스타일을 원하십니까?
   - `한국 웹툰풍 안전교육`: 현대 한국 웹툰풍, 선명한 선화, 셀 셰이딩, 안전 색상 강조
   - `깔끔한 3D 교육 렌더`: 장비와 공간 관계를 입체적으로 설명
   - `플랫 벡터 안전교육`: 단순 도형과 높은 대비로 핵심 행동 전달
   - `준실사 산업현장`: 실제 현장감은 유지하고 교육용 노이즈는 줄임
   - `미니멀 픽토그램`: 표지판/매뉴얼처럼 핵심 금지·허용 행동만 전달

8. 레퍼런스는 어떻게 사용할까요?
   - 동일 인물 유지
   - 분위기만 참고
   - 작업상황 구도만 참고
   - 공간/동선만 참고
   - 사용 금지 요소를 설명

9. 영상 생성까지 진행할까요, 아니면 스토리보드와 이미지만 먼저 볼까요?
   - 기본값은 스토리보드와 이미지 먼저.
   - Seedance live는 Gate 2, 비용 고지, 사용자 승인이 있어야 실행한다.

10. 교육 문구 전달 방식은 무엇인가요?
   - 기본값은 자막/오버레이.
   - 나레이션/TTS는 현재 범위에서 제외한다.

11. 최종 검토자는 누구인가요?
    - 안전 담당자, 현장 관리자, 교육 담당자 등 승인자 기준을 기록한다.

## 빠른 시작

```bash
uv run python -m pytest

uv run python scripts/init_project.py --name "추락 예방" --slug projects/fall-prevention
uv run python scripts/register_sources.py --project projects/fall-prevention --source /path/to/source.pptx
uv run python scripts/render_pptx_sources.py --project projects/fall-prevention --dry-run --mode media_extract
uv run python scripts/extract_topics.py --project projects/fall-prevention
uv run python scripts/intake_project.py --project projects/fall-prevention --target-seconds 30 --image-density normal --text-delivery subtitles_overlay
uv run python scripts/select_topic.py --project projects/fall-prevention --topic-id topic-001
uv run python scripts/search_references.py --project projects/fall-prevention --dry-run
uv run python scripts/analyze_reference_assets.py --project projects/fall-prevention --dry-run
uv run python scripts/extract_style_dna.py --project projects/fall-prevention
uv run python scripts/plan_storyboard.py --project projects/fall-prevention --duration 30 --image-density normal
uv run python scripts/validate_project.py projects/fall-prevention
uv run python scripts/evaluate_storyboard.py --project projects/fall-prevention
uv run python scripts/approve_gate.py --project projects/fall-prevention --gate storyboard
uv run python scripts/plan_image_prompt_team.py --project projects/fall-prevention
uv run python scripts/generate_images.py --project projects/fall-prevention --dry-run
uv run python scripts/validate_images.py --project projects/fall-prevention --dry-run
uv run python scripts/generate_seedance.py --project projects/fall-prevention --dry-run
uv run python scripts/plan_subtitles.py --project projects/fall-prevention --dry-run
uv run python scripts/validate_scene_links.py --project projects/fall-prevention
uv run python scripts/estimate_video_cost.py --project projects/fall-prevention --estimated-credits 0
uv run python scripts/check_story_video_alignment.py --project projects/fall-prevention
```

`assemble_video.py --dry-run`은 `projects/<slug>/media/video/clips/*.mp4`가 있을 때
concat 계획을 만든다. Seedance live를 실행하지 않은 dry-run 프로젝트에서는 이 단계 전까지가
기본 빠른 시작 범위다.

영상 길이와 이미지 분량은 운영 인테이크에서 먼저 결정한다.

- `몇 초짜리 영상을 만드시겠습니까?` 기본값은 30초다.
- `이미지의 분량을 어떻게 하시겠습니까?`
  - `보통`: 현재 기준 유지
  - `많이`: 기준보다 2배 더 많은 이미지/키프레임 계획
  - `더 많이`: 기준보다 4배 더 많은 이미지/키프레임 계획

CLI 값은 `--duration`과 `--image-density normal|high|very_high`로 반영한다.

스타일 선택은 `project_config.json`의 `style_guide_id`에 기록된다. 재사용 가능한 스타일은
루트 [references/style](./references/style)에 보관한다. 현재 기본값은
`korean-industrial-webtoon`이며, 좋은 결과물이 나오면 `references/style/<style-id>/STYLE_GUIDE.md`
와 `references/style/<style-id>/references/`에 추가한다.

`intake_project.py --defaults`는 테스트와 샘플용이다. 운영 프로젝트에서는 `intake_project.py`에
`--target-seconds`, `--image-density`, `--style-guide-id`, `--text-delivery`,
`--approval-scope`, `--reference-notes`를 명시하고, `extract_topics.py` 이후
`select_topic.py --topic-id ...`로 주제를 명시 선택한다.

## 스타일 가이드 카탈로그

프로젝트별 레퍼런스는 `projects/<slug>/refs/approved/`에 두고, 여러 프로젝트에서 재사용할
그림체는 루트 `references/style/`에 둔다.

```text
references/style/
├── README.md
├── catalog.json                       # 인터뷰에서 보여줄 5가지 스타일 선택지
└── korean-industrial-webtoon/
    ├── STYLE_GUIDE.md                 # 스타일 DNA, 프롬프트 블록, 금지 요소, QA 기준
    └── references/
        ├── reference-001.png          # 기준 이미지 복사본
        └── reference-001.md           # 참고할 것 / 복제하지 말 것
```

`generate_images.py`와 `generate_seedance.py`는 선택된 `STYLE_GUIDE.md`를 프롬프트에 자동으로
주입한다. 따라서 프로젝트마다 `style_guide_id`만 바꾸면 같은 교육자료라도 웹툰풍, 3D,
벡터풍 등으로 분기할 수 있다.

## 이미지 프롬프트 제작팀

일관성을 위해 “여러 에이전트가 각자 이미지를 생성”하지 않는다. 병렬화는 이미지 생성 전
프롬프트 설계 단계에만 쓴다.

```text
sc01 Lead Style Agent
  └─ style/character/vehicle/space/camera/rendering bible 확정

sc02~scNN Scene Prompt Agents
  └─ 장면별 previous/current/next, visible cast, gaze target, hazard logic 작성

Visual Director Arbiter
  └─ 모든 장면 프롬프트를 통합 검토하고 ready_for_generation 여부 결정

Imagegen Coordinator
  └─ 통합된 프롬프트 기준으로 Codex imagegen을 순차 실행
```

구성 파일:

- `app/plugin/agents/lead-style-agent/AGENT.md`
- `app/plugin/agents/scene-prompt-agent/AGENT.md`
- `app/plugin/agents/visual-director-arbiter/AGENT.md`
- `scripts/plan_image_prompt_team.py`
- `story/image_prompt_team_plan.json`

`generate_images.py`는 `story/image_prompt_team_plan.json`이 없으면 자동으로 생성한다.
이 preflight 블록은 이미지 프롬프트에 주입되어 “첫 장면 기준, 중앙 통제, 병렬 생성 금지”
규칙을 반복 적용한다.

참고/공식 문서는 [docs/generative-media-reference-index.md](./docs/generative-media-reference-index.md)에 모은다.

## 레퍼런스 배치

생성 일관성을 높이려면 프로젝트 폴더 안에 승인된 레퍼런스를 넣는다. 레퍼런스는 여러 종류를 받을 수 있고, 역할별로 다른 폴더에 둔다. 모든 이미지 레퍼런스는 가능하면 같은 이름의 `.md` 설명을 옆에 둔다.

```text
projects/<slug>/
├── refs/people/                        # 고정 등장인물, 작업자, 신호수
│   ├── worker-001-front.png
│   └── worker-001.profile.md           # 얼굴형, 체형, 복장, PPE, 고정 특징
├── refs/ppe/                           # 안전모, 조끼, 안전화, 장갑 등 PPE
├── refs/equipment/                     # BCT, 덤프트럭, 지게차, 설비, 제품
│   ├── bct-trailer.png
│   └── bct-trailer.md                  # 장비 형태, 색상, 축 수, 크기
├── refs/candidates/                    # 아직 승인 전인 검색/수집 후보
└── refs/approved/                      # 프롬프트에 실제 반영할 승인 레퍼런스
    ├── safety-animation-style.md       # 루트에 직접 둔 일반 스타일 설명도 가능
    ├── people/                         # 사람 포즈, 시선, 신호수 자세 참고
    │   ├── signal-person-reference.png
    │   └── signal-person-reference.md
    ├── work/                           # 작업상황, 위험상황, 예방행동 구도 참고
    │   ├── blind-spot-workflow.png
    │   └── blind-spot-workflow.md
    ├── spaces/                         # 현장 구조, 동선, 사각지대, 통로 참고
    │   ├── plant-entry-layout.png
    │   └── plant-entry-layout.md
    ├── style/                          # 그림체, 질감, 색감, 교육자료 톤
    ├── camera/                         # 카메라 앵글, 렌즈감, 거리감
    └── lighting/                       # 조명, 노출, 날씨, 그림자
```

`generate_images.py`와 `generate_seedance.py`는 아래 폴더를 자동 스캔한다.

- `refs/people`: 고정 인물 identity lock
- `refs/ppe`: 복장/PPE lock
- `refs/equipment`: 장비/차량/제품 lock
- `refs/approved`: 일반 승인 레퍼런스
- `refs/approved/people`: 사람 포즈, 시선, 역할 행동
- `refs/approved/work`: 작업상황, 위험상황, 예방행동
- `refs/approved/spaces`: 현장 배치, 동선, 통로, 사각지대
- `refs/approved/style`: 그림체, 질감, 색감
- `refs/approved/camera`: 구도, 앵글, 거리감
- `refs/approved/lighting`: 조명, 날씨, 노출

이미지 옆에 같은 이름의 `.md`를 두거나, 인물은 `worker-001.profile.md`처럼 프로필 설명을 두면 해당 설명이 모든 이미지/영상 프롬프트에 들어간다.

레퍼런스 `.md`는 “무엇을 참고하고 무엇은 복제하지 말지”를 분리해서 쓴다.

```md
이 레퍼런스에서 참고할 것:
- 신호수가 차량 진행 방향을 바라보는 자세
- 신호봉이 운전자에게 보이는 위치

복제하지 말 것:
- 얼굴 신원
- 회사 로고
- 배경의 특정 상호
```

`refs/candidates`는 검색 후보 보관용이다. 실제 프롬프트에는 자동 반영하지 않으므로, 사용할 이미지는 `approve_reference.py`로 승인하거나 `refs/approved`로 옮긴 뒤 실행한다.

```bash
uv run python scripts/approve_reference.py --project projects/fall-prevention --candidate animation-style.png --role style
uv run python scripts/approve_reference.py --project projects/fall-prevention --candidate work-scene.png --role work
uv run python scripts/analyze_reference_assets.py --project projects/fall-prevention --dry-run
```

`analyze_reference_assets.py --dry-run`은 유료 비전 호출을 하지 않는다. 현재는 이미지 옆 `.md` 설명을 우선 사용하고, 설명이 없으면 파일명 기반 placeholder를 `refs/approved/reference_assets.json`에 기록한다.

## 기준 테스트 자료

실제 자료 기반 검증 fixture:

```text
fixtures/sources/remicon-collision-guide.pptx
```

이 파일은 레미콘 사업장 충돌·접촉 안전작업 가이드이며, 테스트는 이 자료에서 다음 요소가 산출물에 반영되는지 확인한다.

- 레미콘 사업장 대형차량 충돌·접촉 예방
- 사각지대
- 신호수
- BCT
- 덤프트럭
- 후진

현재 하네스는 이 파일에서 PPTX 내부 이미지 미디어와 슬라이드 텍스트를 추출하고, 해당 자료에 맞는 주제와 30초/6컷 스토리보드를 생성한다.
`--mode slide_render`를 쓰면 로컬에 LibreOffice `soffice`와 Poppler `pdftoppm`이 있을 때 슬라이드 전체를 PNG로 렌더링한다.
도구가 없으면 기존 `media_extract`로 안전하게 fallback한다.

## 금지된 기본 동작

```bash
uv run python scripts/generate_images.py --project projects/fall-prevention --live
uv run python scripts/generate_seedance.py --project projects/fall-prevention --live
```

이미지 live 명령은 승인 게이트가 없으면 실패한다. Seedance live 명령은 추가로 `--execute-paid`가 없으면 실패한다.

## 이미지 생성 경로

기본 이미지 생성 경로는 OpenAI API가 아니라 Codex 내장 `imagegen` skill/tool이다.

운영 방식:

1. `generate_images.py --dry-run`이 상세 프롬프트와 imagegen 작업 지시서를 만든다.
2. Codex 에이전트가 `imagegen` skill을 사용해 실제 이미지를 생성한다.
3. 생성 결과는 `$CODEX_HOME/generated_images/...`에만 두지 않고 `projects/<slug>/media/images/draft/scNN_vNNN.png`로 이동 또는 복사한다.
4. 승인된 이미지는 `projects/<slug>/media/images/approved/`로 이동하고, 기존 승인 이미지는 덮어쓰지 않는다.

OpenAI Image API 또는 CLI fallback은 사용자가 명시적으로 API/CLI 경로를 요청할 때만 사용한다.

이미지 프롬프트 작성 기준은 [docs/imagegen-prompting-references.md](./docs/imagegen-prompting-references.md)에 둔다. 프롬프트는 이전 장면, 현재 예방 행동, 다음 장면 연결을 모두 포함해야 하며, 고립된 체크리스트 이미지처럼 만들지 않는다.

### Asset Lock 정책

최근 테스트에서 확인한 한계:

- 텍스트 프롬프트만으로 `sc01~scNN`을 독립 생성하면 사람 얼굴, 체형, PPE, 차량 구조, 배경 설비, 차선, 위험구역이 미세하게 바뀐다.
- 2x2 시트로 한 번에 생성해도 production-grade 동일성은 보장되지 않는다.
- 따라서 하네스는 순수 text-to-image multi-frame 생성을 production 경로로 보지 않는다.

production 경로는 아래 순서다.

```text
1. fixed background/space plate
2. cast character sheet 또는 Higgsfield Soul ID source
3. equipment reference: BCT, dump truck, PPE, hazard-zone markings
4. scene keyframe derivation: reference/edit chain 또는 deterministic compositing
5. image QA: identity, equipment, space, hazard-zone blocker 검사
6. Seedance: approved start/end keyframes + reference media pack
```

`generate_images.py --live`는 `story/imagegen_jobs.json`에 `asset_lock`,
`generation_chain`, `reference_images`, `allowed_change_only`, 그리고
`production_consistency_policy`를 함께 기록한다. `asset_lock.status`가
`draft_exploration_only`이면 산출물은 분위기/스토리 테스트용이며, 바로 Seedance production
keyframe으로 쓰면 안 된다.

Live imagegen job spec은 anchor-first sequential 방식으로만 준비한다.

- `sc01`은 anchor keyframe이다.
- `sc02` 이후는 직전 `media/images/approved/scNN.png`가 있어야 준비된다.
- `--only sc03` 같은 직접 지정도 `sc02` 승인본이 없으면 실패한다.
- `--live`에 `--only`가 없으면 현재 승인 상태 기준 다음 미승인 keyframe 1개만 준비한다.
- 각 job은 `anchor_image`, `previous_approved_image`, `reference_images`, `allowed_change_only`를 포함한다.

Codex imagegen 실행 준비 명령:

```bash
uv run python scripts/generate_images.py --project projects/fall-prevention --live --only sc01
```

이 명령은 실제 API를 호출하지 않고 `story/imagegen_jobs.json`을 만든다. Codex는 이 job spec을 보고 `imagegen` skill/tool로 이미지를 만든 뒤, 결과 파일을 다음 명령으로 프로젝트에 수거한다.

```bash
uv run python scripts/record_image_output.py \
  --project projects/fall-prevention \
  --scene-id sc01 \
  --generated-file /path/to/generated-image.png

uv run python scripts/collect_image_outputs.py \
  --project projects/fall-prevention \
  --source-dir "$CODEX_HOME/generated_images/latest"

uv run python scripts/validate_images.py --project projects/fall-prevention --only sc01
uv run python scripts/approve_image.py --project projects/fall-prevention --scene-id sc01
```

재생성은 기존 draft/approved 파일을 덮어쓰지 않는다.

```bash
uv run python scripts/generate_images.py --project projects/fall-prevention --live --only sc01 --regenerate
```

## 영상 생성 경로

영상 생성은 Higgsfield CLI의 `seedance_2_0`을 사용한다. 비용 통제 때문에 기본 테스트 경로는 10초, 5초 클립 2개, 최대 3회 이하로 제한한다.

Seedance/Higgsfield 고정 원칙:

- `--start-image`와 `--end-image`는 필수 lock layer다.
- cast/equipment/space/style reference가 있으면 `reference_media_pack`으로 job spec에 포함하고, 실제 CLI 명령에는 존재하는 이미지 파일을 `--image`로 추가한다.
- 인물 동일성이 중요한 경우 Higgsfield Soul ID 또는 equivalent character reference를 먼저 만든다.
- prompt는 “무엇을 움직일지”를 설명하고, 동일성은 start/end keyframe과 reference media가 담당한다.

```bash
uv run python scripts/generate_seedance.py --project projects/fall-prevention --dry-run
uv run python scripts/validate_scene_links.py --project projects/fall-prevention
uv run python scripts/check_story_video_alignment.py --project projects/fall-prevention
uv run python scripts/plan_subtitles.py --project projects/fall-prevention --dry-run
uv run python scripts/approve_gate.py --project projects/fall-prevention --gate image_to_video --estimated-credits 35

uv run python scripts/generate_seedance.py \
  --project projects/fall-prevention \
  --live \
  --execute-paid \
  --test-seconds 10 \
  --max-attempts 1 \
  --validation-run \
  --plan-only
```

실제 유료 테스트 실행:

```bash
uv run python scripts/generate_seedance.py \
  --project projects/fall-prevention \
  --live \
  --execute-paid \
  --test-seconds 10 \
  --max-attempts 1 \
  --validation-run
```

생성 후 검증:

```bash
uv run python scripts/inspect_video.py \
  --project projects/fall-prevention \
  --clip projects/fall-prevention/media/video/clips/<clip>.mp4 \
  --tool scenelens \
  --no-transcript

uv run python scripts/validate_video.py --project projects/fall-prevention --expected-clips 1
uv run python scripts/assemble_video.py --project projects/fall-prevention --dry-run
```

`validate_video.py`는 MP4 메타데이터나 수동 점수만으로 통과하지 않는다. 먼저
`inspect_video.py`로 로컬 프레임/OCR evidence manifest를 만든 뒤 sampled frame을 보고
`qa/video_manual_review.json`에 다음 항목을 기록해야 한다.

- character_continuity_score: 사람이 갑자기 생기거나 사라지지 않는가
- gaze_motivation_score: 인물의 시선이 위험원, 신호수, 운전원, 동선 등 명확한 대상에 향하는가
- education_clarity_score: 영상과 자막/오버레이만으로 어떤 안전교육인지 보이는가
- storyboard_alignment_score: 스토리보드와 시작/끝 키프레임 의도가 유지되는가

각 항목 4점 미만이거나 blocker가 있으면 영상은 최종본으로 진행하지 않는다.

현재 범위에서 나레이션, TTS, Whisper/API 전사는 구현하지 않는다. 필요한 교육 문구는
자막, 오버레이, 텍스트 카드 산출물로 처리한다.

## 평가 기준과 루프

영상 제작 품질은 세 단계로 나눠 평가한다.

모든 평가 라운드는 기계용 원장과 사람/에이전트용 학습 노트에 동시에 누적된다.

- 기계용 원장: `qa/evaluation_rounds.jsonl`
- 라운드별 evidence bundle: `qa/evaluation_bundles/<stage>/<item>/round_NNN.json`
- 역할별 독립 평가 산출물: `qa/role_evaluations/<stage>/<item>/round_NNN.json`
- 역할별 개별 발언/판정: `qa/role_evaluations/<stage>/<item>/round_NNN/<role>.json|md`
- Arbiter 최종 판단: `qa/arbiter_decisions/<stage>/<item>/round_NNN.json`
- 조건부 토론 기록: `qa/debates/<stage>/<item>/round_NNN.json`
- 조건부 토론 md 라운드: `qa/debates/<stage>/<item>/round_NNN/*.md`
- LLM/사람용 누적 노트: `llm-wiki/evaluation-rounds.md`

`app/plugin/hooks/hooks.json`은 세션 시작, 도구 실행 전, 도구 실행 후, 종료 시점의 lifecycle hook을 등록한다.
새 세션이나 재개 시에는 `app/plugin/hooks/session-start-anchor.py`가 짧은 mission anchor를 출력한다.
PreToolUse 훅은 live/유료 호출, secret-like 문자열, 보호 경로 수정을 차단한다. Codex imagegen job spec은
승인된 storyboard gate만 요구하고, Seedance/Higgsfield 같은 외부 업로드/유료 비디오 경로는 Gate 2와
`external_upload_allowed=true`를 함께 요구한다. PostToolUse 훅은 project schema, scene link, evidence claim을
검증한다. Stop 훅은 완료 sentinel이 없는 종료를 막기 위한 안전장치다.

`llm-wiki/evaluation-rounds.md`는 다음 라운드 판단을 돕는 라운드별 학습 기록장이다.
원본 evidence를 통째로 복사하지는 않지만, 매 라운드마다 점수, 산출물 경로, blocker,
개선 지시, 다음 프롬프트에 주입할 메모, 반복 blocker를 누적한다. 이미지 재생성 프롬프트를
만들 때 이 기록에서 반복 blocker와 성공한 개선 패턴을 확인하고, 같은 문제가 여러 번 반복되면
단순 재생성이 아니라 스토리보드/레퍼런스 수정으로 에스컬레이션하는 근거로 쓴다.
원본 이미지, 영상, JSON evidence의 source of truth는 각 프로젝트 폴더에 둔다.

각 라운드의 wiki block은 다음 구조를 갖는다.

```text
## image / sc01 / round 1
- decision
- total_score
- blocking_issues
- blocker_signatures
- bundle

### Scores
### Round Outputs
### Improvement Notes
### Next Prompt Memory
### Repeated Blockers
```

1. 시나리오/스토리보드 QA

```bash
uv run python scripts/evaluate_storyboard.py --project projects/fall-prevention
```

평가 항목:

- `source_grounding_score`: 교육자료 출처가 있는가
- `causal_flow_score`: 사고 예방 행동의 원인과 결과가 보이는가
- `granularity_score`: 컷이 너무 넓지 않고 이미지/영상 생성 가능한 단위인가
- `text_delivery_score`: 전달 문구가 자막/오버레이 계약으로 잡혀 있는가
- `continuity_score`: start/end keyframe과 연속성 제약이 있는가

Gate 1은 `approve_gate.py --gate storyboard` 실행 시 스토리보드 QA를 다시 실행한다. `qa/storyboard_quality_reviews.json` 기준이 실패하면 스토리보드 승인은 기록되지 않는다.

2. 스토리보드-이미지 QA와 RALPH loop

```bash
uv run python scripts/validate_images.py --project projects/fall-prevention --only sc01
```

`qa/image_qa_loop.json`에 `ralph_loop`가 기록된다. 이미지가 기준 미달이면
`needs_regeneration` 상태와 함께 부족한 지점, 재생성 프롬프트가 남는다. 이미지
단계는 비용이 영상보다 낮고 수정 효과가 크므로, blocked scene은 점수 기준을 넘을
때까지 재생성/검증 루프를 반복한다.

RALPH 재생성 프롬프트는 단순히 blocker를 나열하지 않는다. `RALPH critique` 블록으로
품질 압박 문구, 실패 기준, 반드시 보존할 요소, 반드시 바꿀 요소, 반복 금지 항목을 함께
다음 imagegen 프롬프트에 주입한다.

```text
RALPH critique for sc01:
Quality pressure: This result is not acceptable for a safety training video...
Failed criteria and required fixes:
- floor_lane_consistency_score below minimum 4: 3
Must preserve:
- approved character identity, helmet, vest, body proportion, and role
Must change this round:
- make every listed blocker visually impossible to miss
Do not repeat:
- floor_lane_consistency_score below minimum 4: 3
```

현재 production 이미지 통과 기준은 11개 축 `44/55` 이상이며, 모든 축이 4점 이상이어야 한다.
기본 6개 축은 스토리 매칭, 인물/장비/PPE, 스토리 흐름, 기술 준비도를 본다. 추가 5개 축은
`qa/image_manual_reviews.json`에 기록되는 수동/격리 시각 QA 기준이다.

- `floor_lane_consistency_score`: 바닥, 차선, 보행로, 콘, 볼라드 일관성
- `background_consistency_score`: 플랜트 구조물, 게이트, 반사경, 표지판, 카메라 방향 일관성
- `character_identity_lock_score`: 작업자 체형, PPE, 역할, 시각 단서 고정
- `vehicle_geometry_lock_score`: BCT, 덤프트럭, 거울, 바퀴, 크기, 상대 위치 고정
- `hazard_zone_consistency_score`: 위험구역, 보행자 동선, 정지선, 통제점 고정

자동 비전 평가자가 붙기 전까지는 `qa/image_manual_reviews.json`이 없으면 draft 이미지가 존재해도
production 통과가 되지 않는다. 이 경우 RALPH 상태는 `needs_regeneration`으로 남고, 수동 시각 QA
또는 이미지 재생성이 필요하다는 blocker가 기록된다.

로컬 휴리스틱 시각 QA 보조 산출물은 아래 명령으로 만든다. 이 명령은 이미지를 유료 업로드하지
않고 contact sheet와 점수 초안을 만든다. `--write-review`를 붙이면 `qa/image_manual_reviews.json`까지
작성하지만, 의미론적 인물/시선 판단은 사람 또는 별도 비전 평가자가 최종 확인해야 한다.

OpenCV MCP는 이 단계의 우선 로컬 비전 도구다. 외부 업로드 없이 바닥/차선 색상 drift,
위험구역 위치, 배경/레이아웃 변화, contact-sheet preprocessing 같은 1차 검사를 맡는다.
사람 동일성, 시선 의미, 교육성 판단은 OpenCV만으로 승인하지 않고 human/model semantic review로 넘긴다.

```bash
uv run python scripts/build_image_visual_review.py --project projects/fall-prevention --only sc01
uv run python scripts/build_image_visual_review.py --project projects/fall-prevention --only sc01 --write-review
```

산출물:

- `qa/visual_review/image_contact_sheet.png`
- `qa/image_visual_review_draft.json`
- 선택 시 `qa/image_manual_reviews.json`

OpenCV MCP 설치/연결:

```toml
[mcp_servers.opencv]
command = "uvx"
args = ["opencv-mcp-server"]
```

설정 후 Codex를 재시작하면 OpenCV MCP 도구를 사용할 수 있다.

RALPH loop는 무조건 20회 실행하는 루프가 아니다. 장면별 최대 20회까지 허용하는
early-stopping loop이며, 기준을 통과하면 즉시 종료한다. 20회에 도달해도 blocker가
남으면 `max_iterations_reached`와 `stop_and_escalate`로 전환하고, 같은 이미지를 계속
재생성하지 않는다.

같은 blocker signature가 같은 scene에서 3회 반복되면 20회를 기다리지 않고
`repeated_blocker_escalation`과 `stop_and_escalate`로 전환한다. 이때 Arbiter는 단순 이미지
재생성이 아니라 스토리보드, 레퍼런스, 프롬프트 계약을 수정하라는 `regeneration_delta`를 남긴다.
이전 라운드의 blocker는 다음 `generate_images` 프롬프트에 `Previous QA blockers for this scene`
섹션으로 자동 주입된다.

이미지 평가는 생성자가 직접 승인하지 않는다. `qa/evaluation_bundles/image/scNN/round_NNN.json`
에 현재 장면, 이전/다음 장면 맥락, 리뷰 결과, 필요한 증거 목록을 묶고, 이 evidence bundle만
보는 격리 평가자 관점으로 채점한다. 스토리보드, 이미지, 영상 QA는 모두 role evaluator를
병렬 실행 가능한 단위로 분리하고, Arbiter가 consensus rule을 적용한다. 기본 통과 규칙은
전체 승인 또는 1개 조건부 승인까지이며, safety/continuity critical veto는 다수결보다 우선한다.

Gate 2는 비용 고지, `external_upload_allowed=true`, 모든 승인 이미지, 모든 scene의 live 이미지 QA coverage,
manual visual image QA, `qa/image_qa_loop.json`의 `passed=true`를 요구한다. dry-run QA나 일부 장면만 리뷰된 상태에서는
영상 제작 승인이 불가능하다.

OMO는 이미지 RALPH의 판정자가 아니라 반복 실행자/작업 관리자로만 쓴다. 먼저 하네스가
`validate_images.py`로 점수, blocker, Arbiter 결정을 만든 뒤, OMO는
`qa/image_qa_loop.json`과 `qa/arbiter_decisions/...`를 읽고 다음 실행 명령을 고른다.
이를 위해 다음 계획 파일을 만들 수 있다.

```bash
uv run python scripts/plan_omo_image_ralph.py --project projects/fall-prevention --only sc01
```

생성물은 `qa/omo_image_ralph_plan.json`이다. 이 파일의 `omo_prompt`는 `$omo:ulw-loop`에서
사용할 수 있는 반복 실행 지시문이며, 점수 판정은 계속 하네스 내부 QA만 사용한다.

3. 스토리보드-이미지-영상 QA와 제안 전용 루프

```bash
uv run python scripts/inspect_video.py --project projects/fall-prevention --clip <clip.mp4> --tool scenelens --no-transcript
uv run python scripts/validate_video.py --project projects/fall-prevention --expected-clips 1 --clip <clip-name>.mp4
```

영상은 유료 생성이므로 자동 재생성하지 않는다. 기준 미달이면
`qa/video_regeneration_proposals.json`에 `propose_only` 모드로 부족한 지점과 다음
수정 제안만 남긴다. 다음 유료 생성은 사용자가 승인한 경우에만 실행한다.

## 원칙

- 기존 샘플 프로젝트와 독립적으로 설계한다.
- 스토리보드 승인 전에는 영상 생성 작업을 실행하지 않는다.
- 영상 생성은 크레딧과 재생성 비용이 있으므로 승인 게이트를 통과한 경우에만 실행한다.
- 모든 안전 관련 문구는 교육자료, SOP, 사용자 승인 메모 중 하나로 추적 가능해야 한다.
