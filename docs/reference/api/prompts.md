# Prompts Module API Reference

**Module:** `claude_ctx_py.core.prompts`

The prompts module provides functions for managing reusable prompt templates in the cortex framework. Prompts are organized in subdirectories under `~/.cortex/prompts/`.

## Overview

Prompts use a category/name slug format for organization:
- `prompts/guidelines/code-review.md` → slug: `guidelines/code-review`
- `prompts/templates/pr-description.md` → slug: `templates/pr-description`
- `prompts/personas/senior-dev.md` → slug: `personas/senior-dev`

## Data Classes

### PromptInfo

Metadata about a prompt definition.

```python
@dataclass
class PromptInfo:
    name: str          # Display name (from frontmatter or filename)
    slug: str          # category/filename-stem format
    description: str   # Prompt description
    category: str      # Parent directory name
    tokens: int        # Estimated token count
    path: Path         # Absolute path to prompt file
    status: str        # "active" or "inactive"
```

**Example:**
```python
PromptInfo(
    name="Code Review Guidelines",
    slug="guidelines/code-review",
    description="Standards for reviewing pull requests",
    category="guidelines",
    tokens=450,
    path=Path("~/.cortex/prompts/guidelines/code-review.md"),
    status="active"
)
```

## Functions

### discover_prompts

```python
def discover_prompts(home: Path | None = None) -> List[PromptInfo]
```

Discover all prompts from `~/.cortex/prompts/` directory.

**Parameters:**
- `home` (Path, optional): Override home directory for testing

**Returns:**
- `List[PromptInfo]`: All discovered prompts with status set

**Behavior:**
- Scans subdirectories recursively for `.md` files
- Parses YAML frontmatter for metadata
- Sets status based on `.active-prompts` file
- Ignores `README.md` and hidden files

**Example:**
```python
prompts = discover_prompts()
for p in prompts:
    print(f"{p.slug}: {p.status}")
# guidelines/code-review: active
# templates/pr-description: inactive
```

---

### prompt_activate

```python
def prompt_activate(slug: str, home: Path | None = None) -> Tuple[int, str]
```

Activate a prompt by adding it to `.active-prompts`.

**Parameters:**
- `slug` (str): Prompt slug in `category/name` format
- `home` (Path, optional): Override home directory

**Returns:**
- `Tuple[int, str]`: (exit_code, message)
  - `(0, "Activated...")` on success
  - `(1, "Error...")` on failure

**Behavior:**
- Verifies prompt file exists at `prompts/{slug}.md`
- Adds slug to `.active-prompts` file
- Refreshes CLAUDE.md references
- Returns error if already active

**Example:**
```python
code, msg = prompt_activate("guidelines/code-review")
print(msg)  # "Activated prompt: guidelines/code-review"
```

---

### prompt_deactivate

```python
def prompt_deactivate(slug: str, home: Path | None = None) -> Tuple[int, str]
```

Deactivate a prompt by removing it from `.active-prompts`.

**Parameters:**
- `slug` (str): Prompt slug in `category/name` format
- `home` (Path, optional): Override home directory

**Returns:**
- `Tuple[int, str]`: (exit_code, message)

**Behavior:**
- Removes slug from `.active-prompts` file
- Refreshes CLAUDE.md references
- Returns error if not currently active

**Example:**
```python
code, msg = prompt_deactivate("guidelines/code-review")
print(msg)  # "Deactivated prompt: guidelines/code-review"
```

---

### list_prompts

```python
def list_prompts(home: Path | None = None) -> str
```

List all prompts with their status.

**Parameters:**
- `home` (Path, optional): Override home directory

**Returns:**
- `str`: Formatted string with prompts grouped by category

**Example Output:**
```
Available prompts:

  guidelines:
    guidelines/code-review (active) ~450t
    guidelines/commit-messages (inactive)

  templates:
    templates/pr-description (inactive) ~200t
```

---

### prompt_status

```python
def prompt_status(home: Path | None = None) -> str
```

Show currently active prompts.

**Parameters:**
- `home` (Path, optional): Override home directory

**Returns:**
- `str`: Formatted string with active prompt slugs

**Example Output:**
```
Active prompts:
  guidelines/code-review
  personas/senior-dev
```

---

### get_prompt_by_slug

```python
def get_prompt_by_slug(slug: str, home: Path | None = None) -> Optional[PromptInfo]
```

Get a specific prompt by its slug.

**Parameters:**
- `slug` (str): Prompt slug in `category/name` format
- `home` (Path, optional): Override home directory

**Returns:**
- `PromptInfo` if found, `None` otherwise

**Example:**
```python
prompt = get_prompt_by_slug("guidelines/code-review")
if prompt:
    print(f"Found: {prompt.name} ({prompt.tokens} tokens)")
```

## Prompt File Format

Prompts are Markdown files with YAML frontmatter:

```markdown
---
name: Code Review Guidelines
description: Standards for reviewing pull requests
tokens: 450
---

# Code Review Guidelines

[Prompt content here...]
```

### Frontmatter Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | No | Display name (defaults to filename) |
| `description` | No | Brief description |
| `tokens` | No | Estimated token count |

## File Locations

| File | Purpose |
|------|---------|
| `~/.cortex/prompts/` | Root directory for all prompts |
| `~/.cortex/prompts/{category}/` | Category subdirectories |
| `~/.cortex/.active-prompts` | List of active prompt slugs |

## CLI Integration

```bash
# List all prompts
cortex prompts list

# Activate a prompt
cortex prompts activate guidelines/code-review

# Deactivate a prompt
cortex prompts deactivate guidelines/code-review

# Show active prompts
cortex prompts status
```

## See Also

- [Skill Authoring Cookbook](/tutorials/skill-authoring-cookbook/) - Similar pattern for skills
- [Core Base Module](/reference/api/base/) - Shared utility functions
