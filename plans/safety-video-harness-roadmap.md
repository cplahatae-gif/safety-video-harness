# 안전교육 영상 자동제작 플러그인 구현 로드맵

> 기준 PRD: `plans/safety-video-harness-final-prd.md`  
> 대상 플러그인: `safety-video-harness`  
> 현재 기준일: 2026-06-10  
> 원칙: 스토리보드와 검증은 무료 루프에서 최대한 반복하고, 이미지/영상/TTS live 호출은 승인 게이트와 비용 명세 뒤에서만 실행한다.

## 0. 현재 상태 요약

### 완료

- [x] 독립형 PRD 작성: `plans/safety-video-harness-final-prd.md`
- [x] 이전 PRD archive 분리: `plans/archive/`
- [x] Codex 플러그인 스캐폴딩: `.codex-plugin/plugin.json`
- [x] 에이전트/스킬/훅 뼈대: `agents/`, `skills/`, `hooks/`
- [x] 프로젝트 초기화 CLI: `scripts/init_project.py`
- [x] 교육자료 등록: `scripts/register_sources.py`
- [x] 실제 PPTX fixture 복사: `fixtures/sources/remicon-collision-guide.pptx`
- [x] PPTX 내부 이미지 12개 추출: `projects/remicon-collision-guide/sources/rendered/`
- [x] 레미콘 자료 기반 주제 추출: `sources/extracted_topics.json`
- [x] 레미콘 자료 기반 30초/6컷 스토리보드: `storyboard/scenes.json`
- [x] Gate 1 승인 전 live 이미지 생성 차단 테스트
- [x] Gate 2 승인 전 live 영상 생성 차단 테스트
- [x] 이미지/영상 프롬프트 dry-run 생성
- [x] 상세 프롬프트 계약: `safety_video_harness/prompt_contract.py`
- [x] 레퍼런스 프로필 자동 반영: `safety_video_harness/assets.py`
- [x] 전체 테스트 통과: `10 passed`

### 아직 미구현

- [ ] 운영용 주제 선택: 테스트용 첫 주제 자동 선택과 실제 사용자 `--topic-id` 선택 분리
- [ ] 진짜 PPTX/PDF/DOCX 렌더링/OCR: 현재 PPTX는 내부 미디어 추출 중심
- [ ] 이미지 reference 자체를 비전으로 분석해 인물/장비 특징을 자동 추출
- [ ] Codex 내장 `imagegen` skill/tool 기반 이미지 생성 흐름
- [ ] 승인 이미지 버전 관리와 선택 재생성
- [ ] Gate 2 비용 명세와 승인 워크플로우 강화
- [ ] 실제 Higgsfield CLI / Seedance live 생성 어댑터
- [ ] 영상 `ffprobe`/`ffmpeg` 검사와 프레임 샘플링
- [ ] 스토리보드/이미지/영상 3자 일치 검증
- [ ] TTS 생성
- [ ] 자막 생성과 ffmpeg 합성
- [ ] 최종 MP4/검수 패키지 생성
- [ ] hook 런타임 적용 검증
- [ ] single-writer lock
- [ ] `external_upload_allowed=false` live 차단
- [ ] 플러그인 설치/재설치/패키징 검증

## 1. 최종 목표

사용자는 플러그인으로 다음 흐름을 실행할 수 있어야 한다.

```text
교육자료 등록
  -> 자료 렌더링
  -> 복수 주제 추출
  -> 사용자 주제 선택
  -> 레퍼런스 이미지/프로필 반영
  -> 스토리보드 생성과 무료 수정
  -> Gate 1 승인
  -> 이미지 키프레임 생성
  -> 이미지 QA와 선택 재생성
  -> Gate 2 승인과 비용 확인
  -> Seedance 영상 생성
  -> 영상 프레임 검사
  -> TTS/자막/합성
  -> 최종 MP4와 QA 패키지
```

최종 산출물은 플러그인이고, 하네스는 플러그인 내부에서 제작 단계를 통제하는 실행/검증 구조다.

## 2. 실행 가드레일

- 유료 호출은 테스트나 자동 루프에서 금지한다.
- `--live`는 명시 승인과 비용 명세 없이는 실패해야 한다.
- 외부 업로드가 금지된 프로젝트는 live 이미지/영상/TTS를 차단한다.
- 승인된 스토리보드, 승인 이미지, 승인 영상은 덮어쓰지 않고 새 버전으로 보존한다.
- 모든 안전 주장에는 `source_citations`가 있어야 한다.
- 이미지 프롬프트는 영어 생성 지시로 유지하고, 자막/문자 생성은 금지한다.
- 영상 생성은 sliding-chain 규칙을 따른다.
- 완료 주장은 `evidence/`에 명령 출력과 산출물 검증 결과가 있어야 한다.

