---
layout: default
title: Skill Authoring Cookbook
parent: Tutorials
nav_order: 4
permalink: /tutorials/skill-authoring-cookbook/
---

# Skill Authoring Cookbook

A practical guide for creating high-quality skills that extend Claude's capabilities with domain-specific expertise.

## What You'll Learn

By the end of this tutorial, you'll be able to:

- Create a well-structured skill from scratch
- Apply the progressive disclosure pattern for token efficiency
- Add quality rubrics for validation
- Use recipes for common skill patterns
- Publish skills that meet quality standards

**Time Estimate:** 30-45 minutes
**Prerequisites:** Basic Markdown, familiarity with `~/.cortex/` structure

---

## Part 1: Skill Structure Overview

### What is a Skill?

A skill is a reusable knowledge module that provides Claude with domain-specific expertise. Skills contain:
- **Core principles** - Essential knowledge always available
- **Implementation patterns** - Practical how-to guidance
- **Anti-patterns** - What to avoid and why
- **Troubleshooting** - Common problems and solutions

### Directory Anatomy

Every skill lives in `~/.cortex/skills/` with this structure:

```
~/.cortex/skills/your-skill-name/
├── SKILL.md              # Required: Main skill definition
├── examples/             # Optional: Code examples
│   ├── basic.py
│   └── advanced.py
├── references/           # Optional: Large reference content
│   └── patterns.md
└── validation/           # Optional: Quality validation
    └── rubric.yaml
```

### SKILL.md Anatomy

The `SKILL.md` file uses YAML frontmatter followed by structured Markdown:

```markdown
---
name: your-skill-name
version: 1.0.0
description: One-line description of what this skill enables
author: Your Name
tags: [category, subcategory, technology]
triggers:
  - "keyword that activates this skill"
  - "another activation phrase"
related_skills:
  - related-skill-name
---

# Your Skill Name

Brief introduction explaining what this skill does.

## Core Principles
[Essential knowledge - always loaded]

## Implementation Patterns
[Practical patterns with examples]

## Anti-Patterns
[What NOT to do]

## Troubleshooting
[Common problems and solutions]

## References
[Links to authoritative sources]
```

### Required Frontmatter Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Kebab-case identifier (must match directory name) |
| `version` | Yes | Semantic version (x.y.z) |
| `description` | Yes | One-line summary (under 100 characters) |
| `tags` | Yes | Categorization for discovery |
| `triggers` | Yes | Keywords that activate this skill |
| `author` | No | Creator attribution |
| `related_skills` | No | Links to complementary skills |

**Checkpoint:** You understand the structure of a skill.

---

## Part 2: Your First Skill

Let's create a minimal skill step by step.

### Step 1: Create the Directory

```bash
mkdir -p ~/.cortex/skills/my-first-skill
```

### Step 2: Create SKILL.md

Create `~/.cortex/skills/my-first-skill/SKILL.md`:

```markdown
---
name: my-first-skill
version: 1.0.0
description: A minimal skill demonstrating the basic structure
author: Your Name
tags: [tutorial, example, getting-started]
triggers:
  - "first skill"
  - "basic skill example"
---

# My First Skill

This skill demonstrates the minimal structure required for a working skill.

## Core Principles

### Principle 1: Keep It Simple

Start with essential knowledge. Add complexity only when needed.

### Principle 2: Be Specific

Vague guidance is useless. Provide concrete, actionable instructions.

### Principle 3: Show, Don't Tell

Examples are worth a thousand words of explanation.

## Implementation Patterns

### Pattern: Basic Usage

When you need to accomplish a task, follow this approach:

1. First, do X
2. Then, do Y
3. Finally, verify with Z

**Example:**

```python
def my_function():
    """A simple implementation."""
    return "Hello from my first skill!"
```

## Anti-Patterns

### Don't: Over-Engineer

**Bad**: Creating complex abstractions for simple problems.

**Why**: Increases cognitive load without proportional benefit.

**Better**: Start simple, refactor when complexity is justified.

## Troubleshooting

### Problem: Skill Not Loading

**Symptom**: The skill doesn't appear in `cortex skills list`.

**Solution**: Verify the directory name matches the `name` field in frontmatter.

## References

- [Claude-ctx Documentation](https://github.com/NickCrew/claude-cortex)
```

### Step 3: Verify Your Skill

```bash
# List all skills
cortex skills list

# Check your skill appears
cortex skills list | grep my-first-skill
```

### Step 4: Test Activation

In a Claude session, try using a trigger phrase:

```
"I need help with my first skill"
```

Claude should recognize the trigger and apply the skill's guidance.

**Checkpoint:** Your skill appears in the skills list and responds to triggers.

---

## Part 3: Progressive Disclosure Pattern

Skills should load information progressively to optimize token usage.

### The Three Tiers

