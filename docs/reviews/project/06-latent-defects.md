# Latent Defect Diagnosis

**Method:** `/diagnose` discipline adapted for a proactive audit (no reported bug). Instead of hypothesizing from reading alone, each suspect was either (a) **confirmed with a minimal repro script** run against the actual modules (Phase 1–2 feedback loop), or (b) classified as a **static finding** where the defect is structural and a repro adds nothing (e.g., a missing `timeout=` argument). Findings already filed in [03-issues.md](./03-issues.md) are cross-referenced, not duplicated.

The "Containment" lines below are absorbed into the unified action plan ([05-recommendations.md](./05-recommendations.md)); regression tests for these findings are items #8–#11 in the master test backlog ([04-test-coverage.md](./04-test-coverage.md)).

Defect classes requested: edge cases, unhandled exceptions, race conditions, resource leaks.

---

## Confirmed by repro (run on 2026-06-12, Python 3.14 venv)

### LD-1. One truncated ledger line bricks the entire project — **[repro confirmed]**

- **Class:** unhandled exception × non-atomic write (compound)
- **Files:** `safety_video_harness/evaluation_rounds.py:100-111` (`_read_round_entries`), `io.py:24-28` (`write_jsonl`)
- **Severity:** High

`write_jsonl` appends without atomicity; a crash or kill mid-append leaves a truncated final line. `_read_round_entries` then raises a raw `json.JSONDecodeError` on every subsequent read.

**Repro:** wrote a ledger with one valid line + one truncated line, called `completed_iterations()` →
```
JSONDecodeError: Unterminated string starting at: line 1 column 20
```

**Blast radius:** `completed_iterations` is called by every `validate_images`, `validate_video`, and arbiter run. One interrupted write permanently breaks all QA commands for that project, with no hint which file is at fault and no recovery path short of hand-editing the JSONL.

**Containment:** in `_read_round_entries`, catch `JSONDecodeError` per line; treat a corrupt **final** line as a torn append (skip + warn), but raise `HarnessError` naming the file/line number for corruption elsewhere. Optionally `fsync` after append.

---

### LD-2. Corrupted JSON state files crash with raw tracebacks — `run_boundary` never sees them — **[repro confirmed]**

- **Class:** unhandled exception
- **Files:** `io.py:14-15` (`read_json`), `cli.py:9-16` (`run_boundary`)
- **Severity:** High

`read_json` propagates `json.JSONDecodeError` and `FileNotFoundError` as-is. `run_boundary` only catches `HarnessError`, so every one of the 30 CLI scripts dumps a raw traceback when any state file (`approvals.json`, `scenes.json`, `project_config.json`, …) is corrupt or missing.

**Repro:** wrote `{"gates": {` to a file, called `read_json` inside `run_boundary` → uncaught `JSONDecodeError` traceback, not a clean exit-1 message.

**Why this matters more here than usual:** `write_json` (`io.py:18-21`) is itself non-atomic (`write_text` directly to the target), so the harness can *produce* the corrupt file that later bricks it — LD-1 and LD-2 are two halves of one failure story. `approvals.json` corrupted mid-write means Gate state is unreadable.

**Containment:**
1. `read_json`: wrap and re-raise as `HarnessError(f"unreadable JSON state file: {path}: {e}")` (keep `from e`).
2. `write_json`: write to `path.with_suffix(".tmp")` then `os.replace()` — atomic on POSIX, eliminates torn state files entirely.

---

### LD-3. Draft version numbering collides after any gap — **[repro confirmed]**

- **Class:** edge case
- **File:** `safety_video_harness/imagegen_jobs.py:86-93` (`_next_draft_path`), same pattern at `:103-106` (`_next_preserved_approved`)
- **Severity:** Medium

Next version = `len(existing) + 1`, i.e., derived from the **count** of files, not the **max** version. Any gap (operator deletes a bad draft, partial cleanup, crash between glob and write) makes the "next" path equal an existing file.

