# 잠재 결함 진단

**방법:** 보고된 버그가 없는 선제 점검에 맞게 `/diagnose` 규율을 변형. 코드만 읽고 가설을 세우는 대신, 각 의심 지점을 (a) 실제 모듈에 대해 **최소 repro 스크립트로 확인**(Phase 1–2 feedback loop)하거나, (b) repro가 의미 없는 구조적 결함(예: `timeout=` 인자 누락)은 **정적 결함**으로 분류했습니다. 이미 [03-issues.md](./03-issues.md)에 등재된 결함은 중복 없이 교차 참조만 합니다.

아래 "Containment" 줄은 통합 액션 플랜([05-recommendations.md](./05-recommendations.md))에 흡수되어 있으며, 이 결함들의 회귀 테스트는 마스터 테스트 백로그([04-test-coverage.md](./04-test-coverage.md))의 #8–#11입니다.

점검 요청 결함 클래스: 엣지케이스, 예외 미처리, 경쟁 조건, 리소스 누수.

---

## repro로 확인 (2026-06-12 실행, Python 3.14 venv)

### LD-1. 잘린 원장 한 줄이 프로젝트 전체를 마비 — **[repro 확인]**

- **클래스:** 예외 미처리 × 비원자적 쓰기 (복합)
- **파일:** `safety_video_harness/evaluation_rounds.py:100-111` (`_read_round_entries`), `io.py:24-28` (`write_jsonl`)
- **심각도:** High

`write_jsonl`은 원자성 없이 append합니다; append 중 크래시나 kill은 잘린 마지막 줄을 남깁니다. 이후 `_read_round_entries`가 모든 읽기에서 raw `json.JSONDecodeError`를 raise합니다.

**Repro:** 정상 1줄 + 잘린 1줄로 원장을 만들고 `completed_iterations()` 호출 →
```
JSONDecodeError: Unterminated string starting at: line 1 column 20
```

**폭발 반경:** `completed_iterations`는 모든 `validate_images`, `validate_video`, arbiter 실행이 호출합니다. 중단된 쓰기 한 번이 해당 프로젝트의 모든 QA 명령을 영구적으로 망가뜨리며, 어느 파일이 문제인지 힌트도 없고 JSONL을 손으로 고치는 것 외에 복구 경로가 없습니다.

**Containment:** `_read_round_entries`에서 줄 단위로 `JSONDecodeError`를 잡고, 손상이 **마지막** 줄이면 torn append로 간주(건너뛰기 + 경고), 그 외 위치의 손상은 파일/줄 번호를 명시한 `HarnessError`. 선택적으로 append 후 `fsync`.

---

### LD-2. 손상된 JSON 상태 파일이 raw traceback으로 크래시 — `run_boundary`가 전혀 못 잡음 — **[repro 확인]**

- **클래스:** 예외 미처리
- **파일:** `io.py:14-15` (`read_json`), `cli.py:9-16` (`run_boundary`)
- **심각도:** High

`read_json`은 `json.JSONDecodeError`와 `FileNotFoundError`를 그대로 전파합니다. `run_boundary`는 `HarnessError`만 잡으므로, 상태 파일(`approvals.json`, `scenes.json`, `project_config.json`, …)이 손상되거나 없으면 30개 CLI 스크립트 전부가 raw traceback을 토합니다.

**Repro:** 파일에 `{"gates": {`를 쓰고 `run_boundary` 안에서 `read_json` 호출 → 깔끔한 exit-1 메시지가 아닌 미포착 `JSONDecodeError` traceback.

**여기서 특히 더 중요한 이유:** `write_json`(`io.py:18-21`) 자체가 비원자적(대상 파일에 직접 `write_text`)이라, 하니스가 나중에 자신을 마비시킬 손상 파일을 *스스로 생산*할 수 있습니다 — LD-1과 LD-2는 한 실패 스토리의 양면입니다. 쓰기 도중 손상된 `approvals.json`은 게이트 상태를 읽을 수 없게 만듭니다.

**Containment:**
1. `read_json`: `HarnessError(f"unreadable JSON state file: {path}: {e}")`로 래핑해 re-raise (`from e` 유지).
2. `write_json`: `path.with_suffix(".tmp")`에 쓴 뒤 `os.replace()` — POSIX에서 원자적, 찢어진 상태 파일을 원천 제거.

---

### LD-3. 버전 갭이 생기면 드래프트 버전 번호가 충돌 — **[repro 확인]**

- **클래스:** 엣지케이스
- **파일:** `safety_video_harness/imagegen_jobs.py:86-93` (`_next_draft_path`), 동일 패턴 `:103-106` (`_next_preserved_approved`)
- **심각도:** Medium

다음 버전 = `len(existing) + 1`, 즉 **최대** 버전이 아니라 파일 **개수**에서 유도. 갭이 생기면(운영자가 불량 드래프트 삭제, 부분 정리, glob과 쓰기 사이 크래시) "다음" 경로가 기존 파일과 같아집니다.

