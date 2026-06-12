# Architecture Improvement Opportunities

**Inputs:** the Stage-1 review ([03-issues.md](./03-issues.md)) and Stage-2 latent-defect diagnosis ([06-latent-defects.md](./06-latent-defects.md)). Every proposal below is anchored to at least one verified finding — no speculative refactors.

**Role of this document:** the structural layer of the unified action plan in [05-recommendations.md](./05-recommendations.md). Tactical fixes shipped from 05 are intentionally subsumed by these slices later (the 05 items marked *"Structural successor"*). Where a slice mentions tests, numbered references point to the master backlog in [04-test-coverage.md](./04-test-coverage.md); unnumbered test descriptions are slice-specific additions.

**Vocabulary** (used consistently throughout): a **module** is anything with an interface and an implementation; **depth** is leverage at the interface — a lot of behavior behind a small interface; a module is **shallow** when callers must know nearly as much as the implementation does; a **seam** is where an interface lives; **locality** is what maintainers gain when change, bugs, and knowledge concentrate in one place. The **deletion test**: if deleting a module makes its complexity reappear across N callers, it was earning its keep; if complexity just vanishes, it was a pass-through.

**Domain vocabulary note:** this repo has no `CONTEXT.md`. The de-facto domain glossary lives in [01-architecture-map.md](./01-architecture-map.md) and `AGENTS.md`. Slice S7 proposes promoting it to a `CONTEXT.md` so naming decisions have a single reference.

Each proposal is a **vertical slice**: independently shippable, includes its own tests, does not require the other slices (dependencies are noted where they exist).

---

## Slice S1 — Project State Store: one deep module for all state-file IO

**Recommendation strength: Strong** · resolves C-1, M-4, LD-1, LD-2 at a single seam

| | |
|---|---|
| **(1) Current problem** | `io.py` + `locks.py` form a shallow seam: callers (~25 call sites across the package) must each know the lock discipline (`assert_unlocked` vs the never-used `file_lock`), that writes are non-atomic, that `read_json` throws raw `JSONDecodeError`, and which relative path each state file lives at (`"qa" / "image_qa_loop.json"` strings are scattered). Four verified defects (C-1, M-4, LD-1, LD-2) all live at this one seam — the strongest possible signal that the interface is too thin for what callers actually need. |
| **(2) Improvement** | A deep `state.py` module (working name: **ProjectStore**) whose interface is small: `store.read(StateFile.APPROVALS)`, `store.write(StateFile.APPROVALS, data)`, `store.append_round(record)`. Behind the interface it owns: atomic write (tmp + `os.replace`), real lock acquisition (`open("x")`), corruption → `HarnessError` with file/line, torn-JSONL-tail tolerance, and the canonical relative path for every known state file. `io.py`/`locks.py` become its implementation details. |
| **(3) Impact scope** | `io.py`, `locks.py` (absorbed); mechanical import swap in ~20 modules; no behavior change for healthy files, so existing tests pass as-is. Regression tests: #6, #8, #9 in [04-test-coverage.md](./04-test-coverage.md). |
| **(4) Priority** | **1 — first.** Every other module sits on top of this seam; fixing the four defects here fixes them everywhere at once (locality), and later slices inherit the guarantees for free (leverage). |

