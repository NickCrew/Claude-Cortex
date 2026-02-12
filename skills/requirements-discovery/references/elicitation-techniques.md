# Elicitation Techniques

## Stakeholder Interview Patterns

### Open Questions (Divergent)

Use early in discovery to explore the problem space:

| Purpose | Example Question |
| --- | --- |
| Understand goals | "What does success look like for this project in 6 months?" |
| Uncover pain points | "Walk me through a typical day. Where do things break down?" |
| Explore context | "What happened that made this project a priority now?" |
| Identify constraints | "What would prevent this from succeeding?" |
| Surface assumptions | "What are we assuming is true that we haven't validated?" |
| Map stakeholders | "Who else should we talk to about this?" |

### Closed Questions (Convergent)

Use to confirm specifics and narrow scope:

| Purpose | Example Question |
| --- | --- |
| Confirm priority | "Is real-time data more important than historical reporting?" |
| Set boundaries | "Is mobile support required for launch?" |
| Validate requirements | "Does the system need to support more than 1000 concurrent users?" |
| Clarify ambiguity | "When you say 'fast', do you mean under 200ms or under 2 seconds?" |

### Contextual Inquiry

Observe users in their environment rather than relying solely on interviews:

1. **Shadow a workflow**: Watch the user perform their actual task
2. **Note workarounds**: Workarounds reveal unmet needs
3. **Ask in context**: "Why did you just copy that into a spreadsheet?"
4. **Record artifacts**: Screenshots, exported files, sticky notes on monitors
5. **Identify invisible tasks**: Things users do automatically without thinking

### Interview Anti-Patterns

- Leading questions ("Don't you think we should use React?")
- Asking about hypothetical behavior ("Would you use X?") instead of actual behavior ("How do you handle X today?")
- Interviewing only executives; missing front-line users
- Recording solutions instead of problems

---

## PRD Structure and Templates

### Standard PRD Sections

```markdown
# Product Requirements Document: [Feature Name]

## 1. Overview
- Problem statement (1-2 paragraphs)
- Business justification and expected impact
- Target users and personas

## 2. Goals and Non-Goals
### Goals
- [Measurable outcome 1]
- [Measurable outcome 2]

### Non-Goals (Explicitly Out of Scope)
- [Thing we are intentionally not doing]

## 3. User Stories
- As a [persona], I want [action] so that [outcome]
- Acceptance criteria for each story

## 4. Functional Requirements
### [Feature Area 1]
- FR-001: [Requirement with clear pass/fail criteria]
- FR-002: [Requirement]

### [Feature Area 2]
- FR-003: [Requirement]

## 5. Non-Functional Requirements
- Performance: [specific thresholds]
- Security: [compliance requirements]
- Scalability: [growth expectations]
- Accessibility: [WCAG level]

## 6. Constraints and Assumptions
- Technical constraints
- Budget and timeline
- Assumptions that need validation

## 7. Success Metrics
- KPI 1: [metric with baseline and target]
- KPI 2: [metric with baseline and target]

## 8. Open Questions
- [Question 1] — Owner: [name], Due: [date]
- [Question 2]

## 9. Appendix
- Research artifacts, interview notes, competitive analysis
```

### PRD Quality Checklist

- [ ] Every requirement has a unique identifier (FR-001, NFR-001)
- [ ] Every requirement is testable with clear pass/fail criteria
- [ ] Goals are measurable with specific metrics
- [ ] Non-goals are explicitly stated
- [ ] All user personas are identified with context
- [ ] Dependencies and constraints are documented
- [ ] Open questions have owners and due dates
- [ ] Document has been reviewed by at least one stakeholder

---

## Scope Definition

### MoSCoW Prioritization

| Priority | Definition | Decision Criteria |
| --- | --- | --- |
| **Must Have** | System does not work without this | Regulatory, legal, core value proposition |
| **Should Have** | Important but system works without it | Significant business value, strong user demand |
| **Could Have** | Nice to have, include if time permits | Incremental improvement, user convenience |
| **Won't Have** | Explicitly excluded from this release | Future consideration, low ROI, out of scope |

### Scope Boundary Definition

Define scope with explicit inclusion and exclusion:

```markdown
## In Scope
- User authentication via OAuth 2.0 (Google, GitHub)
- Dashboard with real-time metrics (refresh every 30s)
- CSV export of report data

## Out of Scope (This Release)
- Custom SSO/SAML integration (planned for v2)
- Mobile app (web responsive only)
- Historical data migration from legacy system

## Assumptions
- Users have modern browsers (Chrome 90+, Firefox 88+, Safari 14+)
- Peak concurrent users will not exceed 500 in first 6 months
```

### Scope Creep Prevention

