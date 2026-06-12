# Visual Continuity Director Reference

Source links:
- OpenAI Image generation: https://developers.openai.com/api/docs/guides/image-generation
- OpenAI Video generation: https://developers.openai.com/api/docs/guides/video-generation
- FFmpeg documentation: https://ffmpeg.org/documentation.html
- ffprobe documentation: https://ffmpeg.org/ffprobe.html
- Central source list: `docs/reference-sources.md`

Checked: 2026-06-12

## Local Reference Notes

- OpenAI image and video generation guidance both depend on strong reference assets and clear prompts. The visual continuity director checks whether the reference chain is strong enough before moving from storyboard to keyframes, and from keyframes to video.
- FFmpeg/ffprobe documentation matters after video generation because visual QA needs real sampled frames and metadata, not just an MP4 filename.
- The director should assess story continuity, image continuity, and video continuity as one pipeline. A late video failure often means an earlier storyboard or keyframe prompt was underspecified.
- Generated visual sequences need stable anchors: cast count, PPE, equipment, lane layout, hazard zone, camera direction, and scene-to-scene movement.
- Paid regeneration should be avoided by catching unresolved gaze, unclear teaching action, and spatial jumps before the video stage.
- Before Gate 1, require each storyboard scene to name who is visible, where they stand, what they look at, what safety risk exists, and what prevention action changes the state.
- Before Gate 2, require approved keyframes to have matching aspect ratio, stable scene geography, no unexplained people, no accidental text rendering, and no unsupported logo/brand detail.
- After video inspection, compare extracted frames against both the storyboard and the approved keyframes. Do not let video QA operate from the MP4 alone.
- If the same blocker appears three times, do not keep asking for image regeneration. Escalate upstream to story, style bible, prompt contract, or reference material.
- Use frame evidence as the shared truth for debate between evaluators. Opinions without frame paths or scene IDs should not decide pass/fail.

## Use In This Harness

The visual continuity director checks image and video sequences as one continuous prevention story.
It works before video generation and after video inspection.

## Operational Rules

- Before image generation, ensure every scene has cast, position, gaze, hazard cue, and change-from-previous.
- Before video generation, block if keyframes are unclear or weakly educational.
- After video generation, inspect sampled frames rather than relying on metadata.
- Treat generic factory footage, unclear gaze, and unexplained character changes as blockers.

## Output Expectations

- Findings must point to specific scene IDs or clip IDs.
- Regeneration deltas must describe the visual correction, not just "improve quality."
