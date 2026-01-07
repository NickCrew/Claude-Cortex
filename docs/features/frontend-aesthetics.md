---
layout: default
title: Frontend Aesthetics
nav_order: 11
---

# Frontend Aesthetics & Design

**New in January 2026** – Generate high-quality, non-generic UI designs.

Cortex now includes a specialized skill and command set to overcome "AI slop" (generic, safe designs like purple gradients and standard fonts) and enforce modern, distinctive aesthetics.

## The `/design:ui` Command

Use the slash command to generate UI code:

```bash
/design:ui "A dashboard for renewable energy monitoring"
```

This command acts as a **thin wrapper** around the `ui-design-aesthetics` skill, enforcing a rigorous workflow:

1.  **Analyze**: Understand the user's goal.
2.  **Select Aesthetic**: Choose a cohesive theme (e.g., Swiss Style, Neo-Brutalism, Solarpunk).
3.  **Architect**: Plan for performance (Dynamic Loading, Progressive Disclosure).
4.  **Implement**: Generate self-contained, runnable code.

## The `ui-design-aesthetics` Skill

This skill (`skills/ui-design-aesthetics`) encapsulates the best practices for modern UI engineering.

### Core Capabilities

*   **Aesthetic Direction**: Enforces distinctive typography (JetBrains Mono, Playfair Display) and bold color choices.
*   **Performance Architecture**: Mandates **Progressive Disclosure**. Components must load dynamically (lazy load, interaction-based) to minimize initial payload.
*   **API Contract Validation**: Ensures frontend components align with backend data structures (Zod schemas).

### Guidelines

The skill strictly follows these reference guides:

*   **Aesthetics**: Avoid Inter/Roboto. Use extreme font weights (100/900). Create depth with layered gradients/noise.
*   **Motion**: Use CSS-only animations. Choreograph page loads with staggered reveals.
*   **Performance**: Optimize for LCP < 2.5s and FID < 100ms. Use Optimistic UI for latency.

## Usage Example

**User:** "Build a settings page."

**Cortex (/design:ui):**
1.  **Activates Skill**: `ui-design-aesthetics`
2.  **Plan**: "I will use a **Swiss Style** aesthetic with high-contrast typography. The heavy 'Account History' table will be **lazy-loaded** only when the user clicks that tab."
3.  **Code**: Generates React components with `React.lazy`, `Suspense`, and Tailwind utility classes for the specific design system.
