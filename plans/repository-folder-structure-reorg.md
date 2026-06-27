# Repository Folder Structure Reorg Plan

## TL;DR
> **Summary**: Reorganize the repository so generated outputs, harness/plugin tooling, reusable references, documentation, and tests are separated by purpose without breaking the current CLI and project contracts.
> **Deliverables**:
> - New root taxonomy and migration map.
> - Compatibility-first move plan for `plugin/`, `harness/`, `references/`, and `runs/`.
> - Tests and QA scenarios for plugin registration, CLI compatibility, project creation, reference scanning, and evidence relocation.
> **Effort**: Large
> **Parallel**: YES - 4 waves
> **Critical Path**: Task 1 -> Task 2 -> Task 3 -> Task 4 -> Task 8 -> Final Verification

## Context

### Original Request
The user wants a full plan to restructure the repository because the current folders mix:
- outputs/results from media work,
- tools that create those outputs, including agents/hooks/skills,
- references used to generate consistent images.

### Interview Summary
No further user question is blocking. The user already expressed the intended grouping:
- "이걸로 인한 결과물" = generated project outputs and run artifacts.
- "이걸 만들기 위한 것들" = harness code, agents, hooks, skills, scripts.
- "레퍼런스 들" = shared and project-level visual references.

### Research Findings
- `README.md` documents current root layout with `.codex-plugin/`, `agents/`, `hooks/`, `skills/`, `safety_video_harness/`, `scripts/`, `schemas/`, `templates/`, `docs/`, `evidence/`, and `projects/<slug>/`.
- `.codex-plugin/plugin.json` currently points to root-relative `"skills": "./skills/"` and `"hooks": "./hooks/hooks.json"`.
- `hooks/hooks.json` invokes scripts under `${CODEX_PLUGIN_ROOT:-${PLUGIN_ROOT}}/hooks/...`.
- Tests directly execute `python3 scripts/*.py`, so CLI compatibility must be preserved while internals move.
- `safety_video_harness/project.py` creates project-internal folders such as `storyboard/`, `prompts/`, `images/`, `video/`, `qa/`, `model/`, `product/`, and `ref/`.
- `safety_video_harness/reference_catalog.py` scans project-local reference paths: `model/cast`, `model/ppe`, `product/equipment`, `ref/approved/*`.
- Test infrastructure exists: `uv run python -m pytest -q` through `pytest` configured in `pyproject.toml`.

### Metis Review
Metis was invoked as `folder_structure_metis`, but it did not return within two 120-second waits and was interrupted. The plan compensates by adding explicit final review tasks and conservative guardrails:
- Do not change project-internal paths in the first migration.
- Do not remove root CLI wrappers until compatibility tests prove parity.
- Do not move live project outputs into shared references.
- Do not run live imagegen, Seedance, TTS, uploads, or paid calls.

## Work Objectives

### Core Objective
Reorganize the repository into purpose-based top-level folders while preserving the public CLI, plugin registration, project output contract, and reference scanning behavior.

### Target Root Taxonomy
```text
/
├── plugin/                 # Codex plugin package surface
│   ├── .codex-plugin/
│   ├── agents/
│   ├── hooks/
│   └── skills/
├── harness/                # Runtime implementation and local CLI internals
│   ├── safety_video_harness/
│   ├── scripts/
│   ├── schemas/
│   └── templates/
├── references/             # Reusable cross-project visual/style references
│   ├── style-guides/
│   ├── cast/
│   ├── ppe/
│   ├── equipment/
│   ├── spaces/
│   └── examples/
├── projects/               # Actual safety-video project workspaces
│   └── <slug>/
├── runs/                   # Root-level run evidence, smoke tests, generated experiments
│   ├── imagegen/
│   ├── implementation/
│   └── smoke/
├── docs/
├── plans/
├── tests/
└── fixtures/
```

### Project-Internal Structure To Preserve
```text
projects/<slug>/
├── sources/
├── storyboard/
├── prompts/
├── images/
├── video/
├── qa/
├── evidence/
├── model/
├── product/
├── ref/
├── style/
├── asset-lock/
├── subtitles/
├── output/
└── llm-wiki/
```

### Deliverables
- `plugin/` package layout with manifest, agents, hooks, and skills.
- `harness/` runtime layout with Python package, scripts, schemas, and templates.
- Root CLI compatibility wrappers under `scripts/` unless the user explicitly approves a breaking CLI change later.
- `references/` for reusable cross-project references, while project-specific references remain in `projects/<slug>/model`, `projects/<slug>/product`, and `projects/<slug>/ref`.
- `runs/` for root-level evidence and experiments currently living under `evidence/`, `audio/`, `clips/`, `output/`, `storyboard/`, and loose `scenes.json`.
- Updated docs/tests/hook registration to reflect moved paths.

