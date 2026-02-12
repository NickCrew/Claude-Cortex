# Branching Strategies

Branching models, merge policies, and release management patterns for collaborative teams. Use when establishing or evolving version control workflows, onboarding teams to a branching model, or choosing between competing strategies.

## Git Flow

A structured model with long-lived branches for development, releases, and hotfixes. Best for projects with scheduled release cycles and multiple supported versions.

### Branch Structure

```
main ─────────────────────────────────────────────► (production)
  │                                      ▲
  │                              merge ──┘
  ▼                                      │
develop ──────────────────────────► release/1.2 ──► (stabilize, then merge to main + develop)
  │         ▲         ▲
  │  merge ─┘  merge ─┘
  ▼         │         │
feature/a ──┘         │
feature/b ────────────┘

hotfix/urgent ──► (branch from main, merge to main + develop)
```

### Rules

- `main` always reflects production
- `develop` is the integration branch for the next release
- Feature branches branch from and merge back to `develop`
- Release branches branch from `develop`, stabilize, then merge to `main` and `develop`
- Hotfix branches branch from `main`, fix, then merge to `main` and `develop`

### When to Use

- Products with versioned releases (v1.0, v1.1, v2.0)
- Teams that need a clear release stabilization phase
- Multiple versions supported simultaneously

### When to Avoid

- Continuous delivery / continuous deployment
- Small teams that deploy on every merge
- Projects where `develop` and `main` would always be identical

## GitHub Flow

A simple model where `main` is always deployable and all work happens on short-lived branches with pull requests.

### Branch Structure

```
main ──────────────────────────────────────────► (always deployable)
  │              ▲              ▲
  │       merge ─┘       merge ─┘
  ▼              │              │
feature/auth ────┘              │
feature/search ─────────────────┘
```

### Rules

1. `main` is always deployable
2. Branch from `main` for any change
3. Open a PR early for visibility
4. Merge to `main` only after review and CI passes
5. Deploy immediately after merge

### When to Use

- Continuous deployment environments
- Small to medium teams
- SaaS products with a single production version
- Teams that prioritize simplicity

### When to Avoid

- Multiple supported versions in production
- Projects requiring release stabilization
- Regulated environments needing formal release gates

## Trunk-Based Development

All developers commit to `main` (trunk) frequently. Feature flags control incomplete work in production.

### Branch Structure

```
main ──────────────────────────────────────────► (always deployable)
  │        ▲     │        ▲
  │ merge ─┘     │ merge ─┘
  ▼        │     ▼        │
short/a ───┘   short/b ───┘
(< 1 day)      (< 1 day)
```

### Rules

1. Branches live less than one day (ideally hours)
2. Feature flags hide incomplete work from users
3. All commits pass CI before merging
4. No long-lived branches except `main`
5. Release from `main` at any time (release branches are optional, short-lived snapshots)

### When to Use

- High-velocity teams with strong CI/CD
- Organizations practicing continuous delivery
- Teams with mature testing and feature flag infrastructure

### When to Avoid

- Teams without feature flag infrastructure
- Low test coverage (incomplete work would ship)
- Highly regulated environments without compensating controls

## Monorepo Strategies

### Path-Based Ownership

```
monorepo/
├── packages/auth/      ← Team A owns
├── packages/billing/   ← Team B owns
├── packages/frontend/  ← Team C owns
└── CODEOWNERS
```

**CODEOWNERS file:**
```
packages/auth/      @team-auth
packages/billing/   @team-billing
packages/frontend/  @team-frontend
```

### Selective CI

Only build and test what changed:

```yaml
# Trigger CI only for changed paths
on:
  push:
    paths:
      - 'packages/auth/**'
      - 'shared/utils/**'
```

**Tools for change detection:**
- `git diff --name-only main...HEAD` to find changed files
- Build tools with built-in change detection (Nx, Turborepo, Bazel)
- Path-based CI triggers in GitHub Actions, GitLab CI

