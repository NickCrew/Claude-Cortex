---
name: justfile-author
description: Use this skill when authoring or refactoring a justfile (and matching Makefile wrapper) for one of Nick's projects. Triggers when the user asks to "create a justfile", "add a justfile to this project", "set up just for…", "wire up tmux services", "scaffold the task runner", or when working in a repo that lacks a justfile but obviously needs one. Produces a justfile using zsh syntax with the standard svc-* tmux service family, the canonical build/lint/dev/test recipes, a thin Makefile passthrough wrapper that auto-installs just, and per-service tx-start.sh helpers. Do NOT use for editing existing third-party justfiles or non-Nick projects unless the user explicitly opts in.
---

# Justfile Author

## Overview

Generate a justfile (and matching Makefile + tx-start helpers) following Nick's
project conventions: zsh shell, DRY parameterized helpers, svc-* tmux service
family wired through `cortex tmux`, and standard quality recipes
(`build`, `lint`, `dev`, `test`, `typecheck`, `ci`, `clean`).

## When to use this skill

- A repo lacks a justfile and the user wants one.
- A justfile exists but is missing the svc-* family, the Makefile wrapper,
  or the standard quality recipes.
- The user asks to add a new service window (e.g., `svc-worker`) to an
  existing justfile.
- The user asks to refactor a justfile to be more DRY or to align with
  the conventions captured here.

Skip this skill when:

- Editing third-party / open-source justfiles (their conventions own).
- The user has explicitly chosen `make`, `npm scripts`, or another runner
  for this project.

## Reference example

`/Users/nick/Developer/Facet/justfile` and `/Users/nick/Developer/Facet/Makefile`
are the canonical reference. When in doubt, mirror their shape.

## Workflow

### Step 1 — Inspect the project

Before writing anything, read the project to determine:

1. **Project slug** — derive from the repo directory basename.
2. **Stack and package manager** — what language(s), which lockfile.
3. **Service catalog** — what long-running processes the dev runs locally.
4. **Existing tooling** — what build/test/lint commands the project
   already uses (do not invent new ones).
5. **Runtime activation needs** — nvm, asdf, uv, etc.

Consult `references/inspection-checklist.md` for the full detection table
and the exact slug-normalization rules.

### Step 2 — Choose the recipe block

Pull the right language reference into context:

| Stack  | Reference                     |
| ------ | ----------------------------- |
| Node   | `references/recipes-node.md`  |
| Rust   | `references/recipes-rust.md`  |
| Python | `references/recipes-python.md`|
| Go     | `references/recipes-go.md`    |

For polyglot repos, read multiple references and combine. For stacks not
listed, mirror the structure of the closest listed stack and substitute
the native commands.

### Step 3 — Choose the service catalog

Consult `references/service-patterns.md` for the full svc-* surface area
and the rules for when to add a new service window. Every detected
service gets a parallel pair of recipes (foreground + svc-) and a
`tx-start-<role>.sh` wrapper.

### Step 4 — Emit the files

Use `assets/justfile.tmpl`, `assets/Makefile.tmpl`, and
`assets/tx-start.sh.tmpl` as the structural starting points. These are
not literal templates — read them, then write the project's actual files
with the inspection results substituted and the irrelevant scaffolding
deleted.

Required substitutions in `justfile.tmpl`:

| Placeholder         | Value                                                  |
| ------------------- | ------------------------------------------------------ |
| `{{PROJECT_TITLE}}` | Human-readable project name (e.g., `Facet`).           |
| `{{PROJECT_SLUG}}`  | Normalized slug (lowercase, underscores).              |
| `{{INSTALL_CMD}}`   | From the language recipe block.                        |
| `{{DEV_CMD}}`       | From the language recipe block.                        |
| `{{BUILD_CMD}}`     | From the language recipe block.                        |
| `{{TYPECHECK_CMD}}` | From the language recipe block.                        |
| `{{LINT_CMD}}`      | From the language recipe block (omit if not configured).|
| `{{TEST_CMD}}`      | From the language recipe block.                        |
| `{{TEST_FILE_CMD}}` | From the language recipe block.                        |
| `{{TEST_WATCH_CMD}}`| From the language recipe block.                        |
| `{{CLEAN_CMD}}`     | Project-specific build artifacts.                      |

In `Makefile.tmpl`, also keep the `.PHONY` list and the passthrough
recipe block in sync with the recipes actually emitted in the justfile —
the catch-all rule pattern is intentionally NOT used; an explicit list
keeps `make help` honest.

For each service, copy `tx-start.sh.tmpl` to
`scripts/tx-start-<role>.sh`, uncomment the relevant runtime activation
block, and replace `{{SERVICE_CMD}}` with the actual launch command.
Make the script executable: `chmod +x scripts/tx-start-<role>.sh`.

