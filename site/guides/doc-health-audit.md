---
layout: default
title: Documentation Health Audit
parent: Guides
nav_order: 11
---

# Documentation Health Audit

Cortex includes a five-phase documentation audit pipeline that assesses docs across structure, accuracy, completeness, quality, and information architecture. Run the full pipeline before releases, or use individual phases for targeted checks.
{: .fs-6 .fw-300 }

---

## The Pipeline

Each phase builds on the previous. Structural issues are found before accuracy is checked, accuracy before completeness, and so on.

```
Phase 1: Structure     →  doc-maintenance
Phase 2: Accuracy      →  doc-claim-validator
Phase 3: Completeness  →  doc-completeness-audit
Phase 4: Quality       →  doc-quality-review
Phase 5: Architecture  →  doc-architecture-review
```

### What Each Phase Checks

| Phase | Skill | Question it answers | Output |
|:------|:------|:-------------------|:-------|
| 1. Structure | `doc-maintenance` | Are links working? Are there orphaned files? Is the folder structure clean? | Broken link list, orphan report, staleness scores |
| 2. Accuracy | `doc-claim-validator` | Do the docs match the code? Are file paths, commands, and behavioral claims true? | Failed claims by severity (P0--P4) |
| 3. Completeness | `doc-completeness-audit` | Is everything documented? What topics are missing for each audience? | Gap report with audience-weighted priorities |
| 4. Quality | `doc-quality-review` | Is the writing clear, consistent, and appropriate for its audience? | Scored review (readability, consistency, audience fit, structure, actionability) |
| 5. Architecture | `doc-architecture-review` | Can users find what they need? Is the hierarchy logical? | IA assessment with 7 heuristic scores |

---

## Running the Full Pipeline

Invoke the orchestrator skill to run all five phases in sequence:

```
/ctx:doc-health-audit
```

The orchestrator handles phase ordering and gating --- if Phase 1 finds critical structural issues, it warns you before proceeding to later phases that depend on a healthy foundation.

### Output

The orchestrator produces a combined dashboard:

| Phase | Status | Key Metric | Top Finding |
|:------|:-------|:-----------|:------------|
| 1. Structure | PASS/WARN/FAIL | N broken links, N orphans | ... |
| 2. Accuracy | PASS/WARN/FAIL | N P0 claims failed | ... |
| 3. Completeness | PASS/WARN/FAIL | N% coverage, N P0 gaps | ... |
| 4. Quality | PASS/WARN/FAIL | Grade A--F | ... |
| 5. Architecture | PASS/WARN/FAIL | Grade A--F | ... |

Plus a prioritized list of the top 5 actions across all phases.

---

## Running Individual Phases

Each phase is a standalone skill you can invoke directly:

```
/ctx:doc-maintenance
/ctx:doc-claim-validator
/ctx:doc-completeness-audit
/ctx:doc-quality-review
/ctx:doc-architecture-review
```

### Common Partial Runs

| Scenario | Phases |
|:---------|:-------|
| "Are the docs accurate after this refactor?" | 1 + 2 |
| "What docs are missing?" | 1 + 3 |
| "Is the writing good enough to publish?" | 4 only |
| "Can users find things after the reorg?" | 1 + 5 |
| "Quick pre-release check" | 1 + 2 + 3 |

---

## Phase Details

### Phase 1: Structure (`doc-maintenance`)

Scans for broken links, orphaned pages, empty files, stale timestamps, and folder structure compliance. This is the foundation --- broken structure makes later phases unreliable.

**Phase gate:** If >10 broken internal links or critical structural issues are found, the orchestrator warns before continuing.

### Phase 2: Accuracy (`doc-claim-validator`)

Extracts testable claims from markdown --- file paths, commands, function references, config keys, behavioral assertions --- and verifies them against the actual codebase.

Uses a two-phase approach:
1. **Deterministic verification** for structural claims (file exists? command exists? symbol found?)
2. **AI-assisted verification** for semantic claims (behavioral assertions, dependency claims, code examples)

Includes git staleness scoring: counts commits to referenced files *after* the doc was last edited to surface likely-stale content.

**Phase gate:** P0 findings (user-facing docs that would break if followed) trigger a warning.

