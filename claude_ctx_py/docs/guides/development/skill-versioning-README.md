---
layout: default
title: Skill Versioning System
nav_order: 6
---

# Skill Versioning System

Complete guide to semantic versioning for skills, enabling evolution without breaking changes.

## Overview

The skill versioning system implements **semantic versioning (semver)** to manage skill evolution over time. This allows skills to be updated, improved, and fixed while maintaining backward compatibility and providing clear upgrade paths.

**Key Benefits:**
- Evolve skills without breaking dependent agents
- Support multiple skill versions simultaneously
- Clear compatibility contracts and upgrade paths
- Rollback capability for problematic updates
- Community skill version management

---

## Semantic Versioning Format

Skills use semantic versioning: `MAJOR.MINOR.PATCH`

```
1.2.3
│ │ │
│ │ └─ PATCH: Bug fixes, typos, minor improvements
│ └─── MINOR: New features, enhancements (backward compatible)
└───── MAJOR: Breaking changes, interface modifications
```

### Version Increment Rules

**MAJOR (X.0.0) - Breaking Changes:**
- Fundamental changes to skill behavior
- Removal of patterns or sections
- Interface changes that affect agents
- Restructured content organization
- Changed activation triggers

**MINOR (x.X.0) - Enhancements:**
- New patterns or techniques added
- Additional examples or use cases
- Expanded explanations
- New best practices sections
- Additional resources

**PATCH (x.x.X) - Fixes:**
- Typo corrections
- Code example bug fixes
- Clarifications without new content
- Link updates
- Formatting improvements

### Examples

```yaml
# Initial release
api-design-patterns: "1.0.0"

# Added GraphQL patterns (new feature)
api-design-patterns: "1.1.0"

# Fixed REST example code bug
api-design-patterns: "1.1.1"

# Restructured versioning section (breaking)
api-design-patterns: "2.0.0"
```

---

## Version Specification Syntax

### Exact Version

```yaml
skills:
  - api-design-patterns@1.2.3
```

Loads exactly version 1.2.3. Fails if version doesn't exist.

### Caret (^) - Compatible Updates

```yaml
skills:
  - api-design-patterns@^1.2.0
```

**Allows:** `>=1.2.0` and `<2.0.0`
**Use when:** You want bug fixes and new features, but no breaking changes
**Example matches:** 1.2.0, 1.2.5, 1.3.0, 1.9.9
**Example rejects:** 2.0.0, 0.9.0

### Tilde (~) - Patch Updates Only

```yaml
skills:
  - api-design-patterns@~1.2.0
```

**Allows:** `>=1.2.0` and `<1.3.0`
**Use when:** You want only bug fixes, no new features
**Example matches:** 1.2.0, 1.2.1, 1.2.9
**Example rejects:** 1.3.0, 2.0.0

### Minimum Version (>=)

```yaml
skills:
  - api-design-patterns@>=1.2.0
```

**Allows:** Any version `>=1.2.0`
**Use when:** You need at least a specific version
**Example matches:** 1.2.0, 1.3.0, 2.0.0, 10.0.0
**Example rejects:** 1.1.9, 1.0.0

### Latest

```yaml
skills:
  - api-design-patterns@latest
  # or simply
  - api-design-patterns
```

**Allows:** Always uses the most recent version
**Use when:** You always want the newest version
**Warning:** May introduce breaking changes unexpectedly

---

## Version Storage Structure

### Directory Layout

```
skills/
├── api-design-patterns@1.0.0/
│   └── SKILL.md
├── api-design-patterns@1.1.0/
│   └── SKILL.md
├── api-design-patterns@2.0.0/
│   └── SKILL.md
└── versions.yaml              # Version registry
```

### versions.yaml Format

```yaml
skills:
  api-design-patterns:
    current: "2.0.0"           # Latest stable version
    versions:                  # All available versions
      - "2.0.0"
      - "1.1.0"
      - "1.0.0"
    compatibility:
      "2.0.0":
        release_date: "2025-10-20"
        notes: "Restructured versioning section with new patterns"
        changes:
          - "Added versioning by URL path examples"
          - "Removed deprecated query parameter versioning"
          - "Updated pagination best practices"
        breaking_changes:
          - "Removed query parameter versioning section"
          - "Changed field filtering syntax examples"
      "1.1.0":
        release_date: "2025-10-15"
        notes: "Added GraphQL patterns"
        changes:
          - "GraphQL schema design patterns"
          - "Query optimization techniques"
          - "Mutation best practices"
      "1.0.0":
        release_date: "2025-10-10"
        notes: "Initial versioned release"
        changes:
          - "REST API design patterns"
          - "Error handling conventions"
          - "Pagination strategies"
```

