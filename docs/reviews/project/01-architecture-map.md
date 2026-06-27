# Architecture Map (Zoom-Out)

One layer above the code: what the modules are, who calls whom, and the project's domain vocabulary.

## Domain glossary

| Term | Meaning |
|---|---|
| **Harness** | The orchestration layer itself. Controls ordering, evidence, approvals, and quality loops — it does not generate media itself. |
| **Storyboard** | The reference contract (`storyboard/scenes.json`). Images and video must never get ahead of it. |
| **Gate 1 / Gate 2** | `storyboard` approval (re-runs storyboard QA) and `image_to_video` approval (requires cost disclosure, `external_upload_allowed`, full image QA coverage). |
| **RALPH loop** | Early-stopping image regeneration loop: max 20 iterations per scene, stops immediately on pass. |
| **Blocker signature** | Normalized identity of a QA failure. Three repeats of the same signature on the same scene escalates to storyboard/reference/prompt revision instead of regeneration. |
| **Role evaluators** | Parallel per-criterion reviewers (story match, identity, PPE, equipment, story flow, technical…). |
| **Arbiter** | Aggregates role reviews under a consensus rule (all approve, or one conditional). Critical safety/continuity veto overrides any majority. |
| **Evidence bundle** | Self-contained JSON given to an isolated evaluator so the generator never approves its own output. |
| **propose_only** | Video QA failure mode: paid video is never auto-regenerated; the harness only writes regeneration proposals. |
| **OMO** | External loop runner/task manager. Reads harness QA outputs and picks the next command; never judges quality itself. |
| **Sliding chain** | Continuity rule: scene N's end keyframe must equal scene N+1's start keyframe so adjacent clips share a frame. |

## Layer diagram

```text
┌────────────────────────────────────────────────────────────────────┐
│ OPERATOR LAYER                                                     │
│  scripts/*.py (30 entry points)  — argparse → library call         │
│  All wrapped by cli.run_boundary (HarnessError → exit 1)           │
├────────────────────────────────────────────────────────────────────┤
│ BEHAVIORAL GUARD LAYER (hooks/, advisory + veto)                   │
│  pretooluse-live-veto · protected-path-veto · secret-veto          │
│  session-start-anchor · stop-sentinel-guard · posttooluse-* (noop) │
├────────────────────────────────────────────────────────────────────┤
│ PIPELINE LAYER (safety_video_harness/)                             │
│  project → source_rendering/source_facts → storyboard              │
│  → prompt_team → prompt_contract → generation                      │
│  → imagegen_jobs (record/approve)  → seedance_live                 │
├────────────────────────────────────────────────────────────────────┤
│ QA / EVALUATION LAYER                                              │
│  storyboard_qa · image_qa · video_qa · video_inspection            │
│  stage_role_reviews → evaluation_consensus → evaluation_arbiter    │
│  image_evaluation_flow → evaluation_rounds (JSONL ledger + wiki)   │
│  blocker_signatures · gates/gate_validation · costs · omo_ralph    │
├────────────────────────────────────────────────────────────────────┤
│ FOUNDATION LAYER                                                   │
│  io (read/write_json[l]) · locks · errors · error_log · validation │
│  assets (reference scanning) · style_guides · reference_profile    │
└────────────────────────────────────────────────────────────────────┘
```

## Pipeline stages and their owning modules

Fixed 17-step order (from README). Mapping to code:

| Stage | Entry script | Library module(s) |
|---|---|---|
| Project init & source registration | `init_project.py`, `register_sources.py` | `project.py` |
| PPTX rendering & topic extraction | `render_pptx_sources.py`, `extract_topics.py`, `select_topic.py` | `source_rendering.py`, `source_facts.py`, `project.py` |
| Reference intake & style DNA | `search_references.py`, `approve_reference.py`, `analyze_reference_assets.py`, `extract_style_dna.py` | `assets.py`, `reference_profile.py`, `style_guides.py` |
| Storyboard | `plan_storyboard.py` | `storyboard.py` (remicon-aware scene plans from `source_facts.py`) |
| Storyboard QA + Gate 1 | `evaluate_storyboard.py`, `approve_gate.py` | `storyboard_qa.py`, `gates.py` |
| Image prompt team preflight | `plan_image_prompt_team.py` | `prompt_team.py` (lead-style → scene agents → arbiter → coordinator) |
| Image prompts & jobs | `generate_images.py` | `generation.py`, `prompt_contract.py`, `imagegen_jobs.py` |
| Image recording & approval | `record_image_output.py`, `approve_image.py` | `imagegen_jobs.py` (versioned drafts, preserved approvals) |
| Image QA / RALPH | `validate_images.py`, `plan_omo_image_ralph.py` | `image_qa.py`, `image_evaluation_flow.py`, `omo_ralph.py` |
| Scene-link validation | `validate_scene_links.py` | `scene_links.py` (sliding chain) |
| Gate 2 + cost | `approve_gate.py`, `estimate_video_cost.py` | `gates.py`, `gate_validation.py`, `costs.py` |
| Seedance dry-run / live | `generate_seedance.py` | `generation.py`, `seedance_live.py` (Higgsfield CLI, `--execute-paid`) |
| Video inspection & QA | `inspect_video.py`, `validate_video.py` | `video_inspection.py`, `video_qa.py` (propose_only) |
| Subtitles (no narration/TTS) | `plan_subtitles.py` | `subtitles.py` |

## Evaluation machinery — call graph

```text
validate_images (generation.py)
 ├─ _image_review_items → scenes + synthetic final-keyframe scene
 ├─ review_scene_image (image_qa.py)         # real checks: story_flow + image file
 └─ record_image_evaluation_rounds (image_evaluation_flow.py)
     ├─ completed_iterations (evaluation_rounds.py)   # reads JSONL ledger
     ├─ image_role_reviews (stage_role_reviews.py)    # split into role verdicts
     ├─ aggregate_arbiter_decision (evaluation_arbiter.py)
     │   ├─ consensus_result / debate_triggers (evaluation_consensus.py)
     │   ├─ _repeated_blockers ← blocker_signatures.py + ledger history
     │   └─ writes qa/arbiter_decisions/... + qa/debates/...
     ├─ write_evaluation_bundle → qa/evaluation_bundles/image/scNN/round_NNN.json
     └─ record_evaluation_round → qa/evaluation_rounds.jsonl + llm-wiki/evaluation-rounds.md
```

Storyboard QA and video QA reuse the same spine (`stage_role_reviews` → consensus → arbiter → rounds), with stage-specific reviewers in `storyboard_qa.py` / `video_qa.py`.

## State files (per project)

| File | Writer | Role |
|---|---|---|
| `project_config.json` | `project.py`, `storyboard.py` | duration, density, style guide, cost policy |
| `approvals.json` | `gates.py` | Gate 1 / Gate 2 state — the single enforcement checkpoint |
| `storyboard/scenes.json` | `storyboard.py` | the reference contract |
| `prompts/image_prompts.json`, `video_prompts.json`, `imagegen_jobs.json` | `generation.py`, `imagegen_jobs.py` | generation work orders |
| `qa/evaluation_rounds.jsonl` | `evaluation_rounds.py` | append-only machine ledger (iteration counts, blocker history) |
| `qa/image_qa_loop.json` | `image_qa.py` | RALPH status consumed by Gate 2 and OMO |
| `llm-wiki/evaluation-rounds.md` | `evaluation_rounds.py` | human/LLM learning notes per round |
| `.harness/DONE` | operator | stop-sentinel for session guard |

## Where to look first when something breaks

- **A live call ran when it shouldn't have** → `gates.require_gate`, `generation.py` live branches, then hooks.
- **Iteration counts look wrong** → `evaluation_rounds.completed_iterations` + the ledger JSONL (see issue C-2).
- **Duplicate/missing reference blocks in prompts** → `assets.py` directory roles (parent/child overlap, see H-2).
- **A scene is stuck regenerating** → arbiter decisions under `qa/arbiter_decisions/image/<scene>/` and `blocker_signatures`.
