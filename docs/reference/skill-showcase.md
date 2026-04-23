# Skill Showcase

A curated guide to the most sophisticated and non-obvious skills in the Cortex
library. These aren't the everyday pattern references — they're the skills that
reshape how agents think, debug, collaborate, and verify their own work.

> **90+ skills** live in `skills/`. This document highlights the ones worth
> knowing about even if you don't use them daily.

---

## Meta-Cognitive Skills

Skills that change *how agents think* rather than *what they know*.

### `testing-skills-with-subagents`

**TDD applied to process documentation.**

Runs RED-GREEN-REFACTOR on skills themselves: write pressure scenarios that make
an agent *want* to violate the skill, run without the skill (RED — watch it
fail), write the skill to address those failures (GREEN), then close
rationalization loopholes (REFACTOR).

| What makes it sophisticated |
|---|
| Taxonomy of pressure types (time, sunk cost, authority, exhaustion, social, pragmatic) — best tests combine 3+ |
| Rationalization tables that catalog exact agent excuses verbatim and add explicit counters |
| Meta-testing: when an agent violates the skill despite having it, asks "how could the skill have been written differently?" — the response reveals whether the problem is documentation, organization, or a missing foundational principle |
| Convergence criterion: skill is "bulletproof" when the agent chooses correctly under maximum pressure, cites skill sections as justification, and acknowledges temptation |

**Trigger:** Creating or editing any discipline-enforcing skill.

---

### `constructive-dissent`

**Structured adversarial analysis at graduated intensity.**

Four levels — Gentle (refine details), Systematic (challenge methodology),
Rigorous (attack premises), Paradigmatic (question the worldview) — each with
its own challenge characteristics and example phrases.

| What makes it sophisticated |
|---|
| Assumption audit distinguishes explicit, implicit, structural, and *temporal* assumptions ("what time constraints are artificial?") |
| Alternative generation uses method inversion (try the opposite), constraint relaxation, and cross-domain inspiration |
| Stakeholder advocacy includes "future stakeholder" — people who aren't here yet |
| Output template forces synthesis: "Strengthen Current Proposal" alongside "Consider Alternative If" |

**Trigger:** Before finalizing major architectural or product decisions.

---

### `socratic-questioning`

**Guided discovery through strategic questioning, not direct instruction.**

Three-phase workflow (Assess → Explore → Consolidate) that teaches through a
layered question progression: Observe → Analyze → Abstract → Apply. Covers
Clean Code, GoF design patterns, and architectural trade-offs.

| What makes it sophisticated |
|---|
| "Name after discovery" principle — only name a pattern after the learner identifies the concept |
| Knowledge revelation timing: confirm insights, contextualize, then apply — never lecture |
| Understanding checkpoints track progression from observation → pattern recognition → principle connection → application → teaching ability |
| Anti-patterns: "if you're explaining more than asking, recalibrate" |

**Trigger:** Code review sessions focused on learning, coaching developers.

---

### `evaluator-optimizer`

**Iterative refinement to production quality through self-critique.**

Accept → Evaluate (score /100) → Decide (>= 90 stop, else refine) → Refine →
Repeat. Scores on correctness, clarity, efficiency, style, and safety.

| What makes it sophisticated |
|---|
| Convergence guarantee: if two consecutive iterations don't improve the score, stop and present the best version |
| "Do not settle" — the skill's behavioral rules explicitly reject "good enough" |
| Self-correction: if a refinement breaks something, revert and try a different approach |
| Each iteration requires showing specific flaws and specific changes — no hand-waving |

**Trigger:** Polishing rough drafts into production-grade code, docs, or designs.

---

## Verification & Trust Skills

Skills that ensure claims are true and work is actually done.

### `doc-claim-validator`

**Semantic accuracy verification for documentation.**

Extracts testable claims from markdown (file paths, commands, function
references, behavioral assertions, dependency claims) and verifies them against
the actual codebase. Goes far beyond broken-link checking.

