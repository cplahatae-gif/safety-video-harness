# Safety Video Harness Handoff

Last updated: 2026-06-18

## Purpose

This repository is an independent Codex plugin-style harness for creating Korean safety-training videos from education materials such as PPTX/SOP files.

The intended flow is:

1. ingest source material
2. extract candidate safety topics
3. interview the user for topic, duration, image density, references, style, aspect ratio, text delivery, and approval scope
4. create and approve a storyboard before image/video work
5. generate image keyframes with Codex built-in `imagegen`
6. evaluate images through score-based QA and RALPH early-stopping loops
7. create Seedance/Higgsfield video prompts from approved start/end keyframes
8. run paid video generation only after explicit Gate 2 approval
9. inspect generated videos through sampled frames and QA reports

No narration/TTS is part of the current scope. Teaching points are delivered with visual action, subtitles, overlays, or title cards.

## Current Git State

- Branch: `main`
- Remote: `https://github.com/cplahatae-gif/safety-video-harness.git`
- Last pushed stable commit before this handoff update: `ec8d2a7 Strengthen visual QA and RALPH prompting`
- Current pending work to commit:
  - OpenCV MCP installation/config documentation
  - OpenCV MCP as local first-pass visual QA layer
  - updated onepagers and tool checks
  - this refreshed `handoff.md`

## Must-Read Files Before Work

For any new Codex session, use this request:

```text
이 저장소의 handoff.md를 먼저 읽고 이어서 작업해줘.
AGENTS.md와 docs/evaluation-rubrics.md, docs/few-shot-examples.md도 읽은 뒤 진행해.
docs/higgsfield-seedance-local-reference.md와 docs/opencv-mcp-local-reference.md도 확인해줘.
유료 호출, live Seedance, live TTS는 승인 전 금지야.
Codex imagegen은 사용자가 명시 승인한 경우에만 실제 생성해.
먼저 현재 상태를 요약하고 다음 작업 계획을 제안해줘.
```

Read these first in any new session:

- `AGENTS.md`
- `CONTEXT.md`
- `README.md`
- `docs/evaluation-rubrics.md`
- `docs/few-shot-examples.md`
- `docs/higgsfield-seedance-local-reference.md`
- `docs/opencv-mcp-local-reference.md`
- `docs/generative-media-reference-index.md`
- `docs/reference-sources.md`

Before using a specific agent or skill, also read:

- `agents/<agent-id>/AGENT.md`
- `agents/<agent-id>/references/*.md`
- `skills/<skill-id>/SKILL.md`
- `skills/<skill-id>/references/*.md`

## Non-Negotiable Rules

- Never run live Seedance/Higgsfield generation, live TTS, external uploads, or any paid call without explicit user approval.
- Codex built-in `imagegen` is the default image-generation path, but still requires the user's explicit instruction for actual generation.
- Do not implement or use OpenAI Image API/CLI fallback unless the user explicitly asks.
- Storyboard comes before image generation.
- Approved keyframes come before video generation.
- Video generation is cost-sensitive and propose-only after QA failure.
- Keep generated-image text out of keyframes unless explicitly approved.
- Korean teaching text should be delivered via subtitle/overlay/title-card artifacts.
- Never make safety claims without source citation.
- Never overwrite approved artifacts.
- RALPH loop is early-stopping, max 20, not fixed 20 rounds.
- Same blocker repeated 3 times escalates upstream instead of repeating regeneration.
- Append QA/evaluation evidence to project evidence and `llm-wiki/evaluation-rounds.md`.
- Use OpenCV MCP/local CV as a no-cost first-pass visual QA layer, not as a semantic final judge.

## Project Structure

Important root folders:

- `.codex-plugin/`: plugin manifest
- `agents/`: role-specific agent packages
- `skills/`: plugin skill packages
- `hooks/`: live-call veto and session-start anchor hooks
- `scripts/`: CLI entrypoints
- `safety_video_harness/`: Python harness implementation
- `schemas/`: JSON contracts
- `style-guides/`: reusable visual style guides
- `templates/project/`: project bootstrap templates
- `docs/`: onepagers, references, rubrics, examples
- `evidence/`: root-level execution evidence; large generated media is local-only and usually not committed
- `projects/`: generated project outputs, usually gitignored

Agent packages currently include:

