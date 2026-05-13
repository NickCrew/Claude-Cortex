# Report Template

The skeleton for `docs/audits/<date>/report.md`. The report is a prioritized findings list — broken first, gap last — with citations on both sides for every finding.

## Structure

Eight sections. Front-loaded so a reader who only reads the first screen sees the highest-severity findings.

```markdown
---
date: <YYYY-MM-DD>
target: <repo or path>
fe-stack: <react | next | remix | vue | other>
be-stack: <express | next | trpc | graphql | other>
total-findings: <N>
by-severity:
  broken: <N>
  drifted: <N>
  mediated: <N>
  stale: <N>
  gap: <N>
by-category:
  orphan-surface: <N>
  unwired-capability: <N>
  method-drift: <N>
  shape-drift: <N>
  validation-drift: <N>
  permission-drift: <N>
  stale-label: <N>
  unsurfaced-config: <N>
priors_used: <true | false>
---

# Wiring Audit — <YYYY-MM-DD>

## Summary

<3–6 sentences: the headline state of the wiring. State the count of broken
findings, the most concerning category, any cross-cutting pattern that shows
up. Don't summarize each finding — that's the body.>

## Scope

- Target: <repo or path>
- Frontend: <stack and entry path>
- Backend: <stack and entry path>
- Excluded: <list anything skipped — test fixtures, dev-only routes, archived code>
- Priors: <if architectural-analysis priors were loaded, name the report date>

## P0 — Broken

<Sorted by category, then ID. Each finding gets a sub-section.>

### W-1  Orphan surface — `GET /api/old-users`

| Field | Value |
|---|---|
| Severity | broken |
| Category | orphan-surface |
| Confidence | high |
| UI side | `src/components/UserList.tsx:18` |
| Backend side | (absent) — `grep -rn "/api/old-users" server/` returned 0 matches |
| Identifier | `GET /api/old-users` |

**Evidence (UI):**

```tsx
const { data } = useQuery({ queryKey: ['users'], queryFn: () => fetch('/api/old-users') })
```

**Suggested fix:**

The endpoint appears to have been renamed to `/api/users` in commit `<hash>`. Update the consumption:

```diff
- queryFn: () => fetch('/api/old-users')
+ queryFn: () => fetch('/api/users')
```

If multiple consumers exist, consider extracting a `usersUrl` constant.

> **Before triaging an orphan-surface finding:** verify there is no indirect persistence path. If the orphan'd value is fed into a form library, persisted via a cycle-coupled handler (regenerate / save-all / submit), or read via URL state, the wire is mediated, not broken. See the indirect-persistence probe in `drift-detection.md`. If a probe match was found, this finding would carry severity `mediated` instead of `broken`.

---

### W-2  Method drift — `POST /api/projects`

| Field | Value |
|---|---|
| Severity | broken |
| Category | method-drift |
| Confidence | high |
| UI side | `src/components/CreateProject.tsx:24` (POST) |
| Backend side | `server/routes/projects.ts:42` (PUT) |
| Identifier | `/api/projects` |

**Evidence (UI):**

```tsx
fetch('/api/projects', { method: 'POST', body: JSON.stringify(input) })
```

**Evidence (backend):**

```ts
app.put('/api/projects', createProject)
```

**Suggested fix:**

Either change the UI to PUT, or change the route to POST. The handler name `createProject` suggests POST is intended; the route was likely changed to PUT inadvertently.

---

## P1 — Drifted

<Same structure for shape-drift, validation-drift, permission-drift findings.>

### W-3  Shape drift — `GET /api/users/:id`

| Field | Value |
|---|---|
| Severity | drifted |
| Category | shape-drift |
| Confidence | high |
| UI side | `src/components/UserProfile.tsx:14` |
| Backend side | `server/routes/users.ts:67` |
| Identifier | `GET /api/users/:id` |

**UI shape (expected):**

```ts
{ name: string; email: string }
```

**Backend shape (actual):**

```ts
{ first_name: string; last_name: string; email: string; createdAt: Date }
```

**Diff:**

- `name` (UI) → no equivalent on backend; backend has `first_name` + `last_name`.
- `email` matches.
- `createdAt` (BE) → unused by UI (not a finding).

**Suggested fix:**

Either:
- Backend adds a computed `name` field (`first_name + ' ' + last_name`), or
- UI consumes `first_name + ' ' + last_name` directly.

The first is cheaper if multiple consumers expect `name`.

---

## P2 — Stale

<Stale-label findings.>

### W-4  Stale label — "Save Draft"

| Field | Value |
|---|---|
| Severity | stale |
| Category | stale-label |
| Confidence | low |
| UI side | `src/components/Editor.tsx:88` |
| Backend candidate | `server/actions/posts.ts:23` (`commitPending`) |
| Inferred rename | "saveDraft" → "commitPending" |

**Evidence (UI):**

```tsx
<Button onClick={savePost}>Save Draft</Button>
```

**Backend evidence (current):**

```ts
export async function commitPending(post: PendingPost) { ... }
```

**Suggested fix:**

If "Save Draft" is the user-facing language and "commit pending" is internal jargon, the label is fine — close as not-an-issue. If the rename was supposed to be reflected in the UI, change to "Commit Pending" or update both to a unified term.

---

## P3 — Gap

<Unwired capabilities and unsurfaced configuration.>

### W-5  Unwired capability — `archiveProject` server action

| Field | Value |
|---|---|
| Severity | gap |
| Category | unwired-capability |
| Confidence | high |
| Backend side | `app/actions.ts:42` |
| UI side | (absent) — `grep -rn "archiveProject" src/` returned 0 matches |
| Identifier | `server-action archiveProject` |

**Evidence (backend):**

```ts
'use server'
export async function archiveProject(projectId: string) { ... }
```

**Notes:**

- Capability was added in commit `<hash>` on `<date>`; possibly not yet wired up by design.
- No UI form, no direct call, no mention in any README or docs.

**Suggested fix:**

Either wire up a UI surface (likely a button on the project settings page), or remove the unused export. If this is in-progress feature work, leave a TODO at the export site noting the planned UI.

---

### W-6  Unsurfaced config — `ENABLE_BETA_BILLING`

| Field | Value |
|---|---|
| Severity | gap |
| Category | unsurfaced-config |
| Confidence | high |
| Backend side | `server/billing/index.ts:12` |
| Surface side | (absent) — no admin toggle, not in `.env.example` |

**Evidence (backend):**

```ts
if (process.env.ENABLE_BETA_BILLING === 'true') {
  // beta path
}
```

**Suggested fix:**

Either:
- Document in `.env.example` with a comment explaining the flag.
- Add an admin settings toggle.
- If always-on or always-off in practice, remove the gate.

---

## Wiring graph

<Optional — if `wiring.mmd` was authored.>

See `wiring.svg` for the visual graph showing surface→capability with broken edges in red and unwired capabilities in amber.

## Methodology

This audit was produced by the `wiring-audit` skill. Two parallel sub-agents enumerated UI surfaces and backend capabilities; the orchestrator computed the diff, applied severity, and verified every citation.

- Sub-agents: <2 (general-purpose, sonnet)>
- Citations verified: <N total — discarded <M> as unresolvable, <K> as fabricated absence claims>
- Priors: <true | false — if true, name the architectural-analysis report date>

## Verification log

### Discarded findings

- <bad citation> — <asserted label> — reason: <e.g., evidence didn't match cited line; absence claim refuted by grep>

### Synthesized inferences

<Stale-label findings, near-match orphan upgrades, and any heuristic-driven
detections list here with their inference path.>

## Open questions

<Architectural questions surfaced by the audit but not findings themselves.
These are seeds for follow-up.>

- Is `archiveProject` (W-5) intended to be wired, or is it dead code?
- The `ENABLE_BETA_BILLING` flag (W-6): is it a runtime kill-switch or a deploy-time toggle? Treatment depends on the answer.
```

## Authoring rules

- **Sort findings by severity desc, then category, then ID.** Always P0 first.
- **Every finding cites both sides** (or grep evidence for the absent side).
- **Suggested fix is mandatory.** A finding without an actionable fix isn't useful triage. If you don't know the fix, name the question that needs answering.
- **Confidence visible per finding.** Readers calibrate action by confidence × severity.
- **Don't aggregate.** Each finding is its own entry. A pattern affecting 5 endpoints becomes 5 findings, with a cross-reference noting the pattern in the summary.
- **No findings without callouts.** The frontmatter's `total-findings` matches the count of `W-N` entries. Off-by-one means you missed a section.

## Length

Most reports run 4–10 pages depending on codebase size. Reports exceeding 30 findings should add a "Pattern" section in the summary highlighting cross-cutting issues — readers can't triage 30+ individual findings without help.

## Filename

Always `report.md`. Don't customize.
