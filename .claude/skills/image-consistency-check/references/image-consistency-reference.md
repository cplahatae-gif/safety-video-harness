# Image Consistency Check Reference

Source links:
- OpenAI Image generation: https://developers.openai.com/api/docs/guides/image-generation
- Central source list: `docs/reference-sources.md`

Checked: 2026-06-12

## Local Reference Notes

- OpenAI image generation guidance supports reference-informed image creation, but repeated scene generation can still drift. This skill treats drift as measurable QA failure, not as normal variation to ignore.
- Prompt engineering guidance recommends evaluations before prompt changes. Image QA is the evaluation layer that decides whether to accept, regenerate, or escalate upstream.
- A keyframe must satisfy both composition and story requirements. A visually polished frame is not acceptable if it omits the hazard, changes PPE, invents extra people, or breaks the start/end chain.
- Exact generated text is unreliable for this use case, so image QA should block frames that rely on AI-rendered Korean/English text instead of external overlays.
- Regeneration deltas should be precise enough to paste into the next prompt: what to preserve, what to remove, and what to make visible.
- Use a two-layer judgement: first check objective constraints from the storyboard and style bible, then check subjective educational clarity.
- Objective blockers include wrong number of workers, missing helmet or vest, changed vehicle type, missing BCT, impossible lane geometry, off-screen gaze target, and invented accident impact.
- Educational blockers include unclear hazard, unclear safe behavior, confusing camera angle, and image that looks like generic plant footage rather than the selected SOP topic.
- QA must preserve approved good traits. A regeneration delta should say both "keep" and "change" so the next round does not discard successful style or composition.
- Store round scores and blocker text in the llm-wiki/evaluation history so future prompts can reuse prior failures as negative constraints.

## Use In This Harness

This skill reviews generated keyframes against storyboard, style bible, continuity bible, and source-grounded safety logic.
It exists because recurring character and composition consistency can fail across separate image generations.

## Operational Rules

- Score story match, style match, character/PPE continuity, equipment continuity, site continuity, and technical readiness.
- Block if a polished image does not connect to the previous and next storyboard beat.
- Block if a person looks off-screen without a visible safety reason.
- Block if the image contains generated Korean/English text, logos, injury, or collision impact.
- Write a regeneration delta that can be injected into the next image prompt.

## Output Expectations

- Results feed `qa/image_qa_loop.json`.
- Same blocker repeated 3 times should escalate upstream instead of repeating image regeneration.
