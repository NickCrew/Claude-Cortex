---
name: product-manager
description: 'Use this skill when writing product requirements documents, prioritizing features, creating user stories, defining acceptance criteria, or setting product metrics. Trigger phrases: ''write a PRD for'', ''prioritize this feature backlog'', ''write user stories for'', ''help me define acceptance criteria'', ''what metrics should we track for''. Not for writing code, designing UI mockups, or conducting user research interviews.'
version: 1.0.0
author: community
tags:
  - business
  - product-management
  - roadmap
  - strategy
license: MIT
keywords:
  - write PRD
  - user stories
  - feature prioritization
  - product
  - manager
  - product manager
---

# Product Manager

## Overview
This skill enables structured product management work—from writing comprehensive PRDs and user stories through feature prioritization and metrics definition. It provides repeatable frameworks (RICE scoring, MoSCoW, OKR-aligned roadmaps) and document templates grounded in real product scenarios. The output is always decision-ready: actionable artifacts that engineering, design, and stakeholders can align on.

## When to Use
- Writing a Product Requirements Document (PRD) for a new feature or product
- Prioritizing a feature backlog with a scoring framework
- Translating user needs into user stories with acceptance criteria
- Defining success metrics (product KPIs) for a feature or initiative
- Creating a quarterly roadmap aligned to business objectives
- Writing a one-pager or feature brief for executive review

## When NOT to Use
- Conducting user research or usability testing (use ux-researcher skill)
- Designing wireframes or high-fidelity UI (use a design skill)
- Writing technical specifications for engineers (use a tech spec skill)
- Building business cases with financial modeling (use business-analyst skill)

## Quick Reference
| Task | Framework/Template |
|------|--------------------|
| Feature prioritization | RICE score: (Reach × Impact × Confidence) / Effort |
| Backlog triage | MoSCoW: Must have / Should have / Could have / Won't have |
| User story format | "As a [user], I want [action] so that [benefit]" |
| Acceptance criteria | Given/When/Then (BDD-style) |
| Success metrics | Primary: 1 north star. Secondary: 3–5 supporting. Guardrails: 2–3 don't-break metrics |
| PRD sections | Overview → Problem → Goals → Users → Requirements → Metrics → Risks → Timeline |
| Impact sizing | 1–5 scale: 1=minimal, 3=moderate, 5=massive uplift |
| Effort sizing | T-shirt: XS/S/M/L/XL; or story points; or person-weeks |

## Instructions

### Step 1: Write a Product Requirements Document (PRD)

**PRD Template:**

---
**Feature Name:** [Name]
**Author:** [PM Name] | **Date:** [Date] | **Status:** Draft / Review / Approved
**Engineering Owner:** | **Design Owner:** | **Launch Target:**

---

**1. Overview (TL;DR)**
One paragraph: what we're building, why, and the expected business impact.

**2. Problem Statement**
- What user pain point or business problem does this solve?
- What is the current experience? (describe the before state)
- What is the evidence this problem is real? (user research, support tickets, data)

**3. Goals and Non-Goals**
| Goals | Non-Goals |
|-------|-----------|
| ✅ Users can complete X without Y friction | ❌ This does not redesign the entire onboarding flow |
| ✅ Reduce support tickets about Z by 30% | ❌ This does not support mobile in V1 |

**4. User Personas**
Who are the primary users? List 1–3 personas with their role, context, and motivation.

**5. Functional Requirements**
List every user-facing behavior the feature must support, organized by user flow:
- FR-01: [Requirement]
- FR-02: [Requirement]

**6. Non-Functional Requirements**
- Performance: page load < 2 seconds at P95
- Availability: 99.9% uptime SLA
- Security: [specific requirements]
- Accessibility: WCAG 2.1 AA compliant

**7. Success Metrics**
- **Primary metric (north star):** e.g., 30-day retention rate for new users
- **Secondary metrics:** e.g., time-to-first-value, feature adoption rate
- **Guardrail metrics:** e.g., support ticket volume (must not increase > 5%)

**8. Risks and Mitigations**
| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| [Risk] | High/Med/Low | High/Med/Low | [Plan] |

**9. Open Questions**
- [ ] Question 1 — Owner: [Name] — Due: [Date]

**10. Launch Plan**
- Alpha: [audience, date]
- Beta: [audience, date]
- GA: [audience, date]

---

### Step 2: Prioritize Features with RICE
RICE score = (Reach × Impact × Confidence) / Effort

**Reach**: How many users affected per quarter? (raw number)
**Impact**: Effect per user: 3=massive, 2=high, 1=medium, 0.5=low, 0.25=minimal
**Confidence**: How sure are we? 100%=high, 80%=medium, 50%=low
**Effort**: Person-months required

```
Feature A: Reach=5000, Impact=2, Confidence=80%, Effort=2 months
RICE = (5000 × 2 × 0.8) / 2 = 4,000

Feature B: Reach=1000, Impact=3, Confidence=90%, Effort=0.5 months
RICE = (1000 × 3 × 0.9) / 0.5 = 5,400  ← prioritize this first
```

