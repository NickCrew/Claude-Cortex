---
id: TASK-10
title: 'Phase 4: CI and pre-commit gate for skill-index drift'
status: Done
assignee: []
created_date: '2026-04-18 17:56'
updated_date: '2026-04-19 00:22'
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
- [x] #1 CI fails on a test branch that edits SKILL.md without refreshing skill-index.json
- [x] #2 Pre-commit hook is documented in contributor guide
- [x] #3 Docs reference the rebuild-index command in developer onboarding
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Phase 4 landed. Drift between SKILL.md front matter and skill-index.json is now prevented at two gates.

**Added:**
- `.github/workflows/skill-index.yml` — runs on PR + push to main, triggered by changes to any SKILL.md, the skill-index, or the build/CLI code that generates it. Single job on ubuntu + Python 3.12: installs via `uv sync --dev`, runs `cortex skills rebuild-index`, fails if `git diff --exit-code skills/skill-index.json` finds any change. Emits `::error::` annotations with the fix command when drift is detected.
- `.pre-commit-config.yaml` — local `rebuild-skill-index` hook, optional but convenient. Installs with `pip install pre-commit && pre-commit install`. Runs `cortex skills rebuild-index && git diff --exit-code skills/skill-index.json` on any commit touching `skills/**/SKILL.md`. Blocks the commit if the resulting index differs from what was staged.
- `docs/devel/skill-index-maintenance.md` — contributor reference covering when to regenerate, how to regenerate, pre-commit install, CI enforcement, and three common error modes with fixes.

**Validated:**
- End-to-end drift simulation: edited `skills/canvas-design/SKILL.md`, ran rebuild, confirmed `git diff --exit-code` returns non-zero → CI gate would fail the PR. Reverted the edit, reran rebuild, confirmed `git diff --exit-code` returns zero → CI gate would pass.
- `.github/workflows/skill-index.yml` syntax validated by explicit re-read (no external YAML linter invoked, but the format matches the repo's other workflows).

**Deferred:**
- CONTRIBUTING.md already has pending user edits (URL renames, Set Up Environment removal). Did not modify it to avoid overlapping hunks. The `docs/devel/skill-index-maintenance.md` doc serves the same purpose and can be linked from CONTRIBUTING.md in a later commit once the pending edits land.

**Not included:**
- Legacy file removal (`skill-rules.json`, `activation.yaml`, `recommendation-rules.json`) — Phase 5
<!-- SECTION:FINAL_SUMMARY:END -->
