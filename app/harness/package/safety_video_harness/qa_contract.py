from __future__ import annotations

from pathlib import Path

from safety_video_harness.io import JsonObject

RUBRIC_SOURCE = "docs/evaluation-rubrics.md"
FEW_SHOT_SOURCE = "docs/few-shot-examples.md"
HIGGSFIELD_SOURCE = "docs/higgsfield-seedance-local-reference.md"


def guide_sources(include_higgsfield: bool = False) -> JsonObject:
    sources: JsonObject = {
        "rubric_source": RUBRIC_SOURCE,
        "few_shot_source": FEW_SHOT_SOURCE,
    }
    if include_higgsfield:
        sources["higgsfield_seedance_source"] = HIGGSFIELD_SOURCE
    return sources


def blocker_categories(issues: list[str]) -> list[JsonObject]:
    return [{"issue": issue, "category": blocker_category(issue)} for issue in issues]


def critical_blockers(issues: list[str]) -> list[str]:
    return [issue for issue in issues if _is_critical(issue)]


def artifact_path(project: Path, path: Path | None, fallback: str) -> str:
    if path is None:
        return fallback
    try:
        return str(path.relative_to(project))
    except ValueError:
        return str(path)


def blocker_category(issue: str) -> str:
    normalized = issue.lower()
    if "source citation" in normalized or "unsupported" in normalized:
        return "source_grounding"
    if "missing draft" in normalized or "required" in normalized or "expected" in normalized:
        return "missing_artifact"
    if "gaze" in normalized or "look" in normalized:
        return "gaze_motivation"
    if "appear" in normalized or "disappear" in normalized or "continuity" in normalized:
        return "continuity"
    if "duration" in normalized or "resolution" in normalized or "metadata" in normalized:
        return "technical"
    if "narration" in normalized or "subtitle" in normalized or "overlay" in normalized:
        return "text_delivery"
    if "collision" in normalized or "injury" in normalized or "unsafe" in normalized:
        return "safety"
    return "quality"


def _is_critical(issue: str) -> bool:
    category = blocker_category(issue)
    return category in {
        "source_grounding",
        "missing_artifact",
        "gaze_motivation",
        "continuity",
        "safety",
    }

