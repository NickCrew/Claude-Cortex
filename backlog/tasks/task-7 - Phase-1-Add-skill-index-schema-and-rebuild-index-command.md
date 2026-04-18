---
id: TASK-7
title: 'Phase 1: Add skill-index schema and rebuild-index command'
status: Done
assignee: []
created_date: '2026-04-18 17:56'
updated_date: '2026-04-18 18:03'
labels:
  - skill-registry
  - infrastructure
dependencies: []
documentation:
  - doc-1
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Land the skill-index infrastructure without touching any consumer yet. This phase is reversible and ships in isolation — the index is built but nothing reads it until Phase 3.

See plan: doc-1 (Skill Registry Consolidation Plan), section "Phase 1: Schema + rebuild-index command".

**Deliverables:**
- `schemas/skill-index.schema.json` — JSON schema describing the generated index
- `claude_ctx_py/skill_index.py` — new module with `build_index(skills_root) -> IndexDoc`, `load_index(path) -> IndexDoc`, `_parse_skill_front_matter(skill_md_path)`
- `cortex skills rebuild-index` — new CLI subcommand wired in `claude_ctx_py/cli.py` under the existing `skills` command group
- `tests/unit/test_skill_index.py` — unit tests covering: happy path, missing front matter, duplicate names, nested paths (collaboration/brainstorming), empty keywords (warning not error), deterministic output
- Must pass `mypy --strict claude_ctx_py/skill_index.py`

**Invariants:**
- Output is deterministic (sorted skills by name, stable field order, no generated_at if that's not stable across reruns — decide during impl)
- Uses existing `_extract_front_matter()` in `claude_ctx_py/core/base.py`
- Zero new runtime deps; stdlib only where possible (PyYAML already in deps)

**Non-goals for this task:**
- Do NOT modify the hook, recommender, or activator
- Do NOT generate the index file itself (that's Phase 2)
- Do NOT add CI gate (that's Phase 4)
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 schemas/skill-index.schema.json exists and validates against a sample index
- [x] #2 claude_ctx_py/skill_index.py exposes build_index, load_index, and passes mypy --strict
- [x] #3 cortex skills rebuild-index runs, prints summary, writes skills/skill-index.json deterministically
- [x] #4 Running rebuild-index twice produces zero git diff
- [x] #5 tests/unit/test_skill_index.py covers happy path, duplicates, nested paths, missing front matter, empty keywords
- [x] #6 No changes to hooks/skill_auto_suggester.py, skill_recommender.py, or activator.py
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Phase 1 landed. skill-index infrastructure is in place without touching any consumer.

**Added:**
- `schemas/skill-index.schema.json` — draft-07 schema describing the generated index (name, path, description, keywords, file_patterns, confidence per entry)
- `claude_ctx_py/skill_index.py` — build_index/load_index/write_index/rebuild_index + _parse_skill_front_matter. Deterministic output (sorted skills, sorted+deduped keyword/pattern arrays, canonical key order, trailing newline). Skips hidden directories (e.g. `.system/`) so infrastructure skills cannot collide with user-facing ones.
- `cortex skills rebuild-index` CLI subcommand wired via `_build_skills_parser` + `_handle_skills_command`, with thin `skill_rebuild_index` wrapper in `core/skills.py`
- `tests/unit/test_skill_index.py` — 22 tests covering happy path, sorted output, nested paths (collaboration/*), duplicate-name errors, missing name, malformed YAML, triggers-as-keywords alias, empty keywords (warn not error), out-of-range confidence, deterministic writes, round-trip load, hidden-dir filter, and CLI entrypoint success/failure/idempotency

**Validated:**
- mypy --strict: 1 source file, 0 issues
- pytest: 22/22 passing
- End-to-end against real /Users/nick/Developer/Cortex/skills: 143 skills indexed, identical SHA on back-to-back runs (idempotent)
- Hidden-dir filter caught a real collision: `.system/skill-creator` vs `skill-creator` — fixed during smoke test

**Not included (deferred per plan):**
- `skills/skill-index.json` not committed (that belongs to Phase 2 after migration script populates keywords)
- Consumers untouched (Phase 3)
- No CI gate yet (Phase 4)
<!-- SECTION:FINAL_SUMMARY:END -->
