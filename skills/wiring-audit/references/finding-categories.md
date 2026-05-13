# Finding Categories

The 8 categories of wiring drift the audit detects. Every finding belongs to exactly one category. Severity defaults follow the rubric below; severity overrides are documented in the finding entry.

Findings use callout prefix `W-` (Wiring). IDs increment from `W-1`.

## The 8 categories

### 1. Orphan surface

**Definition:** UI consumes a capability that doesn't exist on the backend.

**Default severity:** broken

**Detection:**
- Consumption identifier `(kind, identifier)` not present in production map.
- No near-match in production map (Levenshtein > 2).

**Evidence required:**
- UI side citation (the consumption call).
- Grep evidence that the identifier is absent in the backend subtree.

**Examples:**
- `fetch('/api/users')` but backend only has `/api/v2/users`.
- `trpc.users.list.useQuery()` but backend renamed to `trpc.users.findAll`.
- Component imports `useDeleteProject` from a hook module that no longer exports it.

**Severity overrides:**
- **stale**: when the surface is dead code (the component/hook is itself never used). Bug is real but inert.
- **drifted**: when a near-match exists (Levenshtein ≤ 2 or known case-style variant) — re-classify as method-drift or stale-rename.
- **mediated**: when the orphan'd value reaches the backend via a different trigger (form library, cycle-coupled batch persistence, URL-as-state, batched mutation). The setter looks dead but the input works. See `drift-detection.md` § Mediated persistence calibration for the indirect-persistence probe. Findings tagged `mediated` need manual review — they're not bugs, but they're not certified clean either; the orchestrator surfaces them so a human can confirm the indirect path is intentional.

### 2. Unwired capability

**Definition:** Backend exposes a capability that nothing in the UI consumes.

**Default severity:** gap

**Detection:**
- Production identifier not present in consumption map.

**Evidence required:**
- Backend side citation.
- Grep evidence that the identifier is absent in the UI subtree.

**Examples:**
- `app.get('/api/admin/audit', ...)` with no fetch caller.
- tRPC procedure `users.export` defined but no client call.
- Server action `archiveProject` exported but no `<form action={archiveProject}>` or direct call.
- WebSocket event `project:lock` registered but no client subscriber.

**Severity overrides:**
- **broken**: capability is announced (in changelog, README, public API docs) as available but never wired — this is a release-promise bug.
- **stale** when capability is dead code (still exported but the only test coverage is for the capability itself; no integration test exercises it).

### 3. Method drift

**Definition:** URL identifier matches but HTTP method differs.

**Default severity:** broken

**Detection:**
- Same `(http, path)` exists on both sides but with different method.
- For tRPC: same procedure path but `query` on one side and `mutation` on the other.

**Evidence required:**
- Both citations.
- Both methods captured.

**Examples:**
- UI `fetch('/api/users', { method: 'POST' })`, backend has only `GET /api/users`.
- UI uses `useMutation` against a tRPC procedure defined as `.query()`.

### 4. Shape drift

**Definition:** Both sides exist; response shape (or input shape) doesn't match.

**Default severity:** drifted

**Detection:**
- Matched pair has shapes captured on both sides.
- Field-by-field diff finds: missing field, extra required field, type mismatch, or case-style rename.

**Evidence required:**
- Both citations.
- The diffed shapes (both sides) excerpted in the finding.

**Examples:**
- UI expects `{ name, email }`, backend returns `{ first_name, last_name, email }`.
- UI passes `{ projectId }`, backend handler reads `{ project_id }`.
- UI handles `data.items: User[]`, backend returns `data: User[]` (envelope mismatch).

