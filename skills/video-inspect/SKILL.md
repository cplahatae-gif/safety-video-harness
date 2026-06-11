# video-inspect

Inspect videos by metadata and sampled frames.

Use `ffprobe` for duration, FPS, resolution, and audio tracks. Use `ffmpeg` to extract
start, middle, end, and 1fps frames. Compare frames against `scenes.json` and approved images.

Preferred local inspection order:

1. `scenelens --no-whisper --ocr-lang kor+eng`
2. `video-frame-analysis` with `OCR_LANG=kor+eng`
3. `understand-video` only for frames/OCR; transcript output is outside the current no-narration workflow.

Video QA must have an inspection manifest before manual scores can pass.