### Definition of Done
- `uv run python -m pytest -q` passes.
- `python3 -m py_compile harness/safety_video_harness/*.py plugin/hooks/*.py scripts/*.py` passes, adjusted for final paths.
- `python3 scripts/init_project.py --name "구조 QA" --slug <tmp>/structure-qa` still works.
- `python3 scripts/generate_images.py --project <tmp>/structure-qa --dry-run --only sc01` still works after a valid dry-run setup.
- `.codex-plugin/plugin.json` or `plugin/.codex-plugin/plugin.json` resolves registered hooks and skills from the new layout.
- `reference_catalog` still sees project-local `model/ppe`, `model/cast`, `product/equipment`, and `ref/approved/*`.
- Root `README.md` accurately explains where outputs, tools, and references live.

### Must Have
- Compatibility-first migration.
- Tests before path moves for every moved surface.
- Root `scripts/*.py` public entrypoints remain usable during this migration.
- Project-internal paths stay stable.
- `runs/` absorbs root-level evidence/experiment outputs but not project-local `qa/` or `evidence/`.
- Shared references are separate from project-specific approved references.

### Must NOT Have
- No live imagegen.
- No live Seedance.
- No TTS.
- No external uploads.
- No paid calls.
- No destructive cleanup of user evidence.
- No moving approved project assets into shared references.
- No breaking `python3 scripts/*.py` without a separate explicit decision.

## Verification Strategy
> ZERO HUMAN INTERVENTION - all verification is agent-executed.

- Test decision: TDD for moved path behavior and characterization tests before any move.
- Framework: `pytest` through `uv run python -m pytest`.
- QA policy: Every task has command-level QA scenarios.
- Evidence: write command transcripts to `runs/implementation/task-{N}-*.txt` after `runs/` exists; before that, use `evidence/implementation-runs/task-{N}-*.txt`.

## Execution Strategy

### Parallel Execution Waves
Wave 1: Task 1, Task 2, Task 3, Task 4  
Wave 2: Task 5, Task 6, Task 7  
Wave 3: Task 8, Task 9, Task 10  
Wave 4: Task 11, Task 12, Task 13  
Final: F1-F4

### Dependency Matrix
| Task | Depends On | Blocks |
| --- | --- | --- |
| 1. Migration inventory | none | 2, 5, 6, 7 |
| 2. Path resolver contracts | 1 | 5, 6, 7, 8 |
| 3. Project structure contract tests | none | 8, 10 |
| 4. Plugin structure contract tests | none | 6, 9 |
| 5. Introduce `runs/` policy | 1, 2 | 11 |
| 6. Move plugin package | 1, 2, 4 | 9, 12 |
| 7. Move harness internals | 1, 2 | 8, 12 |
| 8. Preserve public CLI wrappers | 2, 7 | 12 |
| 9. Update hook registration | 4, 6 | 12 |
| 10. Reference taxonomy hardening | 3 | 12 |
| 11. Relocate root artifacts | 5 | 12 |
| 12. Documentation rewrite | 6, 7, 8, 9, 10, 11 | 13 |
| 13. Compatibility cleanup | 12 | Final |

## TODOs

- [ ] 1. Create Migration Inventory And Move Map

  **What to do**: Generate a machine-readable inventory mapping every current top-level folder/file to one of: `plugin`, `harness`, `references`, `projects`, `runs`, `docs`, `plans`, `tests`, `fixtures`, `root-keep`, or `delete-candidate`. Save the map as `plans/repository-folder-structure-migration-map.md` or `docs/repository-layout.md` depending on whether it is planning-only or durable docs.

  **Must NOT do**: Do not move files in this task.

  **Parallelization**: Can Parallel: YES | Wave 1 | Blocks: 2, 5, 6, 7 | Blocked By: none

  **References**:
  - Pattern: `README.md:90` - current root structure documentation.
  - Pattern: `CONTEXT.md:34` - architecture orientation and non-negotiable policies.
  - Pattern: `git status --short` - must distinguish existing uncommitted work from new migration changes.

  **Acceptance Criteria**:
  - [ ] `rg -n "audio|clips|output|storyboard|scenes.json|evidence|agents|hooks|skills|scripts|schemas|templates|style-guides" plans/repository-folder-structure-migration-map.md` returns planned destinations.
  - [ ] The map labels `evidence/imagegen-runs`, `evidence/imagegen-tests`, and `evidence/implementation-runs` as move-to-`runs/` candidates, not delete candidates.
  - [ ] The map labels `projects/*` as project workspaces and excludes them from root cleanup moves.

  **QA Scenarios**:
  ```text
  Scenario: Inventory covers every current top-level working directory
    Tool: bash
    Steps: find . -maxdepth 1 -type d | sed 's#^./##' | sort > /tmp/topdirs.txt; rg -f /tmp/topdirs.txt plans/repository-folder-structure-migration-map.md
    Expected: every non-system top-level directory has a destination or explicit ignore reason
    Evidence: evidence/implementation-runs/task-1-inventory-coverage.txt

  Scenario: User evidence is not marked for deletion
    Tool: bash
    Steps: rg -n "evidence/imagegen-runs|evidence/imagegen-tests|evidence/implementation-runs" plans/repository-folder-structure-migration-map.md
    Expected: all three are marked preserve/move, never delete
    Evidence: evidence/implementation-runs/task-1-evidence-preserve.txt
  ```

  **Commit**: YES | Message: `docs(structure): map repository layout migration` | Files: `plans/repository-folder-structure-migration-map.md`