### Step 5 — Validate

After writing the files, run these checks before declaring completion:

1. `just --list` — must succeed and show every recipe.
2. `make help` — must show the passthrough list.
3. For each `svc-<role>` recipe: confirm a matching `tx-start-<role>.sh`
   exists, is executable, and has the right activation block uncommented.
4. `just ci` — should be runnable end-to-end (don't actually run it
   unless the user wants to; just confirm the deps resolve).
5. Confirm `set shell := ["zsh", "-c"]` is present and that no recipe
   uses bash-specific syntax that would break under zsh.

If any check fails, fix it before reporting done.

## Style rules (non-negotiable)

These rules apply to every justfile produced by this skill:

- **Header**: comment block with project name, install hint, usage hint.
- **Settings**: `set dotenv-load := false` and `set shell := ["zsh", "-c"]`.
- **Project identity**: a `project` justfile variable holding the
  normalized slug, used to derive `svc_session` (via `env("TMUX_SESSION",
  project)`) and every `tmux_<role>_window` variable. Do NOT hardcode the
  session name as a string literal — go through `project` so renaming the
  project means changing one line.
- **Default recipe**: `default: @just --list`.
- **DRY service recipes**: every `svc-<role>` delegates to `_svc-start`;
  every `svc-stop-<role>` delegates to `_svc-stop`. Do not inline the
  tmux logic into individual service recipes.
- **Standard targets**: `install`, `dev`, `build`, `typecheck`, `lint`,
  `test`, `test-file`, `test-watch`, `ci`, `clean` — emit every one that
  the project's tooling supports; omit the rest with no placeholder.
- **`ci` recipe**: composes the static-check recipes — at minimum
  `typecheck`, `lint`, `test` (add `fmt-check` for Rust/Go projects).
- **Comments**: one short line per recipe explaining intent. Skip if the
  recipe name is self-explanatory (e.g., `clean:`).

## Style rules for the Makefile

- `SHELL := /bin/bash` and `JUST_DEST ?= $(HOME)/bin`.
- `default: help` showing every passthrough target.
- Single block listing every passthrough recipe; `read -p` prompt to
  install just on first use.
- `test-file` (and any other arg-bearing recipe) gets its own block that
  forwards `FILE=...` as a positional just arg.
- `install-just` cascade: brew → cargo → snap → official curl script,
  with `JUST_DEST` PATH advice if falling back to the script.

## Style rules for tx-start scripts

- `#!/usr/bin/env bash` and `set -euo pipefail`.
- Resolve `ROOT_DIR` from `${BASH_SOURCE[0]}` so the script works from
  any cwd.
- Activate the runtime if the project requires a specific version
  (otherwise leave the block commented and let the inherited shell win).
- Set env defaults via `${VAR:-default}` so the parent shell or `.env`
  always wins.
- End with `exec <command>` (not just `<command>`) so the wrapper PID
  becomes the service PID.

## Anti-patterns to avoid

- Using `bash` as the just shell. The project standard is zsh; use
  `set shell := ["zsh", "-c"]`.
- Hardcoding the tmux session name as a string. Go through `project`.
- Inlining the tmux logic in every `svc-*` recipe. Use the `_svc-start`
  helper instead.
- Calling `tmux capture-pane`, `tmux kill-window`, etc. directly. Always
  go through `cortex tmux`.
- Putting nvm/asdf activation in the justfile. That belongs in the
  `tx-start-*.sh` wrapper.
- Adding a `lint` recipe when the project has no linter configured. Omit
  the recipe entirely; do not emit one that will fail.
- Using `&&` chains where dependent recipes would be clearer (e.g.,
  `ci: typecheck lint test`, not `ci: && just typecheck && just lint && just test`).
- Catch-all `%:` rules in the Makefile. Keep the passthrough list
  explicit so `make help` stays an honest reference.

## Resources

- `assets/justfile.tmpl` — canonical justfile structure with svc-* family.
- `assets/Makefile.tmpl` — passthrough wrapper with install-just cascade.
- `assets/tx-start.sh.tmpl` — service launch script pattern.
- `references/inspection-checklist.md` — slug rules, stack detection,
  service catalog detection.
- `references/recipes-node.md` — pnpm/npm/yarn/bun command map.
- `references/recipes-rust.md` — cargo recipes.
- `references/recipes-python.md` — uv/poetry/pip recipes.
- `references/recipes-go.md` — go recipes.
- `references/service-patterns.md` — svc-* family, cortex tmux CLI,
  internal helper pattern.
