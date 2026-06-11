# seedance-prompting

Write English image and motion prompts for keyframe and Seedance planning.

Every prompt must include subject, scene purpose, PPE, equipment, spatial relationship,
camera, lighting, continuity anchors, and negative constraints. Video prompts must include
start frame role, end frame role, movement, timing, and what must remain unchanged.

Image generation is expected to use Codex built-in `imagegen` skill/tool by default.
Do not route image keyframes through OpenAI Image API or CLI fallback unless the user
explicitly requests that fallback. Generated images must be saved into the project
`images/draft/` or `images/approved/` tree, not left only under `$CODEX_HOME`.
