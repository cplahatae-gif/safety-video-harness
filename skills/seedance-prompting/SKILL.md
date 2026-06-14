# seedance-prompting

Write English image and motion prompts for keyframe and Seedance planning.

Every prompt must include subject, scene purpose, PPE, equipment, spatial relationship,
camera, lighting, continuity anchors, and negative constraints. Video prompts must include
start frame role, end frame role, movement, timing, and what must remain unchanged.

Image generation is expected to use Codex built-in `imagegen` skill/tool by default.
Do not route image keyframes through OpenAI Image API or CLI fallback unless the user
explicitly requests that fallback. Generated images must be saved into the project
`images/draft/` or `images/approved/` tree, not left only under `$CODEX_HOME`.

## References

- Reference index: `docs/generative-media-reference-index.md`
- Higgsfield CLI/MCP page: https://higgsfield.ai/cli
- OpenAI Video generation guide: https://developers.openai.com/api/docs/guides/video-generation
- OpenAI Image generation guide: https://developers.openai.com/api/docs/guides/image-generation
- Local Seedance expert skill: `$CODEX_HOME/skills/seedance-expert/SKILL.md`
- Local Seedance live adapter: `safety_video_harness/seedance_live.py`
- Local skill reference: `references/seedance-prompting-reference.md`
- Evaluation rubric: `docs/evaluation-rubrics.md`
- Few-shot video prompt examples: `docs/few-shot-examples.md`
- Higgsfield/Seedance local reference: `docs/higgsfield-seedance-local-reference.md`
