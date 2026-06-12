---
name: topic-extractor
description: 렌더링된 교육자료(PPTX/SOP)에서 안전교육 영상 주제 후보를 추출할 때 사용. 주제 추출, extract_topics, 교육자료 분석 요청 시 트리거.
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
