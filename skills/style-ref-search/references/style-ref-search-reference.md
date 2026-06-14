# Style Reference Search Reference

Source links:
- OpenAI Image generation: https://developers.openai.com/api/docs/guides/image-generation
- OpenAI Images and vision: https://developers.openai.com/api/docs/guides/images-vision
- Central source list: `docs/reference-sources.md`

Checked: 2026-06-12

## Local Reference Notes

- OpenAI image/vision guidance supports using visual inputs for understanding and generation, but references should be converted into explicit style and content notes before they influence prompts.
- Reference assets need role labels. A person reference, work-situation reference, space reference, camera reference, and style reference should not be mixed together as one undifferentiated pile.
- Approved references should become prompt constraints only after the user or harness marks them active. Candidate references remain inert to avoid accidental style drift or rights problems.
- Exact logos, faces, and protected brand identifiers should not be copied into generated safety images unless the user has explicit rights and approval.
- Manual `.md` descriptions beside images are valuable because they make visual intent reusable even when live vision analysis is unavailable.
- Candidate references should be stored separately from approved references. The harness must never silently consume everything in a folder.
- For each approved image, record why it is approved and which prompt fields it may affect: identity, pose, PPE, machinery, background, color, camera, lighting, or illustration style.
- If a reference is only for style, do not copy its subject matter. If a reference is only for work situation, do not copy its art style.
- When external search is used, preserve search query, source URL, date checked, and a short note on suitability.
- For industrial safety projects, prioritize references with clear PPE, realistic equipment scale, readable site layout, and visible worker-vehicle separation.

## Use In This Harness

This skill collects reference candidates but does not make them active. Only approved references and adjacent `.md`
descriptions can affect prompts.

## Operational Rules

- Separate candidates from approved references.
- Ask the user to classify references: person, work, space, style, camera, lighting, equipment, PPE.
- Write manual descriptions beside images whenever possible.
- Do not copy logos, faces, or protected brand identifiers into generated outputs.
- Treat `ref/candidates` as inert until approval.

## Output Expectations

- Search output should include query, source, role guess, and approval status.
- Prompt contracts should consume only approved assets.
