# Video Quality Regression Review

Date: 2026-06-11

## User-Reported Issues

- Images/video do not connect cleanly.
- A person appears or disappears without a clear story reason.
- Character gaze is awkward and not motivated by the active safety cue.
- The generated result does not immediately communicate what safety education topic is being taught.

## Confirmed From Sampled Frames

Reviewed:

- `projects/remicon-collision-guide/video/frames/video_contact_sheet.png`
- `projects/remicon-collision-guide/video/clips/sc01_sc02_seedance.mp4`
- `projects/remicon-collision-guide/video/clips/sc02_sc03_seedance.mp4`

Confirmed blockers:

- The first clip can read as a worker drifting into or across the hazard zone rather than a clearly controlled prevention action.
- Person placement changes without enough visual motivation.
- The signal-person intervention is not visually dominant enough.
- Gaze direction is not clearly tied to the hazard, driver, signal cue, or safe route.
- Without narration, the safety lesson is weaker than required.

## Harness Defect Found

Previous `validate_video.py` could pass a generated clip using mostly technical metadata:

- duration
- resolution
- codec

It marked manual review as required but did not make manual visual review a hard gate.

## Fix

- Added mandatory `qa/video_manual_review.json` gate.
- Added blocker fields:
  - `character_continuity_score`
  - `gaze_motivation_score`
  - `education_clarity_score`
  - `storyboard_alignment_score`
- Any score below 4 blocks the clip.
- Current generated clips now fail video QA as expected.

## Current Project Status

```text
uv run python scripts/validate_video.py --project projects/remicon-collision-guide --expected-clips 2
video QA blockers: ...
```

This is now the correct status. The existing Seedance outputs are technical test artifacts, not approved final video.

## Verification

```text
uv run pytest -q
30 passed in 6.87s
```
