# Strengths — What Is Done Well

These are patterns worth preserving as the harness grows. Each item names the file(s) that implement it.

## 1. Defense-in-depth on paid/live generation (the project's best property)

The "no live without approval" promise is enforced at **three independent layers**, so deleting any one layer does not break the guarantee:

- **Library layer** — `generation.py` calls `require_gate()` and `_require_external_upload()` inside `generate_images`/`generate_seedance`; `generate_seedance` additionally hard-fails without `--execute-paid` *before* any gate check (`generation.py:117`).
- **Hook layer** — `hooks/pretooluse-live-veto.py` vetoes live commands behaviorally.
- **Policy layer** — `omo_ralph.py` puts Seedance on the loop runner's forbidden-actions list, and `video_qa.py` always writes `paid_generation_allowed: false` with "Do not regenerate automatically" in every proposal.

`--execute-paid` as a second factor on top of `--live` is exactly right for a paid API.

## 2. Gates are real checks, not flags

`gates.approve_gate` re-runs the full storyboard QA (`_require_storyboard_qa`) before recording Gate 1 — a failing storyboard cannot be approved. `gate_validation.py` enforces Gate 2 with five independent conditions: `external_upload_allowed`, clip count, `video_prompts.json` existence, approved image files present, and `image_qa_loop.json` passing. Partial image-QA coverage cannot reach video.

## 3. Approved artifacts are write-once

`imagegen_jobs.approve_image` never overwrites: the existing approved file is renamed to a versioned preserved name before the new draft is copied in (`_next_preserved_approved`). Draft recording uses version-bumped filenames (`scNN_vNNN.png`). Combined with the evidence ledger, this gives a full rollback trail. Tested end-to-end in `test_roadmap_bundle2.py`.

## 4. Evidence and auditability as a design value

- Append-only JSONL ledger (`qa/evaluation_rounds.jsonl`) makes iteration counts and blocker history survive restarts and partial runs.
- Per-round evidence bundles (`evaluation_rounds.write_evaluation_bundle`) let an isolated evaluator score without the generator's context — the generator never approves its own output.
- The human-readable wiki (`llm-wiki/evaluation-rounds.md`) accumulates scores, blockers, improvement notes, and next-prompt memory per round.
- `seedance_live._redact_public_urls` scrubs URLs from run logs before persistence (tested).
- The repository's own `evidence/` folder of red/green test transcripts shows the discipline was actually practiced, not just documented.

## 5. Consensus design with a correct veto

`evaluation_consensus.decision()` handles `critical_veto` *before* any majority logic — a single safety/continuity critical veto cannot be outvoted. The documented rule ("all approve, or N-1 approve plus one conditional") is implemented exactly. `test_evaluation_arbiter.py::test_critical_safety_veto_overrides_consensus` proves it.

## 6. Escalation instead of brute-force regeneration

The blocker-signature mechanism (`blocker_signatures.py` + `evaluation_arbiter._repeated_blockers`) converts "the same failure three times" into a structural escalation (`revise_storyboard` + `regeneration_delta`) rather than a 4th identical regeneration. This is the right economics for image-vs-storyboard cost asymmetry, and the arbiter-side threshold math (prior + current ≥ 3) is correct.

## 7. Consistent operational skeleton

- All 30 scripts use the same `cli.run_boundary` pattern: `HarnessError` → clean stderr message → exit 1. No raw tracebacks for expected failures.
- All file handling uses `pathlib.Path` — Korean and space-containing paths (which this repo itself lives under) work without any string-splitting hazards.
- `from __future__ import annotations` and small, single-purpose modules (median ~100 LOC) throughout.
- JSON contracts have schemas (`schemas/*.json`) and a project-template directory.

## 8. Domain modeling quality

`source_facts.py` and `storyboard.py` encode genuine EHS domain knowledge (blind spots, signal-person positioning, reverse operation, BCT/dump-truck distinctions), with citations threaded from source extraction into each scene node. `validation.py` enforces the no-Korean-text-in-keyframes contract (regex on `image_prompt_en`, subtitle length caps, narration-field prohibition) — directly on-mission for subtitle-based delivery.

## 9. Tests that earn their keep

The suite tests failure paths, not just happy paths: live-without-gate exits non-zero with the right stderr, the RALPH cap test pre-seeds 20 ledger entries, the repeated-blocker test seeds two prior rounds and asserts escalation on the third, and the no-overwrite tests assert the preserved-file rename. Red/green evidence transcripts exist for most of these. (Gaps are listed in [04-test-coverage.md](./04-test-coverage.md) — including one test that currently *codifies* the Gate 2 plan-only bypass, issue H-1; praise for the suite does not extend to that expectation.)
