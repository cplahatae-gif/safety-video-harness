# video-inspect

Inspect videos by metadata and sampled frames.

Use `ffprobe` for duration, FPS, resolution, and audio tracks. Use `ffmpeg` to extract
start, middle, end, and 1fps frames. Compare frames against `scenes.json` and approved images.

Preferred local inspection order:

1. `scenelens --no-whisper --ocr-lang kor+eng`
2. `video-frame-analysis` with `OCR_LANG=kor+eng`
3. `understand-video` only for frames/OCR; transcript output is outside the current no-narration workflow.

Video QA must have an inspection manifest before manual scores can pass.

## References

- Reference index: `docs/generative-media-reference-index.md`
- FFmpeg documentation: https://ffmpeg.org/documentation.html
- ffprobe documentation: https://ffmpeg.org/ffprobe.html
- OpenAI Video generation guide: https://developers.openai.com/api/docs/guides/video-generation
- Local video inspection: `safety_video_harness/video_inspection.py`
- Local video QA: `safety_video_harness/video_qa.py`
- Local video-frame-analysis skill: `$CODEX_HOME/skills/video-frame-analysis/SKILL.md`
- Local understand-video skill: `$CODEX_HOME/skills/understand-video/SKILL.md`
- Local skill reference: `references/video-inspect-reference.md`
- Evaluation rubric: `docs/evaluation-rubrics.md`
- Few-shot video QA examples: `docs/few-shot-examples.md`
- Higgsfield/Seedance local reference: `docs/higgsfield-seedance-local-reference.md`
