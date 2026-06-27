# 권고 — 통합 액션 플랜

**리뷰 전체의 단일 실행 문서입니다.** [03-issues.md](./03-issues.md)와 [06-latent-defects.md](./06-latent-defects.md)는 진단, [07-architecture-improvements.md](./07-architecture-improvements.md)는 설계를 담당하며, 회귀 테스트는 마스터 백로그([04-test-coverage.md](./04-test-coverage.md) §제안, 아래에서 "테스트 #N"으로 참조)에 있습니다. 결함별 교차 참조표는 [README.md](./README.md) §추적성 매트릭스 참조.

작업은 **3개 레이어**로 구성되며, 레이어 간 중첩은 중복 작업이 아니라 의도된 것입니다:

| 레이어 | 정의 | 출처 |
|---|---|---|
| **Tactical fix** | 결함을 지금 제거하는 최소 변경 | 아래 배치들 |
| **Containment** | 폭발 반경을 제한하는 방어 가드 | 06의 "Containment" 줄, 아래 배치에 흡수됨 |
| **Structural** | 결함 클래스 자체를 표현 불가능하게 만드는 deep-module 리팩토링 | 07 슬라이스 S1–S7 |

오늘 배포한 전술 수정은 나중에 해당 구조 슬라이스에 *흡수되는 것이 정상*입니다 (예: `image_evaluation_flow.py`의 C-2 가드는 S4가 들어오면 ledger 모듈로 이동). 전술 먼저 배포하고, 슬라이스가 이를 흡수하게 하십시오.

(위험 × 노력) 순으로 정렬. 각 배치는 독립 배포 가능. ID는 03(C/H/M/L)과 06(LD)을 참조.

## Batch 1 — 안전 스토리의 정합성 (최우선, 약 반나절)

