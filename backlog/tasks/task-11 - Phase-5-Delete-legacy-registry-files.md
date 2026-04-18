---
id: TASK-11
title: 'Phase 5: Delete legacy registry files'
status: To Do
assignee: []
created_date: '2026-04-18 17:56'
labels:
  - skill-registry
  - cleanup
dependencies: []
documentation:
  - doc-1
priority: low
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
After Phase 3 ships and one release cycle passes, remove the legacy files.

See plan: doc-1, section "Phase 5: Delete legacy files".

**Deliverables:**
- Delete `skills/skill-rules.json`
- Delete `skills/activation.yaml`
- Delete `skills/recommendation-rules.json`
- Delete `schemas/skill-rules.schema.json`
- Delete `schemas/recommendation-rules.schema.json`
- Remove fallback branches from all three consumers that referenced those files

**Depends on:** Phase 3 + one release cycle (~1 week) to confirm no regressions
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 All five legacy files deleted
- [ ] #2 No dead code paths remain referencing them
- [ ] #3 Hook, recommender, activator still pass all validation tests
<!-- AC:END -->
