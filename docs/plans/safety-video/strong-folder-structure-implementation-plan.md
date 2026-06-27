# Strong Folder Structure Migration Implementation Plan

## TL;DR
> **Summary**: Migrate the repo to the simplified root structure only after adding a layout abstraction, compatibility tests, and root-level wrappers so existing CLI commands, plugin hooks, and project artifacts keep working during the move.
> **Deliverables**:
> - New root shape: `app/`, `projects/`, `references/`, `docs/`, `tests/`
> - New plugin shape: `app/plugin/{.codex-plugin,agents,skills,hooks}`
> - New harness shape: `app/harness/{package,cli,schemas,templates}`
> - New project shape: `projects/<slug>/{input,refs,story,media,qa}`
> - Migration command for old project folders
> - Compatibility wrappers for old `scripts/*.py` commands
> **Effort**: Large
> **Parallel**: YES - 4 waves after the layout foundation lands
> **Critical Path**: Task 1 -> Task 2 -> Task 3 -> Task 4 -> Task 8 -> Task 11 -> Final Verification

## Context

### Original Request

The user wants a concrete implementation plan for moving to the simplified folder structure, specifically considering what code will break and how to move files safely.

### Target Folder Structure

```text
.
├── app/
│   ├── plugin/
│   │   ├── .codex-plugin/
│   │   ├── agents/
│   │   ├── skills/
│   │   └── hooks/
│   └── harness/
│       ├── package/
│       ├── cli/
│       ├── schemas/
│       └── templates/
├── projects/
│   ├── <project-name>/
│   │   ├── input/
│   │   ├── refs/
│   │   ├── story/
│   │   ├── media/
│   │   └── qa/
│   └── _runs/
├── references/
│   ├── style/
│   ├── people/
│   ├── ppe/
│   ├── equipment/
│   └── spaces/
├── docs/
│   ├── guides/
│   ├── plans/
│   ├── reviews/
│   └── onepagers/
└── tests/
    ├── fixtures/
    ├── unit/
    └── integration/
```

`projects/_runs/` is the default destination for non-production run evidence that does not belong to a named safety-video project. This keeps the root simple without losing dry-run and QA evidence.

Allowed root exceptions after migration:

- `README.md`, `AGENTS.md`, `CONTEXT.md`
- `pyproject.toml`, `uv.lock`
- `.gitignore` and other repository metadata
- `.codex-plugin/` only if Codex requires a root compatibility manifest
- `scripts/` only as temporary compatibility wrappers
- `plans/` only until existing plans are moved or archived under `docs/plans/` in a separately approved cleanup

### Research Findings

- `.codex-plugin/plugin.json` currently points to root `./skills/` and `./hooks/hooks.json`.
- `hooks/hooks.json` runs commands from root `hooks/*.py`.
- `tests/test_plugin_structure.py` asserts root `skills/`, `agents/`, `hooks/`, `schemas/`, `templates/`, `style-guides/`, and `scripts/` paths.
- Most tests execute CLI files directly as `python3 scripts/<name>.py`.
- `pyproject.toml` sets `pythonpath = ["."]`, so moving `safety_video_harness/` breaks imports unless packaging or compatibility is changed first.
- `safety_video_harness/project.py` creates old project folders: `sources`, `model`, `product`, `ref`, `style`, `asset-lock`, `storyboard`, `prompts`, `images`, `video`, `audio`, `subtitles`, `output`, `qa`, `evidence`, `.harness`.
- `reference_catalog.py`, `style_guides.py`, `generation.py`, `scene_links.py`, `prompt_contract.py`, `storyboard.py`, `gate_validation.py`, `validation.py`, docs, and tests contain old project path strings.
- There are existing uncommitted changes and evidence folders. The migration must not revert or silently overwrite them.
- Metis gap-analysis initially timed out twice, then returned. Its key additions are incorporated below: root exception policy, project schema-version policy, hook/script root-resolution risk, and artifact preservation acceptance checks.

### Interview Summary

No additional user decision is required. The default is to do the migration conservatively: add path contracts and compatibility first, move files second, then remove old compatibility only in a later explicit cleanup.

### Metis Review

Metis identified five critical risk classes now covered by this plan:

- The target root structure needs explicit exceptions for repo metadata and temporary compatibility shims.
- This is a project schema migration, not only a cosmetic folder move.
- Moving `scripts/` and `hooks/` breaks code that calculates `ROOT = Path(__file__).resolve().parents[1]`.
- Existing generated JSON contracts contain old relative paths and must be migrated or read through layout fallbacks.
- Existing approved media and uncommitted evidence must be preserved with count checks and overwrite refusal.

## Work Objectives

### Core Objective

Reorganize the repository and generated project layout into a simpler structure without breaking the current safety-video harness workflow, hook guardrails, tests, or existing project artifacts.

### Deliverables

