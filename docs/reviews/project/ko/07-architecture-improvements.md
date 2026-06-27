# 아키텍처 개선 기회

**입력:** 1단계 리뷰([03-issues.md](./03-issues.md))와 2단계 잠재 결함 진단([06-latent-defects.md](./06-latent-defects.md)). 아래 모든 제안은 검증된 결함 최소 1건에 앵커되어 있습니다 — 사변적 리팩토링 없음.

**이 문서의 역할:** [05-recommendations.md](./05-recommendations.md) 통합 액션 플랜의 구조 레이어. 05에서 배포된 전술 수정은 의도적으로 이 슬라이스들에 나중에 흡수됩니다(05에서 *"구조적 후속"* 으로 표시된 항목). 슬라이스가 테스트를 언급할 때 번호 참조는 [04-test-coverage.md](./04-test-coverage.md)의 마스터 백로그를 가리키며, 번호 없는 테스트 설명은 슬라이스 고유 추가분입니다.

**어휘** (전체에서 일관 사용): **모듈**은 인터페이스와 구현을 가진 모든 것; **깊이(depth)** 는 인터페이스에서의 레버리지 — 작은 인터페이스 뒤의 많은 동작; 호출자가 구현만큼 많이 알아야 하면 모듈은 **얕음(shallow)**; **심(seam)** 은 인터페이스가 사는 곳; **국소성(locality)** 은 변경·버그·지식이 한곳에 모일 때 유지보수자가 얻는 것. **삭제 테스트**: 모듈을 지웠을 때 복잡도가 N개 호출자로 재출현하면 제 몫을 하던 것이고, 그냥 사라지면 통과 계층이었던 것.

**도메인 어휘 참고:** 이 저장소에는 `CONTEXT.md`가 없습니다. 사실상의 도메인 용어집은 [01-architecture-map.md](./01-architecture-map.md)와 `AGENTS.md`에 있습니다. 슬라이스 S7이 이를 `CONTEXT.md`로 승격해 네이밍 결정의 단일 기준을 만들 것을 제안합니다.

각 제안은 **수직 슬라이스(vertical slice)**: 독립 배포 가능, 자체 테스트 포함, 다른 슬라이스 불요(의존성은 명시).

---

## 슬라이스 S1 — Project State Store: 모든 상태 파일 IO를 하나의 deep 모듈로

**권고 강도: Strong** · C-1, M-4, LD-1, LD-2를 단일 심에서 해소

| | |
|---|---|
| **(1) 현재 문제** | `io.py` + `locks.py`는 얕은 심입니다: 호출자(패키지 전반 약 25개 호출 지점)가 각자 락 규율(`assert_unlocked` vs 한 번도 안 쓰인 `file_lock`), 쓰기가 비원자적이라는 사실, `read_json`이 raw `JSONDecodeError`를 던진다는 사실, 각 상태 파일의 상대 경로(`"qa" / "image_qa_loop.json"` 문자열이 산재)를 알아야 합니다. 검증된 결함 4건(C-1, M-4, LD-1, LD-2)이 모두 이 한 심에 삽니다 — 인터페이스가 호출자의 실제 필요보다 얇다는 가장 강력한 신호입니다. |
| **(2) 개선안** | 인터페이스가 작은 deep `state.py` 모듈(가칭 **ProjectStore**): `store.read(StateFile.APPROVALS)`, `store.write(StateFile.APPROVALS, data)`, `store.append_round(record)`. 인터페이스 뒤에서 소유하는 것: 원자적 쓰기(tmp + `os.replace`), 실제 락 획득(`open("x")`), 손상 → 파일/줄 명시 `HarnessError`, 잘린 JSONL 꼬리 허용, 알려진 모든 상태 파일의 정식 상대 경로. `io.py`/`locks.py`는 구현 세부가 됨. |
| **(3) 변경 영향 범위** | `io.py`, `locks.py` (흡수); 약 20개 모듈에서 기계적 import 교체; 정상 파일에는 동작 변화가 없어 기존 테스트 그대로 통과. 회귀 테스트: [04-test-coverage.md](./04-test-coverage.md)의 #6, #8, #9. |
| **(4) 우선순위** | **1 — 최우선.** 다른 모든 모듈이 이 심 위에 있음; 여기서 4건을 고치면 모든 곳에서 한 번에 고쳐지고(국소성), 이후 슬라이스가 보장을 공짜로 상속(레버리지). |

