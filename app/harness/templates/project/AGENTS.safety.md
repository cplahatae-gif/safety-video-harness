# Safety Project Rules

- Storyboard before image generation.
- Image generation before video generation.
- Live generation requires gate approval.
- Start with an intake interview before creating storyboard, images, or video.
- Ask about source files, topic, target seconds, image density, reference images, selected style guide, aspect ratio, text delivery, and approval scope.
- Ask which reusable style guide to use after checking whether reference images exist.
- Use Codex built-in `imagegen` skill/tool as the default image generation path.
- Do not use OpenAI Image API/CLI fallback unless the user explicitly requests it.
- Move or copy generated image outputs into this project; do not leave them only under `$CODEX_HOME/generated_images`.
- Every safety claim needs a citation.