- `safety_video_harness.layout` or equivalent central layout module.
- New project creation layout under `input/`, `refs/`, `story/`, `media/`, `qa/`.
- Old-project read compatibility for one migration window.
- Explicit `scripts/migrate_project_structure.py` command.
- Physical folder moves into `app/plugin/`, `app/harness/`, `references/`, `docs/*`.
- Root `scripts/*.py` compatibility wrappers.
- Updated README, AGENTS rules, docs, tests, and one-pager.
- Evidence for all migration verification under `projects/_runs/folder-migration/`.

### Definition of Done

- `uv run python -m pytest` passes.
- Old direct CLI command still works: `uv run python scripts/init_project.py --name smoke --slug <tmp>/old-wrapper-smoke`.
- New CLI path works: `uv run python app/harness/cli/init_project.py --name smoke --slug <tmp>/new-layout-smoke`.
- New project creation produces `input/`, `refs/`, `story/`, `media/`, `qa/`.
- Old project fixture with `sources/`, `ref/approved/`, `storyboard/`, `images/`, `video/` can still be read or migrated.
- Plugin manifest points to `app/plugin` assets and hook commands execute from the moved hook directory.
- No live imagegen, live Seedance, live TTS, paid calls, or external uploads run during migration verification.

### Must Have

- Compatibility before physical moves.
- Characterization tests before changing paths.
- A migration command that is dry-run capable, idempotent, and refuses to overwrite approved assets.
- Explicit old-to-new path mapping.
- Root wrappers for `scripts/*.py` retained until the user approves their removal.
- Evidence written under `projects/_runs/folder-migration/`.

### Must NOT Have

- No bulk `mv` before tests and layout abstraction.
- No deletion of existing uncommitted work.
- No rewriting approved image/video assets.
- No generated media calls.
- No changing RALPH semantics, QA scoring, or gate approval policy except for path resolution.
- No hidden fallback that writes to both old and new locations indefinitely.

## Verification Strategy

> ZERO HUMAN INTERVENTION - all verification is agent-executed.

- Test decision: tests-first for path contracts and migration behavior, then implementation.
- Framework: existing `pytest` through `uv run python -m pytest`.
- QA policy: every task includes happy and failure scenarios.
- Evidence: write logs, command output, and before/after tree snapshots under `projects/_runs/folder-migration/`.

## Execution Strategy

### Parallel Execution Waves

Wave 1: Task 1, Task 2, Task 3. Establish inventory, tests, and central path mapping.

Wave 2: Task 4, Task 5, Task 6, Task 7. Move project-internal path behavior behind layout functions while keeping old projects readable.

Wave 3: Task 8, Task 9, Task 10. Add migration command and physically move root plugin/harness folders with compatibility wrappers.

Wave 4: Task 11, Task 12, Task 13. Move docs/references/evidence, update tests/docs, and run final verification.

### Dependency Matrix

| Task | Depends On | Blocks |
| --- | --- | --- |
| 1. Inventory and Freeze Baseline | none | 2, 3 |
| 2. Characterization Tests | 1 | 4, 8, 9 |
| 3. Layout Module Contract | 1 | 4, 5, 6, 7 |
| 4. New Project Skeleton | 2, 3 | 5, 6, 7, 8 |
| 5. Reference Path Migration | 3, 4 | 8 |
| 6. Story and Prompt Path Migration | 3, 4 | 8 |
| 7. Media, QA, and Gate Path Migration | 3, 4, 6 | 8 |
| 8. Project Migration Command | 4, 5, 6, 7 | 11, 13 |
| 9. Plugin Move | 2, 3 | 11, 13 |
| 10. Harness Move and CLI Wrappers | 2, 3 | 11, 13 |
| 11. Docs and One-Pagers | 8, 9, 10 | 13 |
| 12. Evidence and Reference Cleanup | 8 | 13 |
| 13. Full Verification and Compatibility Audit | 8, 9, 10, 11, 12 | Final |

## TODOs

- [x] 1. Inventory and Freeze Baseline

  **What to do**: Generate a machine-readable inventory before moving anything. Record current root folders, tracked/untracked files, old project path occurrences, hook registrations, plugin manifest paths, and direct script call sites. Save snapshots under `projects/_runs/folder-migration/baseline/`.
  **Must NOT do**: Do not move, rename, delete, or format files.

  **Parallelization**: Can Parallel: YES | Wave 1 | Blocks: 2, 3 | Blocked By: none

  **References**:
  - Pattern: `git status --short` - must preserve uncommitted work.
  - Pattern: `tests/test_plugin_structure.py` - current plugin path assertions.
  - Pattern: `README.md` - current documented root and project layouts.
  - Pattern: `safety_video_harness/project.py` - current project folder source of truth.

  **Acceptance Criteria**:
  - [ ] `projects/_runs/folder-migration/baseline/git-status.txt` exists.
  - [ ] `projects/_runs/folder-migration/baseline/path-occurrences.txt` lists old path strings.
  - [ ] `projects/_runs/folder-migration/baseline/root-tree.txt` exists.
  - [ ] `projects/_runs/folder-migration/baseline/root-exceptions.md` lists allowed root exceptions and why each remains at root.
  - [ ] No files outside `projects/_runs/folder-migration/` are changed by this task.

  **QA Scenarios**:
  ```text
  Scenario: Baseline inventory captures current risks
    Tool: bash
    Steps: run git status, find root folders, and rg old path strings into baseline files
    Expected: files exist and include .codex-plugin, scripts/, hooks/, sources/, storyboard/, images/
    Evidence: projects/_runs/folder-migration/baseline/path-occurrences.txt

  Scenario: Inventory task is non-mutating
    Tool: bash
    Steps: compare git status before and after inventory
    Expected: only baseline evidence files are added
    Evidence: projects/_runs/folder-migration/baseline/git-status-after.txt
  ```

  **Commit**: YES | Message: `test(layout): capture folder migration baseline` | Files: `projects/_runs/folder-migration/baseline/*`

