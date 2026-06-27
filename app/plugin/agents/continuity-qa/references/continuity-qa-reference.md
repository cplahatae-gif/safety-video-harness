# Continuity QA Reference

Source links:
- OpenAI Image generation: https://developers.openai.com/api/docs/guides/image-generation
- OpenAI Video generation: https://developers.openai.com/api/docs/guides/video-generation
- JSON Schema docs: https://json-schema.org/docs
- Central source list: `docs/reference-sources.md`

Checked: 2026-06-12

## Local Reference Notes

- OpenAI image/video generation guidance supports reference-driven generation, but it does not guarantee that every frame will preserve identity, gaze, equipment, and spatial logic. Continuity QA exists to catch these failures before video cost is spent.
- Prompt engineering guidance recommends evaluation suites for prompt behavior. This agent is the evaluation layer for visual continuity and must return structured scores plus blockers, not subjective comments only.
- JSON Schema guidance is relevant because QA output must be machine-readable enough to drive RALPH-loop decisions, blocker counting, and upstream escalation.
- Keyframe continuity should be checked as a chain: previous frame state, current frame action, next frame setup. A single good-looking image can still fail if it breaks the chain.
- Safety education clarity is part of continuity. A scene fails if the viewer cannot tell what hazard is being controlled or why a worker is looking/standing/moving in that way.
- Image generation limitations explicitly include possible consistency and composition failures. QA must assume these failures are normal enough to check systematically.
- Use adjacent-pair review, not only per-image review. `sc02` is judged against `sc01` and `sc03` because video generation will use the images as chained motion anchors.
- Each blocker should include scope: story issue, style issue, prompt issue, image artifact, or video-readiness issue.
- A pass requires no critical blocker. High average score cannot compensate for a missing worker, unexplained gaze, changed vehicle, or invisible prevention action.
- Store repeated blockers in evaluation history so future prompt rounds can inject them as negative constraints.

## Use In This Harness

Continuity QA checks whether storyboard, prompt, image, and video outputs still describe the same safety story.
The OpenAI image guide notes that recurring visual consistency and precise composition can still fail, so this agent
must treat identity and layout drift as real blockers.

## Operational Rules

- Score the current image QA axes: story match, identity, PPE, equipment, story flow, technical readiness, floor/lane, background, character identity lock, vehicle geometry lock, and hazard-zone consistency.
- Block when people appear, disappear, duplicate, or change role without story motivation.
- Block when a gaze target is not visible in the frame.
- Block when the hazard zone, pedestrian route, or vehicle lane jumps spatially between scenes.
- Require `qa/image_manual_reviews.json` or equivalent isolated visual QA before production image approval.
- Require structured blocker output that can be written into JSON QA reports.

## Output Expectations

- Scores use a 0-5 rubric.
- Image pass threshold is 44/55, every axis 4 or higher, no critical blockers, and manual/isolated visual QA present.
- Regeneration deltas must name exactly what changed and what must remain fixed.
