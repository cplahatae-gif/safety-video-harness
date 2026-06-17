from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Final

from PIL import Image, ImageDraw, ImageStat, UnidentifiedImageError

from safety_video_harness.asset_lock import build_asset_lock_manifest
from safety_video_harness.assets import load_reference_assets
from safety_video_harness.errors import HarnessError
from safety_video_harness.image_manual_review import VISUAL_LOCK_SCORE_FIELDS
from safety_video_harness.image_versions import latest_draft_or_none
from safety_video_harness.io import JsonObject, write_json

CONTACT_SHEET_RELATIVE_PATH: Final = Path("qa") / "visual_review" / "image_contact_sheet.png"
VISUAL_REVIEW_DRAFT_PATH: Final = Path("qa") / "image_visual_review_draft.json"
MANUAL_REVIEW_PATH: Final = Path("qa") / "image_manual_reviews.json"


@dataclass(frozen=True, slots=True)
class DraftVisualMetrics:
    scene_id: str
    path: Path
    width: int
    height: int
    mean_rgb: tuple[float, float, float]


def build_visual_review(
    project: Path,
    scenes: list[dict],
    scene_filter: str | None,
    write_review: bool,
    force: bool,
) -> str:
    selected = [scene for scene in scenes if scene_filter is None or scene["id"] == scene_filter]
    if scene_filter is not None and not selected:
        raise HarnessError(f"unknown scene_id: {scene_filter}")
    metrics = [_draft_metrics(project, str(scene["id"])) for scene in selected]
    if any(metric is None for metric in metrics):
        missing = [str(scene["id"]) for scene, metric in zip(selected, metrics, strict=True) if metric is None]
        raise HarnessError("draft image missing for visual QA: " + ", ".join(missing))
    typed_metrics = [metric for metric in metrics if metric is not None]
    contact_sheet = _write_contact_sheet(project, typed_metrics)
    reference_assets = load_reference_assets(project)
    asset_lock = build_asset_lock_manifest(reference_assets)
    reviews = [
        _review_for_metric(metric, typed_metrics[index - 1] if index > 0 else None, asset_lock)
        for index, metric in enumerate(typed_metrics)
    ]
    payload: JsonObject = {
        "reviewer": "local_heuristic_visual_qa",
        "status": "heuristic_requires_human_confirmation_for_semantic_identity",
        "contact_sheet": str(contact_sheet.relative_to(project)),
        "asset_lock_status": str(asset_lock["status"]),
        "reviews": reviews,
    }
    write_json(project / VISUAL_REVIEW_DRAFT_PATH, payload)
    if write_review:
        output = project / MANUAL_REVIEW_PATH
        if output.exists() and not force:
            raise HarnessError(f"{MANUAL_REVIEW_PATH} already exists; use --force to replace it")
        write_json(output, payload)
    return f"visual review prepared {len(reviews)} scene(s); contact sheet: {contact_sheet.relative_to(project)}"


def _draft_metrics(project: Path, scene_id: str) -> DraftVisualMetrics | None:
    draft = latest_draft_or_none(project, scene_id)
    if draft is None:
        return None
    try:
        with Image.open(draft) as image:
            rgb = image.convert("RGB")
            stat = ImageStat.Stat(rgb.resize((1, 1)))
            mean = tuple(float(value) for value in stat.mean)
            return DraftVisualMetrics(scene_id, draft, image.width, image.height, mean)
    except UnidentifiedImageError as exc:
        raise HarnessError(f"draft image is not readable for visual QA: {draft}") from exc


def _write_contact_sheet(project: Path, metrics: list[DraftVisualMetrics]) -> Path:
    output = project / CONTACT_SHEET_RELATIVE_PATH
    output.parent.mkdir(parents=True, exist_ok=True)
    thumb_width = 320
    thumb_height = 180
    label_height = 32
    columns = min(3, max(1, len(metrics)))
    rows = (len(metrics) + columns - 1) // columns
    sheet = Image.new("RGB", (columns * thumb_width, rows * (thumb_height + label_height)), "white")
    draw = ImageDraw.Draw(sheet)
    for index, metric in enumerate(metrics):
        row = index // columns
        column = index % columns
        x = column * thumb_width
        y = row * (thumb_height + label_height)
        with Image.open(metric.path) as image:
            thumb = image.convert("RGB")
            thumb.thumbnail((thumb_width, thumb_height))
            sheet.paste(thumb, (x, y))
        draw.text((x + 8, y + thumb_height + 8), f"{metric.scene_id} | {metric.width}x{metric.height}", fill=(20, 24, 28))
    sheet.save(output)
    return output


def _review_for_metric(
    metric: DraftVisualMetrics,
    previous: DraftVisualMetrics | None,
    asset_lock: dict,
) -> JsonObject:
    locked = str(asset_lock["status"]) == "production_locked"
    delta = _color_delta(metric, previous)
    stable = previous is None or delta <= 60
    scores = {
        "floor_lane_consistency_score": 4 if stable else 3,
        "background_consistency_score": 4 if stable else 3,
        "character_identity_lock_score": 4 if locked else 3,
        "vehicle_geometry_lock_score": 4 if locked else 3,
        "hazard_zone_consistency_score": 4 if locked and stable else 3,
    }
    blockers = [
        f"{field} below minimum 4: {score}"
        for field, score in scores.items()
        if score < 4
    ]
    if not locked:
        blockers.append("asset lock is not production_locked; cast/equipment/space references are required")
    if not stable:
        blockers.append(f"adjacent scene color/layout drift too high: {delta:.2f}")
    return {
        "scene_id": metric.scene_id,
        **scores,
        "blocking_issues": blockers,
        "reviewer": "local_heuristic_visual_qa",
        "notes": (
            "Local heuristic checks image readability, contact-sheet evidence, asset-lock coverage, and coarse adjacent-frame color/layout drift. "
            "It does not replace human or model-based semantic review for gaze, exact identity, or safety meaning."
        ),
        "reviewed_asset": str(metric.path),
        "visual_lock_fields": list(VISUAL_LOCK_SCORE_FIELDS),
        "adjacent_color_delta": round(delta, 2),
    }


def _color_delta(metric: DraftVisualMetrics, previous: DraftVisualMetrics | None) -> float:
    if previous is None:
        return 0
    return sum(abs(current - prior) for current, prior in zip(metric.mean_rgb, previous.mean_rgb, strict=True))
