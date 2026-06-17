# Safety Video Harness Context

## Core Mission

This harness creates safety-training video projects from source training material. It is dry-run first, storyboard first, and approval gated before any live image or paid video generation.

## Domain Terms

- `project`: One safety-video workspace containing sources, references, storyboard, prompts, QA, gates, evidence, and final video assets.
- `source`: A training file such as PPTX/PDF/SOP used as cited safety evidence.
- `topic`: A candidate education subject extracted from source facts.
- `scene`: One storyboard beat. In the sliding-chain video model, scene `scNN` becomes one clip from keyframe `scNN` to keyframe `scNN+1`.
- `keyframe`: A still image used as a Seedance start or end frame.
- `final keyframe`: The extra `scNN+1` image required to close the last clip.
- `asset lock`: The approved reference layer that fixes cast identity, PPE, equipment, space/background, style, and work-situation geometry before production keyframes.
- `reference media pack`: The image references passed to Higgsfield/Seedance alongside start/end keyframes, such as cast sheets, equipment refs, space plates, and style refs.
- `Gate 1`: Storyboard approval. Required before live imagegen job preparation.
- `Gate 2`: Image-to-video approval. Required before live Seedance planning or execution.
- `round`: One recorded evaluator decision in `qa/evaluation_rounds.jsonl`.
- `iteration`: A counted RALPH retry position for a blocked item. Passing validation rounds do not increment image RALPH iteration counts.
- `blocking_issue`: Human-readable problem that prevents approval.
- `blocker_signature`: Stable normalized blocker identity used to detect repeated failure.
- `repeated_blocker`: A blocker signature that has occurred at least three times for the same stage and item.
- `RALPH loop`: Early-stopping repair loop for storyboard/image quality. It stops when thresholds pass, when repeated blockers require upstream escalation, or at max 20 image iterations.
- `propose-only video QA`: Video failures produce recommendations only. The harness must not automatically regenerate paid video.

## Non-Negotiable Policies

- Never run live imagegen, live Seedance, live TTS, or paid calls before explicit approval.
- Do not add narration or TTS. Use title cards, overlays, or subtitles for text delivery.
- Do not let generated image text carry required Korean safety wording.
- Do not overwrite approved assets; preserve older approved versions.
- Do not approve image or video quality from metadata alone.
- Use isolated QA evidence bundles so the generator does not approve its own output.
- Do not treat independent text-only multi-frame generation as production quality; use asset lock, reference/edit chaining, or deterministic compositing before final keyframes.
- Do not generate production Seedance clips from prompt text alone; use approved start/end keyframes and available reference media.

## Architecture Orientation

- State IO lives behind `safety_video_harness.io` and lock helpers.
- Reference scanning lives behind `safety_video_harness.reference_catalog`.
- Image draft/approved versioning lives behind `safety_video_harness.image_versions`.
- External subprocess execution lives behind `safety_video_harness.external_tools`.
- Seedance live planning is guarded in `safety_video_harness.generation` before any live plan file is written.
