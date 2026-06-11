# continuity-qa

Review storyboard, prompts, and images from an isolated QA context.

Return scores, blockers, evidence paths, and concrete regeneration deltas.

## Required Review Axes

- Story flow: adjacent frames must read as one continuous prevention story, not independent checklist cards.
- Sliding chain: `scNN` clip starts at `images/approved/scNN.png` and ends at `images/approved/scNN+1.png`.
- Education match: each scene must trace back to source citations and avoid unsupported safety claims.
- Identity continuity: worker, signal person, supervisor, PPE, BCT, dump truck, and site layout stay consistent.
- Video readiness: if any image has blockers, do not proceed to Higgsfield/Seedance.

## Scoring

- Score each axis 0-5.
- 5: clearly meets the criterion.
- 4: usable with minor manual review.
- 3 or lower: regeneration or storyboard repair required.
- Total pass threshold: 24/30 and no blockers.
