---
id: TASK-12
title: 'Phase 6: Gap-fill keywords for unregistered skills'
status: Done
assignee: []
created_date: '2026-04-18 17:56'
updated_date: '2026-04-19 04:12'
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
- [x] #1 Every skill in the gap report has at least 3 keywords in its SKILL.md front matter
- [x] #2 Gap report in docs/devel/reports/ is empty or deleted
- [x] #3 cortex skills analyze returns sensible matches for each previously-unregistered skill
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Phase 6 complete. All 143 skills in the index now have keywords.

**Approach:**
- Delegated keyword extraction to an Explore subagent (textbook isolation + large_scope case — 64 SKILL.md reads that would otherwise burn main-thread context)
- Augmented the subagent's output with single-token fallbacks and the full skill-name-as-phrase for each skill (e.g., adding "blog", "post", "blog post" to blog-post's keywords so prompts like "write a blog post" match on substring)
- Applied via `scripts/apply-skill-keywords.py` — kept in repo for future gap-fills when new skills are added

**Results:**
- Gap report shrunk from 64 → 0 skills
- `cortex skills rebuild-index` no longer emits any `empty keywords` warnings
- Smoke-tested: "help me write a blog post" surfaces `blog-post`, "design a KPI dashboard" surfaces `dashboard-designer`, "proofread my essay" surfaces `proofreader`, "compliance audit for GDPR" surfaces `compliance-audit` — all skills that were invisible before.

**Known tuning opportunity (separate workstream):**
The `cortex hooks skill-suggest` ranking treats prompt-match, file-context-match, and git-context-match hits with equal weight. Recent git activity dominates top-5 suggestions when the prompt is short. Not a Phase 6 blocker — every skill has keywords now — but weighting prompt matches ~2x would improve signal. Future commit.

**Files:**
- 63 modified SKILL.md files (one skill name was already handled)
- `skills/skill-index.json` regenerated (143 skills, all with keywords)
- `docs/devel/reports/skill-keywords-needing-review.md` updated to show 0 gaps
- `scripts/apply-skill-keywords.py` — reusable for future new-skill gap-fills
<!-- SECTION:FINAL_SUMMARY:END -->
