from __future__ import annotations

import sys


MISSION_ANCHOR = "\n".join(
    (
        "Safety Video Harness Mission Anchor",
        "",
        "You are working on a plugin-style harness for Korean industrial safety training videos.",
        "",
        "Non-negotiables:",
        "- No live imagegen, live Seedance, live TTS, or paid calls unless explicitly approved.",
        "- No narration/TTS in active scope; use subtitles, overlays, or text cards.",
        "- Start with an intake interview before creating storyboard, images, or video.",
        "- Ask for source files, topic, target seconds, image density, reference images, selected style guide, aspect ratio, and approval scope.",
        "- Reference question comes first; style choice comes next with 5 choices from style-guides/catalog.json.",
        "- Storyboard first. Image generation second. Video generation last.",
        "- QA uses parallel role evaluators, Arbiter consensus, critical veto, and evidence bundles.",
        "- Image RALPH is early-stopping max 20; the same blocker 3 times escalates upstream.",
        "- Video failures are propose-only; never auto-regenerate paid video.",
        "- Preserve evidence under qa/, evidence/, and llm-wiki/.",
        "",
    )
)


def main() -> int:
    print(MISSION_ANCHOR)
    return 0


if __name__ == "__main__":
    sys.exit(main())
