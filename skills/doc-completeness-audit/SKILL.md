---
name: doc-completeness-audit
description: Audit documentation completeness by mapping what a doc set should cover against what it actually covers. Produces a prioritized gap report by topic, not just by file. This skill should be used after shipping features, before releases, or when users report missing documentation.
version: 1.0.0
tags:
  - documentation
  - audit
  - completeness
  - review
triggers:
  - audit doc completeness
  - what docs are missing
  - doc coverage gaps
  - documentation gaps
  - are docs complete
dependencies:
  skills:
    - doc-maintenance
    - doc-claim-validator
  tools:
    - Grep
    - Glob
    - Read
    - Bash
    - Agent
token_estimate: ~3500
keywords:
  - doc gaps
  - audit coverage
  - completeness
  - doc
  - audit
  - doc completeness audit
---

# Documentation Completeness Audit

Determine whether a documentation set covers everything it should by building an
inventory of what *needs* documenting and comparing it to what *exists*. The output
is a prioritized gap report — not new documentation.

## When to Use

- After shipping a feature — verify docs cover the new surface area
- Before a release — ensure no undocumented public APIs, CLI flags, or config options
- When users or new hires report "I couldn't find docs for X"
- Periodic health check on doc coverage
- After running `doc-maintenance` (structural) and `doc-claim-validator` (accuracy) to go wider

## Quick Reference

| Resource | Purpose | Load when |
|----------|---------|-----------|
| `references/coverage-model.md` | Defines what "complete" means per doc type | Always (Phase 1) |

---

## Workflow Overview

```
Phase 1: Inventory   → Build the "should exist" list from code and config
Phase 2: Map         → Match inventory items to existing documentation
Phase 3: Classify    → Score each gap by audience impact
Phase 4: Report      → Produce the prioritized gap report
```

---

## Phase 1: Build the Inventory

Construct a list of everything that should be documented. Use four sources, checking
all of them:

### Source 1: Public Code Surface

Run the bundled inventory script to extract documentable surface area deterministically:

```bash
python3 skills/doc-completeness-audit/scripts/inventory.py --root . --json > inventory.json

# Or human-readable:
python3 skills/doc-completeness-audit/scripts/inventory.py --root .

# Run specific detectors only:
python3 skills/doc-completeness-audit/scripts/inventory.py --root . --detectors env_vars,cli_commands
```

The script scans source files across Python, JavaScript/TypeScript, Rust, Go, Ruby, Java,
and shell, extracting six categories:

| Detector | What it extracts |
|----------|-----------------|
| `env_vars` | Environment variable references (`os.environ`, `process.env`, `env::var`, etc.) |
| `cli_commands` | CLI commands and flags (argparse, click, clap, cobra, commander) |
| `config_keys` | Configuration key access in config-related files |
| `http_endpoints` | HTTP route definitions (Flask, FastAPI, Express, Actix, Axum, net/http) |
| `public_exports` | Public module exports (`__init__.py`, `export`, `pub fn`, Go capitalized funcs) |
| `error_types` | Custom error/exception class definitions |
| Event types, webhooks, callbacks | Every event name and payload shape |

Dispatch an Explore agent to scan for these signals. Provide it with the project's
primary language and entry points.

### Source 2: User-Facing Features

Identify features a user interacts with:

- TUI screens, views, keybindings
- CLI workflows (multi-step operations)
- Integration points (hooks, plugins, extensions)
- Authentication/authorization flows
- Error messages that imply user action

### Source 3: Operational Surface

Identify what operators and maintainers need:

- Installation and setup procedures
- Upgrade and migration paths
- Backup and restore procedures
- Troubleshooting common errors
- Environment requirements and dependencies
- CI/CD integration points

### Source 4: Existing Docs Cross-References

Check existing docs for promises of documentation that doesn't exist:

- "See [link]" references to pages that don't exist
- "Coming soon" or "TODO" markers
- Table of contents entries without corresponding pages
- Navigation entries without targets

### Source 5: Architectural / Operational / Migration Topic Discovery (sonnet)

The first four sources catch *code-detectable* surface (env vars, CLI flags,
endpoints, exported APIs, broken cross-references). They miss topics that
exist as architectural patterns, user flows, ops procedures, or migration
paths but don't surface as a single greppable symbol. Examples:

- Architectural patterns the system implements (CQRS, event sourcing,
  saga) — should be documented but won't show up in inventory.py
- User flows implicit across UI surfaces — "how to share a project" may
  span multiple components and isn't a single CLI command
- Migration paths between versions — typically tribal knowledge until
  someone needs them
- Operational runbooks (incidents, rollbacks, capacity events)
- Recovery procedures and disaster scenarios

Dispatch one `general-purpose` + `sonnet` agent for topic discovery:

```
subagent_type: "general-purpose"
model: "sonnet"
description: "Architectural/operational topic discovery"
```

Prompt: read README, top-level docs, and a sample of code (architecture
files, integration boundaries, deployment configs, major feature
directories). Identify topics that *should* be documented but aren't
captured by the code-surface inventory. For each topic, name:

- `topic` — what needs documenting (one phrase)
- `evidence` — what in the codebase implies this topic exists (path:line citations)
- `audience` — who would read this (operators, contributors, advanced users)
- `type` — reference, tutorial, guide, explanation, runbook
- `confidence` — high (clear evidence), medium (inferred), low (speculative)

Append the agent's output to the inventory list before Phase 2.

**Output:** A structured inventory list. Each item has:
- `topic` — what needs documenting
- `source` — where the requirement was discovered (code path, config key, user flow, sonnet inference)
- `audience` — who needs this (end user, developer, operator)
- `type` — what kind of doc it needs (reference, tutorial, guide, explanation, runbook)
- `confidence` — high (deterministic) | medium | low (sonnet-inferred speculative)

---

## Phase 2: Map to Existing Documentation (per-docfile sonnet dispatch)

For each inventory item, determine whether it's documented and how well.
"Adequate coverage" requires reading surrounding context — a grep hit
doesn't tell you whether the topic is truly explained vs. just mentioned in
passing. Orchestrator-side execution would require reading every doc *N*
times (once per inventory item), which strains the context window.

### Dispatch strategy

Two-phase mapping:

1. **Bulk grep pass (orchestrator)** — for each inventory item, grep docs
   for the topic name. Build a candidate match map: which docs mention
   each topic.
2. **Per-docfile sonnet pass** — for each docfile that surfaced as a
   candidate match for any inventory item, dispatch one `general-purpose` +
   `sonnet` agent. The agent receives the doc + the list of inventory
   items that grep'd to this doc, and judges each as Documented / Shallow /
   Misplaced.

This keeps total agent calls ≈ N candidate docfiles (not N inventory items
× M docs). For a typical project with 100 inventory items and 50 docs, the
candidate map usually has 30–50 docs needing review.

### Per-docfile prompt template

```
subagent_type: "general-purpose"
model: "sonnet"
description: "Coverage mapping for <docfile>"
```

Prompt:
```
Read the doc at <DOCFILE_PATH>. The following inventory items grep-matched
this doc — judge each:

<INVENTORY_ITEMS_FOR_THIS_DOC>

For each item, classify as one of:
- Documented: dedicated section or page provides adequate coverage
- Shallow: mentioned but insufficient (missing examples, edge cases,
  parameter listings; flag-in-table without explanation)
- Misplaced: covered, but in the wrong doc type for the audience (API
  reference embedded in a tutorial; user-facing topic in dev-only docs)
- No real match: grep matched but the doc doesn't actually cover the topic
  (incidental mention, different concept with the same word)

Output as YAML:

doc_path: <path>
items_reviewed: N
classifications:
  - item: <topic>
    classification: Documented | Shallow | Misplaced | No real match
    section: <heading or line range where the topic is covered>
    evidence: <quote or paraphrase of the relevant content>
    gap: <if Shallow, what's missing; if Misplaced, where it should live>
```

### Items with no candidate match

Inventory items that grep'd 0 docs go directly to the "Missing" bucket
without a sonnet review. The orchestrator handles these in Phase 3.

### Why per-docfile rather than per-item

Per-item dispatch (one sonnet call per inventory item, reading every
candidate doc fresh) blows up at any meaningful scale (100 items × 5
candidates = 500 calls). Per-docfile lets the agent see all related items
in one pass and cross-reference within the doc — also higher precision
than fragmented per-item judgments.

---

## Phase 3: Classify Gaps by Impact

Not all gaps are equal. Score each gap using audience impact:

### Priority Framework

| Priority | Criteria | Example |
|----------|----------|---------|
| **P0** | User cannot accomplish a core task without this | No installation guide, undocumented required config |
| **P1** | User can work around it but wastes significant time | CLI flag exists but undocumented, error message without troubleshooting |
| **P2** | Missing docs for secondary features or advanced use cases | Plugin API undocumented, advanced config options missing |
| **P3** | Missing docs for edge cases or rarely used features | Obscure env var, deprecated feature migration path |
| **P4** | Nice to have — explanatory content, design rationale | Architecture decision records, "why" behind defaults |

### Audience Weighting

Apply a multiplier based on audience:

| Audience | Weight | Rationale |
|----------|--------|-----------|
| New users / onboarding | 1.5x | First impressions; high abandonment risk |
| Daily users | 1.0x | Core audience |
| Advanced users / contributors | 0.8x | Can read source when docs fail |
| Internal operators | 0.7x | Can ask the team |

A P2 gap for new users (P2 × 1.5 = 3.0) outranks a P1 gap for internal operators (P1 × 0.7 = 2.1).

---

## Phase 4: Produce the Gap Report

### Report Format

```markdown
# Documentation Completeness Audit

**Audit date:** YYYY-MM-DD
**Scope:** [directories or doc sets audited]
**Inventory items:** N total
**Coverage:** N documented / N shallow / N missing / N misplaced

---

## Summary

[2-3 sentences: overall completeness assessment]

Coverage by audience:
| Audience | Documented | Shallow | Missing | Coverage % |
|----------|-----------|---------|---------|------------|
| New users | N | N | N | N% |
| Daily users | N | N | N | N% |
| Contributors | N | N | N | N% |
| Operators | N | N | N | N% |

---

## P0 Gaps — Blocking

| # | Topic | Audience | Source | Current State | What's Needed |
|---|-------|----------|--------|---------------|---------------|
| 1 | [topic] | [who] | [code path] | Missing | [what to write] |

## P1 Gaps — High Impact

| # | Topic | Audience | Source | Current State | What's Needed |
|---|-------|----------|--------|---------------|---------------|

## P2 Gaps — Moderate Impact

| # | Topic | Audience | Source | Current State | What's Needed |
|---|-------|----------|--------|---------------|---------------|

## P3-P4 Gaps — Low Priority

| # | Topic | Audience | Priority | Current State |
|---|-------|----------|----------|---------------|

---

## Shallow Coverage Details

For each Shallow item, explain what's insufficient:

### [Topic]
**Current doc:** [path and section]
**Problem:** [what's missing — examples, edge cases, complete reference, etc.]
**Recommended action:** [specific improvement]

---

## Misplaced Documentation

| Topic | Current Location | Recommended Location | Why |
|-------|-----------------|---------------------|-----|

---

## Well-Documented (No Action Needed)

[List topics with adequate coverage, grouped by audience, so the report
shows the full picture and not just the gaps]
```

---

## Integration with Other Doc Skills

This skill fits into the documentation health pipeline:

```
doc-maintenance         →  Structural health (links, orphans, folders)
doc-claim-validator     →  Semantic accuracy (do claims match code?)
doc-completeness-audit  →  Topic coverage (is everything documented?)
doc-quality-review      →  Prose quality (is it well-written?)
doc-architecture-review →  Information architecture (is it findable?)
```

Route gap remediation to the appropriate producer:
- Reference gaps → `reference-documentation`
- Tutorial gaps → `tutorial-design`
- Explanation gaps → `documentation-production`

---

## Anti-Patterns

- Do not count files as coverage — a file can exist and say nothing useful
- Do not manufacture gaps to look thorough — if coverage is good, say so
- Do not audit archived docs (`docs/archive/`) — they are historical
- Do not require documentation for internal implementation details — only public surface
- Do not treat every function as needing its own doc page — aggregate by topic
- Do not conflate "not documented" with "needs documenting" — some things are correctly undocumented (internal helpers, deprecated code scheduled for removal)

---

## Bundled Resources

### Scripts
- `scripts/inventory.py` — Extract documentable surface area from any codebase (env vars, CLI commands, config keys, HTTP endpoints, public exports, error types)

### References
- `references/coverage-model.md` — Defines coverage expectations per doc type and audience
