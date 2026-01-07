# Cortex Command Namespaces

This repository ships slash command definitions in `commands/`. Each file maps to a Claude Code
slash command (`/namespace:command`). For plugin discovery, command files are flattened as
`commands/<namespace>-<command>.md`; supporting notes and templates live under `commands/<namespace>/`.

## Namespace Overview (current)

- `/analyze`: `code`, `doctor`, `estimate`, `explain`, `security-scan`, `troubleshoot`
- `/cleanup`: `archive-sprint`, `code-cleanup`, `deps-cleanup`, `docs-cleanup`, `test-cleanup`
- `/collaboration`: `assumption-buster`, `concept-forge`, `idea-lab`, `mashup`, `pre-mortem`
- `/ctx`: `brainstorm`, `plan`, `execute-plan`
- `/deploy`: `prepare-release`
- `/design`: `system`, `ui`, `workflow`
- `/dev`: `build`, `code-review`, `dx`, `git`, `implement`, `test`
- `/docs`: `diagrams`, `generate`, `index`, `teacher`, `tutorials`
- `/orchestrate`: `brainstorm`, `spawn`, `task`
- `/quality`: `cleanup`, `improve`
- `/reasoning`: `adjust`, `budget`, `metrics`
- `/session`: `load`, `reflect`, `save`
- `/test`: `generate-tests`
- `/tools`: `select`

## Visual Mode Commands (no namespace)

- `/supersaiyan` - Base visual excellence mode
- `/kamehameha` - Enhanced visual polish
- `/over9000` - Maximum visual polish

## Using Commands

### Via Claude Code Chat

```
/dev:implement auth flow
```

### Via CLI (if enabled)

```
cortex cmd dev:implement "auth flow"
```

Note: `cortex` is deprecated but remains as a compatible alias for now.

## Command Structure

Each command file includes:

```yaml
---
name: namespace:command
description: What the command does
category: workflow|utility|analysis
personas: [thinking, modes]           # Conceptual guidance
subagents: [general-purpose, ...]     # Task tool delegation targets
mcp-servers: [context7, ...]          # Optional MCP integrations
---

# Command Documentation
...
```

## Execution Architecture

Commands coordinate two types of guidance:

### Personas (Thinking Modes)

Conceptual roles that guide Claude's perspective and decision-making:

- `architect` - System design thinking
- `frontend` - UI/UX focus
- `backend` - API and data modeling
- `security` - Security-first mindset
- `qa-specialist` - Quality standards

*Personas influence how Claude thinks, not what tools are used.*

### Subagents (Workers via Task Tool)

Specialized agents launched via Claude Code's Task tool for complex work.

**When commands delegate** (use Task tool to launch subagents):

- Complex operations (>3 files, >5 steps)
- Multi-domain work (code + tests + docs)
- Parallel workstreams possible
- User needs progress visibility

**When commands use direct tools**:

- Simple operations (1-2 files)
- Quick reads/searches
- Atomic changes

See: `docs/reference/architecture/terminology.md` for complete architecture explanation.

## Best Practices

1. **Clear Naming** - Use descriptive, action-oriented names
2. **Focused Purpose** - Each command does one thing well
3. **Consistent Structure** - Follow the template format
4. **Agent Composition** - Leverage multiple agents when needed
5. **Documentation** - Provide clear usage examples
