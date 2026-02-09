---
name: specialist-review
description: Multi-perspective specialist code review that delegates to the Claude CLI. This skill is for non-Claude agents (Codex, Gemini, etc.) that need a thorough code review. The calling agent MUST shell out to the Claude CLI via the bundled script and read the result file. It must NOT attempt to perform the review itself. Claude agents are excluded — Claude has native access to the skills ecosystem and can review directly.
---

# Specialist Review

Delegate a multi-perspective code review to the Claude CLI. This skill is for
**non-Claude agents** (Codex, Gemini, and similar) that lack access to the skills
ecosystem. Claude agents do not need this skill — they can review code directly
using the perspective catalog and skills.

## IMPORTANT: Do Not Review the Code Yourself

**If you are Codex, Gemini, or any non-Claude agent: your ONLY job is to run the
script and read the output file. Do NOT analyze the diff. Do NOT write review
comments. Do NOT adopt perspectives. Shell out and read the result.**

The review requires Claude's skills ecosystem (JIT loading of domain-specific skills
like `owasp-top-10`, `secure-coding-practices`, `python-testing-patterns`, etc.).
Non-Claude agents do not have access to these skills. Attempting the review yourself
produces a shallow, generic review that misses the domain expertise these skills
provide. The script invokes a Claude CLI instance that has full access.

## How to Invoke

### Step 1: Run the script

```bash
# Review current changes vs last commit
skills/specialist-review/scripts/specialist-review.sh --git

# Review changes since a specific ref
skills/specialist-review/scripts/specialist-review.sh --git origin/main

# Review a diff file
skills/specialist-review/scripts/specialist-review.sh /path/to/changes.diff

# Pipe in a diff
git diff HEAD~5..HEAD | skills/specialist-review/scripts/specialist-review.sh -

# Custom output directory
skills/specialist-review/scripts/specialist-review.sh --git HEAD~1 ./my-reviews
```

### Step 2: Read the result

The script prints the output file path to stdout on success. Read that file.

```bash
REVIEW_FILE=$(skills/specialist-review/scripts/specialist-review.sh --git origin/main)
cat "$REVIEW_FILE"
```

The review file contains: triage (selected perspectives), per-perspective findings
with severity ratings, synthesis with cross-cutting concerns and risk interactions,
and a verdict (APPROVE / APPROVE WITH CHANGES / REQUEST CHANGES).

### Step 3: Act on findings

- Fix CRITICAL issues immediately
- Fix IMPORTANT issues before merge
- Note MINOR issues for follow-up
- NITs are optional

## Anti-Patterns

- **Performing the review yourself** — You do not have the skills ecosystem. Shell
  out to the script. This is the most common failure mode.
- **Summarizing the diff before shelling out** — Unnecessary. The script reads the
  diff directly. Do not pre-process it.
- **Ignoring the output file** — The review is written to a file. Read it and act
  on the findings. Do not assume it passed.
- **Using sub-agents for the review** — The script invokes a single Claude CLI
  process. Do not spawn sub-agents.
