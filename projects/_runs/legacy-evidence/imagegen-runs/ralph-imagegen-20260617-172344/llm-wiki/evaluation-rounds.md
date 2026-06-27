# Evaluation Rounds

## storyboard / sc01 / round 1

- decision: `approve_storyboard`
- total_score: `25`
- blocking_issues: 없음
- blocker_signatures: 없음
- bundle: `qa/evaluation_bundles/storyboard/sc01/round_001.json`

### Scores
- total_score: `25`

### Round Outputs
- start_keyframe: `images/approved/sc01.png`
- end_keyframe: `images/approved/sc02.png`
- clip_path: `video/clips/sc01_sc02.mp4`

### Improvement Notes
- Arbiter next action: continue

### Next Prompt Memory
- Apply next: Arbiter next action: continue

### Repeated Blockers
- 없음
## storyboard / sc02 / round 1

- decision: `approve_storyboard`
- total_score: `25`
- blocking_issues: 없음
- blocker_signatures: 없음
- bundle: `qa/evaluation_bundles/storyboard/sc02/round_001.json`

### Scores
- total_score: `25`

### Round Outputs
- start_keyframe: `images/approved/sc02.png`
- end_keyframe: `images/approved/sc03.png`
- clip_path: `video/clips/sc02_sc03.mp4`

### Improvement Notes
- Arbiter next action: continue

### Next Prompt Memory
- Apply next: Arbiter next action: continue

### Repeated Blockers
- 없음
## storyboard / sc03 / round 1

- decision: `approve_storyboard`
- total_score: `25`
- blocking_issues: 없음
- blocker_signatures: 없음
- bundle: `qa/evaluation_bundles/storyboard/sc03/round_001.json`

### Scores
- total_score: `25`

### Round Outputs
- start_keyframe: `images/approved/sc03.png`
- end_keyframe: `images/approved/sc04.png`
- clip_path: `video/clips/sc03_sc04.mp4`

### Improvement Notes
- Arbiter next action: continue

### Next Prompt Memory
- Apply next: Arbiter next action: continue

### Repeated Blockers
- 없음
## storyboard / sc04 / round 1

- decision: `approve_storyboard`
- total_score: `25`
- blocking_issues: 없음
- blocker_signatures: 없음
- bundle: `qa/evaluation_bundles/storyboard/sc04/round_001.json`

### Scores
- total_score: `25`

### Round Outputs
- start_keyframe: `images/approved/sc04.png`
- end_keyframe: `images/approved/sc05.png`
- clip_path: `video/clips/sc04_sc05.mp4`

### Improvement Notes
- Arbiter next action: continue

### Next Prompt Memory
- Apply next: Arbiter next action: continue

### Repeated Blockers
- 없음
## storyboard / sc05 / round 1

- decision: `approve_storyboard`
- total_score: `25`
- blocking_issues: 없음
- blocker_signatures: 없음
- bundle: `qa/evaluation_bundles/storyboard/sc05/round_001.json`

### Scores
- total_score: `25`

### Round Outputs
- start_keyframe: `images/approved/sc05.png`
- end_keyframe: `images/approved/sc06.png`
- clip_path: `video/clips/sc05_sc06.mp4`

### Improvement Notes
- Arbiter next action: continue

### Next Prompt Memory
- Apply next: Arbiter next action: continue

### Repeated Blockers
- 없음
## storyboard / sc06 / round 1

- decision: `approve_storyboard`
- total_score: `25`
- blocking_issues: 없음
- blocker_signatures: 없음
- bundle: `qa/evaluation_bundles/storyboard/sc06/round_001.json`

### Scores
- total_score: `25`

### Round Outputs
- start_keyframe: `images/approved/sc06.png`
- end_keyframe: `images/approved/sc07.png`
- clip_path: `video/clips/sc06_sc07.mp4`

### Improvement Notes
- Arbiter next action: continue

### Next Prompt Memory
- Apply next: Arbiter next action: continue

