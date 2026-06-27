# Recommendations — Unified Action Plan

**This is the single execution document for the whole review.** [03-issues.md](./03-issues.md) and [06-latent-defects.md](./06-latent-defects.md) diagnose; [07-architecture-improvements.md](./07-architecture-improvements.md) designs; regression tests live in the master backlog ([04-test-coverage.md](./04-test-coverage.md) §Suggested, referenced below as "test #N"); the per-finding cross-reference table is in [README.md](./README.md) §Traceability.

Work is organized in **three layers**, and the overlap between them is intentional, not duplicated effort:

| Layer | What it is | Source |
|---|---|---|
| **Tactical fix** | Smallest change that removes the defect now | Batches below |
| **Containment** | Defensive guard that limits blast radius | 06 "Containment" lines, absorbed into the batches below |
| **Structural** | Deep-module refactor that makes the defect class unrepresentable | 07 slices S1–S7 |

A tactical fix shipped today is *expected* to be absorbed later by its structural slice (e.g., the C-2 guard in `image_evaluation_flow.py` moves into the ledger module when S4 lands). Ship tactical first; let the slice subsume it.

Ordered by (risk × effort). Each batch is independently shippable; IDs refer to 03 (C/H/M/L) and 06 (LD).

## Batch 1 — Correctness of the safety story (do first, ~half a day)

1. **C-2** Stop recording RALPH rounds for passing scenes (3-line guard in `image_evaluation_flow.py`) + test #1. Highest value-per-line fix in the codebase: it protects the meaning of the entire evidence ledger. *(Structural successor: S4.)*
2. **H-1** Move `require_gate`/`_require_external_upload` ahead of `build_seedance_live_plan` in the live branch; replace the bypass-codifying test with test #2. *(Structural successor: S6.)*
3. **H-5** Replace the bare `next(...)` with a defaulted lookup + `HarnessError` in `video_qa.py`.
4. **H-6** Real timestamp in `register_source`.
5. **LD-4** Add `timeout=` to all four `subprocess.run` sites and convert `TimeoutExpired` → `HarnessError` (test #10). The Seedance site is a *paid* call with no upper bound today — this belongs in the first batch even though the polished version (process-group kill, shared runner) waits for S5. **Open operational decision:** per-tool timeout values, especially the Higgsfield SLA + margin.

## Batch 2 — State durability and locking (~half a day)

Two separable concerns that the earlier drafts of this plan blurred together; they are now explicit:

6. **Unconditional — atomicity and corruption handling (LD-1, LD-2).** Regardless of any locking decision:
   - `write_json` → write to a tmp file, then `os.replace` (test #9).
   - `read_json` → wrap `JSONDecodeError`/`FileNotFoundError` as `HarnessError` naming the file.
   - `_read_round_entries` → tolerate a torn final JSONL line, raise on corruption elsewhere (test #8).
7. **Decision required — locking (C-1, M-4, LD-6).** Pick one:
   - *Option A (recommended if OMO loops may ever run concurrently):* make `file_lock` atomic (`open("x")`), route `write_json`/`write_jsonl`/wiki-append through it, add test #6.
   - *Option B:* declare the harness single-process in `AGENTS.md`, delete `file_lock`, and rename `assert_unlocked` to something honest like `assert_no_crash_marker`.
   Either option is fine; the current state (dead lock code implying protection) is the only wrong choice. **Note:** slice S1 in 07 assumes Option A; under Option B, S1 still stands but owns only atomicity, corruption policy, and canonical paths — the slice is worth doing either way.

## Batch 3 — Hook hardening (~half a day)

8. **C-3** Protected-path hook reads `protected_paths.json`, lowercases, anchors matches. Delete the hard-coded list (test #3).
9. **M-5** Case-insensitive secret patterns + key-shape regexes.
10. **M-6** Resolve the stop-sentinel from the repo root, not CWD.
11. **M-7** Rename or implement the `posttooluse-*` no-ops.

## Batch 4 — Operator-path robustness (~1 day)

12. **H-4a/H-4b** `record_image_output`: version-bump on retry (test #5) + containment check on the output path (test #4). *(Structural successor: S3.)*
13. **LD-3** Version arithmetic: max-version+1 instead of count+1 in `_next_draft_path` and `_next_preserved_approved` (test #11). *(Structural successor: S3.)*
14. **H-2** One canonical location per reference asset; stop double-injecting root-level approved files. *(Structural successor: S2.)*
15. **LD-8** Exact-match cast-profile sidecar glob (no prefix over-match). *(Structural successor: S2.)*
16. **M-2** Structured `duration_sec` instead of prompt string surgery in `seedance_live.py`.
17. **M-3** Default `transcript_enabled` to `False`.
18. **M-8** Non-empty warning for corrupted PPTX.
19. **LD-5** `_run_understand_video`: secure the new breakdown before deleting the old inspection output.
20. **LD-7** Scene-link validator: reconcile scene `id` with list index; fail on an empty scene list.
21. **LD-10** Guard the ffprobe success-path JSON parse. *(Structural successor: S5.)*

## Batch 5 — Honesty of the QA signal (design work, schedule deliberately)

22. **M-1** The hard-coded 5s in `review_scene_image` are the biggest gap between what the system *reports* and what it *knows*. Until role evaluators produce real scores, label placeholder scores as such in every output JSON (`"score_source": "placeholder"`), and drop or recompute `MINIMUM_TOTAL_SCORE`. When LLM-based role evaluation lands, these fields become real with no schema change.
23. **H-3** Align the wiki repeated-blocker threshold with the arbiter's (3), since the README tells future sessions to *use the wiki* for regeneration decisions. *(Structural successor: S4.)*

## Batch 6 — Hygiene (fold into other PRs opportunistically)

24. The L-1 table in [03-issues.md](./03-issues.md): shared `_latest_draft` helper, single duration key, early scene filtering, `pytest.skip` for fixture-gated tests (test #7), wire or remove `error_log.append_error`.
25. **LD-9** Single ledger read per invocation (canonical entry in 06; absorbed by S4 if that slice ships first — skip the tactical version in that case).

## Structural track (parallel, after Batch 1–2)

The seven slices in [07-architecture-improvements.md](./07-architecture-improvements.md) are the structural layer of this same plan — start with **S1 (ProjectStore)**, then S2/S3 in either order. Slices subsume the tactical fixes marked with *"Structural successor"* above; when a slice lands, delete the tactical guard it replaces rather than keeping both.

## What NOT to change

- The gate architecture, the consensus/veto ordering, the propose-only video policy, the write-once approval semantics, and the evidence-bundle isolation pattern are all correct as designed. Fix the bugs *inside* them; do not redesign them.
- Don't add narration/TTS, parallel imagegen, or auto-regeneration of video while fixing the above — the current restraints are the product.
