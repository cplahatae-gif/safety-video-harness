# 안전교육 영상 자동제작 하네스

이 폴더는 독립형 Codex 플러그인 `safety-video-harness`의 PRD와 실행 설계를 관리한다.

현재 실행 기준 문서는 [plans/safety-video-harness-final-prd.md](./plans/safety-video-harness-final-prd.md)이다.

이전 PRD와 비교 검토 문서는 [plans/archive](./plans/archive)에 보관되어 있다.

## 핵심 방향

- 교육자료, SOP, PPTX를 입력하면 주제 후보를 추출하고 사용자가 제작 주제를 선택한다.
- 영상 제작 전 스토리보드를 먼저 만들고, 스토리보드는 비용 부담 없이 반복 수정한다.
- 승인된 스토리보드 기준으로 Codex 내장 `imagegen` skill/tool로 이미지를 생성한다.
- 승인된 이미지 키프레임을 Higgsfield CLI / Seedance 영상 생성에 사용한다.
- 스토리보드, 이미지, 영상의 3자 일치 여부를 검증한 뒤 최종 합본으로 이동한다.
- 하네스는 플러그인 형태로 구성하며 skills, hooks, agents, MCP, scripts를 명시적으로 나눈다.

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
- [x] 실제 이미지/영상 생성 파일럿 실행
- [x] 나레이션/TTS 제외 정책: 현재 목표는 영상+자막/오버레이 전달

## 빠른 시작

```bash
uv run pytest -q

python3 scripts/init_project.py --name "추락 예방" --slug projects/fall-prevention
python3 scripts/register_sources.py --project projects/fall-prevention --source /path/to/source.pptx
python3 scripts/render_pptx_sources.py --project projects/fall-prevention --dry-run --mode media_extract
python3 scripts/extract_topics.py --project projects/fall-prevention
python3 scripts/select_topic.py --project projects/fall-prevention --topic-id topic-001
python3 scripts/search_references.py --project projects/fall-prevention --dry-run
python3 scripts/analyze_reference_assets.py --project projects/fall-prevention --dry-run
python3 scripts/extract_style_dna.py --project projects/fall-prevention
python3 scripts/plan_storyboard.py --project projects/fall-prevention --duration 30 --image-density normal
python3 scripts/validate_project.py projects/fall-prevention
python3 scripts/approve_gate.py --project projects/fall-prevention --gate storyboard
python3 scripts/generate_images.py --project projects/fall-prevention --dry-run
python3 scripts/validate_images.py --project projects/fall-prevention --dry-run
python3 scripts/validate_scene_links.py --project projects/fall-prevention
python3 scripts/generate_seedance.py --project projects/fall-prevention --dry-run
python3 scripts/estimate_video_cost.py --project projects/fall-prevention --estimated-credits 0
```

영상 길이와 이미지 분량은 운영 인테이크에서 먼저 결정한다.

- `몇 초짜리 영상을 만드시겠습니까?` 기본값은 30초다.
- `이미지의 분량을 어떻게 하시겠습니까?`
  - `보통`: 현재 기준 유지
  - `많이`: 기준보다 2배 더 많은 이미지/키프레임 계획
  - `더 많이`: 기준보다 4배 더 많은 이미지/키프레임 계획

CLI 값은 `--duration`과 `--image-density normal|high|very_high`로 반영한다.

`intake_project.py --defaults`는 테스트와 샘플용이다. 운영 프로젝트에서는 `extract_topics.py` 이후 `select_topic.py --topic-id ...`로 명시 선택한다.

## 레퍼런스 배치

생성 일관성을 높이려면 프로젝트 폴더 안에 승인된 레퍼런스를 넣는다.

```text
projects/<slug>/
├── model/cast/                # 반복 등장 인물, 작업자, 신호수 기준 이미지
│   ├── worker-001-front.png
│   └── worker-001.profile.md  # 얼굴형, 체형, 복장, PPE, 고정 특징 설명
├── model/ppe/                 # 안전모, 조끼, 안전화 등 PPE 기준 이미지
├── product/equipment/         # BCT, 덤프트럭, 장비, 제품 기준 이미지
│   ├── bct-trailer.png
│   └── bct-trailer.md         # 장비 형태와 색상 설명
├── ref/candidates/            # 아직 승인 전인 참고 이미지 후보
└── ref/approved/              # 프롬프트에 실제 반영할 승인 레퍼런스
    ├── animation-style.png
    └── animation-style.md     # 스타일, 질감, 카메라, 조명 설명
```