- [ ] 2. Add Path Resolver Design Before Moves

  **What to do**: Plan and then implement a small path resolver module that centralizes repository-root, plugin-root, harness-root, and project-root discovery. It must allow moved internals while preserving public CLI wrappers. The implementation task must be TDD: first tests prove current paths, then the resolver is added.

  **Must NOT do**: Do not rewrite every module to use the resolver in this task.

  **Parallelization**: Can Parallel: YES | Wave 1 | Blocks: 5, 6, 7, 8 | Blocked By: 1

  **References**:
  - Pattern: `safety_video_harness/project.py:16` - project folder constants.
  - Pattern: `safety_video_harness/style_guides.py` - root-style-guide lookup currently assumes root layout.
  - Pattern: `.codex-plugin/plugin.json:8` - plugin root assumptions.

  **Acceptance Criteria**:
  - [ ] New tests cover repository root, plugin root, harness root, and project root resolution.
  - [ ] Existing tests still pass before any physical folder move.
  - [ ] Resolver has no live/external service dependencies.

  **QA Scenarios**:
  ```text
  Scenario: Resolver finds current repo roots
    Tool: bash
    Steps: uv run python -m pytest tests/test_repository_layout.py::test_path_resolver_finds_current_roots -q
    Expected: test passes and prints one passed test
    Evidence: evidence/implementation-runs/task-2-resolver-current.txt

  Scenario: Resolver rejects non-project directories as project roots
    Tool: bash
    Steps: uv run python -m pytest tests/test_repository_layout.py::test_path_resolver_rejects_missing_project_contract -q
    Expected: test passes by asserting a clear HarnessError
    Evidence: evidence/implementation-runs/task-2-resolver-error.txt
  ```

  **Commit**: YES | Message: `refactor(paths): add repository layout resolver` | Files: `safety_video_harness/layout.py`, `tests/test_repository_layout.py`

- [ ] 3. Characterize Project Workspace Contract

  **What to do**: Add or update tests that assert `init_project` creates the stable project-internal structure. The intended contract remains `sources`, `storyboard`, `prompts`, `images`, `video`, `qa`, `evidence`, `model`, `product`, `ref`, `style`, `asset-lock`, `subtitles`, and `output`.

  **Must NOT do**: Do not rename project-internal folders in this migration.

  **Parallelization**: Can Parallel: YES | Wave 1 | Blocks: 8, 10 | Blocked By: none

  **References**:
  - Pattern: `safety_video_harness/project.py:14` - `PROJECT_DIRS`.
  - Pattern: `README.md:123` - documented project folder contract.
  - Pattern: `safety_video_harness/reference_catalog.py:8` - project reference scan paths.

  **Acceptance Criteria**:
  - [ ] `uv run python -m pytest tests/test_project_structure_contract.py -q` passes.
  - [ ] Tests explicitly include `model/ppe`, `product/equipment`, and `ref/approved/space`.

  **QA Scenarios**:
  ```text
  Scenario: New project has stable internal folders
    Tool: bash
    Steps: tmp=$(mktemp -d); python3 scripts/init_project.py --name "구조 QA" --slug "$tmp/structure-qa"; find "$tmp/structure-qa" -maxdepth 2 -type d | sort
    Expected: output includes storyboard, prompts, images/draft, images/approved, video/clips, qa, model/ppe, product/equipment, ref/approved
    Evidence: evidence/implementation-runs/task-3-project-structure.txt

  Scenario: Missing project contract fails validation
    Tool: bash
    Steps: tmp=$(mktemp -d); mkdir -p "$tmp/bad-project"; python3 scripts/validate_project.py "$tmp/bad-project"
    Expected: non-zero exit and message includes storyboard/scenes.json is missing
    Evidence: evidence/implementation-runs/task-3-project-error.txt
  ```

  **Commit**: YES | Message: `test(project): pin project workspace structure` | Files: `tests/test_project_structure_contract.py`

