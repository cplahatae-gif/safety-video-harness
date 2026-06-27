# 두 분기 비교 종합: 테스트_코덱스 → 테스트_클로드 포팅 가이드

> 생성: 2026-06-27 / 방식: 16-에이전트 병렬 비교 워크플로(신규 모듈 8 + 변경 번들 4 + 인프라 3 + 종합 1)
> 공통 조상 커밋 `2a91849` 이후 분기. Codex 6커밋 선행, Claude는 `.claude/` 하네스 구조로 리팩터 + `gemini_image.sh` 추가.

## 1. 결론 요약

**Codex가 명백히 앞선 핵심 축은 (a) 시각 일관성 강제(asset-lock + 수동 시각 QA 게이트), (b) 견고성 인프라(subprocess 타임아웃·원자적 쓰기·락·손상 내성), (c) 품질 doctrine 문서(CONTEXT.md·확장 루브릭)입니다.** Claude는 영상 QA에서 파이프라인이 끝나고(최종 조립 부재), 이미지 QA가 "16:9 readable이면 자동 5점"으로 생성기 자기승인 패턴이 그대로 남아 있어 AGENTS.md 규칙에 실제 구멍이 있습니다.

**반대로 훅(hooks)·플러그인 패키징·이미지 생성 경로(codex_image.sh/gemini_image.sh)·이름 규약(/ralph-loop, .claude/)은 Claude가 이미 동등 또는 우위**이며, Codex의 `codex_builtin_imagegen`·`$CODEX_HOME`·`.codex-plugin`·argv 훅은 가져오면 오히려 퇴행입니다.

**가장 먼저 가져올 1~3개**: ① 라이브러리 견고화 번들(io 원자적 쓰기 + locks O_EXCL + evaluation_rounds 손상내성 + scene_links 가드 + video_qa h264 가드 + 회귀테스트 — Claude 트리에서 13/14 실패로 실증된 결함), ② `external_tools.py` 중앙 subprocess 러너(타임아웃 없는 무한 행 제거, 위 ①·후속 다수의 선행조건), ③ 매뉴얼 시각-일관성 리뷰 게이트(`image_manual_review.py` + `image_qa.py` 통합, 생성기 자기승인 차단).

---

## 2. 포팅 우선순위 표 (worth_porting=true, 중복 통합·우선순위/가치순)