| What makes it sophisticated |
|---|
| Two-phase verification: deterministic scripts for structural claims, then parallel haiku agents for semantic claims (dependencies, behavioral assertions, code examples) |
| Git staleness scoring: counts commits to a target file *after* the doc was last edited, ranks high-drift claims for review |
| Claim taxonomy of 8 types with different verification methods per type |
| Severity model: P0 (user-facing doc would break if followed) down to P4 (cosmetic) |
| Bundled Python scripts (`extract_claims.py`, `verify_claims.py`) for automated pipeline |

**Trigger:** After refactors, before releases, when onboarding devs say "the docs are wrong."

---

### `verification-before-completion`

**Iron law: no completion claims without fresh evidence.**

A gate function that forces explicit command execution, output reading, and
confirmation before any agent can declare work "done." Explicitly lists common
rationalizations and why they fail.

| What makes it sophisticated |
|---|
| Rejects confidence-as-evidence: "should work" is not verification |
| Specificity-over-spirit approach — lists exact excuses agents use and counters each one |
| Frames unverified completion claims as dishonesty, not efficiency |
| Partial checks prove nothing — the gate requires complete, fresh evidence |

**Trigger:** Automatically, before any agent claims a task is complete.

---

## Debugging & Resilience Skills

Skills that fix bugs at the source and make them structurally impossible.

### `root-cause-tracing`

**Trace backward through the call chain — never fix the symptom.**

A 5-step process: Observe symptom → Find immediate cause → Ask "what called
this?" → Keep tracing up → Find original trigger. Includes instrumentation
techniques when manual tracing hits dead ends.

| What makes it sophisticated |
|---|
| Companion to `defense-in-depth` — find the source, then fortify every layer |
| Bundled bisection script (`find-polluter.sh`) for isolating which test causes state pollution |
| Real worked example traces a 5-level call chain from `git init` in wrong directory back to a top-level variable accessing an empty value before `beforeEach` |
| "NEVER fix just where the error appears" as a structural principle, not a suggestion |

**Trigger:** Error appears deep in execution, unclear where invalid data originated.

---

### `defense-in-depth`

**Validate at every layer data passes through. Make the bug structurally impossible.**

Four validation layers: entry point (reject at API boundary), business logic
(data makes sense for this operation), environment guards (refuse dangerous ops
in specific contexts), debug instrumentation (capture forensics).

| What makes it sophisticated |
|---|
| Each layer catches bugs the others miss: different code paths bypass entry validation, mocks bypass business logic, edge cases on different platforms need environment guards |
| Environment guards are context-aware — e.g., refuse `git init` outside tmpdir during tests |
| Not a suggestion to "add more validation" — it's a concrete 4-layer framework with code templates |
| Born from a real session: all 4 layers were needed, each independently caught bugs |

**Trigger:** After fixing any bug caused by invalid data flowing through multiple layers.

---

### `condition-based-waiting`

**Replace timing guesses with condition polling. Eliminate flaky tests.**

Core pattern: replace every `setTimeout`/`sleep` in tests with a `waitFor()`
that polls for the actual condition you care about.

| What makes it sophisticated |
|---|
| Generic typed `waitFor<T>` implementation with timeout, polling interval, and descriptive error messages |
| Decision tree: if testing actual timing behavior (debounce, throttle), arbitrary timeout IS correct — but document WHY |
| Domain-specific helpers: `waitForEvent`, `waitForEventCount`, `waitForEventMatch` |
| Measured impact from one session: 60% → 100% pass rate, 40% faster execution |

**Trigger:** Tests with arbitrary delays, flaky tests, tests that fail under CI load.

---

## Multi-Agent Coordination Skills

Skills for orchestrating parallel work and cross-model collaboration.

### `dispatching-parallel-agents`

**One agent per independent problem domain. Concurrent investigation.**

Four-step pattern: identify independent domains → create focused agent tasks →
dispatch in parallel → review and integrate. Includes prompt templates for
effective agent scoping.

