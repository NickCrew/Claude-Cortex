# Codex CLI Reference

## Invocation

```bash
codex --full-auto c [--uncommitted|--base <BRANCH>|--commit <SHA>]
```

## Modes

### --uncommitted (Recommended for single-repo or isolated work)

Reviews all uncommitted and unstaged changes in the current working directory.

```bash
codex --full-auto c --uncommitted
```

**Use when:**
- You have only your changes in the working directory
- No other agents' work is mixed in
- You want to review everything you've modified since the last commit

**Output:** Review markdown written to `.agent/reviews/review-<timestamp>.md`

### --base <BRANCH> (Branch comparison)

Reviews all changes between the specified branch and HEAD.

```bash
codex --full-auto c --base origin/main
codex --full-auto c --base main
```

**Use when:**
- You want to compare your current branch against a specific baseline
- In pull request workflows to see what you've changed relative to main

**Output:** Review markdown written to `.agent/reviews/review-<timestamp>.md`

### --commit <SHA> (Specific commit - Monorepo safe)

Reviews only the specified commit's changes. Useful in monorepos where multiple agents work simultaneously.

```bash
codex --full-auto c --commit abc1234
codex --full-auto c --commit HEAD
```

**Use when:**
- You've committed your changes to the repository
- Other agents have uncommitted or untracked changes in the working directory
- You want to review ONLY your commit, not anyone else's work

**Output:** Review markdown written to `.agent/reviews/review-<timestamp>.md`

**Monorepo workflow:**
```bash
# 1. Commit only your changes
git add <your-files>
git commit -m "Your change"

# 2. Get the commit SHA (e.g., abc1234)
COMMIT_SHA=$(git rev-parse HEAD)

# 3. Review that specific commit
codex --full-auto c --commit $COMMIT_SHA

# 4. Read and process review at .agent/reviews/review-<timestamp>.md

# 5. If fixes needed, amend the commit
git add <fixed-files>
git commit --amend --no-edit

# 6. Loop back to step 3 for re-review
```

---

## Output Format

After running `codex --full-auto c`, codex generates a markdown review file at:

```
.agent/reviews/review-<TIMESTAMP>.md
```

Where `<TIMESTAMP>` is in format: `YYYYMMDD-HHMMSS` (e.g., `20260218-143021`)

**The review markdown contains:**
- Summary of files reviewed
- Iteration number (1 of 3, 2 of 3, etc.)
- Findings organized by severity (P0, P1, P2, P3)
- Each finding includes:
  - Finding ID (e.g., `P0-001`)
  - Title
  - File and line range
  - Description of the issue
  - Impact
  - Suggested fix
- Overall verdict: `APPROVE` / `REQUEST CHANGES` / `BLOCKED`

See `references/review-format.md` for detailed format specification.

---

## Output Directory

Codex always writes reviews to `.agent/reviews/` relative to the project root.

To locate the latest review:
```bash
ls -t .agent/reviews/review-*.md | head -1
```

To read the latest review:
```bash
cat "$(ls -t .agent/reviews/review-*.md | head -1)"
```

---

## Environment Variables

Optional environment variables that affect codex behavior (if applicable):

- `CODEX_TIMEOUT` — Max seconds for codex to spend on review (default varies)
- `CODEX_MAX_BUDGET` — Max USD budget for review invocation (default varies)

Check `codex --help` for current supported environment variables.

---

## Exit Codes

- **0** — Review completed successfully; review file written to `.agent/reviews/`
- **Non-zero** — Error (codex CLI failure, git error, etc.); check stderr for details

---

## Diff Size Limits

If your diff is extremely large (>2000 lines), codex may truncate or reject it. In this case:

1. Review a smaller subset of files using path filters (if available)
2. Split the work into smaller commits
3. Review each commit separately

Contact codex documentation or maintainers for guidance on handling large diffs.
