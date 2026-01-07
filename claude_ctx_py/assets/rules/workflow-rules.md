# Workflow Rules

## Task Flow
- Understand -> Plan -> TodoWrite (3+ tasks) -> Execute -> Track -> Validate.
- Claims must be supported by tests, logs, or docs.

## Execution Efficiency
- Use the strongest available tool; batch independent reads/edits in parallel.
- Use Task agents for multi-step or multi-file workstreams.

## Workspace Hygiene
- Remove temporary files and debug artifacts.
- Keep changes scoped to the request.

## Documentation Placement
- How-to guides: `docs/guides/`
- Tutorials: `docs/tutorials/`
- Reference + manpages + API: `docs/reference/`
- Development + contributor docs: `docs/development/`
- Architecture: `docs/architecture/`
- Diagrams: `docs/diagrams/` (or a local `diagrams/` next to the doc)
- Archive: `docs/archive/`

## Git Workflow
- Use feature branches or worktrees for parallel work.
- Start with `git status` and review `git diff` before staging.
- Follow @rules/git-rules.md for commit standards and attribution.