### Phase 3: Completeness (`doc-completeness-audit`)

Builds an inventory of what *should* be documented from four sources:

1. **Public code surface** --- CLI flags, API endpoints, config keys, exported functions
2. **User-facing features** --- TUI screens, workflows, integrations
3. **Operational surface** --- installation, upgrade paths, troubleshooting
4. **Cross-reference promises** --- "see also" links to pages that don't exist

Maps each inventory item to existing docs and classifies as Documented, Shallow, Missing, or Misplaced. Gaps are prioritized by audience impact --- a missing install guide (P0 for new users) outranks a missing advanced config reference (P2 for contributors).

### Phase 4: Quality (`doc-quality-review`)

Scores each document across five dimensions:

| Dimension | What it measures |
|:----------|:----------------|
| **Readability** | Sentence length, passive voice, jargon, paragraph density |
| **Consistency** | Terminology, formatting, heading style, tone |
| **Audience Fit** | Prerequisites, explanation depth, context gaps |
| **Structure** | Heading hierarchy, scannability, front-loading, section length |
| **Actionability** | Copy-pasteable examples, complete steps, expected output |

Dimensions are weighted by doc type --- actionability matters more for tutorials than explanations, consistency matters more for reference pages.

Produces a letter grade (A--F) and identifies systemic issues that affect multiple docs.

### Phase 5: Architecture (`doc-architecture-review`)

Evaluates information architecture against seven heuristics:

| Heuristic | What it assesses |
|:----------|:----------------|
| **Findability** | Can readers locate content without knowing where it lives? |
| **Hierarchy Coherence** | Does the nesting make sense? Is it predictable? |
| **Progressive Disclosure** | Is content layered from simple to complex? |
| **Cross-Linking** | Do links create useful connections between pages? |
| **Pattern Consistency** | Do similar pages follow similar structures? |
| **Separation of Concerns** | Are reference, tutorial, guide, and explanation content distinct? |
| **Maintenance Burden** | Can the structure accommodate growth without reorganization? |

Includes navigation path analysis (tracing user journeys through the docs) and mental model comparison (does the structure match how users think about the product?).

---

## When to Run

| Trigger | Recommended scope |
|:--------|:-----------------|
| Before a release | Full pipeline on all docs |
| After a major refactor | Phase 2 (accuracy) on affected docs |
| After restructuring docs | Phase 1 (structure) + Phase 5 (architecture) |
| New docs added | Phase 3 (completeness) + Phase 4 (quality) |
| Users report confusion | Phase 4 (quality) + Phase 5 (architecture) |
| Monthly health check | Full pipeline |

---

## All Documentation Skills

### Production

| Skill | Command | Purpose |
|:------|:--------|:--------|
| `documentation-production` | `/ctx:documentation-production` | Generate or organize project documentation |
| `reference-documentation` | `/ctx:reference-documentation` | Produce reference-oriented documentation |
| `tutorial-design` | `/ctx:tutorial-design` | Design hands-on tutorials with exercises |
| `mermaid-diagramming` | `/ctx:mermaid-diagramming` | Create Mermaid diagrams for docs |

### Review & Audit

| Skill | Command | Purpose |
|:------|:--------|:--------|
| `doc-health-audit` | `/ctx:doc-health-audit` | Full pipeline: runs all five audit phases in order |
| `doc-maintenance` | `/ctx:doc-maintenance` | Structural health (broken links, orphans, staleness) |
| `doc-claim-validator` | `/ctx:doc-claim-validator` | Semantic accuracy (verify claims match code) |
| `doc-completeness-audit` | `/ctx:doc-completeness-audit` | Topic coverage (inventory gaps by audience) |
| `doc-quality-review` | `/ctx:doc-quality-review` | Prose quality (readability, consistency, audience fit) |
| `doc-architecture-review` | `/ctx:doc-architecture-review` | Information architecture (findability, navigation, hierarchy) |

---

## Related

- [Documentation Commands]({% link guides/docs-commands.md %}) --- `cortex docs` CLI for browsing bundled docs
- [Skills Guide]({% link guides/skills.md %}) --- how skills work and how to discover them
- [Skill Showcase]({% link reference/skills.md %}) --- deep dives into the most sophisticated skills