## 3. 프로젝트 폴더 사용 규칙

레퍼런스는 아래 위치에 둔다.

```text
projects/<slug>/
  model/cast/                 # 사람, 작업자, 신호수, 캐릭터 기준 이미지와 프로필
  model/ppe/                  # 안전모, 조끼, 장갑, 안전화 등 PPE
  product/equipment/          # BCT, 덤프트럭, 장비, 제품
  ref/candidates/             # 후보 레퍼런스. 자동 반영하지 않음
  ref/approved/               # 승인 레퍼런스. 프롬프트에 자동 반영
```

사용 규칙:

- 인물 기준 이미지는 `model/cast/worker-001-front.png`처럼 둔다.
- 인물 설명은 `model/cast/worker-001.profile.md`로 둔다.
- 장비 설명은 `product/equipment/bct-trailer.md`처럼 둔다.
- 스타일 설명은 `ref/approved/safety-animation-style.md`처럼 둔다.
- 이미지 옆에 같은 이름의 `.md`가 있으면 해당 설명을 프롬프트에 넣는다.
- 후보 이미지는 `ref/candidates`에 보관하고, 쓸 것만 `ref/approved`로 이동한다.

## 4. 구현 Wave

### Wave A. 현재 dry-run 기준선 잠금

목표: 지금까지 구현된 MVP가 깨지지 않도록 기준선을 잠근다.

상태:

- [x] 실제 PPTX fixture 기반 테스트 추가
- [x] 상세 프롬프트 계약 테스트 추가
- [x] 레퍼런스 asset 반영 테스트 추가
- [x] `uv run pytest -q` 통과

남은 작업:

- [x] `evidence/baseline-current-state.txt`에 현재 전체 dry-run 실행 로그 저장
- [x] `.pytest_cache`, `__pycache__`, `.DS_Store` 같은 생성물 정리 정책 확정
- [x] README의 빠른 시작 명령과 실제 스크립트 인자 일치 재검증

수용 기준:

- `uv run pytest -q`가 통과한다.
- `projects/remicon-collision-guide`에서 `generate_images.py --dry-run`, `generate_seedance.py --dry-run`이 통과한다.
- 프롬프트 JSON에 `continuity_bible`, `reference_assets`, `sliding_chain_contract`가 있다.

### Wave A-1. 운영용 주제 선택과 자료 렌더링 보강

목표: 현재 fixture 중심 구현을 실제 운영 자료 처리로 확장한다.

문제:

- 현재 `intake_project.py --defaults`는 테스트 편의를 위해 첫 번째 추천 주제를 자동 선택한다.
- 실제 운영에서는 교육자료에 여러 주제가 있을 수 있으므로 사용자가 `topic_id`를 명시해야 한다.
- 현재 PPTX 처리는 내부 `ppt/media/*` 이미지 추출 중심이며, 슬라이드 자체를 렌더링/OCR하는 단계가 아니다.

구현 대상:

- [x] `scripts/select_topic.py --project <path> --topic-id topic-001`
- [x] `project_config.json`에 `selected_topic_id` 저장
- [x] 운영 모드에서 topic 미선택 시 storyboard 생성 실패
- [x] `intake_project.py --defaults`는 테스트/샘플 전용임을 README에 명시
- [x] `render_pptx_sources.py`를 `media_extract`와 `slide_render` 모드로 분리
- [ ] `soffice`가 있으면 슬라이드 PNG 렌더링
- [x] `soffice`가 없으면 명확한 경고와 media extraction fallback
- [x] OCR/text extraction 확장 지점 정의

수용 기준:

- [x] topic 미선택 운영 프로젝트에서 `plan_storyboard.py`가 실패한다.
- [x] `select_topic.py`로 선택한 topic만 storyboard에 반영된다.
- [x] 실제 fixture는 fallback으로도 기존 테스트를 통과한다.
- [x] evidence에 rendering mode가 남는다.

### Wave B. 레퍼런스 비전 프로파일링

목표: 사용자가 사람 이미지나 작업상황 사진을 넣으면, 이미지 자체를 분석해 `.profile.md` 또는 manifest로 저장한다.

구현 대상:

- [x] `scripts/analyze_reference_assets.py`
- [x] `safety_video_harness/reference_profile.py`
- [x] `projects/<slug>/ref/approved/reference_assets.json`
- [x] 사람/장비/스타일/작업상황 분류 필드

입력:

- `model/cast/*.png|jpg|jpeg|webp`
- `model/ppe/*.png|jpg|jpeg|webp`
- `product/equipment/*.png|jpg|jpeg|webp`
- `ref/approved/*.png|jpg|jpeg|webp`

출력 예시:

```json
{
  "assets": [
    {
      "asset_id": "worker-001-front",
      "role": "cast",
      "path": "model/cast/worker-001-front.png",
      "description": "Korean adult worker, white hard hat, orange vest...",
      "locked_traits": ["helmet color", "vest color", "body proportion"],
      "usage": "identity_reference"
    }
  ]
}
```

검증:

- [x] 이미지 파일만 있고 `.md`가 없어도 profile manifest가 생성된다.
- [x] `.md`가 있으면 자동 분석 결과보다 사용자 설명을 우선한다.
- [x] `ref/candidates` 파일은 자동 반영하지 않는다.
- [x] `ref/approved` 파일만 프롬프트에 반영한다.
- [x] `scripts/approve_reference.py`로 candidates에서 approved로 이동할 때 provenance를 기록한다.

주의:

- 이 단계는 비전 모델이 필요할 수 있으므로 live 호출 정책을 분리한다.
- 외부 업로드 불가 프로젝트에서는 이미지 분석 live를 차단하고 수동 `.md` 설명만 허용한다.

### Wave C. Codex imagegen 이미지 생성 흐름

목표: Gate 1 승인 후 Codex 내장 `imagegen` skill/tool로 키프레임 이미지를 실제 생성한다.

설계 원칙:

- 기본 경로는 API adapter가 아니라 Codex 내장 `imagegen` skill/tool이다.
- Python CLI가 직접 내장 imagegen 도구를 호출하는 구조로 가정하지 않는다.
- `generate_images.py --dry-run`은 `image_prompts.json`과 별도로 `prompts/imagegen_jobs.json`을 생성한다.
- Codex 에이전트는 `imagegen_jobs.json`을 읽고 `imagegen` skill을 사용해 이미지를 만든 뒤 지정된 `images/draft/scNN_vNNN.png`로 이동 또는 복사한다.
- OpenAI Image API/CLI fallback은 사용자가 명시적으로 API/CLI 경로를 요청할 때만 허용한다.

구현 대상:

- [x] `safety_video_harness/imagegen_jobs.py`
- [x] `prompts/imagegen_jobs.json`
- [x] Codex `imagegen` skill 호출 지침을 `AGENTS.md`/README에 명시
- [x] `scripts/generate_images.py --live`는 내장 imagegen 실행 지시와 output contract를 생성
- [x] `images/draft/scNN_v001.png`
- [x] `images/approved/scNN.png`
- [ ] `images/rejected/scNN_vNNN.png`
- [x] `qa/image_generation_runs.jsonl`

선행 조건:

- Gate 1 승인
- `external_upload_allowed=true`
- selected topic 존재
- 이미지 프롬프트 dry-run 검증 통과
- reference asset manifest 존재 또는 수동 profile 존재

필수 동작:

- [x] live 실행 전 예상 생성 수와 비용 위험을 출력한다.
- [x] 기존 파일을 덮어쓰지 않는다.
- [x] scene별 output path를 버전으로 저장한다.
- [ ] 실패 시 `errors.jsonl`에 append한다.
- [x] `--only sc03` 같은 선택 생성 옵션을 제공한다.
- [x] `--regenerate sc03`는 기존 파일을 보존하고 새 버전을 만든다.
- [x] 생성 후 `$CODEX_HOME/generated_images/...`에만 남기지 않고 프로젝트 `images/draft/`로 이동 또는 복사한다.

검증:

- [x] Gate 1 미승인 live 생성은 실패한다.
- [x] `external_upload_allowed=false` live 생성은 실패한다.
- [x] dry-run은 유료 호출 없이 prompt plan만 만든다.
- [x] 테스트에서는 실제 imagegen 호출 대신 fake generated file로 output contract와 버전 보존을 검증한다.
- [x] secret/token/API key 문자열이 evidence와 markdown에 남지 않는다.

### Wave D. 이미지 QA 루프

목표: 생성된 이미지가 스토리보드와 프롬프트 계약에 맞는지 검증하고, 재생성 대상만 표시한다.

구현 대상:

