---
name: atomic-commits
description: Use this skill when a working tree contains uncommitted changes that need to be split into a sequence of atomic commits — typically after a long session, an agent hand-off, a rebase resolution, or anytime `git status` shows mixed work that was not committed as it landed. The skill assumes the agent has fresh context and did not author most of the diff, so it treats the working tree as evidence to investigate before grouping. Optimizes for `git bisect`: each commit is the smallest buildable and deployable unit, and no smaller. Uses `cortex git commit` for file-level commits and `cortex git patch --diff` when unrelated changes share a file.
---

# Atomic Commits

## Overview

Take a dirty working tree of uncertain provenance and produce a clean, linear sequence of atomic commits where every commit builds, every commit could be reverted in isolation, and `git bisect` will land on a meaningful unit when chasing a regression. The agent does not assume it remembers what changed — it investigates, classifies, groups, then commits.

## Core Principle: The Bisect Test

Every commit must satisfy this test:

> If `git bisect` lands on this commit alone, can the project still build, run its test suite, and be deployed? And does the commit's title accurately describe a single coherent change?

This produces two rules that govern every grouping decision:

1. **Smallest buildable + deployable unit.** Do not split a change so finely that an intermediate commit fails to compile, breaks tests, or leaves an import dangling. A new module and its first caller belong together if the caller would not compile without the module.
2. **No smaller, no larger.** Do not bundle two unrelated improvements just because they touched the same file. Two bug fixes in `auth.py` should be two commits — bisect cannot tell which one introduced a regression if they ship together.

When the two pull in different directions, prefer the smaller commit and add the minimum scaffolding (e.g., a stub, a no-op default) needed to keep the tree green.

## Workflow

### Phase 1 — Survey

Before classifying anything, get a complete picture of the working tree.

```bash
git status --short
git diff --stat
git diff                       # unstaged
git diff --cached              # staged (rare in this workflow but check)
git log -10 --oneline          # recent history for tone/style of messages
```

If there are staged changes already, decide whether to keep them as-is (commit first) or unstage to reclassify (`git reset HEAD`) — but never use destructive resets. When unsure, ask the user.

### Phase 2 — Investigate

Treat the diff as code written by someone else. For each modified file:

1. **Read the full diff** for the file (`git diff -- path/to/file`), not just the hunks summary.
2. **Read surrounding code** when the diff alone does not explain intent — function signatures, imports, related call sites.
3. **Note the *kind* of change** for each hunk: feature addition, bug fix, refactor, test, docs, formatting, dependency bump, generated/lockfile, config, dead-code removal.
4. **Note dependencies between hunks**: does hunk B import a symbol introduced by hunk A? Does a test in `tests/` exercise a new function in `src/`?

Write a brief mental (or scratch) inventory: a list of logical changes, each tagged with the files and hunks it spans. This inventory is what gets converted into commits.

### Phase 3 — Group

Map the inventory of logical changes onto a commit sequence:

- **One logical change → one commit.** A bug fix and the regression test that proves it is *one* logical change and belongs in *one* commit.
- **Order commits to keep the tree green.** Foundations first (new module, then its callers; new field on a struct, then code that reads it; new test fixture, then tests using it). Never schedule a commit that depends on a symbol introduced by a later commit.
- **Refactors are their own commits.** A behavior-preserving rename or extraction should not ride along with a behavioral change. If a feature commit also contains an unrelated refactor, split them.
- **Generated files travel with the change that regenerates them.** A lockfile bump goes with the dependency change that caused it; a generated client goes with the schema change.
- **Formatting-only changes are their own commit, ideally first or last.** Mixing a reformat into a feature commit obscures the diff under review and confuses bisect.
- **Docs, tests, and code touching the same change live together.** Splitting these is over-fragmentation and breaks the "deployable" half of the rule.

If a single file contains hunks belonging to multiple logical changes, plan to use `cortex git patch` (Phase 4 — hunk-level path).

### Phase 4 — Commit

Use the right tool for the shape of the commit.

#### File-level: `cortex git commit`

When every hunk in each named file belongs to the same logical change, commit the files whole:

```bash
cortex git commit "feat(auth): add OAuth2 device flow support" \
  src/auth/oauth_device.py tests/auth/test_oauth_device.py
```

This stages the named files in full from the working tree and commits atomically. Use this whenever possible — it's the simplest and safest path.

