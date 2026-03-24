---
layout: default
title: Git Workflow
parent: Guides
nav_order: 13
---

# Git Workflow

`cortex git` is a narrow, safety-oriented Git surface for AI agents. It is not
trying to replace every Git command. It covers the operations Cortex wants
agents to perform repeatedly without widening the blast radius.

## What It Is For

Use `cortex git` when you want to:

- make an atomic commit of specific files only
- commit a reviewed diff instead of the whole working tree
- push with protected-branch safety checks
- switch branches without losing uncommitted work
- manage task-scoped worktrees

If you need advanced history surgery or other one-off Git operations, use raw
Git intentionally. For normal agent loops, prefer the safer Cortex wrapper.

## Atomic Commit Workflow

The most important command is:

```bash
cortex git commit "docs(site): add git workflow guide" site/guides/git-workflow.md
```

This wrapper is designed to keep commits small and explicit:

- it requires the commit message first
- it requires specific file paths, not directories or `.`
- it unstages everything first
- it stages only the files you listed
- it warns about non-conventional commit messages or suspiciously broad commits

Those warnings are advisory, but the staging behavior is strict.

## Patch-Based Commit Workflow

When another tool has already prepared a diff, use:

```bash
cortex git patch "fix(docs): tighten tmux examples" \
  --diff review.diff \
  site/guides/tmux-workflow.md
```

Or pipe a diff from stdin:

```bash
git diff -- site/guides/tmux-workflow.md | \
  cortex git patch "docs(site): revise tmux guide" --diff - \
  site/guides/tmux-workflow.md
```

`cortex git patch` applies the diff to the index, verifies that the staged
files match the allowlist you passed, and then commits. This is useful when you
want a very tight "only these hunks in these files" workflow.

## Branch Safety

Create a branch without switching:

```bash
cortex git branch create docs/git-tmux-guides
cortex git branch create docs/git-tmux-guides --from main
```

Switch only when the tree is clean:

```bash
cortex git branch switch docs/git-tmux-guides
```

That distinction is intentional:

- `branch create` does not move the current agent off its branch
- `branch switch` refuses when the working tree is dirty

That helps agents avoid accidental context switches in a half-finished tree.

## Push Safety

Push using the tracking remote and current branch:

```bash
cortex git push
```

Or name them explicitly:

```bash
cortex git push origin docs/git-tmux-guides
```

Force push exists, but Cortex blocks it on protected branches such as `main`
and `master`:

```bash
cortex git push --force origin docs/git-tmux-guides
```

This is meant to reduce the most common "agent did the dangerous obvious thing"
failure mode.

## Safe Stash Workflow

```bash
cortex git stash save "wip docs cleanup"
cortex git stash list
cortex git stash apply
cortex git stash drop --confirm
```

The safety bias here is:

- `apply` keeps the stash entry instead of popping it
- `drop` requires `--confirm`

That makes stash loss a deliberate action instead of an easy mistake.

## Worktree Workflow

`cortex git worktree` is the cleanest way to isolate parallel tasks.

List existing worktrees:

```bash
cortex git worktree list
```

Create one for a branch:

```bash
cortex git worktree add docs/git-tmux-guides
```

Create from a specific base ref:

```bash
cortex git worktree add docs/git-tmux-guides --base main
```

By default Cortex chooses a worktree base directory, creates it if needed, and
adds the directory to `.gitignore` unless you opt out with `--no-gitignore`.

You can inspect or configure the base directory directly:

```bash
cortex git worktree dir
cortex git worktree dir .worktrees
cortex git worktree dir --clear
```

Remove a worktree by branch name or path:

```bash
cortex git worktree remove docs/git-tmux-guides
```

Prune stale metadata:

```bash
cortex git worktree prune --dry-run
cortex git worktree prune --verbose
```

## Recommended Agent Pattern

For most implementation tasks, a good default is:

```bash
# isolate the task
cortex git worktree add docs/git-tmux-guides --base main

# make one focused change
cortex git commit "docs(site): add git workflow guide" \
  site/guides/git-workflow.md

# ship once reviewed
cortex git push
```

That keeps branch state, working tree state, and commit scope easier to reason
about than raw Git does under agent pressure.

## Related

- [Tmux Workflow]({% link guides/tmux-workflow.md %}) -- run and watch agent work in named windows
- [Agent Loops]({% link guides/agent-loops.md %}) -- atomic commit discipline and quality gates
- [Export Context]({% link guides/export.md %}) -- package the right context for parallel work