| 항목 | 영역 | 우선순위 | 작업량 | 가져올 가치 | 리스크 |
|---|---|---|---|---|---|
| 라이브러리 견고화 회귀 픽스+테스트(io 원자적 write·read_json 에러래핑 / locks O_EXCL / evaluation_rounds 손상내성·원자 append / scene_links 빈씬·scNN 가드 / video_qa h264 None가드) | 테스트·패키징, 공유번들(product/visualQA), reference/locks | **High** | Claude 트리 13/14 실패로 실증된 실제 크래시·손상 방지 | 모듈에 아키텍처 변경이 섞여 통째 복사 금지 |
| `external_tools.py` 중앙 subprocess 러너(timeout→HarnessError, run_tool_json) | 외부도구, 공유번들×3, 테스트 | **High** | ffmpeg/ffprobe/higgsfield/soffice 무한 행 제거 | 6개 호출부 외과적 마이그레이션 필요 |
| `asset_lock.py` 에셋 락 레이어 + reference_media_pack | 에셋락, prompt_contract 번들 | **High** | 이 영역 최대 기능 격차(문서로만 있던 일관성 규율을 코드 강제) | 통합 표면 5~6개 모듈, Codex 내장 imagegen 문구 치환 필수 |
| 매뉴얼 시각-일관성 리뷰 게이트(`image_manual_review.py`+`image_qa.py` 통합, MIN 24→44) | 이미지 시각QA, visualQA 번들 | **High** | 생성기 자기승인 차단(AGENTS.md 규칙 구멍 메움) | asset_lock·image_versions 분리 포팅 필요, 게이트만 켜면 리뷰파일 생길 때까지 전부 블로킹 |
| `image_evaluation_flow.py` 통과 씬 조기종료(3줄) | 이미지 시각QA, visualQA 번들 | **High** | RALPH 조기종료 원칙 부합, 원장 오염 제거 | 거의 없음(카운트 소비처 표시 점검만) |
| RALPH 재생성 크리틱 강화(`ralph_prompt.py`: QUALITY_PRESSURE+구조화) | RALPH 모듈, visualQA, prompt 번들 | **High** | 코스메틱 재롤 차단→20회 캡 내 수렴 | 테스트 `test_image_ralph_loop.py:45` "Regenerate sc01" 단언 갱신 |
| `approve_reference` role 라우팅(+--role CLI) | 레퍼런스 카탈로그, reference 번들 | **High** | AGENTS.md "Ask where each reference belongs" 유일 구현 경로 | 스캔측 parent/child 보완 없으면 버그 절반만 해결 |
| PPTX 슬라이드 텍스트→facts 추출 파이프라인 | 공유번들(product) | **High** | 비-레미콘 product 워크플로 핵심(현재 placeholder만) | project.py의 CLAUDE.md 라인 보존 필요(통째 교체 금지) |
| CONTEXT.md 신설(용어집+비협상정책+오리엔테이션) | 문서·가이던스 | **High** | 도구 중립 운영 일관성, 용어 단일출처 | 끝 아키텍처 섹션이 Codex 모듈명 참조→Claude 모듈명으로 교체 |
| AGENTS.md 품질 doctrine 선별 추가(asset lock/text-only=draft/확장 QA축) | 문서·가이던스 | **High** | 도구 경로 무관 품질 규칙, 결과 일관성 | 이미지 경로 규칙·깨진 참조(미포팅 스크립트 거명) 제외 |
| evaluation-rubrics.md 11축/44-55 + 수동 시각QA 요구 | 문서·가이던스 | **High** | 루브릭만 올려도 전체 QA 게이트 상승 | 미보유 코드를 전제조건으로 못박음→코드 타이밍 맞추거나 "or equivalent" 완화 |
| `image_versions.py` 공용 추출(max기반 버전·path-traversal 가드) | 에셋락 | Medium | len()+1→max()+1 버그내성, 프로젝트 외부 출력 차단 | record_image_output 자동증분 동작변경은 선별 |
| 휴리스틱 시각 리뷰+콘택트시트(`image_visual_review.py`) | 이미지 시각QA | Medium | 게이트를 실무화(JSON 수기작성 불필요) | asset_lock 의존→status 판정만 떼어 최소 의존 |
| `_exact_profile_sidecar` 멀티앵글 매칭(-front/back/left/right/side) | 레퍼런스 카탈로그 | Medium | -front 외 다각도 cast/ppe 사이드카 매칭 | assets.py·reference_profile.py 두 곳 적용 |
| `reference_catalog.py` 스캔 일원화 | 레퍼런스 카탈로그, reference 번들 | Medium | 중복 드리프트 원천 제거(Claude 로드맵 07에 이미 계획) | 순수 리팩터, Claude 자체 진행 시 중복 |
| scene_links 빈-씬 가드 + scNN 순번 검증 | 정합검증, prompt 번들 | Medium | 빈 시나리오 false-pass 차단 | 빈 스토리보드 통과시키던 스모크 테스트 조정 |
| 평가원장 손상내성+원자 append(evaluation_rounds/arbiter) | visualQA 번들 | High→Medium | bare json.loads 크래시·비잠금 append 제거 | file_lock·_read_round_entries 이미 존재→신규의존 없음 |
| 에스컬레이션 임계 2→3 정합화 | visualQA 번들 | Medium | 코드-문서 불일치 해소("three times") | 동작변경, rubrics·few-shot 기대치 확인 |
| slide_render 실제 구현(soffice→pdftoppm)+폴백 | 공유번들(product) | Medium | render_pptx_sources --slide_render 깨진 경로 수복 | external_tools 동반 또는 인라인, 미설치 폴백 확인 |
| collect_image_outputs(생성이미지 자동수집) | 공유번들(product) | Medium | record_image_output 이미 보유→래퍼만 추가 | 낮음 |
| project_relative_output 경로봉쇄 가드(인라인) | 공유번들(product) | Medium | "이미지를 프로젝트 밖에 두지 말 것" 코드강제 | 낮음 |
| apply_intake(운영자 인테이크 반영) | 공유번들(product) | Medium | "인테이크 인터뷰 필수" 규칙 구현 | production_consistency_policy 등 Codex 키 분리 |
| OpenCV MCP 무비용 CV 사전필터 가이드(문서) | 외부도구, 문서 | Medium | 유료 비전 전 무료 1차 드리프트 측정 doctrine | 등록부 ~/.codex→claude mcp add 번역, soft 가치 |
| 영상 최종 조립(assemble_video) 스켈레톤 | 영상 조립 | Medium | Wave H(output/final.mp4) 공백 메움 | 자막번인·오디오 미구현→골격일 뿐, 경로/명명 적응 필요 |
| 스토리보드 Gate1 HTML 대시보드 | 대시보드 | Medium | 사람용 게이트 검토 표면(스키마 100% 호환) | 매우 낮음(드롭인) |
| higgsfield-seedance 문서 보강(CLI flags·Soul ID·production order) | 문서 | Medium | 검증된 운영지식, doctrine-실행 연결 | "기본 이미지 경로" 한 줄만 codex_image.sh로 치환 |
| 훅 탐지 로직 체리픽(secret sk-/JWT 정규식 + protected-path 세그먼트 매칭) | 훅, 테스트 | Medium | sk-proj-/eyJ JWT·경로 오탐 보강 | 본문 로직만, argv 계약 절대 미포팅 |
| `.profile.md` 독립 에셋 집계 제외 | 레퍼런스 카탈로그 | Low | 매니페스트 노이즈 제거 | 낮음 |
| story_video_alignment 3자 정합 사전점검(클립명 glob 보정 후) | 정합검증 | Low | scene_links·video_qa 없는 공백 | 클립명 _seedance 오탐→glob 매칭 보정 필수 |
| registered_at 실제 타임스탬프 | 공유번들 | Low | 추적성 개선 | 매우 낮음(1줄) |
| asset-lock 일관성 시스템 전체(generation/imagegen 통합) | 에셋락, prompt 번들 | Low | 영상 텍스트-only 금지 가드레일 | 대형 교차, seedance_live 동반변경 |
| reference_media_pack + media_lock_policy 영상 가드레일 | reference 번들 | Low | image-to-video 원칙 강제 | asset_lock 전체 체인 선행 없으면 무동작 |
| seedance duration prepend(+contract 문구 제거) | reference 번들 | Low | brittle .replace 의존 제거 | 두 파일 짝으로 안 바꾸면 모순지시 |
| opencv-mcp-local-reference.md 신설 | 문서 | Low | 시각 QA 층 운영근거 | 시각QA 코드 포팅에 종속 |
| README 개념 섹션(Asset Lock/RALPH/11축) | 문서 | Low | 운영자 설명서 | 다른 문서 포팅과 중복→후순위 |
| schema-validation 실검증(advisory→enforcement) | 훅 | Low | scene-link 훅과 일관성 | 매 쓰기 풀검증 거짓차단 노이즈 우려 |

