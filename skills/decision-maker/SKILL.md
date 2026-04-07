---
name: decision-maker
description: "Use this skill when you face a complex or high-stakes decision and need a structured framework to evaluate options objectively. Ideal for career choices, product prioritization, vendor selection, or any multi-criteria trade-off. Not for trivial daily decisions or situations that require licensed professional advice."
version: 1.0.0
author: community
tags: [productivity, decision-making, frameworks, analysis]
license: MIT
---

# Decision Maker

## Overview
This skill applies proven decision-making frameworks—pros/cons analysis, weighted scoring matrices, RICE prioritization, the Eisenhower urgency-importance matrix, and pre-mortem analysis—to help you cut through ambiguity and make defensible, well-reasoned choices. By externalizing the decision into a structured format you reduce cognitive bias, surface hidden trade-offs, and create a record of your reasoning that can be revisited or shared with stakeholders.

## When to Use
- You have two or more meaningful options and are unsure which to choose
- The decision has significant, lasting consequences (career, finances, product roadmap, hiring)
- Multiple stakeholders need to align around a shared rationale
- You feel emotionally stuck and want an objective framework to cut through the noise
- You need to prioritize a backlog of features, tasks, or projects
- You want to stress-test a decision you've already leaned toward

## When NOT to Use
- The decision is low-stakes and reversible (where any choice is fine)
- You need licensed advice (legal, medical, financial) — frameworks support, not replace, professionals
- The situation requires immediate crisis action with no time for structured analysis
- Data needed to score criteria is completely unavailable or unknowable
- You simply want validation for a decision already firmly made

## Quick Reference
| Framework | Best For | Output |
|-----------|----------|--------|
| Pros / Cons | Simple binary choices, fast gut-check | Two-column list |
| Weighted Scoring Matrix | Multi-option, multi-criteria trade-offs | Ranked score table |
| RICE | Feature or project prioritization | Priority-ranked backlog |
| Eisenhower Matrix | Task triage and time management | 4-quadrant urgency/importance grid |
| Pre-Mortem | Risk identification before committing | List of failure modes and mitigations |

## Instructions

1. **Clarify the decision** — State the decision in one clear sentence. Define what "success" looks like and the deadline by which you must decide.

2. **Enumerate options** — List every realistic option, including "do nothing" or "defer." Aim for at least two, no more than six manageable choices.

3. **Choose a framework** — Match the framework to the decision type: use Pros/Cons for simple binary choices; Weighted Scoring for multi-criteria comparisons; RICE for backlog prioritization; Eisenhower for task triage; Pre-Mortem for risk stress-testing.

4. **Define criteria (Weighted Scoring)** — Identify 3–7 criteria that matter most (e.g., cost, time-to-value, strategic fit, risk). Assign each a weight from 1–5 reflecting its relative importance.

5. **Score each option** — Rate every option against each criterion on a 1–10 scale. Multiply by weight. Sum the totals. Higher scores indicate better overall fit.

6. **Apply RICE (if prioritizing work)** — For each item calculate: Reach × Impact × Confidence ÷ Effort. Reach = users affected; Impact = 1–3 scale; Confidence = percentage (0–100); Effort = person-weeks.

7. **Map urgency vs. importance (Eisenhower)** — Plot tasks on a 2×2 grid: Do Now (urgent + important), Schedule (important, not urgent), Delegate (urgent, not important), Eliminate (neither).

8. **Run a pre-mortem** — Imagine it is 12 months from now and the chosen option has failed spectacularly. Brainstorm every plausible cause. Use this list to add mitigations or re-weight criteria.

9. **Check for bias** — Review the analysis for sunk-cost fallacy, status-quo bias, and confirmation bias. Ask: "Would I choose this if I were starting fresh?"

10. **Document and decide** — Write a one-paragraph decision summary: chosen option, top three reasons, top two risks and their mitigations, and a review date.

## Examples

