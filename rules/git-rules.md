# Git Rules

> _What to do with the working tree, the index, and history. File-level
> rules (deletion, scratch files, naming) live in `files.md`; tool
> choice (`cortex git` vs raw `git`) and escalation paths live in
> `tools.md`._

## Commits

- Use atomic commits with `git bisect` in mind.
- Use Conventional Commits: `<type>(scope): <summary>`.
- Only commit files using the `cortex git commit` (files) or
  `cortex git patch` (hunks). It is the safest way to stage files
  and hunks.
- Do not use `git add` without explicit permission. Instead, use
  `cortex git`.
- Never use destructive git actions like `git reset --hard` or
  `git checkout`.
- You may modify dirty files as long your intended changes do not
  overlap. Use `git diff` before you modify a dirty file to ensure
  your planned changes do not overlap and then commit with
  `cortex git patch`. If you need to modified an already-modified line in a file, escalate to the user.
- Always group changes into logical commits that bisect well. If a file has changes
  from more than one logical group, you may stage hunks using
  `cortex git patch`. If that is not possible, go with the grouping
  with the majority of changes.
- Commit changes you authored without asking — this overrides the harness
  default "commit only when the user asks." Use `cortex git commit`;
  branch-vs-PR policy is under PRs below. In a mixed working tree, stage only
  your own hunks with `cortex git patch` and leave others' work uncommitted.
- Never commit files or changes you did not touch unless the user explicitly
  asks.
- Prefer creating new commits over amending. Use `--amend` only when
  the user explicitly asks.
- Avoid merge commits. Prefer linear history.

## What "atomic" means in practice

A commit is atomic when all of the following hold:

- It bisects well (i.e. it builds and runs)
- It serves a single stated purpose.
- The commit message subject is one clean sentence — not "and"-chained.
  If you find yourself writing "also" or "additionally" in the
  subject, split the commit.
- Reverting the commit reverses a coherent unit (no half-rollback
  effect).
- Mixed concerns get split: feature + unrelated cleanup is two
  commits, not one. Refactor + behavior change is two commits.

The `atomic-commits` skill has the full workflow for splitting a
mixed working tree into a sequence of clean commits — reach for it
when the working tree has accumulated more than one logical group.

## PRs

- Commit directly to main unless the user explicitly requests a PR.

## Branches

### Strategy

- Always work off of the `main` branch unless the user explicitly asks you to branch.
- Prefer worktrees unless the user explicitly asks for a normal branch.
- Create worktrees under a `.worktrees/` directory at the repository root.
- `.worktrees/` is ignored by git globally
- Branch names should be short and descriptive, in lowercase hyphen-case and prefixed by the issue number (when one exists/is known)
- Before switching branches, ensure dirty state is committed, stashed,
  or genuinely intentional for the destination. Don't carry unrelated
  work-in-progress across a branch boundary.
- Deleting your own merged local branches is fine. Deleting remote
  branches requires explicit user approval.
- Long-lived feature branches drift into pain. If a branch is more
  than a week behind `main`, surface that to the user before
  continuing — rebase or restructure the work; don't paper over the
  divergence.

## Conflicts

- Resolve, don't discard. Read both sides of every conflict and
  produce a merged result that respects the intent of each. Wholesale
  `--ours` or `--theirs` is rarely correct; if a side really should
  win entirely, name the side and the reason in the resolution
  commit message.
- If a conflict's intent isn't obvious from the diff, escalate to the
  user before resolving — guessing at intent corrupts history.
- After resolving, run the build and the relevant tests before
  finalizing the conflict-resolution commit. Conflicts that compile
  but are semantically wrong are a known failure mode.

## Stash

- Stash is for transient context-switches, not storage. If you stash
  something, you intend to pop it within the same session.
- When you stash, name it: `git stash push -m "<short reason>"`. An
  unlabeled stash queue becomes opaque after two entries.
- Don't leave stashes behind at task end. Either pop and commit, or
  drop with a clear note. Long-lived stashes are a known source of
  lost work.

## Hooks and signing

- Never use `--no-verify`, `--no-gpg-sign`, or other hook/signing
  bypasses unless the user explicitly asks. If a hook fails,
  investigate and fix the underlying issue rather than skipping it.
- A failed pre-commit hook means the commit did not happen. Do not
  reach for `--amend` to "rescue" — fix the issue, re-stage, and
  create a new commit. Amending after a hook failure modifies the
  previous commit, which is rarely what's intended.

## Reading state before acting

- Run `git status` and `git diff` before any commit, branch switch,
  or other shape-changing operation. The shape of the working tree is
  the authoritative source of truth — not your memory of what you
  changed.
- If you find unfamiliar files, branches, or stashes, investigate
  before touching them. They may represent another agent's in-flight
  work (see `files.md` for the deletion rule).
