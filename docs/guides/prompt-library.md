---
layout: default
title: Prompt Library
nav_order: 9
---

# Prompt Library

The Prompt Library is a feature for managing reusable prompts, guidelines, and templates that can be selectively injected into your Claude context. Unlike always-loaded context (like CLAUDE.md core files), prompt library items are activated on-demand when you need them.

## Use Cases

- **Guideline documents** - Code review checklists, style guides, architectural principles
- **Long prompts** - Detailed instructions that would consume significant context if always loaded
- **Templates** - PR descriptions, commit message formats, documentation templates
- **Personas** - Specialized behavioral modes for different tasks
- **Reference material** - API documentation, project-specific conventions

## Directory Structure

Prompts are organized in subdirectories under `~/.cortex/prompts/`:

```
~/.cortex/prompts/
├── guidelines/
│   ├── code-review.md
│   ├── security-checklist.md
│   └── api-design.md
├── templates/
│   ├── pr-description.md
│   ├── adr-template.md
│   └── bug-report.md
└── personas/
    ├── senior-architect.md
    ├── security-auditor.md
    └── documentation-writer.md
```

## Prompt File Format

Each prompt is a markdown file with optional YAML front matter:

```markdown
---
name: Code Review Checklist
description: Comprehensive code review guidelines for PR reviews
tokens: 450
---

# Code Review Checklist

## Security
- [ ] No hardcoded credentials or secrets
- [ ] Input validation on all user data
- [ ] SQL injection prevention
...
```

### Front Matter Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | No | Display name (defaults to filename in title case) |
| `description` | No | Brief description of the prompt's purpose |
| `tokens` | No | Estimated token count for context budgeting |

## Slug Format

Prompts use a `category/name` slug format based on their directory structure:

- `~/.cortex/prompts/guidelines/code-review.md` → `guidelines/code-review`
- `~/.cortex/prompts/templates/pr-description.md` → `templates/pr-description`
- `~/.cortex/prompts/personas/senior-architect.md` → `personas/senior-architect`

## CLI Commands

### List all prompts

```bash
cortex prompts list
```

Shows all available prompts grouped by category with their activation status.

### Show active prompts

```bash
cortex prompts status
```

Displays currently active prompts that are being injected into CLAUDE.md.

### Activate prompts

```bash
# Activate a single prompt
cortex prompts activate guidelines/code-review

# Activate multiple prompts
cortex prompts activate guidelines/code-review templates/pr-description
```

### Deactivate prompts

```bash
# Deactivate a single prompt
cortex prompts deactivate guidelines/code-review

# Deactivate multiple prompts
cortex prompts deactivate guidelines/code-review templates/pr-description
```

## TUI Integration

The Prompt Library is integrated into the cortex TUI as a dedicated view.

### Accessing the Prompts View

1. Launch the TUI: `cortex tui`
2. Navigate to the "Prompts" tab using number keys or arrow navigation

### TUI Controls

| Key | Action |
|-----|--------|
| `↑/↓` or `j/k` | Navigate prompts |
| `Space` or `Enter` | Toggle activation |
| `e` | Edit prompt in external editor ($EDITOR) |
| `r` | Refresh prompt list |

### Columns Displayed

- **Name** - Display name from front matter or filename
- **Category** - Parent directory (guidelines, templates, etc.)
- **Tokens** - Estimated token count
- **Status** - Active/Inactive indicator
- **Description** - Brief description

## CLAUDE.md Integration

Active prompts are automatically injected into CLAUDE.md using `@prompts/` references:

```markdown
# Prompt Library
@prompts/guidelines/code-review.md
@prompts/templates/pr-description.md
```

When a prompt is activated:
1. Its slug is added to `~/.cortex/.active-prompts`
2. CLAUDE.md is regenerated with the new `@prompts/` reference
3. Claude Code loads the prompt content on next context refresh

## Wizard Integration

The CLAUDE.md Wizard includes a dedicated step for selecting prompts:

1. Run the wizard: `cortex init --interactive`
2. Step 3 presents all available prompts grouped by category
3. Use arrow keys and Space to toggle selection
4. Continue to review and apply your selections

## Creating New Prompts

### 1. Create the directory structure

```bash
mkdir -p ~/.cortex/prompts/guidelines
mkdir -p ~/.cortex/prompts/templates
mkdir -p ~/.cortex/prompts/personas
```

### 2. Create a prompt file

```bash
cat > ~/.cortex/prompts/guidelines/my-guideline.md << 'EOF'
---
name: My Custom Guideline
description: Project-specific coding guidelines
tokens: 200
---

# My Custom Guideline

Your guideline content here...
EOF
```

### 3. Activate the prompt

```bash
cortex prompts activate guidelines/my-guideline
```

## Best Practices

### Token Budgeting

- Include `tokens` in front matter to help with context budgeting
- Keep prompts focused - split large documents into multiple files
- Deactivate prompts when not needed to preserve context space

### Organization

- Use meaningful category names (guidelines, templates, personas, references)
- Keep related prompts in the same category
- Use descriptive filenames (kebab-case recommended)

### Content Guidelines

- Start with a clear heading (`# Title`)
- Include actionable instructions or reference material
- Use markdown formatting for readability
- Keep content focused on a single purpose

## Activation Persistence

The `.active-prompts` file in `~/.cortex/` persists your prompt selections across sessions:

```
guidelines/code-review
templates/pr-description
personas/senior-architect
```

This file is managed automatically by the CLI and TUI - avoid editing it directly.

## Comparison with Other Features

| Feature | Purpose | Persistence | Context Impact |
|---------|---------|-------------|----------------|
| **Prompts** | On-demand guidelines/templates | Session-based activation | Variable (user-controlled) |
| **Modes** | Behavioral modifications | File-based activation | Always loaded when active |
| **Skills** | Slash command capabilities | Always available | Loaded on invocation |
| **Agents** | Specialized task handling | File-based activation | Always loaded when active |

## Troubleshooting

### Prompt not appearing in list

- Verify the file exists in `~/.cortex/prompts/` subdirectory
- Check file has `.md` extension
- Ensure file is not named `README.md` (excluded by convention)

### Prompt content not loading

- Check CLAUDE.md contains the `@prompts/` reference
- Run `cortex prompts status` to verify activation
- Try deactivating and reactivating the prompt

### Token count showing 0

- Add `tokens:` field to front matter
- Manually estimate tokens (~4 chars per token)
