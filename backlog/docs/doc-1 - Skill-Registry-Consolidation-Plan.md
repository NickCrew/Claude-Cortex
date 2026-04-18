---
id: doc-1
title: Skill Registry Consolidation Plan
type: other
created_date: '2026-04-18 17:55'
---
# Skill Registry Consolidation

**Status:** Proposed
**Created:** 2026-04-18
**Context:** Three parallel skill-keyword registries have drifted; ~half of shipped skills are invisible to the auto-suggestion hook and CLI analyzer
**Approach:** Front matter becomes source of truth; one generated index file serves all consumers

## Problem

Three files describe skill keywords for three different consumers, and none of them stay in sync:

| File | Consumer | Shape | Count |
|---|---|---|---|
| `skills/skill-rules.json` | `hooks/skill_auto_suggester.py` (UserPromptSubmit hook) | Rule-centric, flat keyword list | 34 skills |
| `skills/activation.yaml` | `claude_ctx_py/activator.py` → `cortex skills analyze` | Skill-keyed keyword lists | 62 skills |
| `skills/recommendation-rules.json` | `claude_ctx_py/skill_recommender.py` (rule strategy) | Rule-centric, glob-based | 68 skill targets |

Disk has **132 skill directories**. Concretely:

- **70 skills on disk are absent from `activation.yaml`** — entire categories (research, UX, workflow-*, design, compliance, product) are invisible to the CLI analyzer.
- **9 skills listed in `skill-rules.json` are absent from `activation.yaml`** — the ideation/collaboration cluster (`brainstorming`, `idea-lab`, `mashup`, `pre-mortem`, `concept-forge`, etc.).
- **8 skills referenced by `recommendation-rules.json` don't exist on disk** — `ctx-brainstorming`, `ctx-plan-writing`, `ctx-plan-execution` (stale `ctx-` prefix), plus collaboration skills that live in nested directories the rules never resolved.

There is no CI enforcement. A contributor can ship a new skill, see it listed in the in-tool skills loader, and discover months later that no keyword hook will ever suggest it.

Nine SKILL.md files already carry `keywords:` in their front matter (notably `agent-loops`). The convention exists. It just isn't the source of truth.

## Goals

1. **Single source of truth** — keywords, file patterns, and confidence defaults live in each skill's own `SKILL.md` front matter, alongside its description.
2. **All three consumers read the same artifact** — one generated `skills/skill-index.json` serves the hook, the recommender, and the CLI analyzer.
3. **CI catches drift** — it is impossible to merge a SKILL.md change without refreshing the index.
4. **Portable regeneration** — `cortex skills rebuild-index` is the canonical command, usable on any platform with the package installed. `just` and Homebrew become thin wrappers.
5. **Ship fully built** — end users never regenerate. The wheel includes a current `skill-index.json`; `pip install cortex` is sufficient.

## Non-Goals

- **Not** rewriting the keyword matching algorithms in the consumers. Hook keeps hit-count ranking; recommender keeps its four-strategy blend; CLI analyzer keeps its boolean membership query.
- **Not** changing skill activation UX or thresholds.
- **Not** adding embedding-based keyword similarity (the semantic matcher already handles that inside `SkillRecommender`).
- **Not** designing the Homebrew tap beyond a follow-on scope note.

## Architecture

### Source of truth: SKILL.md front matter

```yaml
---
name: agent-loops
description: Complete operational workflow for implementer agents ...
keywords:
  - agent workflow
  - atomic commit
  - test writing loop
  - lint gate
file_patterns:          # optional; drives recommender's rule strategy
  - "**/agents/**"
confidence: 0.85        # optional; default for file_patterns matches (default 0.8)
---
```

**Absorbed fields:**
- `keywords:` subsumes both `skill-rules.json` keywords *and* `activation.yaml` keywords. The distinction was never semantic — consumers all do substring checks. Migration merges and dedupes.
- `triggers:` (currently in 2 of 9 existing front-matter skills) — treat as a synonym for `keywords` during migration; the reader accepts both keys.
- `file_patterns:` from `recommendation-rules.json` moves per-skill.
- `confidence:` from `recommendation-rules.json` moves per-skill as a default.

**What stays in registry files:** nothing. After migration, the three legacy files are deleted.

### Generated artifact: `skills/skill-index.json`

Single file, committed to the repo, shipped in the wheel. Consumed by all three call sites. Shape:

```json
{
  "$schema": "../schemas/skill-index.schema.json",
  "version": "2026-04-18",
  "generated_from": "SKILL.md front matter",
  "generated_at": "2026-04-18T12:00:00Z",
  "skills": [
    {
      "name": "agent-loops",
      "path": "agent-loops",
      "description": "Complete operational workflow ...",
      "keywords": ["agent workflow", "atomic commit", ...],
      "file_patterns": [],
      "confidence": 0.85
    }
  ]
}
```

`path` is the directory name relative to `skills/`, supporting nested layouts (`collaboration/brainstorming`) without flattening.

### Consumers after migration

| Consumer | Before | After |
|---|---|---|
| `hooks/skill_auto_suggester.py` | Reads `skill-rules.json`; falls back to `claude_ctx_py.SkillRecommender` | Reads `skill-index.json` directly (stdlib JSON only) |
| `claude_ctx_py/skill_recommender.py::_load_rules` | Reads `recommendation-rules.json` | Reads `skill-index.json`; constructs rules from `file_patterns` + `confidence` |
| `claude_ctx_py/activator.py` | Reads `activation.yaml` via PyYAML | Reads `skill-index.json`; the module shrinks to ~40 lines |

The hook keeps its zero-dependency guarantee — stdlib `json.load` on one file.

### Regeneration: `cortex skills rebuild-index`

New CLI subcommand under `cortex skills`. Walks `skills/*/SKILL.md`, parses front matter via `_extract_front_matter()` (exists in `core/base.py`), writes `skill-index.json`.

Idempotent. Deterministic output (sorted skills, stable field order) so `git diff` is clean on reruns.

Fails loudly on:
- Missing `name` / `description`
- Duplicate `name` values across directories
- Malformed YAML front matter
- `keywords` non-list or empty (warning, not error — some skills legitimately have none yet)

## Migration

### Seed keywords from existing registries

One-shot Python script at `scripts/migrate-skill-keywords.py`:

1. Load all three existing registries.
2. For each skill present in any registry, union the keywords (dedupe case-insensitive).
3. For each skill with a `file_patterns` rule in `recommendation-rules.json`, carry it forward.
4. Parse existing SKILL.md, merge merged keywords into its front matter.
5. Write the updated SKILL.md preserving body content exactly.

Pre-merge reconciliation rules:
- **Conflict on confidence** (multiple rules for same skill with different confidences) — take the max.
- **Stale name refs** (`ctx-brainstorming` etc.) — script maintains a rename map (`RENAMES = {"ctx-brainstorming": "brainstorming", ...}`) and applies it.
- **Skill in registry but no matching dir** — log to `docs/devel/reports/skill-migration-orphans.md` for manual review; skip.

### Dead-ref cleanup

Applied during migration:
- `ctx-brainstorming` → `brainstorming`
- `ctx-plan-writing` → `writing-plans`
- `ctx-plan-execution` → `executing-plans`
- `idea-lab`, `mashup`, `pre-mortem`, `concept-forge`, `assumption-buster` — verify path under `skills/collaboration/*`, record `path: "collaboration/<name>"` in index

### Gap fill for 70 unregistered skills

Script emits a report `docs/devel/reports/skill-keywords-needing-review.md` listing every SKILL.md whose front matter keywords are empty after seeding. Follow-on workstream: human or Claude pass populates keywords skill-by-skill, informed by the skill's description.

Not blocking — an index entry with zero keywords is legal, just never auto-suggested until filled.

## Implementation

### Phase 1: Schema + rebuild-index command

- Add `schemas/skill-index.schema.json`
- Add `claude_ctx_py/skill_index.py` with `build_index()`, `load_index()`, `_parse_skill_front_matter()`
- Wire `cortex skills rebuild-index` subcommand in `claude_ctx_py/cli.py`
- Unit tests in `tests/unit/test_skill_index.py`

### Phase 2: Migrate SKILL.md files

- Run `scripts/migrate-skill-keywords.py` once, commit the diff
- Commit the generated `skill-index.json`
- Commit `docs/devel/reports/skill-keywords-needing-review.md`

### Phase 3: Rewrite consumers

Three commits, independently reviewable:
1. `hooks/skill_auto_suggester.py` reads `skill-index.json` (stdlib only, no new deps)
2. `claude_ctx_py/skill_recommender.py::_load_rules` reads `skill-index.json`
3. `claude_ctx_py/activator.py` reads `skill-index.json`; drops PyYAML import

