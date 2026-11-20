---
name: ui-ux-skill-picker
description: "Ask the user what they are trying to achieve with a UI or design request, then recommend the UI/UX skill or skills to run, with the reason and the input each one needs. Use when the user asks which UX, design, or UI review skill to use, or when a UI/UX request is vague enough that more than one skill fits. Recommends only; it does not run the review or design work. Not for requests that already name a skill or map cleanly to one."
keywords:
  - skill picker
  - which ux skill
  - which design skill
  - choose a ux skill
  - ux skill recommendation
triggers:
  - which ux skill
  - which design skill should i use
  - what skill should i use for this ui
  - help me pick a ux skill
  - where do i start with this design
---

# UI/UX Skill Picker

Ask what the user wants out of the work, then point them at the UI/UX skill that does it. Several of these skills overlap at the edges, and the right one depends on the goal more than on the artifact, so the goal comes first.

This skill recommends. It does not run the review, the design, or the research itself.

## When to Use

- The user asks which UX, design, or UI review skill to use.
- The request is vague ("look at my UI", "make this screen better") and more than one skill fits.

If the request already names a skill, or maps to exactly one row in the tables below, invoke that skill directly instead.

## Step 1: Ask the Goal

Skip any question the request already answers. Ask at most two, and use the structured question tool when the session has one.

First question, what the user wants out of this:

1. Find problems in a UI that already exists (built, or as mockups)
2. Design or build something new
3. Understand users or the journey they take
4. Write the words in the interface

Second question, only for goal 1 when the concern is not clear yet. Ask what worries them most:

- Usability: people get lost, confused, or stuck
- Accessibility: keyboard, screen reader, contrast, WCAG
- Behavior: loading, empty, and error states, feedback, timing, keyboard handling
- Look and layout: hierarchy, color, type, density, how it holds up in daily use
- All of it, before a release

## Step 2: Map the Goal to a Skill

### Find problems in an existing UI

| Concern | Skill |
|---------|-------|
| Usability, Nielsen heuristics | `ux-review` |
| Accessibility on its own, WCAG 2.2 AA | `accessibility-audit` |
| States, feedback, timing, keyboard behavior, error recovery | `ux-interaction-review` |
| Visual system, hierarchy, density, daily-use workflow | `design-journey-review` |
| Mockups or wireframes that are not built yet | `design-critiquer` |
| Two or more of the concerns above, or a full pre-release review | `ui-ux-review-suite` |
| Whether the running app works (functional check, screenshots, console errors) | `webapp-testing` |

`ux-review` also covers WCAG alongside the heuristics. Recommend `accessibility-audit` when accessibility is the main concern rather than one of several.

### Design or build something new

| Need | Skill |
|------|-------|
| Interaction behavior and states for a new feature | `interaction-design` |
| Visual direction for a new interface | `ui-design-aesthetics` |
| Component specs, responsive layout, CSS | `frontend-design` |
| Design tokens and a component library | `design-system-architecture` |
| Dashboard layout and KPI selection | `dashboard-designer` |

### Understand users or the journey

| Need | Skill |
|------|-------|
| Interviews, surveys, personas, synthesis | `ux-researcher` |
| A journey map across touchpoints, funnel drop-off | `user-journey-mapping` |

### Write interface text

| Need | Skill |
|------|-------|
| Microcopy, error messages, labels, empty-state text | `ux-writer` |

## Step 3: Recommend

- Tie the reason to what the user said, not to the skill's description.
- Recommend one skill by default. Recommend two only when the goal splits into two concerns that neither skill covers alone.
- Three or more review concerns means `ui-ux-review-suite`, not a list of three skills.
- When the user wants to find problems and then fix them, recommend the review skill first and name the build skill for the fixes afterward.
- Recommend only skills listed in the current session. If a mapped skill is missing, say so and recommend the closest one that is installed.
- If the session lists a UI review skill specific to the project's codebase or framework, recommend it over the generic review skills and say why.

Give the recommendation in this shape, then ask whether to start it. Invoke the skill only after the user says yes.

```markdown
Recommended: `ux-interaction-review`
Why: the save dialog feels broken, and that comes down to state coverage and feedback timing.
Give it: the dialog component and the states you can reproduce.
Afterward: `interaction-design` to design the missing states.
```

Leave out the `Afterward` line when there is no follow-on step.
