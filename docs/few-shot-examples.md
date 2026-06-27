# Few-Shot Examples

Checked: 2026-06-12

Use these examples as local behavior anchors for agents and skills. They are not project outputs; they show the expected level of specificity.

## Storyboard Scene

Bad:

```json
{
  "scene_id": "sc03",
  "visual": "Workers learn about collision prevention.",
  "subtitle": "Stay safe."
}
```

Why it fails:

- no visible action
- no source-grounded hazard
- no cast, equipment, or prevention behavior
- cannot become a precise image prompt

Good:

```json
{
  "scene_id": "sc03",
  "scene_role": "safety_control",
  "source_citation": "slide 6: vehicle-pedestrian separation and signal confirmation",
  "visible_cast": ["signal worker", "BCT driver"],
  "hazard": "BCT entering a shared work route near a dump truck blind spot",
  "prevention_action": "signal worker holds a stop gesture while the driver checks the side mirror before entering",
  "visual_beat": "medium industrial training shot; signal worker in orange vest stands inside marked safe zone, BCT stopped before red hazard arc, dump truck visible ahead",
  "subtitle": "진입 전 정지 신호와 시야 확인",
  "next_setup": "driver prepares to follow the separated route after confirmation"
}
```

## Scene Prompt Brief

Bad:

```text
Draw a cinematic safety scene with workers and trucks.
```

Why it fails:

- no continuity from previous scene
- no gaze target
- no PPE/equipment lock
- no camera or hazard logic

Good:

```text
Scene sc03, safety-control beat. Preserve the same gray ready-mix plant entrance, green pedestrian lane, white BCT, yellow dump truck, and precision industrial webtoon style from sc02. Medium training shot at eye level. The signal worker in a white helmet and orange vest stands on the marked safe-zone edge, facing the BCT driver and holding a clear stop gesture. The BCT remains stopped before the red hazard arc; the dump truck is visible ahead as the blind-spot reason. The driver's gaze is directed toward the side mirror and signal worker, both visible in frame. Prepare sc04 by showing the BCT ready to move only after confirmation. No generated Korean text, no logos, no collision impact, no extra workers.
```

## Image QA Finding

Bad:

```json
{
  "score": 3,
  "comment": "The image is awkward. Improve it."
}
```

Why it fails:

- no axis score
- no blocker category
- no regeneration delta
- no artifact reference

Good:

```json
{
  "scene_id": "sc03",
  "artifact_path": "images/draft/sc03_v002.png",
  "scores": {
    "story_match_score": 4,
    "identity_consistency_score": 4,
    "ppe_score": 4,
    "equipment_score": 4,
    "story_flow_score": 4,
    "technical_score": 5,
    "floor_lane_consistency_score": 4,
    "background_consistency_score": 4,
    "character_identity_lock_score": 3,
    "vehicle_geometry_lock_score": 4,
    "hazard_zone_consistency_score": 4
  },
  "total_score": 44,
  "manual_visual_review": {
    "status": "present",
    "source_path": "qa/image_manual_reviews.json"
  },
  "critical_blockers": [
    "right-side worker face and body proportions drift from approved adjacent frames"
  ],
  "regeneration_delta": "Keep the same BCT, yellow dump truck, lane colors, red hazard zone, green pedestrian route, and webtoon rendering. Restore the right-side worker body type, helmet, vest, and role from the approved adjacent frame. Do not add workers, logos, accident impact, or readable generated text."
}
```

## Video Prompt

Bad:

```text
Make this scene cinematic and dramatic.
```

Why it fails:

- no start/end frame contract
- no motion objective
- no forbidden motion
- no cost-aware control

Good:

```text
Clip sc03_to_sc04. Start from approved keyframe sc03 and end at approved keyframe sc04. Keep the same white BCT, yellow dump truck, gray plant, green pedestrian lane, red hazard arc, white helmets, orange vests, and precision industrial webtoon rendering. Motion objective: the BCT remains stopped for one beat while the signal worker gives a stop gesture; the driver visibly checks the mirror; then the BCT begins a slow controlled movement only after the signal changes. Camera: stable medium training shot with slight slow pan following the BCT nose. Forbidden motion: no collision, no impact, no injury, no extra people, no changed PPE, no unreadable generated text, no sudden camera spin.
```

## Video QA Finding

Good:

```json
{
  "clip_id": "sc03_to_sc04",
  "inspection_manifest": "qa/video_inspection/sc03_to_sc04_manifest.json",
  "sampled_frames": [
    "qa/video_inspection/sc03_to_sc04_0000.jpg",
    "qa/video_inspection/sc03_to_sc04_0005.jpg",
    "qa/video_inspection/sc03_to_sc04_0010.jpg"
  ],
  "scores": {
    "technical_validity": 5,
    "start_end_alignment": 4,
    "character_continuity": 5,
    "gaze_motion_motivation": 3,
    "education_clarity": 4,
    "storyboard_alignment": 4
  },
  "decision": "propose_revision",
  "proposal": "Do not regenerate yet. First revise the video prompt to keep the driver's gaze on the mirror for the first half of the clip and reduce camera motion."
}
```
