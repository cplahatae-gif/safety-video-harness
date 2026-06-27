# Real Manual QA

## Result

APPROVE. A no-cost dry-run safety-video flow was executed after the moves.

## Executed Flow

- `scripts/init_project.py` root wrapper smoke.
- `app/harness/cli/init_project.py` canonical CLI smoke.
- New project flow through source registration, dry-run PPTX render, topic extraction/selection, style DNA extraction, storyboard planning, storyboard approval, image prompt dry-run, and scene link validation.

## Evidence

- `projects/_runs/folder-migration/task-13-cli-smoke.txt`
- `projects/_runs/folder-migration/task-13-new-write-audit.txt`

## Observable

New writes landed under `input/`, `refs/`, `story/`, `media/`, and `qa/`; old root project folders were absent in the smoke project.
