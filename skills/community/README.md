# Community Contributed Skills

Welcome to the community skills directory! This is where developers can contribute specialized knowledge and patterns to the Cortex ecosystem.

## What are Community Skills?

Community skills are specialized knowledge modules contributed by the developer community that extend Claude's capabilities in specific domains. Unlike the core skills maintained by the project team, community skills are:

- **Community-maintained**: Created and updated by community members
- **Peer-reviewed**: Reviewed by other community members before acceptance
- **Opt-in**: Users choose which community skills to enable
- **Experimental**: May be promoted to core skills based on usage and quality

## Quick Start: Contributing a Skill

1. **Fork the repository** and create a new branch
2. **Copy the template**: `cp skills/community/.template/SKILL.md skills/community/your-skill-name/SKILL.md`
3. **Write your skill** following the template structure
4. **Test locally**: `cortex skills validate your-skill-name`
5. **Add registry entry**: Update `skills/community/registry.yaml`
6. **Submit pull request** with your skill and registry entry

See [CONTRIBUTING.md](../../CONTRIBUTING.md) for detailed guidelines.

## Directory Structure

```
skills/community/
├── README.md                      # This file
├── .template/
│   └── SKILL.md                   # Template for new skills
├── registry.yaml                  # Community skill registry
└── your-skill-name/               # Your contributed skill
    └── SKILL.md                   # Skill content
```

## Skill Quality Standards

All community skills must meet these minimum standards:

### Required Elements

- [ ] **Valid YAML frontmatter** with name, description, author, version
- [ ] **Clear activation triggers** in description
- [ ] **"When to Use This Skill" section** with 5-10 specific scenarios
- [ ] **Progressive disclosure structure** (essential → detailed → advanced)
- [ ] **Practical code examples** with annotations
- [ ] **Best practices summary**
- [ ] **Author contact information** for maintenance

### Content Quality

- [ ] **Accurate information**: All patterns and examples must be correct
- [ ] **Current best practices**: Reflects industry standards (not outdated approaches)
- [ ] **Clear writing**: Well-organized, grammatically correct, professional tone
- [ ] **Proper attribution**: Credits sources, references official documentation
- [ ] **No promotional content**: Objective, educational focus (no product marketing)

### Technical Standards

- [ ] **Token budget**: 500-8,000 tokens (split if larger)
- [ ] **Validated**: Passes `cortex skills validate`
- [ ] **No emojis**: Unless explicitly part of domain (e.g., commit message conventions)
- [ ] **Consistent formatting**: Follows template structure
- [ ] **Working examples**: All code examples are syntactically correct

## Contribution Process

### 1. Skill Idea Validation

Before creating a skill, check:

- **Does it already exist?** Search existing core and community skills
- **Is it too broad?** Split large skills into focused modules
- **Is it too narrow?** Consider if it warrants a standalone skill
- **Is it evergreen?** Avoid framework-specific skills tied to single versions

### 2. Skill Development

Use the template structure:

```yaml
---
name: your-skill-name
description: Brief description. Use when [clear trigger condition].
author: Your Name <your.email@example.com>
version: 1.0.0
license: MIT
tags: [category1, category2, category3]
---
```

Follow the progressive disclosure pattern:

1. **Overview** (1-2 paragraphs)
2. **When to Use** (bulleted list)
3. **Core Patterns** (essential → detailed → advanced)
4. **Examples** (practical, annotated code)
5. **Best Practices Summary**
6. **Resources** (official docs, references)

### 3. Testing and Validation

```bash
# Validate skill structure
cortex skills validate your-skill-name

# Test skill loading
cortex skills info your-skill-name

# Check token count
cortex skills info your-skill-name --show-tokens
```

### 4. Registry Entry

Add your skill to `registry.yaml`:

```yaml
your-skill-name:
  author: Your Name
  email: your.email@example.com
  github: yourusername
  version: 1.0.0
  status: active
  created: 2024-10-17
  updated: 2024-10-17
  downloads: 0
  tags:
    - category1
    - category2
  related_skills:
    - related-skill-1
    - related-skill-2
```

### 5. Pull Request Submission

**PR Title Format**: `[Community Skill] Add {skill-name}`

**PR Description Template**:

```markdown
## Skill Information
- **Name**: your-skill-name
- **Category**: [e.g., frontend, backend, security, devops]
- **Token Count**: ~X,XXX tokens
- **Related Skills**: skill1, skill2

## What does this skill provide?
[Brief explanation of the skill's purpose and value]

## When should this skill activate?
[List 3-5 specific trigger scenarios]

## Testing Checklist
- [ ] Validated with `cortex skills validate`
- [ ] Token count within budget (500-8,000)
- [ ] All code examples tested and working
- [ ] No emojis or promotional content
- [ ] Author information complete
- [ ] Registry entry added
```

### 6. Review Process

Your PR will be reviewed for:

