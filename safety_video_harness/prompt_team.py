from __future__ import annotations

from pathlib import Path
from typing import Final

from safety_video_harness.io import read_json, write_json
from safety_video_harness.style_guides import selected_style_guide_id

REFERENCE_LINKS: Final[list[dict[str, str]]] = [
    {
        "name": "OpenAI Image generation guide",
        "url": "https://developers.openai.com/api/docs/guides/image-generation",
        "use": "image generation modes, reference-image workflows, output options, limitations",
    },
    {
        "name": "OpenAI Video generation guide",
        "url": "https://developers.openai.com/api/docs/guides/video-generation",
        "use": "image references, character reuse, video continuity concepts",
    },
    {
        "name": "Higgsfield CLI/MCP",
        "url": "https://higgsfield.ai/cli",
        "use": "CLI auth, model catalog, generate/upload commands, credit-based video generation",
    },
    {
        "name": "Local Codex imagegen skill",
        "url": "$CODEX_HOME/skills/.system/imagegen/SKILL.md",
        "use": "built-in imagegen workflow and save-path policy",
    },
]


def ensure_image_prompt_team_plan(project: Path) -> dict:
    plan_path = project / "prompts" / "image_prompt_team_plan.json"
    if plan_path.exists():
        return read_json(plan_path)
    plan = build_image_prompt_team_plan(project)
    write_json(plan_path, plan)
    return plan


def build_image_prompt_team_plan(project: Path) -> dict:
    scenes = read_json(project / "storyboard" / "scenes.json")
    scene_items = list(scenes.get("scenes", []))
    keyframe_count = int(scenes.get("keyframe_count", len(scene_items)))
    style_guide_id = selected_style_guide_id(project)
    briefs = _scene_prompt_briefs(scene_items, keyframe_count)
    return {
        "schema_version": "1.0",
        "purpose": "pre-image-generation production team plan",
        "style_guide_id": style_guide_id,
        "agent_team": {
            "lead_style_agent": _lead_style_agent(style_guide_id),
            "scene_prompt_agents": briefs,
            "visual_director_arbiter": _visual_director_arbiter(),
        },
        "generation_policy": {
            "parallelize": "scene prompt drafting and review only",
            "centralize": "final imagegen execution through one coordinator",
            "reason": "parallel image generation can break identity, PPE, vehicle, camera, and style continuity",
        },
        "references": REFERENCE_LINKS,
    }


def prompt_team_prompt_block(project: Path) -> str:
    plan_path = project / "prompts" / "image_prompt_team_plan.json"
    if not plan_path.exists():
        return "Image prompt production team plan: not prepared."
    plan = read_json(plan_path)
    lead = dict(dict(plan["agent_team"])["lead_style_agent"])
    director = dict(dict(plan["agent_team"])["visual_director_arbiter"])
    return "\n".join(
        [
            "Image prompt production team preflight:",
            f"- Lead style agent: {lead['mission']}",
            f"- Style guide id: {plan['style_guide_id']}",
            "- Scene prompt agents draft scene-specific briefs; they do not directly generate images.",
            f"- Visual director decision gate: {director['decision_contract']}",
            "- Global rule: first keyframe anchors all later scene identity, PPE, vehicle, site, camera, and rendering locks.",
            "- Generation policy: use one imagegen coordinator after prompt integration; do not let parallel agents generate independent final images.",
        ]
    )


def _lead_style_agent(style_guide_id: str) -> dict:
    return {
        "agent_file": "agents/lead-style-agent/AGENT.md",
        "mission": "turn sc01 into style, character, vehicle, space, camera, rendering, and negative bibles",
        "style_guide_id": style_guide_id,
        "output_contract": [
            "character_bible",
            "vehicle_bible",
            "space_bible",
            "camera_bible",
            "rendering_bible",
            "negative_bible",
        ],
        "hard_locks": [
            "same worker/signal/supervisor PPE colors",
            "same white BCT and yellow dump truck silhouettes",
            "same green pedestrian route and red/orange hazard zone",
            "same precision industrial webtoon linework and cel shading",
        ],
    }


def _scene_prompt_briefs(scene_items: list[dict], keyframe_count: int) -> list[dict]:
    briefs: list[dict] = []
    total = len(scene_items)
    for index, scene in enumerate(scene_items):
        briefs.append(_scene_prompt_brief(scene, index, total))
    if keyframe_count > total and scene_items:
        briefs.append(
            {
                "scene_id": f"sc{keyframe_count:02d}",
                "agent_file": "agents/scene-prompt-agent/AGENT.md",
                "scene_role": "final controlled end keyframe",
                "current_action": "resolve the safety story with vehicles controlled and workers outside hazard zones",
                "previous_continuity": str(scene_items[-1].get("visual_action_ko", "")),
                "next_setup": "no next scene; preserve a stable ending for the final video clip",
                "must_preserve": _must_preserve(),
                "must_avoid": _must_avoid(),
            }
        )
    return briefs


def _scene_prompt_brief(scene: dict, index: int, total: int) -> dict:
    return {
        "scene_id": str(scene["id"]),
        "agent_file": "agents/scene-prompt-agent/AGENT.md",
        "scene_role": f"keyframe {index + 1} of {total}",
        "current_action": str(scene.get("visual_action_ko", scene.get("educational_goal_ko", ""))),
        "previous_continuity": "opening frame" if index == 0 else "continue directly from the prior keyframe",
        "next_setup": "prepare the next prevention beat without a visual jump",
        "visible_cast_rule": "include only people needed to explain the current safety action",
        "gaze_rule": "every visible person must look at a visible hazard, signal, route, mirror, or camera display",
        "must_preserve": _must_preserve(),
        "must_avoid": _must_avoid(),
    }


def _visual_director_arbiter() -> dict:
    return {
        "agent_file": "agents/visual-director-arbiter/AGENT.md",
        "mission": "integrate scene prompt briefs before image generation",
        "decision_contract": "ready_for_generation | revise_scene_prompt | revise_style_bible | revise_storyboard",
        "critical_checks": [
            "cast count and roles do not drift",
            "PPE colors and vehicle shapes remain stable",
            "gaze targets are visible inside the frame",
            "hazard zone, pedestrian route, and vehicle lane remain spatially coherent",
            "no exact Korean or English text is requested inside keyframes",
        ],
        "deferred_work": "parallel consistency-evaluation agents can be added later",
    }


def _must_preserve() -> list[str]:
    return [
        "selected reusable style guide",
        "lead style bible",
        "same PPE colors",
        "same BCT and dump truck identity",
        "same plant entrance and lane layout",
        "previous and next scene continuity",
    ]


def _must_avoid() -> list[str]:
    return [
        "standalone poster composition",
        "unmotivated gaze",
        "random extra workers",
        "sudden person disappearance",
        "readable generated text",
        "logos, collision impact, injury, or gore",
    ]
