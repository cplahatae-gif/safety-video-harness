# Project Handoff: {{PROJECT_NAME}}

Project slug: `{{PROJECT_SLUG}}`

## Required First Reads

Read the repository-level handoff and operating rules before continuing this project:

- `handoff.md`
- `AGENTS.md`
- `docs/evaluation-rubrics.md`
- `docs/few-shot-examples.md`
- `docs/higgsfield-seedance-local-reference.md`

Paid calls, live imagegen, live Seedance, and live TTS are forbidden before explicit approval.

## Project Order

1. Confirm source files and selected topic.
2. Confirm target seconds, image density, style guide, aspect ratio, and reference assets.
3. Build or revise `storyboard/scenes.json`.
4. Run storyboard QA before image work.
5. Generate image prompts and imagegen job specs.
6. Use Codex built-in `imagegen` only after the storyboard gate allows it.
7. Run image QA and RALPH early-stopping loops.
8. Generate Seedance/Higgsfield prompt specs only from approved keyframes.
9. Run live video only after Gate 2 approval, external upload permission, and cost disclosure.

## Local Evidence To Inspect

- `sources/`
- `storyboard/scenes.json`
- `prompts/`
- `images/draft/`
- `images/approved/`
- `qa/`
- `llm-wiki/evaluation-rounds.md`

