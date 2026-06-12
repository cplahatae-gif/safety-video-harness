from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", *args],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_omo_ralph_plan_uses_omo_as_runner_and_harness_as_judge(tmp_path: Path) -> None:
    project = tmp_path / "omo-ralph"
    qa_dir = project / "qa"
    qa_dir.mkdir(parents=True)
    (qa_dir / "image_qa_loop.json").write_text(
        json.dumps(
            {
                "passed": False,
                "next_action": "regenerate_blocked_scenes",
                "ralph_loop": {
                    "status": "needs_regeneration",
                    "blocked_scenes": [
                        {
                            "scene_id": "sc01",
                            "deficiencies": ["gaze target is unclear"],
                            "regeneration_prompt": "Regenerate sc01 and fix gaze target.",
                        }
                    ],
                    "current_iterations": {"sc01": 2},
                    "remaining_iterations": {"sc01": 18},
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    result = run_cli("scripts/plan_omo_image_ralph.py", "--project", str(project), "--only", "sc01")

    assert result.returncode == 0
    plan = load_json(project / "qa" / "omo_image_ralph_plan.json")
    assert plan["execution_model"] == "claude_ralph_loop_as_orchestrator"
    assert plan["decision_source"] == "harness_internal_qa_only"
    assert plan["target_scenes"] == ["sc01"]
    assert "uv run python scripts/validate_images.py" in plan["omo_prompt"]
    assert "--live --only sc01 --regenerate" in "\n".join(plan["allowed_actions"])
    assert "--generated-file <generated_png>" in "\n".join(plan["allowed_actions"])
    assert "--file <generated_png>" not in "\n".join(plan["allowed_actions"])
    assert "Do not score images yourself" in plan["omo_prompt"]
    assert "live Seedance" in plan["forbidden_actions"]


def test_omo_ralph_plan_stops_when_harness_escalates(tmp_path: Path) -> None:
    project = tmp_path / "omo-stop"
    qa_dir = project / "qa"
    qa_dir.mkdir(parents=True)
    (qa_dir / "image_qa_loop.json").write_text(
        json.dumps(
            {
                "passed": False,
                "next_action": "stop_and_escalate",
                "ralph_loop": {
                    "status": "repeated_blocker_escalation",
                    "blocked_scenes": [{"scene_id": "sc02", "deficiencies": ["same blocker"]}],
                    "escalated_scenes": ["sc02"],
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    result = run_cli("scripts/plan_omo_image_ralph.py", "--project", str(project))

    assert result.returncode == 0
    plan = load_json(project / "qa" / "omo_image_ralph_plan.json")
    assert plan["next_omo_action"] == "stop_and_escalate"
    assert "Do not regenerate" in plan["omo_prompt"]
