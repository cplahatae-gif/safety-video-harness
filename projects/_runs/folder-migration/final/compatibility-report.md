# Compatibility Report

## Canonical Root Layout

- Plugin assets: `app/plugin/{.codex-plugin,agents,skills,hooks}`.
- Harness assets: `app/harness/{package,cli,schemas,templates}`.
- Shared reusable style references: `references/style/`.
- Run/evidence archive: `projects/_runs/`.

## Compatibility Shims Kept

- Root `.codex-plugin/plugin.json` points Codex to `app/plugin` assets.
- Root `scripts/*.py` wrappers execute canonical `app/harness/cli/*.py`.

## Project Layout

- New writes use `input/`, `refs/`, `story/`, `media/`, `qa/`.
- Old project read fallbacks remain for `sources/`, `storyboard/`, `prompts/`, `images/`, `video/`, `model/`, `product/`, `ref/`, root `approvals.json`, root `.harness/`, and root `evidence/`.

## Migration Command

- `scripts/migrate_project_structure.py` and `app/harness/cli/migrate_project_structure.py` support `--dry-run`, `--write`, `--project`, `--evidence-dir`, and overwrite guardrails.

## Verification Artifacts

- Full pytest: `projects/_runs/folder-migration/task-13-pytest.txt`.
- CLI smoke: `projects/_runs/folder-migration/task-13-cli-smoke.txt`.
- New write audit: `projects/_runs/folder-migration/task-13-new-write-audit.txt`.
- Evidence/reference cleanup: `projects/_runs/folder-migration/task-12-classification.md`.