### Repeated Blockers
- 없음
## image / sc04 / round 1

- decision: `regenerate`
- total_score: `47`
- blocking_issues: floor_lane_consistency_score below minimum 4: 3; background_consistency_score below minimum 4: 3; hazard_zone_consistency_score below minimum 4: 3; adjacent scene color/layout drift too high: 159.00; floor_lane_consistency_score below minimum 4: 3; background_consistency_score below minimum 4: 3; hazard_zone_consistency_score below minimum 4: 3
- blocker_signatures: image:sc04:general:floor_lane_consistency_score_below_minimum_4_3; image:sc04:general:background_consistency_score_below_minimum_4_3; image:sc04:general:hazard_zone_consistency_score_below_minimum_4_3; image:sc04:general:adjacent_scene_color_layout_drift_too_high_159_00
- bundle: `qa/evaluation_bundles/image/sc04/round_001.json`

### Scores
- story_match_score: `5`
- identity_consistency_score: `5`
- ppe_score: `5`
- equipment_score: `5`
- story_flow_score: `5`
- technical_score: `5`
- floor_lane_consistency_score: `3`
- background_consistency_score: `3`
- character_identity_lock_score: `4`
- vehicle_geometry_lock_score: `4`
- hazard_zone_consistency_score: `3`
- total_score: `47`

### Round Outputs
- reviewed_asset: `images/draft/sc04_v001.png`
- start_keyframe: `images/approved/sc04.png`
- end_keyframe: `images/approved/sc05.png`
- clip_path: `video/clips/sc04_sc05.mp4`

### Improvement Notes
- RALPH critique for sc04:
Quality pressure: This result is not acceptable for a safety training video until the listed blockers are visibly fixed. Re-check the failed frame before generating again; do not make a cosmetic variation that repeats the same issue.
Failed criteria and required fixes:
- floor_lane_consistency_score below minimum 4: 3
- background_consistency_score below minimum 4: 3
- hazard_zone_consistency_score below minimum 4: 3
- adjacent scene color/layout drift too high: 159.00
- floor_lane_consistency_score below minimum 4: 3
- background_consistency_score below minimum 4: 3
- hazard_zone_consistency_score below minimum 4: 3
Must preserve:
- approved character identity, helmet, vest, body proportion, and role
- approved BCT/dump-truck geometry, scale, wheel count, mirrors, and relative position
- approved site layout, concrete floor, lane colors, pedestrian route, cones, bollards, and hazard zone
- current storyboard beat and previous/next scene continuity
Must change this round:
- make every listed blocker visually impossible to miss
- remove unexplained gaze, character drift, vehicle drift, floor/lane drift, or generic factory framing
Do not repeat:
- floor_lane_consistency_score below minimum 4: 3
- background_consistency_score below minimum 4: 3
- hazard_zone_consistency_score below minimum 4: 3
- adjacent scene color/layout drift too high: 159.00
- floor_lane_consistency_score below minimum 4: 3
- background_consistency_score below minimum 4: 3
- hazard_zone_consistency_score below minimum 4: 3
- Regenerate only after directly addressing these visible deficiencies: floor_lane_consistency_score below minimum 4: 3; background_consistency_score below minimum 4: 3; hazard_zone_consistency_score below minimum 4: 3; adjacent scene color/layout drift too high: 159.00. Preserve approved continuity locks.
- Arbiter next action: regenerate_blocked_scenes