---

## CLI Commands

### Show Available Versions

```bash
# Show all versions for a skill
cortex skills versions api-design-patterns

# Output:
# api-design-patterns versions:
#   2.0.0 (current) - 2025-10-20
#   1.1.0           - 2025-10-15
#   1.0.0           - 2025-10-10
```

### Validate Version Specification

```bash
# Validate a version requirement
cortex skills validate api-design-patterns@^1.2.0

# Output:
# ✓ Version specification is valid
# ✓ Compatible versions: 1.2.0, 1.2.1, 1.3.0
```

### Check Compatibility

```bash
# Check if a version requirement can be satisfied
cortex skills info api-design-patterns@^1.0.0

# Output:
# Skill: api-design-patterns@^1.0.0
# Resolved to: 1.1.0
# Compatible with: 1.0.0, 1.1.0
# Note: Version 2.0.0 has breaking changes
```

### List Version History

```bash
# Show detailed version history
cortex skills versions api-design-patterns --detailed

# Output:
# api-design-patterns version history:
#
# 2.0.0 (2025-10-20) [BREAKING]
#   - Added versioning by URL path examples
#   - Removed deprecated query parameter versioning
#   - Changed field filtering syntax examples
#
# 1.1.0 (2025-10-15)
#   - GraphQL schema design patterns
#   - Query optimization techniques
#
# 1.0.0 (2025-10-10) [INITIAL]
#   - REST API design patterns
#   - Error handling conventions
```

---

## Agent Integration

### Specify Version in Agent Frontmatter

```yaml
---
name: backend-architect
skills:
  # Exact version
  - api-design-patterns@1.2.3

  # Compatible updates (recommended)
  - microservices-patterns@^1.0.0

  # Patch updates only (conservative)
  - event-driven-architecture@~1.1.0

  # Minimum version
  - database-design-patterns@>=1.0.0

  # Latest (use with caution)
  - kubernetes-deployment-patterns@latest
---
```

### Default Behavior (No Version Specified)

```yaml
skills:
  - api-design-patterns  # Equivalent to @latest
```

**Recommendation:** Always specify version constraints in production agents.

### Version Resolution at Runtime

```
Agent requests: api-design-patterns@^1.2.0

Available versions: 1.0.0, 1.2.0, 1.2.5, 1.3.0, 2.0.0

Resolution process:
1. Parse requirement: ^1.2.0 = >=1.2.0 and <2.0.0
2. Filter compatible: 1.2.0, 1.2.5, 1.3.0
3. Select latest compatible: 1.3.0
4. Load: skills/api-design-patterns@1.3.0/SKILL.md
```

---

## Creating Versioned Skills

### Initial Release (1.0.0)

```bash
# Create skill directory with version
mkdir -p skills/my-skill@1.0.0
cd skills/my-skill@1.0.0

# Create SKILL.md
cat > SKILL.md << 'EOF'
---
name: my-skill
version: "1.0.0"
description: Initial skill description. Use when [trigger].
---

# My Skill

Initial content...
EOF

# Register in versions.yaml
# (See versions.yaml format above)
```

### Adding a New Version

```bash
# 1. Create new version directory
mkdir -p skills/my-skill@1.1.0

# 2. Copy previous version
cp skills/my-skill@1.0.0/SKILL.md skills/my-skill@1.1.0/SKILL.md

# 3. Update version in frontmatter
# Edit skills/my-skill@1.1.0/SKILL.md:
# version: "1.1.0"

# 4. Make your changes (new patterns, examples, etc.)

# 5. Update versions.yaml
# Add new version and compatibility info
```

### Version Update Workflow

```bash
# 1. Determine version increment
# - Breaking change? → MAJOR
# - New feature?     → MINOR
# - Bug fix?         → PATCH

# 2. Create new version directory
NEW_VERSION="1.2.0"
SKILL_NAME="api-design-patterns"
mkdir -p "skills/${SKILL_NAME}@${NEW_VERSION}"

# 3. Copy and update
cp "skills/${SKILL_NAME}@1.1.0/SKILL.md" \
   "skills/${SKILL_NAME}@${NEW_VERSION}/SKILL.md"

# 4. Edit new version
# Update version in frontmatter
# Make content changes
# Document changes in comments

# 5. Update versions.yaml
# Add to versions list
# Update current version
# Add compatibility entry

# 6. Validate
cortex skills validate "${SKILL_NAME}@${NEW_VERSION}"

# 7. Test
cortex skills info "${SKILL_NAME}@${NEW_VERSION}"
```

