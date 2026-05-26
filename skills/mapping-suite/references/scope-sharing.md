# Scope Sharing (`suite-scope.md`)

The seam that lets every sibling skill in a mapping-suite run inherit the same scope without each one re-resolving it. Phase 0 of the orchestrator writes this file once; sibling skills read it during their own Phase 0/Phase 1.

## Schema

```markdown
---
suite_date: 2026-05-18
recipe: release-driver-onboarding | deployed-system-onboarding | custom
scope: <human-readable scope description, copied from prior arch-analysis or user-supplied>
target_repo: <path or paths — multi-repo unions encoded as ~/source/{a,b,c}>
prior_arch_analysis: <path to docs/architecture/<date>/README.md, or "none">
prior_arch_analysis_date: <YYYY-MM-DD or "n/a">
prior_arch_analysis_age_days: <integer or "n/a">
eve_mcp_used: true | false | partial
detected_shapes: [<compose | kube | driver>]    # for release-analysis
exclusions: [<scope exclusions inherited from arch-analysis or named by user>]
---

# Suite Scope

<2-4 sentences: what's being analyzed, why this scope, what's deliberately excluded.>

## Inherited from prior arch-analysis

<If prior_arch_analysis is non-empty, paste the prior README's Scope section verbatim here so siblings have the full context without re-reading.>

## Release-specific extensions

<For driver-shaped or kube-shaped scopes, any release-time additions to the arch-analysis scope. E.g., "source-control-automation added; not in arch-analysis because it's not a deployed system."

Empty section is fine when scope inherits cleanly without extensions.>
```

## Why a separate file

The suite manifest (`suite.yaml`) is the *run state* — which steps ran, where their output landed. The scope file is the *shared input* — what every sibling reads to know what to analyze.

Splitting them keeps two concerns clean:

- The manifest mutates during the run; the scope is fixed at suite start.
- The scope is human-readable markdown; the manifest is structured YAML.
- Sibling skills only need scope, not run state.

## Sibling skill contract

A sibling skill that opts into the suite-scope contract reads `suite-scope.md` during its own Phase 0 / Phase 1 and treats its frontmatter as authoritative for:

- `target_repo` — what to analyze.
- `prior_arch_analysis` — which prior to ingest (if any).
- `eve_mcp_used` — whether eve-mcp tools are in scope for verification.
- `exclusions` — what to skip.

The sibling does NOT re-prompt the user for scope confirmation when `suite-scope.md` is supplied. The orchestrator already confirmed; double-confirming wastes the user's time.

### Opt-in pattern

The orchestrator passes the suite-scope path explicitly in the sibling's invocation prompt:

> Run release-analysis using the scope at `docs/2026-05-18-suite/suite-scope.md`.

A sibling that recognizes the pattern skips its own Phase 0 lookup and reads the file directly. A sibling that doesn't recognize the pattern (because it predates the convention) treats the prompt as a normal scope description and proceeds with its own Phase 0 — slower, but not broken.

In v1, only `release-analysis` actively reads `suite-scope.md`. Future sibling rewrites can opt in.

## Multi-repo scopes

When the prior arch-analysis covered a union (`~/source/{mainwebcode,cosential-proxy,dev-stack}`), the suite-scope inherits the union verbatim. Sibling skills handle the union the same way arch-analysis did — see arch-analysis's frontmatter for the canonical encoding.

When the recipe needs to *extend* the union (e.g., release-driver onboarding adds `source-control-automation` because it drives the others' release), the orchestrator writes both:

```yaml
target_repo: ~/source/{mainwebcode,cosential-proxy,dev-stack,source-control-automation}
```

with a Release-specific extensions section noting why source-control-automation was added.

## Stale priors

If the prior arch-analysis is older than 30 days, the orchestrator's Phase 0 already asked the user how to proceed (trust the older run, run a fresh focused arch-analysis, or proceed without prior context). Whatever the user chose is recorded in `prior_arch_analysis_age_days` and the body of the file. Sibling skills don't re-ask — they trust the suite's decision.

## When the user supplies an explicit override

Sometimes the user wants to run a sibling against a *different* scope than the rest of the suite. Rare, but legitimate (e.g., wiring-audit on just the frontend subtree of a multi-repo scope). The orchestrator handles this by:

1. Asking whether the override applies just to this step or to subsequent steps too.
2. If just this step, recording the override in the step's `notes` field but leaving `suite-scope.md` unchanged.
3. If applying to subsequent steps, writing a new `suite-scope.md.<step-id>` and updating the suite manifest's later steps to reference it.

This is rare enough that v1 treats it as user-coached: the orchestrator surfaces the override question and lets the user reword the invocation prompt manually rather than automating the file split.
