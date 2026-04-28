# Node recipe block

Use this when `package.json` exists. The package manager is determined by
the lockfile (see `inspection-checklist.md` step 2).

## Package manager command map

| Action                | pnpm                | npm                 | yarn                | bun                |
| --------------------- | ------------------- | ------------------- | ------------------- | ------------------ |
| Install deps          | `pnpm install`      | `npm install`       | `yarn install`      | `bun install`      |
| Run script `<s>`      | `pnpm run <s>`      | `npm run <s>`       | `yarn <s>`          | `bun run <s>`      |
| Exec installed bin    | `pnpm exec <bin>`   | `npx <bin>`         | `yarn <bin>`        | `bunx <bin>`       |
| Add a dep             | `pnpm add <pkg>`    | `npm install <pkg>` | `yarn add <pkg>`    | `bun add <pkg>`    |

Below, `pnpm` is shown; substitute for the detected manager.

## Standard recipes

### install

```just
install:
    pnpm install
```

### dev / svc-dev

```just
dev:
    pnpm run dev
```

The `dev` script in `package.json` is the canonical entry point; do not
hardcode `vite dev` / `next dev` — let the package script handle it so the
recipe stays correct when the framework changes.

### build

```just
build:
    pnpm run build
```

### typecheck

If `tsconfig.json` exists:

- Prefer `pnpm run typecheck` if a `typecheck` script is defined.
- Otherwise use `pnpm exec tsc --noEmit`.

```just
typecheck:
    pnpm exec tsc --noEmit
```

### lint

- Prefer `pnpm run lint` if a `lint` script is defined.
- Otherwise, if `eslint.config.*` or `.eslintrc*` exists, use
  `pnpm exec eslint .`.
- Skip the recipe entirely if no linter is configured.

```just
lint:
    pnpm run lint
```

### test / test-file / test-watch

Detect the test runner from `devDependencies` or `package.json` scripts.

**Vitest:**
```just
test:
    pnpm run test

test-file file:
    pnpm exec vitest run {{ file }}

test-watch:
    pnpm exec vitest
```

**Jest:**
```just
test:
    pnpm run test

test-file file:
    pnpm exec jest {{ file }}

test-watch:
    pnpm exec jest --watch
```

**Playwright (e2e, in addition to unit tests):**
```just
test-e2e:
    pnpm exec playwright test

test-e2e-ui:
    pnpm exec playwright test --ui
```

### clean

```just
clean:
    rm -rf dist .next .nuxt build coverage
```

Trim to only the directories the project actually produces.

## Service multi-window patterns

Common Node service shapes:

| App type                      | Services                              |
| ----------------------------- | ------------------------------------- |
| Vite SPA                      | `dev`                                 |
| Next.js                       | `dev`                                 |
| Vite SPA + local API proxy    | `dev`, `proxy`                        |
| Monorepo with web + api       | `web`, `api` (and any `worker`)       |
| App + background worker       | `dev`, `worker`                       |

For each service, emit:

- A `svc-<role>` recipe that delegates to `_svc-start`
- A matching `svc-stop-<role>` that delegates to `_svc-stop`
- A line in `svc-up: ...` and `svc-stop: ...`
- A `tx-start-<role>.sh` wrapper

## Framework-specific notes

- **Next.js**: `next dev` opens its own port (default 3000). The `tx-start`
  wrapper rarely needs to do more than `exec pnpm run dev`.
- **Vite**: same as Next.
- **Astro**: `astro dev` is the entry; same pattern.
- **NestJS / Express**: usually started via `pnpm run start:dev` (which
  wraps `nodemon` or `tsx watch`). Check the existing `start:dev` script.
- **SvelteKit**: `vite dev` under the hood; treat as Vite.
