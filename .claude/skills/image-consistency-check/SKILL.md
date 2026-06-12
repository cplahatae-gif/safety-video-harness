---
name: image-consistency-check
description: 생성된 키프레임을 스토리보드·연속성 기준으로 검수할 때 사용. 이미지 QA, 키프레임 검증, validate_images 요청 시 트리거.
---

# image-consistency-check

Review generated keyframes against the storyboard and continuity constraints.

Score story match, PPE, equipment, background, style, and safety accuracy. A blocker
requires a regeneration delta and must not proceed to video planning.

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
- Local style guide catalog: `style-guides/README.md`
- Current industrial webtoon style: `style-guides/korean-industrial-webtoon/STYLE_GUIDE.md`
- Local image QA: `safety_video_harness/image_qa.py`
- Local visual continuity agent: `.claude/agents/visual-continuity-director.md`
- Local skill reference: `references/image-consistency-reference.md`
- Evaluation rubric: `docs/evaluation-rubrics.md`
- Few-shot QA examples: `docs/few-shot-examples.md`
