# Triage Framework

Severity classification, cascade prevention, communication protocols, and escalation paths for production incidents. Use during active incidents or when establishing incident response procedures.

## Severity Classification (P0-P3)

### P0 -- Critical

**Definition:** Complete service outage, active data loss, or security breach affecting all users.

| Attribute | Requirement |
|-----------|-------------|
| Response time | < 5 minutes |
| Incident commander | Required (senior engineer or SRE) |
| Communication cadence | Every 15 minutes to stakeholders |
| War room | Immediately opened |
| Escalation | VP/Director notified within 15 minutes |
| Postmortem | Required within 48 hours |

**Examples:**
- Production database unreachable
- Authentication service completely down
- Active data corruption or loss
- Security breach with confirmed exfiltration
- Payment processing halted

### P1 -- High

**Definition:** Major feature broken or significant degradation affecting a large subset of users.

| Attribute | Requirement |
|-----------|-------------|
| Response time | < 30 minutes |
| Incident commander | Required |
| Communication cadence | Every 30 minutes to stakeholders |
| War room | Opened if not resolved in 30 minutes |
| Escalation | Manager notified within 30 minutes |
| Postmortem | Required within 1 week |

**Examples:**
- Payment processing failing for one region
- Search functionality returning errors for 20%+ of queries
- API latency 10x above normal
- Mobile app crash on launch for specific OS version

### P2 -- Medium

**Definition:** Degraded performance or partial feature loss with workarounds available.

| Attribute | Requirement |
|-----------|-------------|
| Response time | < 4 hours |
| Incident commander | Optional (on-call engineer handles) |
| Communication cadence | Status update at start and resolution |
| War room | Not required |
| Escalation | If unresolved after 8 hours |
| Postmortem | Recommended |

**Examples:**
- Elevated latency (2-3x normal) on non-critical endpoints
- Background job processing delayed
- Non-critical third-party integration down
- Report generation slow but functional

### P3 -- Low

**Definition:** Minor issue with minimal user impact. Workaround exists or issue is cosmetic.

| Attribute | Requirement |
|-----------|-------------|
| Response time | Next business day |
| Incident commander | Not required |
| Communication cadence | Ticket update on resolution |
| War room | Not required |
| Escalation | Not required |
| Postmortem | Not required |

**Examples:**
- UI rendering glitch in edge case
- Non-critical cron job failed (will retry)
- Slow dashboard load for internal tool
- Minor logging error that does not affect functionality

### Severity Decision Tree

```
Is data being lost or corrupted?
├─ Yes → P0
└─ No
   Is there a security breach?
   ├─ Yes → P0
   └─ No
      Is the primary service completely down?
      ├─ Yes → P0
      └─ No
         Is a major feature broken for many users?
         ├─ Yes → P1
         └─ No
            Is performance significantly degraded?
            ├─ Yes → P2
            └─ No → P3
```

## Cascade Prevention

### Circuit Breakers

Automatically stop calling a failing dependency to prevent cascading failure.

**Implementation checklist:**
- [ ] Every external dependency has a circuit breaker
- [ ] Failure thresholds are tuned per dependency (not one-size-fits-all)
- [ ] OPEN state returns a meaningful fallback (cached data, degraded response, error)
- [ ] HALF-OPEN probes are lightweight (health check, not full request)
- [ ] Circuit breaker state is observable (metrics, dashboard)
- [ ] Alerts fire when a circuit breaker opens

**Configuration template:**

```
Dependency: [service name]
Failure threshold: [N] failures in [T] seconds
Reset timeout: [T] seconds
Fallback: [cached response | error message | degraded mode]
```

### Bulkhead Isolation

Partition resources so failure in one area cannot exhaust resources for another.

**Patterns:**
- **Thread pool isolation:** Separate thread pools per dependency
- **Connection pool isolation:** Dedicated connection pools per downstream service
- **Process isolation:** Critical and non-critical workloads in separate processes
- **Infrastructure isolation:** Separate clusters for critical vs batch workloads