1. **Document the boundary**: Write down what is out of scope before starting
2. **Change request process**: New requirements go through evaluation, not direct inclusion
3. **Impact assessment**: Every scope addition requires estimating impact on timeline and budget
4. **Stakeholder sign-off**: Scope changes require approval from project sponsor

---

## User Story Mapping

### Story Map Structure

```
                    Activities (user goals)
                    ┌──────────────────────────┐
                    │  Browse  │ Purchase │ Track│
                    └──────────────────────────┘
                           │
                    User Tasks (steps to achieve goal)
                    ┌──────────────────────────┐
Release 1 ──────── │ Search  │ Add to   │ View │
                    │ Products│ Cart     │ Order│
                    └──────────────────────────┘
                    ┌──────────────────────────┐
Release 2 ──────── │ Filter  │ Save for │ Track│
                    │ Results │ Later    │ Ship │
                    └──────────────────────────┘
                    ┌──────────────────────────┐
Release 3 ──────── │ Recommend│ Wishlist │ Return│
                    │ Products│          │ Item  │
                    └──────────────────────────┘
```

### Writing Effective User Stories

**Format:** As a [persona], I want [action] so that [outcome].

**Good example:**
> As a sales manager, I want to filter the pipeline report by team member so that I can identify individual performance issues during weekly reviews.

**Bad example:**
> As a user, I want a filter button so that I can filter things.

The bad example lacks persona specificity, motivation, and context.

---

## Acceptance Criteria Patterns

### Given-When-Then (Gherkin)

```gherkin
Scenario: User applies discount code
  Given the user has items totaling $100 in their cart
  And a valid discount code "SAVE20" exists for 20% off
  When the user enters "SAVE20" in the discount field
  Then the cart total updates to $80
  And the discount line item shows "-$20.00"
  And the discount code field shows "Applied: SAVE20"
```

### Checklist Style

```markdown
**Story: User resets password**

Acceptance criteria:
- [ ] User receives reset email within 60 seconds of request
- [ ] Reset link expires after 24 hours
- [ ] Reset link can only be used once
- [ ] New password must meet complexity requirements (8+ chars, 1 uppercase, 1 number)
- [ ] User is redirected to login after successful reset
- [ ] Error message displayed for expired or invalid links (no information leakage)
```

### Acceptance Criteria Quality Rules

- Each criterion is independently testable
- Criteria use specific values, not vague terms ("fast" -> "under 200ms")
- Edge cases and error states are covered
- Security and accessibility implications are addressed
- No implementation details ("use Redis" -> "cache results for 5 minutes")

---

## Non-Functional Requirements Discovery

### Performance Questions

- What is the expected number of concurrent users?
- What response time is acceptable (P50, P95, P99)?
- What throughput is required (requests/second, transactions/minute)?
- Are there seasonal or event-driven traffic spikes?

### Security Questions

- What data sensitivity classification applies?
- What compliance frameworks apply (GDPR, HIPAA, SOC 2, PCI DSS)?
- What authentication and authorization mechanisms are required?
- What is the acceptable risk tolerance?

### Scalability Questions

- What growth rate is expected over the next 12 months?
- Should the system scale horizontally, vertically, or both?
- Are there data retention or archival requirements?

### Availability Questions

- What uptime SLA is required (99.9%, 99.99%)?
- What is the acceptable recovery time objective (RTO)?
- What is the acceptable recovery point objective (RPO)?
- Are there maintenance windows?

---

## Requirement Traceability

### Traceability Matrix

| Req ID | Requirement | User Story | Test Case | Status |
| --- | --- | --- | --- | --- |
| FR-001 | User can log in with Google OAuth | US-001 | TC-001, TC-002 | Approved |
| FR-002 | Dashboard refreshes every 30s | US-003 | TC-010 | Draft |
| NFR-001 | Page load under 2s (P95) | — | TC-050 | Approved |

### Benefits

- Ensures every requirement has corresponding test coverage
- Traces requirements back to business objectives
- Identifies orphaned tests (tests without requirements)
- Supports impact analysis when requirements change

---

## Priority Negotiation

### Techniques for Resolving Conflicting Priorities

1. **Impact vs. effort matrix**: Plot requirements on a 2x2 grid
2. **Weighted scoring**: Assign weights to criteria (business value, user impact, technical risk)
3. **Buy-a-feature game**: Give stakeholders a fixed budget to allocate across features
4. **Kano model**: Categorize as basic (expected), performance (more is better), or excitement (delighter)

### Facilitation Tips

- Present trade-offs, not opinions: "If we add X, we delay Y by two weeks"
- Use data over advocacy: user research, usage analytics, market data
- Document the decision and rationale, not just the outcome
- Revisit priorities at regular intervals as context changes