- [ ] 4. Characterize Plugin Package Contract

  **What to do**: Update plugin structure tests to support the planned `plugin/` package location. During transition, tests should allow root layout only if compatibility wrappers exist and final tests should require `plugin/.codex-plugin/plugin.json`, `plugin/agents`, `plugin/hooks`, and `plugin/skills`.

  **Must NOT do**: Do not move plugin files until the tests fail for the intended final layout.

  **Parallelization**: Can Parallel: YES | Wave 1 | Blocks: 6, 9 | Blocked By: none

  **References**:
  - Pattern: `tests/test_plugin_structure.py:10` - current manifest assertions.
  - Pattern: `.codex-plugin/plugin.json:8` - current skills/hooks references.
  - Pattern: `hooks/hooks.json:8` - current hook command paths.

  **Acceptance Criteria**:
  - [ ] RED test proves final `plugin/` package does not exist yet.
  - [ ] GREEN test passes after plugin files move and manifest paths are updated.
  - [ ] Hook command strings remain valid from plugin root.

  **QA Scenarios**:
  ```text
  Scenario: Plugin manifest resolves hooks and skills from new plugin root
    Tool: bash
    Steps: uv run python -m pytest tests/test_plugin_structure.py::test_plugin_manifest_and_harness_assets_exist -q
    Expected: test passes with manifest under plugin/.codex-plugin/plugin.json
    Evidence: evidence/implementation-runs/task-4-plugin-manifest.txt

  Scenario: Hook registration references existing moved hook scripts
    Tool: bash
    Steps: uv run python -m pytest tests/test_plugin_structure.py::test_hooks_json_registers_all_entrypoint_hooks -q
    Expected: every hook path in plugin/hooks/hooks.json exists
    Evidence: evidence/implementation-runs/task-4-hooks.txt
  ```

  **Commit**: YES | Message: `test(plugin): pin plugin package layout` | Files: `tests/test_plugin_structure.py`

- [ ] 5. Introduce Runs Policy And Evidence Destination

  **What to do**: Define `runs/` as the root-only location for implementation logs, imagegen experiments, smoke outputs, and root-level generated artifacts. Add a policy doc and tests/scripts that never move project-local `qa/`, `evidence/`, `images/`, or `video/` into root `runs/`.

  **Must NOT do**: Do not delete old `evidence/` content. Move or preserve with manifest only.

  **Parallelization**: Can Parallel: YES | Wave 2 | Blocks: 11 | Blocked By: 1, 2

  **References**:
  - Pattern: root `evidence/` currently contains implementation logs and imagegen run folders.
  - Pattern: `hooks/session-start-anchor.py:22` says preserve evidence under `qa/`, `evidence/`, and `llm-wiki/`.
  - Pattern: project contract keeps `projects/<slug>/evidence`.

  **Acceptance Criteria**:
  - [ ] `runs/README.md` defines `runs/imagegen`, `runs/implementation`, and `runs/smoke`.
  - [ ] Migration map lists old root `evidence/*` movement rules.
  - [ ] Tests or QA command confirms project-local evidence remains under project folders.

  **QA Scenarios**:
  ```text
  Scenario: Root run logs have a defined destination
    Tool: bash
    Steps: rg -n "runs/imagegen|runs/implementation|runs/smoke" runs/README.md plans/repository-folder-structure-migration-map.md
    Expected: all three destinations documented
    Evidence: evidence/implementation-runs/task-5-runs-policy.txt

  Scenario: Project evidence is excluded from root relocation
    Tool: bash
    Steps: rg -n "projects/<slug>/evidence|project-local evidence" runs/README.md plans/repository-folder-structure-migration-map.md
    Expected: explicit exclusion exists
    Evidence: evidence/implementation-runs/task-5-project-evidence.txt
  ```

  **Commit**: YES | Message: `docs(runs): define root run artifact policy` | Files: `runs/README.md`, `plans/repository-folder-structure-migration-map.md`