---

## 3. High 우선순위 상세

### 3-1. 라이브러리 견고화 회귀 픽스 번들
**무엇을**: `io.py`(tmp+os.replace 원자적 쓰기, read_json 누락/파싱오류/비-dict→HarnessError), `locks.py`(marker.open("x") O_EXCL 원자 생성), `evaluation_rounds.py`(찢어진 마지막 JSONL 줄만 관대 skip + file_lock append), `scene_links.py`(빈 스토리보드 HarnessError + scNN id 순번 검증), `video_qa.py`(h264 None 가드)와 신규 `tests/test_review_regressions.py`(14케이스).
**왜**: Codex 테스트를 Claude 트리에 돌리면 13/14가 실패합니다 — 즉 Claude에 실재하는 크래시·손상 결함입니다. `read_json`의 bare json.loads, `file_lock`의 check-then-write TOCTOU, `next(...)`의 StopIteration 모두 안전영상 파이프라인 신뢰성 직결입니다.
**어떻게**: 모듈을 통째 복사하지 말고 픽스만 외과적으로 이식. `io.write_json`의 file_lock 전환은 `locks.py` file_lock과 한 묶음으로 함께. 파일: `safety_video_harness/{io,locks,evaluation_rounds,scene_links,video_qa}.py` + 테스트.
**.claude 충돌 주의**: 같은 모듈에 섞인 **반드시 제외** 항목 — `evaluation_rounds` count>=2→3, `video_qa` transcript_enabled True→False, `imagegen_jobs` codex_cli→codex_builtin_imagegen. 셋 다 Claude 설계와 충돌.