### Next Prompt Memory
- Do not repeat: floor_lane_consistency_score below minimum 4: 3
- Do not repeat: background_consistency_score below minimum 4: 3
- Do not repeat: hazard_zone_consistency_score below minimum 4: 3
- Do not repeat: adjacent scene color/layout drift too high: 159.00
- Do not repeat: floor_lane_consistency_score below minimum 4: 3
- Do not repeat: background_consistency_score below minimum 4: 3
- Do not repeat: hazard_zone_consistency_score below minimum 4: 3
- Apply next: RALPH critique for sc04:
Quality pressure: This result is not acceptable for a safety training video until the listed blockers are visibly fixed. Re-check the failed frame before generating again; do not make a cosmetic variation that repeats the same issue.
Failed criteria and required fixes:
- floor_lane_consistency_score below minimum 4: 3
- background_consistency_score below minimum 4: 3
- hazard_zone_consistency_score below minimum 4: 3
- adjacent scene color/layout drift too high: 159.00
- floor_lane_consistency_score below minimum 4: 3
- background_consistency_score below minimum 4: 3
- hazard_zone_consistency_score below minimum 4: 3
Must preserve:
- approved character identity, helmet, vest, body proportion, and role
- approved BCT/dump-truck geometry, scale, wheel count, mirrors, and relative position
- approved site layout, concrete floor, lane colors, pedestrian route, cones, bollards, and hazard zone
- current storyboard beat and previous/next scene continuity
Must change this round:
- make every listed blocker visually impossible to miss
- remove unexplained gaze, character drift, vehicle drift, floor/lane drift, or generic factory framing
Do not repeat:
- floor_lane_consistency_score below minimum 4: 3
- background_consistency_score below minimum 4: 3
- hazard_zone_consistency_score below minimum 4: 3
- adjacent scene color/layout drift too high: 159.00
- floor_lane_consistency_score below minimum 4: 3
- background_consistency_score below minimum 4: 3
- hazard_zone_consistency_score below minimum 4: 3
- Apply next: Regenerate only after directly addressing these visible deficiencies: floor_lane_consistency_score below minimum 4: 3; background_consistency_score below minimum 4: 3; hazard_zone_consistency_score below minimum 4: 3; adjacent scene color/layout drift too high: 159.00. Preserve approved continuity locks.
- Apply next: Arbiter next action: regenerate_blocked_scenes

### Repeated Blockers
- 없음
## image / sc05 / round 1

- decision: `regenerate`
- total_score: `47`
- blocking_issues: floor_lane_consistency_score below minimum 4: 3; background_consistency_score below minimum 4: 3; hazard_zone_consistency_score below minimum 4: 3; adjacent scene color/layout drift too high: 161.00; floor_lane_consistency_score below minimum 4: 3; background_consistency_score below minimum 4: 3; hazard_zone_consistency_score below minimum 4: 3
- blocker_signatures: image:sc05:general:floor_lane_consistency_score_below_minimum_4_3; image:sc05:general:background_consistency_score_below_minimum_4_3; image:sc05:general:hazard_zone_consistency_score_below_minimum_4_3; image:sc05:general:adjacent_scene_color_layout_drift_too_high_161_00
- bundle: `qa/evaluation_bundles/image/sc05/round_001.json`

### Scores
- story_match_score: `5`
- identity_consistency_score: `5`
- ppe_score: `5`
- equipment_score: `5`
- story_flow_score: `5`
- technical_score: `5`
- floor_lane_consistency_score: `3`
- background_consistency_score: `3`
- character_identity_lock_score: `4`
- vehicle_geometry_lock_score: `4`
- hazard_zone_consistency_score: `3`
- total_score: `47`

### Round Outputs
- reviewed_asset: `images/draft/sc05_v001.png`
- start_keyframe: `images/approved/sc05.png`
- end_keyframe: `images/approved/sc06.png`
- clip_path: `video/clips/sc05_sc06.mp4`