### Example 1: Career Choice — Stay at Current Job vs. Accept Startup Offer
**Input:**
"I have a stable senior engineer role at a Fortune 500 paying $160k. A Series B startup offered me a staff engineer role at $140k base + 0.4% equity. I have a mortgage and two kids. Help me decide."

**Output:**

**Weighted Scoring Matrix**

Criteria | Weight | Fortune 500 (score) | Fortune 500 (weighted) | Startup (score) | Startup (weighted)
--- | --- | --- | --- | --- | ---
Financial security | 5 | 9 | 45 | 5 | 25
Career growth | 4 | 5 | 20 | 9 | 36
Compensation upside | 3 | 4 | 12 | 8 | 24
Work-life balance | 4 | 7 | 28 | 5 | 20
Mission alignment | 2 | 4 | 8 | 8 | 16
**Total** | | | **113** | | **121**

**Pre-Mortem (Startup):** Startup runs out of runway (mitigate: verify 18+ months runway, ask for accelerated vesting cliff), role scope shrinks post-hire (mitigate: get title and scope in writing).

**Recommendation:** The startup scores marginally higher, but the margin is within noise given your dependence on financial stability. Negotiate: request a $150k base, 12-month cliff vesting, and written role definition before accepting. If negotiation fails, the stability of the Fortune 500 warrants staying.

---

### Example 2: Product Prioritization — RICE Scoring a Feature Backlog
**Input:**
"We have 5 features to prioritize for Q3: (A) SSO login, (B) CSV export, (C) Mobile app, (D) Audit logs, (E) Bulk delete. We serve 2,000 enterprise users."

**Output:**

**RICE Scores**

Feature | Reach | Impact | Confidence | Effort (wks) | RICE Score
--- | --- | --- | --- | --- | ---
A – SSO Login | 1,800 | 3 | 90% | 3 | **1,620**
D – Audit Logs | 1,500 | 2 | 80% | 2 | **1,200**
B – CSV Export | 1,200 | 2 | 95% | 1 | **2,280**
E – Bulk Delete | 800 | 1 | 90% | 0.5 | **1,440**
C – Mobile App | 600 | 3 | 60% | 12 | **90**

**Recommended Priority:** B → A → E → D → C. CSV Export delivers the highest RICE score at low effort. Mobile App scores last due to high effort and low confidence — defer to Q4 or a dedicated mobile initiative.

## Best Practices
- Always score options blind (fill in scores before revealing which option you prefer) to reduce anchoring bias
- Involve at least one dissenting voice in the criteria-weighting step to stress-test your priorities
- Revisit your decision at a predetermined date — decisions are hypotheses, not facts
- Use the Eisenhower matrix daily/weekly; reserve weighted scoring for quarterly or life decisions
- When stakes are very high, run both a weighted scoring matrix AND a pre-mortem before committing
- Document your reasoning even if you ultimately go with intuition — you'll learn from the outcome

## Common Mistakes
- Weighting criteria after scoring options (this introduces confirmation bias into the weights)
- Using too many criteria (>7) which dilutes meaningful differentiation between options
- Treating RICE scores as precise — they are directional estimates, not exact measurements
- Skipping the pre-mortem step when you're excited about a preferred option — that's exactly when it's most needed
- Equating a higher score with a guaranteed good outcome — the framework improves odds, not certainty
- Forgetting to include "do nothing" as an explicit option with its own score

## Tips & Tricks
- If two options score within 5% of each other, flip a coin — the framework has told you they're essentially equal, so other factors (gut feel, optionality) should break the tie
- Timebox the analysis: 30 minutes for a pros/cons, 2 hours for a full weighted matrix — decisions don't improve linearly with analysis time
- Use a "regret minimization" sanity check (Bezos): imagine yourself at 80 looking back — which option would you regret NOT trying?
- For team decisions, have each person score independently before sharing results to avoid groupthink
- Export your scoring matrix to a shared doc so stakeholders can see and challenge the inputs, not just the conclusion

## Related Skills
- [task-planner](../../productivity/task-planner/SKILL.md)
- [note-taker](../../productivity/note-taker/SKILL.md)
