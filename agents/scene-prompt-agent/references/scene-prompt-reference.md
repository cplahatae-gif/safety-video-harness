# Scene Prompt Agent Reference

Source links:
- OpenAI Prompt engineering: https://developers.openai.com/api/docs/guides/prompt-engineering
- OpenAI Image generation: https://developers.openai.com/api/docs/guides/image-generation
- OpenAI Video generation: https://developers.openai.com/api/docs/guides/video-generation
- Central source list: `docs/reference-sources.md`

Checked: 2026-06-12

## Local Reference Notes

- OpenAI prompt engineering guidance says production prompts should be managed in code or files with typed inputs, tests, and evaluation checks. In this harness, scene prompt briefs must be deterministic artifacts that can be reviewed, diffed, and regenerated.
- Prompt sections should have explicit boundaries. Use clear fields for source fact, previous scene state, current action, visible cast, camera, hazard, and next-scene setup instead of one long prose paragraph.
- Image generation prompts should specify what must be visible, what must stay consistent, and what must be avoided. This is especially important because separate keyframe generations can drift in character identity, PPE, equipment, and spatial layout.
- Video generation guidance emphasizes continuity across reference images and generated clips. Scene prompts must therefore prepare start/end-frame logic before video prompting happens.
- Generated images should not be asked to render exact Korean text. Use icon-like signs or reserve exact wording for subtitle/title-card overlays.
- Every prompt must include a visible motivation for gaze and pose. If a worker looks left, the hazard, truck, signal person, mirror, route, or sign must be visible on the left.
- Separate stable global style from scene-specific action. Repeating the style bible is good; changing the illustration language per scene is not.
- Include "must preserve" details from the previous scene and "must set up" details for the next scene so the sliding-chain video stage has coherent anchors.
- Use concrete camera descriptions: wide establishing shot, medium training shot, driver-cab POV, over-shoulder mirror check, or static side view. Avoid vague cinematic language without spatial purpose.
- The prompt should describe the educational objective as visual action, not hidden intent. The viewer should infer the SOP rule from what is shown.

## Use In This Harness

Scene prompt agents draft detailed keyframe prompts from storyboard scenes. They do not call imagegen directly.
They write prompt briefs that the visual director can merge into one consistent set.

## Operational Rules

- Always include previous continuity, current action, and next setup.
- Every visible person needs a visible reason to be in the frame.
- Every gaze target must be on screen: hazard, signal person, driver, mirror, camera, route, or sign cue.
- Ask for icon-like signs rather than exact Korean/English text inside generated frames.
- Preserve the lead style bible and do not invent a new art direction per scene.

## Output Expectations

- `scene_role`, `current_action`, `visible_cast`, `gaze_targets`, `hazard_logic`, `composition`.
- `must_preserve` and `must_avoid` must be explicit enough for QA to score.
