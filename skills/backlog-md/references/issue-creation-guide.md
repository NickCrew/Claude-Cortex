# Issue Creation Patterns

Three distinct scenarios with different requirements. Required field: **type label + priority**.

## Scenario 1: Deferred Issues During Feature Implementation

**When:** You're implementing a feature and discover a bug, edge case, or tech debt.
**How:** File immediately with implementation plan (you have context now).
**Plan rule:** ✅ INCLUDE detailed plan — you'll likely fix it.

### Example Workflow

During implementation, you find that error handling is incomplete:

```bash
backlog task create "Handle null reference in payment processor" \
  -d "During PaymentService refactor, found case where null processor reference isn't handled, could cause runtime error in production" \
  -l bug,remediation \
  -l synapse-pingora \
  -p 2 \
  --ac "Service returns meaningful error when processor is null" \
  --ac "Edge case handled in existing tests" \
  --plan "1. Add null check before processor call\n2. Add test for null case\n3. Verify with existing integration tests"
```

### Field Checklist

- ✅ **Title**: Clear, specific (not "Fix bugs")
- ✅ **Description**: What you found and why it matters
- ✅ **Type label**: `remediation` (for deferred review issues)
- ✅ **App label(s)**: What app(s) this affects
- ✅ **Priority**: Use your judgment (most are P2)
- ✅ **Acceptance Criteria**: What "done" means
- ✅ **Implementation Plan**: Steps to fix it

## Scenario 2: Reporting Found Issues (No Plan)

**When:** You discover an issue but won't be implementing it immediately.
**How:** File without plan (let the assignee plan it).
**Plan rule:** ❌ DO NOT include plan — implementer will add it.

### Example Workflow

You find a security issue but it's not your responsibility to fix:

```bash
backlog task create "Potential XSS vulnerability in user input sanitization" \
  -d "Found unsanitized user input accepted in comment field. Could allow XSS if user provides HTML/script tags." \
  -l bug \
  -l signal-horizon-ui,signal-horizon-api \
  -p 1 \
  --ac "All user inputs sanitized before rendering" \
  --ac "XSS test coverage added"
```

**No plan**, no implementation details. Implementer adds plan when they claim it.

### Field Checklist

- ✅ **Title**: Clear, specific
- ✅ **Description**: What's broken, why it matters
- ✅ **Type label**: bug|feature|documentation|refactor
- ✅ **App label(s)**: What affects this
- ✅ **Priority**: P0|P1|P2, use `priority-review` label if unsure
- ✅ **Acceptance Criteria**: Success conditions
- ❌ **NO Implementation Plan**: Leave this for implementer

## Scenario 3: Audit Findings (Structured)

**When:** Reviewer is doing security audit or code quality review.
**How:** Create issues with dependencies and milestones.
**Plan rule:** ✅ INCLUDE plan — you have audit context.

### Example Workflow

Security audit finds three related issues:

```bash
# Issue 1: Core vulnerability
backlog task create "Remove hardcoded API credentials from environment configs" \
  -d "Security audit found hardcoded credentials in .env.example and config files. Violates OWASP A02:2021. Must use environment variables." \
  -l bug,remediation \
  -l synapse-pingora,signal-horizon-api \
  -p 1 \
  --ac "No hardcoded secrets in any config files" \
  --ac "All secrets loaded from env variables" \
  --plan "1. Scan codebase for hardcoded credentials\n2. Update config to use env vars\n3. Update docs for setup\n4. Run security linter"

# Issue 2: Depends on issue 1
backlog task create "Update deployment docs for credential handling" \
  -d "Related to credential hardcoding fix. Document new env var requirements." \
  -l documentation,remediation \
  -l synapse-pingora,signal-horizon-api \
  -p 2 \
  --ac "Deployment guide includes env var setup" \
  --ac "Example .env.example provided"

# Issue 3: Different finding
backlog task create "Upgrade deprecated crypto library" \
  -d "Audit found crypto-js version 4.1.0 is vulnerable (CVE-2023-xyz). Upgrade to 4.1.5+." \
  -l bug,remediation \
  -l signal-horizon-api \
  -p 1 \
  --ac "Crypto-js updated to 4.1.5 or higher" \
  --ac "All crypto calls still functional after upgrade"
```

