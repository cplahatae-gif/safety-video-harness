# Evaluation Rubrics

Checked: 2026-06-12

This document defines local scoring standards for the safety video harness. Use it before any RALPH loop, image regeneration, or video-generation proposal. Do not rely on a general impression such as "looks good"; every pass/fail decision must cite a scene ID, artifact path, score, and blocker.

## Mandatory Reference Read

Before running or simulating any agent or skill, read:

1. `AGENTS.md`
2. the selected `agents/<agent-id>/AGENT.md` or `skills/<skill-id>/SKILL.md`
3. that package's `references/*.md`
4. this rubric when scoring storyboards, images, or video

If the work uses a style guide, also read `style-guides/<style-id>/STYLE_GUIDE.md`.

## Score Scale

Use `0-5` for every evaluation axis.

- `5`: Fully satisfies the contract. The output is clear, source-grounded, consistent, and ready for the next stage.
- `4`: Usable with minor risk. No blocker, but one small issue should be noted for the next round.
- `3`: Borderline. Requires revision before paid or irreversible work. Can be useful as draft evidence.
- `2`: Fails the axis. The scene/image/video would confuse the viewer or break continuity.
- `1`: Severe failure. The output contradicts the source, changes identity/equipment, or hides the safety lesson.
- `0`: Missing or unusable. Required artifact is absent, unreadable, or unrelated to the requested topic.

Critical blockers override totals. A high numeric score cannot pass an artifact with a critical blocker.

## Storyboard QA

Minimum pass: average `4.0` or higher and no critical blocker.

Axes:

- Source grounding: every safety claim maps to extracted source facts or explicit user instruction.
- Teachability: the viewer can understand the hazard and prevention behavior without narration.
- Causal flow: scenes move from hazard context to exposure, control, verification, correction, rule reinforcement, and safe end state.
- Keyframeability: each scene can be drawn as one clear still frame.
- Duration fit: scene count and density match the selected video seconds and image quantity mode.
- Text strategy: exact Korean teaching text is assigned to subtitle, overlay, or title card, not generated inside image keyframes.

Critical blockers:

- unsupported safety claim
- narration/TTS dependency
- scene cannot be represented visually
- no selected topic when multiple topics exist
- sequence jumps from one unrelated safety lesson to another

## Image QA

Minimum pass: total `24/30` or higher and no critical blocker.

Axes:

- Story match: the image shows the intended scene role and safety behavior.
- Identity continuity: recurring workers, PPE, BCT, dump truck, and plant space remain stable.
- PPE/equipment accuracy: helmet, vest, work clothes, truck type, lane, pedestrian route, and hazard zone are plausible.
- Gaze and pose motivation: every visible person looks or gestures toward a visible safety cue.
- Style match: line quality, palette, camera grammar, and rendering style match the selected style guide.
- Video readiness: the image can serve as a start/end keyframe in the sliding-chain plan.

Critical blockers:

- a worker appears, disappears, duplicates, or changes role without story reason
- gaze points off-screen without visible target
- BCT, dump truck, PPE, or site layout changes in a way that breaks continuity
- image relies on AI-rendered Korean/English text
- collision impact, injury, gore, or unsupported accident spectacle appears
- generated frame looks like generic factory footage rather than the selected SOP topic

## Video QA

Video QA is propose-only unless the user explicitly approves paid regeneration.

Minimum pass: every axis `4` or higher, inspection manifest present, and no critical blocker.

Axes:

- Technical validity: duration, resolution, FPS, codec, and file readability are confirmed by local inspection.
- Start/end alignment: clip begins from approved `scNN` and resolves toward approved `scNN+1`.
- Character continuity: people do not appear, disappear, duplicate, or change role without storyboard motivation.
- Gaze and motion motivation: movement, camera, and gaze reinforce the safety cue.
- Education clarity: prevention behavior is understandable from frames plus subtitles/overlays, without narration.
- Storyboard alignment: generated motion does not invent a new story.

Critical blockers:

- no inspection manifest or sampled frame evidence
- video duration/resolution differs from approved spec
- motion emphasizes collision or injury instead of prevention
- unexplained character or vehicle drift
- subtitles/overlays missing when required for comprehension

## RALPH Loop Policy

RALPH is early-stopping, not a fixed 20-round loop.

1. Generate or revise the artifact.
2. Evaluate with the relevant rubric.
3. If pass threshold is met and no critical blocker exists, stop.
4. If failed, write a concrete regeneration delta.
5. Inject previous blockers from `llm-wiki/evaluation-rounds.md`.
6. Repeat until pass or max `20` image/storyboard iterations.
7. If the same blocker appears `3` times, stop repeating and escalate upstream.

Escalation targets:

- Story issue: revise topic/storyboard.
- Style issue: revise style guide or lead style bible.
- Prompt issue: revise scene prompt contract.
- Image artifact: regenerate the affected scene.
- Video issue: propose prompt/keyframe/storyboard fixes; do not auto-regenerate paid video.

