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


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_old_project(project: Path) -> None:
    files = {
        "sources/sources.json": {"sources": []},
        "sources/extracted_topics.json": {"topics": []},
        "storyboard/scenes.json": {"scenes": []},
        "prompts/imagegen_jobs.json": {"jobs": []},
        "images/approved/sc01.png": b"approved image",
        "images/draft/sc01_v001.png": b"draft image",
        "video/clips/sc01_sc02.mp4": b"clip",
        "approvals.json": {"gates": {}},
        ".harness/state.json": {"state": "old"},
    }
    for relative_path, content in files.items():
        path = project / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, bytes):
            path.write_bytes(content)
        else:
            path.write_text(json.dumps(content, ensure_ascii=False) + "\n", encoding="utf-8")


def project_files(project: Path) -> list[str]:
    return sorted(str(path.relative_to(project)) for path in project.rglob("*") if path.is_file())


def test_migrate_project_dry_run_writes_report_without_mutating_project(tmp_path: Path) -> None:
    project = tmp_path / "old-project"
    evidence = tmp_path / "evidence"
    write_old_project(project)
    before = project_files(project)

    result = run_cli(
        "scripts/migrate_project_structure.py",
        "--project",
        str(project),
        "--dry-run",
        "--evidence-dir",
        str(evidence),
    )

    assert result.returncode == 0
    assert project_files(project) == before
    assert not (project / "input").exists()
    report = read_json(evidence / "migration_report.json")
    assert report["dry_run"] is True
    assert any(item["destination"] == "media/images/approved/sc01.png" for item in report["planned_changes"])


def test_canonical_migrate_project_cli_matches_root_wrapper(tmp_path: Path) -> None:
    project = tmp_path / "old-project"
    evidence = tmp_path / "evidence"
    write_old_project(project)

    result = run_cli(
        "app/harness/cli/migrate_project_structure.py",
        "--project",
        str(project),
        "--dry-run",
        "--evidence-dir",
        str(evidence),
    )

    assert result.returncode == 0
    assert read_json(evidence / "migration_report.json")["dry_run"] is True


def test_migrate_project_write_is_idempotent(tmp_path: Path) -> None:
    project = tmp_path / "old-project"
    evidence = tmp_path / "evidence"
    write_old_project(project)

    first = run_cli("scripts/migrate_project_structure.py", "--project", str(project), "--write", "--evidence-dir", str(evidence))
    second = run_cli("scripts/migrate_project_structure.py", "--project", str(project), "--write", "--evidence-dir", str(evidence))

    assert first.returncode == 0
    assert second.returncode == 0
    assert (project / "input" / "sources.json").exists()
    assert (project / "story" / "scenes.json").exists()
    assert (project / "media" / "images" / "approved" / "sc01.png").read_bytes() == b"approved image"
    assert (project / "media" / "video" / "clips" / "sc01_sc02.mp4").read_bytes() == b"clip"
    assert read_json(project / "qa" / "approvals.json") == {"gates": {}}
    assert read_json(project / "qa" / "state" / "state.json") == {"state": "old"}
    assert read_json(project / "project_config.json")["project_layout_version"] == 2
    report = read_json(evidence / "migration_report.json")
    assert report["copied_count"] == 0


def test_migrate_project_refuses_destination_conflict(tmp_path: Path) -> None:
    project = tmp_path / "old-project"
    write_old_project(project)
    destination = project / "input" / "sources.json"
    destination.parent.mkdir(parents=True)
    destination.write_text('{"different": true}\n', encoding="utf-8")

    result = run_cli("scripts/migrate_project_structure.py", "--project", str(project), "--write")

    assert result.returncode != 0
    assert "destination already exists" in result.stderr


def test_migrate_project_never_overwrites_approved_media(tmp_path: Path) -> None:
    project = tmp_path / "old-project"
    write_old_project(project)
    destination = project / "media" / "images" / "approved" / "sc01.png"
    destination.parent.mkdir(parents=True)
    destination.write_bytes(b"different approved image")

    result = run_cli(
        "scripts/migrate_project_structure.py",
        "--project",
        str(project),
        "--write",
        "--allow-overwrite-unapproved",
    )

    assert result.returncode != 0
    assert "refusing to overwrite approved asset" in result.stderr
    assert destination.read_bytes() == b"different approved image"
