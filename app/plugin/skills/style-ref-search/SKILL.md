---
name: style-ref-search
description: Collect, classify, and approve style/reference candidates for safety-video projects without allowing unapproved assets to affect prompt style DNA.
---

# style-ref-search

Collect style reference candidates without automatically using downloaded assets.

Store search queries and candidate metadata. Only approved references can affect style DNA.

## References

- Reference index: `docs/generative-media-reference-index.md`
- OpenAI Image generation guide: https://developers.openai.com/api/docs/guides/image-generation
- OpenAI Images and vision guide: https://developers.openai.com/api/docs/guides/images-vision
- Local style guide catalog: `references/style/README.md`
- Local reference profiling: `safety_video_harness/reference_profile.py`
- Approved reference folders: `model/`, `product/`, `ref/approved/`
- Local skill reference: `references/style-ref-search-reference.md`
- Evaluation rubric: `docs/evaluation-rubrics.md`
- Few-shot examples: `docs/few-shot-examples.md`
