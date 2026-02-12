# Postmortem Patterns

Blameless postmortem structure, root cause analysis techniques, action item tracking, and chaos engineering patterns. Use after incident resolution or when designing resilience testing programs.

## Blameless Postmortem Structure

### Core Principles

1. **No blame:** Focus on systems, processes, and conditions -- not individuals
2. **Assume good intent:** Everyone involved was doing their best with the information available
3. **Learn, don't punish:** The goal is prevention, not accountability
4. **Share widely:** Postmortems are organizational learning, not team shame

### Postmortem Document Template

```markdown
# Incident Postmortem: [Title]

**Date:** [Incident date]
**Severity:** P[0-3]
**Duration:** [Start time] to [End time] ([total duration])
**Incident Commander:** [Name]
**Author:** [Name]
**Status:** [Draft | Review | Final]

## Summary

[1-2 sentence description of what happened and the user impact]

## Impact

- **Users affected:** [Number or percentage]
- **Duration:** [How long users experienced the issue]
- **Revenue impact:** [If applicable]
- **Data impact:** [Any data loss or corruption]
- **SLA impact:** [Any SLA violations]

## Timeline

All times in [timezone].

| Time | Event |
|------|-------|
| HH:MM | [First signal / alert fired] |
| HH:MM | [On-call acknowledged] |
| HH:MM | [Severity classified as P_] |
| HH:MM | [Key investigation finding] |
| HH:MM | [Mitigation applied] |
| HH:MM | [Issue confirmed resolved] |
| HH:MM | [Monitoring confirmed stable] |

## Root Cause

[Detailed description of the root cause. What condition or change led to the failure?]

## Contributing Factors

- [Factor 1: e.g., missing monitoring for this failure mode]
- [Factor 2: e.g., deployment during high-traffic period]
- [Factor 3: e.g., no automated rollback configured]

## What Went Well

- [Thing 1: e.g., alert fired within 2 minutes of impact]
- [Thing 2: e.g., team coordinated effectively in war room]
- [Thing 3: e.g., rollback was smooth and fast]

## What Went Poorly

- [Thing 1: e.g., took 20 minutes to identify the failing service]
- [Thing 2: e.g., no runbook existed for this failure mode]
- [Thing 3: e.g., status page was not updated for 30 minutes]

## Action Items

| ID | Action | Owner | Priority | Due Date | Status |
|----|--------|-------|----------|----------|--------|
| 1 | [Action description] | [Name] | P1 | [Date] | Open |
| 2 | [Action description] | [Name] | P2 | [Date] | Open |

## Lessons Learned

[Key takeaways that should inform future design, process, or tooling decisions]
```

### Postmortem Meeting Facilitation

**Before the meeting:**
- Draft the postmortem document and share 24 hours in advance
- All participants review the timeline for accuracy
- Incident commander prepares the root cause analysis

**During the meeting (60-90 min):**
1. **Timeline review (15 min):** Walk through events, correct errors, fill gaps
2. **Root cause discussion (20 min):** Apply 5 Whys or fishbone analysis
3. **Contributing factors (15 min):** What made the incident worse or harder to resolve?
4. **What went well (10 min):** Reinforce effective practices
5. **Action items (20 min):** Define concrete, assignable, time-bounded actions

**After the meeting:**
- Finalize the document within 24 hours
- Distribute to the broader organization
- Enter action items into the tracking system
- Schedule follow-up review for action item completion

## Root Cause Analysis Techniques

### 5 Whys

Repeatedly ask "why" to drill past symptoms to the underlying cause.

**Example:**

```
Problem: Users received duplicate order confirmation emails.

Why 1: The email service sent the confirmation twice.
Why 2: The order completion event was published twice.
Why 3: The order service retried after a timeout.
Why 4: The message broker acknowledged slowly under load.
Why 5: The broker's disk was 95% full, causing write delays.

Root cause: No disk usage monitoring or alerting on the message broker.
Action: Add disk usage alerting at 80% threshold + auto-scaling.
```

**Guidelines:**
- Stop when you reach a systemic cause you can fix (process, tooling, design)
- Do not stop at "human error" -- ask why the system allowed the error
- Some incidents have multiple root causes; run 5 Whys for each branch
- Answers should be factual, not speculative

### Fishbone Diagram (Ishikawa)

Categorize contributing factors across standard dimensions.

```
                    ┌─ People: On-call unfamiliar with service
                    ├─ Process: No rollback runbook existed
Duplicate emails ───├─ Technology: No idempotency on email sends
                    ├─ Environment: Broker disk at 95%
                    ├─ Monitoring: No disk usage alerts
                    └─ External: Upstream traffic spike
```

**Standard categories:**
- **People:** Knowledge gaps, staffing, communication
- **Process:** Missing runbooks, unclear procedures, approval bottlenecks
- **Technology:** Bugs, missing features, architectural gaps
- **Environment:** Infrastructure, capacity, configuration
- **Monitoring:** Missing alerts, incorrect thresholds, observability gaps
- **External:** Third-party outages, traffic spikes, attacks

### Fault Tree Analysis

Work backward from the failure to identify all possible causes.

```
Top event: Service outage
├── AND: Load balancer failure
│   ├── OR: Config error
│   └── OR: Health check misconfigured
└── AND: No failover triggered
    ├── OR: Failover not configured
    └── OR: Failover health check also failed
```

**When to use:** Complex incidents with multiple interacting failures where 5 Whys is insufficient.

