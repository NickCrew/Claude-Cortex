---
name: pre-mortem
description: "Imagine failure first to surface mitigations that double as feature ideas"
category: collaboration
complexity: standard
mcp-servers: []
personas: [architect, security, devops, product-manager]
subagents: []
---

# /collaboration:pre-mortem — Fail First, Then Design

## Trigger Pattern
```
/collaboration:pre-mortem [initiative] [--horizon 30|90|180]
```

## Behavior
1. Define success state and horizon (default 90 days).
2. Imagine initiative failed; list top failure modes (tech, UX, org, market, compliance).
3. For each failure mode, generate mitigation ideas and guardrails; tag **Effort (S/M/L)** and **Owner**.
4. Pull 2–3 mitigations that double as feature ideas or safeguards.
5. Create immediate guardrail Tasks or `/ctx:plan` handoff.

## Output
- Sections: Success State, Failure Modes, Mitigations, Guardrails/Features, Immediate Tasks.
- Optional save: `docs/plans/<date>-pre-mortem.md`.

## Personas
- **architect**: systemic risks and dependencies
- **security**: threat and compliance angles
- **devops**: reliability and rollout risks
- **product-manager**: user impact and prioritization

## Delegation
- Use Task tool for env/infra discovery; inline for conceptual sessions.

## Follow-up
- Feed guardrails into `/ctx:plan`; ensure Tasks created for critical mitigations.
