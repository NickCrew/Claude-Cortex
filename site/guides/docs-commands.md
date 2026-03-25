---
layout: default
title: Documentation Commands
parent: Guides
nav_order: 10
---

# Documentation Commands

Browse bundled documentation from the CLI using the `cortex docs` command group.

## CLI

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

# Show the docs root path
cortex docs path
```

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

## Related

- [Documentation Health Audit]({% link guides/doc-health-audit.md %}) --- audit pipeline for assessing doc quality
- [Skills Guide]({% link guides/skills.md %}) --- documentation-related skills are listed in the skills system
