# State Patterns and Micro-Interactions

Practical patterns for handling every UI state and designing micro-interactions that provide clear, consistent feedback.

## Loading States

### Skeleton Screens

Use when the layout is predictable and content takes > 300ms to load.

```
+----------------------------------+
| [████████████████]  (avatar)     |   <- grey placeholder shapes
| [████████████████████████]       |      mimic the final layout
| [█████████████]                  |
+----------------------------------+
```

**Guidelines**:
- Match the shape and position of real content.
- Animate with a subtle shimmer (left-to-right pulse).
- Replace progressively as data arrives; do not wait for everything.
- Avoid skeleton screens for actions that complete in < 300ms.

### Spinners

Use when the layout is unpredictable or the area is small.

| Context | Spinner Style | Placement |
|---------|--------------|-----------|
| Full page load | Centered overlay with optional message | Center of viewport |
| Inline action (button click) | Replace button label with spinner | Inside the button |
| Section refresh | Small spinner in section header | Inline with header |
| Background save | Subtle indicator in status bar | Top-right or status area |

**Guidelines**:
- Show a spinner after 200-300ms delay; avoid flash for fast responses.
- Pair with a message for waits > 2 seconds ("Loading your dashboard...").
- For waits > 5 seconds, add a progress indicator or explain the delay.

### Progress Bars

Use when you can estimate completion (file uploads, multi-step processes).

**Guidelines**:
- Show percentage or step count ("Step 2 of 4").
- Never let a progress bar go backward.
- Use indeterminate style only when you truly cannot estimate progress.
- Consider adding estimated time remaining for long operations (> 10 seconds).

---

## Empty States

Empty states are opportunities to guide users, not dead ends.

### Types

| Type | Trigger | Goal |
|------|---------|------|
| First-use empty | New user, no data yet | Educate and motivate first action |
| No results | Search or filter returns nothing | Help user adjust their query |
| Cleared data | User deleted or archived everything | Confirm action, suggest next step |
| Error empty | Data failed to load | Explain and offer retry |

### First-Use Empty State Template

```
[Illustration or icon relevant to the feature]

[Headline: Value proposition, not "Nothing here"]
[Subtext: Brief explanation of what this area does]

[Primary CTA: "Create your first ___"]
[Secondary: "Learn more" or "Import existing"]
```

**Good example**: "Track your team's progress. Create a project to get started."
**Bad example**: "No projects found."

### No Results Template

```
[Search icon or illustration]

No results for "[query]"

Try:
- Check spelling
- Use fewer keywords
- [Clear filters] button
```

---

## Error States

### Severity Levels

| Level | Visual Treatment | User Action Required |
|-------|-----------------|---------------------|
| **Info** | Blue/neutral banner, auto-dismiss | None |
| **Warning** | Yellow/amber, persistent until acknowledged | Optional adjustment |
| **Error** | Red, persistent, blocks progress | Required correction |
| **Critical** | Red overlay or page-level, blocks all interaction | Immediate action or support |

### Error Message Pattern

```
[What happened] + [Why it happened (if known)] + [What to do next]
```

**Good**: "Could not save your changes. The server is temporarily unavailable. Try again in a few minutes, or contact support if this persists."
**Bad**: "Error 500: Internal Server Error"

### Form Validation Errors

**Timing**:
- Validate on blur (when user leaves a field), not on every keystroke.
- Show inline errors next to the field, not in a summary at the top.
- For complex validations (server-side), validate on submit and scroll to the first error.

**Visual treatment**:
- Red border on the input field.
- Error message directly below the field in red text.
- Error icon inside the field (optional).
- Keep the error visible until the user corrects the input.

### Network Error Recovery

| Scenario | Pattern |
|----------|---------|
| Timeout | "This is taking longer than expected. [Retry] or [Cancel]" |
| Offline | "You're offline. Changes will sync when you reconnect." |
| Partial failure | "3 of 5 items saved. [Retry failed items]" |
| Auth expired | "Your session expired. [Sign in again] — your work is saved." |

---

## Success States

### Confirmation Patterns

| Action Type | Feedback | Duration |
|-------------|----------|----------|
| Minor (toggle, save) | Inline checkmark or toast | 2-3 seconds, auto-dismiss |
| Moderate (form submit) | Success banner with summary | Persistent until navigated away |
| Major (purchase, publish) | Dedicated confirmation page | Persistent |
| Destructive (delete) | "Undo" toast with timer | 5-10 seconds before permanent |