- [x] 2. Characterization Tests for Old Behavior

  **What to do**: Add tests that lock current behavior before path changes: root direct script execution, plugin manifest loading, hook command execution, old project read paths, image job path generation, scene link paths, and reference catalog paths.
  **Must NOT do**: Do not update implementation yet. Failing tests at this step should describe missing coverage only, not new behavior.

  **Parallelization**: Can Parallel: YES | Wave 1 | Blocks: 4, 8, 9, 10 | Blocked By: 1

  **References**:
  - Pattern: `tests/test_mvp_flow.py` - CLI flow tests already use `scripts/*.py`.
  - Pattern: `tests/test_seedance_live_guardrails.py` - approved image/video path expectations.
  - Pattern: `tests/test_roadmap_bundle2.py` - image job output and continuity paths.
  - Pattern: `tests/test_plugin_structure.py` - plugin asset existence checks.

  **Acceptance Criteria**:
  - [ ] Tests assert `python3 scripts/init_project.py` still works.
  - [ ] Tests assert old project folders can be read by validation/generation code.
  - [ ] Tests assert hook scripts can execute through the currently registered command path.
  - [ ] `uv run python -m pytest tests/test_plugin_structure.py tests/test_mvp_flow.py` passes before migration implementation.

  **QA Scenarios**:
  ```text
  Scenario: Old CLI remains characterized
    Tool: bash
    Steps: run uv run python -m pytest tests/test_mvp_flow.py
    Expected: direct scripts flow passes
    Evidence: projects/_runs/folder-migration/task-2-old-cli.txt

  Scenario: Plugin path contract is captured
    Tool: bash
    Steps: run uv run python -m pytest tests/test_plugin_structure.py
    Expected: current manifest, hook, agent, skill paths are asserted
    Evidence: projects/_runs/folder-migration/task-2-plugin.txt
  ```

  **Commit**: YES | Message: `test(layout): lock current folder contracts` | Files: `tests/*`

- [x] 3. Central Layout Module Contract

  **What to do**: Introduce a single source of truth for all old and new repository/project paths, preferably `safety_video_harness/layout.py` before any package move. Define stable keys such as `source_raw`, `source_rendered`, `refs_cast`, `refs_ppe`, `refs_equipment`, `refs_space`, `story_scenes`, `story_image_prompts`, `media_image_draft`, `media_image_approved`, `media_video_clips`, `qa_root`, and `state_root`. Include old aliases and new canonical paths. Add project layout version detection: missing version means layout v1, explicit `project_layout_version: 2` means new canonical layout.
  **Must NOT do**: Do not physically move folders in this task.

  **Parallelization**: Can Parallel: YES | Wave 1 | Blocks: 4, 5, 6, 7, 8, 9, 10 | Blocked By: 1

  **References**:
  - Pattern: `safety_video_harness/project.py:PROJECT_DIRS` - current project directory list.
  - Pattern: `safety_video_harness/reference_catalog.py:ASSET_DIRS` - current reference role mapping.
  - Pattern: `safety_video_harness/storyboard.py` - current `storyboard`, `images`, and `video` output strings.
  - Pattern: `safety_video_harness/generation.py` - current image/video job paths.

  **Acceptance Criteria**:
  - [ ] Layout tests cover every old path listed in `PROJECT_DIRS`.
  - [ ] Layout tests cover every new canonical path in `input/`, `refs/`, `story/`, `media/`, `qa/`.
  - [ ] Layout API can resolve read path with old fallback and write path with new canonical path.
  - [ ] Layout API detects v1 and v2 projects deterministically.
  - [ ] No production code writes to both old and new paths by default.

  **QA Scenarios**:
  ```text
  Scenario: New canonical paths resolve consistently
    Tool: bash
    Steps: run layout unit tests for all path keys
    Expected: each key maps to the target simplified structure
    Evidence: projects/_runs/folder-migration/task-3-layout-new.txt

  Scenario: Old aliases remain readable
    Tool: bash
    Steps: create temp old-layout project fixture and resolve read paths
    Expected: resolver finds old files without copying them
    Evidence: projects/_runs/folder-migration/task-3-layout-old.txt
  ```

  **Commit**: YES | Message: `feat(layout): add folder layout resolver` | Files: `safety_video_harness/layout.py`, `tests/*`