- `agents/storyteller/`
- `agents/lead-style-agent/`
- `agents/scene-prompt-agent/`
- `agents/visual-director-arbiter/`
- `agents/continuity-qa/`
- `agents/visual-continuity-director/`
- `agents/video-qa/`

Skill packages currently include:

- `skills/topic-extractor/`
- `skills/story-writer/`
- `skills/style-ref-search/`
- `skills/image-consistency-check/`
- `skills/seedance-prompting/`
- `skills/video-inspect/`

## Key Local Guides

- `docs/evaluation-rubrics.md`
  - Defines 0-5 scoring, storyboard QA, image QA, video QA, critical blockers, and RALPH loop policy.
- `docs/few-shot-examples.md`
  - Gives specificity examples for storyboard scenes, scene prompts, image QA findings, video prompts, and video QA findings.
- `docs/higgsfield-seedance-local-reference.md`
  - Localizes Higgsfield CLI/Seedance command families, dry-run contract, live-call gates, cost rules, upload restrictions, and post-generation QA.
- `docs/opencv-mcp-local-reference.md`
  - Explains OpenCV MCP as local first-pass CV QA for floor/lane, hazard-zone, background, and layout drift.
- `docs/reference-sources.md`
  - Central ledger of official URLs and local reference locations.
- `docs/generative-media-reference-index.md`
  - Maps official/local references to agents and skills.

## Current Validation State

Latest full test run after RALPH/OpenCV updates:

```bash
uv run pytest -q
```

Result:

```text
104 passed
```

Tool check:

```bash
uv run python scripts/check_tools.py
```

Relevant output:

```text
ffmpeg: found
ffprobe: found
higgsfield: found
opencv-mcp-server: configured-via-uvx
```

## Recent Implemented Work

### RALPH Prompting

- Added structured RALPH critique blocks.
- Failed scenes now carry:
  - quality pressure
  - failed criteria
  - must-preserve list
  - must-change list
  - do-not-repeat list
- Previous blockers are injected into the next image prompt under `RALPH previous-round critique`.

Relevant files:

- `safety_video_harness/ralph_prompt.py`
- `safety_video_harness/image_qa.py`
- `safety_video_harness/prompt_contract.py`

### Image QA

Image production pass now requires:

- total `44/55` or higher
- every axis `4` or higher
- no critical blocker
- `qa/image_manual_reviews.json` or equivalent isolated visual QA evidence

Additional visual-lock axes:

- `floor_lane_consistency_score`
- `background_consistency_score`
- `character_identity_lock_score`
- `vehicle_geometry_lock_score`
- `hazard_zone_consistency_score`

Relevant files:

- `safety_video_harness/image_manual_review.py`
- `safety_video_harness/image_visual_review.py`
- `scripts/build_image_visual_review.py`

### OpenCV MCP

OpenCV MCP was installed/tested with:

```bash
uvx opencv-mcp-server
```

It is registered in `~/.codex/config.toml`:

```toml
[mcp_servers.opencv]
command = "uvx"
args = ["opencv-mcp-server"]
```

Important: restart Codex/new session to load the MCP namespace. Current session may not expose it until restart.

OpenCV MCP role in the algorithm:

- local/no-cost first-pass CV inspection
- floor/lane color drift
- hazard-zone layout drift
- background/layout drift
- contact-sheet preprocessing
- not sufficient for semantic identity/gaze/education-clarity approval

### PPTX Rendering

`slide_render` mode now tries:

1. `soffice` to convert PPTX to PDF
2. `pdftoppm` to render PNG slides
3. fallback to `media_extract` when tools are missing

Relevant file:

- `safety_video_harness/source_rendering.py`

### Production Image Policy

Final keyframes should not be treated as production-grade if generated as independent text-only frames.

Preferred order:

1. asset lock
2. reference/edit chaining
3. deterministic compositing for stable background/lane/hazard-zone
4. OpenCV/contact-sheet QA
5. RALPH regeneration only for blocked scenes

## Recent Imagegen Evidence

Latest local evidence project:

```text
evidence/imagegen-runs/ralph-imagegen-20260617-172344
```

This is intentionally local-only and not committed because generated image assets are large.

What happened:

- Generated sc01-sc06 with Codex built-in imagegen.
- Built contact sheet:
  - `qa/visual_review/image_contact_sheet.png`
