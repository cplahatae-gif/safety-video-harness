# continuity-qa

Review storyboard, prompts, and images from an isolated QA context.

Return scores, blockers, evidence paths, and concrete regeneration deltas.

## Required Review Axes

- Story match: the frame shows the intended storyboard role and safety behavior.
- Identity continuity: worker, signal person, supervisor, PPE, BCT, dump truck, and site layout stay consistent.
- PPE/equipment accuracy: helmet, vest, workwear, trucks, lanes, pedestrian route, and hazard zone are plausible.
- Story flow: adjacent frames must read as one continuous prevention story, not independent checklist cards.
- Technical readiness: the image is readable 16:9 keyframe material.
- Visual-lock continuity: floor/lane, background, character identity, vehicle geometry, and hazard-zone scores are present.
- Sliding chain: `scNN` clip starts at `images/approved/scNN.png` and ends at `images/approved/scNN+1.png`.
- Education match: each scene must trace back to source citations and avoid unsupported safety claims.
- Video readiness: if any image has blockers, do not proceed to Higgsfield/Seedance.

## Scoring

- Score each axis 0-5.
- 5: clearly meets the criterion.
- 4: usable with minor manual review.
- 3 or lower: regeneration or storyboard repair required.
- Image pass threshold: total 44/55 or higher, every axis 4 or higher, no critical blockers.
- Production image approval also requires `qa/image_manual_reviews.json` or equivalent isolated visual QA covering floor/lane, background, character identity, vehicle geometry, and hazard-zone consistency.

## References

- Reference index: `docs/generative-media-reference-index.md`
- OpenAI Image generation guide: https://developers.openai.com/api/docs/guides/image-generation
- OpenAI Video generation guide: https://developers.openai.com/api/docs/guides/video-generation
- JSON Schema docs: https://json-schema.org/docs
- Local image QA implementation: `safety_video_harness/image_qa.py`
- Local scene-link validation: `safety_video_harness/scene_links.py`
- Local role reference: `references/continuity-qa-reference.md`
- Evaluation rubric: `docs/evaluation-rubrics.md`
- Few-shot QA examples: `docs/few-shot-examples.md`
