---
id: TASK-13
title: Fix flaky test_specialist_review_falls_back_to_gemini_when_claude_fails
status: To Do
assignee: []
created_date: '2026-04-23 05:22'
updated_date: '2026-04-23 05:26'
labels:
  - test
  - bug
  - agent-loops
  - flaky
dependencies: []
references:
  - 'tests/unit/test_agent_loops_review_scripts.py:110'
  - 'tests/unit/test_agent_loops_review_scripts.py:188'
  - skills/agent-loops/scripts/specialist-review.sh
priority: low
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The test `test_specialist_review_falls_back_to_gemini_when_claude_fails` in `tests/unit/test_agent_loops_review_scripts.py` (line 110) fails with:

```
FileNotFoundError: [Errno 2] No such file or directory: '.../claude.log'
```

The test expects a `claude.log` file to be created during the fake Claude invocation (to verify `--print` was passed), but the log file is never created in the test temp directory. The actual `--print` assertion at line 188 is what trips, because the file that should contain the command-line trace doesn't exist.

**Confirmed pre-existing:** Failure reproduces at commit `bdaef17` (before the multi-specialist-review extraction session) with identical error. The rename from `test-review-request.sh` to `diff-test-audit.sh` did not cause this.

**Likely cause:** Test harness uses a fake `claude` stub that's supposed to write its invocation args to `claude.log` before exiting. Either:
1. The fake stub isn't being installed into PATH before `specialist-review.sh` runs, so the real `claude` (or no-op) runs and no log is written.
2. The fake stub is running but its output redirection is broken (e.g., path not writable).
3. The test's environment setup has drifted from what `specialist-review.sh` expects.

**Adjacent tests that do pass:** The 3 tests that passed in the same run were the `_review_provider_detect_self_uses_*_cli_env_markers` tests, which test `review-provider.sh` directly without running `specialist-review.sh`. So the issue is specific to the specialist-review flow's test scaffolding.

**Scope:** Only the Claude-fallback tests appear affected. Codex/Gemini explicit-provider tests (line 400, 482, 588, 700, 784) weren't run in the stopping-after-first-failure mode, so their status is unknown.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The test passes locally with `uv run pytest tests/unit/test_agent_loops_review_scripts.py::test_specialist_review_falls_back_to_gemini_when_claude_fails`
- [ ] #2 Root cause identified (stub not installed vs. redirection broken vs. other)
- [x] #3 Audit the remaining specialist-review tests in the same file and confirm they pass or file separate follow-ups for any that also fail
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
**Full test-file audit (183.80s, 15 tests, 1 fail / 14 pass):**

- ✅ `test_review_provider_detect_self_uses_gemini_cli_env_markers`
- ✅ `test_review_provider_detect_self_uses_codex_cli_env_markers`
- ✅ `test_review_provider_detect_self_uses_claude_cli_env_markers`
- ❌ `test_specialist_review_falls_back_to_gemini_when_claude_fails`
- ✅ `test_specialist_review_auto_keeps_self_provider_last`
- ✅ `test_specialist_review_auto_detects_gemini_self_provider_from_cli_env`
- ✅ `test_test_review_request_supports_explicit_gemini_provider`
- ✅ `test_test_review_request_auto_keeps_self_provider_last`
- ✅ `test_test_review_request_auto_detects_gemini_self_provider_from_cli_env`
- ✅ `test_specialist_review_supports_explicit_codex_provider`
- ✅ `test_test_review_request_supports_explicit_codex_provider`
- ✅ `test_test_review_request_normalizes_provider_preamble_and_section_aliases`
- ✅ `test_specialist_review_normalizes_provider_preamble`
- ✅ `test_specialist_review_normalizes_code_review_section_aliases`
- ✅ `test_test_review_request_preserves_invalid_artifact_when_normalization_fails`

**Failure is well-isolated.** The diff-test-audit tests (formerly test-review-request) all pass, confirming the rename didn't cause regressions. Other specialist-review tests with fake-claude stubs also pass, including ones that check for `--print` in logs. The failing test is specifically the **Claude-fails-fallback-to-Gemini** path.

**Narrowed diagnosis:** Tests that exercise fake-claude *succeeding* all pass and write claude.log correctly. The failing test is the one where fake-claude is configured to *fail* (non-zero exit). The claude.log expected at line 188 is missing in that path, suggesting the failure-simulation stub either (a) exits before logging, or (b) uses a different log-writing mechanism than the success-simulation stub. Compare the fake-claude implementations in this test vs. the passing tests to find the divergence.
<!-- SECTION:NOTES:END -->