### With Dependencies and Milestones

After creating issues, link them:

```bash
# Link issue 2 to depend on issue 1
backlog task edit <issue-2-id> --dep <issue-1-id>

# Assign to milestone if needed
backlog task edit <issue-1-id> --milestone "Security Hardening Q1"
```

### Field Checklist

- ✅ **Title**: Clear, specific
- ✅ **Description**: What audit found, why it matters, any standards violated
- ✅ **Type label**: bug|remediation (usually for audit findings)
- ✅ **App label(s)**: What affects this
- ✅ **Priority**: Based on severity (security = usually P0/P1)
- ✅ **Acceptance Criteria**: How to verify fix
- ✅ **Implementation Plan**: Steps to remediate
- ✅ **Dependencies** (if applicable): Link related issues
- ✅ **Milestone** (if applicable): Assign to release cycle

## Scenario 4: Explicitly Asked to Plan Work

**When:** User says "Plan out this work" or "Create a task and plan how you'd do it".
**How:** Create with detailed, step-by-step implementation plan.
**Plan rule:** ✅ INCLUDE detailed plan — requirement, not deferral.

### Example Workflow

User asks you to plan a feature:

```bash
backlog task create "Implement real-time notifications for order status" \
  -d "Add real-time push notifications when order status changes. Users should receive browser notifications and see update in dashboard within 2 seconds." \
  -l feature \
  -l signal-horizon-ui,signal-horizon-api \
  -p 2 \
  --ac "Browser push notification sent on status change" \
  --ac "Dashboard updates in real-time (< 2s latency)" \
  --ac "Works offline gracefully (queues until reconnect)" \
  --ac "E2E test coverage for notification flow" \
  --plan "1. Design notification schema and API contract\n2. Implement backend status change webhook\n3. Add notification queue service\n4. Implement browser notification handler\n5. Add dashboard real-time sync via WebSocket\n6. Write integration tests\n7. Performance test latency requirements"
```

### Detailed Plan Guidelines

- **Be thorough**: Break down major steps
- **Include research**: If uncertain about approach, include "1. Research X options"
- **Include tests**: Add test/validation steps
- **Include doc**: Add "Update docs" if applicable
- **Phase-based**: Can organize by layer (backend/frontend) or workflow phase

## Decision Tree: Which Scenario?

```
Are you implementing a feature?
  ├─ Yes, found a bug/tech debt → Scenario 1 (defer with plan)
  └─ No, just reporting it → Scenario 2 (report no plan)

Are you reviewing/auditing?
  └─ Yes → Scenario 3 (audit with plan + dependencies)

Did user explicitly ask for a plan?
  └─ Yes → Scenario 4 (plan as required)
```

## Common Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| Reporting without type label | Issue won't be categorized properly | Always add type label (bug, feature, etc.) |
| Adding plan when reporting | Constrains implementer's approach | Only add plan for scenarios 1, 3, 4 |
| Using wrong remediation | `remediation` is for deferred review issues only | Don't use for new feature ideas |
| Missing priority | Can't be triaged | Always set P0-P4 (or priority-review) |
| Vague description | Implementer doesn't understand context | Include "why" and "what" clearly |
| Too detailed AC | Implementer interprets as implementation steps | Frame as outcomes, not methods |

## Acceptance Criteria Quality

Good (outcome-focused):
- "API returns 200 with correct schema"
- "User sees success message after form submission"
- "Response time < 100ms for 1000 records"

Bad (implementation-focused):
- "Add validateInput() function"
- "Use Promise.all() for parallel requests"
- "Refactor to strategy pattern"

AC should be testable, not prescriptive.
