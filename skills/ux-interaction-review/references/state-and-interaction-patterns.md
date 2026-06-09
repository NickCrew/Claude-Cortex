# State Patterns & Interaction Specifications

Practical patterns for handling UI states and specifying interaction behavior.

## State Handling Patterns

### Loading States

| Context | Pattern | Threshold |
|---------|---------|-----------|
| Predictable layout | Skeleton screen | Show after 300ms |
| Unpredictable layout | Centered spinner | Show after 200ms |
| Inline action (button) | Spinner replaces label, button disabled | Immediate |
| Background save | Subtle status indicator | Immediate |
| Long operation (>5s) | Progress bar with estimate | Immediate |

**Rules:**
- Never show a spinner for operations completing in <200ms (flash avoidance)
- Pair with a message for waits >2s
- Show estimated time for operations >10s
- Replace progressively as data arrives; don't wait for everything

### Empty States

| Type | Goal | Pattern |
|------|------|---------|
| First-use | Educate, motivate first action | Illustration + value prop + CTA |
| No results | Help adjust query | Show query, suggest alternatives, offer "clear filters" |
| Cleared data | Confirm action | Brief confirmation + suggest next step |
| Error empty | Explain + offer retry | Error message + retry button + alternative path |

**Rules:**
- Never show just "No data." Always explain why and what to do next.
- First-use empty states are onboarding opportunities.
- No-results states should echo the search/filter that produced them.

### Error States

| Severity | Visual | Behavior |
|----------|--------|----------|
| Info | Blue/neutral banner | Auto-dismiss after 5s |
| Warning | Amber, persistent | Dismiss on acknowledgment |
| Error | Red, persistent, blocks progress | Required correction |
| Critical | Red overlay, blocks all interaction | Immediate action required |

**Error message formula:** `[What happened] + [Why (if known)] + [What to do next]`

**Network errors:**

| Scenario | Pattern |
|----------|---------|
| Timeout | "Taking longer than expected. [Retry] or [Cancel]" |
| Offline | "You're offline. Changes will sync when you reconnect." |
| Partial failure | "3 of 5 items saved. [Retry failed items]" |
| Auth expired | "Session expired. [Sign in again] -- your work is saved." |
| Clipboard denied | "Copy failed -- text selected, use Ctrl+C" |

### Success States

| Action Type | Feedback | Duration |
|-------------|----------|----------|
| Minor (toggle, copy) | Inline text change or checkmark | 2-3s auto-dismiss |
| Moderate (form submit) | Success banner with summary | Persistent until navigated |
| Major (deploy, publish) | Dedicated confirmation view | Persistent |
| Destructive (delete) | "Undo" toast with countdown | 5-10s before permanent |

---

## Micro-Interaction Specifications

### Button States

| State | Visual | Behavior |
|-------|--------|----------|
| Default | Standard styling | Clickable |
| Hover | Subtle highlight or scale(1.02) | Cursor: pointer |
| Active/Pressed | Slight inset or darker | Responds to click |
| Loading | Spinner replaces label, disabled | Prevents double-submit |
| Disabled | Opacity 0.5-0.6, no pointer | Not interactive |
| Success | Brief checkmark, then revert | Confirms completion |
| Cooldown | Temporarily disabled after action | Prevents rapid re-fire |

### Animation Timing Reference

| Property | Duration | Easing | Use |
|----------|----------|--------|-----|
| Color/opacity | 80-150ms | ease-in-out | Hover states, fade-in |
| Scale/transform | 100-200ms | ease-out | Hover scale, dot enlargement |
| Layout expand/collapse | 200-300ms | ease-in-out | Details, accordions |
| Slide/position | 200-300ms | ease-out | Popovers, panels |
| Page transitions | 300-400ms | ease-in-out | Tab switches, route changes |
| Progress bars | 400ms | ease | Width animation on render |

**Principles:**
- Enter animations slightly faster than exit
- Stagger list items by 30-50ms (max 5-7 items, then group)
- If removing the animation makes nothing worse, remove it
- Always respect `prefers-reduced-motion`

### Popup/Popover Contract

Every popup (tooltip, popover, dropdown, panel) must satisfy:

1. **Open trigger**: click, hover, or focus (document which)
2. **Close triggers** (at minimum):
   - Escape key
   - Click outside
   - Explicit close button (for persistent panels)
3. **Positioning**: below or above trigger, centered, with overflow detection
4. **Entry animation**: fade-in 80ms (opacity 0 to 1)
5. **Stacking**: newer popups dismiss older ones (singleton pattern)
6. **Content**: selectable text, clickable links (unlike CSS pseudo-element tooltips)

### Clipboard Pattern

```
1. User clicks copy button
2. Guard: if _copyLock active, return (debounce)
3. Set _copyLock = true
4. Call navigator.clipboard.writeText(text)
5. On success:
   - Change button label to confirmation ("Copied!")
   - Revert after 1.5-2s
6. On failure:
   - Select the text in a visible element (fallback)
   - Show "Failed -- text selected, Ctrl+C to copy"
   - Revert after 4s
7. Release _copyLock after 2s
```

### Progressive Disclosure Levels

| Level | Visibility | Example |
|-------|-----------|---------|
| Primary | Always visible | Phase grid, key metrics |
| Secondary | One click/expand | Blockers detail, tooltip content |
| Tertiary | Behind navigation or deep expand | Branching rules, full history |

**Rules:**
- Default to simplest view
- Label reveals clearly ("Show advanced", not "More")
- Remember user preference for expanded/collapsed (localStorage)
- Never hide critical/urgent information behind disclosure

---

## Review Checklist (Quick Pass)

Use for a fast scan when a full review isn't warranted:

- [ ] All interactive elements have hover + active states
- [ ] All async operations show loading feedback
- [ ] All error paths show recovery guidance
- [ ] All popups dismiss on Escape and outside-click
- [ ] All copy operations have failure fallback
- [ ] All animations respect prefers-reduced-motion
- [ ] No action requires more than 3 clicks to reach
- [ ] Empty states guide toward action
- [ ] Double-click on buttons doesn't cause problems
- [ ] Stale/outdated data is surfaced visibly
