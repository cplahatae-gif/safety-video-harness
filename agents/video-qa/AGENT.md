# video-qa

Review generated clips from metadata and sampled frames.

Return triad alignment results for storyboard, approved image, and video frame evidence.

## Mandatory Visual QA Gate

Do not approve a generated video only because the MP4 exists, has the right duration,
or matches 1280x720. Technical metadata is only the first check.

For each clip, inspect sampled frames and score:

- character_continuity_score: people must not appear, disappear, duplicate, or change role without storyboard motivation.
- gaze_motivation_score: each visible worker/signal person/driver should look toward the active hazard, signal cue, vehicle route, or another motivated target.
- education_clarity_score: the safety lesson must be understandable from the frame sequence plus subtitles/overlays, without voiceover.
- storyboard_alignment_score: the clip must follow the storyboard beat and start/end keyframe intent.

Any score below 4 is a blocker. A clip also needs a local inspection manifest
from `scripts/inspect_video.py`; manual scores alone cannot pass QA. Record
blockers, inspection manifest paths, and regeneration deltas in
`qa/video_manual_review.json`, then run:

```bash
python3 scripts/validate_video.py --project <project> --expected-clips <n>
```

The video cannot move to final assembly until this validation passes.

## References

- Reference index: `docs/generative-media-reference-index.md`
- FFmpeg documentation: https://ffmpeg.org/documentation.html
- ffprobe documentation: https://ffmpeg.org/ffprobe.html
- OpenAI Video generation guide: https://developers.openai.com/api/docs/guides/video-generation
- Higgsfield CLI/MCP page: https://higgsfield.ai/cli
- Local video inspection: `safety_video_harness/video_inspection.py`
- Local video QA: `safety_video_harness/video_qa.py`
- Local role reference: `references/video-qa-reference.md`
- Evaluation rubric: `docs/evaluation-rubrics.md`
- Few-shot video QA examples: `docs/few-shot-examples.md`
- Higgsfield/Seedance local reference: `docs/higgsfield-seedance-local-reference.md`