**Checklist:**
- [ ] Critical path dependencies have dedicated resource pools
- [ ] Non-critical background work cannot starve critical request handling
- [ ] Resource limits are set per pool (max connections, max threads)
- [ ] Pool exhaustion triggers alerts, not silent queuing

### Load Shedding

Intentionally drop low-priority work to preserve capacity for high-priority traffic.

**Priority tiers:**

| Priority | Traffic Type | Shed When |
|----------|-------------|-----------|
| Critical | Health checks, authentication | Never |
| High | Core user requests | > 95% capacity |
| Medium | Secondary features, analytics | > 80% capacity |
| Low | Background jobs, prefetch | > 70% capacity |

**Implementation:**
- Use request priority headers or path-based classification
- Return 503 with Retry-After header for shed requests
- Monitor shed rate as a metric (shedding > 0 is an alert)

### Graceful Degradation Strategies

| Strategy | Description | Example |
|----------|-------------|---------|
| Feature flags | Disable non-critical features | Turn off recommendations during high load |
| Cached fallback | Serve stale data | Show cached search results when search service is down |
| Read-only mode | Disable writes | Allow browsing but not purchasing during payment outage |
| Static fallback | Serve pre-generated content | Show static landing page when CMS is down |
| Queue and retry | Accept but defer processing | Accept orders, process when backend recovers |

## Communication Protocols

### Status Page Updates

**Template for status page entry:**

```
[TIMESTAMP] - [STATUS: Investigating | Identified | Monitoring | Resolved]

Impact: [Brief description of user-visible impact]
Current status: [What we know and what we're doing]
Next update: [When to expect the next update]
```

**Update cadence:**
- P0: Every 15 minutes until resolved
- P1: Every 30 minutes until resolved
- P2: At start and resolution
- P3: At resolution only

### Stakeholder Notification Template

```
Subject: [P0/P1] [Service] - [Brief impact description]

Severity: P[0-3]
Start time: [ISO 8601 timestamp]
Impact: [Who is affected and how]
Current status: [What we know]
Actions taken: [What we've done so far]
ETA: [If known, otherwise "investigating"]
Next update: [When]
Incident commander: [Name]
War room: [Link/channel]
```

### Internal Communication Rules

1. **One source of truth:** All updates go through the incident channel, not DMs
2. **Facts, not speculation:** Share what you know, flag what you suspect
3. **Timestamp everything:** Every action and observation gets a timestamp
4. **No blame:** Focus on what happened, not who caused it
5. **Clear handoffs:** When rotating, explicitly hand off context

## Escalation Paths

### Escalation Triggers

| Condition | Action |
|-----------|--------|
| P0 not acknowledged in 5 min | Page backup on-call |
| P0/P1 not mitigated in 30 min | Escalate to engineering manager |
| P0 not resolved in 1 hour | Escalate to VP/Director |
| Any severity affecting revenue | Notify finance and business stakeholders |
| Security incident confirmed | Notify security team and legal |
| Data breach suspected | Invoke data breach response plan |

### Escalation Checklist

- [ ] Primary on-call paged and acknowledged
- [ ] If no acknowledgment in 5 min, secondary on-call paged
- [ ] Incident commander assigned
- [ ] Relevant team leads notified
- [ ] Status page updated
- [ ] Customer support briefed with talking points
- [ ] Executive stakeholders notified (P0/P1 only)

### On-Call Responsibilities

**During incident:**
- Acknowledge page within 5 minutes
- Assess severity and open incident channel
- Begin investigation and document findings in real time
- Coordinate with other teams as needed
- Provide status updates at the required cadence

**After incident:**
- Ensure monitoring confirms resolution
- Draft incident timeline
- Schedule postmortem if required
- Update runbooks with any new learnings
- Hand off to next on-call if shift ends during incident
