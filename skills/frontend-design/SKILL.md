---
name: frontend-design
description: 'Use this skill when specifying, designing, or documenting UI components, layouts, and design systems for frontend implementation. Trigger phrases: ''design this UI component'', ''create a responsive layout'', ''spec the CSS for'', ''design system for''. Do NOT use for backend development, server-side logic, data engineering, or writing server code.'
version: 1.0.0
author: community
tags:
  - design
  - frontend
  - css
  - layout
  - responsive
  - components
license: MIT
keywords:
  - design UI
  - responsive layout
  - CSS spec
  - design system
  - frontend
  - frontend design
---

# Frontend Design

## Overview
This skill bridges the gap between visual design and frontend implementation. It produces precise, developer-ready specifications for UI components, responsive layouts, and design systems—including CSS custom properties, layout logic, spacing scales, component states, and interaction behaviors. Whether you are designing a single button component or specifying an entire design system, the output is implementation-ready: exact values, not vague descriptions. This skill is for designing and specifying the frontend; for writing the actual code, pair it with a coding skill.

## When to Use
- Specifying a UI component with all states (default, hover, focus, disabled, error)
- Designing a responsive page layout with breakpoints and grid logic
- Building or extending a design system with tokens, components, and patterns
- Converting a visual design brief into developer-ready CSS specifications
- Defining spacing, typography, and elevation scales for a product
- Designing interactive component behavior (animations, transitions, state changes)

## When NOT to Use
- Backend API design or server-side logic (use `api-designer` skill instead)
- Data engineering, databases, or infrastructure
- Writing actual production code (pair with a coding assistant for implementation)
- Marketing design or print layout
- Mobile native UI (iOS/Android have platform-specific patterns; this skill targets web)

## Quick Reference
| Task | Approach |
|------|----------|
| Spacing scale | 4px base unit: 4, 8, 12, 16, 24, 32, 48, 64, 96, 128 |
| Typography scale | 12, 14, 16 (base), 18, 20, 24, 30, 36, 48, 60, 72px |
| Breakpoints | Mobile: <640px, Tablet: 640–1024px, Desktop: >1024px (adjust for product) |
| Grid | 4-column mobile, 8-column tablet, 12-column desktop; 16–24px gutters |
| Component states | Always spec: default, hover, focus, active, disabled, loading, error |
| Elevation | 3–5 levels: flat, raised (2px), overlay (4–8px), modal (16px), tooltip (24px) |
| Focus ring | 2px offset, 2px width, brand primary color — never remove, only restyle |
| Transition | 150ms ease-out for micro-interactions; 250–300ms for larger state changes |

## Instructions

1. **Define the component or layout scope precisely.** Name the component, its purpose, and where it appears in the product. A "Button" spec covers all button variants across the app; a "Hero Section" spec covers one layout pattern. Clarify scope before specifying—ambiguity at this stage creates implementation inconsistencies later.

2. **Establish the design token foundation first.** Before specifying any component, confirm the token system: color tokens (brand, semantic, neutral scales), spacing scale (4px base unit recommended), typography scale (size, weight, line-height, letter-spacing per level), and border radius values. Components reference tokens, not raw values — this makes theming and design system updates tractable.

3. **Specify every component state.** For interactive components, document all states: default, hover, focus-visible, active/pressed, disabled, loading, and any error or validation states. For each state, specify: background color, text color, border color, shadow, cursor, and transition from previous state. Missing states become inconsistent implementations.

4. **Define layout with explicit grid and spacing logic.** Specify column count, gutter width, and margin at each breakpoint. Name layout regions (header, sidebar, main, footer). Define how the layout collapses across breakpoints — not just "it becomes mobile" but specifically which columns stack, what reorders, and what hides.

5. **Write CSS custom properties for every design token.** Use the `--` prefix convention. Group by category: `--color-brand-primary`, `--spacing-4`, `--font-size-base`, `--radius-md`, `--shadow-md`. Provide the actual values alongside the tokens. This makes the spec immediately usable by developers without translation.

6. **Specify responsive behavior explicitly.** For each breakpoint, document: font sizes, spacing adjustments, layout changes, and component variations (e.g., a desktop mega-menu becoming a mobile drawer). Use `min-width` breakpoints (mobile-first) as the default unless the project already uses a different convention.

7. **Document interaction and animation specs.** For every interactive state transition, specify: duration (ms), easing function, and which properties animate. For complex interactions (modals, drawers, tooltips), specify trigger, entrance animation, exit animation, and focus management behavior.

8. **Produce a component anatomy diagram or structured spec.** Label every sub-element of the component (container, icon, label, badge, etc.) with its token references. This eliminates ambiguity about which part of the spec applies to which element.

## Examples

### Example 1: Button Component Full Specification

**Input:** "Spec a button component for our design system. We have primary, secondary, and ghost variants. Sizes: small, medium, large. Must be accessible. We use a 4px spacing scale and our primary brand color is #2563eb."

