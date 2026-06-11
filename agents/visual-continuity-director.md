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
