# Continuity Bible: Scenario V2

Date: 2026-06-16

Generation strategy:
- Generate one 2x2 storyboard sheet in a single imagegen call.
- Crop the four panels into separate files afterward.
- This is intended to reduce drift across props, road color, mirror presence, vehicles, workers, and style.

## Fixed Visual World

Site:
- Same ready-mix concrete plant entrance in every panel.
- Same camera axis across all panels: three-quarter front-left view of the BCT and right-side pedestrian lane.
- Background silos and conveyors remain in the same broad location.

Road and lane colors:
- Vehicle lane: neutral gray concrete only.
- Pedestrian lane: desaturated green strip on the right side only.
- Hazard zone: fixed red/orange painted arc at the same crossing area in all panels.
- Bollards: black-yellow bollards separating vehicle lane and pedestrian lane.

Mirror policy:
- No large roadside convex mirror in any panel.
- Only normal vehicle side mirrors attached to the BCT may appear.

Vehicles:
- Same white BCT cement tanker truck in all panels.
- Same yellow dump truck parked ahead in the background in all panels.
- No extra vehicles.

Cast:
- Signal worker: one adult Korean male, white hard hat, orange reflective vest, navy workwear, white gloves, black safety boots.
- BCT driver: one adult Korean male, white hard hat, navy workwear, visible through windshield or side window.
- Ground worker: appears only in panels 3 and 4, behind the safety line, never in the vehicle path.

Style:
- Korean industrial webtoon safety illustration.
- Cleaner line art and flatter cel shading than the previous semi-realistic run.
- No generated Korean/English text inside images.
- No logos.

## Panel Beats

1. sc01 hazard context:
   - BCT approaches before the red/orange hazard arc.
   - Signal worker watches from safe green-lane side.
   - Dump truck ahead explains blind spot risk.

2. sc02 stop and confirm:
   - BCT stopped before the hazard arc.
   - Signal worker gives clear stop signal.
   - Driver looks toward signal worker and vehicle side mirror.

3. sc03 verify route:
   - BCT still stopped.
   - Signal worker points to safe vehicle path.
   - Ground worker stands behind safety line.

4. sc04 controlled safe movement:
   - BCT nose has advanced roughly one truck length beyond the previous stop position while staying out of the pedestrian lane.
   - Signal worker guides calmly from safe zone.
   - Ground worker remains behind safety line.

## Production Acceptance Criteria

- Same road colors and hazard arc across all panels.
- No roadside convex mirror appears in any panel.
- Same BCT/dump truck/site/cast design across all panels.
- sc04 must visibly happen later than sc03.
- The four images must read as one causal safety story.