- [x] 4. New Project Skeleton Without Breaking Old Projects

  **What to do**: Change project initialization to create `input/`, `refs/`, `story/`, `media/`, and `qa/` while old projects remain readable through the layout resolver. Map old paths to new paths:
  - `sources/raw` -> `input/sources/raw`
  - `sources/rendered` -> `input/sources/rendered`
  - `sources/*.json` -> `input/*.json`
  - `model/cast` -> `refs/people`
  - `model/ppe` -> `refs/ppe`
  - `product/equipment` -> `refs/equipment`
  - `ref/candidates` -> `refs/candidates`
  - `ref/approved/person` -> `refs/approved/people`
  - `ref/approved/work` -> `refs/approved/work`
  - `ref/approved/space` -> `refs/approved/spaces`
  - `ref/approved/style` -> `refs/approved/style`
  - `style` and `asset-lock` -> `refs/style` and `refs/asset-lock`
  - `storyboard/versions` and `prompts` -> `story/`
  - `images`, `video`, `audio`, `subtitles`, `output` -> `media/`
  - `evidence`, `.harness`, `llm-wiki`, `approvals.json` -> `qa/`
  **Must NOT do**: Do not migrate existing project folders in place in this task.

  **Parallelization**: Can Parallel: NO | Wave 2 | Blocks: 5, 6, 7, 8 | Blocked By: 2, 3

  **References**:
  - Pattern: `safety_video_harness/project.py:init_project` - current initialization flow.
  - Pattern: `templates/project/HANDOFF.md` - project handoff references.
  - Pattern: `README.md` project folder contract - must be updated later, not here.

  **Acceptance Criteria**:
  - [ ] New project creation creates only the new top-level project folders plus required files.
  - [ ] New `project_config.json` includes `project_layout_version: 2`.
  - [ ] Old project fixture can still be validated using read fallbacks.
  - [ ] `approvals.json` location decision is explicit: canonical `qa/approvals.json`, old root fallback allowed.
  - [ ] `.harness` state location decision is explicit: canonical `qa/state/`, old `.harness/` fallback allowed.

  **QA Scenarios**:
  ```text
  Scenario: New project skeleton is simple
    Tool: bash
    Steps: uv run python scripts/init_project.py --name smoke --slug /tmp/new-layout-project
    Expected: top-level project folders include input, refs, story, media, qa
    Evidence: projects/_runs/folder-migration/task-4-new-project-tree.txt

  Scenario: Old project remains readable
    Tool: bash
    Steps: create old-layout fixture, run validate_project
    Expected: validation reads old paths through fallbacks
    Evidence: projects/_runs/folder-migration/task-4-old-project-compat.txt
  ```

  **Commit**: YES | Message: `feat(project): initialize simplified project layout` | Files: `safety_video_harness/project.py`, `safety_video_harness/layout.py`, `tests/*`

- [x] 5. Reference Path Migration

  **What to do**: Move reference catalog logic from old path literals to layout keys. Canonical reference roles are:
  - `cast` -> `refs/people`
  - `ppe` -> `refs/ppe`
  - `equipment` -> `refs/equipment`
  - `approved_reference` -> `refs/approved`
  - `person_reference` -> `refs/approved/people`
  - `work_situation_reference` -> `refs/approved/work`
  - `space_reference` -> `refs/approved/spaces`
  - `style_reference` -> `refs/approved/style`
  - `camera_reference` -> `refs/approved/camera`
  - `lighting_reference` -> `refs/approved/lighting`
  Keep old read fallbacks for `model/cast`, `model/ppe`, `product/equipment`, and `ref/approved/*`.
  **Must NOT do**: Do not change reference semantics or prompt role names.

  **Parallelization**: Can Parallel: YES | Wave 2 | Blocks: 8 | Blocked By: 3, 4

  **References**:
  - Pattern: `safety_video_harness/reference_catalog.py` - role mapping and sidecar handling.
  - Pattern: `safety_video_harness/style_guides.py` - intake folder names.
  - Pattern: `README.md` reference intake docs.

  **Acceptance Criteria**:
  - [ ] Catalog reads new `refs/...` paths.
  - [ ] Catalog reads old paths for migrated/not-yet-migrated projects.
  - [ ] Prompt manifest still contains role names expected by generation code.
  - [ ] Tests cover sidecar `.md` and `.profile.md` files in both old and new locations.

  **QA Scenarios**:
  ```text
  Scenario: New refs are included in prompts
    Tool: bash
    Steps: create temp project with refs/people/operator.png and run reference catalog tests
    Expected: catalog includes role cast with path refs/people/operator.png
    Evidence: projects/_runs/folder-migration/task-5-new-refs.txt

  Scenario: Old refs still work
    Tool: bash
    Steps: create temp project with model/cast/operator.png and run same catalog path
    Expected: catalog includes role cast with old path and no crash
    Evidence: projects/_runs/folder-migration/task-5-old-refs.txt
  ```

  **Commit**: YES | Message: `feat(refs): resolve reference assets through layout` | Files: `safety_video_harness/reference_catalog.py`, `safety_video_harness/style_guides.py`, `tests/*`

