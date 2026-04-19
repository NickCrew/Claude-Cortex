# Skill and Agent Index Maintenance

Two generated artifacts serve as single sources of truth for the suggestion
hooks and CLI tooling:

- `skills/skill-index.json` — consumed by `cortex hooks skill-suggest`,
  `SkillRecommender`, and `cortex skills analyze`. Built from every
  `SKILL.md` file's front matter.
- `agents/agent-index.json` — consumed by `cortex hooks agent-suggest`.
  Built from every `agents/*.md` file's front matter.

Both are committed to the repo; the wheel ships both. Users never regenerate
either. This doc is for contributors editing a skill or an agent.

## When you need to regenerate

**Skill index** — any front-matter change in a `SKILL.md`: adding/renaming
a skill, editing `keywords`, `file_patterns`, `confidence`, `description`,
or moving the skill directory.

**Agent index** — any front-matter change in `agents/<name>.md`:
adding/renaming an agent, editing `activation.keywords`, `tier.conditions`,
`delegate_when`, `description`, or `alias`.

Body-only edits (markdown content after the second `---` block) do not
require regeneration.

## How to regenerate

```bash
cortex skills rebuild-index      # after editing any SKILL.md
cortex agent rebuild-index       # after editing any agents/*.md

git add skills/skill-index.json agents/agent-index.json
```

Output is deterministic — running either command twice with no intervening
front-matter edits produces identical bytes.

## Pre-commit hook (optional)

The bundled pre-commit config covers both indexes:

```bash
pip install pre-commit
pre-commit install
```

After installation, every commit touching a `SKILL.md` file triggers the
skill-index check, and every commit touching an `agents/*.md` file triggers
the agent-index check. If the resulting index differs from what was staged,
the commit is blocked with a message telling you to re-stage.

## CI enforcement

Two workflows enforce the same drift checks on every pull request:

- `.github/workflows/skill-index.yml`
- `.github/workflows/agent-index.yml`

Each runs only when its relevant paths are touched. A PR with a stale index
fails the job, blocking merge until the contributor regenerates and pushes.

## Troubleshooting

**"skill-index: warning: empty keywords: <name>"** on rebuild — the skill's
`SKILL.md` has no `keywords` in its front matter yet. Add at least 3
keywords that a user's prompt would plausibly contain.

**"agent-index: warning: empty keywords: <name>"** — the agent's
`activation.keywords` is empty. Same fix.

**"error building {skill,agent} index: duplicate name"** — two files declare
the same `name` in their front matter. The error message names both paths;
rename one.

**"error: invalid delegate_when values in <name>"** — an agent's
`delegate_when:` has a value outside the allowed set (`isolation`,
`independence`, `parallel`, `large_scope`). See
`rules/specialist-consultation.md` for what each signal means.

**"error: malformed YAML front matter"** — the `---`-delimited block at
the top of the file failed YAML parsing. The error message names the file;
check for mis-indented lists, unquoted colons in strings, or missing
closing `---`.
