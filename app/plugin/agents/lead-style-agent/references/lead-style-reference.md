# Lead Style Agent Reference

Source links:
- OpenAI Image generation: https://developers.openai.com/api/docs/guides/image-generation
- OpenAI Prompt engineering: https://developers.openai.com/api/docs/guides/prompt-engineering
- Local Codex imagegen skill: `$CODEX_HOME/skills/.system/imagegen/SKILL.md`
- Central source list: `docs/reference-sources.md`

Checked: 2026-06-12

## Local Reference Notes

- OpenAI image generation guidance supports using text and image references to guide generation, but consistency across independent generations still needs explicit constraints. The lead style agent turns the first approved frame into reusable visual constraints.
- Prompt engineering guidance favors clear, reusable prompt components. The style bible must be short, stable, and injectable into every scene prompt without drowning out scene-specific action.
- Style references should be translated into concrete visual attributes: line weight, rendering style, PPE colors, body proportions, vehicle silhouette, camera height, lens feel, lighting, and background geometry.
- Avoid asking image generation to solve exact typography or brand replication. Exact text belongs in overlay/subtitle stages, and protected logos or identifiable brand marks must be excluded unless approved.
- If the lead frame is weak, inconsistent, or too generic, downstream prompts will amplify the problem. The correct action is to regenerate or revise the anchor before producing the remaining scene set.
- The style bible must distinguish fixed identity constraints from flexible composition choices. PPE colors and worker proportions are fixed; camera distance may vary by scene.
- Reference images should be converted into descriptive text, not used as vague inspiration. Name line quality, shadows, palette, material texture, background density, and face/hand simplification level.
- For the current webtoon-like industrial style, preserve clean contour lines, controlled gray industrial backgrounds, readable orange PPE, non-gory prevention staging, and realistic worksite scale.
- Negative style constraints are as important as positive ones: no photorealistic drift, no decorative fantasy elements, no brand logos, no random extra workers, no text rendered inside the generated frame.
- The style bible should be compact enough to fit every downstream prompt, but specific enough that a different agent cannot reinterpret the look freely.

## Use In This Harness

The lead style agent uses the first keyframe as the visual anchor. It summarizes the anchor into production bibles
so later scenes inherit the same identity, vehicle, site, camera, and rendering rules.

## Operational Rules

- Convert visual observations into concrete locks, not mood words.
- Use reference images and style guides to offset known image generation consistency limits.
- Avoid exact in-image text because image generation can struggle with precise text rendering.
- Lock recurring elements: PPE colors, body proportions, BCT silhouette, dump truck color, pedestrian lane, hazard zone.
- If `sc01` is not strong enough to anchor the set, request regeneration before other scenes are made.

## Output Expectations

- `character_bible`, `vehicle_bible`, `space_bible`, `camera_bible`, `rendering_bible`, `negative_bible`.
- The bible must be short enough to inject into scene prompts without burying the scene action.
