# Asset Lock Brief: Scenario V3

Date: 2026-06-17

Goal:
- Re-test image generation after changing the harness algorithm to asset-lock-first.
- Do not use Seedance, Higgsfield live generation, TTS, or paid calls.

Method:
1. Generate a fixed asset lock reference sheet.
2. Use that sheet as the visual reference for the storyboard keyframes.
3. Generate the storyboard as one 2x2 sheet to reduce cross-frame drift.
4. Crop the sheet into four keyframes.
5. QA the result against identity, equipment, site, road color, hazard-zone, and story-flow continuity.

Production caveat:
- Codex built-in imagegen cannot guarantee perfect character/background locking from text alone.
- This test checks whether the new asset-lock prompt discipline improves the output.
- True production should still use explicit reference/edit conditioning, Soul ID, or deterministic compositing.

Fixed assets:
- Signal worker: adult Korean male, white hard hat, orange reflective vest, navy workwear, white gloves, black boots, red signal baton.
- BCT driver: adult Korean male, white hard hat, navy workwear, visible in cab.
- Ground worker: adult Korean male, white hard hat, orange reflective vest, navy workwear; appears only in scenes 3 and 4.
- BCT: white cement tanker, consistent cab shape, tanker length, wheel count, side rails.
- Dump truck: yellow dump truck parked ahead, same position and shape.
- Site: ready-mix plant entrance, gray vehicle lane, green pedestrian lane on right, red/orange hazard arc, black-yellow bollards.
- Mirror policy: no large roadside convex mirror.
- Text policy: no readable Korean/English text inside generated images.

Storyboard:
- sc01: hazard context, BCT approaches before hazard arc.
- sc02: BCT stopped before hazard arc, signal worker gives stop signal.
- sc03: BCT remains stopped, signal worker points to safe route, ground worker behind safety line.
- sc04: BCT visibly advances after confirmation, signal worker guides calmly, ground worker remains safe.
