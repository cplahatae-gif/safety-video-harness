from __future__ import annotations

import re


def blocker_signature(stage: str, item_id: str, issue: str) -> str:
    issue_text = issue.lower()
    category = _category(issue_text)
    slug = _slug(issue_text)
    return f"{stage}:{item_id}:{category}:{slug}"


def _category(issue_text: str) -> str:
    if "missing draft image" in issue_text:
        return "technical"
    if "pillow" in issue_text or "readable image" in issue_text or "aspect ratio" in issue_text:
        return "technical"
    if "gaze" in issue_text or "시선" in issue_text or "target" in issue_text:
        return "gaze_motivation"
    if "identity" in issue_text or "character" in issue_text or "worker" in issue_text:
        return "identity_consistency"
    if "story" in issue_text or "storyboard" in issue_text:
        return "story_match"
    if "source" in issue_text or "citation" in issue_text:
        return "source_grounding"
    return "general"


def _slug(issue_text: str) -> str:
    replacements = {
        "missing draft image": "missing_draft_image",
        "gaze target is unclear": "unclear_target",
        "worker identity changes between frames": "worker_identity_changes_between_frames",
    }
    if issue_text in replacements:
        return replacements[issue_text]
    normalized = re.sub(r"[^a-z0-9가-힣]+", "_", issue_text).strip("_")
    return normalized[:80] or "unknown"