**Output:**

#### Design Tokens (establish these first)

```css
/* Color tokens */
--color-brand-primary-500: #2563eb;
--color-brand-primary-600: #1d4ed8;
--color-brand-primary-700: #1e40af;
--color-brand-primary-100: #dbeafe;
--color-neutral-700: #374151;
--color-neutral-800: #1f2937;
--color-white: #ffffff;

/* Spacing */
--spacing-2: 4px;
--spacing-3: 6px;
--spacing-4: 8px;
--spacing-6: 12px;
--spacing-8: 16px;
--spacing-10: 20px;
--spacing-12: 24px;

/* Typography */
--font-size-sm: 14px;
--font-size-base: 16px;
--font-weight-medium: 500;
--line-height-tight: 1.25;

/* Shape */
--radius-md: 6px;

/* Transition */
--transition-fast: 150ms ease-out;
```

#### Size Scale

| Size | Height | Padding (H × V) | Font size | Icon size |
|------|--------|-----------------|-----------|-----------|
| Small (sm) | 32px | 12px × 8px | 14px | 14px |
| Medium (md) | 40px | 16px × 10px | 16px | 16px |
| Large (lg) | 48px | 20px × 12px | 16px | 18px |

#### Variant Specifications

##### Primary Button

| State | Background | Text | Border | Shadow |
|-------|-----------|------|--------|--------|
| Default | `--color-brand-primary-500` | white | none | none |
| Hover | `--color-brand-primary-600` | white | none | none |
| Focus-visible | `--color-brand-primary-500` | white | none | 0 0 0 2px white, 0 0 0 4px `--color-brand-primary-500` |
| Active | `--color-brand-primary-700` | white | none | none |
| Disabled | `--color-brand-primary-200` | `--color-brand-primary-400` | none | none |
| Loading | `--color-brand-primary-500` | transparent | none | none + spinner overlay |

##### Secondary Button

| State | Background | Text | Border |
|-------|-----------|------|--------|
| Default | white | `--color-brand-primary-500` | 1.5px solid `--color-brand-primary-500` |
| Hover | `--color-brand-primary-100` | `--color-brand-primary-600` | 1.5px solid `--color-brand-primary-600` |
| Focus-visible | white | `--color-brand-primary-500` | 1.5px solid + focus ring |
| Disabled | white | `--color-neutral-400` | 1.5px solid `--color-neutral-300` |

##### Ghost Button

| State | Background | Text | Border |
|-------|-----------|------|--------|
| Default | transparent | `--color-neutral-700` | none |
| Hover | `--color-neutral-100` | `--color-neutral-800` | none |
| Focus-visible | transparent | `--color-neutral-700` | focus ring |
| Disabled | transparent | `--color-neutral-400` | none |

#### Interaction Spec
- **Transition:** `background-color var(--transition-fast), border-color var(--transition-fast), box-shadow var(--transition-fast)`
- **Loading state:** Show spinner (16px, white, 1px stroke) centered in button; keep button width fixed; hide label text (or set opacity: 0 to maintain width)
- **Focus ring:** `outline: 2px solid var(--color-brand-primary-500); outline-offset: 2px` — never `outline: none` without replacement

#### Accessibility Requirements
- Role: `button` (native `<button>` preferred over `role="button"` on `<div>`)
- Disabled: use `disabled` attribute, not `aria-disabled` alone (removes from tab order correctly)
- Loading: add `aria-busy="true"` and `aria-label="Loading..."` when in loading state
- Icon-only buttons: require `aria-label` with the button's action

---

### Example 2: Responsive Dashboard Layout Specification

**Input:** "Design a responsive layout for a SaaS analytics dashboard. It needs: a collapsible left sidebar with navigation, a top header bar, and a main content area with a 3-column card grid. Must work on mobile, tablet, and desktop."

**Output:**

#### Layout Architecture

```
Desktop (>1024px):
┌─────────┬──────────────────────────────────────┐
│         │ Header (64px, full width)            │
│ Sidebar │──────────────────────────────────────│
│ (240px) │                                      │
│         │ Main Content Area                    │
│         │ (3-column card grid)                 │
│         │                                      │
└─────────┴──────────────────────────────────────┘

Tablet (640–1024px):
┌──────────────────────────────────────────────┐
│ Header (56px) + hamburger menu icon          │
├──────────────────────────────────────────────┤
│ Main Content (2-column card grid)            │
│ Sidebar: off-canvas drawer, opens on trigger │
└──────────────────────────────────────────────┘

Mobile (<640px):
┌──────────────────────────────────────────────┐
│ Header (52px) + hamburger menu icon          │
├──────────────────────────────────────────────┤
│ Main Content (1-column card grid)            │
│ Sidebar: full-width bottom sheet or drawer   │
└──────────────────────────────────────────────┘
```

