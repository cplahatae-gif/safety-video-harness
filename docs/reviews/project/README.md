# Project Review — Safety Video Harness

**Review dates:** 2026-06-12
**Branch reviewed:** `codex/session-anchor-mas-evaluation` (HEAD `2a91849`)
**Scope:** All 40 modules in `safety_video_harness/` (~4,400 LOC), 30 CLI scripts, 9 hooks, 21 test files, schemas, and plugin config.
**Method:** Three stages. **Stage 1** — three parallel independent code-review passes (core pipeline / QA-evaluation subsystem / scripts-hooks-tests) with manual spot-verification of every critical finding; one reported finding was disproved and excluded. **Stage 2** — latent-defect diagnosis (`/diagnose` discipline): suspects confirmed with minimal repro scripts or classified as static findings. **Stage 3** — architecture deepening analysis anchored to the verified findings.

## Verdict

The harness is a well-architected, safety-first orchestration layer. Its core promise — *no paid generation without explicit gates, storyboard-first ordering, never overwrite approved artifacts, evidence for everything* — is genuinely enforced in the Python library layer, not just documented. Defense-in-depth is real: even if every hook were deleted, `require_gate` / `--execute-paid` / `external_upload_allowed` checks in the library still block live **execution** (one exception on the planning side: `--plan-only` currently writes a paid-path plan before the gate check — issue H-1).

The weaknesses concentrate in five areas:

1. **The locking story is an illusion** — `file_lock` is dead code; `assert_unlocked` is a check-then-act pattern that protects nothing under concurrency (C-1).
2. **State files are not durable** — non-atomic writes can corrupt `approvals.json`/the JSONL ledger, and one torn line bricks every QA command with a raw traceback (LD-1, LD-2 — both repro-confirmed).
3. **The RALPH iteration ledger is polluted by passing scenes** — re-validating a healthy project inflates iteration counts toward the 20-round cap (C-2).
4. **No external call has a timeout** — ffprobe, tesseract, inspection scripts, and the *paid* Higgsfield CLI can all hang the harness indefinitely (LD-4).
5. **The hooks are weaker than the library** — substring matching, case sensitivity, and a hard-coded list that has already drifted from `protected_paths.json` (C-3).

None of these break the single-user, single-process happy path that the project currently runs. All of them matter as soon as the harness is reused, parallelized, or trusted by someone who didn't write it.

## Document index

| File | Role | Contents |
|---|---|---|
| [01-architecture-map.md](./01-architecture-map.md) | Orientation | Zoom-out map: layers, modules, callers, domain glossary |
| [02-strengths.md](./02-strengths.md) | Diagnosis | What is genuinely well done (keep doing this) |
| [03-issues.md](./03-issues.md) | Diagnosis | Stage-1 issues (C/H/M/L) with file:line and fixes |
| [04-test-coverage.md](./04-test-coverage.md) | Diagnosis + **master test backlog** | What the 21 test files guarantee, the gaps, and the numbered regression-test list all other docs reference |
| [05-recommendations.md](./05-recommendations.md) | **Single execution plan** | Unified three-layer action plan (tactical / containment / structural) |
| [06-latent-defects.md](./06-latent-defects.md) | Diagnosis | Latent defects (LD-1…LD-10) — 3 repro-confirmed, 7 static |
| [07-architecture-improvements.md](./07-architecture-improvements.md) | Design | Structural layer: 7 vertical slices (S1–S7) |

## Traceability matrix

Major findings only (criticals, highs, and repro-confirmed/High LDs). Columns: where diagnosed → tactical fix in the action plan → structural slice that subsumes it → regression test in the master backlog.

| Finding | Summary | Diagnosed | 05 Action | 07 Slice | 04 Test |
|---|---|---|---|---|---|
| C-1 / M-4 / LD-6 | Lock is dead code; TOCTOU | 03, 06 | Batch 2 #7 (A/B decision) | S1 | #6 |
| C-2 | Passing scenes pollute RALPH ledger | 03 | Batch 1 #1 | S4 | #1 |
| C-3 | Protected-path hook bypassable + drifted | 03 | Batch 3 #8 | — | #3 |
| H-1 | `--plan-only` skips Gate 2 | 03 | Batch 1 #2 | S6 | #2 |
| H-2 | Reference double-injection | 03 | Batch 4 #14 | S2 | — (S2 tests) |
| H-3 | Repeated-blocker threshold drift (3 vs 2) | 03 | Batch 5 #23 | S4 | — |
| H-4a / H-4b | `record_image_output` no-retry / traversal | 03 | Batch 4 #12 | S3 | #5 / #4 |
| H-5 | `StopIteration` on non-h264 clip | 03 | Batch 1 #3 | S5 | — |
| H-6 | `registered_at: "dry-run"` hard-coded | 03 | Batch 1 #4 | — | — |
| LD-1 | Torn JSONL line bricks project *(repro)* | 06 | Batch 2 #6 | S1 | #8 |
| LD-2 | Non-atomic writes + raw tracebacks *(repro)* | 06 | Batch 2 #6 | S1 | #9 |
| LD-3 | Version-gap collision *(repro)* | 06 | Batch 4 #13 | S3 | #11 |
| LD-4 | No subprocess timeouts (incl. paid call) | 06 | Batch 1 #5 | S5 | #10 |
| M-1 | Placeholder QA scores presented as real | 03 | Batch 5 #22 | — | — |

## Summary scorecard

| Dimension | Rating | Note |
|---|---|---|
| Safety-gate architecture | ★★★★★ | Library-level enforcement, two-factor paid flag, real tests (one plan-only gap, H-1) |
| Evidence / auditability | ★★★★☆ | JSONL ledger + wiki + bundles; ledger pollution bug (C-2) |
| State-file durability | ★★☆☆☆ | Non-atomic writes; one torn line bricks the project (LD-1/LD-2) |
| Concurrency correctness | ★★☆☆☆ | Lock is check-only dead code (C-1) |
| External tool invocation | ★★☆☆☆ | No timeouts on any of 4 subprocess sites, incl. the paid one (LD-4) |
| Hook layer robustness | ★★☆☆☆ | Bypassable substring matching, config drift (C-3) |
| Code organization | ★★★★☆ | Small focused modules, consistent patterns, some duplication (S2/S3 targets) |
| Test quality | ★★★★☆ | Real red/green safety tests; gaps on hooks and plan-only path |
| Real QA signal | ★★★☆☆ | Most image scores are hard-coded 5s; only story-flow + file checks are real (M-1) |
