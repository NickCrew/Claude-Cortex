# Design Process

Architectural decision-making, data integrity patterns, observability guidance, and API evolution strategies for backend services. Use when making design choices that affect reliability, maintainability, and long-term operational health.

## Architectural Decision Framework

### Architecture Decision Records (ADRs)

Capture significant design decisions in a lightweight, version-controlled format.

**ADR Template:**

```markdown
# ADR-NNN: [Title]

## Status
[Proposed | Accepted | Deprecated | Superseded by ADR-NNN]

## Context
What is the issue? What forces are at play? What constraints exist?

## Decision
What is the change being proposed or adopted?

## Consequences
### Positive
- [Benefit 1]
- [Benefit 2]

### Negative
- [Trade-off 1]
- [Trade-off 2]

### Neutral
- [Side effect that is neither good nor bad]
```

**When to write an ADR:**
- Choosing between competing technologies or patterns
- Introducing a new dependency or external service
- Changing data storage strategy or schema design
- Defining API versioning or authentication approach
- Any decision that would be hard to reverse later

### Trade-Off Analysis

Use a structured comparison when multiple options are viable.

| Criterion | Weight | Option A | Option B | Option C |
|-----------|--------|----------|----------|----------|
| Performance | High | Good | Excellent | Fair |
| Complexity | Medium | Low | High | Medium |
| Team expertise | High | Strong | Weak | Medium |
| Operational cost | Medium | Low | High | Medium |
| Reversibility | Low | Easy | Hard | Medium |

**Decision rules:**
- If one option dominates all others on high-weight criteria, choose it
- If trade-offs are balanced, prefer the simpler, more reversible option
- If uncertainty is high, choose the option that preserves the most future flexibility
- Document the reasoning, not just the choice

### Decision Checklist

- [ ] Problem statement is clear and bounded
- [ ] At least two alternatives were considered
- [ ] Trade-offs are documented with weights
- [ ] The decision is reversible, or the cost of reversal is acceptable
- [ ] Affected teams have been consulted
- [ ] The ADR is committed alongside the implementing code

## Data Integrity Patterns

### Transactions

**ACID guarantees and when to relax them:**

| Property | Meaning | When to relax |
|----------|---------|---------------|
| Atomicity | All or nothing | Never for financial data; consider sagas for distributed workflows |
| Consistency | Valid state transitions only | Eventual consistency acceptable for read models |
| Isolation | Concurrent transactions don't interfere | Read-committed sufficient for most reads |
| Durability | Committed data survives crashes | Async replication acceptable for non-critical data |

**Transaction boundaries:**
- Keep transactions as short as possible
- Never hold a transaction open across network calls
- Use optimistic concurrency for read-heavy workloads
- Use pessimistic locking only for high-contention writes

### Idempotency Keys

Prevent duplicate side effects from retried requests.

```
Client generates: Idempotency-Key: <UUID>
Server behavior:
  1. Check if key exists in idempotency store
  2. If yes → return cached response (200, not 409)
  3. If no  → execute request, store response keyed by UUID
  4. Expire keys after 24-48 hours
```

**Implementation checklist:**
- [ ] Keys are stored durably (database, not in-memory cache)
- [ ] Key + response are written atomically with the business operation
- [ ] Expired keys are cleaned up on a schedule
- [ ] Collision handling is defined (reject or overwrite)

### Optimistic Locking

Detect conflicting writes without holding locks.

```
1. Read resource with version: GET /users/123 → { version: 7, name: "Alice" }
2. Update with version check:
   PUT /users/123
   If-Match: "7"
   { name: "Alicia" }
3. Server checks: current version == 7?
   - Yes → update, set version = 8, return 200
   - No  → return 409 Conflict with current state
```

**When to use:**
- Low-contention resources where conflicts are rare
- User-facing forms with edit-and-save workflows
- Any resource where "last write wins" is unacceptable

### Consistency Patterns Summary

| Pattern | Use When | Trade-off |
|---------|----------|-----------|
| Strong consistency | Financial transactions, inventory | Higher latency, lower throughput |
| Eventual consistency | Read models, analytics, caches | Stale reads possible |
| Causal consistency | Chat, collaboration | Complex to implement |
| Read-your-writes | User profile updates | Session affinity required |

## Observability Guidance

### Structured Logging

Emit machine-parseable logs with consistent fields.

**Required fields for every log entry:**

| Field | Purpose | Example |
|-------|---------|---------|
| `timestamp` | When it happened | `2024-01-15T10:30:00.123Z` |
| `level` | Severity | `info`, `warn`, `error` |
| `message` | Human-readable description | `"Payment processed"` |
| `request_id` | Correlation across services | `req_a3f7c9b2` |
| `service` | Which service emitted it | `payment-service` |
| `duration_ms` | Operation timing | `142` |

**Logging levels:**
- **error:** Something failed that requires attention (alerts)
- **warn:** Something unexpected that might need attention (dashboards)
- **info:** Significant business events (audit trail)
- **debug:** Diagnostic detail (disabled in production by default)

