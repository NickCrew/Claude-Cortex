---
layout: default
title: Documentation Commands
parent: Guides
nav_order: 10
---

# Documentation Commands

Cortex supports documentation work through two current surfaces:

1. the `cortex docs` CLI for browsing documentation
2. documentation skills for generation, maintenance, validation, and diagrams

## Documentation Viewer

Browse bundled documentation from the CLI.

### CLI

```bash
# List all documentation
cortex docs list

# Show the docs tree
cortex docs tree

# Search docs
cortex docs search recommendation

# View a specific page
cortex docs view architecture/MASTER_ARCHITECTURE

# Open the interactive docs browser
cortex docs tui
```

The CLI viewer is the reliable reference surface because it maps directly to the
current `cortex docs` command group.

## Documentation Skills

When you want Cortex to help produce or maintain docs inside Claude Code, use
the backing skills directly or their generated slash-command aliases.

### Common skills

| Skill / Command | Purpose |
|:----------------|:--------|
| `documentation-production` / `/ctx:documentation-production` | Generate or organize project documentation |
| `doc-maintenance` / `/ctx:doc-maintenance` | Audit and remediate stale docs |
| `doc-claim-validator` / `/ctx:doc-claim-validator` | Verify doc claims against the codebase |
| `reference-documentation` / `/ctx:reference-documentation` | Produce reference-oriented documentation |
| `mermaid-diagramming` / generated command alias | Create Mermaid diagrams for docs |

## Mermaid Diagrams

Generate diagrams using the `mermaid-diagramming` skill or the
`documentation-production` workflow.

### Supported Diagram Types

| Type | Use Case |
|:-----|:---------|
| `flowchart` | Process flows, decisions, branching |
| `sequence` | System interactions over time |
| `erd` | Entity relationships and data models |
| `class` | Object structure and inheritance |
| `state` | State machines and transitions |
| `gantt` | Project timelines |
| `pie` | Proportions and distributions |

Use Mermaid when a flow, sequence, state machine, or data relationship is hard
to understand in prose alone.

## Related Skills

| Skill | Purpose |
|:------|:--------|
| `documentation-production` | Full documentation workflow (generate, index, diagrams, tutorials) |
| `reference-documentation` | Technical references and API specs |
| `tutorial-design` | Hands-on tutorials with exercises |
| `doc-maintenance` | Audit and fix stale documentation |
| `mermaid-diagramming` | Diagram creation across all Mermaid types |
| `doc-claim-validator` | Verify documentation claims against code |

## Documentation Structure

Cortex follows a convention for organizing docs:

```
docs/
├── architecture/     # System design, ADRs, diagrams
├── development/      # Developer guides, setup
├── guides/           # How-to guides
├── reference/        # CLI reference, config docs
├── tutorials/        # Learning paths
└── archive/          # Deprecated docs
```

If you need to inspect the current docs root in the CLI, use:

```bash
cortex docs path
```