- [x] `safety_video_harness/image_qa.py`
- [x] `scripts/validate_images.py`
- [x] `qa/image_reviews.json`
- [x] `qa/story_image_reviews.json`

검증 항목:

- [ ] 인물 일관성
- [ ] PPE 색상과 착용 상태
- [ ] BCT/덤프트럭 형태 일관성
- [ ] 사각지대/보행자 통로/동선 표시
- [ ] 사고 충돌 순간이나 부상 장면 금지
- [ ] 생성 텍스트/로고 금지
- [ ] 스토리보드 장면과 이미지 내용 일치

Pass/Block 기준:

- `story_match_score < 4`이면 blocker
- `identity_consistency_score < 4`이면 blocker
- `ppe_score < 5`이면 안전교육 blocker
- 생성 텍스트, 로고, 충돌 순간, 부상 장면은 즉시 blocker

출력:

```json
{
  "scene_id": "sc03",
  "story_match_score": 5,
  "identity_consistency_score": 4,
  "ppe_score": 5,
  "blocking_issues": [],
  "decision": "approve_for_video"
}
```

수용 기준:

- blocker가 있는 이미지는 Gate 2 대상에 포함되지 않는다.
- blocker가 있는 씬만 선택 재생성 목록에 표시된다.

### Wave E. Gate 2 비용 명세와 승인

목표: 영상 live 생성 전 비용과 재생성 위험을 사용자가 확인하도록 만든다.

구현 대상:

- [x] `scripts/estimate_video_cost.py`
- [x] `scripts/approve_gate.py --gate image_to_video`
- [x] `safety_video_harness/gate_validation.py`
- [x] `approvals.json` cost disclosure 강화

필수 필드:

- clip count
- seconds per clip
- total seconds
- estimated credits
- expected regeneration risk
- approved image versions
- Seedance model and parameters
- pricing source or manual estimate note
- estimate timestamp

검증:

- [x] 비용 명세 없는 Gate 2 승인은 실패한다.
- [x] 승인 이미지가 없으면 Gate 2 승인은 실패한다.
- [x] 이미지 QA가 통과하지 않으면 Gate 2 승인은 실패한다.
- [x] clip count가 0이면 Gate 2 승인은 실패한다.
- [x] `video_prompts.json`이 없으면 Gate 2 승인은 실패한다.
- [x] `external_upload_allowed=false`이면 Gate 2 승인은 실패한다.

### Wave F. Higgsfield CLI / Seedance live 어댑터

목표: Gate 2 승인 후 Higgsfield CLI로 Seedance 클립을 생성한다.

구현 대상:

- [ ] `safety_video_harness/seedance_adapter.py`
- [ ] fake CLI adapter
- [ ] `scripts/generate_seedance.py --live`
- [ ] `video/clips/scNN_scNN+1_v001.mp4`
- [ ] `qa/video_generation_runs.jsonl`

선행 조사:

- [ ] `higgsfield --help` 저장
- [ ] `higgsfield generate --help` 저장
- [ ] 인증 방식 확인
- [ ] start/end frame 업로드 방식 확인
- [ ] polling/status 확인
- [ ] 결과물 다운로드 경로 확인

검증:

- [ ] Higgsfield CLI가 없으면 명확한 오류를 반환한다.
- [ ] Gate 2 미승인 live 영상 생성은 실패한다.
- [ ] dry-run은 유료 호출 없이 video prompt plan만 만든다.
- [ ] live adapter는 fake CLI로 테스트한다.
- [ ] 실패한 유료 생성은 자동 재시도하지 않는다.
- [ ] polling timeout은 `errors.jsonl`에 남기고 사용자 승인 큐로 보낸다.

### Wave G. 영상 검사와 3자 일치 검증

목표: 생성된 영상이 스토리보드, 이미지 키프레임, 영상 프레임과 일치하는지 검사한다.

구현 대상:

- [ ] `scripts/inspect_video.py`
- [ ] `safety_video_harness/video_inspection.py`
- [ ] tiny local MP4 fixture for tests
- [ ] `video/sampled_frames/scNN/start.png`
- [ ] `video/sampled_frames/scNN/middle.png`
- [ ] `video/sampled_frames/scNN/end.png`
- [ ] `qa/video_reviews.json`
- [ ] `qa/triad_reviews.json`

검사:

- [ ] `ffprobe` 길이, fps, 해상도, 오디오 트랙
- [ ] `ffmpeg` 시작/중간/끝 프레임 추출
- [ ] start frame과 승인 이미지 비교
- [ ] end frame과 다음 승인 이미지 비교
- [ ] 스토리보드 action과 샘플 프레임 내용 비교
- [ ] native audio 제거 여부 확인

