---
layout: default
title: Commands
parent: Reference
nav_order: 1
---

# Command Reference

In the current Cortex model, slash commands are not best understood as a
separate hand-curated product surface. They are primarily generated or derived
from the skill library.

## How Commands Work

Two implementation details matter:

1. `cortex install link` generates `~/.claude/commands/` aliases from
   `skills/`
2. command metadata is discovered from `SKILL.md` files, with the command either
   derived from the skill path or overridden by frontmatter

That means the most accurate source of truth for a command is usually the skill
that backs it.

## Practical Mental Model

Think of it this way:

- **skills** are the canonical reusable workflows
- **slash commands** are one invocation surface for those skills
- the installed `commands/` directory is generated from the skill set rather
  than maintained as an entirely separate authored catalog

## Common Patterns

### Default namespace

Flat skills typically map into a `ctx` namespace:

```text
skills/systematic-debugging/SKILL.md -> /ctx:systematic-debugging
```

### Nested namespaces

Nested skills can map into their own namespace:

```text
skills/collaboration/writing-plans/SKILL.md -> /collaboration:writing-plans
```

### Explicit override

A skill can also define an explicit command in frontmatter:

```yaml
command: /ctx:systematic-debugging
```

## What To Read Instead Of Treating This As A Static Catalog

- [Skills](../guides/skills.md) for the actual skill system
- [Configuration Reference](configuration.md) for install and layout context
- [Installation](../getting-started/installation.md) for `cortex install link`

## Notes

- Avoid relying on older fixed command counts in `site/`.
- If command behavior seems unclear, inspect the backing skill first.
- If the generated aliases differ from older docs, trust the installed skill
  surface and current CLI behavior rather than the legacy command-count copy.