```
┌─────────────────────────────────────────────────────────────┐
│ Tier 1: Core Principles (Always Loaded)                     │
│ - Essential concepts for every use case                     │
│ - Token budget: ~500-1000 tokens                            │
├─────────────────────────────────────────────────────────────┤
│ Tier 2: Implementation Patterns (On Demand)                 │
│ - Practical patterns for common scenarios                   │
│ - Token budget: ~1000-2000 tokens                           │
├─────────────────────────────────────────────────────────────┤
│ Tier 3: Advanced/References (When Needed)                   │
│ - Edge cases, deep dives, comprehensive examples            │
│ - Token budget: Variable (can be large)                     │
└─────────────────────────────────────────────────────────────┘
```

### Tier 1: Core Principles (Dense & Essential)

```markdown
## Core Principles

### The 3 Rules of [Your Domain]

1. **Rule One**: [Single sentence explanation]
2. **Rule Two**: [Single sentence explanation]
3. **Rule Three**: [Single sentence explanation]

### Decision Framework

When facing [situation], ask:
- Is X true? → Do A
- Is Y true? → Do B
- Otherwise → Do C
```

### Tier 2: Implementation Patterns (Actionable)

```markdown
## Implementation Patterns

### Pattern: [Name]

**When to use**: [Specific scenario]

**Structure**:
```language
[Minimal but complete example]
```

**Key points**:
- Point 1
- Point 2
```

### Tier 3: References (External Files)

For extensive content, use the `references/` directory:

```markdown
## Advanced Topics

For comprehensive coverage, see:
- `@references/full-pattern-catalog.md` - All 47 patterns
- `@references/migration-guide.md` - Version upgrade paths
```

### Token Budget Guidelines

| Section | Target Tokens | Purpose |
|---------|---------------|---------|
| Frontmatter | ~100 | Metadata only |
| Core Principles | 500-1000 | Always-available guidance |
| Implementation | 1000-2000 | Common patterns |
| Anti-Patterns | 300-500 | Critical warnings |
| Troubleshooting | 300-500 | Quick fixes |
| **Total Tier 1** | **<1500** | Keep context lean |

**Checkpoint:** You understand how to structure content across tiers.

---

## Part 4: Quality Rubrics

Quality rubrics help ensure skills meet a consistent standard.

### Creating a Rubric

Create `validation/rubric.yaml` in your skill directory:

```yaml
# validation/rubric.yaml
name: my-first-skill
version: 1.0.0

dimensions:
  clarity:
    weight: 0.25
    criteria:
      - name: clear_language
        description: Uses plain language without jargon
        score_guide:
          1: Confusing or overly technical
          3: Mostly clear
          5: Crystal clear throughout

      - name: logical_structure
        description: Information flows logically
        score_guide:
          1: Disorganized
          3: Reasonable structure
          5: Perfect logical flow

  completeness:
    weight: 0.25
    criteria:
      - name: covers_basics
        description: Covers fundamental concepts
        score_guide:
          1: Major gaps
          3: Covers most basics
          5: Thorough foundation

      - name: has_examples
        description: Includes practical examples
        score_guide:
          1: No examples
          3: Some examples
          5: Excellent examples throughout

  accuracy:
    weight: 0.25
    criteria:
      - name: technically_correct
        description: Information is accurate
        score_guide:
          1: Contains errors
          3: Mostly accurate
          5: Verified accuracy

      - name: up_to_date
        description: Reflects current best practices
        score_guide:
          1: Outdated
          3: Mostly current
          5: Cutting-edge current

  usefulness:
    weight: 0.25
    criteria:
      - name: actionable
        description: Provides actionable guidance
        score_guide:
          1: Too abstract to use
          3: Reasonably actionable
          5: Immediately actionable

      - name: solves_problems
        description: Addresses real problems
        score_guide:
          1: Doesn't address real needs
          3: Useful for common cases
          5: Essential tool

passing_threshold: 3.5
```

### The Four Quality Dimensions

| Dimension | Weight | What It Measures |
|-----------|--------|------------------|
| **Clarity** | 25% | Is the skill easy to understand? |
| **Completeness** | 25% | Does it cover the topic adequately? |
| **Accuracy** | 25% | Is the information correct and current? |
| **Usefulness** | 25% | Can it be applied to real problems? |

### Self-Auditing Your Skill

```bash
# If audit script exists
python scripts/audit_skill.py ~/.cortex/skills/my-first-skill
```

**Checkpoint:** You can create a rubric and understand quality dimensions.

---

## Part 5: Recipes

### Recipe 1: Adding Code Examples

**For short examples** (under 30 lines), embed directly:

```markdown
### Pattern: Configuration Loading

```python
import yaml
from pathlib import Path

def load_config(path: str) -> dict:
    """Load configuration from YAML file."""
    with open(Path(path)) as f:
        return yaml.safe_load(f)
