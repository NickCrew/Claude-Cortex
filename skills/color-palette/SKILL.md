---
name: color-palette
description: 'Use this skill when creating, evaluating, or documenting color palettes for brands, products, or design systems. Trigger phrases: ''create a color palette'', ''what colors should I use'', ''brand colors for'', ''accessible color scheme''. Do NOT use for image editing, photo color correction, or print production color matching.'
version: 1.0.0
author: community
tags:
  - design
  - color
  - palette
  - accessibility
  - branding
license: MIT
keywords:
  - color palette
  - brand colors
  - color system
  - WCAG contrast
  - color
  - palette
---

# Color Palette

## Overview
This skill helps you create purposeful, accessible, and cohesive color palettes for digital products and brands. Color is one of the highest-leverage design decisions you can make—it communicates brand personality, guides user attention, conveys meaning, and determines whether your product is usable by people with visual impairments. This skill covers brand palette creation, semantic color systems (primary, secondary, neutral, semantic), accessibility validation against WCAG standards, and design token documentation. The output is a structured, ready-to-use color system, not a mood board.

## When to Use
- Creating a color palette for a new brand, product, or design system
- Extending an existing brand palette for digital use
- Auditing an existing palette for accessibility issues
- Defining semantic color roles (primary, danger, success, warning, neutral)
- Generating color token documentation for developer handoff
- Choosing colors for a specific context (dark mode, data visualization, illustration)

## When NOT to Use
- Photo editing or color grading (use dedicated image editing tools)
- Print production color matching (CMYK and Pantone matching requires specialized tools)
- Interior design or physical product color specification
- Fashion or textile color selection

