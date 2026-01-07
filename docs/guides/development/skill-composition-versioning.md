---
layout: default
title: Skill Composition & Versioning
nav_order: 8
parent: Development
---

# Skill Composition & Versioning

Advanced skill management features for building modular, maintainable knowledge hierarchies with version control.

---

## Skill Composition 🧩

Build complex skills from simple, reusable building blocks.

### Overview

Skill composition enables skills to reference other skills as dependencies, creating modular knowledge hierarchies. This prevents duplication and enables sophisticated skill orchestration.

### Declaring Dependencies

Add dependencies to skill front matter:

```yaml
---
name: full-stack-api-design
version: 1.0.0
depends_on:
  - api-design-patterns@^1.0.0
  - database-design-patterns@^1.0.0
  - event-driven-architecture@^1.0.0
---
```

### Features

**Automatic Resolution** — Dependencies loaded recursively with correct order
**Circular Detection** — Prevents infinite dependency loops
**Version Compatibility** — Ensures compatible versions are loaded
**Load Optimization** — Dependencies loaded once, shared across skills

### Usage

```bash
# View dependency tree
cortex skills compose full-stack-api-design

# Output:
# full-stack-api-design
# ├── api-design-patterns@1.2.3
# ├── database-design-patterns@1.1.0
# └── event-driven-architecture@1.0.5
#     └── microservices-patterns@1.2.1

# Validate composition (check for circular deps)
cortex skills validate full-stack-api-design

# List all composite skills
cortex skills list --composite-only
```

### Configuration

**File:** `skills/composition.yaml`

```yaml
compositions:
  full-stack-api-design:
    name: "Full Stack API Design"
    description: "Complete API design with database and async patterns"
    skills:
      - api-design-patterns@^1.0.0
      - database-design-patterns@^1.0.0
      - event-driven-architecture@^1.0.0
    load_order: [database-design-patterns, api-design-patterns, event-driven-architecture]

  kubernetes-complete:
    name: "Complete Kubernetes Stack"
    description: "Full K8s deployment, security, and GitOps"
    skills:
      - kubernetes-deployment-patterns@^1.0.0
      - kubernetes-security-policies@^1.0.0
      - helm-chart-patterns@^1.0.0
      - gitops-workflows@^1.0.0
```

### Benefits

- ✅ **Reduced Duplication** — Define patterns once, reference everywhere
- ✅ **Modular Knowledge** — Build complex skills from simple blocks
- ✅ **Easier Maintenance** — Update dependencies independently
- ✅ **Clear Dependencies** — Explicit knowledge requirements

---

## Skill Versioning 📦

Semantic versioning for controlled evolution and backward compatibility.

### Overview

Skills use semantic versioning (MAJOR.MINOR.PATCH) enabling controlled updates, breaking change management, and clear upgrade paths.

### Version Format

- **MAJOR** (1.0.0) — Breaking changes, incompatible updates
- **MINOR** (0.1.0) — New features, backward compatible
- **PATCH** (0.0.1) — Bug fixes, no new features

### Version Specifications

```yaml
# Exact version
depends_on:
  - skill@1.2.3

# Caret (≥1.2.0, <2.0.0)
depends_on:
  - skill@^1.2.0

# Tilde (≥1.2.0, <1.3.0)
depends_on:
  - skill@~1.2.0

# Minimum version
depends_on:
  - skill@>=1.2.0

# Latest version
depends_on:
  - skill@latest
```

### Directory Structure

```
skills/
├── api-design-patterns@1.0.0/
│   └── SKILL.md
├── api-design-patterns@1.1.0/
│   └── SKILL.md
├── api-design-patterns@1.2.0/
│   └── SKILL.md
└── versions.yaml
```

### Version Metadata

**File:** `skills/versions.yaml`

```yaml
api-design-patterns:
  versions:
    - version: 1.2.3
      date: 2025-11-01
      changes: Added GraphQL patterns
      breaking: false
    - version: 1.2.0
      date: 2025-10-15
      changes: REST best practices expanded
      breaking: false
    - version: 1.0.0
      date: 2025-09-01
      changes: Initial release
      breaking: false
  latest: 1.2.3
  deprecated: []
```

### Usage

```bash
# Show available versions
cortex skills versions api-design-patterns

# Output:
# api-design-patterns versions:
# - 1.2.3 (latest) - 2025-11-01 - Added GraphQL patterns
# - 1.2.0 - 2025-10-15 - REST best practices expanded
# - 1.0.0 - 2025-09-01 - Initial release

# Show which agents use a skill version
cortex skills deps api-design-patterns@1.2.0

# Check for version conflicts
cortex skills validate --check-versions
```

### Version Resolution

When multiple versions are requested, the system:
1. Checks compatibility constraints
2. Selects highest compatible version
3. Warns about breaking changes
4. Falls back to safe version if conflicts exist

### Upgrade Path

```bash
# Show outdated skills
cortex skills outdated

# Output:
# Outdated Skills:
# - api-design-patterns: 1.0.0 → 1.2.3 (minor updates available)
# - python-testing-patterns: 2.1.0 → 3.0.0 (BREAKING CHANGE)

# Upgrade to latest compatible versions
cortex skills upgrade --all

# Upgrade specific skill (interactive if breaking)
cortex skills upgrade api-design-patterns
```

### Benefits

- ✅ **Controlled Evolution** — Update skills without breaking agents
- ✅ **Backward Compatibility** — Older versions remain available
- ✅ **Clear Upgrade Paths** — Know what changed and why
- ✅ **Dependency Safety** — Prevent version conflicts

---

## Best Practices

### For Skill Authors

**Versioning Guidelines:**
- Increment PATCH for typo fixes, clarifications
- Increment MINOR for new sections, examples
- Increment MAJOR for restructuring, removed content

**Composition Guidelines:**
- Keep dependencies minimal and focused
- Document why each dependency is needed
- Test circular dependency detection
- Provide load_order hints for complex compositions

### For Skill Users

**Version Selection:**
- Use `^` for most dependencies (safe minor updates)
- Use exact versions for critical production skills
- Use `@latest` only for development/testing

**Composition Usage:**
- Prefer composite skills for common stacks
- Create custom compositions for team patterns
- Validate before using in production

---

## Related Features

- **[Skill Ratings & Analytics](skill-ratings-analytics.html)** — Quality metrics and feedback
- **[Skills Guide](../skills.html)** — Complete skill system overview
- **[TUI Skills View](../tui.html)** — Managing skills visually

---

*For implementation details, see `claude_ctx_py/composer.py` and `claude_ctx_py/versioner.py`*
