# Process Patterns

Resilient workflow patterns for multi-step, multi-agent task execution. Use these patterns when designing workflows that must handle failures gracefully, coordinate parallel work, and maintain consistency across distributed operations.

## Saga Pattern

Sagas manage long-running, multi-step processes where each step can be compensated (undone) if a later step fails.

### Orchestration (Central Coordinator)

A single coordinator directs each step and decides what to do on failure.

```
Coordinator
  ├─ Step 1: Reserve inventory  → Compensate: Release inventory
  ├─ Step 2: Charge payment     → Compensate: Refund payment
  ├─ Step 3: Ship order          → Compensate: Cancel shipment
  └─ Step 4: Send confirmation   → Compensate: Send cancellation
```

**When to use:**
- Clear sequential dependencies between steps
- Central visibility into workflow state is required
- You need deterministic retry and compensation ordering

**Trade-offs:**
- Single point of failure at the coordinator
- Easier to reason about and debug
- Coordinator must be durable (persist state across restarts)

### Choreography (Event-Driven)

Each participant listens for events and acts independently. No central coordinator.

```
InventoryService  ──(InventoryReserved)──►  PaymentService
PaymentService    ──(PaymentCharged)──────►  ShippingService
ShippingService   ──(OrderShipped)────────►  NotificationService
```

**When to use:**
- Loosely coupled services with independent lifecycles
- High throughput where central coordination is a bottleneck
- Teams own their own services end-to-end

**Trade-offs:**
- Harder to trace and debug across services
- Risk of implicit coupling through event schemas
- Compensation logic is distributed and harder to verify

### Decision Checklist

- [ ] Are steps strictly sequential? → Orchestration
- [ ] Do services need independent scaling? → Choreography
- [ ] Is end-to-end visibility critical? → Orchestration
- [ ] Are teams autonomous with separate deploy cycles? → Choreography
- [ ] Is the failure/compensation logic complex? → Orchestration

## Compensation and Rollback Strategies

### Compensation Design Principles

1. **Every forward step gets a compensating action** defined at design time
2. **Compensations run in reverse order** of the original steps
3. **Compensations must be idempotent** (safe to retry)
4. **Semantic undo, not literal undo** -- refunding a charge is not the same as never charging

### Compensation Table Template

| Step | Forward Action | Compensation | Idempotent? | Notes |
|------|---------------|--------------|-------------|-------|
| 1 | Create order record | Mark order cancelled | Yes | Soft delete, never hard delete |
| 2 | Reserve inventory | Release reservation | Yes | Check reservation exists first |
| 3 | Charge payment | Issue refund | Yes | Use idempotency key |
| 4 | Send notification | Send correction notice | Yes | Append-only |

### Rollback Strategies

**Immediate rollback:** Compensate all completed steps as soon as any step fails. Best for atomic-feeling operations.

**Deferred rollback:** Queue compensations for later execution. Best when compensations are expensive or external (e.g., refund processing).

**Partial rollback:** Only compensate steps that are inconsistent. Best when some steps are independently valuable.

### Failure During Compensation

- Log the compensation failure with full context
- Retry with exponential backoff
- After retry exhaustion, escalate to a dead letter queue or human operator
- Never silently swallow a failed compensation

## Split/Join Patterns for Parallel Work

### Static Split/Join

Fan out to a known set of parallel tasks, then wait for all to complete.

```
        ┌─► Task A ─┐
Start ──┼─► Task B ──┼──► Join ──► Continue
        └─► Task C ─┘
```

**Join strategies:**
- **All (barrier):** Wait for every branch. Use when all results are required.
- **Any (race):** Continue as soon as one branch completes. Use for redundant execution or fastest-wins.
- **N-of-M (quorum):** Wait for N of M branches. Use for consensus or fault-tolerant reads.
- **Timeout with partial:** Wait up to a deadline, then proceed with whatever completed. Use when partial results are acceptable.

### Dynamic Split/Join

The number of parallel branches is determined at runtime (e.g., one branch per file in a directory).

```
Input list ──► Map (spawn one task per item) ──► Reduce (aggregate results)
```

**Considerations:**
- Set a concurrency limit to avoid resource exhaustion
- Handle individual branch failures without failing the whole fan-out
- Collect partial results and errors separately

### Scatter-Gather

Broadcast a request to multiple agents, collect responses, and merge.

**Use when:** Multiple agents may have relevant information, and you want the union of their knowledge.

## Circuit Breaker Patterns for Task Failure

### States

```
CLOSED ──(failures exceed threshold)──► OPEN
OPEN ──(timeout expires)──► HALF-OPEN
HALF-OPEN ──(probe succeeds)──► CLOSED
HALF-OPEN ──(probe fails)──► OPEN
```

### Configuration Template

| Parameter | Typical Value | Description |
|-----------|--------------|-------------|
| Failure threshold | 3-5 failures | Consecutive failures before opening |
| Reset timeout | 30-60 seconds | Time in OPEN before attempting HALF-OPEN |
| Probe count | 1-3 requests | Requests allowed in HALF-OPEN |
| Success threshold | 2-3 successes | Consecutive successes to return to CLOSED |
| Monitored exceptions | Timeouts, 5xx | Which failures count toward the threshold |

### When to Apply

- [ ] Calling an external service that may be down
- [ ] Delegating to a sub-agent that may hang or crash
- [ ] Accessing a shared resource with contention
- [ ] Any step where repeated failure wastes resources

### Fallback Actions When Open

1. Return a cached/stale result
2. Use a degraded alternative path
3. Queue the work for later retry
4. Return an explicit "temporarily unavailable" signal

## Idempotency in Multi-Step Workflows

### Why Idempotency Matters

Retries are inevitable. Network failures, agent crashes, and timeouts all cause duplicate execution. Every step in a workflow must produce the same result whether executed once or many times.

### Idempotency Techniques

**Idempotency keys:** Assign a unique key per operation. Before executing, check if the key was already processed.

```
Step execution:
1. Generate key = hash(workflow_id + step_id + input)
2. Check: has this key been processed?
   - Yes → return stored result
   - No  → execute, store result keyed by idempotency key
```

**Natural idempotency:** Design operations so re-execution is inherently safe.
- `SET status = 'complete'` is idempotent
- `INCREMENT counter` is NOT idempotent

**Deduplication windows:** Accept duplicate messages but deduplicate within a time window using message IDs.

### Idempotency Checklist

- [ ] Every workflow step has a deterministic idempotency key
- [ ] Side effects (API calls, notifications) are guarded by deduplication
- [ ] Database writes use upsert or conditional writes
- [ ] File operations check for existing output before writing
- [ ] External calls use idempotency headers where supported
- [ ] Compensation actions are also idempotent