### Improvement Notes
- RALPH critique for sc05:
Quality pressure: This result is not acceptable for a safety training video until the listed blockers are visibly fixed. Re-check the failed frame before generating again; do not make a cosmetic variation that repeats the same issue.
Failed criteria and required fixes:
- floor_lane_consistency_score below minimum 4: 3
- background_consistency_score below minimum 4: 3
- hazard_zone_consistency_score below minimum 4: 3
- adjacent scene color/layout drift too high: 161.00
- floor_lane_consistency_score below minimum 4: 3
- background_consistency_score below minimum 4: 3
- hazard_zone_consistency_score below minimum 4: 3
Must preserve:
- approved character identity, helmet, vest, body proportion, and role
- approved BCT/dump-truck geometry, scale, wheel count, mirrors, and relative position
- approved site layout, concrete floor, lane colors, pedestrian route, cones, bollards, and hazard zone
- current storyboard beat and previous/next scene continuity
Must change this round:
- make every listed blocker visually impossible to miss
- remove unexplained gaze, character drift, vehicle drift, floor/lane drift, or generic factory framing
Do not repeat:
- floor_lane_consistency_score below minimum 4: 3
- background_consistency_score below minimum 4: 3
- hazard_zone_consistency_score below minimum 4: 3
- adjacent scene color/layout drift too high: 161.00
- floor_lane_consistency_score below minimum 4: 3
- background_consistency_score below minimum 4: 3
- hazard_zone_consistency_score below minimum 4: 3
- Regenerate only after directly addressing these visible deficiencies: floor_lane_consistency_score below minimum 4: 3; background_consistency_score below minimum 4: 3; hazard_zone_consistency_score below minimum 4: 3; adjacent scene color/layout drift too high: 161.00. Preserve approved continuity locks.
- Arbiter next action: regenerate_blocked_scenes

### Next Prompt Memory
- Do not repeat: floor_lane_consistency_score below minimum 4: 3
- Do not repeat: background_consistency_score below minimum 4: 3
- Do not repeat: hazard_zone_consistency_score below minimum 4: 3
- Do not repeat: adjacent scene color/layout drift too high: 161.00
- Do not repeat: floor_lane_consistency_score below minimum 4: 3
- Do not repeat: background_consistency_score below minimum 4: 3
- Do not repeat: hazard_zone_consistency_score below minimum 4: 3
- Apply next: RALPH critique for sc05:
Quality pressure: This result is not acceptable for a safety training video until the listed blockers are visibly fixed. Re-check the failed frame before generating again; do not make a cosmetic variation that repeats the same issue.
Failed criteria and required fixes:
- floor_lane_consistency_score below minimum 4: 3
- background_consistency_score below minimum 4: 3
- hazard_zone_consistency_score below minimum 4: 3
- adjacent scene color/layout drift too high: 161.00
- floor_lane_consistency_score below minimum 4: 3
- background_consistency_score below minimum 4: 3
- hazard_zone_consistency_score below minimum 4: 3
Must preserve:
- approved character identity, helmet, vest, body proportion, and role
- approved BCT/dump-truck geometry, scale, wheel count, mirrors, and relative position
- approved site layout, concrete floor, lane colors, pedestrian route, cones, bollards, and hazard zone
- current storyboard beat and previous/next scene continuity
Must change this round:
- make every listed blocker visually impossible to miss
- remove unexplained gaze, character drift, vehicle drift, floor/lane drift, or generic factory framing
Do not repeat:
- floor_lane_consistency_score below minimum 4: 3
- background_consistency_score below minimum 4: 3
- hazard_zone_consistency_score below minimum 4: 3
- adjacent scene color/layout drift too high: 161.00
- floor_lane_consistency_score below minimum 4: 3
- background_consistency_score below minimum 4: 3
- hazard_zone_consistency_score below minimum 4: 3
- Apply next: Regenerate only after directly addressing these visible deficiencies: floor_lane_consistency_score below minimum 4: 3; background_consistency_score below minimum 4: 3; hazard_zone_consistency_score below minimum 4: 3; adjacent scene color/layout drift too high: 161.00. Preserve approved continuity locks.
- Apply next: Arbiter next action: regenerate_blocked_scenes

### Repeated Blockers
- 없음
## image / sc07 / round 1

- decision: `regenerate`
- total_score: `0`
- blocking_issues: missing draft image
- blocker_signatures: image:sc07:technical:missing_draft_image
- bundle: `qa/evaluation_bundles/image/sc07/round_001.json`