---

## Backward Compatibility

### Maintaining Compatibility

**DO (Minor/Patch):**
- Add new sections
- Add new examples
- Expand existing explanations
- Add new patterns alongside existing ones
- Fix errors in examples
- Update external links

**DON'T (Would require MAJOR):**
- Remove sections or patterns
- Rename core concepts
- Change fundamental structure
- Remove examples
- Change activation triggers
- Modify skill interface

### Deprecation Strategy

When planning breaking changes:

```markdown
## Pattern X (DEPRECATED)

> **Deprecation Notice:** This pattern is deprecated as of v1.5.0
> and will be removed in v2.0.0. Use Pattern Y instead.

[Old pattern documentation for backward compatibility]

## Pattern Y (RECOMMENDED)

[New pattern documentation]
```

---

## Upgrade Management

### Agent Upgrade Path

```yaml
# Current state
skills:
  - api-design-patterns@^1.0.0  # Using 1.2.5

# New major version 2.0.0 released
# Agent continues using 1.x until manually upgraded

# Upgrade to 2.x
skills:
  - api-design-patterns@^2.0.0

# Or conservative upgrade
skills:
  - api-design-patterns@~2.0.0  # Only 2.0.x patches
```

### Testing Version Compatibility

```bash
# Test with specific version
cortex skills info api-design-patterns@2.0.0

# Test version resolution
cortex skills info api-design-patterns@^1.0.0

# Validate agent with version constraints
cortex agent validate backend-architect
```

### Migration Guides

When releasing breaking changes (MAJOR version), include migration guide:

```markdown
# MIGRATION GUIDE: v1.x → v2.0.0

## Breaking Changes

### 1. Query Parameter Versioning Removed

**Before (v1.x):**
```
GET /api/users?version=1
```

**After (v2.0.0):**
```
GET /api/v1/users
```

**Migration:**
Update your API routes to use URL path versioning.

### 2. Field Filtering Syntax Changed

**Before (v1.x):**
```
GET /api/users?fields=id,name,email
```

**After (v2.0.0):**
```
GET /api/users?select=id,name,email
```

**Migration:**
Replace `fields` parameter with `select`.
```

---

## Version Metrics and Analytics

### Track Version Usage

```bash
# Show which versions are actively used
cortex skills analytics --metric versions

# Output:
# Version Usage Statistics:
#
# api-design-patterns:
#   2.0.0: 15 agents (75%)
#   1.2.5: 4 agents (20%)
#   1.0.0: 1 agent (5%)
```

### Deprecation Impact Analysis

```bash
# Check impact before deprecating
cortex skills deps api-design-patterns@1.0.0

# Output:
# Skills depending on api-design-patterns@1.0.0:
#   - backend-architect-legacy
#   - api-gateway-service (pinned)
#
# ⚠ Warning: 2 agents would be affected by deprecation
```

---

## Community Skills Versioning

### Installing Versioned Community Skills

```bash
# Install specific version
cortex skills community install pdf-generation@1.2.0

# Install with version constraint
cortex skills community install pdf-generation@^1.0.0

# Install latest
cortex skills community install pdf-generation
```

### Publishing Versioned Skills

```yaml
# skills/my-skill@1.0.0/SKILL.md
---
name: my-skill
version: "1.0.0"
author: username
repository: https://github.com/username/my-skill
description: Skill description. Use when [trigger].
tags:
  - api
  - rest
  - design
---
```

### Version Compatibility in Community

```bash
# Check compatibility before installing
cortex skills community validate pdf-generation@^1.2.0

# Output:
# ✓ Version 1.3.5 satisfies constraint ^1.2.0
# ✓ Compatible with your system
# ✓ No conflicting dependencies
```

---

## Best Practices

### For Skill Authors

1. **Start with 1.0.0**
   - Don't use 0.x.x for released skills
   - 1.0.0 indicates stable, production-ready

2. **Document Breaking Changes**
   - Always include migration guides for MAJOR versions
   - Deprecate before removing (give users time to migrate)

3. **Version Metadata**
   - Keep versions.yaml up to date
   - Document all changes in compatibility section

4. **Semantic Versioning Discipline**
   - Be conservative with MAJOR bumps
   - Use MINOR for backward-compatible additions
   - Use PATCH for fixes only

5. **Test Version Compatibility**
   - Validate new versions before release
   - Test upgrade paths from previous versions

### For Skill Users (Agents)

1. **Specify Version Constraints**
   - Don't rely on @latest in production
   - Use caret (^) for flexibility with safety
   - Use tilde (~) for maximum stability

