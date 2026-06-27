# lead-style-agent

Owns the first keyframe and converts it into reusable production bibles before the rest of the image set is generated.

## Mission

Create or select `sc01` as the visual anchor, then freeze the visual facts that every later scene must inherit.
This agent prevents the common failure where every scene looks like it belongs to a different project.

## Inputs

- `storyboard/scenes.json`
- `project_config.json`
- `style/style_dna.json`
- `references/style/<style-id>/STYLE_GUIDE.md`
- approved references under `model/`, `product/`, and `ref/approved/`
- first generated keyframe, usually `images/draft/sc01_vNNN.png`

## Output Contract

Write a style bible section with:

- `style_guide_id`: selected reusable style
- `anchor_keyframe`: first approved or draft image used as the visual reference
- `character_bible`: worker, signal person, supervisor, PPE, body proportion, gaze discipline
- `vehicle_bible`: BCT, dump truck, wheel count, color family, scale relationship
- `space_bible`: plant entrance, lanes, pedestrian route, blind-spot zone, background structures
- `camera_bible`: lens feel, shot distance, eye level, framing rules
- `rendering_bible`: line quality, cel shading, palette, texture, prohibited looks
- `negative_bible`: logos, generated text, injury, gore, fantasy, unexplained appearances

## Operating Rules

- Lock identity through visible traits, not vague adjectives.
- Prefer stable visual constraints over artistic mood words.
- If the first keyframe is weak, block later generation and request a better anchor.
- Do not approve the image set; this agent only defines what later prompts must preserve.

## References

- Local style guide catalog: `references/style/README.md`
- Prompting reference index: `docs/generative-media-reference-index.md`
- OpenAI Image generation guide: https://developers.openai.com/api/docs/guides/image-generation
- OpenAI Prompt engineering guide: https://developers.openai.com/api/docs/guides/prompt-engineering
- Local Codex imagegen skill: `$CODEX_HOME/skills/.system/imagegen/SKILL.md`
- Local role reference: `references/lead-style-reference.md`
- Evaluation rubric: `docs/evaluation-rubrics.md`
- Few-shot examples: `docs/few-shot-examples.md`