- First six-frame comparison found sc04 blocker.
- sc04 failed because it used an interior driver-cab view and broke:
  - floor/lane consistency
  - background consistency
  - hazard-zone consistency
- RALPH regenerated sc04 as an exterior wide shot.
- sc04 v2 passed with `50/55`.
- sc01-sc06 approved images were copied into:
  - `images/approved/sc01.png`
  - `images/approved/sc02.png`
  - `images/approved/sc03.png`
  - `images/approved/sc04.png`
  - `images/approved/sc05.png`
  - `images/approved/sc06.png`
- Summary file:
  - `qa/six_image_consistency_review.md`

Important caveat:

- For a true 30-second six-clip sliding chain, the project still needs final end keyframe `sc07`.
- The six generated images demonstrate consistency testing and RALPH repair, not a complete video-ready chain.

## Typical Commands

Run tests:

```bash
uv run pytest -q
```

Check tools:

```bash
uv run python scripts/check_tools.py
```

Generate or update image prompt team plan:

```bash
uv run python scripts/plan_image_prompt_team.py --project projects/<slug>
```

Generate image job spec:

```bash
uv run python scripts/generate_images.py --project projects/<slug> --live --only sc01
```

Record a Codex imagegen output:

```bash
uv run python scripts/record_image_output.py --project projects/<slug> --scene-id sc01 --generated-file <generated_png>
```

Build visual review/contact sheet:

```bash
uv run python scripts/build_image_visual_review.py --project projects/<slug> --write-review --force
```

Validate generated images:

```bash
uv run python scripts/validate_images.py --project projects/<slug>
```

Validate scene links before video:

```bash
uv run python scripts/validate_scene_links.py --project projects/<slug>
```

Seedance/Higgsfield planning must begin as dry-run:

```bash
uv run python scripts/generate_seedance.py --project projects/<slug> --dry-run
```

## Reference Asset Placement

For a project, place approved references under:

- `projects/<slug>/model/cast/`
- `projects/<slug>/model/ppe/`
- `projects/<slug>/product/equipment/`
- `projects/<slug>/ref/approved/person/`
- `projects/<slug>/ref/approved/work/`
- `projects/<slug>/ref/approved/space/`
- `projects/<slug>/ref/approved/style/`
- `projects/<slug>/ref/approved/camera/`
- `projects/<slug>/ref/approved/lighting/`

Candidate references should remain inert until approved.

Reusable style guides live under:

- `style-guides/<style-id>/STYLE_GUIDE.md`
- `style-guides/<style-id>/references/`

Current notable style:

- `style-guides/korean-industrial-webtoon/STYLE_GUIDE.md`

## Known Design Decisions

- 30 seconds is a cost/quality guardrail, not a technical limit.
- Image quantity is chosen by interview:
  - normal: current baseline
  - many: 2x images
  - more: 4x images
- Video generation should use sliding chain logic:
  - `sc01 -> sc02`
  - `sc02 -> sc03`
  - and so on
- Start/end keyframes must be approved images.
- Live Seedance/TTS remain blocked unless gates and user approval allow them.
- Codex imagegen may be used when the user explicitly asks for image generation.
- OMO may act as repeated task manager, but the harness remains the evaluator/arbiter.

## Suggested Next Work

Recommended next steps:

1. Restart Codex so the new OpenCV MCP namespace loads.
2. Verify available OpenCV MCP tools in the new session.
3. Wire actual OpenCV MCP tool calls into `scripts/build_image_visual_review.py` or a sibling script.
4. Generate required final keyframe `sc07` for the six-clip sliding chain.
5. Run full sc01-sc07 image QA and sliding-chain validation.
6. Only after image QA is stable, run one short paid Seedance test with explicit approval.

## How To Ask The Next Session

Use a request like:

```text
이 저장소의 handoff.md를 먼저 읽고 이어서 작업해줘.
AGENTS.md와 docs/evaluation-rubrics.md, docs/few-shot-examples.md도 읽은 뒤 진행해.
docs/opencv-mcp-local-reference.md도 확인하고, 새 세션에서 OpenCV MCP tool namespace가 로드됐는지 확인해줘.
유료 호출, live Seedance, live TTS는 승인 전 금지야.
먼저 현재 상태를 요약하고 다음 작업 계획을 제안해줘.
```
