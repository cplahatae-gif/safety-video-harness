from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from safety_video_harness.errors import HarnessError
from safety_video_harness.io import ensure_dirs, read_json, sha256_file, write_json
from safety_video_harness.project_handoff import write_project_handoff
from safety_video_harness.source_facts import facts_for_sources, topics_from_facts
from safety_video_harness.source_rendering import extract_pptx_text_assets, extract_rendered_assets
from safety_video_harness.style_guides import default_style_guide_id, reference_intake_defaults, style_interview_defaults

PROJECT_DIRS = [
    "sources/raw",
    "sources/rendered",
    "model/cast",
    "model/ppe",
    "product/equipment",
    "ref/candidates",
    "ref/approved",
    "ref/approved/person",
    "ref/approved/work",
    "ref/approved/space",
    "ref/approved/style",
    "ref/approved/camera",
    "ref/approved/lighting",
    "style",
    "asset-lock",
    "storyboard/versions",
    "prompts",
    "images/draft",
    "images/approved",
    "images/rejected",
    "video/clips",
    "video/sampled_frames",
    "video/inspection",
    "audio",
    "subtitles",
    "output",
    "qa",
    "evidence",
    ".harness",
]


def init_project(project: Path, name: str) -> str:
    if project.exists():
        raise HarnessError(f"Project already exists: {project}")
    ensure_dirs(project, PROJECT_DIRS)
    (project / "PLAN.md").write_text(_plan_template(name), encoding="utf-8")
    (project / "AGENTS.md").write_text(_agents_template(), encoding="utf-8")
    write_project_handoff(project, name)
    write_json(project / "project_config.json", _project_config(project, name))
    write_json(project / "sources" / "sources.json", {"sources": []})
    write_json(project / "sources" / "extracted_topics.json", {"topics": []})
    write_json(project / "sources" / "source_facts.json", {"facts": []})
    write_json(project / "style" / "style_dna.json", {"style": {}, "negative_constraints": []})
    write_json(project / "approvals.json", _approvals())
    write_json(project / ".harness" / "self_score.json", _self_score())
    (project / ".harness" / "turn_count").write_text("0\n", encoding="utf-8")
    (project / ".harness" / "errors.jsonl").write_text("", encoding="utf-8")
    return f"created project {project}"


def register_source(project: Path, source: Path) -> str:
    if not source.exists():
        raise HarnessError(f"source does not exist: {source}")
    sources_path = project / "sources" / "sources.json"
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
    sources = read_json(project / "sources" / "sources.json")
    entries = list(sources.get("sources", []))
    rendered_dir = project / "sources" / "rendered"
    rendered_dir.mkdir(parents=True, exist_ok=True)
    for index, entry in enumerate(entries, start=1):
        assets, rendering_mode, warning = extract_rendered_assets(rendered_dir, entry, index, mode)
        text_assets, text_warning = extract_pptx_text_assets(rendered_dir, entry)
        entry["rendered_assets"] = [str(asset) for asset in assets]
        entry["extracted_text_assets"] = [str(asset) for asset in text_assets]
        entry["page_count"] = len(assets)
        entry["rendering_mode"] = rendering_mode
        entry["render_warning"] = "; ".join(item for item in [warning, text_warning] if item)
    write_json(project / "sources" / "sources.json", {"sources": entries})
    run_mode = "dry-run" if dry_run else "rendered"
    return f"{run_mode} rendered {len(entries)} source(s)"


def extract_topics(project: Path) -> str:
    sources = read_json(project / "sources" / "sources.json")
    source_entries = list(sources.get("sources", []))
    facts = facts_for_sources(source_entries)
    citations = [
        {"source_id": fact["source_id"], "page_or_slide": fact["page_or_slide"], "claim": fact["claim"]}
        for fact in facts
    ]
    topics = topics_from_facts(citations)
    write_json(project / "sources" / "extracted_topics.json", {"topics": topics})
    write_json(project / "sources" / "source_facts.json", {"facts": facts})
    return f"extracted {len(topics)} topic(s)"