### 3-2. external_tools.py 중앙 subprocess 러너
**무엇을**: `run_tool/run_tool_json`(timeout 강제, TimeoutExpired→HarnessError, start_new_session, JSON 검증) 42~45줄 자기완결 모듈.
**왜**: Claude의 `tools._ocr_language_status`(tesseract)·`seedance_live._run_cli`(higgsfield)·video_qa ffprobe가 timeout 없이 subprocess.run을 호출해 외부 CLI 멈춤 시 무한 대기합니다.
**어떻게**: `external_tools.py`만 신규 추가 후 호출부를 개별·외과적으로 마이그레이션하며 모듈별 timeout 설정(tesseract 30s, ffprobe 30s, higgsfield 1500s, video_inspection 300s). 최소 포팅이 목표면 기존 inline 호출에 `timeout=` 인자만 더하는 축소판도 가능.
**.claude 충돌 주의**: source_rendering·video_inspection은 Claude가 이미 분기(.claude 경로, staged move)했으므로 Codex 코드 직수입 금지. 파일만 들이고 콜사이트는 Claude 현행 위에 얹기. 단 Codex의 `.codex/skills` 경로·opencv 프리플라이트는 함께 가져오지 말 것.

### 3-3. asset_lock.py 에셋 락 레이어
**무엇을**: cast/equipment/space 레퍼런스 유무로 production_locked 판정, 역할별 usage가 부여된 reference_media_pack 생성, 프롬프트 계약·imagegen job·Seedance 업로드까지 일관 주입(`build_asset_lock_manifest`/`build_reference_media_pack`/`asset_lock_prompt_block`/`media_paths`).
**왜**: 이 영역 최대 기능 격차. Claude는 "키프레임을 하나의 인과 흐름으로"·"sliding-chain 연속성"을 문서로만 갖고 코드 강제 수단이 전무합니다.
**어떻게**: `asset_lock.py` 모듈 자체는 Path만 의존하는 순수 코드라 그대로 이식 가능. 통합부(generation·prompt_contract·imagegen_jobs·seedance_live·image_visual_review)는 `build_video_prompt_plan`/`_style_and_reference_prompt_block`에 asset_lock 인자 추가 동반.
**.claude 충돌 주의**: Codex 매니페스트·정책 텍스트의 "Codex 내장 imagegen" 전제를 Claude의 codex_image.sh/gemini_image.sh 경로로 치환해야 합니다. 통합 표면이 넓어 effort L — 모듈만 먼저 들이고 통합은 단계적으로.

### 3-4. 매뉴얼 시각-일관성 리뷰 게이트
**무엇을**: `image_manual_review.py`(io만 의존, 독립)의 5개 visual-lock 축(바닥/차선·배경·캐릭터정체성·차량형상·위험구역) + `image_qa.py` 통합(qa/image_manual_reviews.json 부재→하드 블로커, MIN 24→44).
**왜**: Claude image_qa는 16:9 readable이면 무조건 5점을 줘 실제 시각 검수가 없습니다 — AGENTS.md "생성기 자기승인 금지"·"점수 기반 QA" 위반 구멍.
**어떻게**: `image_manual_review.py`는 그대로 이식. 통합 시 `latest_draft_or_none` 대신 Claude 인라인 `_latest_draft`, regeneration_prompt는 Claude `_regeneration_prompt`로 대체하면 asset_lock·image_versions 없이 게이트만 분리 이식 가능. dry_run/blocked/missing 분기 모두 empty_visual_scores 일관 적용. (Codex image_qa.py 83행 들여쓰기 과잉은 복사 금지.)
**.claude 충돌 주의**: 게이트만 켜면 리뷰파일이 손으로 생길 때까지 전 이미지 블로킹 → 휴리스틱 생성기(image_visual_review)를 함께 또는 rubrics 완화 문구와 타이밍 조율.

