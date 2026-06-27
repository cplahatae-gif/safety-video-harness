# Root Exceptions for Folder Migration

The target root is intentionally small: `app/`, `projects/`, `references/`, `docs/`, and `tests/`.

These files or folders may remain at root after migration:

- `README.md`: repository entry document.
- `AGENTS.md`: Codex project rules loaded from the repository root.
- `CONTEXT.md`: architecture and safety-video domain context.
- `pyproject.toml`: Python packaging and test configuration.
- `uv.lock`: locked Python dependency graph.
- `.gitignore` and git metadata: repository operation files.
- `.codex-plugin/`: allowed only as a temporary compatibility manifest if Codex requires a root plugin manifest.
- `scripts/`: allowed only as temporary compatibility wrappers around `app/harness/cli`.
- `plans/`: allowed until existing planning artifacts are moved or archived under `docs/plans/` in a separately approved cleanup.