2. **Review Breaking Changes**
   - Check release notes before upgrading MAJOR versions
   - Test agents after version upgrades

3. **Pin Critical Skills**
   - Use exact versions for mission-critical agents
   - Example: `api-design-patterns@1.2.3`

4. **Upgrade Regularly**
   - Stay within supported version ranges
   - Plan upgrades for MAJOR version changes

---

## Troubleshooting

### Version Not Found

```bash
# Error: Version 1.5.0 not found
cortex skills info api-design-patterns@1.5.0

# Solution: Check available versions
cortex skills versions api-design-patterns
```

### Incompatible Version

```bash
# Error: No compatible version found for ^2.0.0
cortex skills info api-design-patterns@^2.0.0

# Solution: Check available versions
# Latest version might be 1.x.x
cortex skills versions api-design-patterns
```

### Version Conflicts

```yaml
# Agent A requires: api-design-patterns@^1.0.0
# Agent B requires: api-design-patterns@^2.0.0

# Solution: Can't activate both simultaneously
# Either:
# 1. Upgrade Agent A to support 2.x
# 2. Keep agents in separate contexts
```

---

## Implementation Details

### Version Resolution Algorithm

```python
def resolve_version(skill_name: str, version_req: str) -> str:
    """
    Resolve a version requirement to specific version.

    1. Parse version requirement
    2. Get all available versions
    3. Filter by compatibility
    4. Return latest compatible version
    """
    if version_req == "latest":
        return get_latest_version(skill_name)

    available = get_skill_versions(skill_name)
    compatible = [v for v in available if check_compatibility(version_req, v)]

    if not compatible:
        raise VersionNotFoundError(
            f"No compatible version for {skill_name}@{version_req}"
        )

    return max(compatible, key=parse_version)
```

### Version Comparison

```python
def check_compatibility(required: str, available: str) -> bool:
    """Check if available version satisfies requirement."""

    # Exact match
    if not required.startswith(("^", "~", ">=")):
        return required == available

    # Caret: ^1.2.0 = >=1.2.0 and <2.0.0
    if required.startswith("^"):
        req = parse_version(required[1:])
        avail = parse_version(available)
        return (
            avail.major == req.major and
            (avail.minor, avail.patch) >= (req.minor, req.patch)
        )

    # Tilde: ~1.2.0 = >=1.2.0 and <1.3.0
    if required.startswith("~"):
        req = parse_version(required[1:])
        avail = parse_version(available)
        return (
            (avail.major, avail.minor) == (req.major, req.minor) and
            avail.patch >= req.patch
        )

    # Minimum: >=1.2.0
    if required.startswith(">="):
        req = parse_version(required[2:])
        avail = parse_version(available)
        return avail >= req
```

---

## Examples

### Example 1: Creating a New Skill Version

```bash
# Current version: api-design-patterns@1.2.0
# Adding GraphQL patterns (new feature = MINOR)

# 1. Create new version directory
mkdir -p skills/api-design-patterns@1.3.0

# 2. Copy previous version
cp skills/api-design-patterns@1.2.0/SKILL.md \
   skills/api-design-patterns@1.3.0/SKILL.md

# 3. Update version
# Edit SKILL.md frontmatter: version: "1.3.0"

# 4. Add GraphQL section
# Edit SKILL.md: Add new GraphQL patterns section

# 5. Update versions.yaml
# Add 1.3.0 to versions list and compatibility info

# 6. Validate
cortex skills validate api-design-patterns@1.3.0
```

### Example 2: Upgrading Agent to New Major Version

```yaml
# Before: Using api-design-patterns v1.x
---
name: backend-architect
skills:
  - api-design-patterns@^1.0.0
---

# After: Upgrade to v2.x
---
name: backend-architect
skills:
  - api-design-patterns@^2.0.0  # New major version
---

# Test before committing
# cortex agent validate backend-architect
```

### Example 3: Supporting Multiple Versions

```bash
# Keep both v1 and v2 available
skills/
├── api-design-patterns@1.2.5/
│   └── SKILL.md
└── api-design-patterns@2.0.0/
    └── SKILL.md

# Agents can choose their version
# Legacy agent: @^1.0.0 → uses 1.2.5
# Modern agent: @^2.0.0 → uses 2.0.0
```

---

## See Also

- [Skill Analytics Examples](./skill-analytics-examples.md) - Analytics and metrics
- [Skills Guide](../skills.md) - General skills documentation
- [Semantic Versioning](https://semver.org/) - Official semver specification
