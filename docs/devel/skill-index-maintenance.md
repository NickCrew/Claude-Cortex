# Skill Index Maintenance

`skills/skill-index.json` is the single source of truth consumed by the
UserPromptSubmit hook, the `SkillRecommender`, and `cortex skills analyze`.
It is generated from the front matter of every `SKILL.md` file and committed
to the repository.

This doc is for contributors editing skills. Users never regenerate the index —
the wheel ships a current copy.

## When you need to regenerate

Any time you change front matter in a `SKILL.md` file:

- Adding a skill
- Renaming a skill
- Editing `keywords`, `file_patterns`, `confidence`, or `description`
- Moving a skill to a different directory

Body-only edits (the markdown content after the second `---` block) do not
require regeneration.

## How to regenerate

```bash
cortex skills rebuild-index
git add skills/skill-index.json
```

Output is deterministic — running the command twice with no intervening
`SKILL.md` edits produces identical bytes.

## Pre-commit hook (optional)

To catch drift locally before pushing, install the bundled pre-commit hook:

```bash
pip install pre-commit
pre-commit install
```

After installation, the hook runs `cortex skills rebuild-index` on every
commit that touches a `SKILL.md` file. If the resulting index differs from
what was staged, the commit is blocked with a message telling you to
re-stage `skills/skill-index.json`.

## CI enforcement

`.github/workflows/skill-index.yml` runs the same command on every pull
request that touches a `SKILL.md` file or the skill-index itself. A PR with
a stale index fails this job, blocking merge until the contributor regenerates
locally and pushes the updated `skill-index.json`.

## Troubleshooting

**"skill-index: warning: empty keywords: <name>"** on rebuild — the skill's
SKILL.md has no `keywords` in its front matter yet. Add at least 3 keywords
that a user's prompt would plausibly contain. See
`docs/devel/reports/skill-keywords-needing-review.md` for the current gap list.

**"error building skill index: duplicate skill name"** — two `SKILL.md`
files declare the same `name` in their front matter. Check the two paths
the error mentions and rename one.

**"error: malformed YAML front matter"** — the `---`-delimited block at the
top of a `SKILL.md` failed YAML parsing. The error message names the file;
check for mis-indented lists, unquoted colons in strings, or missing closing
`---`.
