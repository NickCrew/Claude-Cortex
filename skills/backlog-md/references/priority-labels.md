# Priority and Labeling System

Agent-optimized priority and labeling system for Backlog.md.

## Priority Levels

**Required** when creating issues. Use the following definitions:

| Priority | Definition | Examples | Typical Workflow |
|----------|-----------|----------|------------------|
| **P0** | Critical problems, major breakage | Service down, security vulnerability, data loss | Fix immediately |
| **P1** | Legitimate bugs impacting users | Feature broken, incorrect behavior, significant performance degradation | Fix in current cycle |
| **P2** | Bugs, edge cases | Unusual input handling, minor UX issues, performance improvements | Schedule in sprint |
| **P3** | Nice-to-have improvements, features we want to do | Convenience features, refactoring, code cleanup we plan for | Include in roadmap |
| **P4** | Backlog, future ideas | Speculative features, long-term improvements | Archive until needed |

## Priority Assignment Strategy

**For implementers filing deferred issues during feature work:**
- Most deferred issues are **P2** (bugs/edge cases found during implementation)
- File P2 by default unless clearly critical (P0/P1)
- If unsure between P2/P3: **use P2** (we want to fix it)
- If unsure about P0/P1: Label with `priority-review` instead of guessing

**For reviewers doing audits:**
- Security findings: Likely P0/P1
- Code quality issues: P2/P3
- If unsure: Label with `priority-review` and let user decide later

**Don't overthink it.** The priority-review label exists for borderline cases.

## Labeling System

### Type Labels (Required)

**Single label per issue. Choose one:**

| Label | Use For |
|-------|---------|
| `bug` | Bug fixes, defects, incorrect behavior |
| `feature` | New functionality, feature requests |
| `documentation` | Docs, guides, API documentation, comments |
| `refactor` | Code cleanup, architecture improvements, no behavior change |
| `remediation` | Deferred issues from reviews/audits (mark issues found during review) |

### App Labels (Optional)

Can use **multiple** app labels per issue. Examples:
- `synapse-pingora`
- `signal-horizon-ui`
- `signal-horizon-api`
- Others as needed

### Custom Labels (Optional)

Agents can add domain-specific labels for routing:
- `performance` — performance improvement or investigation
- `security` — security-related work
- `priority-review` — priority uncertain, needs user decision
- `blocked` — waiting on something external
- Others as useful for agent workflows

## Labeling Examples

**Deferred bug found during code review:**
```bash
backlog task create "Handle null reference in payment processor" \
  -l bug,remediation \
  -l synapse-pingora \
  -p 2
```

**Security audit finding:**
```bash
backlog task create "Remove hardcoded credentials from config" \
  -l bug,remediation \
  -l synapse-pingora,signal-horizon-api \
  -p 1 \
  -l priority-review  # If you're unsure about P0 vs P1
```

**Feature work UI component:**
```bash
backlog task create "Add dark mode toggle to dashboard" \
  -l feature \
  -l signal-horizon-ui \
  -p 3
```

**Documentation for monitoring:**
```bash
backlog task create "Document monitoring setup for sidecars" \
  -l documentation \
  -p 3
```

## When to Use priority-review Label

If you're filing an issue and the priority is unclear, **add the `priority-review` label instead of guessing:**

```bash
backlog task create "Investigate intermittent timeout in batch processor" \
  -l bug \
  -l synapse-pingora \
  -p 2 \
  -l priority-review  # You think it's P2 but might be P1 if it's affecting production
```

The user can review these later and adjust priority as needed.

## Frequency and Patterns

Based on typical workflows:
- **P0/P1 issues**: Usually assigned during code review or when critical bugs surface
- **P2 issues**: Most common during feature implementation (deferred work)
- **P3/P4 issues**: Less common in review cycles, more from long-term planning
- **priority-review**: Use liberally when uncertain
