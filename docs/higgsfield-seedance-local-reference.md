# Higgsfield and Seedance Local Reference

Checked: 2026-06-12

Primary source: https://higgsfield.ai/cli

This is the local operating reference for Higgsfield/Seedance usage in the safety video harness. It avoids requiring every agent run to reopen the web page.

## Official CLI Facts To Preserve

- Install command: `npm install -g @higgsfield/cli`
- Login command: `higgsfield auth login`
- Skill install command shown by Higgsfield: `npx skills add higgsfield-ai/skills`
- Auth, uploads, polling, and result fetching are handled by the CLI.
- Higgsfield uses credits; generation cost depends on model, duration, resolution, and asset type.
- Generation is asynchronous; video jobs can take longer depending on duration and model.
- The command families exposed by the CLI page are:
  - `auth`, `account`, `workspace`, `version`
  - `model list`, `model get`
  - `generate create`, `generate cost`, `generate wait`, `generate get`, `generate list`
  - `upload image`, `upload video`, `upload audio`
  - `soul-id create`, `soul-id wait`, `soul-id list`
  - `marketing-studio virality_predictor`
- Higgsfield exposes multiple image and video models, including Seedance for video.
- Previous generations and uploaded assets can be reused as inputs.

## Harness Policy

- Live Higgsfield/Seedance calls are paid work and require Gate 2 approval.
- Dry-run may create prompt specs, cost-estimate command specs, upload specs, and job specs without executing them.
- Do not auto-run paid video regeneration after QA failure. Produce a proposal first.
- Do not use Higgsfield for image keyframes by default. `scripts/codex_image.sh` (Codex CLI) is the default image path unless the user asks for Higgsfield image generation.
- Do not upload reference images, generated images, source documents, or videos unless `external_upload_allowed=true` and the relevant gate is approved.
- For cost control, use short test clips first. The project policy is a short live test, normally around 10 seconds, and only with explicit user approval.

## Recommended Dry-Run Contract

For each intended clip, write a job spec before any live action:

```json
{
  "clip_id": "sc03_to_sc04",
  "provider": "higgsfield",
  "model_family": "seedance",
  "mode": "image_to_video",
  "duration_seconds": 5,
  "aspect_ratio": "16:9",
  "start_keyframe": "images/approved/sc03.png",
  "end_keyframe": "images/approved/sc04.png",
  "prompt_path": "video_prompts/sc03_to_sc04.md",
  "cost_estimate_required": true,
  "gate_required": "image_to_video",
  "external_upload_allowed_required": true
}
```

## Prompt Requirements

Each video prompt must include:

- clip ID and source scene IDs
- start keyframe role and end keyframe role
- visible cast and equipment to preserve
- motion objective
- camera movement, or explicit static camera
- timing and duration
- forbidden motion
- continuity locks
- no narration/TTS statement
- subtitle/overlay plan if text is needed

## QA Requirements After Generation

After live generation, inspect locally before approval:

1. Save the MP4 into the project output folder.
2. Run `scripts/inspect_video.py` or equivalent local inspection.
3. Confirm duration, resolution, FPS, codec, and unexpected audio presence.
4. Extract sampled frames.
5. Compare sampled frames with storyboard and approved keyframes.
6. Write video QA findings.
7. If failed, produce a paid-regeneration proposal only.