- [x] 6. Story and Prompt Path Migration

  **What to do**: Route storyboard, prompt team, image prompt, and Seedance prompt files through layout keys. Canonical paths:
  - `story/scenes.json`
  - `story/versions/`
  - `story/image_prompts.json`
  - `story/video_prompts.json`
  - `story/image_prompt_team_plan.json`
  - `story/imagegen_jobs.json`
  Old fallbacks: `storyboard/scenes.json`, `storyboard/versions`, `prompts/*.json`.
  **Must NOT do**: Do not change scene schema, story QA scoring, or RALPH logic.

  **Parallelization**: Can Parallel: YES | Wave 2 | Blocks: 7, 8 | Blocked By: 3, 4

  **References**:
  - Pattern: `safety_video_harness/storyboard.py` - scenes and keyframe strings.
  - Pattern: `safety_video_harness/prompt_team.py` - prompt team plan.
  - Pattern: `safety_video_harness/imagegen_jobs.py` - image generation job files.
  - Pattern: `safety_video_harness/seedance_live.py` - video prompt file precondition.

  **Acceptance Criteria**:
  - [ ] New projects write story files under `story/`.
  - [ ] Old projects with `storyboard/scenes.json` and `prompts/*.json` remain readable.
  - [ ] Generated job specs reference canonical new paths for new projects.
  - [ ] Error messages mention canonical path first and old fallback second where useful.

  **QA Scenarios**:
  ```text
  Scenario: New story path is used
    Tool: bash
    Steps: init new project, plan storyboard, plan image prompt team
    Expected: story/scenes.json and story/image_prompt_team_plan.json exist
    Evidence: projects/_runs/folder-migration/task-6-new-story.txt

  Scenario: Old storyboard path remains readable
    Tool: bash
    Steps: old-layout fixture with storyboard/scenes.json, run validate_project and generate_images --dry-run
    Expected: commands pass without requiring a copy to story/
    Evidence: projects/_runs/folder-migration/task-6-old-story.txt
  ```

  **Commit**: YES | Message: `feat(story): resolve storyboard and prompt paths through layout` | Files: `safety_video_harness/*`, `tests/*`

- [x] 7. Media, QA, Gate, and Continuity Path Migration

  **What to do**: Route image, video, audio, subtitle, output, QA, evidence, approvals, and state paths through layout keys. Canonical paths:
  - `media/images/draft`
  - `media/images/approved`
  - `media/images/rejected`
  - `media/video/clips`
  - `media/video/sampled_frames`
  - `media/video/inspection`
  - `media/audio`
  - `media/subtitles`
  - `media/output`
  - `qa/evaluation_rounds.jsonl`
  - `qa/evaluation_bundles`
  - `qa/role_evaluations`
  - `qa/arbiter_decisions`
  - `qa/image_manual_reviews.json`
  - `qa/state`
  - `qa/approvals.json`
  Keep old read fallbacks for `images/*`, `video/*`, root `audio`, root `subtitles`, root `output`, root `approvals.json`, root `.harness`, and root `evidence`.
  **Must NOT do**: Do not approve images or videos; this is path migration only.

  **Parallelization**: Can Parallel: YES | Wave 2 | Blocks: 8 | Blocked By: 3, 4, 6

  **References**:
  - Pattern: `safety_video_harness/generation.py` - image and Seedance job paths.
  - Pattern: `safety_video_harness/image_versions.py` - image versioning and no-overwrite behavior.
  - Pattern: `safety_video_harness/scene_links.py` - sliding-chain continuity paths.
  - Pattern: `safety_video_harness/gate_validation.py` - approval gate preconditions.
  - Pattern: `safety_video_harness/evaluation_rounds.py` - QA ledger.

  **Acceptance Criteria**:
  - [ ] New image drafts write to `media/images/draft/`.
  - [ ] New approved image references use `media/images/approved/scNN.png`.
  - [ ] Scene link validator accepts new canonical paths and old fallback paths.
  - [ ] Gate validation reads canonical `qa/approvals.json` and old root `approvals.json`.
  - [ ] No approved old asset is overwritten during tests.

  **QA Scenarios**:
  ```text
  Scenario: New media paths are produced
    Tool: bash
    Steps: new project through storyboard approval and generate_images --dry-run
    Expected: job outputs point to media/images/draft/scNN_v001.png
    Evidence: projects/_runs/folder-migration/task-7-new-media.txt

  Scenario: Old continuity paths remain accepted
    Tool: bash
    Steps: old fixture with images/approved/sc01.png and prompts/video_prompts.json, run validate_scene_links
    Expected: validator passes or reports only true continuity issues, not missing new folders
    Evidence: projects/_runs/folder-migration/task-7-old-continuity.txt
  ```

  **Commit**: YES | Message: `feat(media): migrate media and qa paths through layout` | Files: `safety_video_harness/*`, `tests/*`

