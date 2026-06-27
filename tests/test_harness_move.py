from __future__ import annotations

import subprocess
from pathlib import Path

import safety_video_harness


ROOT = Path(__file__).resolve().parents[1]


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", *args],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )


def test_package_imports_from_app_harness_package() -> None:
    package_path = Path(safety_video_harness.__file__).resolve()

    assert "app/harness/package/safety_video_harness" in package_path.as_posix()


def test_root_script_wrapper_and_canonical_cli_create_projects(tmp_path: Path) -> None:
    wrapper_project = tmp_path / "wrapper-project"
    canonical_project = tmp_path / "canonical-project"

    wrapper = run_cli("scripts/init_project.py", "--name", "wrapper", "--slug", str(wrapper_project))
    canonical = run_cli(
        "app/harness/cli/init_project.py",
        "--name",
        "canonical",
        "--slug",
        str(canonical_project),
    )

    assert wrapper.returncode == 0
    assert canonical.returncode == 0
    assert (wrapper_project / "qa" / "approvals.json").exists()
    assert (canonical_project / "qa" / "approvals.json").exists()


def test_harness_templates_and_schemas_live_under_app() -> None:
    assert (ROOT / "app" / "harness" / "templates" / "project" / "HANDOFF.md").exists()
    assert (ROOT / "app" / "harness" / "schemas" / "project_config.schema.json").exists()
