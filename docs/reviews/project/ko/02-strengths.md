# 강점 — 잘된 부분

하니스가 성장해도 보존할 가치가 있는 패턴들입니다. 각 항목에 구현 파일을 명시했습니다.

## 1. 유료/라이브 생성에 대한 심층 방어 (이 프로젝트 최고의 속성)

"승인 없이 라이브 금지" 약속이 **독립된 3개 레이어**에서 강제되므로, 어느 한 레이어를 지워도 보장이 깨지지 않습니다:

- **라이브러리 레이어** — `generation.py`가 `generate_images`/`generate_seedance` 내부에서 `require_gate()`와 `_require_external_upload()`를 호출; `generate_seedance`는 추가로 게이트 검사 *이전에* `--execute-paid` 없이는 하드 실패 (`generation.py:117`).
- **훅 레이어** — `hooks/pretooluse-live-veto.py`가 라이브 명령을 행동 차원에서 거부.
- **정책 레이어** — `omo_ralph.py`가 Seedance를 루프 실행자의 금지 행동 목록에 명시, `video_qa.py`는 모든 제안에 항상 `paid_generation_allowed: false`와 "Do not regenerate automatically"를 기록.

`--live` 위에 `--execute-paid`를 2차 인증으로 얹은 것은 유료 API에 정확히 맞는 설계입니다.

## 2. 게이트가 플래그가 아니라 실제 검사

`gates.approve_gate`는 Gate 1 기록 전에 전체 스토리보드 QA를 재실행합니다(`_require_storyboard_qa`) — 실패한 스토리보드는 승인될 수 없습니다. `gate_validation.py`는 Gate 2를 5개 독립 조건으로 강제합니다: `external_upload_allowed`, 클립 수, `video_prompts.json` 존재, 승인 이미지 파일 존재, `image_qa_loop.json` 통과. 일부 장면만 QA된 상태로는 영상 단계에 진입할 수 없습니다.

## 3. 승인 산출물은 write-once

`imagegen_jobs.approve_image`는 절대 덮어쓰지 않습니다: 기존 승인 파일을 버전 붙은 보존 이름으로 먼저 리네임한 뒤 새 드래프트를 복사합니다(`_next_preserved_approved`). 드래프트 기록은 버전 증가 파일명(`scNN_vNNN.png`)을 씁니다. 증거 원장과 결합하면 완전한 롤백 추적이 가능합니다. `test_roadmap_bundle2.py`에서 end-to-end로 테스트됨.

## 4. 설계 가치로서의 증거와 감사 가능성

- append-only JSONL 원장(`qa/evaluation_rounds.jsonl`) 덕분에 반복 횟수와 blocker 이력이 재시작·부분 실행에도 살아남음.
- 라운드별 evidence bundle(`evaluation_rounds.write_evaluation_bundle`)로 격리 평가자가 생성자의 맥락 없이 채점 — 생성자가 자기 산출물을 승인하지 못함.
- 사람이 읽는 위키(`llm-wiki/evaluation-rounds.md`)에 라운드별 점수, blocker, 개선 노트, 다음 프롬프트 메모가 누적.
- `seedance_live._redact_public_urls`가 실행 로그 저장 전에 URL을 마스킹 (테스트됨).
- 저장소의 `evidence/` 폴더에 red/green 테스트 기록이 실재 — 규율이 문서가 아니라 실천이었음을 보여줌.

## 5. veto가 올바른 합의 설계

`evaluation_consensus.decision()`은 어떤 다수결 로직보다 *먼저* `critical_veto`를 처리합니다 — safety/continuity critical veto 1건은 표결로 뒤집을 수 없습니다. 문서화된 규칙("전원 승인, 또는 N-1 승인 + 조건부 1건")이 정확히 구현되어 있습니다. `test_evaluation_arbiter.py::test_critical_safety_veto_overrides_consensus`가 증명.

## 6. 무지성 재생성 대신 에스컬레이션

blocker-signature 메커니즘(`blocker_signatures.py` + `evaluation_arbiter._repeated_blockers`)은 "같은 실패 3회"를 4번째 동일 재생성이 아니라 구조적 에스컬레이션(`revise_storyboard` + `regeneration_delta`)으로 전환합니다. 이미지-스토리보드 비용 비대칭에 맞는 경제학이며, arbiter 쪽 임계값 산술(이전 + 현재 ≥ 3)도 정확합니다.

## 7. 일관된 운영 골격

- 스크립트 30개 전부 동일한 `cli.run_boundary` 패턴: `HarnessError` → 깔끔한 stderr 메시지 → exit 1. 예상된 실패에 raw traceback 없음.
- 모든 파일 처리가 `pathlib.Path` 사용 — 이 저장소 자체가 위치한 한글·공백 경로가 문자열 파싱 위험 없이 동작.
- 전 모듈에 `from __future__ import annotations`, 작고 단일 목적인 모듈(중앙값 약 100줄).
- JSON 계약에 스키마(`schemas/*.json`)와 프로젝트 템플릿 디렉토리 존재.

## 8. 도메인 모델링 품질

`source_facts.py`와 `storyboard.py`는 진짜 EHS 도메인 지식(사각지대, 신호수 위치, 후진 작업, BCT/덤프트럭 구분)을 인코딩하며, 출처 인용이 자료 추출에서 각 장면 노드까지 관통합니다. `validation.py`는 키프레임 내 한글 텍스트 금지 계약(`image_prompt_en` 정규식, 자막 길이 상한, 나레이션 필드 금지)을 강제 — 자막 기반 전달 미션에 정확히 부합합니다.

## 9. 제값 하는 테스트

happy path만이 아니라 실패 경로를 테스트합니다: 게이트 없는 라이브는 올바른 stderr와 함께 non-zero로 종료, RALPH 캡 테스트는 원장에 20개를 사전 주입, 반복 blocker 테스트는 이전 2라운드를 심고 3번째에 에스컬레이션을 단언, no-overwrite 테스트는 보존 파일 리네임을 단언. 대부분 red/green 증거 기록이 존재합니다. (공백은 [04-test-coverage.md](./04-test-coverage.md) 참조 — Gate 2 plan-only 우회를 *고착화하는* 테스트 1건 포함, 이슈 H-1; 테스트 칭찬은 그 기대값에는 해당하지 않습니다.)