## Action Item Tracking

### Action Item Quality Criteria

Every action item must be:
- **Specific:** Clear description of what to do (not "improve monitoring")
- **Assignable:** One owner, not a team
- **Time-bounded:** Due date, not "when we get to it"
- **Verifiable:** Clear definition of done
- **Prioritized:** P1 (before next on-call rotation), P2 (this sprint), P3 (this quarter)

### Action Item Categories

| Category | Description | Examples |
|----------|-------------|---------|
| **Detection** | Improve ability to notice the problem | Add alert, improve dashboard |
| **Prevention** | Stop the problem from occurring | Fix bug, add validation, improve architecture |
| **Mitigation** | Reduce impact when it happens | Add circuit breaker, improve rollback, write runbook |
| **Process** | Improve team response | Update on-call procedures, conduct training |

### Tracking and Follow-Up

- Enter all action items into the team's issue tracker immediately
- Tag with `postmortem` and incident ID for traceability
- Review open postmortem action items weekly in team standup
- Escalate overdue P1 items to engineering manager
- Close action items only when verified complete (not just "code merged")

### Action Item Anti-Patterns

| Anti-Pattern | Problem | Better Alternative |
|-------------|---------|-------------------|
| "Be more careful" | Not actionable | Automate the check |
| "Improve monitoring" | Too vague | "Add alert for X metric when > Y for Z minutes" |
| "No owner assigned" | Will not get done | Assign a specific person |
| "Due: TBD" | Will be deprioritized | Set a concrete date |
| "Add more tests" | Unbounded | "Add regression test for this specific failure mode" |

## Chaos Engineering Patterns

### Fault Injection

Intentionally introduce failures to verify resilience.

**Common fault types:**

| Fault | Tool/Method | Validates |
|-------|-------------|-----------|
| Kill service instance | Process kill, pod delete | Auto-restart, health checks |
| Network latency | tc netem, Toxiproxy | Timeout handling, circuit breakers |
| Network partition | iptables, DNS override | Failover, split-brain handling |
| Disk full | fallocate, dd | Graceful degradation, alerting |
| CPU exhaustion | stress-ng | Autoscaling, load shedding |
| Dependency failure | Mock returning 500s | Fallback paths, error handling |
| Clock skew | chrony offset | Time-dependent logic |

### Fault Injection Checklist

- [ ] Hypothesis defined: "We believe [X] will happen when [fault]"
- [ ] Blast radius limited (single instance, canary, staging)
- [ ] Rollback mechanism ready (kill switch for the experiment)
- [ ] Monitoring in place to observe the effect
- [ ] Team is aware the experiment is running
- [ ] Abort criteria defined (stop if real user impact exceeds N%)

### Game Days

Structured exercises where teams practice incident response against simulated failures.

**Game Day Planning Template:**

```markdown
## Game Day: [Title]

**Date:** [Date and time]
**Duration:** [Expected duration]
**Facilitator:** [Name]
**Participants:** [Team members]

### Scenario
[Description of the simulated incident]

### Objectives
- [ ] Validate alerting detects the failure within [N] minutes
- [ ] Validate team can triage to correct severity
- [ ] Validate mitigation can be applied within [N] minutes
- [ ] Validate communication protocols are followed

### Ground Rules
- This is practice, not evaluation
- Facilitator controls the scenario progression
- Anyone can call "stop" if real production impact is detected
- Document all observations in real time

### Debrief Questions
1. Did alerts fire as expected?
2. Was the right team engaged quickly enough?
3. Were runbooks adequate?
4. What would we do differently in a real incident?
```

**Game day cadence:**
- Quarterly for critical services
- After major architecture changes
- When onboarding new on-call engineers
- After any P0 incident (test the fixes)

## Resilience Testing Methodology

### Resilience Maturity Levels

| Level | Description | Activities |
|-------|-------------|-----------|
| **1 - Reactive** | Fix failures after they happen | Postmortems, basic monitoring |
| **2 - Aware** | Know where failures could happen | Failure mode analysis, risk registry |
| **3 - Proactive** | Test for failures before they happen | Chaos experiments in staging |
| **4 - Continuous** | Regularly validate resilience in production | Automated chaos, game days |
| **5 - Anti-fragile** | Systems improve through failure | Feedback loops, auto-remediation |

### Resilience Testing Checklist

For each critical service, validate:

- [ ] **Single instance failure:** Service recovers when one instance dies
- [ ] **Dependency timeout:** Service handles slow dependencies gracefully
- [ ] **Dependency outage:** Service degrades (not crashes) when dependency is down
- [ ] **Network partition:** Service handles split-brain scenarios
- [ ] **Load spike:** Service sheds load or scales under 3x normal traffic
- [ ] **Disk full:** Service alerts and degrades before crashing
- [ ] **Configuration error:** Service fails fast with clear error on bad config
- [ ] **Rollback:** Previous version can be deployed within 5 minutes
- [ ] **Data corruption:** Backup restore has been tested within the last quarter

### Steady-State Hypothesis

Before running any chaos experiment, define what "normal" looks like:

```
Steady state:
- Request success rate > 99.9%
- p99 latency < 200ms
- Error rate < 0.1%
- No alerts firing

Experiment: Kill 1 of 3 service instances

Hypothesis: Steady state metrics remain within 10% of baseline
            within 60 seconds of the fault injection.

Abort if: Error rate > 5% for more than 30 seconds.
```
