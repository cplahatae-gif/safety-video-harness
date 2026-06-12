# Story Writer Reference

Source links:
- OpenAI Prompt engineering: https://developers.openai.com/api/docs/guides/prompt-engineering
- OpenAI Video generation: https://developers.openai.com/api/docs/guides/video-generation
- Central source list: `docs/reference-sources.md`

Checked: 2026-06-12

## Local Reference Notes

- OpenAI prompt engineering guidance recommends clear instructions, structured context, examples, and evaluation. Story writing should return a storyboard object with fields that image and video agents can test.
- Video generation guidance makes clear that video prompts benefit from concrete visual and motion instructions. Story scenes must therefore specify visible action, safety objective, camera idea, and subtitle/overlay intent.
- The harness excludes narration/TTS, so the story must communicate through visual sequence and on-screen text handled outside generated keyframes.
- Prompt changes should be versionable and testable. Story outputs need stable scene IDs and source citations so RALPH-loop revisions can compare rounds.
- Scene density must be tied to the user’s selected duration and image quantity mode: normal, many, or more.
- Use the selected image density to decide granularity before writing scenes. More images means smaller visual transitions, not extra unrelated content.
- Each scene must answer: what risk is visible, who is responsible, what safe behavior is shown, what the viewer should learn, and what image/video prompt should preserve.
- Do not write broad safety slogans as scenes. Convert them into observable workplace actions.
- If the PPT contains several topics, create candidate topics first and ask which topic to use unless the user explicitly authorizes default selection.
- Storyboard text should reserve exact Korean wording for subtitles/title cards. Generated keyframes should only contain icon-like signage or blank safety panels.

## Use In This Harness

This skill turns a selected topic into a visual storyboard for a short safety video. It should optimize for keyframe
and video generation, not for written narration.

## Operational Rules

- Use a causal safety sequence: establish hazard, show exposure, intervene, verify, correct, reinforce, end safe.
- Every scene must be imageable as a keyframe.
- Keep Korean teaching copy short and suitable for subtitles or overlays.
- Do not create narration, voiceover, or TTS fields.
- Preserve source citations in every scene.

## Output Expectations

- Scene prompts must include "no text" constraints for generated keyframes.
- Scene granularity must match the selected image density.
