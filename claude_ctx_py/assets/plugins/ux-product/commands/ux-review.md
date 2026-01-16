---
model: claude-sonnet-4-0
allowed-tools: Task, Read, Write, Glob, Grep
argument-hint: <component-or-flow> [--focus=<ux|a11y|interaction>]
description: Multi-perspective UX review combining usability, accessibility, and interaction design analysis
---

# UX Review Command

Comprehensive user experience review that coordinates multiple UX specialists for thorough analysis of components, flows, or entire features.

## Overview

This command orchestrates a multi-agent UX review, bringing together perspectives from:
- **UX Designer**: Usability, information architecture, user flows
- **Accessibility Expert**: WCAG compliance, keyboard navigation, screen reader support
- **Interaction Designer**: State management, micro-interactions, feedback patterns

## Arguments

**$1 (Required)**: The component, flow, or feature to review
**--focus**: Optional focus area (ux, a11y, interaction, or all)

## Review Framework

### Phase 1: Initial Assessment
[Extended thinking: Understand the component/flow context, identify primary user goals, and map key interaction points.]

1. **Context Gathering**
   - What is the user trying to accomplish?
   - What is the component's role in the larger flow?
   - Who are the target users?

2. **Heuristic Scan**
   - Apply Nielsen's 10 usability heuristics
   - Identify obvious friction points
   - Note accessibility red flags

### Phase 2: Multi-Perspective Analysis

#### UX Designer Perspective
- User flow completeness and clarity
- Information architecture alignment
- Cognitive load assessment
- Error prevention and recovery
- Mental model alignment

#### Accessibility Expert Perspective
- WCAG 2.1 AA compliance check
- Keyboard navigation audit
- Screen reader experience
- Color contrast verification
- Focus management review

#### Interaction Designer Perspective
- State coverage (loading, empty, error, success)
- Feedback timing and clarity
- Micro-interaction opportunities
- Transition and animation review
- Progressive disclosure patterns

### Phase 3: Synthesis & Recommendations

1. **Critical Issues**: Must fix for usability/accessibility
2. **High Priority**: Significantly impacts user experience
3. **Enhancements**: Would improve delight and efficiency
4. **Future Considerations**: Long-term improvements

## Output Format

```markdown
## UX Review: [Component/Flow Name]

### Summary
[2-3 sentence executive summary]

### Critical Issues
- [ ] Issue 1: Description and impact
- [ ] Issue 2: Description and impact

### Recommendations by Category

#### Usability
- Finding 1 → Recommendation
- Finding 2 → Recommendation

#### Accessibility
- Finding 1 → Recommendation (WCAG criterion)
- Finding 2 → Recommendation (WCAG criterion)

#### Interaction Design
- Finding 1 → Recommendation
- Finding 2 → Recommendation

### Implementation Priority
1. Critical fixes (do first)
2. High-priority improvements
3. Enhancement opportunities
```

## Examples

```bash
# Review a specific component
/ux-review "checkout form"

# Focus on accessibility only
/ux-review "navigation menu" --focus=a11y

# Review entire flow
/ux-review "user onboarding flow" --focus=ux
```

## Integration with Development

After review completion:
1. Create issues/tasks for critical findings
2. Add accessibility requirements to acceptance criteria
3. Update component documentation with UX guidelines
4. Schedule follow-up review after fixes

Invoke the ux-designer agent to coordinate review with: $ARGUMENTS