| What makes it sophisticated |
|---|
| Clear decision tree for when NOT to parallelize: related failures, need for full system context, shared state, exploratory debugging |
| Agent prompt structure requires focus (one domain), self-containment (all context included), and specific output format |
| Anti-pattern catalog: "too broad" (agent gets lost), "no context" (doesn't know where), "no constraints" (refactors everything), "vague output" (unknown changes) |
| Integration step: review summaries, check for conflicts, run full suite, spot-check |

**Trigger:** 3+ independent failures across different subsystems.

---

### `multi-llm-consult`

**Cross-model second opinions via Gemini, OpenAI/Codex, and Qwen.**

Bundled script that sanitizes prompts, queries external providers, and returns
advisory responses for reconciliation against local repo state.

| What makes it sophisticated |
|---|
| Four purpose types: `second-opinion`, `plan`, `review`, `delegate` |
| Mandatory sanitization before sending prompts to external models |
| Responses treated as advisory — must be reconciled with repo constraints |
| Supports prompt files and context files for complex reviews |

**Trigger:** Want another model's perspective, comparing approaches, delegating subtasks.

---

### `agent-loops`

**Complete operational workflow for implementer agents with three-provider review system.**

Defines four sequential loops — Code Change, Test Writing, Lint Gate, Issue
Filing — with severity levels, escalation rules, and maximum iteration counts.
Reviews are provider-aware across all three supported LLMs (Claude, Gemini,
Codex) with strict no-self-review enforcement.

#### Supported Providers

All review operations support three LLM providers with automatic fallback:

| Provider | CLI | Detection |
|---|---|---|
| **Claude** | `claude --print --no-session-persistence` | `CLAUDECODE` env var |
| **Gemini** | `gemini --prompt --output-format text` | Manual or env var |
| **Codex** | `codex exec --ephemeral --skip-git-repo-check` | `CODEX_THREAD_ID` or `CODEX_MANAGED_BY_NPM` env vars |

#### No-Self-Review Enforcement

The core principle is **"you never grade your own homework."** The
`review-provider.sh` helper auto-detects which provider is the current
implementer and enforces a strict ordering:

1. **Non-self providers first** — if Claude is the implementer, try Gemini then
   Codex for review
2. **Self provider last** — only used as final fallback when all independent
   providers fail
3. **Fresh-context Codex fallback** — a separate Codex invocation with no
   authorship of the code, used when all Tier 1 providers are unavailable

Auto-detection reads environment variables (`CLAUDECODE`, `CODEX_THREAD_ID`,
`CODEX_MANAGED_BY_NPM`, `GEMINI_CLI_NO_RELAUNCH`,
`GEMINI_CLI_ACTIVITY_LOG_TARGET`) to identify the implementer. Manual override is
available via `AGENT_LOOPS_SELF_PROVIDER`.

#### Provider Priority System

Review requests follow a three-tier fallback chain:

| Tier | Strategy | When used |
|---|---|---|
| **Tier 1** | Bundled scripts with automatic provider selection | Default — tries providers in priority order, skips self |
| **Tier 2** | Fresh-context Codex fallback | All Tier 1 providers unavailable or fail |
| **Tier 3** | Manual escalation to user | Both automated tiers fail |

Provider selection can be overridden per-script:

| Variable | Scope |
|---|---|
| `SPECIALIST_REVIEW_PROVIDER` | Code review script only |
| `TEST_REVIEW_PROVIDER` | Test audit script only |
| `AGENT_LOOPS_LLM_PROVIDER` | Global override for both |

Each provider has independent timeout control (`CLAUDE_TIMEOUT`,
`GEMINI_TIMEOUT`, `CODEX_TIMEOUT`, default 300s) and Claude has budget control
via `CLAUDE_MAX_BUDGET` (default $0.50).

#### Bundled Scripts

| Script | Purpose |
|---|---|
| `specialist-review.sh` | Multi-perspective code review with diff capture, prior-review continuity, and contract validation |
| `diff-test-audit.sh` | Test coverage audit with auto-discovery of test directories and inline source analysis |
| `review-provider.sh` | Shared provider abstraction (detection, ordering, invocation, timeout) |
| `validate-review-contract.py` | Validates and normalizes review artifacts against required markdown contracts |

| What makes it sophisticated |
|---|
| Three-provider support (Claude, Gemini, Codex) with automatic fallback and self-detection |
| "You never grade your own homework" — enforced structurally via auto-detection, not by convention |
| Circuit breakers prevent infinite loops: 3 cycles for code/test, 2 for lint (mechanical, not semantic) |
| Lint Gate uses a 4-step linter discovery cascade with fail-safe to user — never guesses |
| Contract validation rejects malformed reviews and automatically tries the next provider |
| Scoped remediation reviews with `--prior-review` for continuity across cycles |
| Provider-specific timeouts and budget controls for cost management |

**Trigger:** Starting any implementation task in a multi-agent workflow.

### `multi-specialist-review`

**User-triggered multi-agent code review with grounded, verifiable findings.**

Spawns 3-5 parallel specialist sub-agents (one per review perspective —
correctness, security, performance, architecture, etc.), each reading actual
source files via Read/Grep/Glob rather than just inlined diffs. Findings are
mechanically verified against the codebase before synthesis into a single
review artifact.

Extracted from `agent-loops` because team-based review is a user-triggered
operation — the cost profile (~$2-3/review) and authority profile (PR-level,
security-sensitive changes) warrant explicit invocation, not autonomous agent
decision-making.

#### Orchestration Phases

| Phase | Action | Cost |
|---|---|---|
| **0 — Triage** | `triage_perspectives.py` selects 3-5 perspectives from file types and content signals | Free (deterministic) |
| **1 — Parallel specialists** | Spawn N sub-agents in one message; each writes findings JSON | ~$2-3 |
| **2 — Citation verification** | `verify_citations.py` validates file paths, line ranges, and quoted code against disk | Free (deterministic) |
| **3 — Synthesis** | Team lead deduplicates, merges multi-perspective findings, renumbers | In-context (no spawn) |
| **4 — Validate** | `validate-review-contract.py` (from agent-loops) confirms the review artifact shape | Free (deterministic) |

#### Bundled Scripts

| Script | Purpose |
|---|---|
| `triage_perspectives.py` | Deterministic perspective selection based on file extensions and content signals |
| `verify_citations.py` | Mechanical validation of findings against actual source files (±5 line tolerance) |

| What makes it sophisticated |
|---|
| Specialists read actual source files (not just diffs) — reduces hallucination and catches issues invisible to diff-only review |
| Citation verification rejects findings where file/line/quoted-code don't match disk — strips hallucinated references before they reach the user |
| Multi-perspective independence: parallel dispatch, zero cross-specialist context leakage |
| Deterministic triage, verification, and validation (Phases 0, 2, 4) add zero API cost to the review |
| Requires Claude Code team API — Codex/Gemini agents flag for team review in their handoff rather than invoking |

**Trigger:** User-invoked (slash command or direct skill reference). Not for
autonomous agent workflows.

---

## Ideation & Product Skills

Skills for structured creative thinking and product design.

### `collaboration` suite (8 sub-skills)

**A complete Design Thinking pipeline agents can execute.**

Eight chained skills that form an ideation pipeline, each naming which skills to
pair it with:

```
brainstorming → assumption-buster → mashup → idea-lab → concept-forge → pre-mortem
                                                                           ↓
                                                               writing-plans → executing-plans
```

| Sub-skill | What it does |
|-----------|-------------|
| `brainstorming` | Rapid divergent ideation to define scope |
| `assumption-buster` | Flip (`--opposite`), remove (`--zero`), or exaggerate (`--10x`) constraints |
| `mashup` | Force-fit patterns from orthogonal domains (fintech, gaming, health) |
| `idea-lab` | Timeboxed divergent ideation, outputs ranked options + day-one experiments |
| `concept-forge` | Score concepts on impact/delight/effort, pick a 1-day spike |
| `pre-mortem` | Imagine failure first — surface guardrails that double as feature ideas |
| `writing-plans` | Convert concepts into actionable implementation plans |
| `executing-plans` | Ensure plans translate into tracked tasks with checkpoints |

**Trigger:** Product ideation, feature design, strategic planning sessions.

---

### `incident-response`

**Five-phase production incident management.**

Detect → Triage → Contain → Resolve → Postmortem. Includes cascade prevention
through resilience patterns (circuit breakers, bulkheads, load shedding) and
blameless postmortem design.

| What makes it sophisticated |
|---|
| Rapid severity classification enables parallel action — minimal viable fix first |
| Cascade prevention uses resilience patterns during containment, not just resolution |
| Blameless postmortem decouples human accountability from systemic issue identification |
| "Validate in staging if time permits" — explicit pragmatism about verification under pressure |

**Trigger:** Production incidents, cascade prevention, postmortem facilitation.

---

### `legacy-modernization`

**Incremental migration via strangler fig, feature flags, and compatibility layers.**

Safety-first modernization: add characterization tests for existing behavior
*before* any changes, maintain backward compatibility at every step, run old and
new paths in parallel with continuous monitoring.

| What makes it sophisticated |
|---|
| Safety net phase: characterization tests capture existing behavior as the ground truth |
| Regression prevention and rollback planning matter more than refactoring speed |
| Parallel running of old and new paths with monitoring — not a flag-day cutover |
| Explicitly rejects big-bang rewrites in favor of incremental patterns |

**Trigger:** Modernizing legacy systems, planning migrations, refactoring with safety nets.

---

## Efficiency & Knowledge Skills

Skills that optimize context usage and build collective intelligence.

### `knowledge-synthesis`

**Organizational memory pipeline: extract, validate, and distribute insights.**

Four-phase workflow (Discovery → Codification → Dissemination → Feedback) that
turns raw interaction data into a curated knowledge base with confidence scoring,
citation methodology, and knowledge graph construction.

| What makes it sophisticated |
|---|
| Confidence threshold: codification requires 5+ corroborating instances and zero unresolved contradictions |
| Knowledge graph with `contradicts` edge type — new evidence that challenges existing patterns is surfaced explicitly |
| RAG optimization: chunking guidelines (200-800 tokens, one concept per chunk, front-loaded key info) |
| Continuous learning cycle: Observe → Hypothesize → Test → Codify → Apply → Observe |
| "Do not synthesize from a single data point" — guards against premature generalization |

**Trigger:** Synthesizing findings across sessions, building shared knowledge, pattern extraction.

---

### `token-efficiency`

**Symbolic shorthand for crowded context windows.**

A compression system using logic symbols (`→`, `⇒`, `∴`, `∵`), status
indicators, domain markers, and abbreviations to reduce token usage when context
exceeds 75%.

| Example | |
|---|---|
| **Standard** | "The authentication system has a security vulnerability in the user validation function" |
| **Compressed** | `auth.js:45 → sec risk in user val()` |

**Trigger:** Context window > 75% full, large codebase analysis, complex multi-step workflows.

---

### `cortex-skills-loop`

**Self-improving skill recommendation engine.**

Blends four recommendation strategies — semantic similarity (embeddings),
rule-based file patterns, agent-based skill mapping, and historical success
rates — through a recommend-feedback-rate cycle that improves confidence scoring
over time.

| What makes it sophisticated |
|---|
| Four converging recommendation strategies, not just keyword matching |
| Feedback loop: ratings incrementally improve confidence scoring across sessions |
| Learns from cumulative interactions rather than one-shot recommendations |
| Context-change triggers: new file types, changed workflows, project evolution |

**Trigger:** Automatically, when context changes suggest relevant skills.

---

## Quick Lookup

| Category | Skills | Key Idea |
|----------|--------|----------|
| **Meta-Cognitive** | `testing-skills-with-subagents`, `constructive-dissent`, `socratic-questioning`, `evaluator-optimizer` | Change how agents think |
| **Verification** | `doc-claim-validator`, `verification-before-completion` | Ensure claims are true |
| **Debugging** | `root-cause-tracing`, `defense-in-depth`, `condition-based-waiting` | Fix at the source, make bugs impossible |
| **Multi-Agent** | `dispatching-parallel-agents`, `multi-llm-consult`, `agent-loops` | Coordinate parallel and cross-model work |
| **Ideation** | `collaboration` suite, `incident-response`, `legacy-modernization` | Structured creative and strategic thinking |
| **Efficiency** | `knowledge-synthesis`, `token-efficiency`, `cortex-skills-loop` | Optimize context and build memory |