**Repro:** with `sc01_v002.png` and `sc01_v003.png` present (v001 deleted), `_next_draft_path(..., regenerate=True)` returned `sc01_v003.png` — which already exists.

**Blast radius:** the imagegen job spec points at an existing draft; `record_image_output` then hard-fails with `draft image already exists` (and per issue H-4 there is no retry path), wedging the scene. For `_next_preserved_approved` the same arithmetic could target an existing preserved approval — colliding with the project's write-once promise.

**Containment:** compute `max(int(p.stem.rsplit("_v", 1)[1]) for p in existing) + 1` instead of `len + 1`. Same fix in both functions.

---

## Static findings (structural; no repro needed)

### LD-4. No `timeout=` on any subprocess call — hang risk on every external tool

- **Class:** resource leak / liveness
- **Files:** `tools.py:25` (tesseract), `video_qa.py:192` (ffprobe), `video_inspection.py:118` (inspection skills via bash), `seedance_live.py:130` (Higgsfield CLI)
- **Severity:** High (the Seedance site is a *paid* call with no upper bound)

All four `subprocess.run` sites omit `timeout`. ffprobe on a malformed MP4, tesseract on a pathological image, a wedged Higgsfield CLI network call, or an inspection bash script waiting on stdin will hang the harness indefinitely — and in an OMO loop context, hang the loop runner with it. `capture_output=True` makes it worse: a child that blocks writing nothing gives no visible progress signal.

**Containment:** add per-site timeouts (`ffprobe`/`tesseract`: 30s; inspection scripts: 300s; Higgsfield: generation SLA + margin), catch `subprocess.TimeoutExpired`, re-raise as `HarnessError` naming the command. Note: `subprocess.run(timeout=...)` kills the direct child but `bash`-wrapped grandchildren can survive — for `video_inspection._run`, use `start_new_session=True` and kill the process group on timeout.

### LD-5. `_run_understand_video` destroys previous output before securing the new one

- **Class:** edge case / destructive window
- **File:** `video_inspection.py:84-90`
- **Severity:** Medium

Sequence: run tool → `shutil.rmtree(output)` (deletes the previous inspection evidence) → `shutil.move(generated, output)`. If the move fails (cross-device link, permission, name collision), the old evidence is already gone and the new breakdown is stranded at `clip.with_name(f"{clip.stem}-breakdown")`. For an evidence-first harness, deleting evidence before its replacement is in place is the wrong order.

**Containment:** move the new breakdown to `output.with_suffix(".new")` first, then swap (`rmtree` old only after the new directory is in place), or `os.replace`-style two-step rename.

### LD-6. `assert_unlocked`/`file_lock` race — already filed as **C-1**

- **Class:** race condition — see [03-issues.md](./03-issues.md) C-1/M-4. Listed here for completeness of the race-condition class: there are no *other* shared-state races in the codebase precisely because everything funnels through `write_json`/`write_jsonl`; fixing C-1 closes the class.

A second, smaller TOCTOU exists between gate *check* and paid *execution*: `generate_seedance` validates Gate 2 (`require_gate`) and then runs the CLI; nothing rechecks the gate per job in a multi-job plan. Acceptable today (single operator), worth one line in `_run_cli` if approvals ever become revocable mid-run.

### LD-7. Scene-link validator hard-codes index-based identity

- **Class:** edge case
- **File:** `scene_links.py:26-34`
- **Severity:** Medium

`_review_scene_link` derives expectations purely from list position (`sc{index:02d}` / `sc{index+1:02d}`), while the scene's own `id` is reported but never reconciled. Consequences at the edges:

- A storyboard whose scenes are ordered `sc02, sc01` (or use any other id scheme) passes/fails based on position with misleading messages naming the wrong scene.
- An **empty** scene list produces `reviews=[]`, `passed=true` — `validate_scene_links` succeeds on a storyboard with zero scenes, and Gate 2's clip-count check is the only thing standing behind it.

