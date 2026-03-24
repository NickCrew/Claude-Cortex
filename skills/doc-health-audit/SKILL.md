---
name: doc-health-audit
description: >-
  Orchestrate a full documentation health audit across five dimensions: structural
  health, semantic accuracy, topic completeness, prose quality, and information
  architecture. Runs each phase in dependency order with phase gating. This skill
  should be used for pre-release audits, periodic health checks, or comprehensive
  documentation assessments.
version: 1.0.0
tags: [documentation, audit, orchestration, review]
triggers:
  - full doc audit
  - doc health check
  - documentation health
  - audit all docs
  - pre-release doc check
dependencies:
  skills:
    - doc-maintenance
    - doc-claim-validator
    - doc-completeness-audit
    - doc-quality-review
    - doc-architecture-review
  tools: [Read, Grep, Glob, Bash, Agent]
token_estimate: ~2000
---

# Documentation Health Audit

Orchestrate a comprehensive documentation assessment across five dimensions.
Each phase builds on the previous — structural issues are found before accuracy
is checked, accuracy before completeness, and so on.

This skill does not duplicate any phase logic. It defines the run order, phase
gating, and combined summary. Each phase delegates to its dedicated skill.

## When to Use

- Pre-release audit — full pass before shipping
- Periodic health check — monthly or quarterly
- After a major refactor that touched many docs
- When documentation quality is unknown or untrusted
- First-time assessment of a doc set

For single-dimension checks, use the individual skills directly.

## Pipeline

```
Phase 1: Structure     →  doc-maintenance
Phase 2: Accuracy      →  doc-claim-validator
Phase 3: Completeness  →  doc-completeness-audit
Phase 4: Quality       →  doc-quality-review
Phase 5: Architecture  →  doc-architecture-review
```

### Why This Order

Each phase depends on the prior phase being reasonably healthy:

| Phase | Depends on | Reason |
|-------|-----------|--------|
| Structure | — | Foundation. Broken links and orphans must be visible before anything else |
| Accuracy | Structure | Can't verify claims in docs you can't find or that have broken references |
| Completeness | Accuracy | No point inventorying gaps if existing docs contain false claims |
| Quality | Completeness | Review prose quality only on docs you intend to keep |
| Architecture | Completeness | Need to know what's missing before evaluating whether the structure can hold it |

---

## Execution

### Step 1: Determine Scope

Before running phases, establish what to audit:

- **Full audit** — all documentation (`docs/`, `site/`, `README.md`)
- **Scoped audit** — specific directory or doc set (e.g., "just the reference section")
- **Changed-only audit** — docs modified since a git ref (`git diff --name-only main...HEAD -- '*.md'`)

Pass the scope to each phase so they operate on the same set.

### Step 2: Run Phases with Gating

Run each phase sequentially. After each phase, evaluate the gate condition.

#### Phase 1: Structure (`doc-maintenance`)

**Run:** Invoke `doc-maintenance` on the scoped doc set.

**Gate condition:** Check the findings.
- If >10 broken internal links → **WARN** the user: "Structural issues found. Fix these
  first for accurate results in later phases, or continue anyway?"
- If critical structural issues (missing index pages, completely broken navigation) →
  **RECOMMEND STOP**. Later phases will produce unreliable results.
- Otherwise → **CONTINUE**

#### Phase 2: Accuracy (`doc-claim-validator`)

**Run:** Invoke `doc-claim-validator` on the scoped doc set.

**Gate condition:** Check the findings.
- If P0 findings (user-facing docs that would break if followed) → **WARN** the user.
  These should be fixed before assessing completeness, but the audit can continue.
- Otherwise → **CONTINUE**

#### Phase 3: Completeness (`doc-completeness-audit`)

**Run:** Invoke `doc-completeness-audit` on the scoped doc set.

**Gate condition:** No gate — always continue to quality. Completeness gaps don't
affect quality assessment of existing docs.

#### Phase 4: Quality (`doc-quality-review`)

**Run:** Invoke `doc-quality-review` on the scoped doc set (excluding any docs
flagged for removal in earlier phases).

**Gate condition:** No gate — always continue to architecture.

#### Phase 5: Architecture (`doc-architecture-review`)

**Run:** Invoke `doc-architecture-review` on the scoped doc set. Pass the
completeness gap list from Phase 3 so the architecture review can assess whether
the current structure can accommodate the missing docs.

**Gate condition:** Final phase — no gate.

### Step 3: Produce Combined Summary

After all phases complete (or after an early stop), merge results into a single
dashboard.

---

## Combined Summary Format

```markdown
# Documentation Health Audit

**Audit date:** YYYY-MM-DD
**Scope:** [what was audited]
**Phases completed:** N / 5
**Early stop:** [yes/no — if yes, which phase and why]

---

## Dashboard

| Phase | Skill | Status | Key Metric | Top Finding |
|-------|-------|--------|------------|-------------|
| 1. Structure | doc-maintenance | PASS/WARN/FAIL | N broken links, N orphans | [one line] |
| 2. Accuracy | doc-claim-validator | PASS/WARN/FAIL | N P0, N P1 claims failed | [one line] |
| 3. Completeness | doc-completeness-audit | PASS/WARN/FAIL | N% coverage, N P0 gaps | [one line] |
| 4. Quality | doc-quality-review | PASS/WARN/FAIL | Grade: [A-F], avg score N/25 | [one line] |
| 5. Architecture | doc-architecture-review | PASS/WARN/FAIL | Grade: [A-F], N/35 score | [one line] |

**Overall health:** [Healthy / Needs Attention / Critical]

---

## Priority Actions

Top 5 actions across all phases, ordered by impact:

1. [Phase N] [specific action] — [why it matters]
2. [Phase N] [specific action] — [why it matters]
3. [Phase N] [specific action] — [why it matters]
4. [Phase N] [specific action] — [why it matters]
5. [Phase N] [specific action] — [why it matters]

---

## Phase Reports

[Include or link to each phase's full report below]

### Phase 1: Structure
[doc-maintenance report]

### Phase 2: Accuracy
[doc-claim-validator report]

### Phase 3: Completeness
[doc-completeness-audit report]

### Phase 4: Quality
[doc-quality-review report]

### Phase 5: Architecture
[doc-architecture-review report]
```

---

## Partial Runs

Not every audit needs all five phases. Common partial runs:

| Scenario | Phases to run |
|----------|--------------|
| "Are the docs accurate?" | 1 + 2 only |
| "What's missing?" | 1 + 3 only |
| "Is the writing good?" | 4 only |
| "Can users find things?" | 1 + 5 only |
| "Quick pre-release check" | 1 + 2 + 3 (skip quality and architecture) |
| "Full audit" | All 5 |

When running a subset, skip gates for omitted phases.

---

## Anti-Patterns

- Do not run all five phases if you only need one — use the individual skill directly
- Do not skip Phase 1 (structure) — it's the foundation for everything else
- Do not ignore gate warnings — they exist because later phases produce unreliable results on broken foundations
- Do not combine this with doc remediation in the same session — audit first, fix separately
- Do not run this on archived docs (`docs/archive/`) — they are historical
