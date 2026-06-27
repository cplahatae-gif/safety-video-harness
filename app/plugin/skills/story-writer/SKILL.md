---
name: story-writer
description: Create storyboard-first Korean safety training video scenarios from cited education material without narration or TTS, using subtitles and overlays for teaching points.
---

# story-writer

Create safety-training storyboards from a selected topic and cited source facts.

The story must prioritize hazard recognition, near-miss prevention, correct action,
and a short closing rule. Do not write narration or voiceover. Use short Korean
subtitle or overlay text for the required teaching point.

Before drafting, confirm the project intake is complete: source files, selected topic,
target seconds, image density, reference assets, selected style guide, aspect ratio,
text delivery, and approval scope. If any field is missing, stop and ask for it.

## References

- Reference index: `docs/generative-media-reference-index.md`
- OpenAI Prompt engineering guide: https://developers.openai.com/api/docs/guides/prompt-engineering
- OpenAI Video generation guide: https://developers.openai.com/api/docs/guides/video-generation
- Local source facts: `safety_video_harness/source_facts.py`
- Local storyboard planner: `safety_video_harness/storyboard.py`
- Local storyboard QA: `safety_video_harness/storyboard_qa.py`
- Local skill reference: `references/story-writer-reference.md`
- Evaluation rubric: `docs/evaluation-rubrics.md`
- Few-shot storyboard examples: `docs/few-shot-examples.md`
