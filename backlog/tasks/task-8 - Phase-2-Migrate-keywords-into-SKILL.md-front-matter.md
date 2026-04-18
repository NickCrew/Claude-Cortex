---
id: TASK-8
title: 'Phase 2: Migrate keywords into SKILL.md front matter'
status: Done
assignee: []
created_date: '2026-04-18 17:56'
updated_date: '2026-04-18 20:06'
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
- [x] #1 scripts/migrate-skill-keywords.py is idempotent (running twice yields same output)
- [x] #2 All 132 skill directories have an entry in the generated skill-index.json
- [x] #3 Every skill previously listed in skill-rules.json has keywords in its SKILL.md front matter
- [x] #4 Gap report lists every skill with empty keywords for later manual fill
- [x] #5 Orphan report lists every legacy-registry entry with no matching directory
- [x] #6 No legacy file deletions yet (that is Phase 5)
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Phase 2 landed. All three legacy registries have been migrated into per-skill front matter.

**Added:**
- `scripts/migrate-skill-keywords.py` — idempotent one-shot script with RENAMES map for stale `ctx-*` refs, PyYAML-based merge, canonical key ordering, 2-space indented block-style lists via custom `_IndentedDumper`
- `skills/skill-index.json` (committed, 143 skills) — `skill-index.json` added to .gitignore as a tracked exception
- `docs/devel/reports/skill-keywords-needing-review.md` — 64 skills with empty keywords awaiting Phase 6 gap-fill
- `docs/devel/reports/skill-migration-orphans.md` — 0 orphans (RENAMES resolved all legacy refs cleanly)

**Modified:**
- 71 SKILL.md files across `skills/` and `skills/collaboration/` — keywords unioned from all three registries (case-insensitive dedupe), file_patterns carried forward from `recommendation-rules.json`, confidence set to max when registries disagreed, `triggers:` absorbed into `keywords:` where present
- `.gitignore` — added `!skills/skill-index.json` negation

**Validated:**
- Second run reports "migrated 0 SKILL.md files" — idempotent
- `cortex skills rebuild-index` emits 143-skill index with 2 warnings (empty keyword arrays for `workflow-performance`, `workflow-security-audit` — also flagged in gap report)
- pytest tests/unit/test_skill_index.py: 22/22 passing
- Spot-checked `canvas-design`, `agent-loops`, `api-design-patterns`: keywords merged correctly, `license` field preserved, body content untouched

**Not changed:**
- Legacy files (`skill-rules.json`, `activation.yaml`, `recommendation-rules.json`) remain on disk — Phase 5 deletes them
- Consumers (`hooks/skill_auto_suggester.py`, `skill_recommender.py`, `activator.py`) untouched — Phase 3 flips them
<!-- SECTION:FINAL_SUMMARY:END -->
