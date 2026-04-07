---
name: ux-researcher
description: "Use this skill when planning or conducting user research, writing interview guides, designing surveys for UX insights, synthesizing qualitative findings, creating personas, or writing research reports. Trigger phrases: 'write a user interview guide', 'how do I conduct usability testing', 'synthesize research findings', 'create a user persona', 'design a UX survey'. Not for quantitative market sizing (use market-researcher), writing business requirements (use business-analyst), or product analytics."
version: 1.0.0
author: community
tags: [business, ux, research, user-interviews]
license: MIT
---

# UX Researcher

## Overview
This skill provides a complete framework for planning and executing user research—from choosing the right method through writing interview guides, running usability tests, synthesizing findings with affinity mapping, building personas, and writing a research report that drives product decisions. Good UX research replaces assumptions with evidence, ensuring product teams build things users actually need and can use.

## When to Use
- You need to understand why users behave a certain way (not just what they do)
- You want to validate or invalidate a product assumption before building
- You're writing a user interview guide for a research sprint
- You need to synthesize observations from multiple user sessions into insights
- You're creating user personas from research data
- You want to run a usability test on a prototype or existing product

## When NOT to Use
- Sizing a market or analyzing competitors (use market-researcher skill)
- Writing product requirements from research findings (use product-manager skill)
- Analyzing behavioral analytics data (use data-analyst skill)
- Writing a survey to validate market demand, not UX (use market-researcher skill)

## Quick Reference
| Research Method | Best For | Participants | Time |
|----------------|----------|-------------|------|
| In-depth interviews | Understanding motivations, mental models | 8–15 | 45–60 min each |
| Usability testing (moderated) | Finding interaction problems | 5–8 | 30–60 min each |
| Usability testing (unmoderated) | Broad task success rate | 30–100 | 15–20 min each |
| Card sorting | Information architecture, navigation | 20–30 | 20–30 min each |
| Tree testing | Validating navigation structure | 50–100 | 10–15 min each |
| Diary study | Longitudinal behavior tracking | 10–20 | 1–4 weeks |
| Surveys | Quantifying preferences, attitudes | 200–1,000 | 5–15 min |
| Field observation | Real-world context, workarounds | 5–10 | 1–3 hours each |
| First-click test | Discoverability of UI elements | 50–100 | 5–10 min |
| 5-second test | First impressions, clarity | 20–50 | 5 seconds |

## Instructions

### Step 1: Define the Research Goal
A research plan starts with a clear question. Write it in one sentence:
- "Why do new users drop off during the account setup flow?"
- "How do customer success managers currently track customer health?"
- "Can users successfully complete a payment using our redesigned checkout?"

Then list 3–5 specific learning objectives:
1. What does the current mental model look like for [task]?
2. What are the biggest pain points with the current experience?
3. What terminology do users use to describe [concept]?
4. Where in the flow do users get confused or stuck?
5. What workarounds have users developed?

