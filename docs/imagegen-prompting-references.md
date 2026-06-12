# Imagegen Prompting References

This harness uses `scripts/codex_image.sh` (Codex CLI `codex exec` image generation) as the default image generation path. `scripts/gemini_image.sh` (Gemini Nano Banana) is the explicit-request fallback.
It does not call the OpenAI Image API or CLI fallback unless explicitly requested.

## Local Image Generation Path

- `scripts/codex_image.sh <output.png> "<prompt>" [reference images...]`
- Required behavior:
  - Use built-in `image_gen` by default.
  - Save outputs directly into the project tree (`projects/<slug>/images/draft/...`).
  - Use one built-in call per distinct asset or keyframe.
  - Preserve outputs non-destructively with versioned names.

## OpenAI Official Docs

- `https://developers.openai.com/api/docs/guides/image-generation`
- Relevant guidance applied here:
  - Image generation can be done from text prompts and can also use image references in supported workflows.
  - Multi-turn image generation can refine outputs across turns.
  - Image models can struggle with precise text rendering, visual consistency across repeated subjects, and exact composition control.
  - Cost and latency depend on model, quality, size, and input images.

## Harness Prompting Rules

- Prefer no generated text inside keyframes; use subtitles or overlays later.
- Include previous-scene continuity, current story beat, and next-scene setup in every keyframe prompt.
- Keep recurring people, PPE, vehicles, lane markings, and site layout locked.
- Make every keyframe part of one causal story flow, not a disconnected checklist panel.
- Use score-based QA before approving images for video.