- [ ] 6. Move Plugin Package With Manifest Compatibility

  **What to do**: Move `.codex-plugin/`, `agents/`, `hooks/`, and `skills/` into `plugin/`. Update `plugin/.codex-plugin/plugin.json` to reference `"../skills"` only if required by plugin runtime, otherwise prefer package-local `"./skills/"` by placing manifest at package root-compatible location. If Codex requires `.codex-plugin` at repository root, keep a root compatibility manifest that points to `plugin/skills` and `plugin/hooks/hooks.json`.

  **Must NOT do**: Do not break installed plugin discovery without a root compatibility option.

  **Parallelization**: Can Parallel: YES | Wave 2 | Blocks: 9, 12 | Blocked By: 1, 2, 4

  **References**:
  - Pattern: `.codex-plugin/plugin.json:8` - current manifest fields.
  - Pattern: `hooks/hooks.json:8` - hook commands use plugin root env var.
  - Pattern: `tests/test_plugin_structure.py` - plugin contract tests.

  **Acceptance Criteria**:
  - [ ] `plugin/agents`, `plugin/hooks`, `plugin/skills`, and `plugin/.codex-plugin/plugin.json` exist.
  - [ ] Root compatibility manifest exists if required by Codex plugin loader.
  - [ ] `uv run python -m pytest tests/test_plugin_structure.py tests/test_hook_guardrails.py -q` passes.

  **QA Scenarios**:
  ```text
  Scenario: Plugin package tree is grouped
    Tool: bash
    Steps: find plugin -maxdepth 2 -type d | sort
    Expected: output includes plugin/.codex-plugin, plugin/agents, plugin/hooks, plugin/skills
    Evidence: evidence/implementation-runs/task-6-plugin-tree.txt

  Scenario: Hook guardrails still execute from moved package
    Tool: bash
    Steps: uv run python -m pytest tests/test_hook_guardrails.py -q
    Expected: all hook guardrail tests pass
    Evidence: evidence/implementation-runs/task-6-hook-guardrails.txt
  ```

  **Commit**: YES | Message: `refactor(plugin): group Codex package files` | Files: `plugin/**`, `.codex-plugin/plugin.json`, tests

- [ ] 7. Move Harness Internals Behind `harness/`

  **What to do**: Move `safety_video_harness/`, `schemas/`, `templates/`, and internal script implementations into `harness/`. Keep importable package behavior by updating `pyproject.toml` `pythonpath` or package discovery as needed.

  **Must NOT do**: Do not remove root `scripts/*.py` public entrypoints in this task.

  **Parallelization**: Can Parallel: YES | Wave 2 | Blocks: 8, 12 | Blocked By: 1, 2

  **References**:
  - Pattern: `pyproject.toml` currently uses `pythonpath = ["."]`.
  - Pattern: `scripts/*.py` insert `ROOT = Path(__file__).resolve().parents[1]`.
  - Pattern: `tests/*` import `safety_video_harness` directly.

  **Acceptance Criteria**:
  - [ ] `harness/safety_video_harness`, `harness/schemas`, and `harness/templates` exist.
  - [ ] `uv run python -m pytest tests/test_mvp_flow.py tests/test_roadmap_bundle1.py -q` passes.
  - [ ] Direct Python import of `safety_video_harness` still works from repo root.

  **QA Scenarios**:
  ```text
  Scenario: Harness package imports from new location
    Tool: bash
    Steps: uv run python -c "import safety_video_harness, pathlib; print(pathlib.Path(safety_video_harness.__file__).as_posix())"
    Expected: printed path contains harness/safety_video_harness
    Evidence: evidence/implementation-runs/task-7-import.txt

  Scenario: Core dry-run flow still works
    Tool: bash
    Steps: uv run python -m pytest tests/test_mvp_flow.py -q
    Expected: MVP dry-run tests pass
    Evidence: evidence/implementation-runs/task-7-mvp.txt
  ```

  **Commit**: YES | Message: `refactor(harness): move runtime internals under harness` | Files: `harness/**`, `pyproject.toml`, tests

- [ ] 8. Preserve Root CLI Wrappers

  **What to do**: Keep root `scripts/*.py` as thin wrappers that dispatch to `harness/scripts/*.py` or directly call harness package functions. This preserves README commands and tests that use `python3 scripts/*.py`.

  **Must NOT do**: Do not force users to call `python3 harness/scripts/*.py` in this migration.

  **Parallelization**: Can Parallel: NO | Wave 3 | Blocks: 12 | Blocked By: 2, 7

  **References**:
  - Pattern: `README.md:246` - public command examples use `scripts/*.py`.
  - Pattern: `tests/test_roadmap_bundle1.py:14` - test helper calls `["python3", *args]`.
  - Pattern: current `scripts/*.py` boundary pattern imports `run_boundary`.

  **Acceptance Criteria**:
  - [ ] `python3 scripts/init_project.py --help` works.
  - [ ] `python3 scripts/generate_images.py --help` works.
  - [ ] `uv run python -m pytest -q` passes.

  **QA Scenarios**:
  ```text
  Scenario: Public init_project wrapper still works
    Tool: bash
    Steps: tmp=$(mktemp -d); python3 scripts/init_project.py --name "CLI QA" --slug "$tmp/cli-qa"; test -f "$tmp/cli-qa/project_config.json"
    Expected: command exits 0 and project_config.json exists
    Evidence: evidence/implementation-runs/task-8-cli-init.txt

  Scenario: Unknown script arguments still fail cleanly
    Tool: bash
    Steps: python3 scripts/init_project.py --not-a-real-flag
    Expected: non-zero exit and stderr contains usage or unrecognized arguments
    Evidence: evidence/implementation-runs/task-8-cli-error.txt
  ```

  **Commit**: YES | Message: `refactor(cli): preserve root script wrappers` | Files: `scripts/**`, `harness/scripts/**`, tests

