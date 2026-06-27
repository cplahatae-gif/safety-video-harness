# 포팅 1순위 검증: 라이브러리 견고화 번들 + external_tools

> 2026-06-27 / 출처: `project-review/08-codex-vs-claude-port-guide.md` 1순위
> 증거 로그: `evidence/port-rounds/bundle1-robustness-pytest.txt`

## 이식한 것 (테스트_코덱스 → 테스트_클로드, surgical)

| 파일 | 변경 | 검증 테스트 |
|---|---|---|
| `safety_video_harness/external_tools.py` | **신규**. `run_tool`/`run_tool_json` — subprocess 타임아웃 강제, TimeoutExpired→HarnessError | (간접) |
| `safety_video_harness/locks.py` | `file_lock` O_EXCL 원자 취득(`open("x")`) — TOCTOU 제거 | test_write_json_rejects_existing_lock_marker |
| `safety_video_harness/io.py` | `read_json` 누락/파싱오류/비-dict→HarnessError; `write_json` file_lock+tmp+os.replace 원자 쓰기; `write_jsonl` file_lock | test_read_json_wraps_decode_errors |
| `safety_video_harness/evaluation_rounds.py` | `_read_round_entries` 찢어진 **마지막** JSONL 줄만 관대 skip, 그 외 corrupt는 raise | test_completed_iterations_tolerates_torn_final_jsonl_line |
| `safety_video_harness/scene_links.py` | 빈 스토리보드 raise; scNN 순번(scene id) 불일치 검출 | test_scene_link_validation_rejects_empty_storyboard, ..._checks_scene_id_order |
| `safety_video_harness/video_qa.py` | h264 스트림 부재 None가드→raise; ffprobe를 `run_tool_json`(timeout 30s)로 | test_video_review_reports_missing_h264_as_harness_error |
| `safety_video_harness/seedance_live.py` | `_run_cli`를 `run_tool(..., 1500, ...)`로(higgsfield 무한 행 제거) | test_seedance_cli_timeout_raises_harness_error |
| `safety_video_harness/imagegen_jobs.py` | `record_image_output` 프로젝트 외부 경로 차단; 드래프트/승인 버전 `len()+1`→`max()+1` | test_record_image_output_rejects_paths_outside_project, test_next_draft_path_skips_version_gaps |
| `tests/test_review_regressions.py` | **신규**. 라이브러리 9테스트(8결함+락1) | — |

## 의도적으로 제외한 것 (08 문서 가드대로)

- **아키텍처 혼입**: `evaluation_rounds` 에스컬레이션 임계 2→3, `video_qa` `transcript_enabled` 기본 True→False, `imagegen_jobs` `codex_cli_imagegen`→`codex_builtin_imagegen` 및 instruction 문구 — 전부 Claude 설계와 충돌하므로 미반영(Claude 현행 유지).
- **분리 리팩터/기능**: `image_versions.py` 모듈, `asset_lock`/`reference_media_pack`/`production_consistency_policy` 필드, `collect_image_outputs` — 별도 작업으로 미반영(max버전·path가드만 인라인 선별 이식).
- **훅 회귀 5테스트**(protected-path/secret/stop-sentinel/schema/evidence): Codex의 argv 훅 기준이라 Claude의 stdin-JSON 훅 프로토콜과 불일치 → 미이식. 탐지 로직(secret 정규식 등) 체리픽은 08 문서 Medium 항목으로 후속.

## 검증 결과

- 신규 회귀 테스트: **9 passed**.
- 전체 스위트: **86 passed, 1 failed**.
- 유일한 실패 `test_story_flow_quality.py::test_validate_images_writes_scored_loop_summary`는 **내 변경과 무관한 기존 실패**(변경을 `git stash`로 되돌려도 동일 실패). 원인: 테스트의 `run_cli`가 venv가 아닌 **시스템 `python3`로 `validate_images.py`를 서브프로세스 실행**하는데 그 인터프리터에 **Pillow 미설치** → `"Pillow is required for readable image QA"`로 total_score 0 → passed=False. 환경 의존 문제(코드 결함 아님).

---

# 2순위(시각 QA 게이트) — 독립 부분만 이식

사용자 결정: 합격기준 24→44 상향·수동리뷰 필수화(정책 변경)는 **보류**, 독립·무충돌 부분만 이식.

| 파일 | 변경 |
|---|---|
| `safety_video_harness/image_evaluation_flow.py` | 통과(non-blocked) 씬 조기종료 — iteration 미증가·원장 중복기록 제거(3줄) |
| `safety_video_harness/image_manual_review.py` | **신규** 독립 모듈(io만 의존). 5개 visual-lock 축 + 매뉴얼리뷰 로드/페이로드 헬퍼 |
| `safety_video_harness/ralph_prompt.py` | **신규** 공유 `QUALITY_PRESSURE` 상수 |
| `image_qa.py` / `prompt_contract.py` | `QUALITY_PRESSURE`를 재생성·이전블로커 프롬프트에 주입(기존 테스트 앵커 "Regenerate scNN"·"Do not repeat:" 보존) |
| `tests/test_image_manual_review.py` | **신규** 4 테스트 |

**보류**: `image_qa` 하드게이트(24→44+수동리뷰 필수), `image_visual_review.py`(asset_lock 의존), rubrics 44 — 모두 게이트 정책 변경과 함께 후속.

# 3순위(문서 doctrine + approve_reference role)

| 파일 | 변경 |
|---|---|
| `safety_video_harness/reference_profile.py` | `APPROVED_REFERENCE_ROLES` 맵 + `approved_reference_dir()` + `approve_reference(..., role="root")` — `ref/approved/{person,work,space,style,camera,lighting}` 라우팅. 기본 root = 기존 동작 동일(하위호환). AGENTS.md "Ask where each reference belongs" 구현 |
| `scripts/approve_reference.py` | `--role` 인자 추가 |
| `CONTEXT.md` | **신규** 도메인 용어집 + 비협상 정책 + 구조 오리엔테이션(Claude 모듈명으로 적응: reference_profile/imagegen_jobs/external_tools) |
| `CLAUDE.md` | "작업 전 필수 문서"에 CONTEXT.md 연결 |
| `tests/test_reference_role.py` | **신규** 4 테스트(하위호환·역할라우팅·잘못된역할·dir매핑) |

**보류**(deferred 기능과 결합): AGENTS.md asset-lock/QA축 doctrine, evaluation-rubrics 44 — asset_lock·시각QA게이트 이식 후.

## 최종 검증

- 전체 스위트: **94 passed, 1 failed**(3개 번들 누적, 회귀 0).
- 유일 실패는 동일한 **기존 Pillow 환경 문제**(test_validate_images_writes_scored_loop_summary) — 내 변경과 무관.

## 후속

- (선택) Pillow 환경 문제 해결: 시스템 `python3`에 pillow 설치 또는 테스트 `run_cli`를 `sys.executable` 사용으로 수정.
- 다음(보류분): 시각 QA 하드게이트(24→44+수동리뷰 필수)·asset_lock 일관성 시스템·reference_catalog 통합·영상 최종 조립 — 각각 정책/대형 작업으로 별도 스케줄.
