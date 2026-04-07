---
name: design-critiquer
description: "Use this skill when reviewing, evaluating, or giving structured feedback on UI designs, wireframes, mockups, or design systems. Trigger phrases: 'critique this design', 'give feedback on my UI', 'review this wireframe', 'what's wrong with this design'. Do NOT use for writing code, implementing designs, or marketing material critique."
version: 1.0.0
author: community
tags: [design, critique, ux, ui, feedback]
license: MIT
---

# Design Critiquer

## Overview
This skill provides structured, actionable design critiques grounded in UX principles, visual design fundamentals, and usability heuristics. A good design critique is not a list of personal preferences—it connects observations to user impact and business outcomes. This skill helps you evaluate designs across key dimensions: usability, hierarchy, accessibility, consistency, and clarity. Whether you are reviewing a lo-fi wireframe or a polished high-fidelity mockup, the output is prioritized, constructive feedback that the designer can act on immediately.

## When to Use
- Reviewing wireframes, mockups, or prototypes before development
- Running a design critique session or design review meeting
- Evaluating a redesign against the existing product for regression
- Auditing a live UI for usability and accessibility improvements
- Peer-reviewing a teammate's design work
- Self-critiquing your own design before presenting it

## When NOT to Use
- Writing or implementing code (use `frontend-design` skill instead)
- Creating marketing materials or campaign assets — different discipline
- Evaluating brand identity at a strategic level (brand strategy is a separate domain)
- Legal or compliance review of design assets
- Performance profiling or technical evaluation of a front-end implementation

## Quick Reference
| Task | Approach |
|------|----------|
| First pass | Evaluate from the user's perspective before looking at individual elements |
| Hierarchy | Check: can you read the page in 5 seconds and know what to do? |
| Accessibility | Contrast ratios (4.5:1 text, 3:1 UI), touch targets (44×44px min), focus order |
| Consistency | Same element, same style everywhere — spot deviations from the design system |
| Usability heuristics | Apply Nielsen's 10: visibility, feedback, control, standards, error prevention, etc. |
| Prioritization | Sev 1 (blocks users) → Sev 2 (frustrates users) → Sev 3 (polish/preference) |
| Tone | Critique the design, not the designer; lead with impact, not judgment |
| Positive feedback | Name what works and why — it's as actionable as what doesn't |

## Instructions

1. **Understand the context before critiquing.** Identify: What is this screen trying to accomplish? Who is the user? What stage of the design is this (wireframe vs. polished mockup)? Calibrate the depth of your critique to the fidelity—pixel-perfect feedback on a wireframe wastes everyone's time.

2. **Do a five-second first impression.** Look at the design for five seconds, then look away and answer: What is this page for? What is the primary action? What did my eye go to first? If these are unclear, the hierarchy needs work—this is your most important finding.

3. **Evaluate visual hierarchy and layout.** Check whether size, color, weight, and whitespace guide the eye through the intended reading order. The primary action should be visually dominant. Group related elements. Ensure spacing is consistent and intentional, not random.

4. **Apply Nielsen's usability heuristics.** Systematically check the top relevant heuristics: (1) Visibility of system status, (2) Match between system and real world, (3) User control and freedom, (4) Consistency and standards, (5) Error prevention, (6) Recognition over recall, (7) Flexibility and efficiency, (8) Aesthetic and minimalist design, (9) Error recovery, (10) Help and documentation.

5. **Check accessibility fundamentals.** Verify text contrast meets WCAG AA (4.5:1 for normal text, 3:1 for large text). Confirm interactive elements are at least 44×44px for touch. Check that the design communicates information through more than color alone. Identify any content that depends on hover states with no keyboard equivalent.

6. **Assess consistency with the design system.** Identify any components, spacing, typography, or color values that deviate from established patterns. Inconsistencies erode trust and make the product feel unpolished—even when users can't articulate why.

7. **Prioritize feedback by severity.** Classify every finding: Severity 1 = blocks task completion or causes errors, Severity 2 = creates confusion or frustration, Severity 3 = polish and preference. Lead with Sev 1 findings. Clearly separate preference from principle.

8. **Frame feedback constructively.** Use the format: **Observation → Impact → Suggestion.** "The primary button and secondary button have the same visual weight [observation], which makes it unclear which action to take [impact]. Consider making the primary action visually dominant with a filled style and reserving the outline style for secondary actions [suggestion]."

## Examples

### Example 1: E-Commerce Checkout Screen Critique

**Input:** "Critique this checkout screen. It has: a large product image on the left, a form on the right with fields for name/email/address/card number, a 'Place order' button at the bottom, and a small security badge in the footer. Users are abandoning at this step."

**Output:**

#### Five-Second Test Result
The layout is clear — it reads as a checkout form. However, the primary action ("Place order") is buried at the bottom, requiring a scroll most mobile users won't complete.

#### Severity 1 — Blocks Completion

**Button placement and visibility**
The "Place order" CTA is below the fold on mobile. Users who don't scroll never see it. Move the button directly below the last form field, or add a sticky CTA at the bottom of the viewport on mobile.

