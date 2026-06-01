---
layout: default
title: scripts/ Utilities
parent: Reference
nav_order: 6
summary: Project-internal maintenance and build scripts
read_when:
  - Maintaining one-off migration scripts
  - Migrating skill front matter
  - Repairing skill metadata
---

# scripts/ Utilities

Project-internal maintenance scripts for one-off migrations and metadata repair. These are not intended for routine agent use — they support repository maintenance when skill or agent metadata formats change.

> For agent-facing tools used during daily development (tmux, browser automation, commits), see [bin/ Utilities](bin-utilities.md).

## Overview

| Script | Language | Purpose |
|--------|----------|---------|
| `apply-delegate-when.py` | Python | Backfill or normalize agent delegation metadata |
| `apply-skill-keywords.py` | Python | Apply reviewed keyword metadata to skill front matter |
| `migrate-skill-keywords.py` | Python | Inventory and migrate skill keywords into `SKILL.md` front matter |
| `salvage-triggers-yaml.py` | Python | Repair malformed trigger/keyword YAML during skill metadata migrations |
| `strip-agent-fiction-fields.py` | Python | Remove deprecated generated agent metadata fields |

---

## Registry Validation

The skills registry is validated by the unit test suite, not by a standalone `scripts/` command.

Run the focused checks with:

```bash
python -m pytest tests/unit/test_skill_registry_sync.py
```

The tests cover:

| # | Check | What it validates |
|---|-------|-------------------|
| 1 | Schema validation | `registry.yaml` conforms to `registry.schema.json` (Draft 7) |
| 2 | Path existence | Skill `path` fields point to real directories |
| 3 | Dependency graph | No missing dependency references; no circular dependencies (DFS cycle detection) |
| 4 | Category consistency | Every skill category matches a defined category in the registry |
| 5 | Statistics | Counts in `statistics` block match actual skill counts by status |

### What it removes

1. **Rule symlinks** at `~/.claude/rules/cortex` (always removed if present).
2. **Python package** `claude-cortex` via `pip uninstall` (prompts for confirmation).

### Notes

- Safe to run multiple times — skips missing artifacts gracefully.
- Does not remove user configuration, memory vault data, or custom skills.
