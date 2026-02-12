# Writing Process & Style

Reference for producing clear, well-structured technical documentation tailored to specific audiences.

## Audience Analysis Framework

### Persona Mapping

Identify who will read the documentation before writing a single line.

| Dimension | Questions to Answer |
| --- | --- |
| **Role** | Developer, operator, end-user, decision-maker? |
| **Skill level** | Beginner, intermediate, advanced, mixed? |
| **Goal** | Learn a concept, complete a task, troubleshoot, evaluate? |
| **Context** | First-time visitor, returning user, migrating from competitor? |
| **Environment** | IDE, terminal, browser, mobile? |

### Skill Level Assessment

- **Beginner**: Needs every step spelled out, definitions for domain terms, screenshots or examples at each stage
- **Intermediate**: Familiar with basics, needs task-specific guidance, appreciates shortcuts and tips
- **Advanced**: Wants reference-style content, edge cases, configuration options, and API surface details
- **Mixed audience**: Use progressive disclosure -- lead with essentials, layer depth in expandable sections or linked pages

### Goal Identification Checklist

- [ ] What task does the reader need to complete?
- [ ] What do they already know?
- [ ] What information is blocking them?
- [ ] What is their next step after reading?

## Documentation Types and Structures

### API Documentation

```
# Resource Name
One-line description of what this endpoint/module does.

## Authentication
Required credentials or tokens.

## Endpoints / Methods
### METHOD /path
- Description
- Parameters (table: name, type, required, description)
- Request example
- Response example (success + error)
- Error codes

## Rate Limits
## Changelog
```

### User Guide

```
# Guide Title
Brief description and who this is for.

## Prerequisites
What the reader needs before starting.

## Steps
### Step 1: [Action verb] [Object]
Explanation, then command or action, then verification.

### Step 2: ...

## Next Steps
Where to go after completing this guide.

## Troubleshooting
Common issues and resolutions.
```

### Tutorial

```
# Tutorial: [What you'll build/learn]
Outcome statement and time estimate.

## What You'll Learn
Bulleted list of skills or concepts.

## Prerequisites
## Setup
## Part 1: [First concept]
  Explanation → Example → Practice
## Part 2: [Building on Part 1]
  ...
## Summary
## Exercises
## Further Reading
```

### Changelog

```
# Changelog

## [version] - YYYY-MM-DD
### Added
### Changed
### Fixed
### Removed
### Deprecated
```

### Troubleshooting Guide

```
# Troubleshooting: [System/Feature]

## Symptom: [What the user sees]
**Cause**: Why this happens.
**Fix**: Step-by-step resolution.
**Verify**: How to confirm the fix worked.
```

## Style Patterns

### Active Voice

| Passive (avoid) | Active (prefer) |
| --- | --- |
| "The file is created by the command" | "The command creates the file" |
| "Configuration can be done in..." | "Configure this in..." |
| "It is recommended that..." | "We recommend..." or just state the instruction |

### Scanning-Friendly Structure

- Lead with the most important information (inverted pyramid)
- Use descriptive headings that tell the reader what they will get
- Keep paragraphs to 3-5 sentences maximum
- Use bullet lists for sets of items, numbered lists for sequences
- Bold key terms on first use
- Use tables for structured comparisons
- Add code blocks for anything the reader will type or reference

### Progressive Disclosure

1. **Surface layer**: One-sentence summary of what and why
2. **Action layer**: Steps to complete the task
3. **Detail layer**: Options, edge cases, background context
4. **Reference layer**: Full API surface, configuration matrix, related topics

### Terminology Consistency

- Pick one term per concept and use it everywhere
- Define abbreviations on first use
- Maintain a glossary for projects with heavy domain vocabulary
- Never alternate between synonyms for the same thing

## Editing Checklists

### Accuracy

- [ ] All commands and code samples tested and working
- [ ] Version numbers and paths match the current release
- [ ] Links resolve to valid destinations
- [ ] Screenshots match the current UI
- [ ] Error messages and outputs are accurate

### Clarity

- [ ] Every sentence has a clear subject and verb
- [ ] No jargon used without definition
- [ ] Instructions are unambiguous (one way to interpret each step)
- [ ] Pronouns have obvious antecedents
- [ ] No assumptions about reader knowledge beyond stated prerequisites

### Completeness

- [ ] Prerequisites listed before procedures
- [ ] Every step includes a verification method
- [ ] Error cases and edge cases documented
- [ ] Next steps or related topics linked
- [ ] All placeholders replaced with real values or clearly marked

### Accessibility

- [ ] Headings follow a logical hierarchy (no skipped levels)
- [ ] Images have alt text describing their content
- [ ] Color is not the sole way to convey meaning
- [ ] Code blocks are labeled with the language
- [ ] Tables have header rows
- [ ] Links use descriptive text (not "click here")

## Documentation Lifecycle

### 1. Drafting

- Identify audience, type, and scope
- Gather source material (code, specs, interviews, existing docs)
- Outline structure using the appropriate template
- Write first draft focusing on completeness over polish

### 2. Review

- Self-edit using the checklists above
- Technical review: subject-matter expert verifies accuracy
- Editorial review: check voice, structure, and readability
- Usability review: can someone follow the steps cold?

### 3. Publish

- Place in the correct location within the docs hierarchy
- Update indexes, navigation, and cross-references
- Add metadata (title, description, last-updated date)
- Verify rendering in the target format (site, PDF, IDE)

### 4. Maintain

- Set a review cadence (quarterly or per-release)
- Monitor for broken links and outdated references
- Track reader feedback and support tickets referencing docs
- Archive or redirect deprecated content rather than deleting

## Template Patterns

### Prerequisite Block

```markdown
## Prerequisites

Before you begin, make sure you have:
- [Tool] version [X.Y] or later ([installation guide](link))
- [Access/credential] for [service]
- Familiarity with [concept] ([primer](link) if needed)
```

### Step With Verification

```markdown
### Step N: [Action verb] [Object]

[Brief explanation of what this does and why.]

\`\`\`sh
command --flag value
\`\`\`

Verify it worked:

\`\`\`sh
check-command
\`\`\`

Expected output:
\`\`\`
success indicator
\`\`\`
```

### Admonition Patterns

```markdown
> **Note**: Supplementary information that helps but isn't required.

> **Tip**: Shortcut or best practice the reader may not know.

> **Warning**: Action that could cause data loss or downtime.

> **Important**: Critical information the reader must not skip.
```

### Decision Table

```markdown
| If you need... | Use... | See... |
| --- | --- | --- |
| Quick start | Getting Started guide | [link] |
| Full API surface | API Reference | [link] |
| Migration help | Migration Guide | [link] |
```