def apply_default_intake(project: Path) -> str:
    config = read_json(project / "project_config.json")
    topics = read_json(project / "sources" / "extracted_topics.json")
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
    topics = list(read_json(project / "sources" / "extracted_topics.json").get("topics", []))
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
    queries = {
        "queries": [
            "animated industrial safety training video",
            "construction equipment near miss training animation",
            "산업안전 애니메이션 교육 영상",
        ],
        "dry_run": dry_run,
    }
    write_json(project / "ref" / "candidates" / "search_queries.json", queries)
    return "prepared reference search queries"


def extract_style_dna(project: Path) -> str:
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
    write_json(project / "style" / "style_dna.json", style)
    return "extracted style DNA"


def _project_config(project: Path, name: str) -> dict:
    return {
        "schema_version": "2.1",
        "project_type": "safety",
        "project_name": name,
        "slug": project.name,
        "topic": "",
        "selected_topic_id": "",
        "topic_selection_mode": "",
        "target_seconds": 30,
        "target_duration_sec": 30,
        "image_density": "normal",
        "style_guide_id": default_style_guide_id(),
        "reference_intake": reference_intake_defaults(),
        "style_interview": style_interview_defaults(default_style_guide_id()),
        "duration_policy": "default_30_extend_with_approval",
        "seconds_per_clip": 5,
        "aspect_ratio": "16:9",
        "resolution": "1080p",
        "chain_policy": "hybrid",
        "production_consistency_policy": {
            "text_only_multi_frame_production_allowed": False,
            "independent_text_to_image_generation": "draft_exploration_only",
            "required_before_final_keyframes": [
                "fixed cast reference or Soul ID source",
                "fixed equipment references",
                "fixed space/background plate",
                "reference/edit or compositing derivation for later keyframes",
            ],
            "seedance_requires_start_end_keyframes": True,
            "seedance_reference_media_pack_recommended": True,
        },
        "source_policy": "company_approved_or_generated",
        "external_upload_allowed": False,
        "reference_policy": "approved_candidates_only",
        "safety_boundary": "near_miss_prevention_only",
        "audio_policy": "no_narration_video_only",
        "live_generation_requires_approval": True,
        "credit_budget": {"total": 0, "estimated": 0, "spent": 0, "unit": "credits"},
        "tools": {"image": "codex_builtin_imagegen", "image_fallback": "explicit_openai_api_or_cli", "video": "higgsfield_cli_seedance"},
    }




def _approvals() -> dict:
    return {
        "gates": {
            "storyboard": {"approved": False, "approved_by": "", "approved_at": "", "approved_items": [], "notes": ""},
            "image_to_video": {
                "approved": False,
                "approved_by": "",
                "approved_at": "",
                "approved_items": [],
                "cost_disclosure": {"estimated_credits": 0, "clip_count": 0, "regeneration_risk": ""},
                "notes": "",
            },
        }
    }


def _self_score() -> dict:
    return {"turn": 0, "scores": {"functional": 0, "technical": 0, "completeness": 0, "harness": 0}, "p0_issues": [], "p1_issues": []}


def _plan_template(name: str) -> str:
    return "\n".join(
        [
            "# PLAN",
            "",
            "## Mission",
            f"Create a safety training video project for {name}.",
            "",
            "## End Conditions",
            "- all_l0_pass",
            "- gate1_ready",
            "- dry_run_chain_pass",
            "- sentinel",
            "",
            "## Budgets",
            "- max_turns: 20",
            "- paid_calls_in_loop: 0",
            "",
        ]
    )


def _agents_template() -> str:
    return "\n".join(
        [
            "# Safety Video Harness Agent Rules",
            "",
            "- Do not run live image or video generation without approval.",
            "- Do not create safety claims without source citations.",
            "- Do not overwrite approved artifacts.",
            "- Use dry-run before any live generation.",
            "",
        ]
    )
