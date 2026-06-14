# 프로젝트 리뷰 — Safety Video Harness

**리뷰 일자:** 2026-06-12
**리뷰 대상 브랜치:** `codex/session-anchor-mas-evaluation` (HEAD `2a91849`)
**범위:** `safety_video_harness/` 모듈 40개 전체(약 4,400줄), CLI 스크립트 30개, 훅 9개, 테스트 파일 21개, 스키마, 플러그인 설정.
**방법:** 3단계로 진행. **1단계** — 독립 코드 리뷰 3개를 병렬 수행(핵심 파이프라인 / QA-평가 서브시스템 / 스크립트·훅·테스트)하고 모든 critical 지적을 수동 재검증. 오탐으로 판명된 지적 1건은 제외. **2단계** — 잠재 결함 진단(`/diagnose` 방식): 의심 지점을 최소 repro 스크립트로 확인하거나 정적 결함으로 분류. **3단계** — 검증된 결함에 앵커된 아키텍처 심화 분석.

## 총평

이 하니스는 안전 우선 원칙으로 잘 설계된 오케스트레이션 레이어입니다. 핵심 약속 — *명시적 게이트 없이 유료 생성 금지, 스토리보드 우선 순서, 승인 산출물 덮어쓰기 금지, 모든 것에 증거 남기기* — 가 문서에만 있는 것이 아니라 Python 라이브러리 레이어에서 실제로 강제됩니다. 심층 방어(defense-in-depth)도 실재합니다: 훅을 전부 삭제해도 라이브러리의 `require_gate` / `--execute-paid` / `external_upload_allowed` 검사가 라이브 **실행**을 차단합니다(단, 계획 단계에 예외 1건: `--plan-only`가 현재 게이트 검사 전에 유료 경로 계획 파일을 기록함 — 이슈 H-1).

약점은 다음 다섯 영역에 집중되어 있습니다.

1. **락이 환상임** — `file_lock`은 데드 코드이고, `assert_unlocked`는 check-then-act 패턴이라 동시 실행 시 아무것도 보호하지 못함 (C-1).
2. **상태 파일이 내구적이지 않음** — 비원자적 쓰기로 `approvals.json`/JSONL 원장이 손상될 수 있고, 잘린 한 줄이 모든 QA 명령을 raw traceback과 함께 마비시킴 (LD-1, LD-2 — 둘 다 repro로 확인).
3. **통과한 장면이 RALPH 반복 원장을 오염시킴** — 정상 프로젝트를 재검증할 때마다 반복 횟수가 20회 캡을 향해 부풀어 오름 (C-2).
4. **외부 호출에 timeout이 전혀 없음** — ffprobe, tesseract, inspection 스크립트, 그리고 *유료* Higgsfield CLI 모두 하니스를 무한정 멈출 수 있음 (LD-4).
5. **훅이 라이브러리보다 약함** — 부분 문자열 매칭, 대소문자 구분, 그리고 `protected_paths.json`과 이미 어긋난 하드코딩 목록 (C-3).

이 중 어느 것도 프로젝트가 현재 운영 중인 단일 사용자·단일 프로세스 happy path를 깨뜨리지는 않습니다. 그러나 하니스가 재사용되거나, 병렬화되거나, 작성자가 아닌 사람이 신뢰하게 되는 순간 전부 문제가 됩니다.

## 문서 색인

| 파일 | 역할 | 내용 |
|---|---|---|
| [01-architecture-map.md](./01-architecture-map.md) | 오리엔테이션 | 줌아웃 지도: 레이어, 모듈, 호출 관계, 도메인 용어집 |
| [02-strengths.md](./02-strengths.md) | 진단 | 진짜 잘된 부분 (계속 유지할 것) |
| [03-issues.md](./03-issues.md) | 진단 | 1단계 이슈 (C/H/M/L), file:line과 수정안 포함 |
| [04-test-coverage.md](./04-test-coverage.md) | 진단 + **마스터 테스트 백로그** | 테스트 21개가 실제로 보장하는 것, 공백, 그리고 다른 문서가 번호로 참조하는 회귀 테스트 목록 |
| [05-recommendations.md](./05-recommendations.md) | **단일 실행 계획** | 3-레이어 통합 액션 플랜 (tactical / containment / structural) |
| [06-latent-defects.md](./06-latent-defects.md) | 진단 | 잠재 결함 (LD-1…LD-10) — repro 확인 3건, 정적 7건 |
| [07-architecture-improvements.md](./07-architecture-improvements.md) | 설계 | 구조 레이어: 수직 슬라이스 7개 (S1–S7) |

