# A11y Smoke Check

Run a fast, high-signal accessibility triage for a page, component, or PR. This is a lightweight check, not a full compliance audit.

## Requirements
$ARGUMENTS

## Quick Audit Steps

### 1) Automated Snapshot (Optional but recommended)
Pick one:
- `npx @axe-core/cli <url>`
- `npx pa11y <url> --standard WCAG2AA`
- Lighthouse Accessibility score (Chrome DevTools)

### 2) Keyboard Basics
- All interactive elements reachable via Tab
- Focus indicator always visible
- No keyboard traps
- Logical tab order
- Skip link works for long pages

### 3) Semantics and Labels
- Single, descriptive H1
- Logical heading order (no large jumps)
- Form inputs have visible labels or aria-label
- Buttons and links have clear names
- Images have meaningful alt text or empty alt for decorative

### 4) Visual Contrast
- Text contrast >= 4.5:1 (3:1 for large text)
- UI component contrast >= 3:1 (inputs, buttons, focus rings)

### 5) Motion and Updates
- Respects prefers-reduced-motion
- Dynamic updates announced (aria-live for status)

## Output Format
1. **Result**: Pass, Needs Fixes, or Escalate to Full Audit
2. **Findings**: Severity, location, and fix guidance
3. **Escalation**: If risk is high, recommend `accessibility-audit`

## Escalate to Full Audit When
- New or changed navigation
- Complex forms or authentication flows
- Custom widgets or advanced interactions
- Public releases or compliance requirements

## Notes
This smoke check targets WCAG 2.2 AA by default. If the compliance level differs, state it explicitly.
