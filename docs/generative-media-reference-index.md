# Generative Media Reference Index

This project keeps external references explicit so agent prompts can cite the guidance they rely on.
The source URL ledger is `docs/reference-sources.md`; role-specific operational summaries live inside
`agents/<agent-id>/references/` and `skills/<skill-id>/references/`.

## Official References

- OpenAI Image generation guide: https://developers.openai.com/api/docs/guides/image-generation
  - Use for image generation/editing modes, reference-image workflows, output customization, cost/latency, and known limitations.
  - Relevant constraints for this harness: image generation may struggle with recurring character/brand consistency and precise layout, so we lock style/identity before generation and avoid exact in-image text.
- OpenAI Prompt engineering guide: https://developers.openai.com/api/docs/guides/prompt-engineering
  - Use for agent instruction design, scene prompt structure, structured JSON outputs, and systematic prompt improvement.
- OpenAI Images and vision guide: https://developers.openai.com/api/docs/guides/images-vision
  - Use for image input and vision cost considerations when reference images are uploaded through API-style workflows.
- OpenAI Video generation guide: https://developers.openai.com/api/docs/guides/video-generation
  - Use for continuity concepts such as image references, character reuse, clip extension, and video editing.
- Higgsfield CLI/MCP page: https://higgsfield.ai/cli
  - Use for Higgsfield CLI install/auth, model catalog, generate/upload commands, asynchronous job handling, and credit-based generation policy.
- Model Context Protocol introduction: https://modelcontextprotocol.io/docs/getting-started/intro
  - Use for MCP architecture, external tools/resources, and plugin-style harness integrations.
- Model Context Protocol tools: https://modelcontextprotocol.io/specification/2025-06-18/server/tools
  - Use when designing tool contracts that let models call external systems.
- Model Context Protocol resources: https://modelcontextprotocol.io/specification/2025-06-18/server/resources
  - Use when exposing source files, schema manifests, reference assets, and inspection bundles as context.
- Model Context Protocol prompts: https://modelcontextprotocol.io/specification/2025-06-18/server/prompts
  - Use when turning repeatable workflows into parameterized prompt templates.
- FFmpeg documentation: https://ffmpeg.org/documentation.html
  - Use for official ffmpeg/ffprobe command reference.
- ffprobe documentation: https://ffmpeg.org/ffprobe.html
  - Use for duration, FPS, stream, metadata, and machine-readable video inspection.
- JSON Schema documentation: https://json-schema.org/docs
  - Use for schema validation, output contracts, and QA report formats.
- JSON Schema specification: https://json-schema.org/specification
  - Use for formal schema behavior and validation language details.

## Local References

- Evaluation rubrics: `docs/evaluation-rubrics.md`
  - Use before scoring storyboards, images, video clips, or RALPH-loop outputs.
- Few-shot examples: `docs/few-shot-examples.md`
  - Use before writing storyboard scenes, image prompts, QA findings, or video prompts.
- Higgsfield/Seedance local reference: `docs/higgsfield-seedance-local-reference.md`
  - Use before any Higgsfield/Seedance planning, dry-run, cost estimate, upload, or paid-generation proposal.
- Codex imagegen skill: `$CODEX_HOME/skills/.system/imagegen/SKILL.md`
  - This harness uses Codex built-in `imagegen` as the default image path, not OpenAI API/CLI fallback.
- Seedance expert skill: `$CODEX_HOME/skills/seedance-expert/SKILL.md`
  - Use when writing Seedance/Higgsfield video prompts.
- Style guide catalog: `style-guides/README.md`
  - Use for project-level style choices.
- Current webtoon style: `style-guides/korean-industrial-webtoon/STYLE_GUIDE.md`
  - Use for precision industrial webtoon keyframes.
- Image prompt reference rules: `docs/imagegen-prompting-references.md`
  - Use for local prompt structure, no text in keyframes, story flow, and continuity requirements.

## How Agents Should Use These

1. The lead style agent reads the style guide and first keyframe, then freezes the bible.
2. Scene prompt agents write scene-specific prompt briefs against that bible.
3. Visual director arbiter checks the whole prompt set before `imagegen` runs.
4. Generated images are evaluated by existing QA roles and RALPH loop logic.
5. Video work remains downstream and paid/live generation stays gate-protected.

## Role-to-Reference Map

| Role | Primary references |
|---|---|
| `topic-extractor` | OpenAI Prompt engineering, JSON Schema docs, project source facts |
| `story-writer` | OpenAI Prompt engineering, OpenAI Video generation, local no-narration contract |
| `style-ref-search` | OpenAI Image generation, OpenAI Images and vision, style guide catalog |
| `lead-style-agent` | OpenAI Image generation, local Codex imagegen skill, selected style guide |
| `scene-prompt-agent` | OpenAI Prompt engineering, OpenAI Image generation, style bible |
| `visual-director-arbiter` | OpenAI Image generation limitations, OpenAI Video generation continuity, MCP prompts |
| `image-consistency-check` | OpenAI Image generation limitations, local style guide, visual continuity agents |
| `seedance-prompting` | Higgsfield CLI/MCP, OpenAI Video generation, local Seedance expert skill |
| `video-inspect` | FFmpeg, ffprobe, OpenAI Video generation, local video analysis skills |

## Packaged Summary Rule

Do not make agents or skills depend only on raw external URLs. Each agent/skill package should carry its own
local operating reference under `references/` so it can be copied, reviewed, or executed independently without reopening the source sites during normal work.
| `video-qa` | ffprobe, OpenAI Video generation, Higgsfield CLI/MCP, local inspection manifest |