수용 기준:

- 영상이 멋있어도 교육 목표와 다르면 reject한다.
- start/end frame이 크게 다르면 해당 클립은 재생성 대상이다.
- `triad_match_score < 4`이면 최종 합성 대상에서 제외한다.

### Wave H. TTS, 자막, 합성

목표: 한국어 내레이션, 자막, 영상 클립을 최종 MP4로 합성한다.

구현 대상:

- [ ] `scripts/generate_tts.py`
- [ ] `scripts/compose_video.py`
- [ ] `audio/scNN.wav`
- [ ] `subtitles/final.srt`
- [ ] `output/final.mp4`
- [ ] `output/qa-package/`

정책:

- Seedance native audio는 기본 제거한다.
- 한국어 TTS는 별도 생성한다.
- 자막은 한국어 폰트로 번인한다.
- 나레이션은 `duration_sec * 5` 글자 제한을 우선 유지한다.

검증:

- [ ] TTS live는 명시 승인 전 실패한다.
- [ ] ffmpeg 합성 산출물이 존재한다.
- [ ] 최종 MP4 길이가 목표 길이와 허용 오차 안에 있다.
- [ ] 자막이 존재하고 타이밍이 씬 길이와 맞는다.

### Wave I. 훅 런타임 검증과 보호 구역

목표: 훅 파일이 존재하는 수준을 넘어 실제 Codex 실행에서 차단이 동작하는지 검증한다.

현재 위험:

- 현재 hook 파일은 존재하지만, 실제 플러그인 런타임에 어떻게 등록되는지는 별도 검증이 필요하다.
- 단순히 `--live` 문자열을 무조건 막으면, 승인된 live 실행까지 막을 수 있다.
- hook은 project path, gate 상태, `external_upload_allowed`, cost disclosure를 읽어 판단해야 한다.

구현 대상:

- [ ] hook install/config 문서
- [ ] 새 세션에서 hook smoke test
- [ ] protected paths enforcement
- [ ] secret write veto
- [ ] stop sentinel guard

검증:

- [ ] Gate 없는 `--live` 명령이 훅에서 차단된다.
- [ ] Gate와 upload permission이 충족된 명령은 hook에서 통과한다.
- [ ] protected path 쓰기가 차단된다.
- [ ] API key 문자열 파일 기록이 차단된다.
- [ ] `.harness/DONE` 없는 완료가 차단된다.

### Wave J. single-writer lock과 재생성/롤백

목표: 상태 파일 충돌과 승인 산출물 덮어쓰기를 방지한다.

구현 대상:

- [x] `safety_video_harness/locks.py`
- [x] `safety_video_harness/error_log.py`
- [x] `scenes.json`, `approvals.json`, `.harness/self_score.json` lock 적용
- [ ] `--regenerate` 버전 보존
- [ ] `--rollback` 새 파일 생성 방식
- [ ] 승인 이력 append-only 보존

검증:

- [x] lock 보유 중 같은 파일 쓰기 시도가 실패한다.
- [ ] 재생성은 기존 승인 파일을 삭제하지 않는다.
- [ ] rollback은 승인 이력을 삭제하지 않는다.
- [ ] 모든 adapter 실패는 `.harness/errors.jsonl`에 append-only로 기록된다.

### Wave K. 플러그인 패키징과 설치 검증

목표: 현재 작업폴더 안에서만 동작하는 상태가 아니라, Codex 플러그인으로 재사용 가능하게 만든다.

구현 대상:

- [ ] `.codex-plugin/plugin.json` 최종 검증
- [ ] plugin install/reinstall 절차 문서화
- [ ] 플러그인 명령 목록 정리
- [ ] 새 프로젝트 생성 smoke test
- [ ] README 최종 사용법 갱신

수용 기준:

- 새 세션에서 플러그인을 사용할 수 있다.
- 새 프로젝트를 생성하고 dry-run 체인을 끝까지 돌릴 수 있다.
- 레퍼런스 배치 규칙이 README에 있다.
- live 호출은 승인 조건이 없으면 실패한다.

## 5. 다음 실행 권장 순서

### 다음 작업 묶음 1: 무료 검증 강화

우선순위가 가장 높다.

- Wave A 남은 기준선 잠금
- Wave A-1 운영용 주제 선택과 자료 렌더링 보강
- Wave B 레퍼런스 비전 프로파일링의 dry-run/수동 `.md` 우선 정책
- Wave E Gate 2 비용 명세 강화
- Wave J single-writer lock 기본 구현

