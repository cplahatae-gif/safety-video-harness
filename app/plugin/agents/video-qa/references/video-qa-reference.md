# Video QA Reference

Source links:
- OpenAI Video generation: https://developers.openai.com/api/docs/guides/video-generation
- Higgsfield CLI/MCP: https://higgsfield.ai/cli
- FFmpeg documentation: https://ffmpeg.org/documentation.html
- ffprobe documentation: https://ffmpeg.org/ffprobe.html
- Central source list: `docs/reference-sources.md`

Checked: 2026-06-12

## Local Reference Notes

- OpenAI video generation guidance frames video creation as prompt/reference-driven generation with downloadable outputs and continuity concerns. Video QA must compare output clips against the approved storyboard and keyframes rather than judging the video in isolation.
- Higgsfield/Seedance output is a paid generation path in this project, so QA must produce proposals and cost-aware recommendations instead of triggering automatic regeneration.
- FFmpeg and ffprobe provide local inspection primitives: duration, resolution, frame rate, codec, audio streams, and extracted frame samples.
- Because narration/TTS is excluded, the QA pass must check whether the teaching message is visible through action, subtitle/title-card design, and readable overlays.
- Video QA should identify the cheapest upstream fix: storyboard revision, keyframe regeneration, prompt correction, or only then a new paid video attempt.
- Video generation is asynchronous and failure-prone enough that QA must record job status, clip ID, prompt version, input keyframe IDs, and inspection frame paths.
- A clip is not acceptable just because the first and last frames look correct. It must preserve character count, PPE, gaze target, vehicle direction, and hazard-zone layout through motion.
- Check whether the clip communicates prevention rather than collision. If the clip emphasizes impact, injury, or confusing motion, propose a safer prompt rewrite.
- When sampled frames show drift, name the exact timestamp and whether the issue came from source keyframes, video prompt ambiguity, or generation artifact.
- Keep regeneration propose-only by default. The recommended fix should include expected cost exposure and why cheaper upstream changes are insufficient.

## Use In This Harness

Video QA validates generated clips after inspection manifests exist. It does not approve clips from MP4 metadata alone.
Because video generation is paid, this agent proposes fixes rather than automatically regenerating.

## Operational Rules

- Require `inspect_video.py` output before manual QA can pass.
- Score character continuity, gaze motivation, education clarity, and storyboard alignment.
- Compare sampled frames against storyboard and approved keyframes.
- Treat the absence of narration as intentional; assess subtitles/overlays and visual clarity.
- Do not trigger live Seedance regeneration automatically.

## Output Expectations

- Write blockers and proposals to video QA reports.
- Regeneration output is `propose_only` unless the user explicitly approves paid generation.
