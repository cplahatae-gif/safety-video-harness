from __future__ import annotations

from pathlib import Path

from safety_video_harness.io import JsonObject
from safety_video_harness.layout import PROJECT_LAYOUT_VERSION
from safety_video_harness.style_guides import default_style_guide_id, reference_intake_defaults, style_interview_defaults


def project_config(project: Path, name: str) -> JsonObject:
    style_guide_id = default_style_guide_id()
    return {
        "schema_version": "2.1",
        "project_layout_version": PROJECT_LAYOUT_VERSION,
        "project_type": "safety",
        "project_name": name,
        "slug": project.name,
        "topic": "",
        "selected_topic_id": "",
        "topic_selection_mode": "",
        "target_seconds": 30,
        "target_duration_sec": 30,
        "image_density": "normal",
        "style_guide_id": style_guide_id,
        "reference_intake": reference_intake_defaults(),
        "style_interview": style_interview_defaults(style_guide_id),
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
        "tools": {
            "image": "codex_builtin_imagegen",
            "image_fallback": "explicit_openai_api_or_cli",
            "video": "higgsfield_cli_seedance",
        },
    }


def approvals() -> JsonObject:
    return {
        "gates": {
            "storyboard": {
                "approved": False,
                "approved_by": "",
                "approved_at": "",
                "approved_items": [],
                "notes": "",
            },
            "image_to_video": {
                "approved": False,
                "approved_by": "",
                "approved_at": "",
                "approved_items": [],
                "cost_disclosure": {
                    "estimated_credits": 0,
                    "clip_count": 0,
                    "regeneration_risk": "",
                },
                "notes": "",
            },
        }
    }


def self_score() -> JsonObject:
    return {
        "turn": 0,
        "scores": {"functional": 0, "technical": 0, "completeness": 0, "harness": 0},
        "p0_issues": [],
        "p1_issues": [],
    }


def plan_template(name: str) -> str:
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


def agents_template() -> str:
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
