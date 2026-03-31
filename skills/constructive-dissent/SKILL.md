---
name: constructive-dissent
description: "Structured disagreement protocols that expose weaknesses, test assumptions, and generate alternatives. Use when stress-testing proposals, playing devil's advocate, challenging architectural decisions, or auditing assumptions before finalizing plans."
tags: [decision-making, critical-thinking, collaboration, analysis]
triggers:
  - challenge this
  - devil's advocate
  - what could go wrong
  - stress test
  - critique proposal
  - question assumptions
---

# Constructive Dissent

Systematically challenge proposals through structured dissent protocols that expose weaknesses, test assumptions, and generate superior alternatives.

## When to Use This Skill

- Before finalizing major decisions or architectural choices
- Testing proposals for hidden weaknesses and blind spots
- Generating alternative approaches not yet considered
- Auditing assumptions (explicit, implicit, and structural)
- Evaluating competing solutions with stakeholder perspectives
- Avoid using for routine code reviews — use `requesting-code-review` instead

## Workflow

### Step 1: Select Dissent Intensity

Choose the appropriate challenge level based on decision stakes:

| Level | Purpose | When to Use |
|-------|---------|-------------|
| **Gentle** | Refine without challenging core approach | Low-stakes improvements, early drafts |
| **Systematic** | Challenge methods while respecting intent | Medium-stakes decisions, methodology review |
| **Rigorous** | Attack fundamental premises | High-stakes architecture, major pivots |
| **Paradigmatic** | Question worldview, propose radical alternatives | Strategic direction, innovation pursuit |

### Step 2: Run Assumption Audit

For the proposal under review, systematically identify:

1. **Explicit assumptions** — What's stated as given?
2. **Implicit assumptions** — What's unstated but operating?
3. **Structural assumptions** — What framework biases exist?
4. **Temporal assumptions** — What time constraints are artificial?

```markdown
| Assumption | Type | Validity | Risk if Wrong |
|------------|------|----------|---------------|
| Users prefer speed over accuracy | Implicit | Medium | Product misalignment |
| API rate limits won't change | Temporal | Low | System failure at scale |
```

### Step 3: Generate Edge Cases

Stress-test the proposal across dimensions:

- **Scale extremes**: What happens at 10x and 0.1x volume?
- **Performance limits**: Where does the approach break?
- **User behavior extremes**: Best-case and worst-case usage patterns
- **Resource constraints**: What if budget, time, or team shrinks by half?

### Step 4: Apply Challenge Methodologies

**Alternative Generation Framework:**
1. **Goal abstraction** — Extract core objectives from the specific implementation
2. **Constraint relaxation** — Temporarily remove limitations to see what's possible
3. **Method inversion** — Consider the opposite approach
4. **Cross-domain inspiration** — Apply solutions from other fields

**Stakeholder Advocacy** — Argue from each perspective:
- End user, maintainer, security, accessibility, future stakeholder

### Step 5: Synthesize and Recommend

Produce a structured analysis:

```markdown
## Constructive Dissent Analysis: [Proposal Title]

### Intensity Level: [Selected Level]

### Executive Summary
[2-3 sentence summary of key challenges and recommendations]

### Challenges Raised
#### Challenge 1: [Title]
**Type**: Methodology / Premise / Evidence / Stakeholder
**Core Argument**: [What's being challenged and why]
**Evidence**: [Data or reasoning supporting the challenge]
**Alternative Approach**: [What to do instead]

### Generated Alternatives
#### Alternative 1: [Title]
**Approach**: [High-level description]
**Advantages**: [Why this might be better]
**Trade-offs**: [What you give up]

### Synthesis
- Strengthen current proposal: [specific improvements]
- Consider alternative if: [conditions that favor switching]
- Unresolved questions: [items needing more information]
```

## Best Practices

- **Match intensity to stakes** — Paradigmatic dissent on a CSS tweak wastes everyone's time
- **Preserve constructive framing** — Challenge ideas, not people
- **Always propose alternatives** — Critique without alternatives is just criticism
- **Document assumptions explicitly** — Hidden assumptions are the highest-risk items
- **Use stakeholder advocacy** — Argue each perspective genuinely, not as a strawman
