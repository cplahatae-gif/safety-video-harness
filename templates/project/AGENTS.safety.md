# Safety Project Rules

- Storyboard before image generation.
- Image generation before video generation.
- Live generation requires gate approval.
- Start with an intake interview before creating storyboard, images, or video.
- Ask about source files, topic, target seconds, image density, reference images, selected style guide, aspect ratio, text delivery, and approval scope.
- Ask which reusable style guide to use after checking whether reference images exist.
- Use `scripts/codex_image.sh` (Codex CLI) as the default image generation path.
- Do not use the Gemini fallback (`scripts/gemini_image.sh`) unless the user explicitly requests it.
- Save generated image outputs into this project tree; do not leave them outside the project.
- Every safety claim needs a citation.