> **05 Batch 2 락 결정에 대한 의존성:** 이 슬라이스는 기술된 대로라면 **Option A**(실제 락)를 전제합니다. Option B(단일 프로세스 선언)를 선택해도 S1은 유효합니다 — 그 경우 원자성·손상 정책·정식 경로만 소유하고, 락 획득 동작(및 테스트 #6)이 빠집니다. 어느 옵션이든 할 가치가 있는 슬라이스입니다.

```text
이전 (shallow):  25개 호출자 ── 각자 안다: 경로 + 락 규칙 + json 에러 + 비원자성
이후 (deep):     25개 호출자 ── store.read/write/append ──┐
                                                          └─ 원자성, 락, 손상 정책, 경로 (한곳)
```

---

## 슬라이스 S2 — Reference Catalog: 평행한 두 스캐너 병합

**권고 강도: Strong** · H-2, LD-8 해소; 코드베이스 최대 중복 제거

| | |
|---|---|
| **(1) 현재 문제** | `assets.py`와 `reference_profile.py`는 같은 숨은 개념 — "레퍼런스 디렉토리를 스캔하고 각 자산의 설명을 해석한다" — 의 두 구현입니다. 둘 다 `ASSET_DIRS`를 순회하고, 둘 다 이미지 + 고아 `.md`를 glob하고, 둘 다 동일한 `-front` 분할 휴리스틱으로 사이드카를 해석하며(`assets.py:72`, `reference_profile.py:80`), `_has_matching_image`는 **바이트 단위로 중복**(`assets.py:83-84`, `reference_profile.py:86-87`)입니다. 출력 형태는 이미 갈라졌고(`description` 폴백 문구가 다름) 버그 2개(H-2 부모/자식 이중 스캔, LD-8 접두사 과매칭)를 공유합니다 — 각각 현재 두 번씩 고쳐야 합니다. 삭제 테스트: 어느 파일을 지워도 스캔 복잡도가 상대 호출자에 재출현 → *개념*은 모듈을 가질 자격이 있고, 그것이 둘 있다는 것이 결함입니다. |
| **(2) 개선안** | 하나의 deep `reference_catalog.py`: `load_catalog(project) -> Catalog`. `Catalog`이 모든 자산의 역할·경로·설명·고정 특성·용도를 알고 있음. `reference_assets_prompt_block`과 `analyze_reference_assets`는 같은 카탈로그 위의 얇은 **뷰** 둘이 됨. 부모/자식 디렉토리 규칙(H-2)과 프로필 사이드카 정확 일치(LD-8)는 내부에서 한 번만 결정. `approve_reference`는 분리 유지 — 스캔이 아닌 쓰기 작업. |
| **(3) 변경 영향 범위** | `assets.py`, `reference_profile.py` (병합); `generation.py`, `prompt_contract.py`, `seedance_live.py`, `project.py`의 호출자(import 교체); `reference_assets.json` 출력 형태 보존. 테스트: 산재한 커버리지를 테이블 기반 스캔 테스트 하나로 대체; H-2/LD-8 회귀 케이스. |
| **(4) 우선순위** | **2.** S1과 독립; 변경 줄 수 대비 중복 제거 효과 최대. |

---

## 슬라이스 S3 — Image Version Store: draft/approved 버전 산술 소유

**권고 강도: Strong** · LD-3, H-4(재시도), L-1 중복 해소; write-once 약속 보호

| | |
|---|---|
| **(1) 현재 문제** | 버전 산술이 2개 모듈의 private 헬퍼 3개에 번져 있습니다: `_next_draft_path` / `_next_preserved_approved`(`imagegen_jobs.py`)와 두 번째 `_latest_draft`(`image_qa.py:96` vs `imagegen_jobs.py:96` — 반환 계약이 다른 중복: 하나는 `None` 반환, 하나는 raise). 산술 자체가 엣지에서 틀렸고(LD-3: 개수 기반, 갭 후 충돌), 재시도 경로가 없으며(H-4a), `image_qa.py:211`은 레이아웃을 소유한 모듈이 없어 `parent.parent.parent`로 프로젝트 루트를 재구성합니다. 호출자가 실제로 필요한 인터페이스 — "최신 드래프트 줘", "충돌 없는 다음 경로 줘", "이 승인 파일 보존해" — 는 작은데, 안전하게 호출하기 위해 알아야 할 지식은 큽니다. 전형적인 얕은 모듈. |
| **(2) 개선안** | 하나의 deep `image_versions.py`: `latest_draft(project, scene_id)`, `next_draft(project, scene_id)` (max+1, 절대 충돌 없음, 프로젝트 내 포함 — H-4b 경로 탈출도 닫음), `preserve_approved(project, scene_id)`. write-once 의미론이 모든 호출자가 기억해야 할 규칙이 아니라 *이 모듈의 불변식*이 됨. |
| **(3) 변경 영향 범위** | `imagegen_jobs.py`, `image_qa.py` (헬퍼 교체); 동작 변화는 갭 엣지케이스에서만. 테스트: 갭-충돌 회귀(LD-3 repro가 테스트가 됨, #11), 재시도 버전 증가(#5), 포함 검사(#4). |
| **(4) 우선순위** | **3.** 작고 날카로운 범위; 검증된 결함 2건을 불변식으로 직접 전환. |

---

## 슬라이스 S4 — Evaluation Ledger: 한 번 읽고, 한 번 결정

**권고 강도: Strong** · C-2, H-3, LD-9 해소; 저장 보장은 S1에 의존(먼저 배포 가능하나 S1 이후가 더 깔끔)

| | |
|---|---|
| **(1) 현재 문제** | "라운드 원장" 개념에 주인이 없습니다. `evaluation_rounds.py`는 세 책임 — 원장 IO, 위키 마크다운 렌더링, 시그니처 카운팅 — 을 섞고, `evaluation_arbiter.py`는 같은 파일에 대해 시그니처 카운팅을 *재구현*(`_prior_signature_counts`)하는데 위키와 **임계값이 다릅니다**(H-3: 3 vs 2). 파일은 장면·라운드당 2회 전체 재독되고(LD-9), 반복 횟수 의미론이 깨진 것(C-2)도 정확히 증가 결정이 원장을 소유한 모듈이 아닌 호출자(`image_evaluation_flow.py`)에 살기 때문입니다. 세 모듈이 한 개념의 규칙을 부분 복사로 나눠 들고 있으면, 그 개념은 모듈이 되고 싶다는 뜻입니다. |
| **(2) 개선안** | deep `ledger.py`: `Ledger.load(project)`가 JSONL을 **한 번** 읽음; `completed_iterations(stage, item)`, `signature_counts(stage, item)`, `append(record)` 제공, 단일 `REPEATED_BLOCKER_THRESHOLD`와 "통과 라운드는 RALPH 캡에 불산입" 규칙 소유(C-2 수정이 호출자의 가드가 아닌 불변식이 됨). 위키 렌더링은 전부 `evaluation_markdown.py`로 이동(정확히 이 용도로 이미 존재 — 현재 약 200줄의 마크다운 로직 중 33줄만 보유). |
| **(3) 변경 영향 범위** | `evaluation_rounds.py` (분리), `evaluation_arbiter.py` (private 원장 리더 제거), `image_evaluation_flow.py` (증가 가드 제거), `evaluation_markdown.py` (위키 렌더러 획득). 원장 파일 포맷 불변. 테스트: C-2 회귀(#1), 임계값 정렬 테스트, 단일 읽기 성능 단언(호출 횟수 스파이). |
| **(4) 우선순위** | **4.** 증거 스토리에 가장 하중이 큰 슬라이스; S2/S3보다 약간 커서 그 뒤에 배치. |

```text
이전: evaluation_rounds ─┬─ 원장 IO            evaluation_arbiter ── 자체 원장 리더 (임계값=3)
                         ├─ 위키 렌더링         image_evaluation_flow ── 증가 규칙 (깨짐, C-2)
                         └─ 시그니처 카운트 (임계값=2)
이후: ledger.py ── 1회 로드 / iterations / signatures / append / 임계값 / 캡 규칙
      evaluation_markdown.py ── 모든 위키 렌더링
```

---

## 슬라이스 S5 — External Tool Runner: 모든 subprocess의 단일 심

**권고 강도: Worth exploring** · LD-4, LD-10을 한곳에서 해소

| | |
|---|---|
| **(1) 현재 문제** | 4개 모듈이 `subprocess.run`을 직접 호출하며(`tools.py`, `video_qa.py`, `video_inspection.py`, `seedance_live.py`), 각자 같은 패턴(`check=False`, capture, returncode → `HarnessError`)을 재구현하고 각자 독립적으로 `timeout`을 누락(LD-4)했습니다. 패턴 반복이 단서입니다: 여기에 이름 없는 모듈 — "외부 도구를 안전하게 실행한다" — 이 있습니다. 테스트의 자연스러운 심이기도 합니다(현재는 4개 호출 지점을 따로 monkeypatch). |
| **(2) 개선안** | `external_tools.py`: `run_tool(command, *, timeout, env=None) -> CompletedProcess` — timeout + `TimeoutExpired` → `HarnessError`, `bash` 래핑 손자 프로세스의 프로세스 그룹 kill, 균일한 에러 문구를 소유. ffprobe의 JSON 파싱 가드(LD-10)는 `run_tool_json` 변형에 거주. 테스트는 모든 외부 도구를 fake할 **하나의** 심을 얻음. |
| **(3) 변경 영향 범위** | 호출 지점 4곳 교체; 지점별 timeout 상수 결정(프로브 30초 / 검사 300초 / Higgsfield는 SLA+여유). 테스트: timeout → `HarnessError`(#10), JSON 변형 가드. |
| **(4) 우선순위** | **5.** 기계적으로 단순; "worth exploring"인 이유는 구조가 의심스러워서가 아니라 도구별 timeout 값(특히 유료 Seedance 호출)에 운영 결정이 필요해서. |

---

## 슬라이스 S6 — Seedance 흐름: *plan*과 *execute* 분리

**권고 강도: Worth exploring** · H-1을 구조적으로 해소; Gate 2를 설계상 우회 불가능하게

| | |
|---|---|
| **(1) 현재 문제** | `generation.py:117-131`의 `generate_seedance`는 가드 절이 뒤얽힌 채 4개 모드(dry-run / plan-only / live / paid)를 저글링하는 한 함수입니다 — Gate 2 우회(H-1)는 정확히 `plan_only` 조기 반환이 유료 플래그 검사와 게이트 검사 *사이에* 끼어들면서 발생했습니다. 섞인 책임이 가드 순서를 버그 표면으로 만들었습니다. 같은 모듈이 이미지 생성까지 소유해 `generation.py`가 패키지의 잡동사니 가방이 되어 있습니다. |
| **(2) 개선안** | 도메인 자체의 어휘(Gate 2가 *계획*과 *유료 실행*을 가른다)를 따라 심을 분할: `seedance_flow.plan(project, options)` — 항상 허용, `--live/--execute-paid` 불필요; `seedance_flow.execute(project, plan)` — 게이트 + 유료 플래그 + 외부 업로드 검사를 *내부에서*, 첫 줄에서, 재배열할 모드 플래그 없이 수행. H-1 클래스의 버그가 표현 불가능해짐: `execute`에는 게이트 검사 이전의 코드 경로가 없음. |
| **(3) 변경 영향 범위** | `generation.py` (축소), 신규 `seedance_flow.py`, `scripts/generate_seedance.py` 플래그 매핑(`--plan-only` → plan; `--live --execute-paid` → execute), `seedance_live.py`는 하부에서 불변. 우회 고착화 테스트 재작성(04 §1 참조). CLI 호환성 결정 필요: 구 플래그를 별칭으로 유지할지 끊을지. |
| **(4) 우선순위** | **6.** H-1의 전술 수정(05 Batch 1) 이후에 — 이 슬라이스는 재발을 막는 구조 버전. |

---

## 슬라이스 S7 — 도메인 용어집 `CONTEXT.md` 승격 + 네이밍 정렬

**권고 강도: Worth exploring** · 저위험; 이후 모든 변경의 가치를 곱해줌

| | |
|---|---|
| **(1) 현재 문제** | 도메인 어휘가 산문(`README.md`, `AGENTS.md`)에서는 강한데 코드에서는 비일관적입니다. 검증된 드리프트: **round vs iteration** (`evaluation_rounds.py`가 *round*라 부르는 것에 `"iteration"` 필드를 기록; `image_qa.py`는 최상위 `"iteration": 1` 하드코딩); **RALPH loop vs ralph_loop vs image_qa_loop** (`qa/image_qa_loop.json`이 `ralph_loop` 객체를 담음); **scene vs item vs review item** (`record_image_evaluation_rounds(scenes=...)`가 실제로는 review item을 받음 — 1단계 리뷰에서 거짓 `KeyError` 지적을 낳은 바로 그 모호함); **blocker vs blocking_issue vs blocker_signature** (관련되지만 구별되는 세 개념이 한곳에 정의된 적 없음). LLM 에이전트가 이 저장소의 1급 독자(AGENTS.md 주도)인데, 네이밍 드리프트는 매 세션 맥락 비용을 치르게 합니다. |
| **(2) 개선안** | (a) [01-architecture-map.md](./01-architecture-map.md) 용어집에 3종 blocker 정의를 더해 저장소 루트에 `CONTEXT.md` 생성. (b) 개념당 용어 하나 선정 — 권장: **round**(기록된 평가 1건), **iteration**(RALPH 루프에서 장면의 위치, 즉 *카운트된* 라운드), **review item**(장면 또는 합성 final keyframe) — 순수 내부 식별자를 이에 맞게 개명. (c) 디스크의 JSON 키는 이 슬라이스에서 불변 (영속 키 개명은 개명이 아니라 마이그레이션). |
| **(3) 변경 영향 범위** | 신규 `CONTEXT.md`; `evaluation_rounds.py`, `image_evaluation_flow.py`, `image_qa.py`의 내부 파라미터/변수 개명(동작·파일 포맷 변화 없음); `AGENTS.md`에 `CONTEXT.md` 포인터 추가. |
| **(4) 우선순위** | **7 — 기회 활용.** 개명은 같은 줄을 건드리는 S3/S4에 끼워 넣고, `CONTEXT.md` 생성은 아무 때나. |

---

## 순서와 의존성 지도

```text
S1 ProjectStore ──────────┐  (기반: 저장 보장)
S2 Reference Catalog ─────┤  독립
S3 Image Version Store ───┤  독립
S4 Evaluation Ledger ─────┘  S1 이후가 더 깔끔 (append/torn-tail 정책 사용)
S5 External Tool Runner      독립, 아무 때나
S6 Seedance plan/execute     H-1 전술 수정 이후
S7 CONTEXT.md + 네이밍       기회 활용, S3/S4에 동승
```

**최우선 권고: S1부터.** 검증된 결함 4건이 동시에 가리키는 유일한 슬라이스이고, 다른 모든 모듈이 그 호출자이며, happy path 동작은 바꾸지 않습니다 — 순수한 깊이 이득. S2와 S3가 최적의 두 번째 수: 작고, 독립적이며, 각각 중복된 버그 표면을 단일 불변식으로 전환합니다.

**이 목록이 의도적으로 제외한 것:** 에이전트/스킬/훅 플러그인 레이아웃, 게이트 모델, 합의/veto 설계, propose-only 영상 정책. 이 심들은 설계대로 올바릅니다([02-strengths.md](./02-strengths.md) 참조) — 거기서 발견된 결함은 아키텍처 문제가 아닌 구현 버그이며 [05-recommendations.md](./05-recommendations.md)가 이미 다룹니다.
