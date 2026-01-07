---
name: Frontend Aesthetics
description: Guidelines for generating distinctive, high-quality, and non-generic UI designs.
tokens: 350
---

<frontend_aesthetics>
You tend to converge toward generic, "on distribution" outputs (e.g., "AI slop" with purple gradients and standard fonts). Avoid this. Make creative, distinctive frontends that surprise and delight.

**Typography:**
- **Avoid:** Generic fonts like Arial, Inter, Roboto, Open Sans, Lato, or system defaults.
- **Use:** Distinctive choices that signal quality.
    - *Code:* JetBrains Mono, Fira Code, Space Grotesk.
    - *Editorial:* Playfair Display, Crimson Pro, Fraunces.
    - *Startup:* Clash Display, Satoshi, Cabinet Grotesk.
    - *Technical:* IBM Plex family, Source Sans 3.
- **Pairing:** High contrast is interesting (Display + Monospace, Serif + Geometric Sans). Use extreme weights (100 vs 900) rather than safe middles (400 vs 600).

**Color & Theme:**
- **Commit:** Choose a cohesive aesthetic (e.g., Solarpunk, Swiss Style, Brutalism, Neo-Brutalism, Glassmorphism).
- **Technique:** Use CSS variables for consistency.
- **Avoid:** The clichéd "white background with soft purple gradients."
- **Contrast:** Dominant colors with sharp accents outperform timid, evenly-distributed palettes.

**Motion:**
- **Prioritize:** CSS-only animations for performance and smoothness.
- **Impact:** Focus on a well-orchestrated page load with staggered reveals (`animation-delay`) rather than scattered micro-interactions.

**Backgrounds:**
- **Create Depth:** Use layered CSS gradients, noise textures, or geometric patterns.
- **Avoid:** Flat, solid colors that feel sterile.

**Implementation:**
- Use `tail-wind` utility classes or CSS variables to enforce the theme.
- Interpret requirements creatively. If asked for a "dashboard," don't just make a table; make a data visualization cockpit.
</frontend_aesthetics>
