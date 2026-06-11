# Safety Project Rules

- Storyboard before image generation.
- Image generation before video generation.
- Live generation requires gate approval.
- Use Codex built-in `imagegen` skill/tool as the default image generation path.
- Do not use OpenAI Image API/CLI fallback unless the user explicitly requests it.
- Move or copy generated image outputs into this project; do not leave them only under `$CODEX_HOME/generated_images`.
- Every safety claim needs a citation.