#### CSS Custom Properties for Layout

```css
--sidebar-width: 240px;
--sidebar-collapsed-width: 64px;
--header-height-desktop: 64px;
--header-height-tablet: 56px;
--header-height-mobile: 52px;
--content-padding: 24px;
--content-padding-mobile: 16px;
--grid-gap: 16px;
--grid-gap-desktop: 24px;
```

#### Breakpoint Definitions

| Breakpoint | Token | Value | Grid columns | Card grid |
|------------|-------|-------|--------------|-----------|
| Mobile | `--bp-sm` | 0–639px | 4 col | 1 col |
| Tablet | `--bp-md` | 640–1023px | 8 col | 2 col |
| Desktop | `--bp-lg` | 1024px+ | 12 col | 3 col |
| Wide | `--bp-xl` | 1280px+ | 12 col | 3 col (wider cards) |

#### Sidebar Behavior

| State | Desktop | Tablet | Mobile |
|-------|---------|--------|--------|
| Default | Expanded (240px) | Hidden | Hidden |
| Collapsed | Icon-only (64px) | — | — |
| Open trigger | Toggle button in sidebar | Hamburger in header | Hamburger in header |
| Close trigger | Toggle button | Backdrop click, ESC | Backdrop click, ESC, swipe down |
| Transition | `width 200ms ease-in-out` | Slide in from left (250ms) | Slide in from left (250ms) |
| Backdrop | None | `rgba(0,0,0,0.4)` overlay | `rgba(0,0,0,0.4)` overlay |

#### Focus Management (Sidebar)
- When sidebar opens: focus moves to first focusable nav item
- When sidebar closes: focus returns to trigger (hamburger button)
- Sidebar traps focus while open on mobile/tablet (implement with focus trap library or `inert` attribute on main)

#### Card Grid Specification

```css
.card-grid {
  display: grid;
  grid-template-columns: repeat(1, 1fr);       /* mobile */
  gap: var(--grid-gap);
  padding: var(--content-padding-mobile);
}

@media (min-width: 640px) {
  .card-grid {
    grid-template-columns: repeat(2, 1fr);     /* tablet */
    padding: var(--content-padding);
    gap: var(--grid-gap);
  }
}

@media (min-width: 1024px) {
  .card-grid {
    grid-template-columns: repeat(3, 1fr);     /* desktop */
    gap: var(--grid-gap-desktop);
  }
}
```

#### Card Component Minimum Spec

- **Min height:** 120px
- **Padding:** 20px (desktop), 16px (mobile)
- **Border radius:** `--radius-lg` (8px)
- **Background:** `--color-white`
- **Border:** 1px solid `--color-neutral-200`
- **Shadow:** `0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.06)`
- **Hover shadow:** `0 4px 6px rgba(0,0,0,0.08), 0 2px 4px rgba(0,0,0,0.06)` — transition 150ms

---

## Best Practices
- Always spec from tokens, never raw values — one source of truth for every design decision
- Document every component state before implementation begins; missing states become technical debt
- Use mobile-first responsive design: start with the constrained mobile layout, progressively enhance
- Provide a spacing scale and stick to it — arbitrary spacing values are the enemy of visual consistency
- Write the focus state spec with the same care as the default state — keyboard users deserve the same experience
- Separate component structure (HTML/tokens) from visual style (CSS) in documentation to make implementation flexible

## Common Mistakes
- **Speccing the happy path only:** Missing disabled, loading, and error states creates inconsistent UIs
- **Unitless spacing:** "Some padding" or "a bit of margin" is unusable; always give exact token references or pixel values
- **Breakpoints based on device names:** "iPhone size" and "iPad size" change constantly; use content-based breakpoints
- **Removing focus outlines without replacement:** `outline: none` breaks keyboard navigation; always provide a styled alternative
- **Over-specifying too early:** Pixel-perfect specs for a wireframe-stage component waste time; match spec depth to design fidelity
- **Ignoring the grid:** Components designed in isolation often break when placed in the actual grid system

## Tips & Tricks
- Build your spacing scale in a spreadsheet first, then generate the CSS tokens — catching inconsistencies is easier in a table
- Use CSS logical properties (`margin-inline-start` instead of `margin-left`) for easier RTL support later
- For complex animations, spec using the FLIP technique mental model: define the start state, end state, and duration/easing
- Sticky headers and sidebars need scroll-padding-top specs for anchor navigation to work correctly
- Design your empty states and skeleton loaders as part of the component spec — they're often forgotten until after launch
- Container queries (`@container`) are now well-supported and often better than media queries for component-level responsive behavior

## Related Skills
- [ux-writer](../ux-writer/SKILL.md)
- [design-critiquer](../design-critiquer/SKILL.md)
- [color-palette](../color-palette/SKILL.md)
- [api-designer](../../engineering/api-designer/SKILL.md)
