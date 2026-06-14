# Visual Director Arbiter Reference

Source links:
- OpenAI Image generation: https://developers.openai.com/api/docs/guides/image-generation
- OpenAI Video generation: https://developers.openai.com/api/docs/guides/video-generation
- MCP prompts specification: https://modelcontextprotocol.io/specification/2025-06-18/server/prompts
- Higgsfield CLI/MCP: https://higgsfield.ai/cli
- Central source list: `docs/reference-sources.md`

Checked: 2026-06-12

## Local Reference Notes

- OpenAI prompt engineering guidance recommends modular, versioned prompt builders and evaluation checks. The arbiter should treat scene prompts as candidate components that must be merged into one coherent production prompt set.
- Image generation guidance implies that prompt specificity matters for composition, style, and reference use. The arbiter must reject vague prompts before they reach imagegen.
- Video generation guidance relies on strong input frames and clear motion intent. The arbiter must verify that keyframes are video-ready before paid generation is considered.
- MCP prompt specifications separate reusable prompt templates from dynamic inputs. This maps to the harness design: agent instructions stay stable, while storyboard facts, style bibles, and scene deltas are dynamic inputs.
- Higgsfield/Seedance generation is downstream and paid, so arbitration should prefer cheap prompt/story/style fixes before any live generation.
- The arbiter should merge parallel scene prompts into one visual universe: same art style, recurring worker identity, truck scale, BCT geometry, lane markings, lighting, and camera grammar.
- Arbitration output must be machine-actionable. A decision like "make it better" is invalid; every revision must say which field to change and what phrase or constraint to add.
- If scene agents disagree, prefer source-grounded safety clarity over cinematic novelty. Education comprehension outranks dramatic camera movement.
- Treat reference assets as typed inputs. Person, work situation, equipment, space, style, and camera references affect different prompt fields and should not be blended blindly.
- The ready-for-generation decision requires no unresolved blocker, no missing scene role, no missing gaze target, and no contradiction with the selected style guide.

## Use In This Harness

The visual director arbiter is the gate between parallel scene prompt drafting and centralized image generation.
It prevents each scene agent from creating a different visual universe.

## Operational Rules

- Integrate prompt tone, camera distance, cast count, and visual locks before imagegen.
- Prefer `revise_scene_prompt` over generation when a prompt is vague or inconsistent.
- Escalate to `revise_style_bible` if the anchor is too weak to enforce consistency.
- Escalate to `revise_storyboard` if the scene is too broad or visually impossible.
- Keep actual imagegen execution centralized.

## Output Expectations

- Decision must be one of `ready_for_generation`, `revise_scene_prompt`, `revise_style_bible`, `revise_storyboard`.
- Return concrete revisions per scene rather than generic quality comments.
