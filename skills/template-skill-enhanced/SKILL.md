---
name: template-skill-enhanced
description: "Enhanced skill template with progressive disclosure, bundled resources, and quality rubrics. Use when creating new skills that need structured tiers, reference files, validation rubrics, or advanced bundling patterns beyond the basic template."
version: 1.0.0
license: MIT
tags: [skill-creation, template, progressive-disclosure, bundling]
---

# Enhanced Skill Template

A production-ready skill template demonstrating progressive disclosure, bundled resource patterns, and quality validation. Use this template when creating skills that require tiered content loading, reference file organization, or structured quality scoring.

## When to Use This Skill

- Creating a new skill that needs **progressive disclosure** (tiered content loading)
- Building skills with **bundled resources** (references, examples, validation rubrics)
- Designing skills that exceed basic template complexity
- Setting up skills with **quality targets** and scoring rubrics
- Avoid using for simple, single-purpose skills — use `template-skill` instead

## Workflow

### Step 1: Set Up Frontmatter

Define metadata with kebab-case name, quoted description including a "Use when" clause, version, and tags:

```yaml
---
name: my-new-skill
description: "Clear description of what this skill does. Use when [specific trigger condition]."
version: 1.0.0
tags: [domain, category]
---
```

### Step 2: Write Core Principles (Tier 1 — Always Loaded)

The first section loads immediately on activation. Keep it under ~1000 tokens:

```markdown
## Core Principles

### Principle 1: Foundation Concept
Explanation with a concise code example:

\`\`\`python
# Demonstrate the concept clearly
def foundation_example(input_data):
    validated = validate(input_data)
    return transform(validated)
\`\`\`

**Key Points:**
- Critical aspect that must be understood
- Common misconception to avoid
```

### Step 3: Add Implementation Patterns (Tier 2 — Loaded When Needed)

Detailed patterns for common scenarios (~1500 tokens):

```markdown
### Pattern: Descriptive Name

**Problem**: What specific problem this solves
**Solution**: High-level approach

\`\`\`python
def pattern_implementation(input_data):
    validate(input_data)
    result = transform(input_data)
    return format_output(result)
\`\`\`

**Trade-offs**:
| Aspect | Benefit | Cost |
|--------|---------|------|
| Performance | Fast execution | Higher memory |
| Maintainability | Clear structure | More boilerplate |
```

### Step 4: Add Advanced Usage (Tier 3 — Complex Scenarios)

Reserve for sophisticated implementations (~2000+ tokens). Include edge cases:

| Scenario | Expected Behavior | Handling Strategy |
|----------|-------------------|-------------------|
| Empty input | Graceful failure | Return default or descriptive error |
| Invalid format | Validation error | Clear error message with fix guidance |
| Resource exhaustion | Graceful degradation | Backoff and retry logic |

### Step 5: Organize Bundled Resources

Create sibling directories for heavy content:

```
skills/my-new-skill/
├── SKILL.md                          # Core skill (under token budget)
├── references/
│   ├── README.md                     # Guide to reference docs
│   └── detailed-patterns.md          # Extended pattern documentation
├── examples/
│   └── basic.md                      # Annotated usage example
└── validation/
    └── rubric.yaml                   # Quality scoring rubric
```

### Step 6: Define Quality Targets

Set measurable quality criteria:

```yaml
quality_targets:
  clarity: ">= 4/5"
  completeness: ">= 4/5"
  accuracy: ">= 5/5"
  usefulness: ">= 4/5"
```

### Step 7: Validate the Skill

```bash
cortex skills validate my-new-skill
cortex skills info my-new-skill --show-tokens
```

Ensure total token count stays within 500–8,000 tokens per CONTRIBUTING guidelines.

## Best Practices

- **Progressive disclosure**: Keep Tier 1 concise — load detail on demand
- **Bundled resources**: Move lengthy examples and deep-dives to `references/` or `examples/`
- **Quality rubrics**: Define scoring criteria in `validation/rubric.yaml` so skill outputs can be evaluated consistently
- **Token budget**: Core SKILL.md should stay under token limits; offload heavy content to sibling files
- **Real examples**: Replace all placeholder content with domain-specific, working code
- **Kebab-case naming**: Directories and skill names use lowercase hyphen-case

## Anti-Patterns

- **Placeholder content in production**: Shipping `[Pattern Name]` or `example_code_here()` — always fill in real content
- **Monolithic skills**: Putting everything in SKILL.md instead of using bundled resources
- **Missing "Use when" clause**: Description must include activation context
- **Ignoring token budgets**: Skills over 8,000 tokens slow activation and may be truncated
