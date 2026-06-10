# Recipe: deployed-system onboarding

For systems that get deployed — single repos or multi-repo unions that ship a runtime somewhere (Kubernetes, Compose, both). The unit of analysis is the system itself. Reader: a release engineer or general engineer onboarding to a deployed system end-to-end.

## Validated against

`mainwebcode + cosential-proxy + dev-stack` (2026-05-16 arch-analysis run): a CFML monolith + Caddy reverse proxy + Docker Compose orchestrator wiring ~30 microservices. The arch-analysis pass produced 8 mode reports with 296 verified findings, 3 to 7 synthesized concepts per mode, and a cross-mode index of 25+ shared callouts. Release-analysis would naturally layer on top.

## When to choose this recipe

- The target deploys somewhere — has Dockerfile, Compose, manifests, or platform descriptors.
- The target has actual source code in addition to release config (so arch-analysis has something to analyze).
- The reader wants to understand the system end-to-end, not just its release surface.
- Appropriate for both single-repo and multi-repo (union) scopes.

If the target is release-driver-shaped instead (no deployable runtime, just tooling that drives others' releases), use the `release-driver-onboarding` recipe.

## Plan

```yaml
steps:
  - id: 1
    skill: architectural-analysis
    purpose: "Map the system end-to-end across 8 modes — IA, data flow, integrations, UI surfaces, interaction patterns, data model, control flow, failure modes"
    invocation_prompt: |
      Run architectural-analysis against <target_repo> using the suite
      scope at docs/<suite-date>-suite/suite-scope.md.
      
      Use the full mode set unless the user named a subset. Phase 2's
      doc-led workflow (the rewrite from commit 3f3376d) treats in-tree
      docs as the spine of the report; Phase 5b's gap-first synthesis
      surfaces the institutional risk register.
    expected_output: docs/architecture/<date>/
    expected_artifacts:
      - README.md
      - doc-map.md
      - docs-inventory.txt
      - information/report.md
      - data-flow/report.md
      - integrations/report.md
      - ui-surfaces/report.md
      - interaction-patterns/report.md
      - data-model/report.md
      - control-flow/report.md
      - failure-modes/report.md
      - <date>.html
    approval_gate: |
      Confirm the output landed and the synthesis README's "Undocumented
      behaviors" section has content (the gap inventory is the lead;
      empty gap inventory usually means the analysis didn't try hard
      enough).

  - id: 2
    skill: release-analysis
    purpose: "Layer release-shaped views on top of the architectural map — promotion path, environment matrix, configuration provenance, recovery procedures"
    invocation_prompt: |
      Run release-analysis against <target_repo> using the suite scope
      at docs/<suite-date>-suite/suite-scope.md.
      
      Phase 0 should detect the prior arch-analysis at
      docs/architecture/<date>/ (from step 1) and inherit its scope and
      doc-map automatically. Detect the release shape (compose-only,
      kube-only, or compose+kube) per the indicators in SKILL.md.
    expected_output: docs/release/<date>/
    expected_artifacts:
      - README.md
      - doc-map.md
      - promotion-path/report.md
      - environment-matrix/report.md
      - configuration-provenance/report.md
      - recovery-rollback/report.md
      - <date>.html
    approval_gate: |
      Confirm release-analysis ingested the arch-analysis prior (the
      Provenance section names the inherited path and date). Confirm
      cross-skill callouts ([I-N], [C-N], [F-N]) appear in at least
      one mode report.

  - id: 3
    skill: wiring-audit
    purpose: "Find UI/backend drift — orphan surfaces, unwired capabilities, contract violations. Optional; skip if the system has minimal UI."
    invocation_prompt: |
      Run wiring-audit against <target_repo> using the suite scope at
      docs/<suite-date>-suite/suite-scope.md.
      
      Pass docs/architecture/<date>/ui-surfaces/ and integrations/ as
      priors so the audit can skip rediscovery and focus on diff.
    expected_output: docs/audits/<date>/
    expected_artifacts:
      - report.md
      - registries/surfaces.yaml
      - registries/capabilities.yaml
    approval_gate: |
      Confirm the audit surfaced findings (most non-trivial systems
      have at least a few orphan surfaces or stale labels). If the
      report is empty, either the audit ran too narrowly or the system
      genuinely has clean wiring.
    optional: true
    skip_default_when: |
      - The system has no UI (pure API or batch processing).
      - The user explicitly opted out at suite start.

  - id: 4
    skill: mapping-suite (compile)
    purpose: "Build the combined navigation HTML linking all completed steps"
    invocation_prompt: |
      bash skills/mapping-suite/scripts/compile-combined.sh \
          docs/<suite-date>-suite/
    expected_output: docs/<suite-date>-suite/<suite-date>-suite.html
    approval_gate: |
      Open the combined HTML; confirm all completed siblings are linked
      in the recommended reading order.
```

## Reading order

When the suite is done, recommend the user read in this order:

1. **Combined HTML** — the navigation entry point.
2. **Architectural-analysis synthesis README** — leads with "Undocumented behaviors" (gap inventory) and "Documentation drift" sections per the doc-led workflow. Read this first to know the system's shape and where the docs lie.
3. **Release-analysis synthesis README** — the release surface, layered on top of the arch view.
4. **Architectural-analysis information-architecture report** — the module hierarchy. Reference this when you need to know "where does X live."
5. **Architectural-analysis failure-modes report** — the highest-density tribal knowledge in the suite. Where the footguns are.
6. **Release-analysis recovery-rollback report** — the recovery procedures that build on the failure modes.
7. **Architectural-analysis other modes** — read as needed by topic.
8. **Wiring-audit report** (if run) — the appendix; read when "why is this UI element broken" comes up.

## What NOT to expect from this recipe

- **Test coverage analysis** — `test-review` is a separate concern. Recommend as a follow-up if the user cares about test health.
- **Documentation completeness audit** — `doc-completeness-audit` is a separate concern. The arch-analysis Phase 5b reconciliation flags gap states; if the user wants a focused doc-coverage view, run that skill afterward.
- **Security review** — `security-auditor` is separate.
- **Performance analysis** — the performance-optimization skills are separate.

## Common variations

- **Skip wiring-audit when there's no UI.** Step 3 is marked optional; the orchestrator skips it automatically when the user confirms "no UI" at suite start.
- **Run only arch-analysis.** If the user is doing knowledge-transfer for someone who won't be operating the system (just understanding it), step 2 (release-analysis) is unnecessary. Drop it and go straight to combined HTML.
- **Multi-repo union.** This recipe handles multi-repo cleanly; arch-analysis and release-analysis both inherit the union scope from `suite-scope.md`. The combined HTML links to the union artifacts.
- **Existing recent arch-analysis.** If the user has an arch-analysis from <30 days ago, the orchestrator's Phase 0 picks it up and step 1 is replaced with "use existing" — the suite skips the cost of re-running 8 sub-agents. The combined HTML links to the existing arch-analysis dir.
