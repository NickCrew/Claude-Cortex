# Git Rules

## Identity and Attribution (CRITICAL)
- Never include AI or Claude attribution in commit messages, trailers, or author metadata.
- Commits must be authored by the user's git identity.

## Commit Format
- Use Conventional Commits: `<type>(scope): <summary>`
- Keep commits atomic: one logical change per commit.
- Review `git status` and `git diff` before staging or committing.

Example: `fix(auth): prevent token refresh race`
