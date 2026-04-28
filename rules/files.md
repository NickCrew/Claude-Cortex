# File Management Rules

> _What to do with files in the working tree: where they live, when to
> delete, when to ignore. Git mechanics live in `git-rules.md`; tool
> choice for file ops (e.g. `trash` vs `rm`) lives in `tools.md`._

## Moving, renaming, and reverting

- Moving and renaming files is allowed without asking.
- Restoring a file you deleted earlier in the same session is allowed.
- Revert a file only when the change is yours or the user explicitly
  asks. If a git operation leaves you unsure about other agents'
  in-flight work, stop and coordinate instead of reverting.

## Deletion

- Delete unused or obsolete files when your changes make them irrelevant
  (refactors, feature removals, replaced modules).
- **Before attempting to delete a file to resolve a local type/lint
  failure, stop and ask the user.** Other agents are often editing
  adjacent files; deleting their work to silence an error is never
  acceptable without explicit approval.
- Coordinate with other agents before removing their in-progress edits —
  don't revert or delete work you didn't author unless everyone agrees.
- Use `trash` rather than `rm` (see `tools.md`) so deletions are
  recoverable.

## Scratch and temporary files

- Use `/tmp/` for truly ephemeral files: one-command intermediate
  output, throwaway logs, single-shot scripts. They vanish on reboot,
  which is the point.
- Use a project-local gitignored scratch directory (e.g. `tmp/` or
  `.scratch/`) for experiments that need to outlive a single command
  but don't belong in the codebase. Clean it up before ending the task.
- Do not leave debugging scaffolding (one-off scripts, sample inputs,
  reproduction files) in the working tree at task end. Either promote
  the file to a real location and commit it, or delete it.
- Plan documents and analysis tied to ongoing work belong in Backlog
  (see `documentation.md`), not loose `*.md` files at the repo root.

## Generated and local-state files

- Never commit generated artifacts: build output, coverage reports,
  compiled assets, lockfile churn from local-only tools. Add a
  `.gitignore` entry the moment you notice one slipping through.
- Local state files (e.g. `.active-*`, `.env.local`, editor caches)
  must be gitignored. If one is already tracked, fix the `.gitignore`
  and untrack the file in a separate, scoped commit. Use the
  `cortex git` workflow for the untrack; escalate to the user if no
  clean `cortex git` path exists.
- Treat `.gitignore` itself as a deliberate file: group entries by
  category, and add a one-line comment if the reason for an entry
  isn't obvious from the path.

## Large and binary files

- Don't commit substantial binaries (recordings, large images, captured
  data, profiling traces) without checking with the user — they bloat
  history irreversibly. Prefer LFS, an external store, or a reference
  link.
- Small intentional binaries are fine: icons, screenshots embedded in
  docs, test fixtures. Screenshots and diagrams belong in
  `docs/assets/` (per `documentation.md`), not loose at the project
  root.
- One-off binary outputs go to `/tmp/` or a gitignored scratch
  directory, not into commits.

## Symlinks

- Symlinks within the working tree are fine when they reflect a real
  asset relationship (e.g. this repo's `agents/`, `skills/`,
  `commands/` symlinked into `~/.claude/` for plugin testing). Note
  the link's purpose nearby if it isn't obvious.
- Don't commit symlinks that point into user-specific home directories
  with absolute paths — they break for everyone else.

## Naming

- Lowercase hyphen-case for files and directories (`my-feature.md`,
  `skills/my-skill/`). Exceptions: language or tool conventions
  (`README.md`, `Makefile`, `Cargo.toml`, `__init__.py`).
- Filenames describe content, not version or status. Avoid
  `final-v2.md`, `new-cli.py`, `temp.json`. If something is "new" or
  "temp," it's either replacing an existing file (rename and delete
  the old) or it's scratch (and doesn't belong in the tree).