**Containment:** assert `scene.get("id") == f"sc{index:02d}"` as its own blocker, and fail on an empty scene list.

### LD-8. Cast-profile sidecar glob over-matches on filename prefixes

- **Class:** edge case
- **Files:** `assets.py:72`, `reference_profile.py:80`
- **Severity:** Low

`path.stem.split('-front')[0]` + `glob(f"{stem}*.profile.md")` means `worker-001-front.png` matches `worker-001.profile.md` **and** `worker-0010.profile.md`, `worker-001b.profile.md`, etc. With ≥10 cast members using this naming scheme, the wrong identity profile silently joins the prompt — an identity-lock harness injecting the wrong identity is a quiet quality failure, not a crash.

**Containment:** match exactly `f"{base}.profile.md"`, falling back to a delimiter-anchored pattern.

### LD-9. Ledger grows without bound and is re-read in full, twice per scene per round

*(Canonical entry — the L-1 table row in [03-issues.md](./03-issues.md) points here.)*

- **Class:** resource (performance) — scaling cliff, not a leak
- **Files:** `evaluation_arbiter.py` (`_prior_signature_counts`), `evaluation_rounds.py` (`_repeated_blockers`, `completed_iterations`)
- **Severity:** Low today; Medium once C-2 is fixed and projects live long

Every arbiter decision and every round record re-reads and re-parses the entire `evaluation_rounds.jsonl`. With C-2 unfixed (passing scenes append rounds on every validation), ledger growth is super-linear in usage, making this O(n²) pattern bite sooner. No file handles leak (`read_text` closes), but parse cost compounds.

**Containment:** read the ledger once per `validate_images` invocation and thread the entries through; or maintain per-scene cursor files.

### LD-10. ffprobe success-path JSON parse is unguarded

- **Class:** unhandled exception (minor sibling of LD-2)
- **File:** `video_qa.py:209-211`
- **Severity:** Low

After the `returncode != 0` check, `json.loads(result.stdout)` assumes well-formed output. ffprobe writing warnings to stdout with `-of json` is rare but observed in the wild with exotic containers; the result is a raw `JSONDecodeError`. One `try/except` → `HarnessError` closes it. (The missing-h264 `StopIteration` two lines later is already filed as H-5.)

---

## Resource-leak sweep result

Explicitly checked and **clean**:
- `PIL.Image.open` is used inside a `with` block (`image_qa.py:241`) — no handle leak.
- All file reads/writes use `read_text`/`write_text`/context-managed handles — no dangling descriptors.
- `subprocess.run` with `capture_output` — no pipe leaks (the risk is hanging, LD-4, not leaking).
- No threads, no sockets, no tempfile usage outside tests.

## Summary table

| ID | Class | Severity | Verified | One-line containment |
|----|-------|----------|----------|----------------------|
| LD-1 | Unhandled exception + torn append | High | repro | Tolerate torn last line; raise `HarnessError` otherwise |
| LD-2 | Unhandled exception + non-atomic write | High | repro | `read_json`→`HarnessError`; `write_json`→tmp+`os.replace` |
| LD-3 | Edge case (version gap) | Medium | repro | max-version+1, not count+1 |
| LD-4 | Hang / liveness | High | static | `timeout=` + `TimeoutExpired`→`HarnessError` on all 4 sites |
| LD-5 | Destructive window | Medium | static | Secure new output before deleting old |
| LD-6 | Race condition | — | cross-ref | Same fix as C-1 |
| LD-7 | Edge case (index vs id, empty list) | Medium | static | Reconcile id with index; fail empty storyboard |
| LD-8 | Edge case (glob prefix) | Low | static | Exact-match profile sidecar |
| LD-9 | Scaling cliff | Low→Med | static | Single ledger read per invocation |
| LD-10 | Unhandled exception | Low | static | Guard ffprobe JSON parse |