#### Hunk-level: `cortex git patch --diff`

When a file contains hunks that belong to *different* logical changes, isolate the hunks for one commit via a diff fed through `--diff`. The `files` positional is an allowlist — the command will refuse to commit if the diff stages anything outside that list, so name only the files this particular commit should touch.

Two practical ways to produce the diff:

**Option A — interactive split via temp file.** Generate the file's full diff, edit it down to only the hunks for this commit, then apply:

```bash
git diff -- src/auth/oauth_device.py > /tmp/commit-1.diff
# edit /tmp/commit-1.diff in place: delete hunks that don't belong in this commit
cortex git patch "fix(auth): reject device codes after expiry" \
  --diff /tmp/commit-1.diff src/auth/oauth_device.py
```

**Option B — stdin pipe.** Build the targeted diff with `git diff` flags or by piping through filters, and feed via `-`:

```bash
git diff -- src/auth/oauth_device.py \
  | filter-hunks-script \
  | cortex git patch "fix(auth): reject device codes after expiry" \
      --diff - src/auth/oauth_device.py
```

After each hunk-level commit, the remaining hunks for that file stay in the working tree, ready to be committed (whole or split again) by the next call.

**Strongly prefer hunk-level commits over bundling unrelated changes.** Two bug fixes in the same file should not share a commit. The hunk-level path is the right tool, not a last resort.

#### Commit message conventions

Recent history in most Cortex/Nick projects uses Conventional Commits with lowercase types:

- `feat(scope): summary` — new behavior
- `fix(scope): summary` — bug fix
- `refactor(scope): summary` — behavior-preserving change
- `docs(scope): summary` — docs only
- `test(scope): summary` — tests only
- `chore(scope): summary` — tooling, deps, build
- `build(scope): summary` — packaging, lockfiles

Always check `git log -10 --oneline` first and match the project's actual style.

### Phase 5 — Verify

After the last commit, confirm the result:

```bash
git status                  # working tree should be clean (or only contain
                            # changes you explicitly chose not to commit)
git log -N --oneline        # N = number of commits you just made
git diff HEAD~N..HEAD --stat
```

Spot-check that:

- Every commit's diff stat looks coherent (no surprise files).
- Commit messages name a single change each.
- The order respects build dependencies (foundations before callers).

If a commit looks wrong, do **not** rewrite history with destructive operations. Either continue with a follow-up `fix:` commit or escalate to the user before any rebase.

## Decision Heuristics

When uncertain about a grouping call, use these defaults:

| Situation | Default |
|---|---|
| Bug fix + its regression test | One commit |
| New feature + its unit tests | One commit |
| New feature + integration tests + docs | One commit if tightly coupled; split docs only if substantial |
| Two unrelated bug fixes, same file | Two commits via `cortex git patch` |
| Refactor that enables a feature | Two commits: refactor first, then feature |
| Lockfile change | Bundled with the dependency edit that caused it |
| Generated file (codegen, schema, types) | Bundled with the source change that regenerates it |
| Pure reformatting across many files | Its own commit, kept separate from logic |
| Dead code removal | Its own commit unless it's directly enabled by the change you're making |
| Config change + code that reads it | One commit |
| One commit you're unsure about | Smaller, with hunk-level patch — bisect rewards atomicity |

## Pitfalls to Avoid

- **Don't commit dirty files you didn't author** without checking with the user first. If `git status` shows changes outside the scope you were asked to handle, surface them rather than sweeping them in.
- **Don't use `git add` directly.** It bypasses Cortex's safety checks. Use `cortex git commit` or `cortex git patch`.
- **Don't use `git reset --hard`, `git checkout --`, or `git stash drop`** to "clean up" — these destroy uncommitted work. If a state is confusing, investigate rather than reset.
- **Don't break the build to make commits smaller.** A commit that fails to compile is worse than a commit that bundles two related changes. Add a stub if needed and remove it in a follow-up.
- **Don't separate a fix from its test.** If `bisect` lands on the fix and the test is in a later commit, the bisect tool can't validate the fix actually worked at that point.
- **Don't reorder commits if the original order had a reason** (e.g., a dependency upgrade that unblocks an API change). Keep the natural order; only reorder for build-greenness.
- **Don't blindly trust your read of the diff.** When unsure what a hunk does, read the surrounding code or run the relevant test. Wrong groupings are hard to repair after the fact.
