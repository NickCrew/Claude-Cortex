---
layout: default
title: Agent Loops
parent: Guides
nav_order: 9
---

# Agent Loops

`agent-loops` is the implementation discipline skill for Cortex. It is the
workflow you use when an agent is expected to make real code changes, verify
them, and leave behind reviewable evidence instead of "looks good to me"
confidence.
{: .fs-6 .fw-300 }

---

## What It Is

The skill-backed command is:

```text
/ctx:agent-loops
```

Use it when the work involves:

- writing or changing production code
- adding or updating tests
- running review and remediation cycles
- deciding what should be committed now versus filed for later

The core promise is simple: implementation work moves through explicit loops,
not vague "done" states.

## The Three Loops

`agent-loops` organizes implementation into three sequential gates:

```text
Code Change Loop -> Test Writing Loop -> Lint Gate
```

Each loop has a clear exit condition:

- **Code Change Loop** exits only when all `P0` and `P1` review findings are resolved.
- **Test Writing Loop** exits only when all `P0` and `P1` test gaps are resolved and the tests are not low-quality or misleading.
- **Lint Gate** exits only when lint passes cleanly.

If a loop cannot converge after the allowed remediation cycles, the skill says
to stop and escalate rather than thrash.

## The Non-Negotiables

These are the parts of the skill that matter most in practice:

- **Atomic commits, not feature blobs.** Each loop works on the next smallest complete, reviewable change.
- **Independent review only.** The implementer does not review their own diff or self-audit their own tests.
- **`committer`, not ad hoc `git commit`.** The skill explicitly requires `committer` for the loop commit step.
- **Evidence before completion.** Review artifacts, audit artifacts, tests, and lint results are the exit criteria.

## Review Routing

The code-review and test-audit flow is stricter than the old "ask another
model if convenient" approach.

### Code review order

1. Provider-aware review script first
2. Fresh-context Codex fallback reviewer if needed
3. Escalate if no independent reviewer is available

### Test audit order

1. Provider-aware test-audit script first
2. Fresh-context Codex fallback auditor if needed
3. Escalate if no independent auditor is available

The important behavioral rule is that the implementer never "grades their own
homework."

## Severity Model

The skill uses review severities to decide what blocks loop exit:

| Severity | Meaning | Loop behavior |
|:---------|:--------|:--------------|
| `P0` | Security or correctness critical | Must fix before exit |
| `P1` | Reliability, validation, or edge-case issue | Must fix before exit |
| `P2` | Important but non-blocking improvement | File follow-up issue |
| `P3` | Nice-to-have cleanup or preference | File follow-up issue |

That means `agent-loops` is opinionated about what gets fixed now versus what
gets tracked for later.

## Atomic Commit Model

The unit of work is the next atomic commit, not "the feature."

An atomic commit should:

- do one logical thing
- be reviewable in isolation
- keep related logic, types, and tests together
- leave the tree in a state where existing checks still make sense

The skill explicitly recommends using `committer` at the end of each loop exit:

```bash
committer "fix(parser): reject CONNECT requests with missing port" src/parser.rs tests/test_parser.rs
```

If your change needs multiple independent design decisions, it probably needs
multiple loop passes and multiple commits.

## Code Change Loop

This is the first loop: implement, review, remediate, re-review.

High-level flow:

```text
Implement -> specialist-review -> remediate P0/P1 -> specialist-review -> commit
```

What it enforces:

- review happens on a scoped diff
- only cited `P0` and `P1` findings block exit
- `P2` and `P3` findings become tracked follow-up work
- repeated failure triggers a circuit breaker instead of endless retries

The skill’s circuit breaker is three review cycles. If `P0` or `P1` findings
still remain, the agent should stop and escalate with the latest artifact.

## Test Writing Loop

This loop is not just "write some tests." It requires an independent audit for
coverage gaps and bad-test patterns.

High-level flow:

```text
Audit -> write tests -> verify -> re-audit -> commit
```

What the audit is looking for:

- missing contract coverage
- missing error-path or edge-case tests
- mirror tests
- flaky assertions
- tests that would still pass if the implementation were broken

This is one of the best parts of the skill: it treats false confidence as a
real failure mode, not a minor testing preference.

## Lint Gate

The lint gate is the final cleanup loop:

```text
Discover linter -> auto-fix what is safe -> re-check -> commit
```

Unlike review and test audit, lint is binary. The skill’s stance is that team
lint policy is not something the agent negotiates around. If a rule seems
wrong, escalate rather than silently bypassing it.

## Issue Filing

`agent-loops` also defines what happens to non-blocking findings.

- `P2` and `P3` issues should be filed rather than silently dropped.
- The filed issue should include enough context to be actionable later.
- Backlog-first tracking is preferred when a project already has a backlog flow.

So the skill is not just "fix things now"; it is also "leave the work in a
cleanly trackable state."

## How To Use It Well

The shortest practical pattern is:

1. Run `/ctx:agent-loops` when starting implementation.
2. Decompose the work into the next atomic commit.
3. Finish the code loop.
4. Finish the test loop.
5. Finish the lint gate.
6. Commit with `committer`.

The review and audit steps inside `agent-loops` are part of the skill workflow
itself. They are not the same thing as `cortex suggest --review`, which is a separate
standalone recommendation surface for loading review-relevant skills.

## What This Guide Is Not

This guide is intentionally high-level. The underlying skill contains the full
operator contract, including:

- exact reviewer and auditor fallback rules
- script invocation details
- review artifact shape
- audit artifact shape
- circuit-breaker behavior

If you are editing the skill itself or implementing review tooling around it,
read `skills/agent-loops/SKILL.md` in the repo directly.

## Related Guides

- [Planning & Collaboration]({% link guides/planning.md %}) -- turn ideas into atomic workstreams
- [Skills]({% link guides/skills.md %}) -- how skill-backed commands are discovered and used
- [CLI Usage]({% link guides/cli.md %}) -- current CLI surfaces around review and docs