- [x] 8. Project Migration Command

  **What to do**: Add `scripts/migrate_project_structure.py` and new canonical CLI equivalent. It must support `--dry-run`, `--write`, `--project <path>`, and `--evidence-dir`. It must print and write a mapping report, create missing new folders, copy or move old files according to a deterministic mapping, refuse overwrites unless `--allow-overwrite-unapproved` is given, and never overwrite approved media. It must be idempotent.
  **Must NOT do**: Do not migrate all projects automatically. The command migrates only an explicit `--project`.

  **Parallelization**: Can Parallel: NO | Wave 3 | Blocks: 11, 12, 13 | Blocked By: 4, 5, 6, 7

  **References**:
  - Pattern: `scripts/init_project.py` - existing thin CLI pattern.
  - Pattern: `safety_video_harness/image_versions.py` - approved asset preservation behavior.
  - Pattern: `safety_video_harness/errors.py` - error reporting style.
  - Pattern: `projects/` and `evidence/` - existing project/run artifacts must be classified, not blindly moved.

  **Acceptance Criteria**:
  - [ ] `--dry-run` produces a report and changes no project files.
  - [ ] `--write` migrates an old temp project into the new structure.
  - [ ] Running `--write` twice makes no additional changes.
  - [ ] Existing destination file conflict fails with a clear error.
  - [ ] Approved images/videos are never overwritten.

  **QA Scenarios**:
  ```text
  Scenario: Dry-run migration is non-mutating
    Tool: bash
    Steps: copy an old-layout fixture, run migrate_project_structure.py --dry-run, compare tree before/after
    Expected: only evidence report changes
    Evidence: projects/_runs/folder-migration/task-8-dry-run.txt

  Scenario: Write migration is idempotent
    Tool: bash
    Steps: run --write twice on temp old project
    Expected: first run migrates, second run reports no-op
    Evidence: projects/_runs/folder-migration/task-8-idempotent.txt
  ```

  **Commit**: YES | Message: `feat(project): add explicit folder migration command` | Files: `scripts/migrate_project_structure.py`, `app/harness/cli/*`, `safety_video_harness/*`, `tests/*`

- [x] 9. Move Plugin Assets Under `app/plugin`

  **What to do**: Move `.codex-plugin/`, `agents/`, `skills/`, and `hooks/` into `app/plugin/`. Update `plugin.json` so its relative paths work from the moved manifest location. Update hook commands to resolve scripts relative to `app/plugin/hooks/`. Fix hook Python root resolution so hooks can import or locate the harness package after moving away from root `hooks/`. Keep root compatibility only where required by Codex installation behavior: if Codex requires `.codex-plugin/plugin.json` at repo root, leave a minimal root manifest or documented symlink/wrapper strategy and test it.
  **Must NOT do**: Do not change hook guardrail logic.

  **Parallelization**: Can Parallel: YES | Wave 3 | Blocks: 11, 13 | Blocked By: 2, 3

  **References**:
  - Pattern: `.codex-plugin/plugin.json` - current manifest.
  - Pattern: `hooks/hooks.json` - current lifecycle hook registrations.
  - Pattern: `tests/test_plugin_structure.py` - expected plugin assets.
  - Pattern: `AGENTS.md` - rules that point to agent/skill docs.

  **Acceptance Criteria**:
  - [ ] Plugin tests assert the new `app/plugin` locations.
  - [ ] Hook commands execute successfully from the moved location.
  - [ ] Session-start hook still prints mission anchor.
  - [ ] Live veto hook still blocks live imagegen/Seedance/TTS/paid calls without approval.
  - [ ] Hook scripts no longer depend on `Path(__file__).resolve().parents[1]` meaning the repository root.
  - [ ] If a root manifest remains, it is a compatibility shim and documented as temporary.

  **QA Scenarios**:
  ```text
  Scenario: Moved hooks execute
    Tool: bash
    Steps: run python3 app/plugin/hooks/session-start-anchor.py
    Expected: mission anchor prints and return code is 0
    Evidence: projects/_runs/folder-migration/task-9-hook.txt

  Scenario: Live veto still blocks unsafe call
    Tool: bash
    Steps: run existing hook guardrail tests
    Expected: unapproved live tool payload is rejected
    Evidence: projects/_runs/folder-migration/task-9-veto.txt
  ```

  **Commit**: YES | Message: `refactor(plugin): move plugin assets under app` | Files: `app/plugin/*`, `.codex-plugin/*`, `tests/*`, `AGENTS.md`

