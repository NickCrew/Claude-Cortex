---
layout: default
title: Documentation Commands
parent: Guides
nav_order: 10
---

# Documentation Commands

Cortex provides commands and tools for generating, indexing, and viewing documentation within Claude Code.

## /docs:generate

Generate focused documentation for components, APIs, or features.

```bash
/docs:generate [target] [--type inline|external|api|guide] [--style brief|detailed]
```

### Documentation Types

| Type | Output |
|:-----|:-------|
| `inline` | JSDoc/docstring comments added directly to code |
| `external` | Separate documentation files |
| `api` | API reference with endpoints, schemas, and examples |
| `guide` | User-facing guides with practical examples |

### Examples

```bash
# Add inline documentation to a module
/docs:generate src/auth/login.js --type inline

# Generate API reference
/docs:generate src/api --type api --style detailed

# Create a user guide
/docs:generate payment-module --type guide --style brief

# Document a component library
/docs:generate components/ --type external
```

The command analyzes the target code, identifies public interfaces, and generates documentation matching the requested type and style.

## /docs:index

Build a project documentation index or knowledge base.

```bash
/docs:index [target] [--type docs|api|structure|readme] [--format md|json|yaml]
```

### Index Types

| Type | Output |
|:-----|:-------|
| `docs` | General documentation knowledge base |
| `api` | API documentation structure |
| `structure` | Project structure with cross-references |
| `readme` | README and overview documentation |

### Examples

```bash
# Generate a project structure doc
/docs:index project-root --type structure --format md

# Build an API documentation index
/docs:index src/api --type api --format json

# Create a documentation knowledge base
/docs:index . --type docs
```

The index command performs multi-pass analysis: first scanning the codebase structure, then cross-referencing components, and finally validating completeness.

## Documentation Viewer

Browse bundled documentation from the CLI or TUI.

### CLI

```bash
# List all documentation
cortex docs

# View a specific page
cortex docs architecture/MASTER_ARCHITECTURE

# Search by filename
cortex docs MASTER_ARCHITECTURE
```

### TUI

Press `d` in the TUI to open the documentation viewer, or use the Command Palette (`Ctrl+P`) and search for "Docs".

**Navigation:**

| Key | Action |
|:----|:-------|
| Arrow keys / `j`/`k` | Navigate tree (left pane) or scroll content (right pane) |
| `Enter` | Expand/collapse directory or select file |
| `PageUp` / `PageDown` | Scroll content |
| `Esc` or `q` | Close viewer |

The viewer renders markdown with syntax highlighting, tables, and formatted lists.

## Mermaid Diagrams

Generate diagrams using the `mermaid-diagramming` skill or the documentation-production skill's diagrams reference.

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

### Examples

```bash
# User flow diagram
/docs:diagrams "User login flow with MFA and lockout" --type flowchart

# API interaction sequence
/docs:diagrams "Checkout API interaction" --type sequence

# Data model
/docs:diagrams "Customer, Order, Invoice schema" --type erd
```

Each diagram is generated in both basic and styled variants with accessibility notes and rendering guidance.

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

The `/docs:index` command can scaffold this structure for a new project.