### 3-5~3-11. 나머지 High (요약)
- **image_evaluation_flow 3줄 픽스**: `if not blocked: counts=prior; continue` — 통과 씬 iteration 중복기록 제거. 독립·무의존, 즉시 적용.
- **RALPH 크리틱 강화(ralph_prompt.py)**: QUALITY_PRESSURE + Must preserve/change/Do-not-repeat. 순수 텍스트, 하네스 중립. 테스트 단언 갱신 필요.
- **approve_reference role 라우팅**: `reference_profile.py`에 APPROVED_REFERENCE_ROLES 맵+role 인자(기본 root 하위호환)+`approved_reference_dir()`, `scripts/approve_reference.py` --role. Claude 03-issues.md가 H급으로 적시한 중복주입 버그 정수.
- **PPTX 텍스트 추출**: `source_rendering`(ZipFile+ElementTree)→`project`(extracted_text_assets)→`source_facts`(facts_from_text_assets) 3파일 연동. 표준라이브러리만. project.py CLAUDE.md 라인 보존.
- **CONTEXT.md / AGENTS.md doctrine / evaluation-rubrics 11축**: 도구 중립 품질 doctrine. CLAUDE.md에 @CONTEXT.md import 추가로 "AGENTS.md+CONTEXT.md 함께 읽기" 재현. 단 모듈명·이미지경로·미포팅 스크립트 거명은 Claude 기준으로 치환, 코드 미보유 전제조건은 완화 문구 처리.

---

## 4. 리팩터 주의 영역 (단순 복사 위험)

**(1) reference_profile/assets → reference_catalog.py 통합**: Codex의 -94/-61줄 변동은 거의 전부 스캔로직을 `reference_catalog.py`로 빼낸 순수 리팩터입니다. Claude 로드맵 07-architecture-improvements.md가 동일 통합을 이미 계획 중이라 방향은 일치하나, **Claude가 자체 진행하면 충돌**합니다. 권장 전략: 우선순위 높은 개별 패치(role 라우팅·_exact_profile_sidecar·.profile.md 제외)만 먼저 인라인 적용하고, 통합 리팩터는 Codex 구현을 출발점으로 채택할지 별도 결정. assets.py의 catalog_for_prompt 위임은 cosmetic이라 통합 채택 시에만 의미.

**(2) assets → asset_lock + image_versions 분리**: 두 신규 모듈은 generation·prompt_contract·imagegen_jobs·seedance_live·image_visual_review를 가로지릅니다. **부분 포팅(필드만 추가) 시 호출부 인자 불일치로 깨집니다.** 권장: asset_lock과 image_versions는 각각 순수모듈(Path/pathlib만 의존)이므로 모듈을 먼저 이식하고, 통합부는 시각 QA 게이트 포팅과 묶어 단일 작업으로. image_versions의 max기반 버전·path가드만 선별 이식 가능(record_image_output 자동증분 동작변경은 제외 권장).

**(3) image_qa.py / evaluation_rounds.py / video_qa.py 혼합 커밋**: 견고화 픽스와 아키텍처 변경(임계값·transcript 기본값·imagegen 모드)이 한 모듈에 섞임. **모듈 통째 복사 절대 금지**, 픽스만 라인 단위로.