`generate_images.py`와 `generate_seedance.py`는 `model/cast`, `model/ppe`, `product/equipment`, `ref/approved`를 자동 스캔한다. 이미지 옆에 같은 이름의 `.md`를 두거나, 인물은 `worker-001.profile.md`처럼 프로필 설명을 두면 해당 설명이 모든 이미지/영상 프롬프트에 들어간다.

`ref/candidates`는 검색 후보 보관용이다. 실제 프롬프트에는 자동 반영하지 않으므로, 사용할 이미지는 `approve_reference.py`로 승인하거나 `ref/approved`로 옮긴 뒤 실행한다.

```bash
python3 scripts/approve_reference.py --project projects/fall-prevention --candidate animation-style.png
python3 scripts/analyze_reference_assets.py --project projects/fall-prevention --dry-run
```

`analyze_reference_assets.py --dry-run`은 유료 비전 호출을 하지 않는다. 현재는 이미지 옆 `.md` 설명을 우선 사용하고, 설명이 없으면 파일명 기반 placeholder를 `ref/approved/reference_assets.json`에 기록한다.

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

현재 MVP는 이 파일에서 PPTX 내부 이미지 미디어 12개를 추출하고, 해당 자료에 맞는 주제와 30초/6컷 스토리보드를 생성한다.

## 금지된 기본 동작

```bash
python3 scripts/generate_images.py --project projects/fall-prevention --live
python3 scripts/generate_seedance.py --project projects/fall-prevention --live
```

이미지 live 명령은 승인 게이트가 없으면 실패한다. Seedance live 명령은 추가로 `--execute-paid`가 없으면 실패한다.

## 이미지 생성 경로

기본 이미지 생성 경로는 OpenAI API가 아니라 Codex 내장 `imagegen` skill/tool이다.

운영 방식:

1. `generate_images.py --dry-run`이 상세 프롬프트와 imagegen 작업 지시서를 만든다.
2. Codex 에이전트가 `imagegen` skill을 사용해 실제 이미지를 생성한다.
3. 생성 결과는 `$CODEX_HOME/generated_images/...`에만 두지 않고 `projects/<slug>/images/draft/scNN_vNNN.png`로 이동 또는 복사한다.
4. 승인된 이미지는 `projects/<slug>/images/approved/`로 이동하고, 기존 승인 이미지는 덮어쓰지 않는다.

OpenAI Image API 또는 CLI fallback은 사용자가 명시적으로 API/CLI 경로를 요청할 때만 사용한다.

이미지 프롬프트 작성 기준은 [docs/imagegen-prompting-references.md](./docs/imagegen-prompting-references.md)에 둔다. 프롬프트는 이전 장면, 현재 예방 행동, 다음 장면 연결을 모두 포함해야 하며, 고립된 체크리스트 이미지처럼 만들지 않는다.

Codex imagegen 실행 준비 명령:

```bash
python3 scripts/generate_images.py --project projects/fall-prevention --live --only sc01
```

이 명령은 실제 API를 호출하지 않고 `prompts/imagegen_jobs.json`을 만든다. Codex는 이 job spec을 보고 `imagegen` skill/tool로 이미지를 만든 뒤, 결과 파일을 다음 명령으로 프로젝트에 수거한다.

```bash
python3 scripts/record_image_output.py \
  --project projects/fall-prevention \
  --scene-id sc01 \
  --generated-file /path/to/generated-image.png

python3 scripts/validate_images.py --project projects/fall-prevention --only sc01
python3 scripts/approve_image.py --project projects/fall-prevention --scene-id sc01
```

재생성은 기존 draft/approved 파일을 덮어쓰지 않는다.

```bash
python3 scripts/generate_images.py --project projects/fall-prevention --live --only sc01 --regenerate
```

## 영상 생성 경로

