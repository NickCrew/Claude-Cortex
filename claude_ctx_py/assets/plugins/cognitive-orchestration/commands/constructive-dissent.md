---
model: claude-opus-4-1
allowed-tools: Task, Read, Write, Bash, Glob, Grep
argument-hint: <proposal> [--intensity=<gentle|systematic|rigorous|paradigmatic>] [--alternatives=<count>]
description: Structured disagreement to strengthen proposals through systematic challenge
---

# Constructive Dissent Command

Systematically challenge proposals through structured dissent protocols that expose weaknesses, test assumptions, and generate superior alternatives.

## Overview

Transform potential conflicts into productive tension that leads to breakthrough thinking and robust implementation strategies.

## Arguments

**$1 (Required)**: The proposal or decision to challenge
**--intensity**: Challenge level (gentle, systematic, rigorous, paradigmatic)
**--alternatives**: Number of alternatives to generate (default: 3)

## Dissent Intensity Framework

### Gentle Level (Refinement-focused)
[Extended thinking: Improve without fundamental challenge to core approach]

**Challenge Characteristics**:
- Assumption questioning with evidence requests
- Edge case identification with boundary testing
- Implementation detail refinement
- Risk mitigation suggestions
- Alternative approach comparison

**Example Phrases**:
- "This approach has merit, but what if we considered..."
- "I'm curious about how this would handle..."
- "What assumptions are we making about..."
- "Have we considered the implications of..."

### Systematic Level (Methodology-challenging)
[Extended thinking: Challenge underlying methods while respecting intent]

**Challenge Characteristics**:
- Methodology critique with alternatives
- Evidence evaluation with validation requirements
- Stakeholder perspective integration
- Long-term consequence analysis
- Resource allocation questioning

**Example Phrases**:
- "While the goal is sound, I question whether this methodology..."
- "The evidence presented doesn't address..."
- "From the perspective of [stakeholder], this might..."
- "Long-term, this could lead to..."

### Rigorous Level (Premise-challenging)
[Extended thinking: Attack fundamental premises, demand comprehensive justification]

**Challenge Characteristics**:
- Fundamental premise questioning
- Paradigm alternative generation
- Success criteria challenge
- Stakeholder priority reordering
- Innovation opportunity identification

**Example Phrases**:
- "I fundamentally question whether we're solving the right problem..."
- "This entire framework assumes X, but what if..."
- "Are we defining success correctly, or should we..."
- "This prioritizes X, but shouldn't we prioritize Y because..."

### Paradigmatic Level (Worldview-challenging)
[Extended thinking: Question fundamental worldview, propose radical alternatives]

**Challenge Characteristics**:
- Worldview assumption identification
- Revolutionary approach generation
- Value system questioning
- Future-state visioning
- Breakthrough innovation pursuit

**Example Phrases**:
- "This assumes a world where X, but we're moving toward..."
- "What if everything we think we know about this is wrong?"
- "Instead of optimizing within constraints, what if we eliminated them?"
- "Are we thinking big enough?"

## Challenge Methodologies

### Assumption Audit
1. **Explicit assumptions**: What's stated as given?
2. **Implicit assumptions**: What's unstated but operating?
3. **Structural assumptions**: What framework biases exist?
4. **Temporal assumptions**: What time constraints are artificial?

### Edge Case Generation
- **Scale extremes**: Minimum and maximum scenarios
- **Performance limits**: Where does it break?
- **User behavior extremes**: Best and worst case usage
- **Environmental variations**: Different contexts
- **Resource constraints**: Limited budget/time/people

### Alternative Generation Framework
1. **Goal abstraction**: Extract core objectives from specific implementation
2. **Constraint relaxation**: Temporarily remove limitations
3. **Method inversion**: Consider opposite approaches
4. **Cross-domain inspiration**: Apply solutions from other fields
5. **Future projection**: Design for different conditions

### Stakeholder Advocacy
- **End user**: How does this affect people using it?
- **Maintainer**: What's the ongoing cost?
- **Security**: What risks does this introduce?
- **Accessibility**: Who might be excluded?
- **Future stakeholder**: Who isn't here yet?

## Output Format

```markdown
## Constructive Dissent Analysis: [Proposal Title]

### Intensity Level: [Selected Level]

### Executive Summary
[2-3 sentence summary of key challenges and recommendations]

### Assumption Audit
| Assumption | Type | Validity | Risk if Wrong |
|------------|------|----------|---------------|
| [Assumption 1] | Explicit/Implicit | High/Medium/Low | [Impact] |

### Challenges Raised

#### Challenge 1: [Title]
**Type**: [Methodology/Premise/Evidence/Stakeholder]
**Core Argument**: [What's being challenged and why]
**Evidence**: [Data or reasoning supporting challenge]
**Alternative Approach**: [What to do instead]

### Generated Alternatives

#### Alternative 1: [Title]
**Approach**: [High-level description]
**Advantages**: [Why this might be better]
**Trade-offs**: [What you give up]
**Implementation Path**: [How to execute]

### Synthesis Recommendations

#### Strengthen Current Proposal
1. [Specific improvement]
2. [Specific improvement]

#### Consider Alternative If
- [Condition that favors switching]
- [Condition that favors switching]

### Unresolved Questions
- [Question requiring more information]
- [Question requiring more information]
```

## Examples

```bash
# Gentle challenge for refinement
/constructive-dissent "Our API pagination strategy uses offset-based pagination" --intensity=gentle

# Systematic challenge for major decision
/constructive-dissent "Migrate to microservices architecture" --intensity=systematic --alternatives=3

# Rigorous challenge for strategic direction
/constructive-dissent "Build our own CMS instead of using existing solutions" --intensity=rigorous

# Paradigmatic challenge for transformation
/constructive-dissent "Our business model of per-seat licensing" --intensity=paradigmatic
```

## Success Indicators

- Identified assumptions that were previously invisible
- Generated viable alternatives not previously considered
- Strengthened original proposal through challenge
- Clear decision criteria for choosing approaches
- Stakeholder perspectives adequately represented

Invoke constructive challenge analysis with: $ARGUMENTS
