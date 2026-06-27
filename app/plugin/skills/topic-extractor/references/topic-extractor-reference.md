# Topic Extractor Reference

Source links:
- OpenAI Prompt engineering: https://developers.openai.com/api/docs/guides/prompt-engineering
- JSON Schema docs: https://json-schema.org/docs
- Central source list: `docs/reference-sources.md`

Checked: 2026-06-12

## Local Reference Notes

- OpenAI prompt engineering guidance emphasizes relevant context and structured outputs. Topic extraction must preserve the original education material as grounded context and return schema-compatible candidates.
- JSON Schema guidance supports explicit contracts for required fields, types, and validation. Extracted topics should be predictable enough for downstream storyboard generation and QA.
- Education materials can contain multiple teachable risks. The extractor should not collapse them into one vague theme; it should list candidate topics with evidence, priority, and video suitability.
- Source citations are mandatory because later stages must reject unsupported safety claims.
- Topic selection should remain a user/interview decision unless the user explicitly asks for an automatic default.
- Split topics by teachable action, not only by slide title. One PPT may contain traffic control, blind spots, pedestrian route, communication signal, and equipment separation as separate candidates.
- Each topic candidate needs a video-fit estimate: whether it can be shown visually in 10-30 seconds without narration.
- Prefer topics with visible before/after behavior. A good safety video topic has an unsafe setup, a correction, and a safe final state.
- Keep extracted topic output deterministic: stable IDs, source page/slide references, risk type, target worker, core prevention behavior, and excluded claims.
- If source rendering is incomplete, mark confidence low and request manual confirmation instead of inventing missing SOP details.

## Use In This Harness

This skill turns rendered education material into multiple candidate safety topics. It must preserve source citations
so later storyboard and QA stages can reject unsupported claims.

## Operational Rules

- Extract multiple topics when the education material covers more than one risk.
- Include risk type, target worker, citation, priority, and video-fit score.
- Prefer concrete incident-prevention topics over abstract safety slogans.
- Keep output schema-compatible with `sources/extracted_topics.json`.
- Do not select the final topic unless the user asks for defaults.

## Output Expectations

- Topic IDs are stable.
- Every recommendation is grounded in rendered source facts.
