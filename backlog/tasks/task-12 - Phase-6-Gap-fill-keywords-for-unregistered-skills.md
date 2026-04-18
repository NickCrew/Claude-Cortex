---
id: TASK-12
title: 'Phase 6: Gap-fill keywords for unregistered skills'
status: To Do
assignee: []
created_date: '2026-04-18 17:56'
labels:
  - skill-registry
  - content
dependencies: []
documentation:
  - doc-1
priority: low
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Populate keywords for the ~70 skills that had no seed data in any legacy registry.

See plan: doc-1, section "Gap fill for 70 unregistered skills" and "Phase 6: Gap fill".

**Deliverables:**
- Updated SKILL.md front matter for every skill listed in `docs/devel/reports/skill-keywords-needing-review.md`
- Regenerated `skills/skill-index.json` after each batch
- Gap report shrinks to zero entries

**Approach:** Keywords inferred from skill description + typical use cases. Can be done in batches of ~20 skills per PR.

**Depends on:** Phase 2 (needs gap report)
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Every skill in the gap report has at least 3 keywords in its SKILL.md front matter
- [ ] #2 Gap report in docs/devel/reports/ is empty or deleted
- [ ] #3 cortex skills analyze returns sensible matches for each previously-unregistered skill
<!-- AC:END -->
