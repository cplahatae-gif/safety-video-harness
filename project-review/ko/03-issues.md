# 이슈 — 우선순위별 지적 사항

독립 리뷰 3개 패스 결과를 통합·중복 제거하고 스팟 검증했습니다. **[verified]** 표시는 에이전트 보고 후 소스를 직접 재확인한 항목입니다. 에이전트 지적 1건(`image_evaluation_flow.py`의 합성 final-keyframe 장면에서 `KeyError`가 난다는 주장)은 검증 과정에서 **반증**되어 — `validate_images`가 합성 장면을 포함한 `review_items` 전체를 `scenes`로 전달하므로 `scene_by_id`에 항상 존재 — 이 보고서에서 제외했습니다.

심각도: **C** = critical, **H** = high, **M** = medium, **L** = low.

---

## C-1. 단일 작성자 락이 환상 — `file_lock`은 데드 코드 **[verified]**

- **파일:** `safety_video_harness/locks.py:14-29`, `safety_video_harness/io.py`
- **확신도:** High

`file_lock`(실제로 `.lock` 마커를 생성하는 컨텍스트 매니저)은 코드베이스 어디에서도 import되거나 사용되지 않습니다 — grep으로 확인. 모든 쓰기 경로는 `assert_unlocked`만 호출하는데, 이는 check-then-act 검사입니다: `.lock` 파일이 이미 있으면 에러를 내지만 락을 생성하지는 않습니다. 따라서:

1. 어떤 작성자도 락을 잡지 않음; 동시 프로세스 2개가 모두 `assert_unlocked`를 통과해 같은 JSON 파일에 경쟁.
2. `file_lock` 자체도 도입 시 TOCTOU 레이스 존재: `marker.exists()` 검사 후 비배타적 `write_text`.

하니스는 현재 단일 프로세스라 잠복 상태이지만 — 프로젝트가 명시적으로 OMO 기반 루프 실행자를 계획하고 있어 동시 호출이 현실적입니다.

**수정안:**
```python
# locks.py — 원자적 획득
@contextmanager
def file_lock(path: Path) -> Iterator[None]:
    marker = lock_path(path)
    try:
        with marker.open("x", encoding="utf-8") as f:   # 배타적 생성, POSIX에서 원자적
            f.write("held by current process\n")
    except FileExistsError:
        raise HarnessError(f"single-writer lock is held: {marker}")
    try:
        yield
    finally:
        marker.unlink(missing_ok=True)

# io.py — 실제로 사용
def write_json(path: Path, data: JsonObject) -> None:
    with file_lock(path):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
```
대안: 파이프라인을 엄격히 단일 프로세스로 문서화하고 `file_lock`을 삭제 — 제공하지 않는 보장을 암시하는 코드를 제거.

---

## C-2. 통과한 장면이 RALPH 반복 원장을 오염 **[verified]**

- **파일:** `safety_video_harness/image_evaluation_flow.py:19-36`
- **확신도:** High

캡 가드는 `blocked AND prior_iterations >= MAX_RALPH_ITERATIONS`일 때만 건너뜁니다. blocking issue가 **없는** 장면은 *모든* `validate_images` 호출마다 새 원장 라운드를 기록합니다. 결과:

- 반복 횟수가 더 이상 "재생성 시도 횟수"가 아니라 "검증된 횟수"를 의미.
- 정상 프로젝트를 20회 이상 재검증하면 모든 장면이 캡에 도달한 것처럼 보이고, `build_loop_summary`가 한 번도 막힌 적 없는 장면을 `maxed_scenes`로 표시해 거짓 `stop_and_escalate`를 유발할 수 있음.

**수정안:** 막히지 않은 장면은 라운드를 건너뛰거나(또는 카운트 증가 없이 기록):
```python
blocked = bool(review.get("blocking_issues"))
if not blocked:
    counts[scene_id] = prior_iterations
    continue
if prior_iterations >= MAX_RALPH_ITERATIONS:
    counts[scene_id] = prior_iterations
    continue
```
통과 라운드도 증거로 남기고 싶다면 RALPH 캡에 들어가지 않는 별도 카운터(`validation_runs`)로 기록.

---

## C-3. 보호 경로 훅: 순진한 부분 문자열 매칭 + `protected_paths.json`과 드리프트

- **파일:** `hooks/pretooluse-protected-path-veto.py:7-12`, `hooks/protected_paths.json`
- **확신도:** High

