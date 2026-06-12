# Issues — Prioritized Findings

Consolidated from three independent review passes, deduplicated, and spot-verified. Items marked **[verified]** were manually re-checked against the source after the review agents reported them. One agent finding (a claimed `KeyError` on the synthetic final-keyframe scene in `image_evaluation_flow.py`) was **disproved** during verification — `validate_images` passes the full `review_items` list (including the synthetic scene) as `scenes`, so `scene_by_id` always contains it — and is excluded from this report.

Severity: **C** = critical, **H** = high, **M** = medium, **L** = low.

---

## C-1. The single-writer lock is an illusion — `file_lock` is dead code **[verified]**

- **Files:** `safety_video_harness/locks.py:14-29`, `safety_video_harness/io.py`
- **Confidence:** High

`file_lock` (the context manager that actually creates the `.lock` marker) is never imported or used anywhere in the codebase — confirmed by grep. Every write path only calls `assert_unlocked`, which is a check-then-act test: it errors if a `.lock` file already exists but never creates one. Therefore:

1. No writer ever holds a lock; two concurrent processes both pass `assert_unlocked` and race on the same JSON file.
2. Even `file_lock` itself, if adopted, has a TOCTOU race: `marker.exists()` check followed by non-exclusive `write_text`.

The harness is currently single-process, so this is latent — but the project explicitly plans OMO-driven loop runners, which makes concurrent invocation realistic.

**Fix:**
```python
# locks.py — atomic acquisition
@contextmanager
def file_lock(path: Path) -> Iterator[None]:
    marker = lock_path(path)
    try:
        with marker.open("x", encoding="utf-8") as f:   # exclusive create, atomic on POSIX
            f.write("held by current process\n")
    except FileExistsError:
        raise HarnessError(f"single-writer lock is held: {marker}")
    try:
        yield
    finally:
        marker.unlink(missing_ok=True)

# io.py — actually use it
def write_json(path: Path, data: JsonObject) -> None:
    with file_lock(path):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
```
Alternatively, document the pipeline as strictly single-process and delete `file_lock` so the code stops implying a guarantee it doesn't provide.

---

## C-2. Passing scenes pollute the RALPH iteration ledger **[verified]**

- **File:** `safety_video_harness/image_evaluation_flow.py:19-36`
- **Confidence:** High

The cap guard only short-circuits when `blocked AND prior_iterations >= MAX_RALPH_ITERATIONS`. A scene with **no** blocking issues records a new ledger round on *every* `validate_images` call. Consequences:

- Iteration counts no longer mean "regeneration attempts"; they mean "times validated".
- A healthy project re-validated 20+ times makes every scene appear to have hit the cap, and `build_loop_summary` can flag never-blocked scenes as `maxed_scenes`, potentially triggering a false `stop_and_escalate`.

**Fix:** skip (or record without incrementing) rounds for unblocked scenes:
```python
blocked = bool(review.get("blocking_issues"))
if not blocked:
    counts[scene_id] = prior_iterations
    continue
if prior_iterations >= MAX_RALPH_ITERATIONS:
    counts[scene_id] = prior_iterations
    continue
```
If you want passing rounds in the evidence trail, record them under a separate counter (`validation_runs`) that does not feed the RALPH cap.

---

## C-3. Protected-path hook: naive substring match + drift from `protected_paths.json`

- **Files:** `hooks/pretooluse-protected-path-veto.py:7-12`, `hooks/protected_paths.json`
- **Confidence:** High

The hook joins `sys.argv` into one string and substring-matches a **hard-coded** list (`["AGENTS.md", "hooks/", "schemas/", "templates/"]`), while `protected_paths.json` — the supposed source of truth — also lists `approvals.json`. Problems:

- **Drift:** writing directly to `approvals.json` (bypassing `approve_gate.py`) is not vetoed.
- **Case sensitivity:** `AGENTS.MD`, `Hooks/` pass the check; macOS default filesystems are case-insensitive, so `Hooks/pretooluse-live-veto.py` writes to the real file.
- **False positives:** any unrelated path containing `schemas/` as a substring is denied.

**Fix:** have the hook load `protected_paths.json`, lowercase-normalize, and match against path-like arguments (anchored, so `nohooks` ≠ `hooks`). This removes the duplicate list entirely.

---

## H-1. `--live --execute-paid --plan-only` skips Gate 2

- **File:** `safety_video_harness/generation.py:117-131`
- **Confidence:** High

In the live branch, `plan_only` returns *before* `require_gate(project, "image_to_video")` and `_require_external_upload`. A paid live plan (`seedance_live_plan.json`) is built and written for an unapproved project, and the CLI reports success. Execution is still blocked later, but the gate's "no paid-path artifacts before approval" intent is violated, and an existing test (`test_seedance_live_plan_uses_two_five_second_clips_for_10s`) codifies the bypass by expecting exit 0 on an unapproved project.