**MoSCoW for sprint planning:**
- **Must have**: Without this, the sprint/release fails (user can't complete core task)
- **Should have**: High value, but workaround exists without it
- **Could have**: Nice to have; cut if effort spikes
- **Won't have**: Explicitly deferred to future release; prevents scope creep

### Step 3: Write User Stories
Format: `As a [user type], I want [capability] so that [benefit].`

Rules for good user stories:
- Focus on the user's goal, not the implementation
- One story = one deliverable unit of value
- Small enough to complete in one sprint
- Testable: acceptance criteria can be written for it

**Example:**
> As a **free-plan user**, I want to **upgrade to Pro with one click from within the app** so that **I don't have to navigate to a separate billing page and lose my context.**

### Step 4: Write Acceptance Criteria (Given/When/Then)
For each user story, write 2–5 acceptance criteria in BDD format:

```
Scenario: Successful upgrade flow
  Given I am logged in as a free-plan user
  And I am on any page in the app
  When I click "Upgrade to Pro" in the nav bar
  Then I should see the upgrade modal with pricing details
  And the modal should pre-fill my account email
  
Scenario: Failed payment
  Given I am on the upgrade modal
  When I submit payment with a declined card
  Then I should see the error message "Payment declined. Please try another card."
  And my account should remain on the free plan
  And no charge should appear on my card
```

### Step 5: Define Product Metrics
For every feature, define metrics in three tiers:

**Tier 1 — Primary (North Star)**: The one metric that proves the feature is delivering value.
**Tier 2 — Secondary**: Supporting metrics that explain *why* the primary metric moved.
**Tier 3 — Guardrails**: Metrics that must NOT regress (existing feature health).

Example for an upgrade flow feature:
- **Primary**: Conversion rate from free to paid (target: +2pp in 90 days)
- **Secondary**: Modal open rate, modal → checkout rate, checkout → completed rate
- **Guardrails**: Free plan user satisfaction score (must not drop), support tickets about billing (must not increase > 10%)

## Examples

### Example 1: Write a PRD for a New Feature — In-App Notifications

**Input:** "We want to add in-app notifications so users don't miss important events."

**PRD excerpt:**

---
**Feature Name:** In-App Notification Center
**Status:** Draft | **Launch Target:** Q2 2024 | **Effort:** M (3 engineers, 6 weeks)

**Problem Statement:**
Users miss critical events (payment failures, team invitations, limit warnings) because they only receive emails, which have a 22% open rate. This results in 340 monthly support tickets from users who say they "didn't know" about an issue. Churn analysis shows 18% of churned users had an unresolved payment failure 7+ days before cancellation.

**Goals:** Enable users to see and act on critical account events without leaving the app. Target: reduce missed-event support tickets by 50% in 90 days.

**Non-Goals:** Push notifications (mobile), email digest redesign, third-party integrations.

**Requirements:**
- FR-01: Users can see a notification bell icon in the top nav with an unread count badge
- FR-02: Clicking the bell opens a dropdown with the 20 most recent notifications
- FR-03: Notifications have type (info/warning/error), title, body, timestamp, and optional CTA link
- FR-04: Users can mark individual or all notifications as read
- FR-05: System generates notifications for: payment failure, plan limit reached, team invite received, 7-day trial ending

**Primary metric:** Support tickets tagged "missed-event" (target: −50% in 90 days)
**Secondary:** Notification open rate, CTA click rate per notification type
**Guardrails:** Page load time on nav (must stay < 200ms), email open rate (must not drop)

---

### Example 2: Prioritize a Feature Backlog

**Input:** 5 features competing for next quarter's roadmap.

| Feature | Reach | Impact | Confidence | Effort (months) | RICE Score |
|---------|-------|--------|------------|-----------------|------------|
| SSO / SAML login | 800 enterprise users | 3 (massive — blocks enterprise sales) | 90% | 2 | **1,080** |
| Dark mode | 12,000 all users | 0.5 (minimal productivity gain) | 80% | 1 | **4,800** |
| Bulk CSV export | 2,500 power users | 2 (high — replaces manual workaround) | 90% | 0.5 | **9,000** ← #1 |
| AI summary feature | 5,000 users | 2 (high) | 50% | 3 | **1,667** |
| Mobile app | 12,000 all users | 2 (high) | 70% | 8 | **2,100** |

**Recommendation:**
1. **Bulk CSV export** (RICE: 9,000) — quick win, clear ROI
2. **Dark mode** (RICE: 4,800) — broad reach, low effort
3. **Mobile app** (RICE: 2,100) — high effort; plan for H2
4. **AI summary** (RICE: 1,667) — deprioritize until confidence improves
5. **SSO** (RICE: 1,080) — low RICE score but strategic; fast-track if enterprise deal depends on it

## Best Practices
- Write the success metrics before writing requirements—it clarifies what you're actually building
- Every requirement should map to a user need; delete requirements that don't
- Invite engineering into PRD review early—they'll catch infeasibility and suggest better approaches
- Keep the PRD to 2–4 pages; appendices for edge cases and technical detail
- Version your PRD (v0.1 draft, v1.0 approved) and record who approved it and when
- "Non-goals" are as important as goals—they prevent scope creep

## Common Mistakes
- Writing requirements as solutions ("Add a button that…") instead of problems ("Users need to…")
- Including too many must-haves: if everything is a must, nothing is
- Skipping acceptance criteria: engineers will interpret requirements differently without them
- Defining success only by shipping, not by user behavior change
- Ignoring guardrail metrics: a new feature that improves one thing but breaks another is not a success
- Writing a PRD in isolation: no engineering or design input until handoff

## Tips & Tricks
- Use the "5 Whys" to make sure you're solving the root cause, not a symptom
- For ambiguous requirements, write what the UI should say—even rough copy clarifies intent
- A one-page feature brief (problem + proposed solution + success metric) is faster to align on than a full PRD; use it to get buy-in before writing the full doc
- Add a "North Star Question": "How will we know in 90 days if this feature succeeded?" Answer it in the metrics section
- Link the PRD to the relevant user research, data analysis, and design mockups in a "references" section

## Related Skills
- [ux-researcher](../../business/ux-researcher/SKILL.md)
- [business-analyst](../../business/business-analyst/SKILL.md)
- [okr-planner](../../business/okr-planner/SKILL.md)
- [market-researcher](../../business/market-researcher/SKILL.md)
