---
name: topic-extractor
description: Extract multiple source-cited safety education topic candidates from rendered PPTX, SOP, or guide materials for user selection before storyboard planning.
---

# topic-extractor

Use rendered education material to propose multiple safety-training topics.

Output `sources/extracted_topics.json` with source citations, risk type, target worker,
video-fit score, priority score, and recommendation status.

## References

- Reference index: `docs/generative-media-reference-index.md`
- OpenAI Prompt engineering guide: https://developers.openai.com/api/docs/guides/prompt-engineering
- JSON Schema docs: https://json-schema.org/docs
- Local source facts: `safety_video_harness/source_facts.py`
- Local topic extraction: `safety_video_harness/project.py`
- Project schema: `schemas/project_config.schema.json`
- Local skill reference: `references/topic-extractor-reference.md`
- Evaluation rubric: `docs/evaluation-rubrics.md`
- Few-shot examples: `docs/few-shot-examples.md`
