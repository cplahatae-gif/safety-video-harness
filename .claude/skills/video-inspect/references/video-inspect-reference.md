# Video Inspect Reference

Source links:
- FFmpeg documentation: https://ffmpeg.org/documentation.html
- ffprobe documentation: https://ffmpeg.org/ffprobe.html
- OpenAI Video generation: https://developers.openai.com/api/docs/guides/video-generation
- Central source list: `docs/reference-sources.md`

Checked: 2026-06-12

## Local Reference Notes

- FFmpeg documentation is the official command reference for media processing; ffprobe is the inspection tool used for metadata such as duration, streams, frame rate, resolution, and codec.
- OpenAI video generation guidance treats generated video as an artifact that can be downloaded, inspected, extended, or edited. This harness must inspect the artifact before any QA decision.
- Metadata alone cannot prove educational quality. The skill must extract representative frames and provide them to video QA.
- OCR is required when subtitles, overlays, title cards, or warning signs are expected.
- Audio transcript handling is intentionally excluded from the active workflow because narration/TTS is a deferred feature.
- Inspect every generated clip before storyboard alignment QA. Required evidence includes ffprobe metadata, frame sample list, contact sheet or frame paths, and any OCR text found.
- Sample at least first, middle, and last frame for short clips. For longer clips or suspicious motion, add scene-change frames.
- Verify technical basics before judging content: duration, resolution, FPS, codec, file readability, and whether unexpected audio exists.
- If a video cannot be inspected locally, treat it as blocked. Do not approve based on filename, thumbnail, or generation success status alone.
- Save inspection outputs under the project evidence/QA structure so paid generation results remain auditable.

## Use In This Harness

This skill produces video inspection evidence before video QA. Metadata alone is insufficient; sampled frames are required.

## Operational Rules

- Use ffprobe for duration, FPS, resolution, codec, and audio stream checks.
- Use ffmpeg or local video skills to extract start, middle, end, and sampled frames.
- Run OCR when overlays or title cards are expected.
- Keep transcript/Whisper out of the active no-narration workflow unless explicitly requested later.
- Write an inspection manifest that `validate_video.py` can reference.

## Output Expectations

- Video QA must receive frame evidence, not just the MP4 path.
- Inspection output must identify clip ID, timestamps, frame paths, and basic metadata.
