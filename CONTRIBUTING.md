# Contributing to Claude Cortex

Thank you for your interest in contributing to the Claude Cortex! This document provides guidelines for different types of contributions.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Types of Contributions](#types-of-contributions)
- [Development Workflow](#development-workflow)
- [Contributing Community Skills](#contributing-community-skills)
- [Contributing Core Features](#contributing-core-features)
- [Contributing Documentation](#contributing-documentation)
- [Pull Request Process](#pull-request-process)
- [Style Guidelines](#style-guidelines)
- [Testing Guidelines](#testing-guidelines)
- [Getting Help](#getting-help)

## Code of Conduct

This project adheres to a Code of Conduct that all contributors are expected to follow:

- **Be respectful**: Treat all community members with respect and consideration
- **Be collaborative**: Work together constructively and help others
- **Be professional**: Keep discussions focused on technical merit
- **Be inclusive**: Welcome contributors from all backgrounds and experience levels

Unacceptable behavior includes harassment, discrimination, trolling, or personal attacks. Violations should be reported to project maintainers.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Claude Code CLI (for testing)
- Familiarity with YAML and Markdown

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/claude-ctx-plugin.git
   cd claude-ctx-plugin
   ```

3. Add upstream remote:
   ```bash
   git remote add upstream https://github.com/NickCrew/claude-ctx-plugin.git
   ```

### Install Development Dependencies

```bash
# Install the package in editable mode
python3 -m pip install -e .

# Install development dependencies
python3 -m pip install -r requirements-dev.txt

# Verify installation
claude-ctx --version
```

### Set Up Environment

```bash
# Point the claude-ctx CLI to your local development copy
export CLAUDE_PLUGIN_ROOT="$(pwd)"

# Add to your shell config for persistence
echo 'export CLAUDE_PLUGIN_ROOT="/path/to/your/claude-ctx-plugin"' >> ~/.zshrc
```

## Types of Contributions

We welcome several types of contributions:

### 1. Community Skills
Expert knowledge modules in specific domains. See [Contributing Community Skills](#contributing-community-skills).

### 2. Bug Fixes
Corrections to existing functionality. Include:
- Clear description of the bug
- Steps to reproduce
- Expected vs actual behavior
- Your fix with tests

### 3. Feature Enhancements
Improvements to existing features. Discuss in GitHub Issues first.

### 4. Documentation
Improvements to README, guides, examples, or code comments.

### 5. Tests
Additional test coverage for existing functionality.

### 6. Tooling
Improvements to build process, CLI, or developer experience.

## Development Workflow

### 1. Create a Branch

```bash
# Update your local main branch
git checkout main
git pull upstream main

# Create feature branch
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
# or
git checkout -b skill/your-skill-name
```

Branch naming conventions:
- `feature/` - New features or enhancements
- `fix/` - Bug fixes
- `skill/` - Community skills
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Test additions or improvements

### 2. Make Changes

- Follow the [Style Guidelines](#style-guidelines)
- Write clear commit messages
- Add tests for new functionality
- Update documentation as needed

### 3. Test Your Changes

```bash
# Run validation
claude-ctx skills validate your-skill-name

# Run tests (if available)
python -m pytest tests/

# Test CLI commands
claude-ctx --help
claude-ctx skills list
claude-ctx skills info your-skill-name
```

### 4. Commit Your Changes

Use clear, descriptive commit messages:

```bash
git add .
git commit -m "Add: Brief description of change

Detailed explanation of what changed and why.
Include any breaking changes or migration notes.

Fixes #123"
```

Commit message format:
- `Add:` - New features or files
- `Fix:` - Bug fixes
- `Update:` - Changes to existing features
- `Refactor:` - Code refactoring
- `Docs:` - Documentation changes
- `Test:` - Test additions or changes
- `Chore:` - Maintenance tasks

### 5. Push and Create PR

```bash
# Push to your fork
git push origin feature/your-feature-name

# Create pull request on GitHub
```

## Contributing Community Skills

Community skills are the most common contribution type. See [skills/community/README.md](skills/community/README.md) for comprehensive guidelines.

### Quick Reference

1. **Copy the template**:
   ```bash
   mkdir -p skills/community/your-skill-name
   cp skills/community/.template/SKILL.md skills/community/your-skill-name/SKILL.md
   ```

2. **Write your skill** following the template structure

3. **Update frontmatter**:
   ```yaml
   ---
   name: your-skill-name
   description: Clear description. Use when [trigger].
   author: Your Name <your.email@example.com>
   version: 1.0.0
   license: MIT
   tags: [category1, category2]
   created: 2024-10-17
   updated: 2024-10-17
   ---
   ```

4. **Validate**:
   ```bash
   claude-ctx skills validate your-skill-name
   ```

5. **Add registry entry** in `skills/community/registry.yaml`:
   ```yaml
   your-skill-name:
     author: Your Name
     email: your.email@example.com
     github: yourusername
     version: 1.0.0
     status: active
     license: MIT
     created: 2024-10-17
     updated: 2024-10-17
     downloads: 0
     activations: 0
     rating: 0.0
     tags:
       - category1
       - category2
     related_skills: []
     dependencies: []
   ```

6. **Submit PR** with title: `[Community Skill] Add {skill-name}`

### Skill Quality Checklist

- [ ] Follows template structure
- [ ] Valid YAML frontmatter
- [ ] Clear activation triggers
- [ ] 5-10 "When to Use" scenarios
- [ ] Code examples are working and tested
- [ ] Progressive disclosure structure
- [ ] Best practices summary included
- [ ] No emojis (unless domain-specific)
- [ ] Grammar and spelling checked
- [ ] Token count: 500-8,000 tokens
- [ ] Passes `claude-ctx skills validate`
- [ ] Registry entry added
- [ ] Author contact information complete

## Contributing Core Features

Core features (commands, agents, CLI) require maintainer approval and higher standards.

### Before Starting

1. **Open an issue** describing the feature
2. **Discuss design** with maintainers
3. **Get approval** before implementing
4. **Follow project architecture** patterns

### Core Contribution Requirements

- **Test coverage**: Minimum 80% for new code
- **Documentation**: Update relevant docs
- **Backward compatibility**: No breaking changes without major version bump
- **Performance**: No significant performance regression
- **Security**: Follow security best practices

### Core Code Standards

```python
# Example: Python code standards

"""
Module docstring explaining purpose.
"""

from typing import List, Dict, Optional

def function_name(param: str, optional_param: Optional[int] = None) -> Dict[str, str]:
    """
    Clear docstring explaining what function does.

    Args:
        param: Description of parameter
        optional_param: Description with default

    Returns:
        Description of return value

    Raises:
        ValueError: When this error occurs
    """
    # Implementation with clear comments
    pass
```

## Contributing Documentation

Documentation improvements are always welcome!

### Documentation Types

1. **README updates**: Main project README
2. **Guide improvements**: Skills guide, contribution guide
3. **Code comments**: Inline documentation
4. **Examples**: Usage examples and tutorials
5. **Website docs**: Jekyll documentation site

### Documentation Standards

- **Clear and concise**: Avoid jargon, explain concepts
- **Examples included**: Show, don't just tell
- **Up-to-date**: Match current codebase
- **Well-organized**: Logical structure and flow
- **Accessible**: Appropriate for target audience

### Testing Documentation

```bash
# For website docs
cd docs
bundle install
bundle exec jekyll serve --livereload

# Verify links work
# Check formatting renders correctly
# Test code examples
```

## Pull Request Process

### PR Title Format

Use clear, descriptive titles:

- `[Community Skill] Add {skill-name}`
- `[Feature] Add {feature-description}`
- `[Fix] Resolve {bug-description}`
- `[Docs] Update {documentation-area}`
- `[Refactor] Improve {component-name}`

### PR Description Template

```markdown
## Summary
Brief description of changes

## Type of Change
- [ ] Bug fix (non-breaking change fixing an issue)
- [ ] New feature (non-breaking change adding functionality)
- [ ] Community skill (new skill contribution)
- [ ] Breaking change (fix or feature requiring version bump)
- [ ] Documentation update

## Motivation
Why this change is needed

## Changes Made
- Change 1
- Change 2
- Change 3

## Testing
How changes were tested:
- [ ] Validated with claude-ctx commands
- [ ] Added/updated tests
- [ ] Tested locally
- [ ] Documentation reviewed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Tests added/updated and passing
- [ ] Dependent changes merged

## Related Issues
Fixes #123
Related to #456

## Screenshots (if applicable)
```

### Review Process

1. **Automated checks**: CI runs validation and tests
2. **Maintainer review**: Code quality, design, tests
3. **Community feedback**: For significant changes
4. **Approval required**: At least one maintainer approval
5. **Merge**: Squash and merge to main

### Review Timeline

- **Community skills**: 3-7 days
- **Bug fixes**: 1-3 days
- **Features**: 5-14 days
- **Documentation**: 1-3 days

## Style Guidelines

### YAML

```yaml
# Use 2-space indentation
# Quote strings when necessary
# Consistent key ordering

name: skill-name
description: Clear description with proper grammar.
tags:
  - lowercase-hyphenated
  - consistent-naming
```

### Markdown

```markdown
# Use ATX-style headers (# not underlines)
# One blank line between sections
# Code blocks with language specifiers
# Consistent list formatting (- for unordered, 1. for ordered)

## Section Header

Paragraph with **bold** and *italic* formatting.

- List item 1
- List item 2
  - Nested item

```language
// Code block with language
```
```

### File Naming

- **Hyphen-case**: `your-skill-name/` not `Your_Skill_Name/`
- **Descriptive**: Clear purpose from name
- **Consistent**: Follow existing patterns
- **No special chars**: Alphanumeric and hyphens only

### Code Comments

```python
# Good: Explains WHY
# Cache result to avoid expensive computation on repeated calls
result = expensive_function()

# Bad: Explains WHAT (code already shows this)
# Set x to 5
x = 5
```

## Testing Guidelines

### Skill Validation

```bash
# Validate single skill
claude-ctx skills validate your-skill-name

# Validate all skills
claude-ctx skills validate --all

# Check token count
claude-ctx skills info your-skill-name --show-tokens
```

### Manual Testing

Test your changes with real Claude Code usage:

1. Install your changes locally
2. Test relevant CLI commands
3. Verify skill activation
4. Check error handling
5. Test edge cases

### Test Documentation

Document how to test your changes in PR description:

```markdown
## Testing Steps

1. Install package: `pip install -e .`
2. Run command: `claude-ctx skills info your-skill-name`
3. Verify output matches expected result
4. Test error case: `claude-ctx skills info nonexistent`
5. Confirm error message is clear
```

## Getting Help

### Resources

- **Documentation**: [Project docs](https://nickcrew.github.io/claude-ctx-plugin/)
- **Skills guide**: [skills/README.md](skills/README.md)
- **Community guide**: [skills/community/README.md](skills/community/README.md)
- **Template**: [skills/community/.template/SKILL.md](skills/community/.template/SKILL.md)

### Support Channels

- **Questions**: [GitHub Discussions](https://github.com/NickCrew/claude-ctx-plugin/discussions)
- **Bug reports**: [GitHub Issues](https://github.com/NickCrew/claude-ctx-plugin/issues)
- **Feature requests**: [GitHub Issues](https://github.com/NickCrew/claude-ctx-plugin/issues) with `enhancement` label
- **PR help**: Comment on your pull request

### Tips for New Contributors

1. **Start small**: Begin with documentation or small bug fixes
2. **Ask questions**: Use Discussions for clarification
3. **Review existing PRs**: Learn from approved contributions
4. **Be patient**: Reviews take time, especially for complex changes
5. **Iterate**: Expect feedback and be ready to make changes

## Recognition

Contributors are recognized in several ways:

- **Credited in files**: Author attribution in contributed skills
- **Registry entry**: Community skills registry
- **Contributors list**: GitHub contributors page
- **Release notes**: Significant contributions mentioned

Thank you for contributing to Claude Cortex!

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (see LICENSE file).

## Questions?

If you have questions not covered here:

1. Check existing [documentation](https://nickcrew.github.io/claude-ctx-plugin/)
2. Search [GitHub Issues](https://github.com/NickCrew/claude-ctx-plugin/issues)
3. Ask in [GitHub Discussions](https://github.com/NickCrew/claude-ctx-plugin/discussions)
4. Open a new issue with the `question` label

We're here to help make your contribution successful!