1. **Technical accuracy**: Patterns and examples are correct
2. **Quality standards**: Meets all required elements
3. **Writing quality**: Clear, professional, well-organized
4. **Community value**: Fills a gap, useful to multiple users
5. **Maintenance commitment**: Author commits to maintaining skill

Reviews typically take 3-7 days. Reviewers may request changes.

## Skill Categories

Organize skills by primary domain:

### Architecture & Design

- System architecture patterns
- API design approaches
- Database design patterns
- Design principles and methodologies

### Development

- Language-specific patterns
- Framework best practices
- Testing strategies
- Performance optimization

### Infrastructure

- Deployment patterns
- Container orchestration
- Infrastructure as Code
- CI/CD workflows

### Security

- Security patterns
- Threat modeling
- Secure coding practices
- Compliance frameworks

### DevOps

- Monitoring and observability
- Incident response
- SRE practices
- Automation patterns

### Domain-Specific

- Industry-specific patterns (fintech, healthcare, etc.)
- Specialized technologies
- Emerging paradigms

## Maintenance and Ownership

### Author Responsibilities

As a skill author, you commit to:

1. **Respond to issues**: Within 2 weeks for bug reports
2. **Keep content current**: Update for major ecosystem changes
3. **Review contributions**: Evaluate PRs that improve your skill
4. **Deprecation notice**: Provide 90 days notice if abandoning skill

### Skill Lifecycle

**Active**: Maintained, recommended for use
**Maintenance**: Minimal updates, stable
**Deprecated**: Superseded by newer skill, 90-day sunset period
**Archived**: No longer maintained, removed from registry

### Community Maintenance

If original author becomes inactive:

1. Open issue requesting adoption
2. Wait 30 days for author response
3. Community member can request adoption
4. Maintainers approve adoption and transfer ownership

## Recognition and Attribution

### Contributor Recognition

- **Authors credited** in skill frontmatter and registry
- **Contributor badge** on GitHub profile (if available)
- **Usage metrics** shown in registry (downloads, activations)
- **Featured skills** highlighted in documentation

### Promotion to Core

Skills may be promoted to core if they:

- Receive high usage (>100 unique users)
- Maintain high quality (>4.5/5 rating)
- Fill critical gap in core skills
- Author agrees to core maintenance standards

Promoted skills remain credited to original author.

## Getting Help

### Resources

- **Template**: `skills/community/.template/SKILL.md`
- **Examples**: See core skills in `skills/*/SKILL.md`
- **Validation**: `cortex skills validate --help`
- **Documentation**: [Project docs](https://nickcrew.github.io/cortex-plugin/)

### Support Channels

- **Questions**: Open discussion in GitHub Discussions
- **Bug reports**: GitHub Issues with `community-skill` label
- **Feature requests**: GitHub Issues with `enhancement` label
- **Pull request help**: Comment on your PR

### Community Guidelines

1. **Be respectful**: Constructive feedback only
2. **Be patient**: Reviewers are volunteers
3. **Be collaborative**: Help others improve their skills
4. **Be professional**: No promotional content or spam

## FAQ

### Q: Can I contribute a skill for a specific framework version?

A: Yes, but ensure the skill name reflects versioning (e.g., `vue3-composition-patterns` not `vue-patterns`). Consider if framework-agnostic patterns would be more valuable.

### Q: What if my skill overlaps with an existing skill?

A: Evaluate if yours provides unique value. Consider contributing improvements to existing skill instead of creating duplicate.

### Q: Can I contribute multiple related skills?

A: Yes! Consider skill composition - one skill can reference others. See `skills/composition.yaml` for examples.

### Q: How do I update my skill after it's merged?

A: Submit a new PR with changes, increment version number, and update the `updated` field in registry.

### Q: Can I transfer my skill to another maintainer?

A: Yes. Submit PR updating author information in both skill frontmatter and registry. Both parties should comment approving transfer.

### Q: What license should I use?

A: We recommend MIT license for maximum compatibility. You can choose any OSI-approved license.

### Q: Can organizations contribute skills?

A: Yes! Use organization name as author and provide designated contact person.

## Example Skills

See these community skills for reference:

### Well-Structured Examples (from core)

- **api-design-patterns**: Comprehensive coverage, clear examples
- **async-python-patterns**: Focused scope, progressive disclosure
- **kubernetes-security-policies**: Practical examples, best practices

### Template Variations

**Minimal Skill** (500-1,500 tokens):

- Single focused topic
- Quick reference format
- Essential patterns only

**Standard Skill** (1,500-3,000 tokens):

- Multiple related patterns
- Detailed examples
- Best practices included

**Comprehensive Skill** (3,000-8,000 tokens):

- Complex domain coverage
- Advanced patterns
- Multiple tiers of disclosure

## Version History

- **1.0.0** (2024-10-17): Initial community skills framework
  - Template created
  - Registry established
  - Contribution guidelines defined

## Contributors

Community skills are made possible by developers like you. Thank you to all contributors!

See `registry.yaml` for complete author list.
