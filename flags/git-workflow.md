# Git & PR Workflow Flags

Flags for version control best practices, PR workflows, and commit discipline.

**Estimated tokens: ~160**

---

**--pr-ready**
- Trigger: Before creating pull request, pre-merge validation, code review preparation
- Behavior: Comprehensive PR checklist validation and preparation
- Checks: Tests passing, coverage maintained, docs updated, no merge conflicts, CI green
- Generates: PR description with context, changelog entry, affected areas, testing notes
- Suggests: Reviewers based on code ownership, related PRs, breaking changes callout
- Validates: Conventional commits, linked issues, meaningful commit messages
- Prepares: Screenshots (if UI), migration guide (if breaking), rollback plan

**--commit-discipline**
- Trigger: Feature development, team collaboration, clean git history
- Behavior: Enforce conventional commits and atomic, meaningful changes
- Format: `type(scope): subject` - feat, fix, docs, refactor, test, chore, perf, ci
- Validates: Commit message quality, logical grouping, single responsibility per commit
- Prevents: WIP commits, "fix typo" commits, massive multi-concern commits
- Ensures: Atomic commits (revertable), descriptive messages, proper scope
- Examples: `feat(auth): add OAuth2 support`, `fix(api): handle null response`

**--changelog**
- Trigger: Release preparation, semantic versioning, user-facing changes
- Behavior: Auto-generate changelog from conventional commits
- Format: Keep a Changelog (Added, Changed, Deprecated, Removed, Fixed, Security)
- Groups: By version and category, breaking changes highlighted prominently
- Sources: Commit messages, PR labels, release tags, issue references
- Validates: Semantic version bumps match change significance
- Tools: conventional-changelog, standard-version, semantic-release

**--branch-strategy**
- Trigger: Team collaboration, release management, environment deployments
- Behavior: Enforce consistent branching strategy (Git Flow, GitHub Flow, Trunk-Based)
- Patterns: feature/, bugfix/, hotfix/, release/ prefixes
- Validates: Branch naming conventions, base branch correctness, merge strategy
- Ensures: Protected branches, required reviews, status checks before merge
- Strategies: Git Flow (main/develop/feature), GitHub Flow (main/feature), Trunk-Based

**--git-hygiene**
- Trigger: Repository maintenance, clean history, team onboarding
- Behavior: Maintain clean git repository and history
- Checks: No large files (use LFS), .gitignore completeness, no committed secrets
- Validates: No merge commits in feature branches (rebase preferred), linear history
- Cleans: Stale branches, unused remotes, dangling commits
- Prevents: Binary files in repo, IDE configs, OS files (.DS_Store), node_modules
- Tools: git-lfs, BFG Repo-Cleaner, git-filter-repo

**--semantic-versioning**
- Trigger: Package releases, API versioning, dependency management
- Behavior: Enforce semantic versioning (MAJOR.MINOR.PATCH)
- Rules: MAJOR (breaking), MINOR (features), PATCH (fixes)
- Validates: Version bumps match change types from commits
- Generates: Version tags, release notes, migration guides for breaking changes
- Ensures: Version consistency across package.json, setup.py, Cargo.toml, etc.
- Related: Conventional commits → automatic version determination