### Celebration Patterns

Reserve for meaningful milestones:
- Completing onboarding
- First successful action (first project, first deployment)
- Achievement thresholds

Keep subtle: a brief animation, a congratulatory message. Avoid blocking the user's next action.

---

## Micro-Interaction Design

### Button States

| State | Visual | Behavior |
|-------|--------|----------|
| **Default** | Standard styling | Clickable |
| **Hover** | Subtle highlight, slight scale (1.02) or color shift | Cursor changes to pointer |
| **Focus** | Visible focus ring (2px outline, offset) | Keyboard accessible |
| **Active/Pressed** | Slight inset or darker shade | Responds to click |
| **Loading** | Spinner replaces label, button disabled | Prevents double-submit |
| **Disabled** | Reduced opacity (0.5-0.6), no pointer cursor | Not interactive; tooltip explains why |
| **Success** | Brief checkmark animation, then return to default | Confirms action completed |

### Input Field States

| State | Visual |
|-------|--------|
| **Default** | Grey border |
| **Focus** | Blue/primary border, optional subtle shadow |
| **Filled** | Standard border, shows entered value |
| **Error** | Red border, error message below |
| **Disabled** | Grey background, reduced opacity |
| **Read-only** | No border, plain text appearance |

### Animation Guidelines

| Property | Duration | Easing |
|----------|----------|--------|
| Color/opacity changes | 150-200ms | ease-in-out |
| Scale/transform | 200-300ms | ease-out |
| Layout shifts (expand/collapse) | 250-350ms | ease-in-out |
| Page transitions | 300-400ms | ease-in-out |
| Complex sequences | 400-600ms | custom cubic-bezier |

**Principles**:
- Animations should feel responsive, not decorative. If removing an animation makes nothing worse, remove it.
- Respect `prefers-reduced-motion`: disable non-essential animations.
- Enter animations should be slightly faster than exit animations.
- Stagger list item animations by 30-50ms per item (max 5-7 items, then fade as group).

---

## Feedback Patterns

### Optimistic Updates

Show the result immediately, then confirm with the server. Roll back on failure.

**When to use**:
- Actions with high success rate (> 99%): likes, toggles, reorders.
- Low-risk actions where a brief inconsistency is acceptable.

**When to avoid**:
- Financial transactions, data deletion, permission changes.
- Actions where rollback would confuse the user.

**Implementation**:
1. Apply change to UI immediately.
2. Send request to server in background.
3. On success: do nothing (UI already correct).
4. On failure: revert UI, show error toast with retry option.

### Progressive Disclosure

Reveal complexity gradually as users need it.

**Levels**:
1. **Primary**: Always visible. The most common action or information.
2. **Secondary**: One click away. "Show advanced options" or an expand/collapse.
3. **Tertiary**: Behind a link, modal, or separate page. Rarely needed settings.

**Guidelines**:
- Default to the simplest view.
- Use clear labels that describe what will be revealed ("Advanced filters", not "More").
- Remember user preferences for expanded/collapsed state.
- Do not hide critical information behind disclosure.

### Toast Notifications

| Type | Duration | Dismissible | Position |
|------|----------|-------------|----------|
| Success | 3-5 seconds | Auto-dismiss | Bottom-right or top-center |
| Info | 5-7 seconds | Auto-dismiss + manual | Bottom-right or top-center |
| Warning | Persistent | Manual dismiss | Top-center |
| Error | Persistent | Manual dismiss | Top-center |
| Undo | 5-10 seconds (with countdown) | Manual dismiss | Bottom-center |

**Stacking**: Show max 3 toasts at once. Queue additional ones. Newest on top.

---

## Skeleton Screen Recipes

### Card List

```
+----------------------------------+
| [██]  [████████████]             |
|       [█████████████████]        |
|       [████████]                 |
+----------------------------------+
| [██]  [████████████]             |
|       [█████████████████]        |
|       [████████]                 |
+----------------------------------+
```

### Data Table

```
| [████████] | [████████] | [████████] |  <- header (static)
|------------|------------|------------|
| [████████] | [██████]   | [████]     |  <- shimmer rows
| [██████]   | [████████] | [██████]   |
| [████████] | [████]     | [████████] |
```

### Profile Page

```
+--------+  [████████████████]
|        |  [████████████████████████]
| [████] |  [█████████████]
|        |
+--------+  [████████████████████████████████]
             [██████████████████████████]
             [████████████████████]
```

Replace each section independently as its data loads.