**Severity overrides:**
- **broken**: when the missing field is the only one the UI uses (the consumption code path crashes immediately).
- **stale**: when the consumption ignores the field anyway (UI receives it, doesn't read it; bug is latent).

### 5. Validation drift

**Definition:** Frontend and backend validation rules diverged for the same field.

**Default severity:** drifted

**Detection:**
- Both sides have explicit validation (zod/yup/joi/manual) for the same field on the same identifier.
- Constraints differ: max length, min/max value, regex, required-vs-optional, allowed values.

**Evidence required:**
- Both citations.
- Both schemas excerpted.

**Examples:**
- FE allows email up to 320 chars, BE caps at 100.
- FE `age: z.number().min(0)`, BE `age: z.number().min(13).max(120)`.
- FE optional, BE required (form submits successfully but backend rejects with 422).

### 6. Permission drift

**Definition:** UI's permission gate disagrees with backend's authorization check.

**Default severity:** drifted

**Detection:**
- Either UI gates the surface behind a permission check while backend has `auth: none`, or backend requires a role/scope the UI doesn't gate on.
- Heuristic comparison on the gating expression.

**Evidence required:**
- UI permission signal (or absence).
- Backend auth requirement (or absence).

**Examples:**
- UI: `if (user.role === 'admin') { <DeleteAccountButton /> }`. Backend: route has no auth check. UI hides the button but backend would let anyone call it.
- UI: button always visible. Backend: rejects non-admins. UI shows the button to users who can't actually use it.

**Severity overrides:**
- **broken**: backend `auth: none` while UI gates (auth-bypass) — upgrade urgency.
- **stale**: UI gates and backend gates with different but compatible expressions — annotate but lower severity.

### 7. Stale label

**Definition:** UI text references a backend concept that has been renamed.

**Default severity:** stale

**Detection:**
- Heuristic: a noun phrase from a `user_label` doesn't appear in current capability evidence, but a near-match (Levenshtein ≤ 3, or a known rename pattern) does.

**Evidence required:**
- UI label location and text.
- Backend symbol's *new* location (the renamed concept).
- Confidence: `low` by default — heuristic detection.

**Examples:**
- Button "Save Draft" but backend action renamed from `saveDraft` to `commitPending`.
- Help text mentions "the user's avatar" but backend field renamed from `avatar` to `profile_image_url`.

**Severity overrides:**
- **drifted**: public-facing user surface (landing page, signup flow) — labels that lie cause real user confusion.
- **broken**: when the label is part of a contract (e.g., button label rendered into an email or invoice) and a downstream system depends on the label string.

### 8. Unsurfaced config

**Definition:** An env var or config key gates backend behavior with no UI/CLI/admin surface to control it, and no documentation.

**Default severity:** gap

**Detection:**
- Capability of kind `env_var_consumer` or `config_key_consumer`.
- No surface in the UI references the same var/key (no settings page, no admin form).
- No documentation in `.env.example`, `config.example.*`, or README.

**Evidence required:**
- Backend citation (where the var/key is read).
- Grep evidence of absence in UI and docs.

**Examples:**
- `process.env.ENABLE_BETA_BILLING` checked in code, no admin toggle, not in `.env.example`.
- `config.features.experimental_search` read by handlers, no config UI exposes it.

**Severity overrides:**
- **drifted**: when documentation exists but is contradictory or stale.
- **stale**: when the var/key is read but the code path is dead (always-false gate, never reached).

## Severity rubric

| Severity | Meaning | Action timeline |
|---|---|---|
| **broken** | Runtime failure imminent or certain. Users hit a 404, 500, or visible bug. | Fix before next deploy. |
| **drifted** | Works in some cases, fails in others. Contracts mismatched, validation gaps. | Fix before next release. |
| **mediated** | Looks orphan but indirect-persistence probe found a likely cycle-coupled / form-library / URL-state path. Not a bug; needs manual confirmation. | Review when convenient; close as not-a-finding once confirmed intentional. |
| **stale** | Cosmetic or latent. Labels lie, but the wire still carries data. | Fix opportunistically. |
| **gap** | Capability or config exists but unsurfaced. No bug yet, but feature is invisible. | Fix as feature work. |

## Severity priority sort

Within the report, findings are grouped by severity (broken first, then drifted, then stale, then gap), then by category, then by ID. Each finding gets a P-ranking inferred from severity:

- broken → **P0**
- drifted → **P1**
- mediated → **P2** (manual review)
- stale → **P2**
- gap → **P3**

The report's frontmatter aggregates `by-severity` counts.

## Confidence vs severity

Confidence and severity are independent. A `broken` finding can have `confidence: low` (heuristic detection of a possible orphan) or `confidence: high` (definitive grep returned zero matches across the backend). The report shows both: severity drives ordering; confidence drives whether the reader treats the finding as actionable or speculative.

A finding with `severity: broken, confidence: low` should usually be presented as: "if this consumption is hit, the call would 404 — but the consumption itself may be dead code; confirm by running the surface."
