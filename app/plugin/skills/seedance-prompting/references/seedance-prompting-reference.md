# Seedance Prompting Reference

Source links:
- Higgsfield CLI/MCP: https://higgsfield.ai/cli
- OpenAI Video generation: https://developers.openai.com/api/docs/guides/video-generation
- OpenAI Image generation: https://developers.openai.com/api/docs/guides/image-generation
- Central source list: `docs/reference-sources.md`

Checked: 2026-06-12

## Local Reference Notes

- OpenAI video generation guidance emphasizes prompts plus reference images, clip creation, extension, editing, and continuity. This harness uses that principle by treating approved keyframes as hard start/end anchors.
- Higgsfield/Seedance prompting should be motion-specific: name the action, camera movement, safety objective, forbidden motion, and continuity lock rather than repeating only the image prompt.
- Paid video generation must sit behind Gate 2. Prompt drafting can be dry-run, but live generation needs user approval, cost disclosure, and external upload permission.
- The project has a no-narration policy. Video prompts must not request voiceover, TTS, or spoken explanation.
- If image QA has unresolved blockers, Seedance prompts should not be generated for live use because the video model will likely amplify the defect.
- Each clip prompt must describe motion between two approved keyframes, not invent a new scene. The start frame and end frame are the hard visual contract.
- Keep motion short, legible, and safety-oriented: slow truck approach, worker pause, spotter signal, driver mirror check, pedestrian route confirmation, hazard-zone avoidance.
- Avoid uncontrolled camera changes. If movement is needed, specify a simple pan, dolly, or static industrial training shot rather than cinematic chaos.
- Include forbidden motion such as "no collision impact", "no worker disappearance", "no extra workers", "no logo mutation", and "no unreadable AI-generated text".
- Live video is behind Gate 2. Dry-run can create prompt specs, but paid generation requires user approval, external upload permission, cost note, and exact clip count.

## Use In This Harness

This skill writes video prompts after approved keyframes exist. It must preserve the start/end keyframe contract and
stay behind Gate 2 because Seedance/Higgsfield generation is paid.

## Operational Rules

- Use start and end keyframes as hard anchors.
- Preserve PPE, vehicle identity, lane layout, hazard zones, and camera continuity.
- Motion should illustrate prevention, not an accident impact.
- Do not include narration or TTS.
- Live generation requires cost disclosure, user approval, and `external_upload_allowed=true`.

## Output Expectations

- Every clip prompt names start frame, end frame, motion objective, forbidden motion, and continuity lock.
- Failed video QA should produce proposals only, not automatic paid regeneration.
