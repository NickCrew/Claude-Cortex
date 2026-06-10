---
name: wiring-audit
description: User-triggered audit that finds wiring drift between a project's UI surfaces and backend capabilities — orphan surfaces (UI calls endpoints/hooks/procedures that no longer exist), unwired capabilities (backend routes/exports that nothing surfaces), shape drift (both exist but contracts mismatch), method drift (URL matches, HTTP verb does not), validation drift (frontend vs backend rules diverged), permission drift (UI exposes what backend forbids or vice versa), stale labels (UI text references renamed backend concepts), and unsurfaced configuration (env vars or flags that gate behavior with no UI or CLI to control them). This skill should be used when the user asks to "audit our wiring," "find UI/backend drift," "find unwired capabilities," "find stale surfaces," "check for contract violations," "find unused endpoints," "find unused hooks," "what mismatches between UI and backend," or any similar request whose deliverable is a prioritized findings report rather than a descriptive snapshot. Generic across UI frameworks but optimized for React applications (hooks, fetch, react-query, SWR, tRPC, server actions, react-router, Next.js). Not for descriptive architectural snapshots (use architectural-analysis), security audits (use security-auditor), or performance audits (use the performance-optimization skills).
keywords:
  - wiring audit
  - audit our wiring
  - UI backend drift
  - unwired capabilities
  - stale surfaces
  - contract violations
  - unused endpoints
  - unused hooks
---

# Wiring Audit

## Overview

Diff a project's *consumed* surface (UI buttons, components, hooks, fetch calls, tRPC client invocations, GraphQL queries, server actions) against its *produced* capability (route handlers, hook exports, tRPC routers, GraphQL resolvers, exported async functions) and report every mismatch as a prioritized finding with citations on both sides.

The audit's load-bearing claim: every UI consumption should match exactly one backend production, and every production should be consumed somewhere. Orphans, drift, and gaps are the failure modes. The report is the punch list.

## When to use

Trigger this skill when the user asks for:

- A wiring/drift audit ("audit our wiring," "find drift")
- Identification of unused or orphan code on the wire (unused endpoints, unused hooks)
- Verification that backend capabilities are surfaced ("what's not exposed in the UI?")
- Verification that UI surfaces are wired ("is anything in the UI broken or stale?")
- Contract violation detection between FE and BE
- Stale label detection (UI copy that lies about what the backend does)

Do not trigger for:

- Descriptive architectural snapshots (use `architectural-analysis`)
- Security review (use `security-auditor` or `/security-review`)
- Performance audit (use the performance-optimization skills)
- Test coverage audit (use `test-review`)

## Workflow

Six phases. The diff (phase 3) is the load-bearing one — the rest are supporting work to feed it accurate inputs.

### 1. Scope

Establish:

- **Target**: full repo, or a frontend-path and backend-path pair in a monorepo, or a single full-stack project (Next.js, Remix, etc.).
- **Stack detection**: identify FE framework (React + which router, which data layer) and BE framework (Express, Fastify, Hono, Next.js routes/route handlers/server actions, tRPC, GraphQL). The signal-set in `references/react-patterns.md` and `references/capability-enumeration.md` adapts based on what's detected.
- **Output root**: `docs/audits/<YYYY-MM-DD>/` — create now if missing.
- **Priors**: if `docs/architecture/<recent-date>/` exists from a previous architectural-analysis run, the UI-surfaces and integrations reports can be passed as priors to skip rediscovery (saves sub-agent time).

### 2. Dispatch enumerators (parallel)

Two sub-agents, dispatched in a single message with two `Agent` tool calls (parallel, one-shot, no `team_name`):

- **Surface enumerator** (`general-purpose`, sonnet) — walks UI, returns the consumed-set per `references/surface-enumeration.md`.
- **Capability enumerator** (`general-purpose`, sonnet) — walks backend, returns the produced-set per `references/capability-enumeration.md`.

Both return YAML registries (see `references/audit-protocol.md` for the contract). Both need sonnet because correlation reasoning across full files matters here — `Explore` excerpt reads aren't sufficient.

### 3. Drift detection (orchestrator)

Read `references/drift-detection.md`. The orchestrator:

1. Builds consumption and production maps keyed by `(kind, identifier)`.
2. Computes set differences (orphans on each side).
3. For matched pairs, runs shape/method/auth/validation comparison.
4. Each mismatch becomes a candidate finding tagged with one of the 8 categories from `references/finding-categories.md`.

### 4. Severity assignment

Apply the rubric in `references/finding-categories.md`:

| Severity | Default applies to | Override when |
|---|---|---|
| **broken** | orphan-surface, method-drift | Surface is dead code (no callers itself) — downgrade to stale |
| **drifted** | shape-drift, validation-drift, permission-drift | Auth-bypass flavor → upgrade to broken |
| **stale** | stale-label | Public-facing user surface → upgrade to drifted |
| **gap** | unwired-capability, unsurfaced-config | Capability is brand-new (recent commit) → annotate "expected, planned" |

### 5. Verify

Every finding's citation must resolve. Use codanna (when `.codanna/` exists) or grep + `Read` to confirm:

- The cited UI line exists and contains the asserted consumption.
- The cited backend line exists and contains (or fails to contain, for orphan claims) the asserted capability.
- For "stale label" findings, confirm the asserted-renamed backend symbol actually exists at the new location.

Discard findings whose citations fail to resolve. Maintain a discard log for the report's verification section.

### 6. Render report (and optional wiring graph)

- Author `docs/audits/<date>/report.md` per `references/report-template.md`.
- Persist raw registries: `docs/audits/<date>/registries/surfaces.yaml` and `capabilities.yaml`. These let future audits diff against them (compare-to-history is a future v2 feature).
- Optionally author `docs/audits/<date>/wiring.mmd` showing surface→capability with broken edges highlighted in red, unwired capabilities in amber.
- If the wiring graph is authored, run `bash scripts/render.sh docs/audits/<date>/` to produce `wiring.svg`.

## Output layout

```
docs/audits/2026-05-10/
├── report.md                          ranked findings, severity-grouped
├── wiring.mmd                         optional supplemental graph
├── wiring.svg                         optional, run scripts/render.sh
└── registries/
    ├── surfaces.yaml                  raw consumed-set
    └── capabilities.yaml              raw produced-set
```

## Strict citation policy

Every finding must carry path:line citations on both sides where applicable:

- **UI side citation** for the consumption (the `fetch` call, `useQuery` invocation, hook import, form submission, etc.).
- **Backend side citation** for the production (the route handler, exported function, tRPC procedure definition).
- For orphan-surface findings, the backend side citation is replaced by a grep-evidence line ("`grep -rn 'route /api/old' server/` returned 0 matches").
- For unwired-capability findings, the UI side is replaced similarly.
- For stale-label findings, both the UI label location *and* the renamed backend symbol's new location are cited.

Fabricated "missing X" claims are the dominant failure mode for audits — sub-agents over-fire on absence. The verification protocol grep-checks every absence claim before the finding is recorded.

## React focus

Generic by design but optimized for React. The signal catalog in `references/react-patterns.md` covers:

- Hook naming conventions and custom hook unwrapping
- React Query / SWR / Apollo / urql data layer signals
- tRPC client patterns (and the type-safety caveat)
- Next.js server actions (capabilities, not routes)
- React Router and Next.js routing (loaders, actions)
- Form action patterns
- Permission-aware rendering vs backend authorization

For non-React targets, the same workflow applies but the FE-side signal catalog is sparser. Tell the user up front if the UI-side detection will be limited.

## Resources

- `references/audit-protocol.md` — workflow phases, registry contracts, sub-agent prompts
- `references/surface-enumeration.md` — UI consumption discovery (generic + React-aware)
- `references/capability-enumeration.md` — backend capability discovery (Node.js HTTP, Next.js, tRPC, GraphQL)
- `references/drift-detection.md` — the diff algorithm in detail
- `references/finding-categories.md` — 8 categories, severity rubric, evidence requirements
- `references/react-patterns.md` — React-specific signal catalog
- `references/report-template.md` — ranked findings report skeleton
- `scripts/render.sh` — render `wiring.mmd` to `wiring.svg` via `mmdc`
- `scripts/verify-findings.sh` — quick path:line existence check over a findings report