- [ ] 9. Update Hook Registration For New Plugin Root

  **What to do**: Update hook registrations and tests so hooks execute from `plugin/hooks`. Ensure `CODEX_PLUGIN_ROOT` and `PLUGIN_ROOT` assumptions still resolve. Keep guardrail behavior unchanged.

  **Must NOT do**: Do not loosen live/paid/TTS/upload guardrails.

  **Parallelization**: Can Parallel: YES | Wave 3 | Blocks: 12 | Blocked By: 4, 6

  **References**:
  - Pattern: `plugin/hooks/hooks.json` after Task 6.
  - Pattern: `tests/test_hook_guardrails.py` - direct hook behavior tests.
  - Pattern: `plugin/hooks/pretooluse-live-veto.py` - live veto semantics.

  **Acceptance Criteria**:
  - [ ] Hook JSON references only existing paths.
  - [ ] Hook guardrail tests pass.
  - [ ] `python3 plugin/hooks/session-start-anchor.py` prints the mission anchor.

  **QA Scenarios**:
  ```text
  Scenario: Session start hook works from plugin path
    Tool: bash
    Steps: python3 plugin/hooks/session-start-anchor.py
    Expected: stdout contains Safety Video Harness Mission Anchor
    Evidence: evidence/implementation-runs/task-9-session-anchor.txt

  Scenario: Live veto still blocks TTS
    Tool: bash
    Steps: uv run python -m pytest tests/test_hook_guardrails.py::test_live_veto_denies_tts_commands_even_with_storyboard_approval -q
    Expected: test passes
    Evidence: evidence/implementation-runs/task-9-tts-veto.txt
  ```

  **Commit**: YES | Message: `refactor(hooks): resolve hooks from plugin package` | Files: `plugin/hooks/**`, `.codex-plugin/plugin.json`, tests

- [ ] 10. Harden Reference Taxonomy

  **What to do**: Keep project-specific references in project folders, but add shared reference docs under `references/`. Extend docs and tests so `references/ppe` and project-local `model/ppe` have distinct purposes. If implementation changes are needed, add resolver support for optional shared references without replacing project-local references.

  **Must NOT do**: Do not make shared references automatically override project-approved references.

  **Parallelization**: Can Parallel: YES | Wave 3 | Blocks: 12 | Blocked By: 3

  **References**:
  - Pattern: `safety_video_harness/reference_catalog.py:8` - project-local scan paths.
  - Pattern: `README.md:292` - currently says reusable styles are root `style-guides`.
  - Pattern: `AGENTS.md:36` - asks where each reference belongs.

  **Acceptance Criteria**:
  - [ ] Docs explain `references/` as reusable library and `projects/<slug>/ref` as approved project inputs.
  - [ ] Tests prove project-local PPE/cast/equipment still appear in image prompts.
  - [ ] Shared references are not used unless copied/approved into a project or explicitly selected.

  **QA Scenarios**:
  ```text
  Scenario: Project PPE remains project-local
    Tool: bash
    Steps: uv run python -m pytest tests/test_reference_taxonomy.py::test_project_ppe_reference_enters_prompt -q
    Expected: generated prompt contains model/ppe fixture description
    Evidence: evidence/implementation-runs/task-10-project-ppe.txt

  Scenario: Shared reference is not implicitly approved
    Tool: bash
    Steps: uv run python -m pytest tests/test_reference_taxonomy.py::test_shared_reference_not_used_without_project_approval -q
    Expected: prompt excludes references/ppe fixture unless copied or selected
    Evidence: evidence/implementation-runs/task-10-shared-ref-boundary.txt
  ```

  **Commit**: YES | Message: `docs(references): separate shared and project references` | Files: `references/**`, `README.md`, `AGENTS.md`, tests

