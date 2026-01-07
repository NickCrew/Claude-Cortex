# Prompt Library

This directory contains reusable prompts, guidelines, and templates that can be selectively loaded into your Claude context.

## Directory Structure

```
prompts/
├── guidelines/     # Checklists, standards, best practices
├── templates/      # Document templates, formats
└── personas/       # Behavioral profiles and mindsets
```

## Usage

### CLI

```bash
# List available prompts
cortex prompts list

# Activate a prompt
cortex prompts activate guidelines/code-review-checklist

# Show active prompts
cortex prompts status

# Deactivate a prompt
cortex prompts deactivate guidelines/code-review-checklist
```

### TUI

1. Launch: `cortex tui`
2. Navigate to the "Prompts" tab
3. Use Space/Enter to toggle activation
4. Press `e` to edit a prompt in your $EDITOR

## Creating New Prompts

1. Create a `.md` file in the appropriate subdirectory
2. Add YAML front matter with metadata:

```yaml
---
name: My Prompt Name
description: Brief description of what this prompt does
tokens: 200
---
```

3. Add your prompt content below the front matter
4. Activate with `cortex prompts activate category/filename`

## When to Use

**Use prompts for:**
- Guidelines you don't need in every session
- Long reference material that consumes significant context
- Task-specific checklists and templates
- Specialized personas for particular work types

**Don't use prompts for:**
- Always-needed context (use CLAUDE.md core files)
- Simple commands (use slash commands)
- Frequently-used short instructions (use modes/rules)

## Included Examples

| Prompt | Category | Description |
|--------|----------|-------------|
| `code-review-checklist` | guidelines | Comprehensive PR review checklist |
| `pr-description` | templates | Pull request description template |
| `security-auditor` | personas | Security-focused review mindset |

See the [Prompt Library Guide](../docs/guides/prompt-library.md) for full documentation.
