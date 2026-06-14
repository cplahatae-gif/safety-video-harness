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