### Phase 4: CI + pre-commit

- `.github/workflows/*.yml` job: `cortex skills rebuild-index && git diff --exit-code skills/skill-index.json`
- `.pre-commit-config.yaml` hook: same command, local only (optional for contributors)

### Phase 5: Delete legacy files

After Phase 3 ships and a release cycle passes (~1 week):
- Remove `skills/skill-rules.json`
- Remove `skills/activation.yaml`
- Remove `skills/recommendation-rules.json`
- Remove `schemas/skill-rules.schema.json`, `schemas/recommendation-rules.schema.json`

### Phase 6: Gap fill

Low-priority, ongoing. Each unregistered skill gets a keyword pass; rebuild-index after each batch.

## Distribution

### Wheel / sdist

`pyproject.toml` already declares `skills/` as package data (verify during Phase 1). `skill-index.json` is a regular file in that tree; no new packaging work needed.

### End user flow

1. `pip install cortex` — index shipped, nothing to regenerate
2. Hook activates on next `UserPromptSubmit` — reads bundled index
3. `cortex skills analyze "..."` — reads same bundled index

### Contributor flow

1. `pip install -e ".[dev]"` — editable install, index shipped from last commit
2. Edit a SKILL.md — front matter now includes keywords
3. Run `cortex skills rebuild-index` (or let pre-commit do it)
4. Commit both SKILL.md and skill-index.json changes

### Safety net in readers

If `skill-index.json` is missing OR older than any `SKILL.md` mtime, emit a single stderr warning:

```
cortex: skill-index.json appears stale; run `cortex skills rebuild-index`
```

**Do not auto-rebuild.** System-wide installs have no write access to site-packages; auto-rebuild would fail silently or inconsistently. Loud warning + manual command is the safer contract.

## Validation

- All 132 skill directories produce an entry in `skill-index.json`
- `cortex skills analyze "REST API"` returns `api-design-patterns` (parity with today)
- `cortex skills analyze "accessibility"` now returns `accessibility-audit` (was missing pre-migration)
- UserPromptSubmit hook on a prompt containing "prompt engineering" surfaces `prompt-engineering` (was missing)
- `skill_recommender.py` unit tests still pass without modification to test fixtures
- CI job fails on a test branch that edits SKILL.md without rebuilding index
- `python -c "import yaml"` is no longer required for `cortex skills analyze`

## Rollout

Sequenced to avoid a flag day:

1. Phase 1 merges — command exists but nothing consumes the index
2. Phase 2 merges — index is now committed; `skill-index.json` is correct and up-to-date alongside the legacy files
3. Phase 3 ships over ~3 commits — each consumer flips independently; legacy files remain as fallback
4. Phase 4 adds CI guard
5. Phase 5 deletes legacy files after a release boundary

Rollback story: if Phase 3 breaks a consumer, revert that single commit. The legacy files are still on disk until Phase 5.

## Follow-on: Homebrew tap

Out of scope for this plan; listed here so it isn't forgotten.

A tap at e.g. `nickfergs/homebrew-cortex` could provide macOS/Linux ergonomics:

- `generate_completions_from_executable(bin/"cortex", "completions")` — requires a `cortex completions bash|zsh|fish` subcommand (small follow-on)
- `man1.install "docs/reference/cli/man/cortex.1"` — requires manpage generation (`argparse-manpage` in CI)
- `post_install` block runs `cortex skills rebuild-index` after install, even though the shipped wheel already has a current index — defense in depth

The tap is additive. It does not change the pip install story, and nothing in this plan assumes Homebrew is present. Windows users would eventually get parallel treatment via `winget` or `scoop`; the same `cortex completions` / manpage primitives serve both.

## Open questions

1. Do we ship a `keywords` linter? Something like `cortex skills lint` that warns on keywords shorter than 3 chars, duplicated across skills, or containing regex metacharacters that won't substring-match as expected. Low priority, worth a ticket.
2. Should `confidence` be keyword-specific or skill-specific? Current plan is skill-specific (single default). If a skill has multiple `file_patterns` with different confidences, we'd need per-pattern objects. Defer until a use case appears.
3. `triggers:` vs `keywords:` — kept as aliases during migration. Collapse to one field after Phase 5?
