---
name: seedance-prompting
description: 키프레임 이미지/Seedance 영상용 영문 프롬프트를 작성할 때 사용. 이미지 프롬프트, 영상 프롬프트, Seedance 계획 요청 시 트리거.
---

# seedance-prompting

Write English image and motion prompts for keyframe and Seedance planning.

Every prompt must include subject, scene purpose, PPE, equipment, spatial relationship,
camera, lighting, continuity anchors, and negative constraints. Video prompts must include
start frame role, end frame role, movement, timing, and what must remain unchanged.

Image generation is expected to use `scripts/codex_image.sh` (Codex CLI) by default.
Use `scripts/gemini_image.sh` (Gemini Nano Banana) only when the user explicitly
requests that fallback. Generated images must be saved into the project
`images/draft/` or `images/approved/` tree.

## References

- Reference index: `docs/generative-media-reference-index.md`
- Higgsfield CLI/MCP page: https://higgsfield.ai/cli
- OpenAI Video generation guide: https://developers.openai.com/api/docs/guides/video-generation
- OpenAI Image generation guide: https://developers.openai.com/api/docs/guides/image-generation
- Local Seedance expert skill: `~/.claude/skills/seedance-expert/SKILL.md`
- Local Seedance live adapter: `safety_video_harness/seedance_live.py`
- Local skill reference: `references/seedance-prompting-reference.md`
- Evaluation rubric: `docs/evaluation-rubrics.md`
- Few-shot video prompt examples: `docs/few-shot-examples.md`
- Higgsfield/Seedance local reference: `docs/higgsfield-seedance-local-reference.md`