- [x] 10. Move Harness Package, CLI, Schemas, and Templates Under `app/harness`

  **What to do**: Move `safety_video_harness/` to `app/harness/package/safety_video_harness/`, move canonical CLI files to `app/harness/cli/`, move `schemas/` to `app/harness/schemas/`, and move `templates/` to `app/harness/templates/`. Update packaging so imports work without relying only on `pythonpath = ["."]`. Fix CLI root discovery so canonical CLI files do not assume `Path(__file__).resolve().parents[1]` is the repository root. Keep root `scripts/*.py` wrappers that call the canonical CLI entrypoints.
  **Must NOT do**: Do not remove root `scripts/*.py` in this migration.

  **Parallelization**: Can Parallel: YES | Wave 3 | Blocks: 11, 13 | Blocked By: 2, 3

  **References**:
  - Pattern: `pyproject.toml` - current package and pytest pythonpath config.
  - Pattern: `scripts/*.py` - current direct CLI entrypoints.
  - Pattern: `safety_video_harness/project_handoff.py` - template path currently derives from repo root.
  - Pattern: `tests/test_mvp_flow.py` - direct root script execution.

  **Acceptance Criteria**:
  - [ ] `import safety_video_harness` works in tests.
  - [ ] `uv run python scripts/init_project.py ...` still works.
  - [ ] `uv run python app/harness/cli/init_project.py ...` works.
  - [ ] Template lookup resolves `app/harness/templates/project/HANDOFF.md`.
  - [ ] Schema validation resolves `app/harness/schemas/*.json`.
  - [ ] Root wrappers are intentionally thin and contain no duplicated business logic.

  **QA Scenarios**:
  ```text
  Scenario: Old root script wrapper works
    Tool: bash
    Steps: uv run python scripts/init_project.py --name wrapper --slug /tmp/wrapper-project
    Expected: command succeeds and creates new-layout project
    Evidence: projects/_runs/folder-migration/task-10-wrapper.txt

  Scenario: Canonical CLI works
    Tool: bash
    Steps: uv run python app/harness/cli/init_project.py --name canonical --slug /tmp/canonical-project
    Expected: command succeeds and creates new-layout project
    Evidence: projects/_runs/folder-migration/task-10-canonical-cli.txt
  ```

  **Commit**: YES | Message: `refactor(harness): move package and cli under app` | Files: `app/harness/*`, `scripts/*`, `pyproject.toml`, `tests/*`

- [x] 11. Update Documentation, Rules, and One-Pagers

  **What to do**: Update `README.md`, `AGENTS.md`, `CONTEXT.md` if needed, docs guides, one-pagers, and any generated HTML folder overview to describe the simplified structure and compatibility rules. Replace old reference placement instructions with the new `refs/` and root `references/` vocabulary while preserving safety-video semantics.
  **Must NOT do**: Do not change approval policies or live-generation constraints.

  **Parallelization**: Can Parallel: YES | Wave 4 | Blocks: 13 | Blocked By: 8, 9, 10

  **References**:
  - Pattern: `README.md` root structure and command examples.
  - Pattern: `AGENTS.md` reference path rules.
  - Pattern: `docs/repository-folder-structure-onepager.html` - previous folder overview.
  - Pattern: `CONTEXT.md` domain terms and architecture orientation.

  **Acceptance Criteria**:
  - [ ] README root tree matches actual folders.
  - [ ] README project tree uses `input/`, `refs/`, `story/`, `media/`, `qa/`.
  - [ ] AGENTS reference placement rule uses new paths and mentions old paths only as migration fallback.
  - [ ] One-pager HTML reflects the final simplified root.
  - [ ] No docs instruct users to run live imagegen/Seedance/TTS without approval.

  **QA Scenarios**:
  ```text
  Scenario: Docs do not point to stale core paths
    Tool: bash
    Steps: rg old core path strings in README.md AGENTS.md CONTEXT.md docs
    Expected: old strings appear only in migration/fallback sections
    Evidence: projects/_runs/folder-migration/task-11-doc-rg.txt

  Scenario: Command examples still execute
    Tool: bash
    Steps: run the README dry-run smoke command sequence on a temp project
    Expected: all dry-run commands pass
    Evidence: projects/_runs/folder-migration/task-11-readme-smoke.txt
  ```

  **Commit**: YES | Message: `docs(layout): document simplified folder structure` | Files: `README.md`, `AGENTS.md`, `CONTEXT.md`, `docs/*`

- [x] 12. Evidence and Reusable Reference Cleanup

  **What to do**: Classify current root `evidence/` folders and reusable references. Move non-production dry-run evidence into `projects/_runs/` through a recorded migration report. Move reusable style guides from `style-guides/` into `references/style/`, preserving catalog semantics. Move reusable people/PPE/equipment/space assets into their matching `references/*` folder only if they are not project-specific.
  **Must NOT do**: Do not move project-specific approved artifacts out of their project. Do not delete root evidence until the new location and tests are verified.

  **Parallelization**: Can Parallel: YES | Wave 4 | Blocks: 13 | Blocked By: 8

  **References**:
  - Pattern: `evidence/imagegen-runs/`, `evidence/imagegen-tests/`, `evidence/implementation-runs/` - current untracked evidence.
  - Pattern: `style-guides/catalog.json` - reusable style catalog.
  - Pattern: `README.md` style guide docs.

  **Acceptance Criteria**:
  - [ ] Evidence classification report exists.
  - [ ] Reusable styles are available under `references/style/`.
  - [ ] Project-specific artifacts remain under `projects/<slug>/`.
  - [ ] Any temporary root compatibility path is documented.
  - [ ] No evidence files are lost; before/after file counts match.

  **QA Scenarios**:
  ```text
  Scenario: Evidence migration preserves file count
    Tool: bash
    Steps: count files before and after moving root evidence to projects/_runs
    Expected: counts match, excluding migration reports
    Evidence: projects/_runs/folder-migration/task-12-evidence-counts.txt

  Scenario: Style catalog still loads
    Tool: bash
    Steps: run style guide loading tests after moving style-guides to references/style
    Expected: default style id resolves and references load
    Evidence: projects/_runs/folder-migration/task-12-style.txt
  ```

  **Commit**: YES | Message: `refactor(assets): move shared references and run evidence` | Files: `references/*`, `projects/_runs/*`, `style-guides/*`, `tests/*`