### Scores
- story_match_score: `0`
- identity_consistency_score: `0`
- ppe_score: `0`
- equipment_score: `0`
- story_flow_score: `0`
- technical_score: `0`
- floor_lane_consistency_score: `0`
- background_consistency_score: `0`
- character_identity_lock_score: `0`
- vehicle_geometry_lock_score: `0`
- hazard_zone_consistency_score: `0`
- total_score: `0`

### Round Outputs
- start_keyframe: `images/approved/sc07.png`
- end_keyframe: `images/approved/sc07.png`

### Improvement Notes
- RALPH critique for sc07:
Quality pressure: This result is not acceptable for a safety training video until the listed blockers are visibly fixed. Re-check the failed frame before generating again; do not make a cosmetic variation that repeats the same issue.
Failed criteria and required fixes:
- missing draft image
Must preserve:
- approved character identity, helmet, vest, body proportion, and role
- approved BCT/dump-truck geometry, scale, wheel count, mirrors, and relative position
- approved site layout, concrete floor, lane colors, pedestrian route, cones, bollards, and hazard zone
- current storyboard beat and previous/next scene continuity
Must change this round:
- make every listed blocker visually impossible to miss
- remove unexplained gaze, character drift, vehicle drift, floor/lane drift, or generic factory framing
Do not repeat:
- missing draft image
- Regenerate only after directly addressing these visible deficiencies: missing draft image. Preserve approved continuity locks.
- Arbiter next action: regenerate_blocked_scenes

### Next Prompt Memory
- Do not repeat: missing draft image
- Apply next: RALPH critique for sc07:
Quality pressure: This result is not acceptable for a safety training video until the listed blockers are visibly fixed. Re-check the failed frame before generating again; do not make a cosmetic variation that repeats the same issue.
Failed criteria and required fixes:
- missing draft image
Must preserve:
- approved character identity, helmet, vest, body proportion, and role
- approved BCT/dump-truck geometry, scale, wheel count, mirrors, and relative position
- approved site layout, concrete floor, lane colors, pedestrian route, cones, bollards, and hazard zone
- current storyboard beat and previous/next scene continuity
Must change this round:
- make every listed blocker visually impossible to miss
- remove unexplained gaze, character drift, vehicle drift, floor/lane drift, or generic factory framing
Do not repeat:
- missing draft image
- Apply next: Regenerate only after directly addressing these visible deficiencies: missing draft image. Preserve approved continuity locks.
- Apply next: Arbiter next action: regenerate_blocked_scenes

### Repeated Blockers
- 없음
## image / sc07 / round 2

- decision: `regenerate`
- total_score: `0`
- blocking_issues: missing draft image
- blocker_signatures: image:sc07:technical:missing_draft_image
- bundle: `qa/evaluation_bundles/image/sc07/round_002.json`

### Scores
- story_match_score: `0`
- identity_consistency_score: `0`
- ppe_score: `0`
- equipment_score: `0`
- story_flow_score: `0`
- technical_score: `0`
- floor_lane_consistency_score: `0`
- background_consistency_score: `0`
- character_identity_lock_score: `0`
- vehicle_geometry_lock_score: `0`
- hazard_zone_consistency_score: `0`
- total_score: `0`

### Round Outputs
- start_keyframe: `images/approved/sc07.png`
- end_keyframe: `images/approved/sc07.png`

### Improvement Notes
- RALPH critique for sc07:
Quality pressure: This result is not acceptable for a safety training video until the listed blockers are visibly fixed. Re-check the failed frame before generating again; do not make a cosmetic variation that repeats the same issue.
Failed criteria and required fixes:
- missing draft image
Must preserve:
- approved character identity, helmet, vest, body proportion, and role
- approved BCT/dump-truck geometry, scale, wheel count, mirrors, and relative position
- approved site layout, concrete floor, lane colors, pedestrian route, cones, bollards, and hazard zone
- current storyboard beat and previous/next scene continuity
Must change this round:
- make every listed blocker visually impossible to miss
- remove unexplained gaze, character drift, vehicle drift, floor/lane drift, or generic factory framing
Do not repeat:
- missing draft image
- Regenerate only after directly addressing these visible deficiencies: missing draft image. Preserve approved continuity locks.
- Arbiter next action: regenerate_blocked_scenes