훅이 `sys.argv`를 한 문자열로 합쳐 **하드코딩된** 목록(`["AGENTS.md", "hooks/", "schemas/", "templates/"]`)으로 부분 문자열 매칭하는데, 진짜 기준이어야 할 `protected_paths.json`에는 `approvals.json`도 들어 있습니다. 문제:

- **드리프트:** `approvals.json` 직접 쓰기(`approve_gate.py` 우회)가 거부되지 않음.
- **대소문자 구분:** `AGENTS.MD`, `Hooks/`는 검사를 통과; macOS 기본 파일시스템은 대소문자 비구분이라 `Hooks/pretooluse-live-veto.py`가 실제 파일에 쓰임.
- **오탐:** `schemas/`를 부분 문자열로 포함하는 무관한 경로가 거부됨.

**수정안:** 훅이 `protected_paths.json`을 읽고, 소문자 정규화하고, 경로 형태 인자에 대해 앵커드 매칭(`nohooks` ≠ `hooks`)하도록 변경. 중복 목록 자체가 사라집니다.

---

## H-1. `--live --execute-paid --plan-only`가 Gate 2를 건너뜀

- **파일:** `safety_video_harness/generation.py:117-131`
- **확신도:** High

live 분기에서 `plan_only`가 `require_gate(project, "image_to_video")`와 `_require_external_upload` *이전에* 반환합니다. 미승인 프로젝트에 대해 유료 라이브 계획(`seedance_live_plan.json`)이 작성되고 CLI는 성공을 보고합니다. 실행 자체는 이후에 막히지만, "승인 전 유료 경로 산출물 금지"라는 게이트 의도가 위반되며, 기존 테스트(`test_seedance_live_plan_uses_two_five_second_clips_for_10s`)가 미승인 프로젝트에서 exit 0을 기대해 이 우회를 고착화하고 있습니다.

**수정안:** `require_gate` + `_require_external_upload` 호출을 `build_seedance_live_plan` 위로 이동하거나, plan-only를 `--live --execute-paid`가 필요 없는 명시적 게이트리스 dry-run 모드로 재정의 (한쪽 의미론을 선택; 현재는 둘의 최악 조합).

---

## H-2. 레퍼런스 스캔이 루트 레벨 승인 자산을 이중 로드

- **파일:** `safety_video_harness/assets.py:10` (ASSET_DIRS), `approve_reference` 흐름
- **확신도:** High

`approved_reference` 역할이 모든 역할 하위 디렉토리의 *부모*인 `ref/approved`를 `glob("*")`로 스캔하는 동시에, `person/work/space/style/camera/lighting` 역할들이 자식 디렉토리를 스캔합니다. `approve_reference`는 승인 이미지를 평면 루트에 떨어뜨립니다. 파일 위치에 따라 프롬프트에 **1회 또는 2회**(루트 역할 + 하위 역할) 주입되어 레퍼런스 블록이 중복됩니다. `.md` 프로필 스캔도 같은 부모/자식 중첩 문제가 있습니다.

**수정안:** `approve_reference`가 대상 역할 하위 디렉토리를 요구하게 하거나, `approved_reference` 역할을 `ref/approved` 직속 파일로만 제한 (자산별 정식 위치 1곳을 정의).

---

## H-3. 반복 blocker 임계값이 arbiter와 위키에서 불일치

- **파일:** `safety_video_harness/evaluation_arbiter.py:120-125` (합계 ≥ 3에서 발동 — 올바름), `safety_video_harness/evaluation_rounds.py:263-271` (≥ 2에서 "repeated" 표시)
- **확신도:** High

arbiter는 문서대로 총 3회 발생 시 에스컬레이션합니다. 위키의 `Repeated Blockers` 섹션은 2회에 시그니처를 repeated로 표시합니다. 사람(또는 README가 재생성 판단에 쓰라고 명시한 위키를 읽는 LLM)은 시스템이 에스컬레이션하기 한 라운드 전에 "repeated"를 보게 되고 — 이 맵이 의사결정 입력으로 승격되면 에스컬레이션이 의도보다 일찍 발동합니다.

**수정안:** `evaluation_rounds._repeated_blockers`에서 `REPEATED_BLOCKER_THRESHOLD`를 import/인라인하여 `>= 3` 사용, 또는 위키 필드를 `recurring_blockers (≥2, informational)`로 개명.

---

## H-4. `record_image_output`은 재시도 불가 + 잡 파일의 출력 경로를 신뢰

- **파일:** `safety_video_harness/imagegen_jobs.py:28-52`
- **확신도:** High (재시도), Medium (경로 탈출)

한 함수에 두 가지 문제:

- **H-4a — 재시도 경로 없음:** 드래프트 파일이 이미 존재하면(부분 실패 후 재실행 등) `draft image already exists`로 raise — 생성 쪽과 달리 여기에는 `--regenerate` 버전 증가가 없습니다. 수동 파일 삭제 없이는 해당 장면 복구 불가.
- **H-4b — 경로 탈출:** `output = project / str(job["output"])`가 보호 경로 목록에 *없는* `imagegen_jobs.json`을 신뢰. 변조된 `"output": "../../..."`은 프로젝트 디렉토리를 벗어나고 `copyfile`이 그대로 따라감.

**수정안:** (H-4a) 충돌 시 기존 `_next_draft_path(..., regenerate=True)` 로직으로 다음 버전으로 증가; (H-4b) `if not output.resolve().is_relative_to(project.resolve()): raise HarnessError(...)` 추가.

---

## H-5. 비h264 클립에서 `video_qa`가 raw `StopIteration`으로 크래시

- **파일:** `safety_video_harness/video_qa.py:94`
- **확신도:** High

`next(stream for ... if codec_name == "h264")`에 기본값이 없습니다. VP9/AV1/손상/오디오 전용 클립이면 `StopIteration`이 발생하고, `run_boundary`는 `HarnessError`만 잡으므로 traceback으로 탈출합니다.

**수정안:** `next((...), None)` 후 `HarnessError(f"no h264 video stream found in {path}")` raise.

---

## H-6. 자료 등록 타임스탬프가 `"dry-run"`으로 하드코딩

- **파일:** `safety_video_harness/project.py:77`
- **확신도:** High

`"registered_at": "dry-run"`이 무조건 기록됩니다 — 실제 등록에도 타임스탬프가 남지 않아, 프로젝트가 크게 투자한 증거 추적이 영구적으로 훼손됩니다.

**수정안:** `dry_run: bool` 인자를 받아 실제 실행 시 `datetime.now(UTC).isoformat()` 기록 (코드베이스의 다른 모든 타임스탬프와 동일하게).

---

## M-1. 이미지 QA 필드 점수 대부분이 하드코딩 5점

- **파일:** `safety_video_harness/image_qa.py` (`review_scene_image`)
- **확신도:** High

`story_match_score`, `identity_consistency_score`, `ppe_score`, `equipment_score`, `technical_score`가 상수입니다; `story_flow_score`(3 또는 5)와 이미지 파일 검사만 변합니다. 파급 효과 둘:

- QA 게이트의 실질 강도가 story-flow + 파일 존재 검사뿐; 보고서의 루브릭 점수는 권위 있어 보이지만 placeholder.
- `MINIMUM_TOTAL_SCORE = 24`는 에러 경로 외에는 실패 조건으로 도달 불가능 (가변 필드 1개 최대 열화 시 합계 28), 즉 죽은 임계값.

**수정안:** 점수를 실제 role evaluator 출력에 연결하거나, 출력 JSON에 `"score_source": "placeholder"`를 표기해 하류 독자(Arbiter, OMO, 사람)가 과신하지 않게 할 것. 총점 하한도 재산정 또는 제거.

---

## M-2. Seedance 길이를 문자열 치환으로 패치

- **파일:** `safety_video_harness/seedance_live.py:88-91`
- **확신도:** High

`prompt.replace("Generate a 5 second Seedance clip", f"Generate a {duration} second ...", 1)`은 `prompt_contract.py`의 템플릿 문구가 바뀌면 조용히 no-op이 되어 유료 API에 잘못된 길이를 보냅니다.

**수정안:** 비디오 프롬프트 플랜에 `duration_sec`를 구조화된 필드로 보관하고 잡 빌드 시점에 최종 프롬프트 조립.

---

## M-3. 수동 리뷰 transcript 기본값이 가짜 blocker 생성

- **파일:** `safety_video_harness/video_qa.py:186`
- **확신도:** High

`manifest.get("transcript_enabled", True)`는 키를 *생략한* 검사 manifest(구버전·외부 도구 산출물)를 모두 차단합니다. 하니스가 쓴 manifest는 항상 `False`를 기록하는데도.

**수정안:** 기본값을 `False`로 — transcript 도구 부재가 "transcript 켜짐"으로 읽히면 안 됩니다.

---

## M-4. 위키 append가 그나마 있는 약한 락마저 우회

- **파일:** `safety_video_harness/evaluation_rounds.py:132-175`
- **확신도:** High

`_append_wiki_summary`가 `.md` 경로에 `assert_unlocked`를 확인한 뒤 raw append합니다; 두 줄 위의 JSONL 원장 쓰기와는 별개의 비원자적 작업입니다. 둘 사이에서 크래시하면 원장과 위키가 어긋납니다.

