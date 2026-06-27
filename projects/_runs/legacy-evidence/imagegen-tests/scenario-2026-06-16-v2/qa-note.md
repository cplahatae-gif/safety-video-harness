# QA Note: Scenario V2

Date: 2026-06-16

Artifacts:
- `continuity-bible.md`
- `storyboard-sheet.png`
- `images/sc01-hazard-context.png`
- `images/sc02-stop-confirm.png`
- `images/sc03-verify-route.png`
- `images/sc04-controlled-movement.png`

Generation method:
- One 2x2 storyboard sheet generated in a single imagegen call.
- The sheet was cropped into four separate keyframe images.
- This reduced cross-image drift compared with independent per-scene generation.

## Continuity Review

Passes:
- Large roadside convex mirror issue is resolved. No large convex mirror appears in the panels.
- Vehicle lane remains gray concrete across panels.
- Pedestrian lane remains green on the right side across panels.
- Red/orange hazard arc remains visible and mostly stable across panels.
- Ground worker appears only in the later panels, matching the intended story.
- The four panels read as one causal flow: approach -> stop -> route verification -> guided movement.

Production blockers:
- Character identity is not actually locked. The signal worker's face, body proportions, pose language, and vest details drift between panels.
- Driver identity is not locked. The driver face and cab pose differ subtly between panels.
- Background is not actually fixed. Plant geometry, building edges, conveyor placement, and the right-side wall/pedestrian-lane context drift between panels.
- BCT geometry changes subtly across panels, including cab proportions, tanker length, ladder/rail details, and wheel spacing.
- Dump truck placement and shape are only approximate, not production-consistent.
- The red/orange hazard arc remains present but changes shape, size, and position enough to weaken spatial continuity.
- sc03 and sc04 are still too visually similar; the BCT does not advance enough to strongly communicate "controlled safe movement."
- Because the four panels are cropped from one generated sheet, each individual image is lower resolution than a full single-frame generation.
- The style remains semi-realistic webtoon illustration; it is cleaner than v1 but still not a fully flat Naver-webtoon-like cel style.
- Some hand/baton details are acceptable for draft review but not perfect.

Scores:
- Story match: 4/5
- Identity continuity: 2/5
- PPE/equipment accuracy: 3/5
- Gaze and pose motivation: 4/5
- Style match: 3/5
- Video readiness: 2/5

Decision:
- This is only a better prompt experiment than v1, not an acceptable production keyframe set.
- It is not suitable for Seedance start/end keyframes.
- Text-only imagegen, even with a 2x2 sheet, does not guarantee production-grade identity/background continuity.
- The next production approach should switch from independent generation to deterministic asset composition or reference/edit-based keyframe derivation.

Next workflow change:
- Do not keep regenerating four independent text-prompted panels.
- First create locked production assets:
  - one fixed background plate
  - one fixed BCT asset or reference
  - one fixed dump truck asset or reference
  - one fixed signal-worker character sheet
  - one fixed driver/ground-worker character sheet
- Then build frames by either:
  1. deterministic compositing with Pillow/ImageMagick, or
  2. edit/reference-based generation from the previous approved frame, not pure text generation.
- Only after this lock layer exists should individual frames enter image QA/RALPH.