### Next Prompt Memory
- Do not repeat: missing draft image
- Apply next: RALPH critique for sc07:
Quality pressure: This result is not acceptable for a safety training video until the listed blockers are visibly fixed. Re-check the failed frame before generating again; do not make a cosmetic variation that repeats the same issue.
Failed criteria and required fixes:
- missing draft image
Must preserve:
- approved character identity, helmet, vest, body proportion, and role
- approved BCT/dump-truck geometry, scale, wheel count, mirrors, and relative position
- approved site layout, concrete floor, lane colors, pedestrian route, cones, bollards, and hazard zone
- current storyboard beat and previous/next scene continuity
Must change this round:
- make every listed blocker visually impossible to miss
- remove unexplained gaze, character drift, vehicle drift, floor/lane drift, or generic factory framing
Do not repeat:
- missing draft image
- Apply next: Regenerate only after directly addressing these visible deficiencies: missing draft image. Preserve approved continuity locks.
- Apply next: Arbiter next action: regenerate_blocked_scenes

### Repeated Blockers
- 없음
## image / sc07 / round 3

- decision: `regenerate`
- total_score: `30`
- blocking_issues: manual visual consistency review is required before image approval: score floor/lane, background, character identity, vehicle geometry, and hazard-zone consistency; floor_lane_consistency_score below minimum 4: 0; background_consistency_score below minimum 4: 0; character_identity_lock_score below minimum 4: 0; vehicle_geometry_lock_score below minimum 4: 0; hazard_zone_consistency_score below minimum 4: 0; total score below minimum 44: 30
- blocker_signatures: image:sc07:identity_consistency:manual_visual_consistency_review_is_required_before_image_approval_score_floor_l; image:sc07:general:floor_lane_consistency_score_below_minimum_4_0; image:sc07:general:background_consistency_score_below_minimum_4_0; image:sc07:identity_consistency:character_identity_lock_score_below_minimum_4_0; image:sc07:general:vehicle_geometry_lock_score_below_minimum_4_0; image:sc07:general:hazard_zone_consistency_score_below_minimum_4_0; image:sc07:general:total_score_below_minimum_44_30
- bundle: `qa/evaluation_bundles/image/sc07/round_003.json`

### Scores
- story_match_score: `5`
- identity_consistency_score: `5`
- ppe_score: `5`
- equipment_score: `5`
- story_flow_score: `5`
- technical_score: `5`
- floor_lane_consistency_score: `0`
- background_consistency_score: `0`
- character_identity_lock_score: `0`
- vehicle_geometry_lock_score: `0`
- hazard_zone_consistency_score: `0`
- total_score: `30`

### Round Outputs
- reviewed_asset: `images/draft/sc07_v001.png`
- start_keyframe: `images/approved/sc07.png`
- end_keyframe: `images/approved/sc07.png`

