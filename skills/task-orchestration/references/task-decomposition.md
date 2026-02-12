# Task Decomposition

Structured approaches for breaking complex work into plannable, assignable, and trackable units. Use when facing ambiguous requirements, multi-agent coordination, or work that needs dependency analysis and parallel execution planning.

## Planning Methodology (Work Breakdown Structure)

### Top-Down Decomposition

Start from the deliverable and recursively split until each leaf is a single assignable unit of work.

```
Level 0: Project / Epic
  Level 1: Feature or Milestone
    Level 2: Task (assignable, estimable)
      Level 3: Subtask (single action, <2 hours)
```

### Decomposition Rules

1. **100% rule:** Child tasks must fully account for the parent -- nothing missing, nothing extra
2. **Mutual exclusivity:** No overlap between sibling tasks
3. **Outcome-oriented:** Name tasks by what they produce, not what they do
4. **Testable completion:** Every task has a clear "done" definition

### Work Breakdown Template

```markdown
## [Epic Name]

### [Feature 1]
- [ ] Task 1.1: [Outcome] — Owner: TBD, Est: S/M/L
  - Acceptance: [How to verify]
  - Dependencies: [None | Task X.Y]
- [ ] Task 1.2: [Outcome] — Owner: TBD, Est: S/M/L

### [Feature 2]
...
```

### Decomposition Checklist

- [ ] Every leaf task can be completed by one agent/person
- [ ] Every leaf task has a verifiable completion criterion
- [ ] No task exceeds 4 hours of estimated effort
- [ ] Dependencies between tasks are explicitly listed
- [ ] The sum of leaf tasks equals the parent deliverable

## Dependency Mapping

### Dependency Types

| Type | Description | Example |
|------|-------------|---------|
| **Finish-to-Start (FS)** | B cannot start until A finishes | Deploy after tests pass |
| **Start-to-Start (SS)** | B cannot start until A starts | Logging starts when service starts |
| **Finish-to-Finish (FF)** | B cannot finish until A finishes | Docs finish when code finishes |
| **Start-to-Finish (SF)** | B cannot finish until A starts | Rare; legacy handoff |

### Critical Path Analysis

The critical path is the longest chain of dependent tasks. It determines the minimum project duration.

**Finding the critical path:**
1. List all tasks with durations and dependencies
2. Forward pass: calculate earliest start/finish for each task
3. Backward pass: calculate latest start/finish for each task
4. Slack = Latest Start - Earliest Start
5. Tasks with zero slack are on the critical path

**Using the critical path:**
- Prioritize critical-path tasks for resource allocation
- Add buffers to critical-path tasks, not to every task
- Monitor critical-path tasks more closely for delays
- Reassign non-critical tasks to free up critical-path resources

### Blocker Identification

Proactively identify blockers before they stall work:

- [ ] **External dependencies:** APIs, services, or data from other teams
- [ ] **Shared resources:** Files, databases, or environments with contention
- [ ] **Knowledge gaps:** Tasks requiring expertise not yet available
- [ ] **Approval gates:** Reviews, sign-offs, or compliance checks
- [ ] **Environment setup:** Infrastructure or tooling not yet provisioned

### Dependency Visualization

```
Task A ──► Task C ──► Task E ──► Done
Task B ──► Task C
Task B ──► Task D ──► Task E

Critical path: B → C → E (if B + C + E > A + C + E)
```

## Task Sizing and Estimation Heuristics

### T-Shirt Sizing

| Size | Duration | Complexity | Uncertainty |
|------|----------|-----------|-------------|
| **XS** | < 30 min | Single file, mechanical change | None |
| **S** | 30 min - 2 hr | Few files, clear approach | Low |
| **M** | 2 - 4 hr | Multiple files, some design decisions | Medium |
| **L** | 4 - 8 hr | Cross-cutting, requires investigation | High |
| **XL** | > 8 hr | **Needs further decomposition** | Very high |

### Estimation Guidelines

1. **If it feels XL, decompose further** -- XL tasks are planning failures
2. **Estimate from the bottom up** -- aggregate leaf task estimates, don't top-down guess
3. **Include uncertainty explicitly** -- "2-4 hours" is more honest than "3 hours"
4. **Calibrate on completed work** -- track actual vs estimated to improve over time
5. **Separate effort from elapsed time** -- a 2-hour task blocked for a day is still S-sized effort

### Effort vs Complexity Matrix

|  | Low Effort | High Effort |
|--|-----------|-------------|
| **Low Complexity** | Automate or batch | Delegate; parallelize |
| **High Complexity** | Timebox investigation | Decompose; spike first |

### When to Spike

Run a timeboxed investigation (spike) before estimating when:
- The technology is unfamiliar
- The approach is unclear after 10 minutes of analysis
- Multiple viable solutions exist and the trade-offs are unknown
- Integration points are undocumented

**Spike output:** A written recommendation with enough detail to estimate the real task.

## Parallel vs Sequential Execution Decisions

### Decision Framework

```
Can tasks run independently?
├─ Yes: Are there shared resources?
│   ├─ No  → Run in parallel
│   └─ Yes → Can we partition the resource?
│       ├─ Yes → Parallel with partitioning
│       └─ No  → Sequential (or lock-based parallel)
└─ No: Is there a data dependency?
    ├─ Yes → Sequential (respect the dependency)
    └─ No  → Check for ordering requirements
        ├─ Yes → Sequential
        └─ No  → Parallel
```

### Parallelization Checklist

- [ ] Tasks do not read/write the same files
- [ ] Tasks do not depend on each other's output
- [ ] Combined resource usage stays within limits (CPU, memory, API rate limits)
- [ ] Failure of one task does not invalidate another's work
- [ ] Results can be merged without conflicts

### Concurrency Limits

Set explicit limits to avoid resource exhaustion:

| Resource | Typical Limit | Why |
|----------|--------------|-----|
| Parallel agents | 3-5 | Context switching overhead, API rate limits |
| File writers | 1 per file | Prevent write conflicts |
| API callers | Per rate limit | Avoid throttling |
| Build processes | CPU cores - 1 | Leave headroom for coordination |

### Sequential When

- Steps must be validated before proceeding (quality gates)
- Shared mutable state cannot be partitioned
- Order matters for correctness (database migrations, schema changes)
- Debugging is more important than speed (trace one path at a time)

## Resource Allocation Patterns

### Capability-Based Assignment

Match tasks to agents based on skills, not availability alone.

```
Task requires: [TypeScript, React, testing]
Agent A skills: [TypeScript, React, Node.js]     → Match: 2/3
Agent B skills: [Python, Django, testing]         → Match: 1/3
Agent C skills: [TypeScript, React, testing]      → Match: 3/3 ← Assign
```

### Load Balancing Strategies

- **Round-robin:** Distribute tasks evenly. Simple but ignores task size and agent skill.
- **Least-loaded:** Assign to the agent with the most available capacity.
- **Skill-weighted:** Prefer agents whose skills best match the task, with load as a tiebreaker.
- **Affinity:** Prefer assigning related tasks to the same agent to reduce context switching.

### Rebalancing Triggers

Reassign work when:
- An agent is blocked waiting on an external dependency
- An agent's task estimate was significantly wrong (2x+ overrun)
- A higher-priority task arrives that requires a specific agent
- An agent completes early and can absorb work from an overloaded peer
