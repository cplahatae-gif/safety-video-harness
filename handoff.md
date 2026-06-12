# Safety Video Harness Handoff

Last updated: 2026-06-12

## Purpose

This repository is an independent Codex plugin-style harness for creating short Korean safety training videos from education materials such as PPTX/SOP files.

The intended flow is:

1. ingest source material
2. extract candidate safety topics
3. interview the user for topic, duration, image density, references, style, aspect ratio, and approval scope
4. create a storyboard before any image/video work
5. generate image keyframes with Codex built-in `imagegen`
6. evaluate images through score-based QA and RALPH early-stopping loops
7. create Seedance/Higgsfield video prompts from approved start/end keyframes
8. run paid video generation only after explicit Gate 2 approval
9. inspect generated videos through sampled frames and QA reports

No narration/TTS is part of the current scope. Teaching points are delivered with visual action, subtitles, overlays, or title cards.

## Current Branch And Commit

- Branch: `codex/session-anchor-mas-evaluation`
- Remote: `https://github.com/cplahatae-gif/safety-video-harness.git`
- Latest pushed commit before this handoff was created: `1fd0281d49cbabf06b31cd8accfecad310b2f9da`
- Commit title: `Harden safety video harness guidance`

## Must-Read Files Before Work

For any new Codex session, explicitly follow this instruction:

```text
Read `handoff.md` first, then read `AGENTS.md`, `docs/evaluation-rubrics.md`, and `docs/few-shot-examples.md` before continuing.
Paid calls, live imagegen, live Seedance, and live TTS are forbidden before explicit approval.
```

Read these first in any new session:

- `AGENTS.md`
- `README.md`
- `docs/evaluation-rubrics.md`
- `docs/few-shot-examples.md`
- `docs/higgsfield-seedance-local-reference.md`
- `docs/generative-media-reference-index.md`
- `docs/reference-sources.md`

Before using a specific agent or skill, also read:

- `agents/<agent-id>/AGENT.md`
- `agents/<agent-id>/references/*.md`
- `skills/<skill-id>/SKILL.md`
- `skills/<skill-id>/references/*.md`

## Non-Negotiable Rules

- Never run live image generation, live Seedance/Higgsfield generation, live TTS, uploads, or any paid call without explicit user approval.
- Codex built-in `imagegen` is the default image-generation path.
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
- `evidence/`: root-level execution evidence
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
  - Gives bad/good examples for storyboard scenes, scene prompts, image QA findings, video prompts, and video QA findings.
- `docs/higgsfield-seedance-local-reference.md`
  - Localizes Higgsfield CLI/Seedance command families, dry-run contract, live-call gates, cost rules, upload restrictions, and post-generation QA.
- `docs/reference-sources.md`
  - Central ledger of official URLs and local reference locations.
- `docs/generative-media-reference-index.md`
  - Maps official/local references to agents and skills.

## Current Validation State

Latest full test run before this handoff:

```bash
uv run pytest -q
```

Result:

```text
76 passed in 15.45s
```

Additional verification evidence:

- `evidence/package-local-reference-verification-2026-06-12.txt`
- `evidence/local-guide-hardening-2026-06-12.txt`
- `evidence/agent-skill-reference-map-2026-06-12.txt`
- `evidence/image-prompt-team-preflight-2026-06-12.txt`

## Typical Commands

Run tests:

```bash
uv run pytest -q
```

Inspect plugin structure tests:

```bash
uv run pytest -q tests/test_plugin_structure.py
```

Generate or update image prompt team plan in dry-run style:

```bash
uv run python scripts/plan_image_prompt_team.py --project projects/<slug>
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
- Live imagegen/Seedance/TTS remain blocked unless gates and user approval allow them.
- Handoff from OMO loop is acceptable as repeated task manager, but harness remains the evaluator/arbiter.

## Suggested Next Work

Recommended next steps:

1. Run a small dry-run using a real fixture project and confirm the new rubrics/few-shot docs are referenced in generated QA outputs.
2. Improve any script output that still produces shallow prompts or shallow QA findings.
3. Add explicit tests that QA reports include rubric axis names and blocker categories.
4. Keep the generated project-level `HANDOFF.md` aligned with `templates/project/HANDOFF.md` whenever bootstrap rules change.
5. Only after storyboard and image QA quality is stable, run one short paid Seedance test with explicit user approval.

## How To Ask The Next Session

Use a request like:

```text
이 저장소의 handoff.md를 먼저 읽고 이어서 작업해줘.
AGENTS.md와 docs/evaluation-rubrics.md, docs/few-shot-examples.md도 읽은 뒤 진행해.
유료 호출, live imagegen, live Seedance, live TTS는 승인 전 금지야.
먼저 현재 상태를 요약하고 다음 작업 계획을 제안해줘.
```
