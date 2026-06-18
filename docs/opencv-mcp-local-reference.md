# OpenCV MCP Local Reference

Checked: 2026-06-18

Source: https://github.com/GongRzhe/opencv-mcp-server

## Purpose In This Harness

OpenCV MCP is the preferred no-cost first-pass visual inspection layer for generated safety-video keyframes.
It is not a semantic vision model. Use it before any paid or external vision service to catch local,
measurable consistency problems.

## Codex MCP Registration

Configured in `~/.codex/config.toml`:

```toml
[mcp_servers.opencv]
command = "uvx"
args = ["opencv-mcp-server"]
```

Restart Codex after this configuration change so the MCP tools are loaded into the session.

## Use In The Algorithm

Run order:

1. Generate scene keyframes into `images/draft/scNN_vNNN.png`.
2. Build `qa/visual_review/image_contact_sheet.png`.
3. Use OpenCV MCP/local CV checks for:
   - image dimensions and readability
   - coarse color drift across adjacent keyframes
   - lane/hazard-zone color region stability
   - background/layout drift
   - contact-sheet comparison artifacts
4. Write findings into `qa/image_visual_review_draft.json`.
5. Promote or merge findings into `qa/image_manual_reviews.json`.
6. Run `scripts/validate_images.py`.
7. If blockers remain, RALPH writes a critique block and regenerates only blocked scenes.

## What OpenCV MCP Is Good At

- Floor, lane, and hazard-zone color drift.
- Major background/composition drift.
- Contact-sheet generation and frame preprocessing.
- Cropping regions for later human or LLM review.
- Video frame sampling/preprocessing when the pipeline reaches Seedance QA.

## What OpenCV MCP Is Not Enough For

- Whether a worker is exactly the same person.
- Whether gaze is semantically motivated.
- Whether the frame teaches the intended safety lesson.
- Whether a new character is justified by the storyboard.

Those require human review or a vision-language model. In this harness, OpenCV MCP is the cost-saving
pre-filter, not the final semantic judge.

## Safety And Cost Policy

- Local OpenCV checks are allowed before Gate 2 because they do not upload project media.
- Do not replace `qa/image_manual_reviews.json` with OpenCV metadata alone.
- Paid/external vision services still require `external_upload_allowed=true` and explicit user approval.