이 묶음은 유료 호출 없이 품질과 안전성을 높인다.

### 다음 작업 묶음 2: Codex imagegen 이미지 생성 준비

- Wave C Codex imagegen 이미지 생성 흐름
- Wave D 이미지 QA 루프
- 승인 이미지 버전 관리

이 묶음부터 외부 업로드와 비용 정책이 중요하다. 단, 기본 구현은 OpenAI API adapter가 아니라 Codex 내장 `imagegen` skill/tool 사용을 전제로 한다.

### 다음 작업 묶음 3: 영상 live 준비

- Wave F Higgsfield CLI 계약 확인
- Wave G 영상 검사와 3자 일치 검증

Higgsfield CLI가 설치되어 있지 않으면 fake CLI 테스트까지 먼저 구현한다.

### 다음 작업 묶음 4: 최종 영상 제작

- Wave H TTS/자막/합성
- Wave K 플러그인 패키징

## 6. OMO 실행 요청 예시

무료 검증 강화부터 실행하려면 다음처럼 요청한다.

```text
$omo:start-work
plans/safety-video-harness-roadmap.md를 실행 계획으로 삼아서 다음 작업 묶음 1만 구현해줘.

범위:
- Wave A 남은 기준선 잠금
- Wave A-1 운영용 주제 선택과 자료 렌더링 보강
- Wave B 레퍼런스 비전 프로파일링은 유료/외부 업로드 없이 dry-run과 수동 .md 우선 정책까지만
- Wave E Gate 2 비용 명세 강화
- Wave J single-writer lock 기본 구현
- live 이미지 생성, live Seedance 생성, live TTS 호출 금지
- 유료 호출 금지
- plans/archive 수정 금지

검증:
- uv run pytest -q 통과
- 실제 fixture projects/remicon-collision-guide 기준 dry-run 재실행
- evidence/ 아래 실행 증거 저장
- README 사용법 갱신

끝나면 구현한 파일, 테스트 결과, 남은 작업을 요약해줘.
```

Codex imagegen 이미지 생성 흐름을 구현하려면 다음처럼 요청한다.

```text
$omo:start-work
plans/safety-video-harness-roadmap.md의 다음 작업 묶음 2를 구현해줘.

범위:
- Codex 내장 imagegen skill/tool을 기본 이미지 생성 경로로 고정
- generate_images.py는 imagegen job spec과 output contract를 생성
- 테스트에서는 실제 imagegen 호출 없이 fake generated file만 사용
- OpenAI API/CLI adapter 구현 금지
- Gate 1, external_upload_allowed, 버전 보존 정책 적용
- 이미지 QA 루프 강화

검증:
- live 호출은 승인/업로드 허용 없으면 차단
- fake generated file로 images/draft 버전 파일 저장 테스트
- blocker 이미지 선택 재생성 테스트
- uv run pytest -q 통과
- evidence/에 실행 로그 저장
```

실제 이미지 생성 파일럿을 할 때는 별도 승인 문구가 필요하다.

```text
$omo:start-work
plans/safety-video-harness-roadmap.md 기준으로 실제 이미지 생성 파일럿을 실행해줘.

명시 승인:
- Codex 내장 imagegen skill/tool 사용 허용
- 사용할 프로젝트: projects/remicon-collision-guide
- 사용할 씬: sc01만
- 생성 전 imagegen job spec과 저장 경로를 먼저 보여주고 내 확인을 받은 뒤 실행
- Seedance 영상 생성과 TTS는 금지
```

## 7. 완료 정의

로드맵 전체 완료 조건:

- [ ] 플러그인 설치 후 새 프로젝트 생성 가능
- [ ] 실제 교육자료 등록 가능
- [ ] 주제 후보 추출 가능
- [ ] 레퍼런스 이미지/프로필 반영 가능
- [ ] 스토리보드 무료 수정 루프 가능
- [ ] Gate 1 후 이미지 생성 가능
- [ ] 이미지 QA와 선택 재생성 가능
- [ ] Gate 2 후 Seedance 영상 생성 가능
- [ ] 영상 프레임 검사 가능
- [ ] 스토리보드/이미지/영상 3자 일치 검증 가능
- [ ] TTS/자막/합성 가능
- [ ] 최종 MP4와 QA 패키지 생성 가능
- [ ] 모든 유료 호출은 명시 승인과 evidence를 가진다.