**수정안:** C-1 수정 후 두 쓰기를 하나의 `file_lock` 범위로 묶기.

---

## M-5. secret-veto 훅이 대소문자 구분 + 패턴 빈약

- **파일:** `hooks/pretooluse-secret-veto.py:6-7`
- **확신도:** High

`re.compile(r"API_KEY|SECRET|TOKEN|Bearer ")`는 `api_key=`, `bearer`, `sk-…`, `eyJ…`(JWT), `Bearer\t`를 놓치고, `TOKEN`은 무해한 이름에 오탐합니다. 현재로서는 통제가 아니라 알림 수준입니다.

**수정안:** `(?i)` 플래그 + 흔한 키 형태 패턴(`sk-[A-Za-z0-9]`, `eyJ[A-Za-z0-9_-]+\.`), 그리고 쓰기 작업으로 거부 범위 한정.

---

## M-6. stop-sentinel이 CWD 상대 경로 사용

- **파일:** `hooks/stop-sentinel-guard.py:8`
- **확신도:** High

`Path(".harness/DONE")`은 호출자의 작업 디렉토리에 의존합니다; 다른 모든 훅은 `Path(__file__)`에서 해석합니다. CWD가 다르면 stop 가드가 조용히 무력화(또는 오발동)됩니다.

**수정안:** 저장소 루트 기준으로 해석하거나 `--project` 인자 수용.

---

## M-7. `posttooluse-*` 훅이 검증기인 척하는 no-op

- **파일:** `hooks/posttooluse-schema-validation.py`, `hooks/posttooluse-evidence-feedback.py`
- **확신도:** High

둘 다 입력과 무관하게 알림 출력 후 exit 0. 파일명이 실제로 일어나지 않는 검증을 약속합니다.

**수정안:** `scripts/validate_project.py`/증거 검사를 실제 호출하거나, `*-reminder.py`로 개명해 존재하지 않는 커버리지를 가정하지 못하게 할 것.

---

## M-8. 손상된 PPTX가 조용히 placeholder로 렌더링

- **파일:** `safety_video_harness/source_rendering.py:37-39`
- **확신도:** High

`BadZipFile` 분기가 빈 경고와 함께 placeholder 출력을 반환해 `entry["render_warning"]`에 아무것도 기록되지 않고, 운영자는 자료가 읽을 수 없는 상태였음을 알지 못합니다.

**수정안:** 해당 분기에서 비어 있지 않은 경고 문자열 반환.

---

## L-1. 사소한 품질 항목

| 항목 | 위치 | 비고 |
|---|---|---|
| `_latest_draft` 중복 | `image_qa.py:95` vs `imagegen_jobs.py:96` | 동일 로직, 다른 반환 계약; 공유 헬퍼로 추출 |
| 길이 키 이중화 | `project.py:187-188` | `target_seconds`와 `target_duration_sec` 동시 유지; 하나만 |
| 전체 프롬프트 생성 후 `scene_filter` 적용 | `generation.py:52-68` | 낭비; `scene_items`를 먼저 필터 |
| 라운드당 원장 2회 읽기 | `evaluation_arbiter` + `evaluation_rounds` | Canonical 항목: [06-latent-defects.md](./06-latent-defects.md) LD-9 |
| `dict(dict(...))` 이중 래핑 | `prompt_team.py:71` | 바깥 호출은 no-op |
| `debate_positions()` 2회 계산 | `evaluation_outputs.py:53,60` | 리스트 캐시 |
| `build_loop_summary`의 `"iteration": 1` 하드코딩 | `image_qa.py:122` | 오해 소지 있는 최상위 필드; 카운트에서 유도 |
| `parent.parent.parent`로 드래프트 경로 유도 | `image_qa.py:211` | 깨지기 쉬운 구조 가정; `project`를 명시적으로 전달 |
| 역할별 blocker가 기준별로 필터되지 않음 | `stage_role_reviews.py:83-92` | 역할 파일에 무관한 blocker가 실림 |
| `error_log.append_error` 미사용 | `error_log.py` | `run_boundary`에 연결하거나 제거 |
| `test-seconds must be 5 or 10` 메시지 vs `% 5 == 0` 검사 | `seedance_live.py:75-76` | 메시지와 제약 불일치 |
| `is_remicon_collision_source` 부분 문자열 매칭 | `source_facts.py` | "레미콘" 포함 경로 전부 매칭; 명시적 source-type 필드 권장 |
