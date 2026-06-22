---
name: design-journey-review
description: "Combined visual design and user journey review: color systems, typography, spacing, information density, visual hierarchy, workflow stages, emotional curve, friction points, and daily-use optimization. Use when evaluating how an interface looks, how it serves its user over time, and whether the design earns its space."
keywords:
  - visual design
  - aesthetics
  - user journey
  - color system
  - typography
  - information density
  - workflow optimization
  - daily driver
triggers:
  - design review
  - visual review
  - aesthetics review
  - journey review
  - how does this serve the user
  - is this optimized for daily use
  - review the design
file_patterns:
  - '**/*.tsx'
  - '**/*.jsx'
  - '**/*.vue'
  - '**/*.svelte'
  - '**/*.css'
  - '**/*.scss'
confidence: 0.8
---

# Design & Journey Review

Combined review of visual design and user journey. Evaluates whether an interface looks coherent and purposeful (color, type, spacing, density, hierarchy) and whether it serves the user's real workflow across sessions (friction points, emotional curve, golden path optimization, information architecture for daily use).

This skill merges the "how does it serve the user?" axis: visual hierarchy, color/type coherence, density balance, workflow stages, emotional patterns, and daily-use friction.

## When to Use

- Evaluating visual hierarchy and information density for data-dense UIs
- Reviewing color system coherence (semantic colors, phase colors, theme adaptation)
- Assessing typography choices and type scale effectiveness
- Mapping the user's actual workflow and identifying friction
- Optimizing for daily-driver use cases (expert users, repeated sessions)
- Evaluating whether design choices earn their viewport space
- Finding density inversions (low-value content in high-value positions)

Do NOT use for interaction mechanics (state coverage, feedback timing, escape hatches). Use `ux-interaction-review` for those.

## Quick Reference

| Task | Load reference |
| --- | --- |
| Visual system evaluation criteria | `skills/design-journey-review/references/visual-and-journey-criteria.md` |

## Workflow

### Step 1: Identify the Aesthetic Identity

Before evaluating individual elements, name the aesthetic the interface is targeting. Common archetypes:

- Mission control / operational terminal (dark, data-dense, monospace, status colors)
- Swiss/minimal (clean, lots of white space, geometric, strict grid)
- Linear/GitHub (dark panels, subtle borders, pill chips, blue accent)
- Editorial (large type, serif headings, generous spacing, reading-focused)
- Dashboard/enterprise (card-based, neutral, data visualization heavy)

If the interface doesn't commit to an identity, that's the first finding.

### Step 2: Color System Assessment

Evaluate the color architecture:

**Layer depth:**
- How many background layers exist? (bg, surface 1, surface 2, elevated)
- Is the contrast between layers sufficient but not jarring?
- Does the depth system create clear containment?

**Semantic colors:**
- Are success/warning/error/info colors distinct from each other?
- Do they occupy different hue bands with sufficient mutual contrast?
- Are any overloaded (same color meaning different things)?

**Accent/phase colors:**
- Do identifier colors collide with semantic colors? (common failure: green phases looking like "success")
- Are phase/category colors distinguishable at small sizes?
- Do light/dark theme variants maintain the same relative relationships?

**Color-mix patterns:**
- Are tinted backgrounds (e.g., `color-mix(in srgb, var(--X) 15%, transparent)`) used consistently?
- What mix ratios are used and are they uniform?

### Step 3: Typography Assessment

**Type scale:**
- What is the range? (e.g., 10px to 22px)
- Is the range compressed (hierarchy via weight only) or expanded (hierarchy via size)?
- Is there a clear "start here" size that anchors reading?
- Are there elements too small for their importance?

**Font pairing:**
- Does the mono/sans pairing work for the domain?
- Is monospace reserved for the right things (identifiers, code, versions)?
- Are weights used meaningfully or indiscriminately?

**Minimum sizes:**
- What's the smallest text? Is it legible on standard (96dpi) displays?
- Are critical labels/identifiers large enough to scan without squinting?

### Step 4: Spacing & Density

**Spacing rhythm:**
- Is there a consistent base unit? (4px, 8px, etc.)
- Do spacing values follow a scale (geometric, linear, or ad-hoc)?
- Are there rhythm breaks where adjacent elements use incompatible spacing?

