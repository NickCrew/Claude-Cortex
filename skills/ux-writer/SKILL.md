---
name: ux-writer
description: 'Use this skill when crafting microcopy, UI text, or in-product writing—error messages, tooltips, button labels, empty states, onboarding flows, and confirmation dialogs. Trigger phrases: ''write microcopy for'', ''write UI copy'', ''write error messages'', ''write onboarding text'', ''button label for''. Do NOT use for marketing copy (use copywriter) or long-form documentation (use technical-writer).'
version: 1.0.0
author: community
tags:
  - design
  - ux-writing
  - microcopy
  - ui-text
  - copywriting
license: MIT
keywords:
  - write microcopy
  - UI text
  - button label
  - error message
  - writer
  - ux writer
---

# UX Writer

## Overview
This skill helps you craft clear, helpful, and human UI text that guides users through your product without friction. UX writing is not marketing copy—it lives inside the product and its job is to reduce confusion, build trust, and move users toward success. Good microcopy is invisible when it works and painfully obvious when it doesn't. This skill covers the full spectrum of in-product text: button labels, error messages, empty states, tooltips, onboarding flows, confirmation dialogs, form helper text, and success messages. The output is production-ready copy, not placeholder text.

## When to Use
- Writing or rewriting button labels and CTAs inside a product
- Crafting error messages that explain what went wrong and how to fix it
- Designing empty states that guide users toward their first action
- Writing onboarding flows, welcome screens, and feature tours
- Composing tooltip and helper text for complex fields or controls
- Creating confirmation dialogs, destructive-action warnings, and success messages
- Auditing and improving existing UI copy for clarity and tone consistency

## When NOT to Use
- Marketing landing pages, ads, or campaign copy (use `copywriter` skill instead)
- Long-form help articles or user manuals (use `technical-writer` skill instead)
- Brand naming or tagline development
- Social media posts or email newsletters
- Legal disclaimers or compliance text (consult legal)

## Quick Reference
| Task | Approach |
|------|----------|
| Button labels | Verb + noun: "Save draft", "Delete account". Never "OK" or "Click here" |
| Error messages | What happened + why + how to fix: "Password too short — use at least 8 characters" |
| Empty states | Explain the blank, then invite action: "No projects yet. Start your first one." |
| Tooltips | One sentence max. Answer "what does this do?" not "why does this exist?" |
| Onboarding | Progressive disclosure: show the next step, not every step at once |
| Destructive actions | Name the consequence explicitly: "Delete project" not "Confirm" |
| Success messages | Confirm the action, optionally suggest the next step |
| Tone | Match the product voice; default to warm, direct, and plain English |

## Instructions

1. **Identify the UI element and context.** Determine exactly what element needs copy (button, error, tooltip, etc.), where it appears in the user journey, and who the user is at that moment. A user mid-checkout needs different language than a new signup exploring features.

2. **Define the job of the text.** Every piece of microcopy does exactly one job: inform, instruct, reassure, warn, or motivate. Name the job before you write a single word. Copy that tries to do two jobs usually does neither well.

3. **Write in plain language.** Use the simplest word that does the job. "Start" over "Initiate". "Delete" over "Remove permanently". Aim for a reading level your least technical user can parse at a glance—UI text is read in seconds, not minutes.

4. **Apply the error message formula for all error states.** Structure: (1) what happened in plain terms, (2) why it happened if helpful, (3) what the user can do next. Never blame the user ("You entered an invalid email") — be neutral or take system responsibility ("That email address isn't valid — check for typos and try again").

5. **Shorten ruthlessly.** Count your words, then cut 30%. Every word costs attention. Button labels should be 1–3 words. Tooltips: one sentence. Error messages: two sentences max. If a concept needs more than that, the UI probably needs redesign, not more copy.

6. **Check consistency.** Use the same verb for the same action throughout the product. If the nav says "Sign in", the button must not say "Log in". Inconsistency erodes trust faster than bad copy does.

7. **Test against your voice and tone guide.** If the brand is warm and conversational, "Oops, something went wrong" fits. If it's enterprise and formal, it doesn't. When in doubt, default to neutral and direct.

8. **Write variants and compare.** Generate 3 options for any important piece of copy, then evaluate against: clarity, brevity, brand tone, and whether it reduces or increases user anxiety.

## Examples