## Quick Reference
| Task | Approach |
|------|----------|
| Brand palette | Start with 1 primary hue, add 1–2 accent hues, build neutrals |
| Accessibility | Text on background must meet 4.5:1 (AA) or 7:1 (AAA) contrast ratio |
| Semantic colors | Map roles: primary, secondary, success (#22c55e range), warning (#f59e0b range), danger (#ef4444 range) |
| Neutral scale | Generate 9–11 shades (50–950) from near-white to near-black |
| Dark mode | Don't invert; remap semantic roles to dark-optimized values |
| Data viz | Use categorical (distinct hues) or sequential (single hue, varying lightness) palettes |
| Token naming | Use semantic names: `color.brand.primary`, `color.feedback.error`, not hex values |
| Tints and shades | Generate 9 steps per color; 500 = base, 100 = lightest, 900 = darkest |

## Instructions

1. **Gather brand context before choosing any color.** Identify: industry, audience, competitors, brand personality keywords (e.g., "trustworthy, modern, approachable"), any existing brand colors that must be retained, and primary use case (web app, marketing site, mobile app). Color choices must serve the brand, not just look nice in isolation.

2. **Choose the primary hue strategically.** One hue anchors the entire system. Consider industry conventions (blue for trust/tech, green for health/finance, orange for energy/creativity), then differentiate. Generate a full 9-step scale for the primary hue (50, 100, 200, 300, 400, 500, 600, 700, 800, 900). The 500 step is typically the base brand color; 600–700 are used for hover and interactive states.

3. **Add secondary and accent colors with intention.** Secondary colors extend the palette for components, illustrations, and charts. Use color theory to select harmonious relationships: analogous (adjacent hues), complementary (opposite hues), or triadic (three evenly spaced hues). Limit to 1–2 secondary hues to avoid visual noise.

4. **Build the neutral scale.** Neutrals carry the most visual weight in a digital product (backgrounds, text, borders, dividers). Generate 9–11 steps from near-white to near-black. Slightly warm or cool the neutrals to complement your primary hue — pure gray often feels sterile.

5. **Define semantic color roles.** Map functional meaning to colors: primary (brand actions), secondary (alternative actions), success (completion, positive), warning (caution, needs attention), danger/error (destructive actions, failures), info (neutral information). Each semantic role needs a background, text, and border value at minimum.

6. **Validate all combinations against WCAG accessibility standards.** Every color combination used for text must meet WCAG 2.1 AA (4.5:1 contrast ratio for normal text, 3:1 for large text ≥18pt or 14pt bold). UI components and focus indicators must meet 3:1 against adjacent colors. Document the passing and failing combinations explicitly.

7. **Plan for dark mode if required.** Dark mode is not an inversion of the light palette. Remap your semantic tokens to dark-optimized values: reduce saturation on large surfaces, use lighter neutrals for text, and ensure the same contrast ratios hold. Background levels in dark mode typically use 900, 800, 700 steps rather than white.

8. **Document as design tokens.** Name every color using semantic, role-based names rather than descriptive names. `color.brand.primary.500` is better than `blue-medium`. Provide hex, RGB, and HSL values. Group tokens by category: brand, semantic/feedback, neutral, data visualization.

## Examples

### Example 1: SaaS Product Color Palette — FinTech App

**Input:** "Create a color palette for a fintech budgeting app called 'Vault'. Brand personality: trustworthy, calm, modern. Target users: millennials managing personal finances. Must be accessible."

**Output:**

#### Brand Strategy
Vault needs to signal financial trustworthiness (blue family) while feeling modern and approachable rather than cold and corporate. Primary: a confident teal-blue. Neutrals: cool-gray with a slight blue cast. Accents: a muted green for positive financial states, a warm amber for warnings.

#### Primary Palette — Vault Blue

| Token | Hex | Use |
|-------|-----|-----|
| `brand.primary.50` | `#eff6ff` | Light backgrounds, hover states |
| `brand.primary.100` | `#dbeafe` | Tinted surface backgrounds |
| `brand.primary.200` | `#bfdbfe` | Borders, dividers on tinted surfaces |
| `brand.primary.400` | `#60a5fa` | Icons, secondary interactive |
| `brand.primary.500` | `#2563eb` | **Base brand color** |
| `brand.primary.600` | `#1d4ed8` | Button hover, active states |
| `brand.primary.700` | `#1e40af` | Pressed states, emphasis |
| `brand.primary.900` | `#1e3a8a` | Dark text on light backgrounds |

#### Semantic Colors

| Role | Hex | Contrast on white | Use |
|------|-----|-------------------|-----|
| Success | `#16a34a` | 5.1:1 ✅ AA | Positive balance, completed goals |
| Warning | `#d97706` | 4.6:1 ✅ AA | Upcoming bills, low balance |
| Danger | `#dc2626` | 5.8:1 ✅ AA | Overspent, failed transaction |
| Info | `#0284c7` | 4.7:1 ✅ AA | Tips, informational messages |

#### Neutral Scale — Cool Gray

| Token | Hex | Use |
|-------|-----|-----|
| `neutral.50` | `#f8fafc` | App background |
| `neutral.100` | `#f1f5f9` | Card backgrounds |
| `neutral.200` | `#e2e8f0` | Borders, dividers |
| `neutral.400` | `#94a3b8` | Placeholder text, icons |
| `neutral.600` | `#475569` | Secondary body text |
| `neutral.800` | `#1e293b` | **Primary body text** — 16.7:1 on white ✅ AAA |
| `neutral.900` | `#0f172a` | Headings, high-emphasis text |

#### Accessibility Validation

| Combination | Contrast | WCAG |
|-------------|----------|------|
| `neutral.800` on `neutral.50` | 16.7:1 | ✅ AAA |
| `brand.primary.500` on white | 5.1:1 | ✅ AA |
| `brand.primary.600` on white | 6.4:1 | ✅ AA |
| White on `brand.primary.500` | 5.1:1 | ✅ AA (large text) |
| `neutral.400` on white | 2.5:1 | ❌ Fail — use only for decorative, non-essential elements |

---

### Example 2: Accessible Color Scheme Audit — Existing Palette

**Input:** "Audit this color palette for accessibility. Primary: #7c3aed (purple), Secondary: #f472b6 (pink), Text: #6b7280 (gray), Background: #ffffff (white), Error: #ef4444 (red). Fix any failures."

**Output:**

#### Audit Results

| Combination | Contrast | Result | Fix Required? |
|-------------|----------|--------|---------------|
| Text `#6b7280` on white | 4.1:1 | ❌ Fails AA (needs 4.5:1) | Yes |
| Primary `#7c3aed` on white | 5.9:1 | ✅ AA Pass | No |
| White on Primary `#7c3aed` | 5.9:1 | ✅ AA Pass | No |
| Secondary `#f472b6` on white | 2.5:1 | ❌ Fails AA | Yes |
| White on Error `#ef4444` | 4.1:1 | ❌ Fails AA | Yes |
| Error `#ef4444` on white | 4.1:1 | ❌ Fails AA | Yes |

#### Fixes

**Body text:** Change `#6b7280` → `#4b5563`
- New contrast on white: 7.0:1 ✅ AAA
- Still matches the cool-gray family

**Secondary (pink):** `#f472b6` is too light for text use. Reserve for decorative elements only. For text or interactive use, use `#be185d` (5.0:1 ✅ AA) instead.

**Error color:** Change `#ef4444` → `#dc2626`
- White text on `#dc2626`: 5.8:1 ✅ AA
- `#dc2626` on white: 5.8:1 ✅ AA
- Visually imperceptible change; functionally significant improvement

#### Updated Palette Summary

| Role | Old | New | Status |
|------|-----|-----|--------|
| Primary | `#7c3aed` | `#7c3aed` | ✅ No change |
| Secondary (interactive) | `#f472b6` | `#be185d` | 🔄 Updated |
| Body text | `#6b7280` | `#4b5563` | 🔄 Updated |
| Error | `#ef4444` | `#dc2626` | 🔄 Updated |

---

## Best Practices
- Always validate colors in context — a color that passes in isolation may fail on a colored background
- Generate the full neutral scale before choosing accent colors; neutrals set the tone for everything
- Use HSL to build scales: keep hue and saturation constant, vary lightness systematically
- Reserve your brightest, most saturated colors for the smallest, most important elements (primary buttons, alerts)
- Test your palette in grayscale — if the hierarchy disappears, you're relying too much on hue alone
- Document every token with its use case, not just its value

## Common Mistakes
- **Using brand colors for body text without checking contrast:** Brand blue looks great in logos; it often fails WCAG on white backgrounds
- **Too many accent colors:** More than 3–4 distinct hues creates visual chaos; reduce and consolidate
- **Building dark mode by inverting the light palette:** Dark surfaces need desaturated, warm-shifted colors — pure inverted colors look harsh
- **Naming colors descriptively:** "light-blue-2" is meaningless to a developer. Use semantic names: `color.brand.primary.200`
- **Forgetting color-blind users:** ~8% of men have color vision deficiency; never use red/green alone to convey pass/fail
- **One shade per color:** A single brand blue with no scale means designers invent ad-hoc variations — always build the full scale

## Tips & Tricks
- Start with the neutral scale — it's the unsung hero of every great product palette
- Use Oklch or HSLuv color spaces for perceptually uniform scales (same lightness = same perceived brightness)
- The 500 step is your base; 400 is for hover, 600 is for pressed, 700 is for text — this pattern works reliably
- When in doubt about contrast, use the WebAIM Contrast Checker or Figma's built-in accessibility tools
- Color temperature affects mood: warm neutrals (slight yellow/red cast) feel friendly; cool neutrals (slight blue cast) feel precise and professional
- For data visualization palettes, use ColorBrewer's schemes — they're designed and tested for perceptual distinctiveness

## Related Skills
- [design-critiquer](../design-critiquer/SKILL.md)
- [frontend-design](../frontend-design/SKILL.md)
- [ux-writer](../ux-writer/SKILL.md)
