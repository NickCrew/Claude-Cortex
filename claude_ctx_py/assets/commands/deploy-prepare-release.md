---
name: "deploy:prepare-release"
description: Prepare application for production deployment
category: deployment
personas: [deployment-engineer, quality-engineer, security-specialist]
subagents: [general-purpose, code-reviewer, security-auditor, test-automator]
---

# /deploy:prepare-release — Skill-backed release prep

## Use
- Load `skills/release-prep/SKILL.md` (skill `release-prep`) and follow it.
- Then load `skills/release-prep/references/prepare-release.md` for the detailed workflow.

## Usage
```
/deploy:prepare-release [version] [--type major|minor|patch]
```