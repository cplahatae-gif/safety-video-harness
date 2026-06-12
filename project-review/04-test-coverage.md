# Test Coverage Assessment

21 test files. Overall character: the suite tests the *safety contracts* with genuine red/green pairs (and keeps the transcripts in `evidence/`), which is rare and valuable. The gaps cluster around the hook layer and a few paths the tests accidentally codify as correct.

## Well covered (with the test that proves it)

| Guarantee | Test |
|---|---|
| Live image/video without gate approval fails with correct stderr | `test_mvp_flow.py`, `test_roadmap_bundle2.py` |
| RALPH cap: 20 pre-seeded ledger rounds → `max_iterations_reached` | `test_image_ralph_loop.py::test_image_qa_stops_ralph_after_max_iterations` |
| Repeated-blocker escalation on the 3rd identical signature | `test_evaluation_arbiter.py::test_validate_images_escalates_after_three_repeated_blockers` |
| Approved images preserved (rename, not overwrite) on re-approval | `test_roadmap_bundle2.py` (two tests) |
| Seedance guardrails: `--execute-paid` required, 10s cap, ≤3 attempts, validation-run⇒max-attempts=1 | `test_seedance_live_guardrails.py` |
| URL redaction in Seedance run logs | `test_seedance_live_guardrails.py::test_seedance_live_run_log_redacts_public_output_url` |
| Critical safety veto overrides consensus majority | `test_evaluation_arbiter.py::test_critical_safety_veto_overrides_consensus` |
| Single-writer lock blocks approval writes (the `assert_unlocked` path) | `test_roadmap_bundle1.py::test_approval_write_respects_single_writer_lock` |
| Korean/space paths end-to-end | remicon fixture tests under pytest `tmp_path` |
| Subtitle/no-narration contract | `test_subtitle_contract.py`, `test_no_narration_contract.py` |
| Storyboard density/quality contracts | `test_storyboard_density.py`, `test_storyboard_quality.py`, `test_story_flow_quality.py` |

## Gaps

### 1. A test codifies the Gate 2 plan-only bypass (ties to issue H-1)
`test_seedance_live_guardrails.py::test_seedance_live_plan_uses_two_five_second_clips_for_10s` runs `--live --execute-paid --plan-only` on a project **without** gate approval and asserts `returncode == 0`. When H-1 is fixed, this test must change; today it actively protects the bypass.

### 2. Hook layer is almost untested
- `pretooluse-protected-path-veto.py`: no tests (no case-insensitivity test, no `approvals.json` drift test).
- `pretooluse-secret-veto.py`: no tests at all.
- `stop-sentinel-guard.py`: no test, including the CWD-dependence (M-6).
- `posttooluse-*`: no behavioral tests — consistent with them being no-ops (M-7); any "does it run" test would pass even if deleted.
- Only `pretooluse-live-veto.py` and `session-start-anchor.py` get coverage via `test_plugin_structure.py`.

### 3. Ledger semantics under repeated validation (ties to C-2)
No test calls `validate_images` repeatedly on a *passing* project and asserts iteration counts stay flat. That is exactly the scenario where the cap pollution bug bites.

### 4. Concurrency / lock acquisition
The lock test only exercises `assert_unlocked` against a manually created `.lock` file. Nothing tests `file_lock` acquisition/release (it's dead code, C-1) or two competing writers.

### 5. Vacuously passing video tests
Several tests in `test_video_qa.py` / `test_video_regeneration_proposals.py` begin with `if not source.exists(): return` — on a machine without the MP4 fixture they pass while testing nothing. Use `pytest.skip("fixture missing")` so skipped coverage is visible in the test report.

### 6. Path traversal in `record_image_output` (ties to H-4)
No test feeds a tampered `imagegen_jobs.json` output path and asserts containment within the project directory.

### 7. Retry/idempotency of operator commands
No test re-runs `record_image_output` for the same scene (the current behavior — hard failure with no recovery path — is itself issue H-4a).

## Suggested new tests (in priority order)

> **This list is the master regression-test backlog.** [05-recommendations.md](./05-recommendations.md), [06-latent-defects.md](./06-latent-defects.md), and [07-architecture-improvements.md](./07-architecture-improvements.md) reference these by number instead of restating them.

1. `test_validate_images_does_not_increment_iterations_for_passing_scenes` — re-run validation N times, assert `current_iterations` unchanged (C-2 regression guard).
2. `test_seedance_plan_only_requires_gate` — replace the current bypass-codifying expectation (H-1).
3. `test_protected_path_veto_matches_json_and_is_case_insensitive` — parametrized over `protected_paths.json` entries, upper/lower variants (C-3).
4. `test_record_image_output_rejects_paths_outside_project` (H-4b).
5. `test_record_image_output_retry_bumps_version` (H-4a).
6. `test_file_lock_blocks_second_writer` — once C-1 lands (skip if 05 Batch 2 chooses Option B / single-process).
7. Convert fixture-gated video tests to `pytest.skip`.
8. `test_ledger_tolerates_torn_final_line` — truncated last JSONL line is skipped with a warning, earlier corruption raises `HarnessError` (LD-1).
9. `test_write_json_is_atomic` — simulate a crash between tmp write and replace; assert the original file is intact (LD-2).
10. `test_subprocess_timeout_raises_harness_error` — fake hanging child process per tool-runner site (LD-4).
11. `test_next_draft_path_skips_version_gaps` — with v002/v003 present and v001 deleted, next path must not collide (LD-3; the repro in 06 becomes this test).