### Improvement Notes
- RALPH critique for sc07:
Quality pressure: This result is not acceptable for a safety training video until the listed blockers are visibly fixed. Re-check the failed frame before generating again; do not make a cosmetic variation that repeats the same issue.
Failed criteria and required fixes:
- manual visual consistency review is required before image approval: score floor/lane, background, character identity, vehicle geometry, and hazard-zone consistency
- floor_lane_consistency_score below minimum 4: 0
- background_consistency_score below minimum 4: 0
- character_identity_lock_score below minimum 4: 0
- vehicle_geometry_lock_score below minimum 4: 0
- hazard_zone_consistency_score below minimum 4: 0
- total score below minimum 44: 30
Must preserve:
- approved character identity, helmet, vest, body proportion, and role
- approved BCT/dump-truck geometry, scale, wheel count, mirrors, and relative position
- approved site layout, concrete floor, lane colors, pedestrian route, cones, bollards, and hazard zone
- current storyboard beat and previous/next scene continuity
Must change this round:
- make every listed blocker visually impossible to miss
- remove unexplained gaze, character drift, vehicle drift, floor/lane drift, or generic factory framing
Do not repeat:
- manual visual consistency review is required before image approval: score floor/lane, background, character identity, vehicle geometry, and hazard-zone consistency
- floor_lane_consistency_score below minimum 4: 0
- background_consistency_score below minimum 4: 0
- character_identity_lock_score below minimum 4: 0
- vehicle_geometry_lock_score below minimum 4: 0
- hazard_zone_consistency_score below minimum 4: 0
- total score below minimum 44: 30
- Regenerate only after directly addressing these visible deficiencies: manual visual consistency review is required before image approval: score floor/lane, background, character identity, vehicle geometry, and hazard-zone consistency; floor_lane_consistency_score below minimum 4: 0; background_consistency_score below minimum 4: 0; character_identity_lock_score below minimum 4: 0; vehicle_geometry_lock_score below minimum 4: 0; hazard_zone_consistency_score below minimum 4: 0; total score below minimum 44: 30. Preserve approved continuity locks.
- Arbiter next action: regenerate_blocked_scenes

### Next Prompt Memory
- Do not repeat: manual visual consistency review is required before image approval: score floor/lane, background, character identity, vehicle geometry, and hazard-zone consistency
- Do not repeat: floor_lane_consistency_score below minimum 4: 0
- Do not repeat: background_consistency_score below minimum 4: 0
- Do not repeat: character_identity_lock_score below minimum 4: 0
- Do not repeat: vehicle_geometry_lock_score below minimum 4: 0
- Do not repeat: hazard_zone_consistency_score below minimum 4: 0
- Do not repeat: total score below minimum 44: 30
- Apply next: RALPH critique for sc07:
Quality pressure: This result is not acceptable for a safety training video until the listed blockers are visibly fixed. Re-check the failed frame before generating again; do not make a cosmetic variation that repeats the same issue.
Failed criteria and required fixes:
- manual visual consistency review is required before image approval: score floor/lane, background, character identity, vehicle geometry, and hazard-zone consistency
- floor_lane_consistency_score below minimum 4: 0
- background_consistency_score below minimum 4: 0
- character_identity_lock_score below minimum 4: 0
- vehicle_geometry_lock_score below minimum 4: 0
- hazard_zone_consistency_score below minimum 4: 0
- total score below minimum 44: 30
Must preserve:
- approved character identity, helmet, vest, body proportion, and role
- approved BCT/dump-truck geometry, scale, wheel count, mirrors, and relative position
- approved site layout, concrete floor, lane colors, pedestrian route, cones, bollards, and hazard zone
- current storyboard beat and previous/next scene continuity
Must change this round:
- make every listed blocker visually impossible to miss
- remove unexplained gaze, character drift, vehicle drift, floor/lane drift, or generic factory framing
Do not repeat:
- manual visual consistency review is required before image approval: score floor/lane, background, character identity, vehicle geometry, and hazard-zone consistency
- floor_lane_consistency_score below minimum 4: 0
- background_consistency_score below minimum 4: 0
- character_identity_lock_score below minimum 4: 0
- vehicle_geometry_lock_score below minimum 4: 0
- hazard_zone_consistency_score below minimum 4: 0
- total score below minimum 44: 30
- Apply next: Regenerate only after directly addressing these visible deficiencies: manual visual consistency review is required before image approval: score floor/lane, background, character identity, vehicle geometry, and hazard-zone consistency; floor_lane_consistency_score below minimum 4: 0; background_consistency_score below minimum 4: 0; character_identity_lock_score below minimum 4: 0; vehicle_geometry_lock_score below minimum 4: 0; hazard_zone_consistency_score below minimum 4: 0; total score below minimum 44: 30. Preserve approved continuity locks.
- Apply next: Arbiter next action: regenerate_blocked_scenes

### Repeated Blockers
- 없음
