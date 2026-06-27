# Story Flow + Seedance Live Evidence

Date: 2026-06-11

## Tool Installs

```text
Pillow 12.2.0
ImageMagick 7.1.2-25
ffmpeg 8.1.1
```

## Implemented

- Story-flow image prompting rules.
- OpenAI/Codex imagegen reference documentation file.
- Score-based image QA loop.
- Scene-link validator and hook.
- Bounded Seedance live path:
  - `--execute-paid` required
  - `--test-seconds <= 10`
  - `--max-attempts <= 3`
  - 10 seconds maps to two 5-second clips
- Video QA scoring script.

## Real Project Validation

```text
uv run python scripts/generate_images.py --project projects/remicon-collision-guide --dry-run
image dry-run prepared 6 prompt(s)

uv run python scripts/validate_scene_links.py --project projects/remicon-collision-guide
validated 6 scene link(s)

uv run python scripts/validate_images.py --project projects/remicon-collision-guide
validated 6 image plan(s)

uv run python scripts/validate_project.py projects/remicon-collision-guide
project valid
```

## Higgsfield Cost Estimate

```text
sc01: 17.5 credits
sc02: 17.5 credits
total: 35 credits
```

## Live Seedance Outputs

- `projects/remicon-collision-guide/video/clips/sc01_sc02_seedance.mp4`
- `projects/remicon-collision-guide/video/clips/sc02_sc03_seedance.mp4`
- `projects/remicon-collision-guide/video/frames/video_contact_sheet.png`

Returned URLs:

- `[redacted-url]`
- `[redacted-url]`

## Video Metadata

Both generated clips:

```text
codec: h264
resolution: 1280x720
duration: 5.061950 seconds
audio: aac
```

## Final Verification

```text
uv run pytest -q
28 passed in 6.54s

uv run python scripts/check_tools.py
python3: found
ffmpeg: found
ffprobe: found
node: found
npm: found
higgsfield: found

uv run python scripts/validate_video.py --project projects/remicon-collision-guide --expected-clips 2
validated 2 video clip(s)
```

## Manual QA Note

The two live clips are technically valid and preserve the industrial site, PPE, and vehicle continuity. The first clip still reads partly as a hazard-zone approach during transition, so final production should prefer one more prompt refinement that makes the signal-person intervention clearer before expanding to the full 30 seconds.
