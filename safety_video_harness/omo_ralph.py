from __future__ import annotations

from pathlib import Path

from safety_video_harness.errors import HarnessError
from safety_video_harness.io import JsonObject, read_json, write_json


def build_omo_image_ralph_plan(project: Path, scene_filter: str | None = None) -> str:
    loop_path = project / "qa" / "image_qa_loop.json"
    if not loop_path.exists():
        raise HarnessError("image_qa_loop.json is missing; run validate_images.py first")
    loop = read_json(loop_path)
    target_scenes = _target_scenes(loop, scene_filter)
    next_action = str(loop.get("next_action", ""))
    plan: JsonObject = {
        "execution_model": "omo_ulw_loop_as_orchestrator",
        "decision_source": "harness_internal_qa_only",
        "target_scenes": target_scenes,
        "next_omo_action": _next_omo_action(loop, next_action),
        "allowed_actions": _allowed_actions(project, target_scenes),
        "forbidden_actions": _forbidden_actions(),
        "stop_conditions": _stop_conditions(),
        "source_files": {
            "loop_summary": "qa/image_qa_loop.json",
            "arbiter_decisions": "qa/arbiter_decisions/image/<scene>/round_NNN.json",
            "round_ledger": "qa/evaluation_rounds.jsonl",
            "wiki_memory": "llm-wiki/evaluation-rounds.md",
        },
        "omo_prompt": _omo_prompt(project, target_scenes, next_action),
    }
    write_json(project / "qa" / "omo_image_ralph_plan.json", plan)
    return f"planned OMO image RALPH orchestration for {len(target_scenes)} scene(s)"


def _target_scenes(loop: JsonObject, scene_filter: str | None) -> list[str]:
    ralph_loop = loop.get("ralph_loop", {})
    if not isinstance(ralph_loop, dict):
        return []
    blocked = list(ralph_loop.get("blocked_scenes", []))
    scenes = [str(scene.get("scene_id", "")) for scene in blocked if isinstance(scene, dict)]
    scenes = [scene for scene in scenes if scene]
    if scene_filter is None:
        return scenes
    return [scene for scene in scenes if scene == scene_filter]


def _next_omo_action(loop: JsonObject, next_action: str) -> str:
    if bool(loop.get("passed", False)):
        return "stop_passed"
    if next_action == "stop_and_escalate":
        return "stop_and_escalate"
    if next_action == "regenerate_blocked_scenes":
        return "prepare_imagegen_jobs_only"
    return "manual_review"


def _allowed_actions(project: Path, target_scenes: list[str]) -> list[str]:
    project_arg = str(project)
    actions = [f"uv run python scripts/validate_images.py --project {project_arg}"]
    for scene_id in target_scenes:
        actions.append(
            f"uv run python scripts/generate_images.py --project {project_arg} --live --only {scene_id} --regenerate"
        )
        actions.append(
            f"uv run python scripts/record_image_output.py --project {project_arg} --scene-id {scene_id} --generated-file <generated_png>"
        )
        actions.append(f"uv run python scripts/validate_images.py --project {project_arg} --only {scene_id}")
    return actions


def _forbidden_actions() -> list[str]:
    return [
        "live imagegen",
        "live Seedance",
        "live TTS",
        "paid video generation",
        "Do not score images yourself; use validate_images.py and Arbiter outputs only.",
        "Do not run live imagegen unless the user explicitly approves that paid or external step.",
        "Do not run live Seedance inside image RALPH.",
        "Do not run live TTS or narration tools.",
        "Do not change Gate 1, Gate 2, critical veto, repeated blocker, or max-20 rules.",
    ]


def _stop_conditions() -> list[str]:
    return [
        "qa/image_qa_loop.json passed=true",
        "next_action=stop_and_escalate",
        "ralph_loop.status=max_iterations_reached",
        "ralph_loop.status=repeated_blocker_escalation",
        "target_scenes is empty",
    ]


def _omo_prompt(project: Path, target_scenes: list[str], next_action: str) -> str:
    if next_action == "stop_and_escalate":
        return _stop_prompt(project, target_scenes)
    return _run_prompt(project, target_scenes)


def _run_prompt(project: Path, target_scenes: list[str]) -> str:
    scene_text = ", ".join(target_scenes) if target_scenes else "none"
    return "\n".join(
        [
            "$omo:ulw-loop",
            f"Project: {project}",
            f"Target image scenes: {scene_text}",
            "Use OMO only as the repeated execution manager.",
            "Do not score images yourself; the harness is the only judge.",
            f"Start each round with: uv run python scripts/validate_images.py --project {project}",
            "Read qa/image_qa_loop.json and qa/arbiter_decisions before choosing the next command.",
            "For each blocked scene, prepare Codex imagegen job specs with generate_images.py --live --regenerate.",
            "After the user or Codex imagegen provides a PNG, record it with record_image_output.py --generated-file.",
            "Re-run validate_images.py and stop when the harness says passed or stop_and_escalate.",
            "Never call live Seedance, live TTS, or any paid video command inside this image loop.",
        ]
    )


def _stop_prompt(project: Path, target_scenes: list[str]) -> str:
    scene_text = ", ".join(target_scenes) if target_scenes else "blocked scenes"
    return "\n".join(
        [
            "$omo:ulw-loop",
            f"Project: {project}",
            f"Target image scenes: {scene_text}",
            "Do not regenerate. The harness returned stop_and_escalate.",
            "Read qa/image_qa_loop.json and qa/arbiter_decisions, then propose upstream storyboard, reference, or prompt-contract fixes.",
            "Do not score images yourself and do not call paid or live generation tools.",
        ]
    )
