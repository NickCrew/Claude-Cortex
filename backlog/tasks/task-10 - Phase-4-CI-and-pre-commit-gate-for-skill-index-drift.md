---
id: TASK-10
title: 'Phase 4: CI and pre-commit gate for skill-index drift'
status: To Do
assignee: []
created_date: '2026-04-18 17:56'
labels:
  - skill-registry
  - ci
dependencies: []
documentation:
  - doc-1
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Prevent any future drift between SKILL.md front matter and the generated index.

See plan: doc-1, section "Phase 4: CI + pre-commit".

**Deliverables:**
- `.github/workflows/` job step: `cortex skills rebuild-index && git diff --exit-code skills/skill-index.json` — fails PR if index is stale
- `.pre-commit-config.yaml` hook entry running the same command (optional for contributors but documented)
- Docs update: `docs/devel/` contributor guide mentions running rebuild-index after SKILL.md edits

**Depends on:** Phase 3 (consumers already flipped so gate is meaningful)
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 CI fails on a test branch that edits SKILL.md without refreshing skill-index.json
- [ ] #2 Pre-commit hook is documented in contributor guide
- [ ] #3 Docs reference the rebuild-index command in developer onboarding
<!-- AC:END -->
