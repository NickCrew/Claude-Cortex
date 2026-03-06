---
layout: default
title: Reference
nav_order: 4
has_children: true
---

# Reference Documentation

Technical reference documentation for cortex configuration, APIs, and CLI.

## Contents

- [Configuration Reference](configuration.md) - All configuration files with schemas and examples
- [Skill Showcase](skill-showcase.md) - Curated guide to the most sophisticated skills, categorized by capability
- [bin/ Utilities](bin-utilities.md) - Agent-facing tools for routine development (`tx`, `browser_tools`, `committer`, etc.)
- [scripts/ Utilities](scripts-utilities.md) - Project-internal maintenance scripts (manpages, registry validation, uninstall)
- [Manpages](README.md) - CLI manpage generation
- [Settings Files Catalog](../settings-files.md) - Complete file listing

## Configuration Files

| File | Description |
|------|-------------|
| [`cortex-config.json`](configuration.md#cortex-configjson) | Main launcher configuration |
| [`memory-config.json`](configuration.md#memory-configjson) | Memory vault settings |
| [`skill-rules.json`](configuration.md#skill-rulesjson) | Keyword-based skill matching |
| [`recommendation-rules.json`](configuration.md#recommendation-rulesjson) | File pattern recommendations |

## JSON Schemas

All cortex configuration files have JSON schemas for validation:

```
schemas/
├── cortex-config.schema.json
├── memory-config.schema.json
├── skill-rules.schema.json
├── recommendation-rules.schema.json
└── onboarding-state.schema.json
```

See the [Configuration Reference](configuration.md#json-schema-validation) for editor setup instructions.
