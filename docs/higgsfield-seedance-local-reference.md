# Higgsfield and Seedance Local Reference

Checked: 2026-06-12

Primary source: https://higgsfield.ai/cli

This is the local operating reference for Higgsfield/Seedance usage in the safety video harness. It avoids requiring every agent run to reopen the web page.

## Official CLI Facts To Preserve

- Install command: `npm install -g @higgsfield/cli`
- Login command: `higgsfield auth login`
- Skill install command shown by Higgsfield: `npx skills add higgsfield-ai/skills`
- Auth, uploads, polling, and result fetching are handled by the CLI.
- `generate create` accepts media flags including `--image`, `--start-image`, `--end-image`, `--video`, and `--audio`.
- `seedance_2_0` exposes a `medias` parameter, and the CLI can attach local files or uploaded IDs through media flags.
- `soul-id create` trains reusable Soul references from multiple uploaded images; use this for recurring human identity when allowed.
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
- Do not use Higgsfield for image keyframes by default. Codex built-in `imagegen` is the default image path unless the user asks for Higgsfield image generation.
- Do not upload reference images, generated images, source documents, or videos unless `external_upload_allowed=true` and the relevant gate is approved.
- For cost control, use short test clips first. The project policy is a short live test, normally around 10 seconds, and only with explicit user approval.
- Do not create production Seedance clips from text prompt alone. Use approved `start_image`, approved `end_image`, and available reference media.
- Treat Soul ID, cast sheets, equipment references, and space/background plates as the lock layer; prompt text is orchestration, not identity storage.

## Consistency Lessons

The local imagegen tests showed the same limitation reported by common AI video workflows:

- Text-only multi-frame generation drifts in face, body, PPE, vehicle geometry, road markings, and background.
- A single 2x2 storyboard sheet reduces drift but still does not guarantee production-grade identity or background continuity.
- Production-grade continuity requires reference conditioning or deterministic composition before video generation.

Recommended production order:

1. Build an asset lock manifest.
2. Create or approve cast, equipment, space/background, style, and work-situation references.
3. If recurring human identity matters and external upload is approved, create a Higgsfield Soul ID from multiple cast images.
4. Generate or compose approved keyframes from locked assets.
5. Use those approved keyframes as `--start-image` and `--end-image`.
6. Attach the available reference media pack with `--image` flags when building Higgsfield jobs.
7. Keep clips short and chained: `sc01 -> sc02`, `sc02 -> sc03`, and so on.

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
  "start_keyframe": "media/images/approved/sc03.png",
  "end_keyframe": "media/images/approved/sc04.png",
  "prompt_path": "story/video_prompts.json",
  "reference_media_pack": [
    "refs/people/signal-worker.png",
    "refs/equipment/bct-truck.png",
    "refs/approved/spaces/plant-entry.png",
    "refs/approved/style/webtoon-style.png"
  ],
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
- reference media roles: cast, equipment, space/background, style, and work-situation references
- explicit statement that start/end keyframes and media references are the lock layer
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