**Form field order**
Asking for card details before confirming the order summary creates anxiety. Show an order summary (items, total, shipping cost) before payment fields. Users need to confirm what they're paying before they trust you with payment details.

#### Severity 2 — Frustrates Users

**Security badge placement**
The security badge is in the footer, after the payment form — where users least expect it. Place trust signals (SSL lock icon, accepted card logos, "Secure checkout" language) directly adjacent to the card number field, where purchase anxiety peaks.

**No inline validation**
Card number and email errors appear only after submit. Add real-time validation (confirm email format, format card numbers with spaces as users type). Errors at submit feel punishing; errors in the moment feel helpful.

**Field labels vs. placeholders**
If labels disappear when typing begins (placeholder-only pattern), users lose context mid-form. Use persistent floating labels or label-above-field patterns.

#### Severity 3 — Polish

**Product image size**
The large product image on the left takes significant real estate. At checkout, the user has already decided to buy — a smaller image or order summary card serves them better. Consider converting this space to a concise order summary instead.

#### What Works Well
- Single-column form on the right provides a clear linear path
- "Place order" button label is specific and clear — better than "Submit" or "Continue"

---

### Example 2: Dashboard Wireframe Critique

**Input:** "Review this dashboard wireframe for a SaaS analytics tool. It shows: a left sidebar with 12 nav items, a top bar with username and settings icon, a main area with 8 metric cards in a 4x2 grid, and a large line chart below. Users say it feels overwhelming."

**Output:**

#### First Impression
The layout signals "analytics tool" immediately, which is good. But 12 sidebar items and 8 metric cards compete equally for attention — there is no clear starting point. Users feeling overwhelmed is a direct symptom of missing hierarchy.

#### Severity 1 — Blocks Effective Use

**Navigation overload**
12 top-level nav items exceeds the cognitive limit for scannable menus (~7 items). Group related items under collapsible sections or move secondary items into a settings area. Consider which 5–7 items represent 80% of user journeys and elevate those.

**No primary metric**
All 8 metric cards are the same size and weight. Users don't know which number matters most. Identify the 1–2 KPIs that define success and make them visually larger or differently styled. This also gives new users an onboarding anchor.

#### Severity 2 — Frustrates Users

**Chart with no context**
The large line chart shows a trend but (in the wireframe) has no date range selector, no comparison period, and no annotation for significant events. A chart without context is noise. Add: a date range control, a comparison toggle ("vs. previous period"), and a baseline reference line.

**Metric card density**
Eight metrics above the chart pushes the chart below the fold on typical laptop screens. Consider a "key metrics" row of 3–4 metrics, with the remaining metrics accessible in a secondary panel or drill-down.

#### Severity 3 — Polish

**Top bar real estate**
The top bar shows only username and settings. Consider adding a search bar (speeds up navigation for power users) and a notification bell (keeps users in context without breaking flow).

#### Structural Recommendation
Apply progressive disclosure: show the most important 3 metrics prominently, the trend chart below, and offer "View all metrics" to expand. This reduces the visual noise without removing any data.

#### What Works Well
- Left sidebar with persistent navigation is the right pattern for a tool users visit daily
- The 4x2 card grid is clean and extendable — the pattern is good, the content priority needs work

---

## Best Practices
- Always lead with what the design is trying to accomplish — critique without context is noise
- Use the Observation → Impact → Suggestion format for every finding
- Separate your personal preferences from design principles explicitly
- Acknowledge what works — naming successes helps designers understand the pattern to repeat
- Prioritize findings; a list of 30 equal comments is as unhelpful as no comments
- Time-box your critique: 5-second test first, then systematic review — don't jump to details first

## Common Mistakes
- **Prescribing solutions without explaining the problem:** "Make the button blue" without explaining why leaves the designer no better off
- **Conflating preference with principle:** "I don't like this font" is not a critique; "This font renders poorly at small sizes on low-resolution screens" is
- **Ignoring context:** Critiquing a lo-fi wireframe for visual polish, or a polished mockup only on wireframe-level structure
- **All negatives:** A critique with zero positive observations fails to teach the designer what to keep
- **Missing the user:** Critiques that focus only on aesthetics without asking "can a real user accomplish their goal here?" miss the point of UX

## Tips & Tricks
- Walk through the design as a specific user persona, not as a designer — catch problems you'd otherwise skip
- Print or screenshot and annotate with numbered callouts; it's clearer than a bulleted list
- For controversial feedback, cite a principle or data point to depersonalize it: "WCAG 2.1 requires 4.5:1 contrast for this text size"
- Ask "What is this user feeling right now?" at each screen — emotion is a usability dimension
- The best critique ends with a clear "top 3 actions" summary so the designer knows exactly where to start

## Related Skills
- [ux-writer](../ux-writer/SKILL.md)
- [frontend-design](../frontend-design/SKILL.md)
- [color-palette](../color-palette/SKILL.md)
- [ux-researcher](../../research/ux-researcher/SKILL.md)
