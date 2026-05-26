# Suite Manifest (`suite.yaml`)

The run manifest for a mapping-suite invocation. Tracks which sibling skills the recipe calls for, where each one's output landed, and what status each step is in. Read by `compile-combined.sh` to know what to link to.

## Schema

```yaml
suite_date: 2026-05-18
recipe: release-driver-onboarding | deployed-system-onboarding | custom
scope_doc: suite-scope.md
status: in_progress | completed | paused | failed

steps:
  - id: 1
    skill: release-analysis
    purpose: "Map how this tool drives releases for the CRM fleet"
    invocation_prompt: |
      Run release-analysis against ~/source/source-control-automation
      using scope_shape: driver-only.
      No prior arch-analysis to ingest — proceed without prior context.
    expected_output: docs/release/<date>/
    actual_output: docs/release/2026-05-17/   # filled in after completion
    status: completed                          # pending | in_progress | completed | skipped | failed
    started_at: 2026-05-17T12:14:00Z
    completed_at: 2026-05-17T13:42:00Z
    notes: "Driver-shape reframe used; 109 findings, 6 discarded, 5 drift."
    skip_reason: ~                             # populated when status: skipped
    failure_reason: ~                          # populated when status: failed

  - id: 2
    skill: doc-claim-validator
    purpose: "Verify runbook claims against current code and eve state"
    invocation_prompt: |
      Run doc-claim-validator against ~/source/source-control-automation/docs/runbooks/
      with priors at docs/release/2026-05-17/.
    expected_output: docs/audits/<date>/
    actual_output: ~
    status: pending
    started_at: ~
    completed_at: ~
    notes: ~
```

## Field semantics

### Top-level

- `suite_date` — the date the suite started (not the date each sibling ran). Used for the suite parent directory name.
- `recipe` — the named recipe or `custom` for user-defined sequences.
- `scope_doc` — relative path to `suite-scope.md` from the suite parent dir. Always `suite-scope.md` in v1.
- `status` — overall suite status. Computed from step statuses:
  - All `completed` or `skipped` → `completed`
  - Any `in_progress` → `in_progress`
  - Any `failed` (without remediation) → `failed`
  - User explicitly paused → `paused`

### Per-step

- `id` — sequential integer starting at 1. Stable across the suite's lifetime; don't renumber when a step is skipped.
- `skill` — the sibling skill's name. Must match a registered skill that the user has access to.
- `purpose` — one-sentence "why this step." Surfaces in the orchestrator's "present" output and in the combined HTML's navigation.
- `invocation_prompt` — verbatim copy of what the user types/invokes to run the sibling. Captured so the manifest is reproducible.
- `expected_output` — relative path pattern. Used to detect the sibling's actual output dir during step completion.
- `actual_output` — populated after the sibling finishes; the resolved output path. Used by `compile-combined.sh` to link.
- `status` — see lifecycle below.
- `started_at`, `completed_at` — ISO-8601 timestamps. Populated by the orchestrator at gate transitions.
- `notes` — free-form. Often a one-line summary of what the step produced (finding counts, drift counts, etc.).
- `skip_reason` — populated only when `status: skipped`. One sentence.
- `failure_reason` — populated only when `status: failed`. Captures the error so the suite can be resumed.

## Step lifecycle

```
pending  ──▶  in_progress  ──┬──▶  completed
                              ├──▶  skipped       (user opted out)
                              └──▶  failed        (sibling errored or output didn't validate)

failed ──▶  in_progress       (user retries)
failed ──▶  skipped           (user gives up on this step but continues suite)
```

Statuses are monotonic except for the `failed → in_progress` retry transition. Don't reset `completed` to `pending` — if a sibling needs re-running, append a new step (id increments) rather than mutating the original.

## Compile-combined contract

`scripts/compile-combined.sh` reads `suite.yaml` and:

1. Iterates `steps[]` in `id` order.
2. Skips steps with `status` in {`pending`, `in_progress`, `failed`, `skipped`}. Only `completed` steps appear in the combined HTML.
3. For each `completed` step, follows `actual_output` to find the sibling's HTML (or markdown fallback) and creates a navigation link.
4. Renders the combined HTML with section per step: skill name, purpose, link to standalone artifact, brief note.

If `suite.yaml` has zero `completed` steps, `compile-combined.sh` exits with a friendly error rather than producing an empty HTML.

## Mutating the manifest

The orchestrator mutates `suite.yaml` between steps. Practical points:

- **Atomic writes.** Use a temp file + rename, not in-place edits, so a partial write doesn't corrupt the manifest mid-suite.
- **Read-before-write.** The manifest is the source of truth; always re-read it before updating to avoid clobbering changes from a parallel agent (rare but possible).
- **Don't delete steps.** A skipped step is recorded as `skipped`, not removed. The manifest is the audit trail for the suite.
- **Don't edit `actual_output` after completion.** If a sibling's output moved, the manifest no longer reflects what the suite saw — open a new step or escalate to the user.

## When the suite resumes

A suite can pause and resume across sessions. To resume:

1. Read `docs/<suite-date>-suite/suite.yaml`.
2. Find the first step with `status` in {`pending`, `in_progress`, `failed`}.
3. Re-present that step's invocation prompt to the user.
4. Continue the coaching loop from there.

The orchestrator never assumes a suite is fresh. If a manifest exists at the resolved suite-date path, it's already in flight — confirm with the user before starting a parallel suite for the same date.