1. **C-2** 통과한 장면의 RALPH 라운드 기록 중단 (`image_evaluation_flow.py`에 3줄 가드) + 테스트 #1. 코드베이스에서 줄당 가치가 가장 높은 수정: 증거 원장 전체의 의미를 보호합니다. *(구조적 후속: S4.)*
2. **H-1** live 분기에서 `require_gate`/`_require_external_upload`를 `build_seedance_live_plan` 앞으로 이동; 우회 고착화 테스트를 테스트 #2로 교체. *(구조적 후속: S6.)*
3. **H-5** `video_qa.py`의 기본값 없는 `next(...)`를 기본값 조회 + `HarnessError`로 교체.
4. **H-6** `register_source`에 실제 타임스탬프.
5. **LD-4** 4개 `subprocess.run` 지점 전부에 `timeout=` 추가, `TimeoutExpired` → `HarnessError` 변환 (테스트 #10). Seedance 지점은 현재 상한 없는 *유료* 호출 — 다듬어진 버전(프로세스 그룹 kill, 공유 러너)은 S5를 기다리더라도 이것만은 첫 배치에 들어가야 합니다. **미결 운영 결정:** 도구별 timeout 값, 특히 Higgsfield SLA + 여유분.

## Batch 2 — 상태 내구성과 락 (약 반나절)

이전 버전 계획이 뭉뚱그렸던 두 가지 분리 가능한 관심사를 명시적으로 나눕니다:

6. **무조건 — 원자성과 손상 처리 (LD-1, LD-2).** 락 결정과 무관하게:
   - `write_json` → tmp 파일에 쓴 뒤 `os.replace` (테스트 #9).
   - `read_json` → `JSONDecodeError`/`FileNotFoundError`를 파일명을 명시한 `HarnessError`로 래핑.
   - `_read_round_entries` → 잘린 마지막 JSONL 줄은 허용, 그 외 손상은 raise (테스트 #8).
7. **결정 필요 — 락 (C-1, M-4, LD-6).** 하나를 선택:
   - *Option A (OMO 루프가 동시 실행될 가능성이 있다면 권장):* `file_lock`을 원자적으로(`open("x")`) 만들고 `write_json`/`write_jsonl`/위키 append를 통과시키며 테스트 #6 추가.
   - *Option B:* `AGENTS.md`에 하니스를 단일 프로세스로 선언, `file_lock` 삭제, `assert_unlocked`를 `assert_no_crash_marker` 같은 정직한 이름으로 변경.
   어느 쪽이든 괜찮습니다; 유일하게 틀린 선택은 현재 상태(보호를 암시하는 데드 락 코드)입니다. **참고:** 07의 슬라이스 S1은 Option A를 전제합니다; Option B에서도 S1은 유효하되 원자성·손상 정책·정식 경로만 소유합니다 — 어느 쪽이든 할 가치가 있는 슬라이스입니다.

## Batch 3 — 훅 강화 (약 반나절)

8. **C-3** 보호 경로 훅이 `protected_paths.json`을 읽고, 소문자 정규화하고, 앵커드 매칭. 하드코딩 목록 삭제 (테스트 #3).
9. **M-5** 대소문자 무시 secret 패턴 + 키 형태 정규식.
10. **M-6** stop-sentinel을 CWD가 아닌 저장소 루트 기준으로 해석.
11. **M-7** `posttooluse-*` no-op들을 개명하거나 구현.

## Batch 4 — 운영 경로 견고화 (약 1일)

12. **H-4a/H-4b** `record_image_output`: 재시도 시 버전 증가 (테스트 #5) + 출력 경로 포함 검사 (테스트 #4). *(구조적 후속: S3.)*
13. **LD-3** 버전 산술: `_next_draft_path`와 `_next_preserved_approved`에서 count+1 대신 max-version+1 (테스트 #11). *(구조적 후속: S3.)*
14. **H-2** 레퍼런스 자산별 정식 위치 1곳; 루트 레벨 승인 파일 이중 주입 중단. *(구조적 후속: S2.)*
15. **LD-8** 캐스트 프로필 사이드카 glob 정확 일치 (접두사 과매칭 제거). *(구조적 후속: S2.)*
16. **M-2** `seedance_live.py`의 프롬프트 문자열 수술 대신 구조화된 `duration_sec`.
17. **M-3** `transcript_enabled` 기본값을 `False`로.
18. **M-8** 손상 PPTX에 비어 있지 않은 경고.
19. **LD-5** `_run_understand_video`: 이전 검사 출력 삭제 전에 새 breakdown 확보.
20. **LD-7** 씬 링크 검증기: 장면 `id`와 리스트 인덱스 대조; 빈 장면 리스트에서 실패.
21. **LD-10** ffprobe 성공 경로 JSON 파싱 가드. *(구조적 후속: S5.)*

## Batch 5 — QA 신호의 정직성 (설계 작업, 일정 별도 배정)

22. **M-1** `review_scene_image`의 하드코딩 5점은 시스템이 *보고하는 것*과 *아는 것* 사이의 가장 큰 간극입니다. role evaluator가 실제 점수를 내기 전까지 모든 출력 JSON에 placeholder 점수를 그렇다고 표기하고(`"score_source": "placeholder"`), `MINIMUM_TOTAL_SCORE`는 삭제 또는 재산정. LLM 기반 역할 평가가 들어오면 스키마 변경 없이 이 필드들이 실제가 됩니다.
23. **H-3** 위키 반복 blocker 임계값을 arbiter와 같게(3) 정렬 — README가 미래 세션에 재생성 판단 시 *위키를 쓰라고* 지시하기 때문. *(구조적 후속: S4.)*

## Batch 6 — 위생 (다른 PR에 기회 봐서 포함)

24. [03-issues.md](./03-issues.md)의 L-1 표: 공유 `_latest_draft` 헬퍼, 단일 길이 키, 조기 장면 필터링, fixture 의존 테스트 `pytest.skip` (테스트 #7), `error_log.append_error` 연결 또는 제거.
25. **LD-9** 호출당 원장 1회 읽기 (canonical은 06; S4가 먼저 배포되면 흡수됨 — 그 경우 전술 버전 생략).

## 구조 트랙 (병행, Batch 1–2 이후)

[07-architecture-improvements.md](./07-architecture-improvements.md)의 슬라이스 7개가 이 계획의 구조 레이어입니다 — **S1(ProjectStore)** 부터 시작, 이후 S2/S3 순서 무관. 슬라이스는 위에서 *"구조적 후속"* 으로 표시된 전술 수정을 흡수합니다; 슬라이스가 들어오면 대체된 전술 가드는 둘 다 유지하지 말고 삭제하십시오.

## 바꾸지 말 것

- 게이트 아키텍처, 합의/veto 순서, propose-only 영상 정책, write-once 승인 의미론, evidence-bundle 격리 패턴은 모두 설계대로 올바릅니다. 그 *내부의* 버그를 고치고, 재설계는 하지 마십시오.
- 위 수정을 진행하는 동안 나레이션/TTS, 병렬 imagegen, 영상 자동 재생성을 추가하지 마십시오 — 현재의 절제가 곧 제품입니다.