**(4) ralph_prompt.py 모듈 신설 vs 인라인 격상**: Claude "Surgical/Simplicity" 원칙상 두 인라인 함수 본문만 강화 텍스트로 교체하는 게 최소 변경이나, QUALITY_PRESSURE를 image_qa·prompt_contract 양쪽이 공유하므로 DRY 위해선 모듈 신설이 일관적. 둘 중 하나 선택. image_qa는 호출부 약 5개소이므로 시그니처 유지한 채 내부만 위임.

---

## 5. 가져오지 말 것 / 보류 (Claude 동등·우위 또는 Codex 특유 구조)

| 항목 | 이유 |
|---|---|
| `codex_builtin_imagegen` execution_mode + 지시문 | Claude는 codex_image.sh(기본)+gemini_image.sh(fallback) 단일 경로 못박음 — 정면 충돌 |
| imagegen 도구 문자열(explicit_openai_api_or_cli) | AGENTS.md "다른 API/CLI 이미지 경로 구현 금지" 위반 |
| omo_ralph OMO/$omo:ulw-loop 리네임, build_image_visual_review 훅 배선 | Claude는 /ralph-loop·claude_ralph_loop·codex_image.sh가 정합 — 리네임이 구조 파괴 |
| `.codex-plugin/plugin.json`, top-level agents/AGENT.md·skills, argv 훅 | Claude .claude 하네스(stdin-JSON, settings.json 배선)와 상호 배타. Claude test_plugin_structure가 오히려 더 촘촘 |
| 8개 훅 통째 포팅 | **훅 영역은 Claude가 우위** — 정식 프로토콜(hookSpecificOutput/permissionDecision/stop_hook_active) + settings.json 매처 등록. Codex는 argv print 구버전. 탐지 로직 조각만 체리픽 |
| tools.py `~/.codex/skills` 경로 + opencv-mcp 프리플라이트 | Claude는 ~/.claude/skills가 정답 — 스킬 탐지 깨짐 |
| transcript_enabled True→False | Claude의 fail-closed가 "메타데이터만으로 통과 금지"와 정합 — 의도적 보수값 유지 |
| evidence-feedback 완료주장 차단 훅 | Claude PostToolUse는 tool_input/response만 받아 산문 주장 스캔 불가 — 프로토콜상 재현 불가 |
| templates/imagegen-prompting/reference-sources 경로 치환 | Claude 경로로 이미 적응 — 포팅 시 역적응 회귀 |
| roadmap 체크박스 [x] 표시 | 코드 미보유 상태에서 완료 표기는 거짓 상태 — 포팅 완료분만 사후 체크 |

**보류(코드 타이밍 종속)**: opencv-mcp 문서·README 개념 섹션·reference_media_pack 영상 가드레일·asset-lock 전체 시스템 — 각각 선행 코드(시각 QA 층·asset_lock 체인) 포팅 후에만 의미.

---

## 6. 권장 다음 단계 액션

1. **견고화 번들 + external_tools.py를 첫 PR로 묶어 이식**(High×2). `tests/test_review_regressions.py`를 먼저 Claude 트리에 올려 13/14 실패를 확인 → 픽스만 라인 단위로 적용 → 14/14 green. 아키텍처 혼입(임계값·transcript·imagegen 모드)은 명시적 제외. 회귀 위험 낮고 가치 즉시.

2. **시각 QA 게이트를 두 번째 작업으로 분리 포팅**: `image_manual_review.py`(독립) + `image_qa.py` 통합 + `image_evaluation_flow` 3줄 픽스 + `ralph_prompt.py` 강화를 한 묶음으로, asset_lock·image_versions 의존을 인라인 대체해 최소 의존으로. 동시에 evaluation-rubrics.md를 "or equivalent isolated visual QA artifact" 완화 문구로 갱신해 운영 블로킹 회피.

3. **문서 doctrine + approve_reference role을 세 번째로**: CONTEXT.md 신설(@import 배선, 모듈명 Claude화) + AGENTS.md 품질 규칙 선별 추가 + approve_reference role 라우팅(03-issues.md H급 버그 해소). asset_lock 전체 시스템·reference_catalog 통합·영상 최종 조립은 위 3개 안정화 후 별도 대형 작업으로 스케줄링.