## 추적성 매트릭스

주요 결함만 수록 (critical, high, repro 확인/High LD). 열 구성: 진단 위치 → 액션 플랜의 전술 수정 → 이를 흡수하는 구조 슬라이스 → 마스터 백로그의 회귀 테스트.

| 결함 | 요약 | 진단 | 05 액션 | 07 슬라이스 | 04 테스트 |
|---|---|---|---|---|---|
| C-1 / M-4 / LD-6 | 락이 데드 코드; TOCTOU | 03, 06 | Batch 2 #7 (A/B 결정) | S1 | #6 |
| C-2 | 통과 장면이 RALPH 원장 오염 | 03 | Batch 1 #1 | S4 | #1 |
| C-3 | 보호 경로 훅 우회 가능 + 드리프트 | 03 | Batch 3 #8 | — | #3 |
| H-1 | `--plan-only`가 Gate 2 건너뜀 | 03 | Batch 1 #2 | S6 | #2 |
| H-2 | 레퍼런스 중복 주입 | 03 | Batch 4 #14 | S2 | — (S2 테스트) |
| H-3 | 반복 blocker 임계값 불일치 (3 vs 2) | 03 | Batch 5 #23 | S4 | — |
| H-4a / H-4b | `record_image_output` 재시도 불가 / 경로 탈출 | 03 | Batch 4 #12 | S3 | #5 / #4 |
| H-5 | 비h264 클립에서 `StopIteration` | 03 | Batch 1 #3 | S5 | — |
| H-6 | `registered_at: "dry-run"` 하드코딩 | 03 | Batch 1 #4 | — | — |
| LD-1 | 잘린 JSONL 한 줄이 프로젝트 마비 *(repro)* | 06 | Batch 2 #6 | S1 | #8 |
| LD-2 | 비원자적 쓰기 + raw traceback *(repro)* | 06 | Batch 2 #6 | S1 | #9 |
| LD-3 | 버전 갭 충돌 *(repro)* | 06 | Batch 4 #13 | S3 | #11 |
| LD-4 | 서브프로세스 timeout 없음 (유료 호출 포함) | 06 | Batch 1 #5 | S5 | #10 |
| M-1 | placeholder QA 점수가 실제처럼 보임 | 03 | Batch 5 #22 | — | — |

## 종합 스코어카드

| 항목 | 평가 | 비고 |
|---|---|---|
| 안전 게이트 아키텍처 | ★★★★★ | 라이브러리 레벨 강제, 2중 유료 플래그, 실질 테스트 (plan-only 공백 1건, H-1) |
| 증거 / 감사 가능성 | ★★★★☆ | JSONL 원장 + 위키 + 번들; 원장 오염 버그 (C-2) |
| 상태 파일 내구성 | ★★☆☆☆ | 비원자적 쓰기; 잘린 한 줄이 프로젝트 마비 (LD-1/LD-2) |
| 동시성 정합성 | ★★☆☆☆ | 락이 check-only 데드 코드 (C-1) |
| 외부 도구 호출 | ★★☆☆☆ | 4개 subprocess 지점 전부 timeout 없음, 유료 포함 (LD-4) |
| 훅 레이어 견고성 | ★★☆☆☆ | 우회 가능한 부분 문자열 매칭, 설정 드리프트 (C-3) |
| 코드 구성 | ★★★★☆ | 작고 집중된 모듈, 일관된 패턴, 일부 중복 (S2/S3 대상) |
| 테스트 품질 | ★★★★☆ | 진짜 red/green 안전 테스트; 훅과 plan-only 경로에 공백 |
| 실질 QA 신호 | ★★★☆☆ | 이미지 점수 대부분이 하드코딩 5점; story-flow + 파일 검사만 실질 (M-1) |
