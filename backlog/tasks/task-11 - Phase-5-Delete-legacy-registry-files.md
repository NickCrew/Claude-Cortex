---
id: TASK-11
title: 'Phase 5: Delete legacy registry files'
status: Done
assignee: []
created_date: '2026-04-18 17:56'
updated_date: '2026-04-19 03:22'
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
- [x] #1 All five legacy files deleted
- [x] #2 No dead code paths remain referencing them
- [x] #3 Hook, recommender, activator still pass all validation tests
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Phase 5 landed. All five legacy registry files are gone and every consumer reads from skill-index.json exclusively.

**Deleted:**
- `skills/skill-rules.json`
- `skills/activation.yaml`
- `skills/recommendation-rules.json`
- `schemas/skill-rules.schema.json`
- `schemas/recommendation-rules.schema.json`

**Fallback code removed:**
- `claude_ctx_py/skill_recommender.py` — removed `self.rules_path` init, the `recommendation-rules.json` fallback branch, `_get_default_rules()` (9 hardcoded rules), and `_save_rules()`. If no index is readable the rule strategy simply produces no recommendations; the other three strategies (semantic/agent/pattern) continue to function.
- `claude_ctx_py/hooks/skill_suggest.py` — removed `candidate_rule_paths()` and the legacy loop in `load_entries()`. Also removed the `CLAUDE_SKILL_RULES` env var from the docstring.
- `claude_ctx_py/core/asset_discovery.py` — removed `skills/activation.yaml`, `skills/recommendation-rules.json`, `skills/skill-rules.json` from `_SETTINGS_RELATIVE_PATHS`.

**Not deleted:**
- `hooks/skill_auto_suggester.py` standalone script — kept as backward-compat shim for users whose `~/.claude/settings.json` still references it directly. Will be removed in a follow-up cleanup after sufficient time for users to run `cortex hooks install skill-suggest`.

**Validated:**
- mypy --strict: 0 issues on modified modules
- 41/41 tests passing
- `cortex hooks skill-suggest` fires correctly on prompts containing keywords from the new index
- `cortex skills analyze "REST API"` returns `api-design-patterns`
- `SkillRecommender` loads 68 rules from bundled `skill-index.json` (same count as before)
<!-- SECTION:FINAL_SUMMARY:END -->
