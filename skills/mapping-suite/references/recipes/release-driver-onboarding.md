# Recipe: release-driver onboarding

For tooling that *drives* releases for other systems — PowerShell fleet orchestrators, deploy-bot scripts, release-cutting CLIs. The unit of analysis is the operations the tool performs, not the tool itself. Reader: a release engineer onboarding to a tool they'll be running.

## Validated against

`source-control-automation` (2026-05-17 run): a PowerShell tool that orchestrates the release of ~26 CRM platform repos. The tool itself doesn't ship a deployable service. Recipe produced a 109-finding release-analysis report with three live drift findings and three concrete recovery gaps; runbook reconciliation flagged 8 docs as authoritative on procedure with a handful of finding-level drifts inside them.

## When to choose this recipe

- The target has no Dockerfile, no Compose, no Kubernetes manifests for itself.
- The target has a `data/` or `config/` directory describing *other* systems (namespaces, manifests, channels).
- The target has a `docs/runbooks/` directory naming fleet operations (cut-release, forward-merge, close-release, environment-roll, etc.).
- The target has CLI entrypoints (`.ps1`, `scripts/`, `bin/`) that take channel/namespace/manifest names as arguments.

If the target hits these signals, release-analysis's driver-shaped detection will activate and this recipe gets you to the most useful artifact fastest.

## Plan

```yaml
steps:
  - id: 1
    skill: release-analysis
    purpose: "Map the fleet pipeline this tool drives — promotion path, environment matrix, configuration provenance, recovery procedures"
    invocation_prompt: |
      Run release-analysis against <target_repo> using the suite scope at
      docs/<suite-date>-suite/suite-scope.md.
      
      The target is a release-driver tool — scope_shape: driver-only (or
      driver+kube if the tool also ships itself via Eve). No prior
      architectural-analysis to ingest unless the user supplied one;
      proceed without prior context if not.
    expected_output: docs/release/<date>/
    expected_artifacts:
      - README.md
      - promotion-path/report.md
      - environment-matrix/report.md
      - configuration-provenance/report.md
      - recovery-rollback/report.md
      - <date>.html
    approval_gate: |
      Confirm the output landed and the driver-shape framing was used
      (the synthesis README's Scope section should explicitly call out
      that the tool drives releases rather than ships itself).

  - id: 2
    skill: doc-claim-validator
    purpose: "Verify runbook claims against current code and live eve state — catch drifted procedures release-analysis Phase 5b flagged"
    invocation_prompt: |
      Run doc-claim-validator against <target_repo>/docs/runbooks/.
      Use docs/release/<date>/ from step 1 as priors so the validator
      can compare runbook claims against the verified findings catalog.
      Pay special attention to procedural ordering — runbooks that name
      the right steps in the wrong order are a common drift pattern in
      release-driver tools.
    expected_output: docs/audits/<date>/
    expected_artifacts:
      - report.md
    approval_gate: |
      Confirm the validator surfaced specific drift findings, not just
      "no claims found." Runbooks for release-driver tools should
      always have verifiable claims (file paths, command names, env
      vars, expected outputs).

  - id: 3
    skill: mapping-suite (compile)
    purpose: "Build the combined navigation HTML linking step 1 + step 2"
    invocation_prompt: |
      bash skills/mapping-suite/scripts/compile-combined.sh \
          docs/<suite-date>-suite/
    expected_output: docs/<suite-date>-suite/<suite-date>-suite.html
    approval_gate: |
      Open the combined HTML in a browser; confirm both sibling reports
      are linked and the navigation reads cleanly.
```

## Reading order

When the suite is done, recommend the user read in this order:

1. **Combined HTML** (`<suite-date>-suite.html`) — the navigation entry point. One-page index of what got produced.
2. **Release-analysis synthesis README** — the scope, headline findings, and reading-path recommendation for the four release-analysis modes.
3. **Release-analysis recovery-rollback report** — for a release engineer onboarding, this is the highest-value mode. Names the recovery procedures, the gap states with no documented recovery, and which runbooks are authoritative.
4. **Release-analysis promotion-path report** — the canonical map of the fleet pipeline.
5. **Release-analysis configuration-provenance report** — when "where does this config come from" comes up (it will).
6. **Release-analysis environment-matrix report** — for fleet topology questions.
7. **Doc-claim-validator report** — the appendix; consult when a specific runbook's accuracy is in question.

## What NOT to expect from this recipe

- **A general system snapshot** — release-driver tools don't have a "system" the way deployed services do. The output is operations-shaped, not architecture-shaped.
- **The tool's internal architecture** — release-analysis treats the tool as a black box that performs operations. If you need to understand the tool's *implementation* (PowerShell module structure, error handling patterns, etc.), run `architectural-analysis` separately afterward.
- **A wiring audit** — release-driver tools usually don't have a UI, so wiring-audit findings would be sparse. Skip it for this recipe.
- **Test coverage analysis** — `test-review` is a separate concern; recommend it as a follow-up if the user cares about the tool's test health.

## Common variations

- **Tool also ships itself** (e.g., a release-bot deployed to Kube). Add `architectural-analysis` as step 0 with `--scope <target>` to map the tool's own architecture; re-scope step 1 to `driver+kube`.
- **Multi-tool suite** (the team has 3 release-driver tools). Run this recipe per tool, with separate suite directories. Combining their outputs into one super-suite is out of scope for v1.
- **Existing arch-analysis on this tool**. Pass `--prior <path>` to the orchestrator's Phase 0; release-analysis will inherit. Useful when the tool's own implementation has been mapped and you want release-analysis to *extend* that view rather than ignore it.