**Repro:** `sc01_v002.png`와 `sc01_v003.png`만 있는 상태(v001 삭제)에서 `_next_draft_path(..., regenerate=True)`가 — 이미 존재하는 — `sc01_v003.png`를 반환.

**폭발 반경:** imagegen 잡 스펙이 기존 드래프트를 가리키게 되고, `record_image_output`이 `draft image already exists`로 하드 실패(이슈 H-4a에 따라 재시도 경로도 없음)하여 장면이 wedge됩니다. `_next_preserved_approved`의 같은 산술은 기존 보존 승인 파일을 겨냥할 수 있어 — 프로젝트의 write-once 약속과 충돌합니다.

**Containment:** `len + 1` 대신 `max(int(p.stem.rsplit("_v", 1)[1]) for p in existing) + 1`. 두 함수 모두 동일 수정.

---

## 정적 결함 (구조적; repro 불필요)

### LD-4. 모든 subprocess 호출에 `timeout=` 없음 — 외부 도구마다 행(hang) 위험

- **클래스:** 리소스 누수 / 활성성(liveness)
- **파일:** `tools.py:25` (tesseract), `video_qa.py:192` (ffprobe), `video_inspection.py:118` (bash 경유 inspection 스킬), `seedance_live.py:130` (Higgsfield CLI)
- **심각도:** High (Seedance 지점은 상한 없는 *유료* 호출)

4개 `subprocess.run` 지점 전부 `timeout` 누락. 손상 MP4의 ffprobe, 병적인 이미지의 tesseract, 멈춘 Higgsfield CLI 네트워크 호출, stdin을 기다리는 inspection bash 스크립트가 하니스를 무한정 멈춥니다 — OMO 루프 맥락에서는 루프 실행자까지 함께 멈춥니다. `capture_output=True`가 상황을 악화시킵니다: 아무것도 쓰지 않고 블록된 자식은 진행 신호조차 없습니다.

**Containment:** 지점별 timeout 추가(`ffprobe`/`tesseract`: 30초; inspection 스크립트: 300초; Higgsfield: 생성 SLA + 여유), `subprocess.TimeoutExpired`를 잡아 명령어를 명시한 `HarnessError`로 re-raise. 주의: `subprocess.run(timeout=...)`은 직계 자식만 죽이고 `bash`로 감싼 손자는 살아남을 수 있음 — `video_inspection._run`에는 `start_new_session=True` 후 timeout 시 프로세스 그룹 kill.

### LD-5. `_run_understand_video`가 새 출력 확보 전에 이전 출력을 파괴

- **클래스:** 엣지케이스 / 파괴 윈도우
- **파일:** `video_inspection.py:84-90`
- **심각도:** Medium

순서: 도구 실행 → `shutil.rmtree(output)` (이전 검사 증거 삭제) → `shutil.move(generated, output)`. move가 실패하면(크로스 디바이스 링크, 권한, 이름 충돌) 이전 증거는 이미 사라졌고 새 breakdown은 `clip.with_name(f"{clip.stem}-breakdown")`에 고립됩니다. 증거 우선 하니스에서, 대체물이 자리 잡기 전에 증거를 지우는 것은 잘못된 순서입니다.

**Containment:** 새 breakdown을 먼저 `output.with_suffix(".new")`로 옮긴 뒤 교체(새 디렉토리가 자리 잡은 후에만 이전 것 `rmtree`), 또는 `os.replace` 스타일의 2단계 rename.

### LD-6. `assert_unlocked`/`file_lock` 레이스 — **C-1**로 기등재

- **클래스:** 경쟁 조건 — [03-issues.md](./03-issues.md) C-1/M-4 참조. 경쟁 조건 클래스의 완결성을 위해 기재: 모든 것이 `write_json`/`write_jsonl`을 통과하기 때문에 코드베이스에 *다른* 공유 상태 레이스는 없습니다; C-1을 고치면 이 클래스가 닫힙니다.

더 작은 두 번째 TOCTOU가 게이트 *검사*와 유료 *실행* 사이에 있습니다: `generate_seedance`가 Gate 2를 검증(`require_gate`)한 뒤 CLI를 실행하는데, 멀티 잡 플랜에서 잡별로 게이트를 재확인하지 않습니다. 현재(단일 운영자)는 수용 가능; 승인이 실행 중 철회 가능해지면 `_run_cli`에 한 줄 가치가 있습니다.

### LD-7. 씬 링크 검증기가 인덱스 기반 정체성을 하드코딩

- **클래스:** 엣지케이스
- **파일:** `scene_links.py:26-34`
- **심각도:** Medium

`_review_scene_link`가 기대값을 순전히 리스트 위치(`sc{index:02d}` / `sc{index+1:02d}`)에서 유도하고, 장면 자신의 `id`는 보고만 할 뿐 대조하지 않습니다. 엣지에서의 결과:

- 장면 순서가 `sc02, sc01`이거나 다른 id 체계를 쓰는 스토리보드는 위치 기준으로 통과/실패하며, 엉뚱한 장면을 지목하는 오해성 메시지를 냅니다.
- **빈** 장면 리스트는 `reviews=[]`, `passed=true` — 장면이 0개인 스토리보드에서 `validate_scene_links`가 성공하고, 그 뒤를 막는 것은 Gate 2의 클립 수 검사뿐입니다.

