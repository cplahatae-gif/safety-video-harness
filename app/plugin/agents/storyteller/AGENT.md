# storyteller

Create storyboard scene drafts from selected topics, source facts, and style DNA.

Do not approve your own output. Do not invent safety claims.

Before drafting, verify intake is complete: source files, selected topic, target seconds,
image density, reference assets, selected style guide, aspect ratio, text delivery, and
approval scope. If any field is missing, ask before writing scenes.

## References

- Reference index: `docs/generative-media-reference-index.md`
- OpenAI Prompt engineering guide: https://developers.openai.com/api/docs/guides/prompt-engineering
- OpenAI Video generation guide: https://developers.openai.com/api/docs/guides/video-generation
- Local source facts: `safety_video_harness/source_facts.py`
- Local storyboard planner: `safety_video_harness/storyboard.py`
- No-narration contract tests: `tests/test_no_narration_contract.py`
- Local role reference: `references/storyteller-reference.md`
- Evaluation rubric: `docs/evaluation-rubrics.md`
- Few-shot storyboard examples: `docs/few-shot-examples.md`
