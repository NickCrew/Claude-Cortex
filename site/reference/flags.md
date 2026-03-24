---
layout: default
title: Legacy Flags
parent: Reference
nav_order: 3
nav_exclude: true
---

# Legacy Flags

This page is retained only to clarify terminology drift.

The older Cortex docs talked about `FLAGS.md`, flag categories, and a TUI Flag
Manager. That is **not** the current public model for this repo.

## Current Status

For the current `site/` documentation, treat flag-based workflow guidance as
historical rather than canonical.

If you are using Cortex today, the primary user-facing building blocks are:

- **agents** for activation and delegation
- **skills** for reusable instruction packs
- **rules** for behavioral guidance
- **hooks** for automation

## What To Read Instead

- [Skills](../guides/skills.md)
- [AI Intelligence](../guides/ai-intelligence.md)
- [Configuration Reference](configuration.md)

## Why This Page Exists

Some older docs and examples still refer to flags. This placeholder exists so
those references are clearly marked as outdated instead of pretending the old
flag surface is still the recommended entry point.
