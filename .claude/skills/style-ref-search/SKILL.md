---
name: style-ref-search
description: 스타일 레퍼런스 이미지 후보를 검색·수집할 때 사용. 레퍼런스 검색, 스타일 후보, search_references 요청 시 트리거. 승인 전 후보는 프롬프트에 반영하지 않는다.
---

# style-ref-search

Collect style reference candidates without automatically using downloaded assets.

Store search queries and candidate metadata. Only approved references can affect style DNA.

## References

- Reference index: `docs/generative-media-reference-index.md`
- OpenAI Image generation guide: https://developers.openai.com/api/docs/guides/image-generation
- OpenAI Images and vision guide: https://developers.openai.com/api/docs/guides/images-vision
- Local style guide catalog: `style-guides/README.md`
- Local reference profiling: `safety_video_harness/reference_profile.py`
- Approved reference folders: `model/`, `product/`, `ref/approved/`
- Local skill reference: `references/style-ref-search-reference.md`
- Evaluation rubric: `docs/evaluation-rubrics.md`
- Few-shot examples: `docs/few-shot-examples.md`
