# Prioritization Frameworks

Practical reference for selecting and applying product prioritization methods. Each framework includes when to use it, how to score, and a worked example.

## RICE Scoring

**When to use**: Comparing features objectively across a shared backlog.

### Formula

```
RICE Score = (Reach x Impact x Confidence) / Effort
```

### Definitions

| Factor | Description | Scale |
|--------|-------------|-------|
| **Reach** | Number of users/events affected per time period | Estimated count (e.g., users/quarter) |
| **Impact** | How much each user is affected | 3 = massive, 2 = high, 1 = medium, 0.5 = low, 0.25 = minimal |
| **Confidence** | How sure you are about estimates | 100% = high, 80% = medium, 50% = low |
| **Effort** | Person-months of work required | Estimated person-months |

### Worked Example

| Feature | Reach | Impact | Confidence | Effort | Score |
|---------|-------|--------|------------|--------|-------|
| Onboarding wizard | 5000 | 2 | 80% | 3 | 2667 |
| Dark mode | 8000 | 0.5 | 100% | 2 | 2000 |
| Export to PDF | 1000 | 3 | 50% | 1 | 1500 |

### Tips
- Re-estimate Reach quarterly; do not reuse stale numbers.
- Use Confidence to penalize guesswork, not to inflate pet projects.
- Effort should reflect total team effort, not just engineering.

---

## MoSCoW Method

**When to use**: Time-boxed releases where you need to draw a firm scope line.

### Categories

| Category | Meaning | Rule of Thumb |
|----------|---------|---------------|
| **Must Have** | Non-negotiable for this release | Without these, the release fails |
| **Should Have** | Important but not critical | Painful to leave out, but release still works |
| **Could Have** | Nice to have | Include only if time and budget allow |
| **Won't Have (this time)** | Explicitly out of scope | Acknowledged, parked for a future cycle |

### Process

1. List all candidate items.
2. Stakeholders assign each item a category (force a decision; "maybe" is not a category).
3. Validate that Must Haves fit within capacity. If not, something is mis-categorized.
4. Fill remaining capacity with Should Haves, then Could Haves.
5. Move overflow to Won't Have with a clear reason.

### Anti-patterns
- Everything is a Must Have: capacity math will expose this.
- No Won't Haves: you are not making real trade-offs.
- Skipping stakeholder alignment: categories should be consensus, not dictated.

---

## Jobs-to-be-Done (JTBD)

**When to use**: Understanding why customers switch products or adopt features, beyond surface-level requests.

### Core Concept

Customers "hire" products to do a job. The job statement follows a structured format:

```
When [situation], I want to [motivation], so I can [expected outcome].
```

### Job Mapping Steps

1. **Define the job**: What is the functional, emotional, and social job?
2. **Map the process**: Break the job into steps (locate, prepare, confirm, execute, monitor, modify, conclude).
3. **Find underserved needs**: Where is the current solution slow, error-prone, or missing?
4. **Prioritize opportunities**: Score each unmet need by importance and satisfaction gap.

### Opportunity Score

```
Opportunity = Importance + max(Importance - Satisfaction, 0)
```

| Need | Importance (1-10) | Satisfaction (1-10) | Opportunity |
|------|-------------------|---------------------|-------------|
| Find matching items quickly | 9 | 4 | 14 |
| Compare prices across sources | 7 | 6 | 8 |
| Save progress for later | 8 | 8 | 8 |

High-opportunity scores indicate underserved needs worth building for.

### Tips
- Interview customers about their last real purchase decision, not hypothetical preferences.
- Jobs are stable over time; solutions change. Focus on the job, not the feature.
- Combine JTBD with RICE to filter what to build first.

---

## OKR Alignment

**When to use**: Connecting feature work to measurable business outcomes.

### Structure

```
Objective: [Qualitative, inspiring goal]
  KR1: [Metric] from [baseline] to [target] by [date]
  KR2: [Metric] from [baseline] to [target] by [date]
  KR3: [Metric] from [baseline] to [target] by [date]
```

