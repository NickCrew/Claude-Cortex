# Reference Documentation Guide

This directory contains reference documentation that Claude loads as needed during skill execution. Unlike the main SKILL.md which loads immediately, reference files are loaded on-demand to optimize context usage.

## Directory Structure

```
references/
├── README.md              # This file - navigation and usage guide
├── detailed-patterns.md   # Extended pattern documentation (when created)
├── api-reference.md       # API specifications (when applicable)
├── troubleshooting.md     # Common issues and solutions (when created)
└── glossary.md            # Domain-specific terminology (when created)
```

## When to Use References

Reference files should be loaded when:

1. **Deep Dive Required**: User needs detailed information beyond core principles
2. **Troubleshooting**: User encounters issues requiring diagnostic guidance
3. **Integration**: User is integrating with external systems or services
4. **Advanced Scenarios**: User's use case exceeds basic pattern coverage

## Reference File Guidelines

### File Organization

Each reference file should follow this structure:

```markdown
# Reference: [Topic Name]

## Overview
Brief description of what this reference covers and when to use it.

## Quick Reference
Most commonly needed information in table or list format.

## Detailed Content
Comprehensive coverage of the topic.

## Related References
Links to other relevant reference files.
```

### Content Principles

1. **Searchable**: Use clear headings and keywords for grep-based discovery
2. **Modular**: Each file covers one topic comprehensively
3. **Progressive**: Order content from common to rare use cases
4. **Practical**: Include working examples and code snippets
5. **Current**: Keep information up-to-date with latest versions

### Size Guidelines

| File Type | Target Size | Max Size |
|-----------|-------------|----------|
| Quick reference | ~500 words | 1000 words |
| Detailed guide | ~2000 words | 5000 words |
| Comprehensive reference | ~5000 words | 10000 words |

For files exceeding 10000 words, split into multiple files with clear navigation.

## Search Patterns

When looking for information in reference files, use these grep patterns:

```bash
# Find pattern documentation
grep -r "Pattern:" references/

# Find code examples
grep -r "```" references/

# Find troubleshooting entries
grep -r "Issue:" references/
grep -r "Problem:" references/

# Find API information
grep -r "Endpoint:" references/
grep -r "Method:" references/
```

## Creating New References

When adding a new reference file:

1. **Identify the need**: What information gap does this address?
2. **Check for overlap**: Could this be added to an existing file?
3. **Name clearly**: Use descriptive, lowercase-with-hyphens names
4. **Add to index**: Update this README with the new file
5. **Link appropriately**: Add cross-references from SKILL.md if needed

### Reference Template

```markdown
# Reference: [Topic Name]

## Overview

[1-2 sentences describing what this reference covers]

## Quick Reference

| Item | Description | Example |
|------|-------------|---------|
| [Key item] | [Brief description] | [Example value] |

## [Main Section 1]

### [Subsection]

[Detailed content with examples]

```language
// Code example
example_code()
```

## [Main Section 2]

[Additional content]

## Related References

- `reference-name.md` - [How it relates]
- `another-reference.md` - [How it relates]

## Changelog

- YYYY-MM-DD: Initial creation
- YYYY-MM-DD: [Update description]
```

## Loading Strategy

Claude uses these strategies to determine when to load references:

### Automatic Loading Triggers

- User mentions topic covered by a reference file
- Current pattern requires additional context
- Troubleshooting mode is activated
- Integration with external system is detected

### Manual Loading Requests

Users can request reference loading explicitly:
- "Show me the detailed patterns"
- "I need the API reference"
- "What does [term] mean?"

### Conditional Loading

References load based on context:
- Error messages trigger troubleshooting.md
- API questions trigger api-reference.md
- Unfamiliar terms trigger glossary.md

## Best Practices for Reference Usage

### For Skill Authors

1. **Keep SKILL.md lean**: Move detailed content to references
2. **Use progressive disclosure**: Core concepts in SKILL.md, details in references
3. **Avoid duplication**: Information lives in ONE place
4. **Maintain consistency**: Use consistent formatting across references
5. **Update together**: When updating SKILL.md, check if references need updates

### For Users

1. **Start with SKILL.md**: Core concepts first
2. **Request specifics**: Ask for detailed patterns when needed
3. **Search first**: Use keywords to find relevant references
4. **Report gaps**: If information is missing, suggest additions

## Maintenance

### Regular Review

- [ ] Check for outdated information (quarterly)
- [ ] Verify code examples still work (monthly)
- [ ] Update external links (quarterly)
- [ ] Review and incorporate user feedback (ongoing)

### Version Alignment

References should be versioned with the main skill:
- Major version: Structural changes to references
- Minor version: Content additions or updates
- Patch version: Typo fixes and minor corrections

## Index of Available References

<!-- Update this section as references are added -->

| File | Description | Last Updated |
|------|-------------|--------------|
| README.md | This navigation guide | YYYY-MM-DD |
| (Add new references here) | | |

---

*Reference documentation follows the progressive disclosure pattern from the cortex cookbook.*