영상 생성은 Higgsfield CLI의 `seedance_2_0`을 사용한다. 비용 통제 때문에 기본 테스트 경로는 10초, 5초 클립 2개, 최대 3회 이하로 제한한다.

```bash
python3 scripts/generate_seedance.py --project projects/fall-prevention --dry-run
python3 scripts/validate_scene_links.py --project projects/fall-prevention
python3 scripts/approve_gate.py --project projects/fall-prevention --gate image_to_video --estimated-credits 35

python3 scripts/generate_seedance.py \
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
python3 scripts/generate_seedance.py \
  --project projects/fall-prevention \
  --live \
  --execute-paid \
  --test-seconds 10 \
  --max-attempts 1 \
  --validation-run
```

생성 후 검증:

```bash
python3 scripts/inspect_video.py \
  --project projects/fall-prevention \
  --clip projects/fall-prevention/video/clips/<clip>.mp4 \
  --tool scenelens \
  --no-transcript

python3 scripts/validate_video.py --project projects/fall-prevention --expected-clips 1
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

새 세션이나 재개 시에는 `hooks/session-start-anchor.py`가 짧은 mission anchor를 출력한다.
이 앵커는 live/유료 호출 금지, no narration/TTS, 스토리보드 우선, 병렬 role evaluator,
Arbiter consensus, critical veto, RALPH escalation, evidence 보존 규칙을 다시 주입하기 위한
세션 시작용 안전장치다.

`llm-wiki/evaluation-rounds.md`는 원본 evidence의 복사본이 아니라 다음 라운드 판단을 돕는
요약 인덱스다. 이미지 재생성 프롬프트를 만들 때 반복 blocker를 확인하고, 같은 문제가 여러
번 반복되면 단순 재생성이 아니라 스토리보드/레퍼런스 수정으로 에스컬레이션하는 근거로 쓴다.
원본 이미지, 영상, JSON evidence의 source of truth는 각 프로젝트 폴더에 둔다.

1. 시나리오/스토리보드 QA

```bash
python3 scripts/evaluate_storyboard.py --project projects/fall-prevention
```

평가 항목:

- `source_grounding_score`: 교육자료 출처가 있는가
- `causal_flow_score`: 사고 예방 행동의 원인과 결과가 보이는가
- `granularity_score`: 컷이 너무 넓지 않고 이미지/영상 생성 가능한 단위인가
- `text_delivery_score`: 전달 문구가 자막/오버레이 계약으로 잡혀 있는가
- `continuity_score`: start/end keyframe과 연속성 제약이 있는가

2. 스토리보드-이미지 QA와 RALPH loop

```bash
uv run python scripts/validate_images.py --project projects/fall-prevention --only sc01
```

`qa/image_qa_loop.json`에 `ralph_loop`가 기록된다. 이미지가 기준 미달이면
`needs_regeneration` 상태와 함께 부족한 지점, 재생성 프롬프트가 남는다. 이미지
단계는 비용이 영상보다 낮고 수정 효과가 크므로, blocked scene은 점수 기준을 넘을
때까지 재생성/검증 루프를 반복한다.

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

3. 스토리보드-이미지-영상 QA와 제안 전용 루프

```bash
python3 scripts/inspect_video.py --project projects/fall-prevention --clip <clip.mp4> --tool scenelens --no-transcript
python3 scripts/validate_video.py --project projects/fall-prevention --expected-clips 1 --clip <clip-name>.mp4
```

영상은 유료 생성이므로 자동 재생성하지 않는다. 기준 미달이면
`qa/video_regeneration_proposals.json`에 `propose_only` 모드로 부족한 지점과 다음
수정 제안만 남긴다. 다음 유료 생성은 사용자가 승인한 경우에만 실행한다.

## 원칙

- 기존 샘플 프로젝트와 독립적으로 설계한다.
- 스토리보드 승인 전에는 영상 생성 작업을 실행하지 않는다.
- 영상 생성은 크레딧과 재생성 비용이 있으므로 승인 게이트를 통과한 경우에만 실행한다.
- 모든 안전 관련 문구는 교육자료, SOP, 사용자 승인 메모 중 하나로 추적 가능해야 한다.
