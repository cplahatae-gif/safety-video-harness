# Safety Video Harness Rules

- Never run live image or video generation without approval.
- Before changing architecture, pipeline terminology, RALPH semantics, or QA ledger behavior, read `CONTEXT.md`.
- Before using any local agent or skill, read its `AGENT.md`/`SKILL.md` and package-local `references/*.md`.
- Before scoring storyboard, image, or video outputs, read `docs/evaluation-rubrics.md`.
- Before writing a new storyboard, prompt, QA finding, or video prompt, check `docs/few-shot-examples.md` for the expected specificity level.
- Before any Higgsfield/Seedance planning or dry-run, read `docs/higgsfield-seedance-local-reference.md`.
- Start each new safety-video project with an intake interview before storyboard, image, or video generation.
- Each new safety-video project must include a generated project-level `HANDOFF.md` from `app/harness/templates/project/HANDOFF.md`.
- Intake must ask for source files, topic, target seconds, image density, reference images, selected style guide, aspect ratio, text delivery, and approval scope.
- Use Codex built-in `imagegen` skill/tool as the default image generation path.
- Do not implement OpenAI Image API/CLI image generation unless the user explicitly asks for that fallback.
- Never leave project image assets only under `$CODEX_HOME/generated_images`; move or copy selected outputs into the project.
- Never make a safety claim without a source citation.
- Never overwrite approved artifacts.
- Keep generated-image text out of keyframes unless explicitly approved.
- Deliver required Korean text through subtitle/overlay/title-card artifacts, not generated text inside image keyframes.
- Build keyframes as one causal story flow, not disconnected checklist panels.
- Each image prompt must state previous-scene continuity, current story beat, and next-scene setup.
- Do not treat independent text-only multi-frame image generation as production quality; it is draft exploration only.
- Before final keyframes, create or approve an asset lock layer: cast, PPE, equipment, space/background, style, and work-situation references.
- Prefer reference/edit chaining or deterministic compositing for production keyframes when character, vehicle, or background consistency matters.
- Validate sliding-chain continuity before video work: scNN must end at scNN+1 so adjacent clips share a keyframe.
- Seedance/Higgsfield clips must use approved start/end keyframes and available reference media; do not generate production video from prompt text alone.
- Use Higgsfield Soul ID or equivalent character reference when recurring human identity must be preserved and external upload is approved.
- Use score-based QA before regeneration or video: story match, identity, PPE, equipment, story flow, technical readiness, floor/lane consistency, background consistency, character identity lock, vehicle geometry lock, and hazard-zone consistency.
- Do not approve production images without `qa/image_manual_reviews.json` or an equivalent isolated visual QA artifact covering floor/lane, background, identity, vehicle geometry, and hazard-zone consistency.
- Use `scripts/build_image_visual_review.py` to create local contact-sheet evidence before Gate 2; treat it as heuristic support, not a full semantic replacement for human/model visual review.
- Use OpenCV MCP as the preferred no-cost first-pass visual inspection layer for floor/lane, hazard-zone, background, and layout drift; do not treat OpenCV metadata as a full semantic identity/gaze review.
- Treat RALPH as an early-stopping loop: stop immediately when thresholds pass, and never exceed 10 image QA iterations per scene.
- Evaluate generated assets from an isolated QA context using an evidence bundle; do not let the generator approve its own output.
- Append every storyboard, image, and video QA round to project evidence and `llm-wiki/evaluation-rounds.md`.
- Do not pass video QA from metadata alone; sampled-frame inspection evidence plus visual QA must approve character continuity, gaze motivation, education clarity, and storyboard alignment.
- Treat unclear gaze direction, unexplained character appearance/disappearance, or generic factory footage as video blockers.
- Ask where each reference belongs: `refs/people`, `refs/ppe`, `refs/equipment`, `refs/approved/people`, `refs/approved/work`, `refs/approved/spaces`, `refs/approved/style`, `refs/approved/camera`, or `refs/approved/lighting`. Old `model/`, `product/`, and `ref/` paths are migration read fallbacks only.
- After asking whether references exist, ask which reusable style guide to use and show 5 choices from `references/style/catalog.json`.
- Store reusable styles under `references/style/<style-id>/STYLE_GUIDE.md` with reference images in `references/style/<style-id>/references/`.
- Use dry-run before live work.
- Do not treat approval for one stage as approval for later stages; broad wording such as "go ahead" or "make it" is not enough to skip checkpoints.
- Required human checkpoints for every safety-video project:
  1. Storyboard/scenario approval before live image generation or final image prompt execution.
  2. Keyframe/image approval after image generation and QA, before any Higgsfield/Seedance upload or video generation.
  3. Final video confirmation after generated video QA, before calling the result final or handing it off as approved.
- Before any paid Seedance/Higgsfield execution, also disclose estimated credits, confirm external upload permission, and get explicit approval for that paid run.
- Treat 30 seconds as a cost guardrail, not a technical limit.
- Inspect video through sampled frames, not direct MP4 understanding.
- When handing off, ending a long task, or preparing work for another session, include a ready-to-copy recommended prompt that tells the next session which files to read, which approvals are forbidden, and what the next action should be.
