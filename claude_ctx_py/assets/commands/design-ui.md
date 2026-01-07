---
name: "design:ui"
description: Generates high-quality UI designs by invoking the ui-design-aesthetics skill.
category: design
complexity: standard
agents:
  - react-specialist
  - tailwind-expert
---

# /design:ui — Skill-backed command


You are invoking the **UI Design & Aesthetics** skill.

**GOAL:** Design a beautiful, performant interface that adheres to the user's request.

**INSTRUCTIONS:**
1.  **Activate** the `ui-design-aesthetics` skill immediately.
2.  **Follow** the workflow defined in `skills/ui-design-aesthetics/SKILL.md`:
    *   **Aesthetics:** Reject generic defaults. Choose a specific theme (e.g., Swiss, Solarpunk).
    *   **Performance:** Implement **Progressive Disclosure**. Load components dynamically (lazy load, interaction-based).
    *   **Contracts:** Define Zod schemas for data.
3.  **Implement** the solution.

**Performance Constraints:**
- Minimize initial payload.
- Measure and state expected load times.
- Ensure interaction latency is < 100ms (use optimistic UI).

**Output:**
- Self-contained, runnable code.
- Explicit notes on *why* specific aesthetic and performance choices were made.