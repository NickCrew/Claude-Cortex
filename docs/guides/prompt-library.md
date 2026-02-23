---
layout: default
title: Prompt Library
nav_order: 9
---

# Prompt Library

Prompt snippets are reusable markdown files you can keep under `~/.claude/prompts/` (or project-local `.claude/prompts/`) and reference from your context files when needed.

## Use cases

- coding/review checklists
- PR / ADR / incident templates
- team conventions and style notes
- domain-specific reference snippets

## Directory structure

```text
~/.claude/prompts/
├── guidelines/
├── templates/
├── personas/
└── references/
```

## Prompt file format

Use markdown with optional frontmatter:

```markdown
---
name: Code Review Checklist
description: Security + correctness checks for PR review
tokens: 450
---

# Code Review Checklist

- Validate inputs
- Check error handling
- Confirm test coverage
```

## Slug format

Use `category/name` based on path:

- `~/.claude/prompts/guidelines/code-review.md` -> `guidelines/code-review`
- `~/.claude/prompts/templates/pr-description.md` -> `templates/pr-description`

## Activation model

Prompt snippets are activated by reference in your context files (for example `CLAUDE.md`):

```markdown
# Prompt Library
@prompts/guidelines/code-review.md
@prompts/templates/pr-description.md
```

If your setup uses an `.active-prompts` file, treat it as generated state and avoid manual edits.

## TUI workflow

```bash
cortex tui
```

Use the docs/context management views to inspect current active context and related files.

## Create new prompts

```bash
mkdir -p ~/.claude/prompts/guidelines
cat > ~/.claude/prompts/guidelines/my-guideline.md << 'EOF_PROMPT'
---
name: My Guideline
description: Project-specific coding guideline
tokens: 200
---

# My Guideline

Your content here.
EOF_PROMPT
```

Then add an `@prompts/...` reference in your context file.

## Best practices

- keep prompts focused and composable
- include token estimates in frontmatter
- prefer many small snippets over one very large prompt
- remove inactive references to keep context lean

## Troubleshooting

- Ensure prompt files are `.md` and under a `prompts/` subdirectory.
- Confirm the `@prompts/...` reference path is correct.
- Reload/refresh context in your Claude Code session after edits.
