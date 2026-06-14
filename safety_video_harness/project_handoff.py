from __future__ import annotations

from pathlib import Path

TEMPLATE_PATH = Path(__file__).resolve().parents[1] / "templates" / "project" / "HANDOFF.md"


def write_project_handoff(project: Path, name: str) -> None:
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    project_handoff = template.replace("{{PROJECT_NAME}}", name).replace("{{PROJECT_SLUG}}", project.name)
    (project / "HANDOFF.md").write_text(project_handoff, encoding="utf-8")