### Step 2: Choose the Right Research Method
**Discovery research** (you don't know what the problems are yet):
→ In-depth interviews, field observation, diary studies

**Generative research** (generating ideas, understanding context):
→ Interviews, focus groups, co-design workshops

**Evaluative research** (testing a specific design or prototype):
→ Moderated usability testing, unmoderated usability testing, first-click tests

**Validation research** (confirming a hypothesis or measuring change):
→ A/B testing, surveys, benchmarking studies

### Step 3: Write a User Interview Guide
An interview guide structures the conversation without scripting it rigidly.

**Interview guide structure:**
```
1. Welcome and consent (5 min)
2. Warm-up: background questions (5 min)
3. Current behavior: how they do the task today (15 min)
4. Pain points and workarounds (10 min)
5. Concept exploration (if applicable) (10 min)
6. Wrap-up: anything else? (5 min)
```

**Sample interview guide — Understanding how project managers track work:**

---
**Research Goal:** Understand how engineering project managers track work and surface blockers.
**Participant criteria:** Engineering PMs at companies with 20–200 engineers; 2+ years in role.
**Duration:** 45–60 minutes.

**Welcome script:**
> "Thank you for making time today. I'm going to ask you questions about how you currently manage projects—there are no right or wrong answers. I'm here to learn from your experience, not to test you. I may take notes or have a colleague take notes. Is it okay if I record this session? The recording is only used internally."

**Warm-up (5 min):**
- Tell me a bit about your current role and team.
- How many engineers are on your team?
- What does your day-to-day look like?

**Current behavior (15 min):**
- Walk me through how you tracked last week's work, from Monday to Friday. (Probe: what tools did you use? What did that look like?)
- How do you know if a project is on track?
- How do you find out about blockers? How does that information reach you?
- Can you show me what your current project tracking setup looks like? (If screen share available)

**Pain points (10 min):**
- What's the most frustrating part of tracking work right now?
- When does the current process break down?
- Tell me about a time a project went off track. How did you find out?
- What workarounds do you use?

**Concept exploration (10 min, if showing a prototype):**
> "I'd like to show you something we're working on and get your honest reaction. This is early—nothing is built yet."
- Talk me through your first impression.
- How would you use this in your current workflow?
- What's missing? What would make this more useful?

**Wrap-up (5 min):**
- Is there anything important I didn't ask about?
- Who else do you think I should speak with?

---

**Probing techniques:**
- "Tell me more about that."
- "What do you mean by X?"
- "What happened next?"
- "Why is that?"
- "Can you give me a specific example?"
- "How often does that happen?"

### Step 4: Run a Usability Test
**Task writing principles:**
- Write tasks as scenarios, not instructions: "Imagine you need to add a new team member to your project" — not "Click on Settings → Team → Add Member"
- Tasks should have a clear, verifiable completion point
- Avoid jargon or product terminology in tasks (use the user's language)
- Provide realistic context: "You just hired a contractor, Sarah Chen..."

**Sample 30-minute usability test script:**

**Task 1 (Onboarding):** "You just signed up for this product. Please set up your account as you normally would."
- Success: User reaches the main dashboard
- Failure: User abandons or asks for help

**Task 2 (Core feature):** "You need to create a new project for the Q4 product launch. Please do that now."
- Success: Project created with a name and at least one team member
- Watch for: Discovery of "New Project" button, confusion around required fields

**Task 3 (Error recovery):** "Try to invite a colleague using the email address: not-an-email"
- Success: User sees error message and corrects it
- Watch for: Error message clarity, ability to recover without reload

**What to observe and note:**
- Where does the user hesitate (> 3 seconds without action)?
- Where do they go first? (reveals mental model)
- What do they say out loud? ("I'd expect this to be in Settings")
- Where do they make errors?
- What do they say about the language/labels?

### Step 5: Affinity Mapping — Synthesizing Research
After 8+ interviews, you'll have hundreds of individual observations. Affinity mapping organizes them into themes.

**Process:**
1. **Write each observation on a sticky note** (digital: Miro/FigJam): one idea per note
   - Good: "User said she checks email first thing every morning for project updates"
   - Bad: "User has communication problems" (too interpreted)
2. **Cluster similar notes** — move stickies that feel related near each other
3. **Name each cluster** with a theme label (the insight, not the description):
   - Not: "Email usage"
   - Yes: "Email is the default status update channel even when better tools exist"
4. **Identify patterns** across clusters: which themes appeared in 6/8 interviews?
5. **Generate insights**: "Users rely on email for status updates because [existing tools] don't surface the right level of summary information for their role"

### Step 6: Create a User Persona
A persona is a composite character built from research patterns—not a made-up stereotype.

**Persona template:**
```
Name: Marcus, the Overwhelmed Engineering Manager
Photo: [Stock photo of a 35-year-old in a casual office]

Quote: "I spend more time in status meetings than actually helping my team."

Background:
- Engineering Manager at a 150-person SaaS company
- 12 engineers across 3 squads, reporting to VP Engineering
- 5 years as a manager, 8 years as an engineer before that

Goals:
- Know the status of all projects without attending every standup
- Surface blockers before they cause delays
- Spend less time in meetings, more time on 1:1 coaching

Frustrations:
- Information is scattered across Jira, Slack, and email
- Has to interrupt engineers to get status updates
- Reports take 2 hours/week to compile manually

Behaviors:
- Checks Slack first thing; treats it as a status board
- Reviews Jira weekly but finds it too detailed for his needs
- Relies on his tech lead to aggregate information from the team

Tools used: Jira, Confluence, Slack, Google Sheets, Zoom

Technology comfort: High — was an engineer, comfortable with complex tools
```

### Step 7: Write a Research Report
A UX research report communicates findings and recommendations to decision makers.

**Report structure:**
1. **Research Goal and Questions** (1 paragraph)
2. **Methods and Participants** (brief: 8 interviews, 5 usability tests, etc.)
3. **Key Findings** (top 3–5 themes, with evidence quotes and observation counts)
4. **Recommendations** (prioritized list tied to product decisions)
5. **Appendix** (full interview notes, video clips, raw data)

**Finding format:**
> **Finding 3: Users don't discover the notification center until they miss an important event.**
>
> Evidence: 6 of 8 participants did not scroll to the notification bell icon during the first session. 3 participants mentioned they only discovered it after receiving a follow-up email saying they had missed a notification.
>
> Quote (Participant 4): "I didn't even know that was there. I just assumed the app didn't have notifications."
>
> Recommendation: Move notification bell to the primary navigation bar with an unread count badge. Trigger a tooltip on first login pointing to it.

## Examples

### Example 1: Create a User Interview Guide for a B2B SaaS Product
**Input:** "We're a project management tool. We want to understand why users abandon our product during the first 30 days."

**Key learning objectives:**
1. What did users expect the product to do before signing up?
2. What specific tasks did they try to accomplish in the first week?
3. Where did they get stuck or confused?
4. What alternatives did they try or switch to?
5. What would have kept them engaged?

**Interview guide excerpt (Current behavior section):**
> "Think back to your first week using [Product]. What was the first thing you tried to do?"
> - Probe: "What happened when you tried that?"
> - Probe: "How did that compare to what you expected?"
>
> "Can you walk me through a specific project you tried to set up?"
> - Probe: "Where did you get stuck?"
> - Probe: "What did you do when that happened?"
>
> "What made you decide to stop using it?" (for churned users)
> - Probe: "What would have changed your decision?"
> - Probe: "What did you switch to?"

**Output from 10 interviews — top findings:**
1. 7/10 users expected to import tasks from another tool on Day 1 — no import wizard existed
2. 8/10 users couldn't figure out the difference between "Projects" and "Workspaces"
3. 6/10 users gave up on inviting teammates because the invite flow was buried in Settings

---

### Example 2: Synthesize Research Findings into a Report
**Input:** 8 usability test sessions on a checkout redesign.

**Finding 1: The "Review Order" step causes confusion about what's next.**
> 7 of 8 participants paused for 4+ seconds on the Review Order screen. 5 said they weren't sure if they had already placed the order. Quote: "I thought I was done when I saw this page—I didn't realize I still had to confirm."
> **Recommendation:** Replace "Review Order" button label with "Place Order – $49.99" and add visual cue that this is the final step.

**Finding 2: Promo code field causes drop-off for users without a code.**
> 4 of 8 participants clicked the promo code field even though they didn't have a code, then abandoned checkout. This matches our analytics (23% of users who open promo field don't complete checkout).
> **Recommendation:** Hide the promo code field behind a small text link ("Have a promo code?") instead of displaying an open input field.

**Finding 3: Shipping option selection is the most confusing step.**
> All 8 participants tried to change shipping after selecting it, expecting a dropdown not a radio button. 3 participants couldn't figure out how to change it.
> **Recommendation:** Switch from radio buttons to a clickable card selection component with a clear "Change" affordance.

## Best Practices
- Recruit real users from your target segment, not internal employees (they know too much)
- Test with 5 users to find 80% of usability issues (Nielsen's law)—you don't need 50
- Always pilot test your interview guide with a colleague before running it with real participants
- Record sessions (with consent)—you will miss things while facilitating
- Share raw findings (video clips, quotes) alongside your report—stakeholders trust evidence they can see
- Present findings as insights ("users don't trust the security badge") not observations ("2 people looked at the badge")
- Deliver findings within 2 weeks of research completion; insights go stale

## Common Mistakes
- Leading questions: "Did you find it confusing that the button is small?" → biases the answer
- Testing with the wrong audience: testing a CRM with students, not sales reps
- Showing the design before understanding current behavior
- Asking hypothetical questions: "Would you use this feature?" (users say yes, then don't)
- Reporting observations as insights without analyzing patterns across sessions
- Writing a report no one reads — present key findings in a 10-minute meeting, keep the document as a reference

## Tips & Tricks
- "Concurrent think-aloud" — ask users to narrate their thoughts as they go, it reveals mental models in real time
- Recruiting: offer $50–100 gift cards for 45-minute sessions; response rate improves 3×
- Share a 3-minute video highlight reel of the most impactful moments — stakeholders remember video, not text
- The best question to end any interview: "Is there anything you wish I had asked?"
- Use the "Jobs to be Done" framing in interview analysis: "When [situation], I want to [motivation], so I can [outcome]"

## Related Skills
- [product-manager](../../business/product-manager/SKILL.md)
- [market-researcher](../../business/market-researcher/SKILL.md)
- [business-analyst](../../business/business-analyst/SKILL.md)