**Containment:** `scene.get("id") == f"sc{index:02d}"`를 자체 blocker로 단언하고, 빈 장면 리스트에서 실패.

### LD-8. 캐스트 프로필 사이드카 glob이 파일명 접두사에 과매칭

- **클래스:** 엣지케이스
- **파일:** `assets.py:72`, `reference_profile.py:80`
- **심각도:** Low

`path.stem.split('-front')[0]` + `glob(f"{stem}*.profile.md")` 때문에 `worker-001-front.png`가 `worker-001.profile.md` **그리고** `worker-0010.profile.md`, `worker-001b.profile.md` 등에 매칭됩니다. 이 명명 체계로 캐스트가 10명 이상이면 잘못된 신원 프로필이 조용히 프롬프트에 합류합니다 — identity-lock 하니스가 잘못된 신원을 주입하는 것은 크래시가 아닌 조용한 품질 실패입니다.

**Containment:** 정확히 `f"{base}.profile.md"` 매칭, 구분자 앵커 패턴으로 폴백.

### LD-9. 원장이 무한 성장하며 장면·라운드당 2회 전체 재독

*(Canonical 항목 — [03-issues.md](./03-issues.md)의 L-1 표 행이 여기를 가리킴.)*

- **클래스:** 리소스 (성능) — 누수가 아닌 스케일링 절벽
- **파일:** `evaluation_arbiter.py` (`_prior_signature_counts`), `evaluation_rounds.py` (`_repeated_blockers`, `completed_iterations`)
- **심각도:** 현재 Low; C-2 수정 후 프로젝트가 오래 살면 Medium

모든 arbiter 결정과 라운드 기록이 `evaluation_rounds.jsonl` 전체를 다시 읽고 파싱합니다. C-2 미수정 상태(통과 장면이 검증마다 라운드 append)에서는 원장 성장이 사용량 대비 초선형이라 이 O(n²) 패턴이 더 빨리 뭅니다. 파일 핸들 누수는 없으나(`read_text`가 닫음) 파싱 비용이 복리로 증가합니다.

**Containment:** `validate_images` 호출당 원장을 1회 읽고 엔트리를 전달; 또는 장면별 커서 파일 유지.

### LD-10. ffprobe 성공 경로의 JSON 파싱이 무방비

- **클래스:** 예외 미처리 (LD-2의 사소한 형제)
- **파일:** `video_qa.py:209-211`
- **심각도:** Low

`returncode != 0` 검사 이후의 `json.loads(result.stdout)`는 출력이 정상이라고 가정합니다. `-of json`에서 ffprobe가 stdout에 경고를 쓰는 경우는 드물지만 특이 컨테이너에서 실제로 관찰됩니다; 결과는 raw `JSONDecodeError`. `try/except` → `HarnessError` 한 번이면 닫힙니다. (두 줄 아래의 h264 누락 `StopIteration`은 H-5로 기등재.)

---

## 리소스 누수 점검 결과

명시적으로 확인했고 **깨끗함**:
- `PIL.Image.open`은 `with` 블록 내 사용 (`image_qa.py:241`) — 핸들 누수 없음.
- 모든 파일 읽기/쓰기가 `read_text`/`write_text`/컨텍스트 관리 핸들 사용 — 매달린 디스크립터 없음.
- `subprocess.run` + `capture_output` — 파이프 누수 없음 (위험은 누수가 아니라 행, LD-4).
- 스레드·소켓 없음, 테스트 외 tempfile 사용 없음.

## 요약표

| ID | 클래스 | 심각도 | 검증 | 한 줄 containment |
|----|-------|--------|------|--------------------|
| LD-1 | 예외 미처리 + torn append | High | repro | 잘린 마지막 줄 허용; 그 외 `HarnessError` |
| LD-2 | 예외 미처리 + 비원자적 쓰기 | High | repro | `read_json`→`HarnessError`; `write_json`→tmp+`os.replace` |
| LD-3 | 엣지케이스 (버전 갭) | Medium | repro | count+1이 아닌 max-version+1 |
| LD-4 | 행 / 활성성 | High | 정적 | 4개 지점 전부 `timeout=` + `TimeoutExpired`→`HarnessError` |
| LD-5 | 파괴 윈도우 | Medium | 정적 | 이전 것 삭제 전 새 출력 확보 |
| LD-6 | 경쟁 조건 | — | 교차 참조 | C-1과 동일 수정 |
| LD-7 | 엣지케이스 (인덱스 vs id, 빈 리스트) | Medium | 정적 | id-인덱스 대조; 빈 스토리보드 실패 |
| LD-8 | 엣지케이스 (glob 접두사) | Low | 정적 | 프로필 사이드카 정확 일치 |
| LD-9 | 스케일링 절벽 | Low→Med | 정적 | 호출당 원장 1회 읽기 |
| LD-10 | 예외 미처리 | Low | 정적 | ffprobe JSON 파싱 가드 |