- [ ] 11. Relocate Root Artifacts Into `runs/`

  **What to do**: Move root-level implementation/evidence experiment folders into `runs/` according to the map. Candidate sources include root `evidence/imagegen-runs`, `evidence/imagegen-tests`, `evidence/implementation-runs`, `evidence/scenelens-smoke`, `evidence/understand-video-smoke`, `evidence/video-frame-analysis-smoke`, and loose root output directories such as `audio`, `clips`, `output`, `storyboard`, and `scenes.json` if they are not active project contracts.

  **Must NOT do**: Do not delete files. Do not move anything under `projects/<slug>/`.

  **Parallelization**: Can Parallel: YES | Wave 4 | Blocks: 12 | Blocked By: 5

  **References**:
  - Pattern: current root `evidence/` file list.
  - Pattern: `PROJECT_DIRS` includes project-local `audio`, `output`, and `evidence`, so root loose dirs need classification.
  - Pattern: user explicitly asked to distinguish outputs from creation tools.

  **Acceptance Criteria**:
  - [ ] `runs/` contains relocated root run artifacts.
  - [ ] No files under `projects/` are moved.
  - [ ] A manifest records old path, new path, and reason for every move.

  **QA Scenarios**:
  ```text
  Scenario: Root evidence move manifest exists
    Tool: bash
    Steps: rg -n "old_path|new_path|reason" runs/MIGRATION_MANIFEST.md
    Expected: manifest contains old/new/reason columns or entries
    Evidence: evidence/implementation-runs/task-11-manifest.txt

  Scenario: Project folders were untouched
    Tool: bash
    Steps: git diff --name-status -- projects
    Expected: output is empty or contains only intentional test fixture changes
    Evidence: evidence/implementation-runs/task-11-projects-untouched.txt
  ```

  **Commit**: YES | Message: `chore(runs): relocate root run artifacts` | Files: `runs/**`, removed old root artifact paths

- [ ] 12. Rewrite Operator Documentation For New Layout

  **What to do**: Update `README.md`, `CONTEXT.md`, `docs/generative-media-reference-index.md`, and any one-pager references to describe the new root taxonomy and compatibility policy. Replace root references to `agents/`, `hooks/`, `skills/`, `safety_video_harness/`, `schemas/`, `templates/`, `style-guides/`, and `evidence/` with their final paths or compatibility notes.

  **Must NOT do**: Do not update docs to advertise a path before the path exists.

  **Parallelization**: Can Parallel: YES | Wave 4 | Blocks: 13 | Blocked By: 6, 7, 8, 9, 10, 11

  **References**:
  - Pattern: `README.md:90` current plugin structure.
  - Pattern: `docs/generative-media-reference-index.md:49` current style guide path.
  - Pattern: `AGENTS.md` path-sensitive rules.

  **Acceptance Criteria**:
  - [ ] `rg -n "agents/|hooks/|skills/|safety_video_harness/|style-guides/|evidence/" README.md docs AGENTS.md CONTEXT.md` returns only correct new paths or explicit compatibility notes.
  - [ ] README has a concise "Repository Layout" section with outputs/tools/references split.
  - [ ] Handoff template points next sessions at the right files.

  **QA Scenarios**:
  ```text
  Scenario: Docs mention new top-level buckets
    Tool: bash
    Steps: rg -n "plugin/|harness/|references/|runs/|projects/<slug>" README.md CONTEXT.md
    Expected: all buckets are documented
    Evidence: evidence/implementation-runs/task-12-doc-buckets.txt

  Scenario: No stale root path claims remain
    Tool: bash
    Steps: rg -n "├── agents/|├── hooks/|├── skills/|├── safety_video_harness/" README.md docs
    Expected: no stale root tree claims unless explicitly marked compatibility wrapper
    Evidence: evidence/implementation-runs/task-12-stale-paths.txt
  ```

  **Commit**: YES | Message: `docs(structure): document reorganized repository layout` | Files: `README.md`, `CONTEXT.md`, `docs/**`, `templates/project/HANDOFF.md`

