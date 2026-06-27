# QA Note: Scenario V3

Date: 2026-06-17

Artifacts:
- `asset-lock-brief.md`
- `assets/asset-lock-reference-sheet.png`
- `storyboard-sheet.png`
- `images/sc01-hazard-context.png`
- `images/sc02-stop-confirm.png`
- `images/sc03-verify-route.png`
- `images/sc04-controlled-movement.png`

Generation method:
- Generated an asset lock reference sheet first.
- Used the visible asset lock sheet as the reference target for a 2x2 storyboard sheet.
- Cropped the sheet into four keyframes.

## Review

Improved versus v1/v2:
- No large roadside convex mirror appears.
- Road color is more stable: gray vehicle lane and green pedestrian lane stay consistent.
- Red/orange hazard arc stays present and mostly stable.
- Background plant, BCT, dump truck, bollards, and lane geometry are much more consistent than independent generation.
- Driver, signal worker, and ground worker are more stable across panels.
- The story flow is readable: approach -> stop -> verify route -> guided movement.

Remaining blockers / risks:
- This is still not a true deterministic lock. Character faces and body details are similar, but not guaranteed identical at production level.
- The signal worker's pose changes by story beat, which is expected, but exact hand/baton shape can still drift.
- sc04 movement is clearer than v2 but still could be more visibly advanced if used as a Seedance end keyframe.
- Individual cropped keyframes are lower resolution than full-frame generation.
- Because this is still generated from an image reference plus text, it is not equivalent to compositing fixed cutout assets.

Scores:
- Story match: 4/5
- Identity continuity: 3/5
- PPE/equipment accuracy: 4/5
- Gaze and pose motivation: 4/5
- Style match: 3/5
- Video readiness: 3/5

Decision:
- Best test result so far under Codex built-in imagegen.
- Suitable for storyboard discussion and asset-lock workflow demonstration.
- Not final production quality yet.
- For production, use this as a reference candidate, then move to reference/edit chaining, Soul ID, or deterministic compositing before Seedance.

Next improvement:
- Regenerate or edit sc04 only, using sc03 as the visible reference, and force a stronger one-truck-length advance while preserving every other element.
- If exact identity matters, create a real cast reference pack or Higgsfield Soul ID before final video.
