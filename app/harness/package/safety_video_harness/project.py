from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from safety_video_harness.errors import HarnessError
from safety_video_harness.io import ensure_dirs, read_json, sha256_file, write_json
from safety_video_harness.layout import CANONICAL_PROJECT_DIRS, LayoutKey, layout_for_project
from safety_video_harness.project_defaults import (
    agents_template,
    approvals,
    plan_template,
    project_config,
    self_score,
)
from safety_video_harness.project_handoff import write_project_handoff
from safety_video_harness.source_facts import facts_for_sources, topics_from_facts
from safety_video_harness.source_rendering import extract_pptx_text_assets, extract_rendered_assets
from safety_video_harness.style_guides import default_style_guide_id, reference_intake_defaults, style_interview_defaults

PROJECT_DIRS = list(CANONICAL_PROJECT_DIRS)


def init_project(project: Path, name: str) -> str:
    if project.exists():
        raise HarnessError(f"Project already exists: {project}")
    layout = layout_for_project(project)
    ensure_dirs(project, PROJECT_DIRS)
    (project / "PLAN.md").write_text(plan_template(name), encoding="utf-8")
    (project / "AGENTS.md").write_text(agents_template(), encoding="utf-8")
    write_project_handoff(project, name)
    write_json(project / "project_config.json", project_config(project, name))
    write_json(layout.write_path(LayoutKey.SOURCE_REGISTRY), {"sources": []})
    write_json(layout.write_path(LayoutKey.SOURCE_TOPICS), {"topics": []})
    write_json(layout.write_path(LayoutKey.SOURCE_FACTS), {"facts": []})
    write_json(layout.write_path(LayoutKey.REFS_STYLE) / "style_dna.json", {"style": {}, "negative_constraints": []})
    write_json(layout.write_path(LayoutKey.QA_APPROVALS), approvals())
    write_json(layout.write_path(LayoutKey.QA_STATE) / "self_score.json", self_score())
    (layout.write_path(LayoutKey.QA_STATE) / "turn_count").write_text("0\n", encoding="utf-8")
    (layout.write_path(LayoutKey.QA_STATE) / "errors.jsonl").write_text("", encoding="utf-8")
    return f"created project {project}"


def register_source(project: Path, source: Path) -> str:
    if not source.exists():
        raise HarnessError(f"source does not exist: {source}")
    layout = layout_for_project(project)
    sources_path = layout.read_path(LayoutKey.SOURCE_REGISTRY)
    sources = read_json(sources_path)
    entries = list(sources.get("sources", []))
    source_id = f"src-{len(entries) + 1:03d}"
    entry = {
        "source_id": source_id,
        "path": str(source),
        "type": source.suffix.removeprefix(".").lower() or "file",
        "sha256": sha256_file(source),
        "page_count": 0,
        "rendered_assets": [],
        "registered_at": datetime.now(UTC).isoformat(),
    }
    entries.append(entry)
    write_json(sources_path, {"sources": entries})
    return f"registered {source_id}"


def render_sources(project: Path, dry_run: bool, mode: str = "media_extract") -> str:
    layout = layout_for_project(project)
    sources = read_json(layout.read_path(LayoutKey.SOURCE_REGISTRY))
    entries = list(sources.get("sources", []))
    rendered_dir = layout.read_path(LayoutKey.SOURCE_RENDERED)
    rendered_dir.mkdir(parents=True, exist_ok=True)
    for index, entry in enumerate(entries, start=1):
        assets, rendering_mode, warning = extract_rendered_assets(rendered_dir, entry, index, mode)
        text_assets, text_warning = extract_pptx_text_assets(rendered_dir, entry)
        entry["rendered_assets"] = [str(asset) for asset in assets]
        entry["extracted_text_assets"] = [str(asset) for asset in text_assets]
        entry["page_count"] = len(assets)
        entry["rendering_mode"] = rendering_mode
        entry["render_warning"] = "; ".join(item for item in [warning, text_warning] if item)
    write_json(layout.read_path(LayoutKey.SOURCE_REGISTRY), {"sources": entries})
    run_mode = "dry-run" if dry_run else "rendered"
    return f"{run_mode} rendered {len(entries)} source(s)"