**Information density:**
- For each major section, assess: space consumed vs. value for the user's primary task
- Find density inversions (low-value content occupying prime viewport real estate)
- For expert/daily-use tools: is instructional content collapsible after first visit?

**Density table:**

| Element | Space | Value for daily use | Verdict |
|---------|-------|---------------------|---------|
| [name] | Npx | high/medium/low/near-zero | justified/overweight/collapse |

### Step 5: Visual Hierarchy

Evaluate the scan order. For data-dense interfaces:

- Where does the eye land first? Is that the right place?
- Within a repeated element (row, card), is there a clear scan order? (identifier → status → metadata → action)
- Do elements at the same hierarchy level have the same visual weight?
- Are section breaks clear without being heavy?
- Do actionable elements look sufficiently different from informational ones?

### Step 6: User Journey Mapping

Map the user's actual workflow, not the interface structure:

**Golden path** (most frequent session, ~80% of visits):
- What does the user do, in order?
- How many steps/clicks to complete?
- Where is friction? (extra clicks, scroll depth, context switches, waiting)
- What is the total time?

**Secondary paths** (less frequent but still important):
- What triggers these?
- Are they accessible without disrupting the golden path?

**Journey stages:**

For each stage, document:
- **Goal**: what the user is trying to accomplish
- **Actions**: what they do
- **Friction**: what slows them down
- **Emotion**: satisfaction, neutrality, or frustration (and why)
- **Opportunity**: what would make this faster or more satisfying

### Step 7: Daily-Driver Optimization

For tools used repeatedly by the same person:

- **First visit vs. Nth visit**: is there instructional content that should hide after the first session?
- **Session state**: does the tool remember where you left off? (last tab, last selection, scroll position)
- **Viewport budget**: is the most-used content above the fold without scrolling?
- **Navigation memory**: can you deep-link to specific views? Does the URL reflect state?
- **Context preservation**: when the user navigates away and back, is their position preserved?

### Step 8: Produce Report

```markdown
## Design & Journey Review: [Component/Flow]

### Summary
[2-3 sentences: aesthetic coherence, biggest design opportunity, workflow assessment]

### Aesthetic Identity
[What is it? Does it commit? Score /10]

### Color System
| Aspect | Assessment | Issue (if any) |
|--------|-----------|----------------|
| Layer depth | | |
| Semantic colors | | |
| Phase/identifier colors | | |
| Theme adaptation | | |

### Typography
| Element | Size | Weight | Assessment |
|---------|------|--------|------------|
| [primary identifier] | | | |
| [body text] | | | |
| [smallest text] | | | |
| [most actionable text] | | | |

### Density Assessment
| Element | Space | Daily Value | Verdict |
|---------|-------|-------------|---------|
| [name] | | | |

### Visual Hierarchy Issues
- [ ] [Finding + recommendation]

### User Journey
**Golden path**: [steps → time → friction]

| Stage | Goal | Friction | Opportunity |
|-------|------|----------|-------------|
| [name] | | | |

### Daily-Driver Findings
- [ ] [Finding + recommendation]

### Distinctive Elements (Preserve These)
- [What's working well and should not be changed]

### Prioritized Recommendations

#### High Impact
1. [recommendation]

#### Medium Impact
1. [recommendation]

#### Enhancement
1. [recommendation]
```

## Principles

- **Aesthetic identity must be committed.** Mixed metaphors (enterprise cards + terminal monospace + marketing gradients) signal design debt.
- **Color collisions are bugs.** If an identifier color is indistinguishable from a semantic color at operational sizes, it misleads.
- **Type size correlates with importance.** If the most actionable text is the smallest, the hierarchy is inverted.
- **Viewport space is finite and expensive.** Every element must earn its position through daily-use value, not one-time instructional value.
- **The golden path defines the layout.** The most-frequent workflow should require zero scrolling, zero extra clicks, zero context switches.
- **Expert users outgrow onboarding.** Instructional content should collapse, hide, or shrink after the first few sessions.
- **Density is not clutter.** Data-dense dashboards for expert users should be tight. The problem is density inversions, not density itself.
- **Don't propose what you can't see.** If you can't articulate what the current aesthetic IS, you can't assess whether a change fits.