### Good OKR Checklist

- [ ] Objective is ambitious but achievable (aim for ~70% hit rate).
- [ ] Key Results are measurable, not tasks.
- [ ] Each KR has a baseline and a target.
- [ ] KRs are leading indicators, not lagging (prefer activation rate over annual revenue).
- [ ] No more than 3-5 KRs per Objective.

### Linking Features to OKRs

| Feature | Primary OKR | Expected KR Impact | Confidence |
|---------|-------------|-------------------|------------|
| Onboarding wizard | Improve activation | Activation rate +15% | High |
| Dark mode | Increase engagement | Session time +5% | Medium |
| Export to PDF | Reduce churn | Support tickets -10% | Low |

Features that do not connect to any OKR should be questioned or deprioritized.

---

## Impact/Effort Matrix

**When to use**: Quick visual triage during planning sessions or brainstorms.

### Quadrants

```
          High Impact
              |
  Quick Wins  |  Big Bets
  (Do First)  |  (Plan Carefully)
--------------+--------------
  Fill-Ins    |  Money Pits
  (Do If Idle)|  (Avoid)
              |
          Low Impact
   Low Effort      High Effort
```

### Process

1. List candidate items on sticky notes or a shared board.
2. Each item gets a rough Impact score (1-5) and Effort score (1-5).
3. Place on the matrix. Discuss disagreements.
4. Sequence: Quick Wins first, then Big Bets with proper planning, Fill-Ins as capacity allows, Money Pits last or never.

### Common Mistakes
- Underestimating effort by ignoring testing, docs, and rollout.
- Conflating "loud stakeholder" with "high impact."
- Using the matrix once and never revisiting as context changes.

---

## Feature Scoring Template

A combined template for when you want to evaluate features across multiple dimensions.

### Scoring Rubric

| Dimension | Weight | 1 (Low) | 3 (Medium) | 5 (High) |
|-----------|--------|---------|------------|----------|
| Customer value | 30% | Nice to have | Solves a real pain | Must-have for key segment |
| Strategic alignment | 25% | Tangential | Supports a KR | Directly drives an Objective |
| Revenue potential | 20% | No clear path | Indirect contribution | Direct monetization |
| Technical feasibility | 15% | Major unknowns | Some complexity | Well-understood |
| Competitive advantage | 10% | Table stakes | Differentiation | Unique moat |

### Calculation

```
Weighted Score = Sum(Dimension Score x Weight)
```

### Template Row

| Feature | Customer Value | Strategic Align | Revenue | Feasibility | Competitive | Weighted Score |
|---------|---------------|----------------|---------|-------------|-------------|---------------|
| Feature A | 4 | 5 | 3 | 4 | 2 | 3.95 |

---

## Roadmap Planning Patterns

### Time Horizons

| Horizon | Timeframe | Confidence | Detail Level |
|---------|-----------|------------|-------------|
| Now | 0-6 weeks | High | Specific features with owners |
| Next | 6-12 weeks | Medium | Themes with candidate features |
| Later | 3-6 months | Low | Strategic bets and exploration areas |

### Theme-Based Roadmap

Group features under themes rather than dates:

```
Theme: "Frictionless Onboarding"
  - Onboarding wizard (Now)
  - Progressive profiling (Next)
  - Personalized templates (Later)

Theme: "Power User Retention"
  - Keyboard shortcuts (Now)
  - Custom dashboards (Next)
  - API access (Later)
```

### Roadmap Review Cadence

| Activity | Frequency | Participants |
|----------|-----------|-------------|
| Backlog grooming | Weekly | PM + Engineering leads |
| Roadmap review | Monthly | PM + Design + Engineering + Stakeholders |
| Strategic review | Quarterly | Leadership + PM |
| Vision refresh | Annually | Full team offsite |

### Anti-patterns
- Date-driven roadmaps with no flexibility: prefer outcome-driven.
- Roadmap as a promise: it is a plan, not a contract.
- No explicit "not doing" list: makes it impossible to say no.
