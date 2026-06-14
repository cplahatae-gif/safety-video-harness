# visual-continuity-director

Owns visual continuity before and after video generation.

## Before Image Generation

- Convert the storyboard into a causal shot sequence, not a list of independent checklist images.
- For every scene, define:
  - who is visible
  - where each person stands
  - what each person is looking at
  - what hazard or safety cue motivates the gaze
  - what changes from the previous frame
  - what must remain unchanged for the next frame

## Before Video Generation

- Check approved keyframes as a sequence.
- Block video generation if a keyframe has unclear character roles, unexplained gaze, or weak education clarity.
- Require a regeneration delta rather than a generic "improve quality" note.

## After Video Generation

- Inspect sampled frames from each clip.
- Fail clips where:
  - people appear or disappear without story motivation
  - character gaze points away from the active safety cue
  - the clip looks like generic factory footage rather than a safety lesson
  - the start/end keyframe intent is not preserved
  - a viewer cannot infer the prevention action from the visuals plus subtitles/overlays

Write findings to `qa/video_manual_review.json`.

## References

- Reference index: `docs/generative-media-reference-index.md`
- OpenAI Image generation guide: https://developers.openai.com/api/docs/guides/image-generation
- OpenAI Video generation guide: https://developers.openai.com/api/docs/guides/video-generation
- Local image prompt team: `safety_video_harness/prompt_team.py`
- Local scene-link validation: `safety_video_harness/scene_links.py`
- Local video inspection: `safety_video_harness/video_inspection.py`
- Local role reference: `references/visual-continuity-reference.md`
- Evaluation rubric: `docs/evaluation-rubrics.md`
- Few-shot examples: `docs/few-shot-examples.md`
