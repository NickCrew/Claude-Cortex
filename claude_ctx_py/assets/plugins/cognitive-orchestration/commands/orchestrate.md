---
model: claude-opus-4-1
allowed-tools: Task, Read, Write, Bash, Glob, Grep
argument-hint: <problem> [--team-size=<3-12>] [--pattern=<sequential|parallel|dialectical>]
description: Multi-perspective analysis through dynamic expert team coordination
---

# Orchestrate Command

Assemble and coordinate a team of virtual experts to analyze problems from multiple perspectives, generating insights unavailable from any single viewpoint.

## Overview

The orchestrate command implements cognitive orchestration patterns for complex problem-solving:
- Dynamic team assembly based on problem domain
- Voice-differentiated expert analysis
- Structured disagreement protocols
- Convergent synthesis into actionable wisdom

## Arguments

**$1 (Required)**: The problem or question to analyze
**--team-size**: Number of experts (3-12, default: auto-detect)
**--pattern**: Orchestration pattern (sequential, parallel, dialectical)

## Complexity Scaling Framework

### Simple (3-4 experts)
[Extended thinking: Single-phase analysis with direct synthesis for focused problems]

**Team Composition**:
- Core domain expert
- Implementation specialist
- Integration coordinator

**Execution**: Sequential expert consultation → Direct synthesis

### Moderate (5-6 experts)
[Extended thinking: Two-phase with structured disagreement for problems with trade-offs]

**Team Composition**:
- Multiple domain specialists
- Constructive challenger
- Integration lead

**Execution**: Parallel analysis → Disagreement round → Collaborative synthesis

### Complex (7-9 experts)
[Extended thinking: Multi-phase with hierarchical synthesis for enterprise decisions]

**Team Composition**:
- Strategic advisors
- Technical specialists
- Operational experts
- Dissenting voices
- Synthesis coordinator

**Execution**: Hierarchical analysis → Multiple disagreement rounds → Emergent synthesis

### Enterprise (10+ experts)
[Extended thinking: Teams-of-teams for organization-level decisions]

**Team Composition**:
- Strategic team (vision, business, market)
- Technical team (architecture, implementation, operations)
- Quality team (security, testing, reliability)
- Meta-integration coordinator

**Execution**: Team-level synthesis → Cross-team integration → Meta-synthesis

## Orchestration Patterns

### Sequential Pattern
Best for: Problems with clear dependency chains
```
Expert A → Expert B → Expert C → Synthesis
(Each builds on previous insights)
```

### Parallel Pattern
Best for: Problems needing diverse simultaneous perspectives
```
Expert A ─┐
Expert B ─┼→ Synthesis
Expert C ─┘
(Independent analysis, combined insights)
```

### Dialectical Pattern
Best for: Problems with competing valid approaches
```
Thesis (Expert A) ←→ Antithesis (Expert B) → Synthesis
(Structured opposition yields breakthrough)
```

### Hierarchical Pattern
Best for: Complex multi-level decisions
```
Strategic Layer (Experts A, B)
        ↓
Tactical Layer (Experts C, D, E)
        ↓
Operational Layer (Experts F, G)
        ↓
    Synthesis
```

### Adaptive Pattern
Best for: Evolving problems with unknown structure
```
Start → Assess → Select Pattern → Execute → Reassess → Adapt
(Pattern switches as understanding deepens)
```

## Expert Voice Template

```markdown
### [Expert Title] Analysis

**Domain Vocabulary**: [5-7 characteristic terms]
**Key Question**: "[What I always ask]"

Looking at this through my lens as a [role], I notice...

**Primary Insight**: [Core finding from this perspective]
**Trade-off Identified**: [What this view reveals about tensions]
**Recommendation**: [Actionable guidance from this expertise]
```

## Disagreement Protocol

### Intensity Levels

1. **Gentle** (refinement-focused)
   - "This approach has merit, but what if..."
   - Edge case identification
   - Optimization suggestions

2. **Systematic** (methodology-challenging)
   - "While the goal is sound, I question whether..."
   - Alternative framework proposals
   - Evidence evaluation

3. **Rigorous** (premise-challenging)
   - "I fundamentally question whether we're solving the right problem..."
   - Paradigm alternatives
   - Success criteria redefinition

4. **Paradigmatic** (worldview-challenging)
   - "What if everything we think we know is wrong?"
   - Revolutionary approaches
   - Constraint elimination

## Synthesis Template

```markdown
## Expert Team Synthesis

### Convergent Insights
[Where experts agree and why this matters]

### Creative Tensions
[Where perspectives productively differ]
- Tension 1: [Expert A] vs [Expert B] on [issue]
- Resolution approach: [How to honor both]

### Integrated Solution
[Unified approach that honors multiple viewpoints]

### Emergent Discoveries
[Insights that emerged only from combining perspectives]

### Implementation Path
1. [First action]
2. [Second action]
3. [Third action]
```

## Examples

```bash
# Auto-detect team size and pattern
/orchestrate "Should we migrate from monolith to microservices?"

# Specify team size for focused analysis
/orchestrate "Review our authentication architecture" --team-size=5

# Force dialectical pattern for contested decisions
/orchestrate "Evaluate build vs buy for payment processing" --pattern=dialectical

# Large team for strategic decisions
/orchestrate "Plan our 3-year technical roadmap" --team-size=10
```

## Success Indicators

- Insights unavailable from any single perspective
- Productive disagreement leading to stronger solutions
- Emergent understanding beyond simple aggregation
- Clear actionable recommendations with trade-off awareness

Invoke the master-orchestrator agent with: $ARGUMENTS