### Example 1: Error Messages for a Sign-Up Form

**Input:** "Write error messages for a sign-up form. Fields: email, password (min 8 chars, must include a number), username (3–20 chars, letters and numbers only). Tone: friendly, modern SaaS."

**Output:**

#### Email field errors

| Trigger | Message |
|---------|---------|
| Empty on submit | Enter your email address to continue. |
| Invalid format | That doesn't look like an email address — check for typos. |
| Already registered | An account with this email already exists. [Sign in instead?] |

#### Password field errors

| Trigger | Message |
|---------|---------|
| Empty on submit | Choose a password to secure your account. |
| Too short | Password must be at least 8 characters. |
| No number | Add at least one number to strengthen your password. |
| Confirmed password mismatch | These passwords don't match — give it another try. |

#### Username field errors

| Trigger | Message |
|---------|---------|
| Too short | Username must be at least 3 characters. |
| Too long | Keep your username under 20 characters. |
| Invalid characters | Usernames can only contain letters and numbers. |
| Already taken | That username is taken — try adding a number or your initial. |

#### Success state

> **You're all set, [Name]!** Your account is ready. Let's get started. → **Go to dashboard**

---

### Example 2: Empty State for a Project Management App

**Input:** "Write empty state copy for a project management app. States needed: no projects, no tasks in a project, no team members. Tone: encouraging, startup-friendly."

**Output:**

#### No projects yet

**Heading:** Your workspace is ready.
**Body:** Projects live here. Create your first one to start organizing work, tracking tasks, and collaborating with your team.
**Button:** Create project

---

#### No tasks in this project

**Heading:** Nothing here yet — that's about to change.
**Body:** Add your first task to kick things off. Break your project into steps and start making progress.
**Button:** Add task

---

#### No team members

**Heading:** You're working solo — for now.
**Body:** Invite your team to collaborate, assign tasks, and move faster together.
**Button:** Invite people
**Secondary link:** Learn how sharing works →

---

### Example 3: Destructive Action Confirmation Dialog

**Input:** "Write a confirmation dialog for permanently deleting a user account. The action cannot be undone. Tone: serious but not alarming."

**Output:**

#### Dialog title
Delete your account?

#### Dialog body
This will permanently delete your account, all your projects, and your data. This can't be undone.

#### Buttons
- **Primary (destructive):** Delete my account
- **Secondary (cancel):** Keep my account

> **Design note:** The cancel action should be the visually prominent button. The destructive action should be secondary in visual weight but clearly labeled.

---

## Best Practices
- Lead with what the user can do, not what they can't: "Save up to 5 files" not "You can't save more than 5 files"
- Name the object in button labels: "Delete project" not "Delete" — specificity prevents accidental actions
- Use sentence case for UI text (not Title Case or ALL CAPS) unless brand standards differ
- Avoid jargon, internal terms, and engineering-speak in user-facing copy
- Write gender-neutral, inclusive copy; prefer "they" for singular unknown users
- Pair error messages visually with the field they describe — proximity beats explanation

## Common Mistakes
- **"Click here" links:** Screen readers read links out of context; the link text must describe the destination
- **Vague errors:** "Something went wrong" is never acceptable without a recovery action
- **Over-apologizing:** "We're so sorry, but unfortunately..." wastes characters and sounds insincere
- **Inconsistent verb tenses:** Mixing "Your file was saved" and "Saving your file..." in the same flow
- **Using "please" everywhere:** One "please" per flow is polite; five is patronizing
- **Writing for the happy path only:** Empty states, errors, and loading states need as much care as core flows

## Tips & Tricks
- Read your copy aloud at a conversational pace — if you stumble, the user will too
- The "Grandma test": if your least technical user would be confused, simplify
- Keep a "word swap" list: initiate → start, terminate → end, utilize → use
- Use active voice in errors: "We couldn't process your payment" not "Payment could not be processed"
- When copy feels long, ask "Can the UI design carry some of this load?" — a well-placed icon can replace a sentence
- Write the error states before the success states; they reveal gaps in the logic

## Related Skills
- [copywriter](../../writing/copywriter/SKILL.md)
- [technical-writer](../../writing/technical-writer/SKILL.md)
- [design-critiquer](../design-critiquer/SKILL.md)
- [frontend-design](../frontend-design/SKILL.md)
