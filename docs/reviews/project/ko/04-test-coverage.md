# 테스트 커버리지 평가

테스트 파일 21개. 전체 성격: 이 스위트는 *안전 계약*을 진짜 red/green 쌍으로 테스트하고 그 기록을 `evidence/`에 보관합니다 — 드물고 가치 있는 일입니다. 공백은 훅 레이어와, 테스트가 우연히 "정상"으로 고착화한 몇 개 경로에 몰려 있습니다.

## 잘 커버된 것 (증명하는 테스트와 함께)

| 보장 | 테스트 |
|---|---|
| 게이트 승인 없는 라이브 이미지/영상은 올바른 stderr와 함께 실패 | `test_mvp_flow.py`, `test_roadmap_bundle2.py` |
| RALPH 캡: 원장에 20라운드 사전 주입 → `max_iterations_reached` | `test_image_ralph_loop.py::test_image_qa_stops_ralph_after_max_iterations` |
| 3번째 동일 시그니처에서 반복 blocker 에스컬레이션 | `test_evaluation_arbiter.py::test_validate_images_escalates_after_three_repeated_blockers` |
| 재승인 시 승인 이미지 보존 (덮어쓰기 아닌 리네임) | `test_roadmap_bundle2.py` (테스트 2개) |
| Seedance 가드레일: `--execute-paid` 필수, 10초 캡, ≤3회, validation-run⇒max-attempts=1 | `test_seedance_live_guardrails.py` |
| Seedance 실행 로그 URL 마스킹 | `test_seedance_live_guardrails.py::test_seedance_live_run_log_redacts_public_output_url` |
| critical safety veto가 합의 다수결을 무효화 | `test_evaluation_arbiter.py::test_critical_safety_veto_overrides_consensus` |
| 단일 작성자 락이 승인 쓰기를 차단 (`assert_unlocked` 경로) | `test_roadmap_bundle1.py::test_approval_write_respects_single_writer_lock` |
| 한글/공백 경로 end-to-end | pytest `tmp_path` 하의 레미콘 fixture 테스트 |
| 자막/나레이션 금지 계약 | `test_subtitle_contract.py`, `test_no_narration_contract.py` |
| 스토리보드 분량/품질 계약 | `test_storyboard_density.py`, `test_storyboard_quality.py`, `test_story_flow_quality.py` |

## 공백

### 1. Gate 2 plan-only 우회를 고착화한 테스트 (이슈 H-1 연계)
`test_seedance_live_guardrails.py::test_seedance_live_plan_uses_two_five_second_clips_for_10s`는 게이트 승인 **없는** 프로젝트에서 `--live --execute-paid --plan-only`를 실행하고 `returncode == 0`을 단언합니다. H-1을 수정하면 이 테스트도 바꿔야 합니다; 현재는 우회를 적극적으로 보호하고 있습니다.

### 2. 훅 레이어가 거의 미테스트
- `pretooluse-protected-path-veto.py`: 테스트 없음 (대소문자 우회 테스트, `approvals.json` 드리프트 테스트 없음).
- `pretooluse-secret-veto.py`: 전혀 테스트되지 않음.
- `stop-sentinel-guard.py`: CWD 의존성(M-6) 포함 테스트 없음.
- `posttooluse-*`: 행동 테스트 없음 — no-op이라는 사실(M-7)과 일관됨; "실행되긴 하나" 테스트는 삭제되어도 통과할 것.
- `pretooluse-live-veto.py`와 `session-start-anchor.py`만 `test_plugin_structure.py`로 커버.

### 3. 반복 검증 시 원장 의미론 (C-2 연계)
*통과하는* 프로젝트에 `validate_images`를 반복 호출하고 반복 카운트가 그대로인지 단언하는 테스트가 없습니다. 캡 오염 버그가 무는 바로 그 시나리오입니다.

### 4. 동시성 / 락 획득
락 테스트는 수동 생성한 `.lock` 파일에 대한 `assert_unlocked`만 검사합니다. `file_lock` 획득/해제(데드 코드, C-1)나 경쟁하는 작성자 2개를 테스트하는 것이 없습니다.

### 5. 공허하게 통과하는 영상 테스트
`test_video_qa.py` / `test_video_regeneration_proposals.py`의 여러 테스트가 `if not source.exists(): return`으로 시작합니다 — MP4 fixture 없는 머신에서는 아무것도 테스트하지 않고 통과합니다. `pytest.skip("fixture missing")`을 써서 건너뛴 커버리지가 리포트에 보이게 해야 합니다.

### 6. `record_image_output` 경로 탈출 (H-4b 연계)
변조된 `imagegen_jobs.json` 출력 경로를 주입해 프로젝트 디렉토리 내 포함을 단언하는 테스트가 없습니다.

### 7. 운영자 명령의 재시도/멱등성
같은 장면에 `record_image_output`을 재실행하는 테스트가 없습니다 (현재 동작 — 복구 경로 없는 하드 실패 — 자체가 이슈 H-4a).

## 제안 신규 테스트 (우선순위 순)

> **이 목록이 마스터 회귀 테스트 백로그입니다.** [05-recommendations.md](./05-recommendations.md), [06-latent-defects.md](./06-latent-defects.md), [07-architecture-improvements.md](./07-architecture-improvements.md)는 재기술 대신 번호로 참조합니다.

1. `test_validate_images_does_not_increment_iterations_for_passing_scenes` — 검증을 N회 재실행, `current_iterations` 불변 단언 (C-2 회귀 가드).
2. `test_seedance_plan_only_requires_gate` — 현재의 우회 고착화 기대값 교체 (H-1).
3. `test_protected_path_veto_matches_json_and_is_case_insensitive` — `protected_paths.json` 항목 + 대소문자 변형으로 파라미터화 (C-3).
4. `test_record_image_output_rejects_paths_outside_project` (H-4b).
5. `test_record_image_output_retry_bumps_version` (H-4a).
6. `test_file_lock_blocks_second_writer` — C-1 반영 후 (05 Batch 2가 Option B/단일 프로세스를 선택하면 생략).
7. fixture 의존 영상 테스트를 `pytest.skip`으로 전환.
8. `test_ledger_tolerates_torn_final_line` — 잘린 마지막 JSONL 줄은 경고와 함께 건너뛰고, 그 외 손상은 `HarnessError` (LD-1).
9. `test_write_json_is_atomic` — tmp 쓰기와 replace 사이 크래시 시뮬레이션; 원본 파일 무결 단언 (LD-2).
10. `test_subprocess_timeout_raises_harness_error` — 도구 러너 지점별 멈춘 자식 프로세스 fake (LD-4).
11. `test_next_draft_path_skips_version_gaps` — v001 삭제 후 v002/v003 존재 시 다음 경로가 충돌하지 않아야 함 (LD-3; 06의 repro가 이 테스트가 됨).
