# Task 12 Evidence And Reference Classification

## Moved

- `evidence/` -> `projects/_runs/legacy-evidence/`
- `style-guides/` -> `references/style/`

## Compatibility

- Root `.codex-plugin/plugin.json` remains as a Codex compatibility shim.
- Root `scripts/*.py` remain as compatibility wrappers for canonical `app/harness/cli/*.py`.
- Old project-internal paths remain read fallbacks only through `safety_video_harness.layout`.

## Not Moved In Task 12

- `projects/<slug>/` artifacts stay project-local.
- `fixtures/`, `scenarios/`, `storyboard/`, and `project-review/` are not root evidence runs and were left untouched.
- Empty root `audio/`, `clips/`, and `output/` directories were removed after confirming they contained no files.

## Counts

before=498
after=498
