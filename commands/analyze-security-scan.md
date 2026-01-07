---
name: "analyze:security-scan"
description: Comprehensive security vulnerability assessment
category: analysis
personas: [security-specialist, compliance-auditor]
subagents: [security-auditor]
---

# /analyze:security-scan — Skill-backed security assessment

## Use
- Start with `skills/owasp-top-10/SKILL.md` (skill `owasp-top-10`) for baseline vulnerability framing.
- Use `skills/threat-modeling-techniques/SKILL.md` for structured threat modeling.
- Use `skills/security-testing-patterns/SKILL.md` for SAST/DAST/pentest planning.
- Use `skills/secure-coding-practices/SKILL.md` for remediation guidance.

## Usage
```
/analyze:security-scan [path] [--standard OWASP|GDPR|SOC2|HIPAA]
```

## Output
- Executive summary + detailed findings + compliance notes (as applicable).