**Anti-patterns:**
- Logging sensitive data (PII, credentials, tokens)
- Using string interpolation instead of structured fields
- Logging inside tight loops
- Missing correlation IDs across service boundaries

### Distributed Tracing

Track requests across service boundaries.

**Trace propagation headers:**
```
traceparent: 00-<trace-id>-<span-id>-<flags>
tracestate: vendor=value
```

**Span naming conventions:**
- `HTTP GET /users/{id}` -- inbound request
- `db.query SELECT users` -- database call
- `http.client GET payment-service` -- outbound call
- `queue.publish orders` -- message publish

### Metrics (RED + USE)

**RED method (request-driven services):**
- **Rate:** Requests per second
- **Errors:** Failed requests per second
- **Duration:** Latency distribution (p50, p95, p99)

**USE method (resource-driven systems):**
- **Utilization:** Percentage of resource capacity in use
- **Saturation:** Queue depth or backlog
- **Errors:** Resource-level error counts

**Key metrics to instrument:**
- [ ] Request rate and error rate per endpoint
- [ ] Latency percentiles (p50, p95, p99) per endpoint
- [ ] Database connection pool utilization
- [ ] Queue depth and consumer lag
- [ ] Cache hit/miss ratio
- [ ] External dependency latency and error rate

### Alerting Guidelines

| Severity | Condition | Response Time | Example |
|----------|-----------|---------------|---------|
| Critical | Service down or data loss risk | < 5 min | Error rate > 50% for 2 min |
| High | Significant degradation | < 30 min | p99 latency > 5s for 5 min |
| Medium | Elevated errors or slow trend | < 4 hr | Error rate > 5% for 15 min |
| Low | Informational / capacity planning | Next business day | Disk usage > 80% |

**Alert quality rules:**
- Every alert must have a runbook link
- Alerts that never fire should be reviewed (threshold too high?)
- Alerts that fire constantly should be tuned or demoted (alert fatigue)
- Page only for conditions that require immediate human action

## API Evolution Strategies

### Versioning Lifecycle

```
v1 (current) ──► v2 (beta) ──► v2 (current) ──► v1 (deprecated) ──► v1 (sunset)
```

**Phase definitions:**

| Phase | Description | Duration |
|-------|-------------|----------|
| Beta | Available for testing, no stability guarantees | 1-3 months |
| Current | Stable, fully supported, recommended for use | Until next version |
| Deprecated | Supported but no new features, migration urged | 6-12 months |
| Sunset | Removed, returns 410 Gone | After deprecation period |

### Deprecation Communication

```http
Sunset: Sat, 31 Dec 2025 23:59:59 GMT
Deprecation: true
Link: <https://api.example.com/v2/docs>; rel="successor-version"
```

**Deprecation checklist:**
- [ ] Sunset header added to all deprecated endpoints
- [ ] Migration guide published with before/after examples
- [ ] Usage analytics identify remaining consumers
- [ ] Direct outreach to high-volume consumers
- [ ] Monitoring tracks migration progress
- [ ] Grace period allows buffer after sunset date

### Non-Breaking Changes (Safe within a version)

- Adding new optional fields to responses
- Adding new optional query parameters
- Adding new endpoints
- Adding new enum values (if clients handle unknown values)
- Relaxing validation (accepting wider input)

### Breaking Changes (Require new version)

- Removing or renaming fields
- Changing field types
- Tightening validation (rejecting previously valid input)
- Changing URL structure
- Modifying authentication requirements
- Changing error response format

### Migration Path Template

```markdown
## Migrating from v1 to v2

### Breaking Changes
1. `user.name` split into `user.first_name` and `user.last_name`
2. Pagination changed from offset to cursor-based

### Step-by-Step
1. Update client to handle both `name` and `first_name`/`last_name`
2. Switch pagination calls to cursor-based
3. Update base URL from `/v1/` to `/v2/`
4. Remove v1 compatibility code

### Timeline
- v2 beta available: [date]
- v1 deprecated: [date]
- v1 sunset: [date]
```

## Service Boundary Identification

### Boundary Heuristics

A service boundary should align with:

1. **Business capability:** A service owns a complete business function (payments, inventory, notifications)
2. **Data ownership:** A service owns its data store and is the single source of truth for that data
3. **Team ownership:** A service is owned by one team that can deploy it independently
4. **Change frequency:** Things that change together should be in the same service

### Boundary Anti-Patterns

| Anti-Pattern | Symptom | Fix |
|-------------|---------|-----|
| **Distributed monolith** | Every change requires deploying multiple services | Merge tightly coupled services |
| **Shared database** | Multiple services read/write the same tables | Split data ownership, use APIs |
| **Chatty services** | Excessive inter-service calls for single operations | Merge or batch calls |
| **Nano services** | Services so small they add overhead without value | Merge into cohesive units |

### Boundary Decision Checklist

- [ ] Can this service be deployed independently?
- [ ] Does it own its data (no shared tables)?
- [ ] Can one team maintain it without cross-team coordination for most changes?
- [ ] Does it have a clear, stable API contract?
- [ ] Would splitting it further add more coordination overhead than value?
