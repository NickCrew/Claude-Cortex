# Git Rules

## Identity and Attribution (CRITICAL)
- Never include AI or Claude attribution in commit messages, trailers, or author metadata.
- Commits must be authored by the user's git identity.

## Commits

- Only commit files using the `committer` tool. It is the safest way to stage files and hunks.
- Use Conventional Commits: `<type>(scope): <summary>`
- Keep commits atomic: one logical change per commit.
- Review `git status` and `git diff` before staging or committing.
- You must get explicit permission and provide a good reason before each invocation of the `git add` command.
- Never use destructive git actions like `git reset --hard` or `git checkout`
- You may modify dirty files as long your intended changes do not overlap. Use `git diff` before you modify a dirty file to ensure your planned changes do not overlap. If they do, you must escalate to the user. 
- Always group changes into logical commits. If a file has changes from more than one logical group, you may stage hunks using `committer --patch`. If that is not possible, go with the grouping with the majority of changes. 
- Never commit files you did not touch unless the user explicitly asks.

Example: `fix(auth): prevent token refresh race`

