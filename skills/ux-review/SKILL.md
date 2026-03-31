---
name: ux-review
description: "Multi-perspective UX review combining usability heuristics, WCAG accessibility checks, and interaction design analysis. Use when reviewing UI components before release, evaluating user flows for usability issues, conducting design critiques, or auditing accessibility compliance."
tags: [ux, usability, accessibility, design-review, heuristics]
triggers:
  - ux review
  - usability review
  - design critique
  - user experience analysis
  - heuristic evaluation
---

# UX Review

Comprehensive user experience review that coordinates usability, accessibility, and interaction design perspectives for thorough analysis of components, flows, or features.

## When to Use This Skill

- Reviewing new components or features before release
- Evaluating existing flows for usability issues
- PR reviews that touch UI/UX code
- Design system component reviews
- Onboarding flow or checkout flow optimization
- Avoid using for purely visual/aesthetic reviews — use `ui-design-aesthetics` instead

## Workflow

### Step 1: Gather Context

Answer these questions before reviewing:

1. What is the user trying to accomplish?
2. What is this component's role in the larger flow?
3. Who are the target users (personas, skill level)?
4. What are the success criteria?

### Step 2: Run Heuristic Scan (Nielsen's 10)

Evaluate the interface against each heuristic:

| Heuristic | Check |
|-----------|-------|
| Visibility of system status | Does the user always know what's happening? |
| Match with real world | Does it use familiar language and concepts? |
| User control and freedom | Can users undo, go back, escape? |
| Consistency and standards | Does it follow platform conventions? |
| Error prevention | Are mistakes prevented before they happen? |
| Recognition over recall | Is information visible rather than memorized? |
| Flexibility and efficiency | Are there shortcuts for expert users? |
| Aesthetic and minimalist design | Is every element necessary? |
| Error recovery | Are error messages helpful and actionable? |
| Help and documentation | Is guidance available when needed? |

### Step 3: Multi-Perspective Analysis

#### Usability Perspective

- **User flow**: Is the path to completion clear and efficient?
- **Information architecture**: Is content organized logically?
- **Cognitive load**: Is the interface overwhelming?
- **Mental models**: Does it work like users expect?

#### Accessibility Perspective (WCAG 2.1 AA)

- **Keyboard navigation**: Can everything be done without a mouse?
- **Screen reader**: Is the experience equivalent for assistive tech users?
- **Color contrast**: Do all text/UI elements meet 4.5:1 ratio?
- **Focus management**: Is focus order logical, visible, and never trapped?

```html
<!-- Example: Accessible button with proper ARIA -->
<button aria-label="Close dialog" aria-describedby="close-hint">
  <svg aria-hidden="true"><!-- icon --></svg>
</button>
<span id="close-hint" class="sr-only">Press Escape to close</span>
```

#### Interaction Design Perspective

- **State coverage**: Are all states handled (loading, empty, error, success)?
- **Feedback**: Does the user know their action worked?
- **Transitions**: Are animations purposeful and under 300ms?
- **Progressive disclosure**: Is complexity revealed appropriately?

### Step 4: Prioritize Findings

Categorize every finding:

| Priority | Criteria | Action |
|----------|----------|--------|
| **Critical** | Blocks usability or fails WCAG AA | Must fix before release |
| **High** | Significantly degrades experience | Fix in current sprint |
| **Enhancement** | Improves delight and efficiency | Backlog for next iteration |
| **Future** | Long-term improvements | Track in roadmap |

### Step 5: Produce Review Report

```markdown
## UX Review: [Component/Flow Name]

### Summary
[2-3 sentence executive summary]

### Critical Issues
- [ ] Issue 1: [Description, impact, WCAG criterion if applicable]
- [ ] Issue 2: [Description, impact]

### Recommendations by Category

#### Usability
| Finding | Impact | Recommendation |
|---------|--------|----------------|
| [Issue] | High/Med/Low | [Fix] |

#### Accessibility
| Finding | WCAG Criterion | Recommendation |
|---------|----------------|----------------|
| [Issue] | [2.x.x Level] | [Fix] |

#### Interaction Design
| Finding | Impact | Recommendation |
|---------|--------|----------------|
| [Issue] | High/Med/Low | [Fix] |

### Next Steps
1. Create issues for critical findings
2. Add accessibility requirements to acceptance criteria
3. Schedule follow-up review after fixes
```

## Focus Area Deep Dives

Use `--focus` to narrow the review scope:

- **`--focus=ux`**: User flow mapping, task efficiency, error recovery, learnability
- **`--focus=a11y`**: WCAG 2.1 AA audit, keyboard nav, screen reader, contrast, focus management
- **`--focus=interaction`**: State coverage, feedback timing, micro-interactions, animation review

## Best Practices

- **Test with real content** — Lorem ipsum hides information architecture problems
- **Check all states** — Empty, loading, error, success, and edge-case states
- **Verify keyboard flow** — Tab through the entire component without a mouse
- **Use browser dev tools** — Lighthouse accessibility audit catches low-hanging fruit
- **Prioritize ruthlessly** — A focused list of critical fixes beats a wall of suggestions