```
```

**For longer examples**, use the `examples/` directory:

```
your-skill/
├── SKILL.md
└── examples/
    ├── basic_usage.py
    └── advanced_patterns.py
```

Reference in SKILL.md:

```markdown
For complete examples, see:
- `@examples/basic_usage.py` - Getting started
- `@examples/advanced_patterns.py` - Production patterns
```

### Recipe 2: Anti-Patterns Section

Use this template:

```markdown
## Anti-Patterns

### Don't: [Descriptive Name]

**The Mistake**:
```language
# What people do wrong
[bad code]
```

**Why It's Problematic**:
- Reason 1
- Reason 2

**The Fix**:
```language
# The correct approach
[good code]
```

**Key Difference**: [One sentence explaining the improvement]
```

### Recipe 3: Troubleshooting Guides

Use this template:

```markdown
## Troubleshooting

### Problem: [Symptom User Experiences]

**Symptoms**:
- Observable symptom 1
- Observable symptom 2

**Common Causes**:
1. Cause A
2. Cause B

**Diagnosis**:
```bash
# Command to check the issue
[diagnostic command]
```

**Solutions**:

**For Cause A**:
```bash
[fix command]
```

**For Cause B**:
1. Step 1
2. Step 2

**Prevention**: [How to avoid this in the future]
```

### Recipe 4: Large Reference Content

For content exceeding 500 lines, use `references/`:

```
your-skill/
├── SKILL.md
└── references/
    ├── api-reference.md
    └── pattern-catalog.md
```

Reference in SKILL.md:

```markdown
## References

### API Reference
Complete documentation: `@references/api-reference.md`

### Pattern Catalog
All 47 patterns: `@references/pattern-catalog.md`
```

**Checkpoint:** You can apply recipes for common patterns.

---

## Part 6: Publishing Checklist

### Metadata Checklist

```markdown
- [ ] `name` matches directory name (kebab-case)
- [ ] `version` follows semantic versioning (x.y.z)
- [ ] `description` is under 100 characters
- [ ] `tags` include relevant categories (minimum 2)
- [ ] `triggers` are specific and non-conflicting
```

### Content Quality Checklist

```markdown
- [ ] Core Principles section exists and is under 1500 tokens
- [ ] At least one Implementation Pattern with example
- [ ] At least one Anti-Pattern documented
- [ ] Troubleshooting section addresses common issues
- [ ] All code examples are tested and runnable
- [ ] No TODO comments or placeholder content
```

### Quality Gate

Run the quality audit:

```bash
python scripts/audit_skill.py ~/.cortex/skills/your-skill
```

**Required**:
- Overall score >= 3.5/5.0
- No dimension below 3.0/5.0

### Final Review

```markdown
## Pre-Publish Verification

### Structure
- [ ] SKILL.md exists at root
- [ ] Directory name matches `name` field

### Content
- [ ] Core Principles are concise and essential
- [ ] Patterns are actionable with examples
- [ ] Anti-patterns warn against real mistakes
- [ ] Troubleshooting addresses real problems

### Quality
- [ ] Audit score >= 3.5
- [ ] All examples tested
- [ ] Spelling and grammar checked

### Ready
- [ ] All checklists pass
```

**Checkpoint:** You have a complete publishing checklist.

---

## Summary

You've learned how to:

1. **Structure a skill** with proper directory layout and SKILL.md anatomy
2. **Create your first skill** with minimal but complete content
3. **Apply progressive disclosure** to optimize token usage
4. **Add quality rubrics** for validation
5. **Use recipes** for common patterns
6. **Publish skills** that meet quality standards

## Next Steps

- Browse existing skills in `~/.cortex/skills/` for inspiration
- Create a skill for a domain you know well
- Contribute improvements to existing skills

---

## Quick Reference

### Minimal SKILL.md Template

```markdown
---
name: skill-name
version: 1.0.0
description: One-line description
tags: [tag1, tag2]
triggers:
  - "trigger phrase"
---

# Skill Name

Brief introduction.

## Core Principles

1. **Principle One**: Explanation
2. **Principle Two**: Explanation

## Implementation Patterns

### Pattern: Name

**When to use**: Scenario

```language
example code
```

## Anti-Patterns

### Don't: Bad Practice

Why it's bad and what to do instead.

## Troubleshooting

### Problem: Common Issue

Solution steps.
```

### Directory Structure

```
skill-name/
├── SKILL.md           # Required
├── examples/          # Optional
├── references/        # Optional
└── validation/        # Optional
    └── rubric.yaml
```

### Quality Dimensions

| Dimension | Check |
|-----------|-------|
| Clarity | Plain language, logical flow |
| Completeness | Covers basics, has examples |
| Accuracy | Technically correct, current |
| Usefulness | Actionable, solves problems |