- [x] 13. Full Verification and Compatibility Audit

  **What to do**: Run the complete test suite, direct CLI smoke tests, hook guardrail tests, old-project migration tests, and new-project flow tests. Produce a compatibility report listing which old paths remain as wrappers/fallbacks and which are canonical.
  **Must NOT do**: Do not remove compatibility wrappers in this task.

  **Parallelization**: Can Parallel: NO | Wave 4 | Blocks: Final Verification | Blocked By: 8, 9, 10, 11, 12

  **References**:
  - Pattern: `uv run python -m pytest` - full test suite.
  - Pattern: `scripts/validate_project.py`, `scripts/generate_images.py --dry-run`, `scripts/validate_scene_links.py` - core dry-run verification commands.
  - Pattern: `hooks/pretooluse-live-veto.py` - live guardrail verification.

  **Acceptance Criteria**:
  - [ ] `uv run python -m pytest` passes.
  - [ ] Old root wrapper CLI smoke passes.
  - [ ] New canonical CLI smoke passes.
  - [ ] Old project migration dry-run and write tests pass.
  - [ ] Hook guardrail tests pass.
  - [ ] `rg` confirms stale active path writes remain only in documented compatibility shims and migration tests.
  - [ ] Compatibility report exists at `projects/_runs/folder-migration/final/compatibility-report.md`.

  **QA Scenarios**:
  ```text
  Scenario: Full suite passes
    Tool: bash
    Steps: uv run python -m pytest
    Expected: all tests pass
    Evidence: projects/_runs/folder-migration/task-13-pytest.txt

  Scenario: No stale path writes remain
    Tool: bash
    Steps: run dry-run project flow and inspect created tree
    Expected: new writes land under input, refs, story, media, qa; old paths are absent unless fixture explicitly old
    Evidence: projects/_runs/folder-migration/task-13-new-write-audit.txt
  ```

  **Commit**: YES | Message: `test(layout): verify folder migration compatibility` | Files: `projects/_runs/folder-migration/final/*`, `tests/*`

## Final Verification Wave

> ALL must APPROVE. Present consolidated results to user and get explicit okay before completing the migration work.

- [x] F1. Plan Compliance Audit
  - Check every task acceptance criterion has evidence.
  - Confirm no implementation skipped the layout abstraction or compatibility layer.
  - Evidence: `projects/_runs/folder-migration/final/plan-compliance.md`

- [x] F2. Code Quality Review
  - Review for duplicated path literals, unclear fallback logic, hidden writes to old paths, and over-broad migration code.
  - Evidence: `projects/_runs/folder-migration/final/code-quality-review.md`

- [x] F3. Real Manual QA
  - Execute a no-cost dry-run safety-video flow using the new structure from project init through image job dry-run and scene link validation.
  - Evidence: `projects/_runs/folder-migration/final/manual-qa.md`

- [x] F4. Scope Fidelity Check
  - Confirm no live imagegen, live Seedance, live TTS, paid calls, or external uploads occurred.
  - Confirm RALPH, gate approval, and QA scoring semantics changed only by path resolution.
  - Evidence: `projects/_runs/folder-migration/final/scope-fidelity.md`

## Commit Strategy

Use small commits by dependency boundary:

1. `test(layout): capture folder migration baseline`
2. `test(layout): lock current folder contracts`
3. `feat(layout): add folder layout resolver`
4. `feat(project): initialize simplified project layout`
5. `feat(refs): resolve reference assets through layout`
6. `feat(story): resolve storyboard and prompt paths through layout`
7. `feat(media): migrate media and qa paths through layout`
8. `feat(project): add explicit folder migration command`
9. `refactor(plugin): move plugin assets under app`
10. `refactor(harness): move package and cli under app`
11. `docs(layout): document simplified folder structure`
12. `refactor(assets): move shared references and run evidence`
13. `test(layout): verify folder migration compatibility`

If any wave fails, stop at the smallest failing commit boundary. Do not continue physical moves while compatibility tests are red.

## Success Criteria

- The repo root is simple: `app/`, `projects/`, `references/`, `docs/`, `tests/`, plus minimal compatibility shims only if Codex/plugin packaging requires them.
- New projects use `input/`, `refs/`, `story/`, `media/`, `qa/`.
- Existing projects can be read or explicitly migrated.
- Project layout version is explicit: new projects write `project_layout_version: 2`; old projects without that field are treated as layout version 1.
- Root `scripts/*.py` still work as wrappers.
- Moved canonical CLI files under `app/harness/cli/` work.
- Plugin and hooks work from `app/plugin/`.
- Shared reference assets live under `references/`.
- Run evidence lives under `projects/_runs/`.
- All tests pass without live generation or paid calls.
