---
name: ux-interaction-review
description: "Combined UX and interaction design review: usability heuristics, state coverage, feedback patterns, timing, keyboard behavior, error recovery, and progressive disclosure. Use when reviewing how an interface works mechanically and whether interactions are well-designed for use."
keywords:
  - ux review
  - interaction design
  - usability review
  - state coverage
  - micro-interactions
  - feedback patterns
  - error states
  - heuristic evaluation
triggers:
  - ux review
  - interaction review
  - usability review
  - review interactions
  - state coverage
  - how does this work
  - is this well designed
file_patterns:
  - '**/*.tsx'
  - '**/*.jsx'
  - '**/*.vue'
  - '**/*.svelte'
  - '**/*.ts'
confidence: 0.8
---

# UX & Interaction Review

Combined review of usability and interaction design. Evaluates whether an interface works mechanically (state coverage, feedback, timing, error recovery) and whether users can accomplish their goals efficiently (heuristics, flow, progressive disclosure).

This skill merges the "how does it work?" axis: heuristics, state coverage, feedback patterns, keyboard behavior, timing, animation, and error handling.

## When to Use

- Reviewing new or existing components before release
- Evaluating multi-state interactions (modals, popovers, wizards, dashboards)
- Auditing error/empty/loading/success state handling
- Assessing feedback timing and animation choreography
- Checking keyboard behavior and escape hatches
- PR reviews that touch interactive code
- Design system component reviews

Do NOT use for purely visual/aesthetic concerns (typography, color palettes, spacing rhythm) or for mapping the user's emotional journey across sessions. Use `design-journey-review` for those.

## Quick Reference

| Task | Load reference |
| --- | --- |
| State patterns and micro-interaction specs | `skills/ux-interaction-review/references/state-and-interaction-patterns.md` |

## Workflow

### Step 1: Gather Context

1. What is the user trying to accomplish?
2. What component/flow is under review? What states can it be in?
3. Who are the users (expert vs. novice)? Single-user tool vs. public-facing?
4. What are the success criteria?

### Step 2: Heuristic Scan (Nielsen's 10)

Evaluate against each heuristic. Score Good / Fair / Poor:

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

### Step 3: Interaction Map

For every interactive element, document:

| Element | Trigger | Feedback | States | Dismiss/Escape |
|---------|---------|----------|--------|----------------|
| [name] | click/hover/focus | what changes | all possible states | how to exit |

### Step 4: State Coverage Audit

Check each state is handled:

| State | Handled? | Notes |
|-------|----------|-------|
| Loading | | |
| Empty (first use) | | |
| Empty (no results) | | |
| Partial data | | |
| Full / normal | | |
| Error (network) | | |
| Error (validation) | | |
| Error (permissions) | | |
| Success | | |
| Stale / outdated | | |
| Offline | | |
| Disabled | | |

### Step 5: Feedback & Timing Assessment

For each interaction, evaluate:

- **Latency class**: instant (<100ms), fast (100-300ms), noticeable (300ms-1s), slow (>1s)
- **Feedback timing**: does the user know their action worked immediately?
- **Animation duration**: appropriate for the action? (micro: 80-150ms, layout shift: 200-300ms, page transition: 300-400ms)
- **Progressive disclosure**: is complexity revealed only when needed?
- **Escape hatches**: can the user dismiss/undo/cancel from any state?

| Element | Duration | Easing | Assessment |
|---------|----------|--------|------------|
| [name] | Nms | ease-X | too fast / good / too slow |

### Step 6: Error Recovery & Edge Cases

- What happens on clipboard failure (especially file:// protocol)?
- What happens on rapid double-click?
- What happens if the data is stale?
- What happens if the user navigates away mid-action?
- Are destructive actions reversible?

### Step 7: Prioritize Findings

| Priority | Criteria | Action |
|----------|----------|--------|
| **Critical** | Blocks usability, user cannot complete task | Must fix |
| **High** | Significantly degrades experience or loses data | Fix this sprint |
| **Medium** | Noticeable friction, workaround exists | Next iteration |
| **Enhancement** | Improves delight, polish | Backlog |

### Step 8: Produce Report

```markdown
## UX & Interaction Review: [Component/Flow]

### Summary
[2-3 sentences: overall assessment, biggest concern, best strength]

### Heuristic Scores
[Table with Good/Fair/Poor per heuristic]

### Interaction Map
[Table: element, trigger, feedback, states, dismiss]

### State Coverage
[Table: state, handled yes/no, notes]

### Timing & Feedback
[Table: element, duration, easing, assessment]

### Findings by Priority

#### Critical
- [ ] Finding (impact, recommendation)

#### High
- [ ] Finding (impact, recommendation)

#### Medium / Enhancement
- [ ] Finding (impact, recommendation)

### Patterns to Preserve
[What's working well that should NOT be changed]
```

## Principles

- **State coverage is non-negotiable.** Every UI element exists in multiple states. If you can't enumerate them, the review isn't done.
- **Feedback must be immediate.** If the user clicks and nothing visibly changes for >100ms, that's a bug.
- **Escape hatches everywhere.** Every popup, modal, panel, and expanded state must be dismissible via Escape, outside-click, or an explicit close action.
- **Debounce destructive paths.** Copy buttons, delete buttons, submit buttons should all guard against rapid double-invocation.
- **Respect `prefers-reduced-motion`.** All non-essential animations should be wrapped in a motion media query.
- **Progressive disclosure over density.** Don't show everything at once. Reveal on interaction, not on load.
- **Test with real data.** Placeholder content hides information architecture problems. Empty states hide missing error handling.
