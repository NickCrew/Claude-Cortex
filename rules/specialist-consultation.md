# Specialist Consultation

> *When you need expert advice, second opinions, sanity checks, plan review,
> design input, pros/cons analysis, hazard warnings, or a specialist's
> perspective on trade-offs.*

## Two shapes of help

**Skills** pull a pattern or workflow into your current context — you stay
the one doing the work. Skills are surfaced automatically by the
`skill-suggest` hook; reach for one when you need a knowledge pattern.

**Specialist agents** are subagents with different priors who can consult
on questions you haven't answered yourself. Reach for one when you want
another perspective, not another pair of hands.

## When to consult

Consultation is lightweight — a short question, a focused answer, and you
keep moving. Good shapes:

- **Plan review.** "Here's what I'm about to do. Concerns? Gotchas?"
- **Explanation.** "Explain this topic so I can build a better mental model."
- **Decision support.** "I'm choosing between X and Y. Pros / cons?"
- **Hazard scan.** "What should I watch out for while doing X?"
- **Design opinion.** "Do you like this UX / API / schema?"
- **Rubber-duck.** Often just formulating the question surfaces the answer.

Invent new shapes as they fit. The pattern is "short exchange with a
specialist," not a fixed menu.

## How to consult

Use the `Agent` tool with a focused prompt — state the question, provide
just enough context for the specialist to engage, keep it short.

```
Agent({
  subagent_type: "postgres-expert",
  description: "Consult on schema choice",
  prompt: "I'm choosing between a single 'events' table with a type column
           vs. separate tables per event type. ~100M rows/year, read-heavy
           analytics. Which direction, and what am I missing?"
})
```

Expect 3-5 points back, not a rewritten plan.

## Consultation vs delegation

- **Consultation** keeps ownership with you. The specialist injects perspective;
  you decide what to do with it.
- **Delegation** hands the task off. The specialist returns a completed result
  and you integrate it.

Agent front matter declares `delegate_when:` for agents worth fully delegating
to (large scope, independent review, fresh context, parallel workstreams).
If it's empty, treat the agent as consultation-only.

## When not to consult

- The answer is already in your current context.
- The task is large enough that delegation is the honest move.
- You're stalling — consultation can become procrastination.

## Agents by Specialty

- **Code Review:** `code-reviewer`
- **Security:** `security-auditor`
- **Documentation:** `docs-architect`
- **Diagnostics:** `debugger`
- **Performance:** `performance-monitor`
- **Testing:** `test-automator`
- **Web Development**
  - **UI/UX:** `ui-ux-designer`
  - **CSS:** `tailwind-expert`
  - **Tests:** `vitest-expert`
  - **APIs:** `rest-expert`
  - **WebSockets:** `websocket-engineer`
  - **Performance:** `frontend-optimizer`
  - **React:** `react-specialist`
    - **UI Component Libraries:** `component-architect`
    - **State Management:** `state-architect`
  - **Hosting:**
    - `cloud-architect`
    - `kubernetes-architect`
- **Databases:**
  - **Postgres:** `postgres-expert`
  - **Design:** `database-admin`
  - **Performance:** `database-optimizer`
  - **SQL:** `sql-pro`
- **Coding:**
  - **Python:** `python-pro`
  - **Rust:** `rust-pro`
  - **Typescript/Javascript:** `typescript-pro`, `javascript-pro`
- **Project Management**
  - **Planning/Delegation:** `orchestrator`
  - **Hand-offs/Summaries:** `context-manager`
  - **Persistence:** `memory-keeper`