- [ ] 13. Compatibility Cleanup And Guardrail Review

  **What to do**: Remove obsolete duplicate docs or path aliases only after all tests and QA scenarios pass. Keep root wrappers that are public API. Add a final no-live guardrail check.

  **Must NOT do**: Do not remove compatibility wrappers for `scripts/*.py`.

  **Parallelization**: Can Parallel: NO | Wave 4 | Blocks: Final | Blocked By: 12

  **References**:
  - Pattern: `README.md` public commands.
  - Pattern: `tests/test_hook_guardrails.py` live/paid guardrails.
  - Pattern: `git status --short` for unrelated user changes.

  **Acceptance Criteria**:
  - [ ] `uv run python -m pytest -q` passes.
  - [ ] `git diff --check` passes.
  - [ ] `rg -n "live Seedance|live TTS|external_upload_allowed|imagegen" plugin/hooks README.md AGENTS.md` confirms guardrails are still documented.

  **QA Scenarios**:
  ```text
  Scenario: Full test suite remains green
    Tool: bash
    Steps: uv run python -m pytest -q
    Expected: all tests pass, no xfail/skip added by this migration
    Evidence: evidence/implementation-runs/task-13-full-pytest.txt

  Scenario: Guardrails still block forbidden live/TTS/upload paths
    Tool: bash
    Steps: uv run python -m pytest tests/test_hook_guardrails.py -q
    Expected: all hook guardrail tests pass
    Evidence: evidence/implementation-runs/task-13-guardrails.txt
  ```

  **Commit**: YES | Message: `chore(structure): clean compatibility leftovers` | Files: path-specific cleanup only

## Final Verification Wave
> ALL must APPROVE. Present consolidated results to user and get explicit "okay" before completing.

- [ ] F1. Plan Compliance Audit
  - Verify every planned bucket exists or has a compatibility note.
  - Command: `find plugin harness references runs projects docs plans tests fixtures -maxdepth 2 -type d | sort`
  - Evidence: `evidence/implementation-runs/f1-plan-compliance.txt`

- [ ] F2. Code Quality Review
  - Run a code review focused on path resolver simplicity, no over-broad abstractions, and no broken public wrappers.
  - Command: `uv run python -m pytest -q && git diff --check`
  - Evidence: `evidence/implementation-runs/f2-code-quality.txt`

- [ ] F3. Real Manual QA
  - Create a temp project through the root `scripts/` CLI, run source registration with fixture, dry-run storyboard/image/video planning, and validate project.
  - Command sequence:
    ```bash
    tmp=$(mktemp -d)
    python3 scripts/init_project.py --name "구조 최종 QA" --slug "$tmp/structure-final"
    python3 scripts/register_sources.py --project "$tmp/structure-final" --source fixtures/sources/remicon-collision-guide.pptx
    python3 scripts/render_pptx_sources.py --project "$tmp/structure-final" --dry-run --mode media_extract
    python3 scripts/extract_topics.py --project "$tmp/structure-final"
    python3 scripts/intake_project.py --project "$tmp/structure-final" --defaults
    python3 scripts/extract_style_dna.py --project "$tmp/structure-final"
    python3 scripts/plan_storyboard.py --project "$tmp/structure-final" --duration 30
    python3 scripts/generate_images.py --project "$tmp/structure-final" --dry-run --only sc01
    python3 scripts/generate_seedance.py --project "$tmp/structure-final" --dry-run
    python3 scripts/validate_project.py "$tmp/structure-final"
    ```
  - Expected: all commands exit 0; no live generation occurs.
  - Evidence: `evidence/implementation-runs/f3-real-manual-qa.txt`

- [ ] F4. Scope Fidelity Check
  - Verify no project outputs were deleted, no paid/live tools were run, and no unrelated user changes were reverted.
  - Commands:
    ```bash
    git status --short
    rg -n "higgsfield generate|audio.speech|text-to-speech|--execute-paid" evidence runs || true
    ```
  - Evidence: `evidence/implementation-runs/f4-scope-fidelity.txt`

## Commit Strategy
- Commit 1: `docs(structure): map repository layout migration`
- Commit 2: `refactor(paths): add repository layout resolver`
- Commit 3: `test(project): pin project workspace structure`
- Commit 4: `test(plugin): pin plugin package layout`
- Commit 5: `docs(runs): define root run artifact policy`
- Commit 6: `refactor(plugin): group Codex package files`
- Commit 7: `refactor(harness): move runtime internals under harness`
- Commit 8: `refactor(cli): preserve root script wrappers`
- Commit 9: `refactor(hooks): resolve hooks from plugin package`
- Commit 10: `docs(references): separate shared and project references`
- Commit 11: `chore(runs): relocate root run artifacts`
- Commit 12: `docs(structure): document reorganized repository layout`
- Commit 13: `chore(structure): clean compatibility leftovers`

Do not commit automatically unless explicitly approved.

## Success Criteria
- The root layout clearly separates outputs, tooling, references, docs/plans, tests/fixtures, and projects.
- Public commands under `scripts/` still work.
- Codex plugin registration still works.
- Project-internal reference and output paths remain stable.
- Root run artifacts are preserved under `runs/` with a migration manifest.
- Full tests and final manual QA pass without live media calls.