### Monorepo Considerations

| Concern | Approach |
|---------|----------|
| CI time | Selective builds, remote caching |
| Code ownership | CODEOWNERS, path-based review rules |
| Dependencies | Shared packages with explicit versioning |
| Merge conflicts | Smaller, more frequent PRs |
| Repository size | Git LFS for binaries, shallow clones |

## Branch Naming Conventions

### Recommended Format

```
<type>/<ticket>-<short-description>

Examples:
  feature/AUTH-123-oauth-login
  fix/BUG-456-null-pointer-checkout
  chore/INFRA-789-upgrade-node
  hotfix/SEC-012-xss-sanitize
  release/1.2.0
```

### Type Prefixes

| Prefix | Purpose |
|--------|---------|
| `feature/` | New functionality |
| `fix/` | Bug fix |
| `hotfix/` | Urgent production fix |
| `chore/` | Maintenance, dependencies, tooling |
| `release/` | Release stabilization |
| `experiment/` | Spike or proof of concept (may be discarded) |

### Naming Rules

- Use lowercase with hyphens (no spaces, no underscores)
- Include ticket/issue number when available
- Keep descriptions under 5 words
- Delete branches after merge

## Merge vs Rebase Policies

### Merge Commit (No Fast-Forward)

```
main: A ─── B ─── M (merge commit)
               ╲ ╱
feature:        C ─ D
```

**Pros:** Preserves full branch history, easy to revert entire feature
**Cons:** Cluttered history with merge commits
**When:** Default for most teams; required when branch history matters

### Squash Merge

```
main: A ─── B ─── S (single squashed commit)

feature: C ─ D ─ E  (branch commits discarded)
```

**Pros:** Clean linear history on main, one commit per PR
**Cons:** Loses granular commit history from the branch
**When:** Feature branches with messy/WIP commits; most PRs

### Rebase and Fast-Forward

```
main: A ─── B ─── C' ─── D' (rebased commits)
```

**Pros:** Perfectly linear history, no merge commits
**Cons:** Rewrites history (dangerous if branch is shared), harder to revert a feature as a unit
**When:** Solo branches, clean commit discipline, linear history requirement

### Policy Decision Guide

| Factor | Merge | Squash | Rebase |
|--------|-------|--------|--------|
| History clarity | Moderate | High | High |
| Feature revertability | Easy | Easy | Hard (must revert multiple commits) |
| Commit discipline required | Low | Low | High |
| Safe for shared branches | Yes | Yes | No |
| Team consensus needed | Low | Low | High |

**Recommended default:** Squash merge for feature branches, merge commit for release branches.

## Release Management Patterns

### Semantic Versioning

```
MAJOR.MINOR.PATCH

1.0.0 → 1.0.1  (patch: backward-compatible bug fix)
1.0.1 → 1.1.0  (minor: backward-compatible new feature)
1.1.0 → 2.0.0  (major: breaking change)
```

### Release Trains

Scheduled releases at fixed intervals regardless of feature completeness.

```
Week 1: Feature freeze for v1.2
Week 2: Stabilization and testing
Week 3: Release v1.2, start v1.3 development
```

**Pros:** Predictable cadence, reduced release anxiety
**Cons:** Features may miss the train, artificial deadlines

### Continuous Release

Every merge to main is a potential release. Deploy gates (CI, canary, rollback) replace manual release processes.

```
Merge to main → CI → Canary deploy (5%) → Monitor → Full deploy
                                            ↓ (if errors)
                                         Auto-rollback
```

### Release Checklist

- [ ] All CI checks pass on the release commit
- [ ] Changelog updated with user-facing changes
- [ ] Version bumped (tag or version file)
- [ ] Release notes drafted
- [ ] Rollback plan documented
- [ ] Deployment monitoring dashboards ready
- [ ] Stakeholders notified of release window
