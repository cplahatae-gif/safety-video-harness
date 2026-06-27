---
name: image-consistency-check
description: Review generated safety-video keyframes against storyboard, continuity, PPE, equipment, style, and source-grounded safety constraints before approval or regeneration.
---

# image-consistency-check

Review generated keyframes against the storyboard and continuity constraints.

Score story match, PPE, equipment, background, style, and safety accuracy. A blocker
requires a regeneration delta and must not proceed to video planning.
Production images cannot pass Gate 2 without `qa/image_manual_reviews.json` or
equivalent isolated visual QA covering floor/lane, background, character identity,
vehicle geometry, and hazard-zone consistency.

## Story-Flow Rule

Generated images must not be treated as isolated safety checklist panels. For a
30-second safety training video, each keyframe should preserve the same site and
characters while showing a clear cause-and-effect progression:

1. hazard context established
2. risky approach or exposure made visible
3. signal/control intervention
4. driver or worker verification action
5. correction to safe route or safe zone
6. rule reinforcement
7. controlled final state

When reviewing images, mark a blocker if a frame is visually polished but does not
connect to the previous and next storyboard beat.

## References

- Reference index: `docs/generative-media-reference-index.md`
- OpenAI Image generation guide: https://developers.openai.com/api/docs/guides/image-generation
- Local style guide catalog: `references/style/README.md`
- Current industrial webtoon style: `references/style/korean-industrial-webtoon/STYLE_GUIDE.md`
- Local image QA: `safety_video_harness/image_qa.py`
- Local visual continuity agent: `agents/visual-continuity-director/AGENT.md`
- Local skill reference: `references/image-consistency-reference.md`
- Evaluation rubric: `docs/evaluation-rubrics.md`
- Few-shot QA examples: `docs/few-shot-examples.md`