> **Dependency on the 05 Batch 2 lock decision:** this slice as written assumes **Option A** (real locking). If Option B (single-process declaration) is chosen, S1 still stands — it then owns atomicity, corruption policy, and canonical paths only, and the lock-acquisition behavior (and test #6) drops out. The slice is worth doing under either option.

```text
Before (shallow):  25 callers ── each knows: paths + lock rules + json errors + non-atomicity
After  (deep):     25 callers ── store.read/write/append ──┐
                                                           └─ atomicity, locking, corruption policy, paths (one place)
```

---

## Slice S2 — Reference Catalog: merge the two parallel scanners

**Recommendation strength: Strong** · resolves H-2, LD-8; removes the largest duplication in the codebase

| | |
|---|---|
| **(1) Current problem** | `assets.py` and `reference_profile.py` are two implementations of the same hidden concept — "scan the reference directories and resolve each asset's description." Both iterate `ASSET_DIRS`, both glob images + orphan `.md`s, both resolve sidecars with the identical `-front`-split heuristic (`assets.py:72`, `reference_profile.py:80`), and `_has_matching_image` is **byte-for-byte duplicated** (`assets.py:83-84`, `reference_profile.py:86-87`). They have already diverged in output shape (`description` fallback text differs) and they share two bugs (H-2 parent/child double-scan, LD-8 prefix over-match) — each of which must currently be fixed twice. Deletion test: deleting either file makes the scanning complexity reappear in the other's callers → the *concept* earns a module; having two of them is the defect. |
| **(2) Improvement** | One deep `reference_catalog.py`: `load_catalog(project) -> Catalog`. The `Catalog` knows every asset's role, path, description, locked traits, and usage. `reference_assets_prompt_block` and `analyze_reference_assets` become two thin **views** over the same catalog. The parent/child directory rule (H-2) and exact profile-sidecar matching (LD-8) are decided once, inside. `approve_reference` stays separate — it is a write operation, not a scan. |
| **(3) Impact scope** | `assets.py`, `reference_profile.py` (merged); callers in `generation.py`, `prompt_contract.py`, `seedance_live.py`, `project.py` (import swap); `reference_assets.json` output shape preserved. Tests: one table-driven scan test replaces scattered coverage; H-2/LD-8 regression cases. |
| **(4) Priority** | **2.** Independent of S1; highest duplication payoff per line changed. |

---

## Slice S3 — Image Version Store: own the draft/approved version arithmetic

**Recommendation strength: Strong** · resolves LD-3, H-4 (retry), L-1 dup; protects the write-once promise

| | |
|---|---|
| **(1) Current problem** | Version arithmetic is smeared across three private helpers in two modules: `_next_draft_path` / `_next_preserved_approved` (`imagegen_jobs.py`) and a second `_latest_draft` (`image_qa.py:96` vs `imagegen_jobs.py:96` — duplicated with different return contracts: one returns `None`, one raises). The arithmetic itself is wrong at the edge (LD-3: count-based, collides after a gap), the retry path doesn't exist (H-4), and `image_qa.py:211` reconstructs the project root via `parent.parent.parent` because no module owns the layout. The interface callers actually need — "give me the latest draft", "give me a guaranteed-fresh next path", "preserve this approved file" — is tiny; the knowledge currently required to call safely is large. Classic shallow module. |
| **(2) Improvement** | One deep `image_versions.py`: `latest_draft(project, scene_id)`, `next_draft(project, scene_id)` (max+1, never collides, contained within the project — closes the H-4 traversal too), `preserve_approved(project, scene_id)`. Write-once semantics become *this module's invariant* instead of a rule every caller must remember. |
| **(3) Impact scope** | `imagegen_jobs.py`, `image_qa.py` (helpers replaced); behavior change only in the gap edge case. Tests: gap-collision regression (the LD-3 repro becomes the test), retry version bump, containment check. |
| **(4) Priority** | **3.** Small, sharply scoped, directly converts two verified defects into invariants. |

---

## Slice S4 — Evaluation Ledger: read once, decide once

**Recommendation strength: Strong** · resolves C-2, H-3, LD-9; depends on S1 for storage guarantees (can ship before it, but lands cleaner after)

| | |
|---|---|
| **(1) Current problem** | The "round ledger" concept has no owner. `evaluation_rounds.py` mixes three responsibilities — ledger IO, wiki markdown rendering, and signature counting — while `evaluation_arbiter.py` *re-implements* signature counting against the same file (`_prior_signature_counts`), with a **different threshold** than the wiki's (H-3: 3 vs 2). The file is re-read in full twice per scene per round (LD-9), and the iteration-count semantics broke (C-2) precisely because the increment decision lives in a caller (`image_evaluation_flow.py`) instead of in the module that owns the ledger. When three modules each hold a partial copy of one concept's rules, that concept is asking to be a module. |
| **(2) Improvement** | A deep `ledger.py`: `Ledger.load(project)` reads the JSONL **once**; exposes `completed_iterations(stage, item)`, `signature_counts(stage, item)`, `append(record)` and owns the single `REPEATED_BLOCKER_THRESHOLD` and the "passing rounds don't count toward the RALPH cap" rule (C-2 fix becomes an invariant, not a guard in a caller). Wiki rendering moves wholly into `evaluation_markdown.py` (it already exists for exactly this purpose — today it holds only 33 of the ~200 lines of markdown logic). |
| **(3) Impact scope** | `evaluation_rounds.py` (split), `evaluation_arbiter.py` (drops its private ledger reader), `image_evaluation_flow.py` (drops the increment guard), `evaluation_markdown.py` (gains the wiki renderer). Ledger file format unchanged. Tests: C-2 regression (repeat validation, flat counts), threshold-alignment test, single-read performance assertion (call-count spy). |
| **(4) Priority** | **4.** The most load-bearing slice for the evidence story; slightly larger than S2/S3, so it goes after them. |

```text
Before: evaluation_rounds ─┬─ ledger IO          evaluation_arbiter ── own ledger reader (threshold=3)
                           ├─ wiki rendering     image_evaluation_flow ── increment rule (broken, C-2)
                           └─ signature count (threshold=2)
After:  ledger.py ── load-once / iterations / signatures / append / thresholds / cap rule
        evaluation_markdown.py ── all wiki rendering
```

---

## Slice S5 — External Tool Runner: one seam for every subprocess

**Recommendation strength: Worth exploring** · resolves LD-4, LD-10 in one place

| | |
|---|---|
| **(1) Current problem** | Four modules call `subprocess.run` directly (`tools.py`, `video_qa.py`, `video_inspection.py`, `seedance_live.py`), each re-implementing the same pattern (`check=False`, capture, returncode → `HarnessError`) and each independently missing `timeout` (LD-4). The pattern repetition is the tell: there is an unnamed module here — "run an external tool safely." It is also the natural seam for tests, which currently monkeypatch four different call sites. |
| **(2) Improvement** | `external_tools.py`: `run_tool(command, *, timeout, env=None) -> CompletedProcess`, owning timeout + `TimeoutExpired` → `HarnessError`, process-group kill for `bash`-wrapped children, and uniform error text. ffprobe's JSON parse guard (LD-10) lives in a `run_tool_json` variant. Tests get **one** seam to fake all external tools. |
| **(3) Impact scope** | 4 call sites swapped; per-site timeout constants chosen (30s probe / 300s inspection / SLA+margin for Higgsfield). Tests: timeout → `HarnessError` (fake sleeping child), JSON-variant guard. |
| **(4) Priority** | **5.** Mechanically simple; graded "worth exploring" only because the per-tool timeout values need an operational decision (especially the paid Seedance call), not because the structure is in doubt. |

---

## Slice S6 — Seedance flow: separate *plan* from *execute*

**Recommendation strength: Worth exploring** · resolves H-1 structurally; makes Gate 2 unbypassable by construction

| | |
|---|---|
| **(1) Current problem** | `generate_seedance` in `generation.py:117-131` is one function juggling four modes (dry-run / plan-only / live / paid) with interleaved guard clauses — and the Gate 2 bypass (H-1) happened exactly because the `plan_only` early-return slipped *between* the paid-flag check and the gate check. Mixed responsibilities made the ordering of guards a bug surface. The same module also owns image generation, so `generation.py` is the package's grab-bag. |
| **(2) Improvement** | Split the seam along the domain's own vocabulary (Gate 2 separates *planning* from *paid execution*): `seedance_flow.plan(project, options)` — always allowed, never needs `--live/--execute-paid`; `seedance_flow.execute(project, plan)` — checks gate + paid flag + external-upload *inside*, as its first lines, with no mode flags to reorder. The H-1 class of bug becomes unrepresentable: there is no code path in `execute` before the gate check. |
| **(3) Impact scope** | `generation.py` (shrinks), new `seedance_flow.py`, `scripts/generate_seedance.py` flag mapping (`--plan-only` → plan; `--live --execute-paid` → execute), `seedance_live.py` unchanged underneath. The bypass-codifying test gets rewritten (see 04-test-coverage §1). CLI compatibility decision needed: keep old flags as aliases or break. |
| **(4) Priority** | **6.** Do after H-1's tactical fix (Batch 1 in [05-recommendations.md](./05-recommendations.md)) — this slice is the structural version that prevents recurrence. |

---

## Slice S7 — Domain glossary as `CONTEXT.md` + naming alignment

**Recommendation strength: Worth exploring** · low-risk; multiplies the value of every future change

| | |
|---|---|
| **(1) Current problem** | The domain vocabulary is strong in prose (`README.md`, `AGENTS.md`) but inconsistent in code. Verified drift: **round vs iteration** (`evaluation_rounds.py` writes `"iteration"` fields into things it calls *rounds*; `image_qa.py` hardcodes a top-level `"iteration": 1`); **RALPH loop vs ralph_loop vs image_qa_loop** (`qa/image_qa_loop.json` contains the `ralph_loop` object); **scene vs item vs review item** (`record_image_evaluation_rounds(scenes=...)` actually receives review items — the exact ambiguity that produced a false `KeyError` finding during Stage-1 review); **blocker vs blocking_issue vs blocker_signature** (three related-but-distinct concepts, never defined in one place). LLM agents are first-class readers of this repo (AGENTS.md-driven), and naming drift costs them context on every session. |
| **(2) Improvement** | (a) Create `CONTEXT.md` at the repo root from the glossary in [01-architecture-map.md](./01-architecture-map.md), adding the three-way blocker definition. (b) Pick one term per concept — recommended: **round** (one recorded evaluation), **iteration** (a scene's position in the RALPH loop — i.e., rounds *that counted*), **review item** (scene or synthetic final keyframe), and rename pure-internal identifiers to match. (c) Leave on-disk JSON keys unchanged in this slice (renaming persisted keys is a migration, not a rename). |
| **(3) Impact scope** | New `CONTEXT.md`; internal parameter/variable renames in `evaluation_rounds.py`, `image_evaluation_flow.py`, `image_qa.py` (no behavior change, no file-format change); `AGENTS.md` gains a pointer to `CONTEXT.md`. |
| **(4) Priority** | **7 — opportunistic.** Fold the renames into whichever of S3/S4 touches the same lines; create `CONTEXT.md` any time. |

---

## Sequencing and dependency map

```text
S1 ProjectStore ──────────┐  (foundation: storage guarantees)
S2 Reference Catalog ─────┤  independent
S3 Image Version Store ───┤  independent
S4 Evaluation Ledger ─────┘  cleaner after S1 (uses its append/torn-tail policy)
S5 External Tool Runner      independent, any time
S6 Seedance plan/execute     after the tactical H-1 fix
S7 CONTEXT.md + naming       opportunistic, ride along with S3/S4
```

**Top recommendation: start with S1.** It is the only slice that four verified defects point at simultaneously, every other module is its caller, and it changes no behavior on the happy path — pure depth gain. S2 and S3 are the best second moves: small, independent, and each converts a duplicated bug surface into a single invariant.

**What this list deliberately excludes:** the agent/skill/hook plugin layout, the gate model, the consensus/veto design, and the propose-only video policy. Those seams are correct as designed (see [02-strengths.md](./02-strengths.md)) — the defects found there are implementation bugs, not architecture problems, and are already covered by [05-recommendations.md](./05-recommendations.md).
