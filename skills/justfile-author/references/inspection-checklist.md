# Project inspection checklist

Run this checklist before generating a justfile. The output drives both the
language-specific recipe block (which `recipes-*.md` to consult) and the
service catalog (how many `svc-*` recipes to emit).

## Step 1 — Derive the project slug

The justfile `project` variable is derived from the repo directory name:

1. Take the basename of the repo root (the directory containing `.git/`).
2. Lowercase it.
3. Replace runs of whitespace, hyphens, and dots with a single underscore.
4. Strip leading/trailing underscores.

Examples:

| Directory      | Slug          |
| -------------- | ------------- |
| `Facet`        | `facet`       |
| `Atlas Crew`   | `atlas_crew`  |
| `my-app`       | `my_app`      |
| `cool.tool.v2` | `cool_tool_v2`|

## Step 2 — Detect the language and package manager

Look at the repo root. The first file that matches wins; the rest are
informational signals (e.g., a `Cargo.toml` next to a `package.json` means
it is a polyglot repo and both blocks may be needed).

| File                             | Stack    | Manager / Toolchain                                |
| -------------------------------- | -------- | -------------------------------------------------- |
| `pnpm-lock.yaml`                 | Node     | pnpm — see `recipes-node.md`                       |
| `bun.lockb` or `bun.lock`        | Node     | bun — see `recipes-node.md`                        |
| `yarn.lock`                      | Node     | yarn — see `recipes-node.md`                       |
| `package-lock.json`              | Node     | npm — see `recipes-node.md`                        |
| `package.json` (no lockfile)     | Node     | npm (default) — see `recipes-node.md`              |
| `Cargo.toml`                     | Rust     | cargo — see `recipes-rust.md`                      |
| `pyproject.toml` + `uv.lock`     | Python   | uv — see `recipes-python.md`                       |
| `pyproject.toml` + `poetry.lock` | Python   | poetry — see `recipes-python.md`                   |
| `pyproject.toml` (no lockfile)   | Python   | pip + venv (default) — see `recipes-python.md`     |
| `requirements.txt` only          | Python   | pip + venv — see `recipes-python.md`               |
| `go.mod`                         | Go       | go modules — see `recipes-go.md`                   |
| `mix.exs`                        | Elixir   | mix (out of scope; treat as freeform)              |
| `Gemfile`                        | Ruby     | bundler (out of scope; treat as freeform)          |

## Step 3 — Detect the service catalog

A "service" is anything that runs as a long-lived foreground process during
local development. Each gets its own `svc-<role>` recipe and matching tmux
window named `<project>-<role>`.

Detection sources, in priority order:

1. **`package.json` "scripts"** — entries named `dev`, `start`, `serve`,
   `dev:proxy`, `dev:worker`, `dev:web`, `dev:api`, etc. Each `dev:<role>`
   script becomes a separate svc recipe.
2. **`Procfile`** — each line is a service. The label before `:` is the role.
3. **`docker-compose.yml`** — services that the developer typically runs
   outside Docker (web, worker, queue consumer). Database/cache services
   usually stay in compose.
4. **`Cargo.toml` `[[bin]]` entries** — each binary that is a long-running
   server is a service.
5. **Python entry points** — `pyproject.toml` `[project.scripts]` entries
   that start with `serve`, `run-`, or contain `app`.
6. **`fly.toml` / `Dockerfile` `CMD`** — the production entry point usually
   maps to a single `dev` service.

If no clear service entry is found, emit only `svc-dev` and leave a comment
in the justfile pointing to where to add more.

## Step 4 — Detect the existing build/test/lint commands

For every standard quality target (`build`, `lint`, `test`, `typecheck`),
prefer commands already defined in the project. Do not invent new tools.

- **Node**: read `package.json` `"scripts"`. If `lint` script exists, use
  `pnpm run lint`; if not, check for `eslint.config.*` or `.eslintrc*` and
  shell out to `pnpm exec eslint .`. Same pattern for `typecheck` (script
  → `tsc --noEmit` if `tsconfig.json` exists).
- **Rust**: standard cargo subcommands. Lint = `cargo clippy --all-targets
  --all-features -- -D warnings`. Typecheck = `cargo check`.
- **Python**: read `pyproject.toml` for `[tool.ruff]`, `[tool.mypy]`,
  `[tool.pytest.ini_options]`. Use whichever the project actually configures.
- **Go**: `go build ./...`, `go test ./...`, `go vet ./...`, `golangci-lint
  run` if `.golangci.yml` exists.

If a tool isn't configured, omit its recipe rather than emitting one that
will fail. The user can add it later.

## Step 5 — Detect runtime activation needs

The `tx-start-*.sh` wrapper handles runtime activation. Check for:

- `.nvmrc` or `engines.node` in `package.json` → add the nvm block
- `.python-version` or `pyproject.toml` `requires-python` → uv handles it
  via `uv run`; only add an asdf/pyenv block if neither uv nor poetry is in
  use
- `.tool-versions` → add the asdf block
- `rust-toolchain.toml` → cargo handles it; no activation needed

If none of these signals are present, leave the activation block commented
out in `tx-start-*.sh` and let the inherited shell environment handle it.
