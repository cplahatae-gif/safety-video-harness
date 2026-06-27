# Storyteller Reference

Source links:
- OpenAI Prompt engineering: https://developers.openai.com/api/docs/guides/prompt-engineering
- OpenAI Video generation: https://developers.openai.com/api/docs/guides/video-generation
- Central source list: `docs/reference-sources.md`

Checked: 2026-06-12

## Local Reference Notes

- OpenAI prompt engineering guidance recommends clear task instructions, relevant context, examples when useful, and evaluation before production changes. Story output must therefore be structured, source-grounded, and testable rather than a freeform treatment.
- Prompt-managed workflows should keep production prompts in code/files with version control. Story decisions in this harness must be written as durable storyboard fields so later image/video stages can trace what changed.
- Video generation guidance treats prompts and reference images as inputs for motion, scene continuity, and clip management. The story must be designed as keyframeable visual beats, not as narration-first copy.
- Short safety videos need cause-and-effect ordering: hazard context, exposure, prevention action, verification, correction, rule reinforcement, safe end state.
- Because narration/TTS is intentionally excluded, every teaching point must be expressible through visual action, title card, subtitle, or on-screen overlay.
- Treat source material as the authority. If the PPT or extracted material does not support a claim, do not invent it for dramatic effect.
- The story should avoid accident-impact spectacle. For safety education, the dramatic center is near-miss recognition and prevention behavior.
- Keep each beat narrow enough to become one still image and one short motion segment. If a beat needs multiple simultaneous lessons, split it before prompt drafting.
- Prefer visible safety controls: separated pedestrian route, waiting line, spotter signal, speed reduction, mirror check, stop line, cone/barrier, warning zone, and final confirmation gesture.
- Preserve scene IDs and source citations through every revision so RALPH-loop outputs can compare round-by-round changes without losing traceability.

## Use In This Harness

The storyteller turns selected safety topics and source facts into a short visual sequence. It does not write narration.
It writes visual beats that later agents can turn into keyframes and video prompts.

## Operational Rules

- Treat prompts as structured task programs: topic, source citation, hazard, prevention action, visual beat, subtitle.
- Split the story into concrete safety actions rather than broad advice.
- Every scene must trace back to source facts or approved user instructions.
- Keep Korean teaching text short enough for subtitle or overlay handling.
- Do not create unsupported safety claims, brand claims, or voiceover requirements.
- Preserve a cause-and-effect sequence: hazard context, exposure, control action, verification, correction, rule reinforcement, final safe state.

## Output Expectations

- Scene actions must be imageable in one keyframe.
- Subtitles must not depend on narration.
- The scene order must support start/end keyframe chaining.
