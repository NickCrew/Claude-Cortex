---
id: TASK-8
title: 'Phase 2: Migrate keywords into SKILL.md front matter'
status: To Do
assignee: []
created_date: '2026-04-18 17:56'
labels:
  - skill-registry
  - migration
dependencies: []
documentation:
  - doc-1
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Run the one-shot migration and commit the results. After this task, every skill that existed in any legacy registry has its keywords in its own SKILL.md.

See plan: doc-1, section "Migration" and "Phase 2: Migrate SKILL.md files".

**Deliverables:**
- `scripts/migrate-skill-keywords.py` — idempotent one-shot script (left in repo for auditability)
- Updated SKILL.md files across `skills/**` (expected ~90 edits based on registry overlap)
- `skills/skill-index.json` — committed, generated via `cortex skills rebuild-index`
- `docs/devel/reports/skill-keywords-needing-review.md` — gap report for the ~40-50 skills with no seed data
- `docs/devel/reports/skill-migration-orphans.md` — registry refs with no matching directory (ctx-* entries, etc.)

**Reconciliation rules** (from plan):
- Union keywords across all three registries, dedupe case-insensitive
- Apply rename map for ctx-* stale refs
- Take max confidence when registries disagree
- file_patterns from recommendation-rules.json carry forward per-skill
- triggers: field accepted as keywords: alias during migration

**Depends on:** Phase 1 (needs `cortex skills rebuild-index`)
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 scripts/migrate-skill-keywords.py is idempotent (running twice yields same output)
- [ ] #2 All 132 skill directories have an entry in the generated skill-index.json
- [ ] #3 Every skill previously listed in skill-rules.json has keywords in its SKILL.md front matter
- [ ] #4 Gap report lists every skill with empty keywords for later manual fill
- [ ] #5 Orphan report lists every legacy-registry entry with no matching directory
- [ ] #6 No legacy file deletions yet (that is Phase 5)
<!-- AC:END -->
