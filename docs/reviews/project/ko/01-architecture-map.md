# 아키텍처 지도 (줌아웃)

코드보다 한 층 위에서 본 그림: 모듈이 무엇이고, 누가 누구를 호출하며, 프로젝트의 도메인 어휘는 무엇인가.

## 도메인 용어집

| 용어 | 의미 |
|---|---|
| **하니스(Harness)** | 오케스트레이션 레이어 그 자체. 순서, 증거, 승인, 품질 루프를 통제하며 — 미디어를 직접 생성하지 않는다. |
| **스토리보드(Storyboard)** | 기준 계약 (`storyboard/scenes.json`). 이미지와 영상은 절대 스토리보드를 앞서가면 안 된다. |
| **Gate 1 / Gate 2** | `storyboard` 승인(스토리보드 QA 재실행)과 `image_to_video` 승인(비용 고지, `external_upload_allowed`, 전체 이미지 QA 커버리지 필요). |
| **RALPH 루프** | 조기 종료형 이미지 재생성 루프: 장면당 최대 20회, 통과 즉시 중단. |
| **Blocker signature** | QA 실패의 정규화된 식별자. 같은 장면에서 같은 시그니처가 3회 반복되면 재생성이 아니라 스토리보드/레퍼런스/프롬프트 수정으로 에스컬레이션. |
| **Role evaluator** | 기준별 병렬 평가자 (story match, identity, PPE, equipment, story flow, technical…). |
| **Arbiter** | 합의 규칙(전원 승인, 또는 조건부 1건 허용) 아래 역할 리뷰를 종합. safety/continuity critical veto는 어떤 다수결보다 우선. |
| **Evidence bundle** | 격리된 평가자에게 주는 자기완결 JSON — 생성자가 자기 산출물을 승인하지 못하게 한다. |
| **propose_only** | 영상 QA 실패 모드: 유료 영상은 절대 자동 재생성하지 않고 수정 제안만 기록. |
| **OMO** | 외부 루프 실행자/작업 관리자. 하니스 QA 산출물을 읽고 다음 명령을 고를 뿐, 품질을 직접 판정하지 않는다. |
| **Sliding chain** | 연속성 규칙: N번 장면의 end keyframe = N+1번 장면의 start keyframe — 인접 클립이 프레임을 공유. |

## 레이어 다이어그램

```text
┌────────────────────────────────────────────────────────────────────┐
│ 운영자 레이어                                                       │
│  scripts/*.py (엔트리포인트 30개)  — argparse → 라이브러리 호출      │
│  전부 cli.run_boundary로 래핑 (HarnessError → exit 1)               │
├────────────────────────────────────────────────────────────────────┤
│ 행동 가드 레이어 (hooks/, 권고 + 거부)                               │
│  pretooluse-live-veto · protected-path-veto · secret-veto          │
│  session-start-anchor · stop-sentinel-guard · posttooluse-* (noop) │
├────────────────────────────────────────────────────────────────────┤
│ 파이프라인 레이어 (safety_video_harness/)                            │
│  project → source_rendering/source_facts → storyboard              │
│  → prompt_team → prompt_contract → generation                      │
│  → imagegen_jobs (record/approve)  → seedance_live                 │
├────────────────────────────────────────────────────────────────────┤
│ QA / 평가 레이어                                                    │
│  storyboard_qa · image_qa · video_qa · video_inspection            │
│  stage_role_reviews → evaluation_consensus → evaluation_arbiter    │
│  image_evaluation_flow → evaluation_rounds (JSONL 원장 + 위키)      │
│  blocker_signatures · gates/gate_validation · costs · omo_ralph    │
├────────────────────────────────────────────────────────────────────┤
│ 기반 레이어                                                         │
│  io (read/write_json[l]) · locks · errors · error_log · validation │
│  assets (레퍼런스 스캔) · style_guides · reference_profile          │
└────────────────────────────────────────────────────────────────────┘
```

## 파이프라인 단계와 담당 모듈

고정된 17단계 순서(README 기준). 코드 매핑:

| 단계 | 엔트리 스크립트 | 라이브러리 모듈 |
|---|---|---|
| 프로젝트 초기화·자료 등록 | `init_project.py`, `register_sources.py` | `project.py` |
| PPTX 렌더링·주제 추출 | `render_pptx_sources.py`, `extract_topics.py`, `select_topic.py` | `source_rendering.py`, `source_facts.py`, `project.py` |
| 레퍼런스 인테이크·스타일 DNA | `search_references.py`, `approve_reference.py`, `analyze_reference_assets.py`, `extract_style_dna.py` | `assets.py`, `reference_profile.py`, `style_guides.py` |
| 스토리보드 | `plan_storyboard.py` | `storyboard.py` (`source_facts.py`의 레미콘 인지 장면 플랜) |
| 스토리보드 QA + Gate 1 | `evaluate_storyboard.py`, `approve_gate.py` | `storyboard_qa.py`, `gates.py` |
| 이미지 프롬프트팀 preflight | `plan_image_prompt_team.py` | `prompt_team.py` (lead-style → scene agents → arbiter → coordinator) |
| 이미지 프롬프트·잡 | `generate_images.py` | `generation.py`, `prompt_contract.py`, `imagegen_jobs.py` |
| 이미지 기록·승인 | `record_image_output.py`, `approve_image.py` | `imagegen_jobs.py` (버전 드래프트, 보존형 승인) |
| 이미지 QA / RALPH | `validate_images.py`, `plan_omo_image_ralph.py` | `image_qa.py`, `image_evaluation_flow.py`, `omo_ralph.py` |
| 씬 링크 검증 | `validate_scene_links.py` | `scene_links.py` (sliding chain) |
| Gate 2 + 비용 | `approve_gate.py`, `estimate_video_cost.py` | `gates.py`, `gate_validation.py`, `costs.py` |
| Seedance dry-run / live | `generate_seedance.py` | `generation.py`, `seedance_live.py` (Higgsfield CLI, `--execute-paid`) |
| 영상 검사·QA | `inspect_video.py`, `validate_video.py` | `video_inspection.py`, `video_qa.py` (propose_only) |
| 자막 (나레이션/TTS 없음) | `plan_subtitles.py` | `subtitles.py` |

## 평가 기계 — 호출 그래프

```text
validate_images (generation.py)
 ├─ _image_review_items → 장면들 + 합성 final-keyframe 장면
 ├─ review_scene_image (image_qa.py)         # 실질 검사: story_flow + 이미지 파일
 └─ record_image_evaluation_rounds (image_evaluation_flow.py)
     ├─ completed_iterations (evaluation_rounds.py)   # JSONL 원장 읽기
     ├─ image_role_reviews (stage_role_reviews.py)    # 역할별 판정으로 분리
     ├─ aggregate_arbiter_decision (evaluation_arbiter.py)
     │   ├─ consensus_result / debate_triggers (evaluation_consensus.py)
     │   ├─ _repeated_blockers ← blocker_signatures.py + 원장 이력
     │   └─ qa/arbiter_decisions/... + qa/debates/... 기록
     ├─ write_evaluation_bundle → qa/evaluation_bundles/image/scNN/round_NNN.json
     └─ record_evaluation_round → qa/evaluation_rounds.jsonl + llm-wiki/evaluation-rounds.md
```

스토리보드 QA와 영상 QA도 같은 척추(`stage_role_reviews` → consensus → arbiter → rounds)를 재사용하며, 단계별 평가자만 `storyboard_qa.py` / `video_qa.py`에 따로 둔다.

## 상태 파일 (프로젝트별)

| 파일 | 작성자 | 역할 |
|---|---|---|
| `project_config.json` | `project.py`, `storyboard.py` | 길이, 분량, 스타일 가이드, 비용 정책 |
| `approvals.json` | `gates.py` | Gate 1 / Gate 2 상태 — 단일 강제 체크포인트 |
| `storyboard/scenes.json` | `storyboard.py` | 기준 계약 |
| `prompts/image_prompts.json`, `video_prompts.json`, `imagegen_jobs.json` | `generation.py`, `imagegen_jobs.py` | 생성 작업 지시서 |
| `qa/evaluation_rounds.jsonl` | `evaluation_rounds.py` | append-only 기계 원장 (반복 횟수, blocker 이력) |
| `qa/image_qa_loop.json` | `image_qa.py` | Gate 2와 OMO가 소비하는 RALPH 상태 |
| `llm-wiki/evaluation-rounds.md` | `evaluation_rounds.py` | 라운드별 사람/LLM용 학습 노트 |
| `.harness/DONE` | 운영자 | 세션 가드용 stop-sentinel |

## 문제 발생 시 가장 먼저 볼 곳

- **막혀야 할 라이브 호출이 실행됨** → `gates.require_gate`, `generation.py`의 live 분기, 그다음 훅.
- **반복 횟수가 이상함** → `evaluation_rounds.completed_iterations` + 원장 JSONL (이슈 C-2 참조).
- **프롬프트에 레퍼런스 블록이 중복/누락** → `assets.py` 디렉토리 역할 (부모/자식 중첩, H-2 참조).
- **장면이 재생성에서 빠져나오지 못함** → `qa/arbiter_decisions/image/<scene>/`의 arbiter 결정과 `blocker_signatures`.