**Fix:** move the `require_gate` + `_require_external_upload` calls above `build_seedance_live_plan`, or make plan-only an explicitly gateless dry-run mode that does not require `--live --execute-paid` (pick one semantics; today it's the worst of both).

---

## H-2. Reference scan double-loads root-level approved assets

- **Files:** `safety_video_harness/assets.py:10` (ASSET_DIRS), `approve_reference` flow
- **Confidence:** High

`approved_reference` scans `ref/approved` (the *parent* of all role subdirectories) with `glob("*")`, while `person/work/space/style/camera/lighting` roles scan the children. `approve_reference` drops approved images at the flat root. Depending on where a file lands it is injected into prompts **once or twice** (root role + sub-role), producing duplicate reference blocks. The `.md` profile scan has the same parent/child overlap.

**Fix:** make `approve_reference` require a target role subdirectory, or restrict the `approved_reference` role to files directly in `ref/approved` *only* (it already does for images via suffix filtering — the real issue is root-dropped files belonging to no role; define one canonical location per asset).

---

## H-3. Repeated-blocker thresholds disagree between arbiter and wiki

- **Files:** `safety_video_harness/evaluation_arbiter.py:120-125` (fires at total ≥ 3 — correct), `safety_video_harness/evaluation_rounds.py:263-271` (marks "repeated" at ≥ 2)
- **Confidence:** High

The arbiter escalates at three total occurrences as documented. The wiki's `Repeated Blockers` section marks a signature as repeated at two. A human (or an LLM reading the wiki, which the README explicitly recommends for regeneration decisions) sees "repeated" one round before the system escalates — and if this map is ever promoted to a decision input, escalation fires early.

**Fix:** import/inline `REPEATED_BLOCKER_THRESHOLD` in `evaluation_rounds._repeated_blockers` and use `>= 3`, or rename the wiki field to `recurring_blockers (≥2, informational)`.

---

## H-4. `record_image_output` cannot be retried and trusts the job file's output path

- **File:** `safety_video_harness/imagegen_jobs.py:28-52`
- **Confidence:** High (retry), Medium (traversal)

Two problems in one function:

- **H-4a — No retry path:** if the draft file already exists (e.g., re-running after a partial failure), it raises `draft image already exists` — and unlike generation, there is no `--regenerate` version bump here. The scene becomes unrecoverable without manual file deletion.
- **H-4b — Path traversal:** `output = project / str(job["output"])` trusts `imagegen_jobs.json`, which is *not* on the protected-path list. A tampered `"output": "../../..."` escapes the project directory; `copyfile` follows it.

**Fix:** (H-4a) on conflict, bump to the next version via the existing `_next_draft_path(..., regenerate=True)` logic; (H-4b) add `if not output.resolve().is_relative_to(project.resolve()): raise HarnessError(...)`.

---

## H-5. `video_qa` crashes with a raw `StopIteration` on non-h264 clips

- **File:** `safety_video_harness/video_qa.py:94`
- **Confidence:** High

`next(stream for ... if codec_name == "h264")` has no default. A VP9/AV1/corrupted/audio-only clip raises `StopIteration`, which escapes `run_boundary` (it only catches `HarnessError`) as a traceback.

**Fix:** `next((...), None)` then raise `HarnessError(f"no h264 video stream found in {path}")`.

---

## H-6. Source registration timestamp is hard-coded to `"dry-run"`

- **File:** `safety_video_harness/project.py:77`
- **Confidence:** High

`"registered_at": "dry-run"` is written unconditionally — real registrations get no timestamp, permanently degrading the evidence trail that the project otherwise invests heavily in.

**Fix:** accept a `dry_run: bool` and write `datetime.now(UTC).isoformat()` for real runs (matching every other timestamp in the codebase).

---

## M-1. Most image QA field scores are hard-coded 5s

- **File:** `safety_video_harness/image_qa.py` (`review_scene_image`)
- **Confidence:** High

`story_match_score`, `identity_consistency_score`, `ppe_score`, `equipment_score`, `technical_score` are constants; only `story_flow_score` (3 or 5) and the image-file checks vary. Two knock-on effects:

- The QA gate is only as strong as story-flow + file existence; the rubric scores in reports look authoritative but are placeholders.
- `MINIMUM_TOTAL_SCORE = 24` is unreachable as a failure condition outside error paths (max degradation with one variable field is 28), i.e., dead threshold.

**Fix:** either wire these scores to the actual role-evaluator outputs, or label them `"score_source": "placeholder"` in the output JSON so downstream readers (Arbiter, OMO, humans) don't over-trust them. Re-derive or remove the total-score floor accordingly.

---

## M-2. Seedance duration is patched by string replacement

- **File:** `safety_video_harness/seedance_live.py:88-91`
- **Confidence:** High

`prompt.replace("Generate a 5 second Seedance clip", f"Generate a {duration} second ...", 1)` silently no-ops if the template wording in `prompt_contract.py` ever changes, sending the wrong duration to a paid API.

**Fix:** carry `duration_sec` as a structured field in the video prompt plan and compose the final prompt at job-build time.

---

## M-3. Manual-review transcript default generates spurious blockers

- **File:** `safety_video_harness/video_qa.py:186`
- **Confidence:** High

`manifest.get("transcript_enabled", True)` blocks any inspection manifest that *omits* the key (older or externally produced manifests), even though harness-written manifests always set `False`.

**Fix:** default to `False` — absence of transcript tooling should not read as "transcript enabled".

---

## M-4. Wiki append bypasses even the weak locking that exists

- **File:** `safety_video_harness/evaluation_rounds.py:132-175`
- **Confidence:** High

`_append_wiki_summary` checks `assert_unlocked` against the `.md` path then raw-appends; the JSONL ledger write two lines earlier is a separate non-atomic operation. A crash between the two leaves ledger and wiki out of sync.

**Fix:** wrap both writes in one `file_lock` scope once C-1 is fixed.

---

## M-5. Secret-veto hook is case-sensitive and pattern-poor

- **File:** `hooks/pretooluse-secret-veto.py:6-7`
- **Confidence:** High

`re.compile(r"API_KEY|SECRET|TOKEN|Bearer ")` misses `api_key=`, `bearer`, `sk-…`, `eyJ…` (JWT), and `Bearer\t`; meanwhile `TOKEN` false-positives on benign names. As written it is a reminder, not a control.

**Fix:** `(?i)` flag plus common key-shape patterns (`sk-[A-Za-z0-9]`, `eyJ[A-Za-z0-9_-]+\.`), and scope the veto to write operations.

---

## M-6. Stop-sentinel uses a CWD-relative path

- **File:** `hooks/stop-sentinel-guard.py:8`
- **Confidence:** High

`Path(".harness/DONE")` depends on the invoker's working directory; every other hook resolves from `Path(__file__)`. Wrong CWD silently disables (or falsely enforces) the stop guard.

**Fix:** resolve from the repo root or accept `--project`.

---

## M-7. `posttooluse-*` hooks are no-ops presenting as validators

- **Files:** `hooks/posttooluse-schema-validation.py`, `hooks/posttooluse-evidence-feedback.py`
- **Confidence:** High

Both print a reminder and exit 0 regardless of input. Their filenames promise validation that never happens.

**Fix:** either invoke `scripts/validate_project.py` / evidence checks for real, or rename to `*-reminder.py` so nobody assumes coverage that doesn't exist.

---

## M-8. Corrupted PPTX renders silently as a placeholder

- **File:** `safety_video_harness/source_rendering.py:37-39`
- **Confidence:** High

The `BadZipFile` branch returns a placeholder output with an empty warning, so `entry["render_warning"]` records nothing and the operator never learns the source was unreadable.

**Fix:** return a non-empty warning string from that branch.

---

## L-1. Minor quality items

| Item | Location | Note |
|---|---|---|
| Duplicated `_latest_draft` | `image_qa.py:95` vs `imagegen_jobs.py:96` | Same logic, different return contracts; extract one shared helper |
| Dual duration keys | `project.py:187-188` | `target_seconds` and `target_duration_sec` both maintained; keep one |
| `scene_filter` applied after building all prompts | `generation.py:52-68` | Wasted work; filter `scene_items` first |
| Ledger read twice per scene per round | `evaluation_arbiter` + `evaluation_rounds` | Canonical entry: [06-latent-defects.md](./06-latent-defects.md) LD-9 |
| `dict(dict(...))` double wrap | `prompt_team.py:71` | No-op outer call |
| `debate_positions()` computed twice | `evaluation_outputs.py:53,60` | Cache the list |
| `build_loop_summary` hard-codes `"iteration": 1` | `image_qa.py:122` | Misleading top-level field; derive from counts |
| Draft path derived via `parent.parent.parent` | `image_qa.py:211` | Fragile structural assumption; pass `project` explicitly |
| Per-role blockers not filtered by criterion | `stage_role_reviews.py:83-92` | Roles carry unrelated blockers into their files |
| `error_log.append_error` never called | `error_log.py` | Wire it into `run_boundary` or remove |
| `test-seconds must be 5 or 10` message vs `% 5 == 0` check | `seedance_live.py:75-76` | Message and constraint disagree |
| `is_remicon_collision_source` substring match | `source_facts.py` | Any path containing "레미콘" matches; prefer an explicit source-type field |
