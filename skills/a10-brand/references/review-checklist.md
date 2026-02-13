# A10 Brand Review Checklist — Expanded

Use this checklist when auditing any visual output for A10 brand compliance. Work through each
section and report findings grouped by severity.

---

## Critical (Must Fix)

These violations make the output instantly recognizable as "not A10." Fix before shipping.

### Shape & Geometry
- [ ] No rounded corners on buttons (`border-radius: 0`)
- [ ] No rounded corners on cards
- [ ] No rounded corners on form inputs
- [ ] No rounded corners on badges/tags
- [ ] No rounded corners on images/containers
- [ ] No rounded corners on tooltips/modals
- [ ] No slanted/angled button edges
- [ ] No pill-shaped elements

### Typography
- [ ] Rubik font loaded via Google Fonts
- [ ] Rubik actually rendering (not falling back to system font)
- [ ] H1-H4 using Light weight (300), NOT Bold or Regular
- [ ] No Bold headlines (only Light 300 for H1-H4)
- [ ] No Comic Sans, Papyrus, or novelty fonts (obviously)

### Color
- [ ] All prominent colors from A10 brand palette
- [ ] No off-brand blues (watch for Tailwind blue-500/600, Bootstrap blue, Material blue)
- [ ] Magenta NOT used as a background color
- [ ] Magenta NOT dominant (should be ≤8% of color presence)
- [ ] Logo displayed in approved colors only (A10 Blue, Navy, White, or Black)
- [ ] Logo NOT on accent-colored backgrounds

### Accessibility
- [ ] Text contrast meets WCAG 2.1 AA (4.5:1 normal, 3:1 large)
- [ ] No light text on light backgrounds
- [ ] No dark text on dark backgrounds
- [ ] Interactive elements have visible focus states

---

## Major (Should Fix)

These issues are noticeable to someone familiar with the brand. Fix for polish.

### Buttons
- [ ] Primary button height: 56px
- [ ] Outlined button height: 48px
- [ ] Secondary button height: 40px
- [ ] Correct padding per size (32px / 24px / 20px horizontal)
- [ ] Title Case labels ("Learn More" not "LEARN MORE")
- [ ] Hover states present and using correct dark/light variants
- [ ] Blue button hover: `#004189` (light) or `#7CBAFF` (dark)
- [ ] Magenta button hover: `#A01B72`

### Font Weights
- [ ] Body text: Regular 400
- [ ] Buttons/navigation: Medium 500
- [ ] Links: SemiBold 600
- [ ] Eyebrows: Bold 700, ALL-CAPS, letter-spacing 0.1em
- [ ] No Bold (700) used for headlines or body

### Color Proportions
- [ ] Blues (Navy + A10 Blue) dominate the color landscape
- [ ] White used appropriately (backgrounds, text on dark)
- [ ] Accent colors (Purple, Orange, Cloud Blue, Green, Red) limited to data/status
- [ ] Accent colors NOT used for backgrounds or large decorative areas
- [ ] Sky Blue used as secondary, not competing with A10 Blue for primary
- [ ] Overall proportion feels: 80% primary / 15% secondary / 5% accent

### Charts & Data Viz
- [ ] Value labels on every bar/data point
- [ ] Grid lines dashed (not solid) at low opacity
- [ ] Gradient fills (not flat solid fills) on bars
- [ ] No rounded corners on chart bars
- [ ] Series colors follow priority order (Blue → Sky → Green → Orange → Red...)
- [ ] Chart title in Light 300 with subtitle in Regular 400
- [ ] Rubik font used for all chart text

### Typography Rules
- [ ] Ragged-right alignment (no justified text)
- [ ] No ALL-CAPS except eyebrows/small labels
- [ ] No hyphenation
- [ ] "A10 Networks" kept on same line (not breaking across lines)
- [ ] Body line-height: 24px (1.5)
- [ ] Reasonable line length (60-80 characters)

### Theme Consistency
- [ ] Light theme: white/gray backgrounds with navy text
- [ ] Dark theme: navy/black backgrounds with light text and sky-blue links
- [ ] Not mixing light and dark theme elements inconsistently
- [ ] Links using correct theme color (`#0057B7` light, `#529EEC` dark)

---

## Minor (Polish)

These are the details that separate good from great.

### Spacing
- [ ] Using the scale: 4 / 8 / 16 / 24 / 32 / 48 / 64px
- [ ] Consistent padding across similar elements
- [ ] Generous whitespace (not cramped)
- [ ] Card padding: 24px
- [ ] Section padding: 48-64px vertical

### Layout
- [ ] Section backgrounds alternating (White → Light Gray → Navy → Blue)
- [ ] No visible borders between sections (color change = separation)
- [ ] Cards using subtle box-shadow (not borders)
- [ ] Hero section has diagonal split opportunity utilized

### Icons
- [ ] Consistent sizing across icon set
- [ ] Colored with brand palette only
- [ ] Clean lines, no drop shadows
- [ ] No gradients unless from approved gradient set

### Links
- [ ] SemiBold 600 weight
- [ ] Correct color per theme
- [ ] Hover color change present
- [ ] Arrow suffix (" >") where appropriate

### Charts (Detail)
- [ ] Subtitle with temporal/contextual info
- [ ] Hover states with opacity transition
- [ ] Legend markers are squares (not circles)
- [ ] Value labels formatted (X.Xk for thousands)
- [ ] Left/top highlight edge on bars (rgba white 0.12)
- [ ] Base opacity 0.9, hover 1.0

### Eyebrows
- [ ] Letter-spacing: 0.1em
- [ ] Font-size: 16px
- [ ] Bold 700 weight
- [ ] ALL-CAPS

---

## Spirit Check

Beyond mechanical compliance, does the output embody the A10 brand personality?

### Confidence
- [ ] Clear visual hierarchy — one focal point per section
- [ ] Decisive color choices (not timid or washed out)
- [ ] Headlines feel authoritative yet elegant (Light 300 does this)
- [ ] CTAs are prominent and unambiguous

### Cleanliness
- [ ] Whitespace is generous, not cramped
- [ ] No visual clutter or competing focal points
- [ ] Information density is appropriate for the medium
- [ ] Grid alignment is consistent

### Engineering Aesthetic
- [ ] Feels precise and intentional
- [ ] Every element serves a purpose
- [ ] No decorative elements without function
- [ ] Data presentation is clear and well-labeled

### Brand Cohesion
- [ ] Would this look at home next to a10networks.com?
- [ ] Color balance feels like "a page from the same book" as other A10 materials
- [ ] Typography creates the signature "lightweight elegance"
- [ ] The diagonal energy / sharp-edge identity is present where appropriate

### Common Off-Brand Patterns to Watch For
- [ ] Tailwind defaults — rounded-lg, blue-500, gray-200 backgrounds
- [ ] Bootstrap defaults — rounded buttons, card-body padding, #007bff blue
- [ ] Material defaults — rounded corners, elevation shadows, Roboto font
- [ ] Generic "AI slop" — purple gradients, Inter font, excessive rounded corners
- [ ] Stock photography clichés — handshakes, puzzle pieces, hooded hackers

---

## Reporting Format

When reporting audit results, structure as:

### 🔴 Critical Issues (X found)
For each: what's wrong, where, exact fix (with hex codes, CSS props, font weights)

### 🟡 Major Issues (X found)
For each: what's wrong, where, recommended fix

### 🔵 Minor Issues (X found)
For each: what could be improved, suggested approach

### ✅ Brand Spirit Assessment
2-3 sentences on overall brand alignment, calling out what works well and what feels off.
