---
name: story-writer
description: 선택된 주제와 출처 근거로 안전교육 스토리보드를 작성할 때 사용. 스토리보드 생성, 시나리오 작성, 장면 구성 요청 시 트리거.
---

# story-writer

Create safety-training storyboards from a selected topic and cited source facts.

The story must prioritize hazard recognition, near-miss prevention, correct action,
and a short closing rule. Do not write narration or voiceover. Use short Korean
subtitle or overlay text for the required teaching point.

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