def extract_topics(project: Path) -> str:
    layout = layout_for_project(project)
    sources = read_json(layout.read_path(LayoutKey.SOURCE_REGISTRY))
    source_entries = list(sources.get("sources", []))
    facts = facts_for_sources(source_entries)
    citations = [
        {"source_id": fact["source_id"], "page_or_slide": fact["page_or_slide"], "claim": fact["claim"]}
        for fact in facts
    ]
    topics = topics_from_facts(citations)
    write_json(layout.read_path(LayoutKey.SOURCE_TOPICS), {"topics": topics})
    write_json(layout.read_path(LayoutKey.SOURCE_FACTS), {"facts": facts})
    return f"extracted {len(topics)} topic(s)"


def apply_default_intake(project: Path) -> str:
    layout = layout_for_project(project)
    config = read_json(project / "project_config.json")
    topics = read_json(layout.read_path(LayoutKey.SOURCE_TOPICS))
    topic_entries = list(topics.get("topics", []))
    if topic_entries:
        config["topic"] = topic_entries[0]["title_ko"]
        config["selected_topic_id"] = topic_entries[0]["topic_id"]
        config["topic_selection_mode"] = "default"
    style_guide_id = str(config.get("style_guide_id", default_style_guide_id()))
    config["style_guide_id"] = style_guide_id
    config["reference_intake"] = reference_intake_defaults()
    config["style_interview"] = style_interview_defaults(style_guide_id)
    write_json(project / "project_config.json", config)
    return "applied default intake"


def apply_intake(
    project: Path,
    target_seconds: int | None = None,
    image_density: str | None = None,
    style_guide_id: str | None = None,
    aspect_ratio: str | None = None,
    resolution: str | None = None,
    text_delivery: str | None = None,
    approval_scope: str | None = None,
    reference_notes: str | None = None,
) -> str:
    config = read_json(project / "project_config.json")
    if target_seconds is not None:
        config["target_seconds"] = target_seconds
        config["target_duration_sec"] = target_seconds
    if image_density is not None:
        config["image_density"] = image_density
    if style_guide_id is not None:
        config["style_guide_id"] = style_guide_id
    if aspect_ratio is not None:
        config["aspect_ratio"] = aspect_ratio
    if resolution is not None:
        config["resolution"] = resolution
    if text_delivery is not None:
        config["text_delivery"] = text_delivery
    if approval_scope is not None:
        config["approval_scope"] = approval_scope
    config["reference_intake"] = reference_intake_defaults()
    if reference_notes is not None:
        reference_intake = dict(config["reference_intake"])
        reference_intake["operator_notes"] = reference_notes
        config["reference_intake"] = reference_intake
    style_id = str(config.get("style_guide_id", default_style_guide_id()))
    config["style_interview"] = style_interview_defaults(style_id)
    write_json(project / "project_config.json", config)
    return "applied intake"


def select_topic(project: Path, topic_id: str) -> str:
    layout = layout_for_project(project)
    topics = list(read_json(layout.read_path(LayoutKey.SOURCE_TOPICS)).get("topics", []))
    selected = next((topic for topic in topics if topic.get("topic_id") == topic_id), None)
    if selected is None:
        raise HarnessError(f"unknown topic_id: {topic_id}")
    config = read_json(project / "project_config.json")
    config["topic"] = selected["title_ko"]
    config["selected_topic_id"] = topic_id
    config["topic_selection_mode"] = "explicit"
    write_json(project / "project_config.json", config)
    return f"selected topic {topic_id}"


def search_references(project: Path, dry_run: bool) -> str:
    layout = layout_for_project(project)
    queries = {
        "queries": [
            "animated industrial safety training video",
            "construction equipment near miss training animation",
            "산업안전 애니메이션 교육 영상",
        ],
        "dry_run": dry_run,
    }
    write_json(layout.write_path(LayoutKey.REFS_CANDIDATES) / "search_queries.json", queries)
    return "prepared reference search queries"


def extract_style_dna(project: Path) -> str:
    layout = layout_for_project(project)
    config = read_json(project / "project_config.json")
    style_guide_id = str(config.get("style_guide_id", default_style_guide_id()))
    style = {
        "selected_style_guide_id": style_guide_id,
        "style": {
            "palette": "clear industrial safety colors",
            "camera": "wide educational framing",
            "texture": "clean instructional animation",
            "guide": style_guide_id,
        },
        "negative_constraints": [
            "no gore",
            "no impact frame",
            "no text in generated images",
            "no unsafe behavior shown as successful",
        ],
    }
    write_json(layout.write_path(LayoutKey.REFS_STYLE) / "style_dna.json", style)
    return "extracted style DNA"
