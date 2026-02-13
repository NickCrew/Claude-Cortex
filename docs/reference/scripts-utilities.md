---
layout: default
title: scripts/ Utilities
parent: Reference
nav_order: 6
summary: Project-internal maintenance and build scripts
read_when:
  - Generating manpages
  - Validating the skills registry
  - Uninstalling the cortex package
  - Running CI checks on registry integrity
---

# scripts/ Utilities

Project-internal maintenance scripts for building, validating, and managing the cortex package itself. These are not intended for routine agent use — they support release engineering, CI pipelines, and package lifecycle tasks.

> For agent-facing tools used during daily development (tmux, browser automation, commits), see [bin/ Utilities](bin-utilities.md).

## Overview

| Script | Language | Purpose |
|--------|----------|---------|
| [`generate-manpages.py`](#generate-manpagespy) | Python | Generate roff manpages from argparse definitions |
| [`validate_registry.py`](#validate_registrypy) | Python | Validate skills registry against schema and business rules |
| [`uninstall.sh`](#uninstallsh) | Bash | Remove cortex plugin artifacts |

---

## generate-manpages.py

Generates roff-format manpages from the `cortex` CLI's argparse definitions. Outputs to `docs/reference/`.

### Usage

```bash
python3 scripts/generate-manpages.py
```

### What it generates

| File | Description |
|------|-------------|
| `docs/reference/cortex.1` | Main `cortex` manpage with all top-level commands |
| `docs/reference/cortex-tui.1` | TUI subcommand manpage |
| `docs/reference/cortex-workflow.1` | Workflow subcommand manpage |

### How it works

1. Imports `build_parser()` from `claude_ctx_py.cli` to get the live argparse tree.
2. Walks the parser and subparsers to extract commands, options, and descriptions.
3. Renders each into roff format with standard sections (NAME, SYNOPSIS, DESCRIPTION, COMMANDS, OPTIONS, ENVIRONMENT, FILES, SEE ALSO).

The generated manpages are committed to the repo so they're available after `cortex install post` runs.

---

## validate_registry.py

Validates the skills registry (`skills/registry.yaml`) against its JSON schema and a set of business rules. Used in CI and before releases to catch registry inconsistencies.

### Usage

```bash
python3 scripts/validate_registry.py
python3 scripts/validate_registry.py --verbose
python3 scripts/validate_registry.py --check-paths
```

### Options

| Option | Description |
|--------|-------------|
| `-v, --verbose` | Print detailed progress for each check |
| `--check-paths` | Treat missing skill paths as errors (default: warnings) |

### Validation checks

The validator runs six checks in order:

| # | Check | What it validates |
|---|-------|-------------------|
| 1 | Schema validation | `registry.yaml` conforms to `registry.schema.json` (Draft 7) |
| 2 | Author references | Every author ID in a skill exists in `authors.yaml` |
| 3 | Path existence | Skill `path` fields point to real directories |
| 4 | Dependency graph | No missing dependency references; no circular dependencies (DFS cycle detection) |
| 5 | Category consistency | Every skill category matches a defined category in the registry |
| 6 | Statistics | Counts in `statistics` block match actual skill counts by status |

### Exit codes

| Code | Meaning |
|------|---------|
| `0` | All checks passed |
| `1` | One or more errors found |

### Dependencies

Requires `jsonschema` and `PyYAML`:

```bash
pip install jsonschema pyyaml
```

---

## uninstall.sh

Removes cortex plugin artifacts from the system. Interactive — prompts before uninstalling the Python package.

### Usage

```bash
./scripts/uninstall.sh
```

### What it removes

1. **Rule symlinks** at `~/.claude/rules/cortex` (always removed if present).
2. **Python package** `claude-cortex` via `pip uninstall` (prompts for confirmation).

### Notes

- Safe to run multiple times — skips missing artifacts gracefully.
- Does not remove user configuration, memory vault data, or custom skills.
