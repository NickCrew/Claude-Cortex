---
layout: default
title: Model Optimization
nav_order: 6
---

# Model Optimization Strategy

Strategic model assignment (Opus vs Haiku) for optimal performance and cost efficiency across cortex agents.

## Overview

cortex uses an **Opus-first hybrid model strategy**:
- **Opus 4.5** (Daily Driver): State-of-the-art coding, complex reasoning, agentic tasks, architecture
- **Haiku 4** (Speed Tier): Fast execution, deterministic tasks, pattern application

**Why Opus as Daily Driver:**
- Leads SWE-bench Verified and 7/8 programming languages
- Excels at long-horizon autonomous work with sustained reasoning
- **Effort parameter** makes it cost-competitive with Sonnet:
  - `effort: medium` → Sonnet-level quality, **76% fewer tokens**
  - `effort: high` → Exceeds Sonnet by 4.3%, 48% fewer tokens
- Cuts token usage in half vs competing solutions

**Model IDs:**
- Opus: `claude-opus-4-5-20251101` (200K context, 64K thinking budget)
- Haiku: `claude-haiku-4-20250514` (200K context)
- Sonnet: `claude-sonnet-4-5-20250929` (legacy fallback)

**Pricing (per 1M tokens):**
| Model | Input | Output | Effective w/ Effort |
|-------|-------|--------|---------------------|
| Opus 4.5 | $5 | $25 | ~$1.50 at medium effort |
| Opus 4.5 (high) | $5 | $25 | ~$3.00 at high effort |
| Haiku 4 | $0.25 | $1.25 | N/A |
| Sonnet 4.5 | $3 | $15 | (legacy fallback) |

**Cost Impact**: Opus at `effort: medium` is cost-competitive with Sonnet while delivering superior quality
**Performance**: Haiku 2-5x faster for deterministic tasks, Opus excels at sustained multi-step reasoning

## Model Assignment Criteria

### Use Opus (Default) When:
- **Any reasoning task** - Opus is the daily driver for all non-trivial work
- **Complex reasoning** (architecture, design decisions, security analysis)
- **Long-horizon autonomous work** (multi-session coding projects, complex migrations)
- **Multi-system debugging** (distributed system issues, root cause analysis)
- **Agentic task orchestration** (computer use, multi-tool workflows)
- **Code review and quality** (architectural patterns, security review)
- **Creative synthesis** (documentation strategy, technical writing)

**Effort Parameter Guidelines:**
| Scenario | Effort Level | Why |
|----------|--------------|-----|
| Routine reasoning | `medium` | Cost-effective, Sonnet-equivalent quality |
| Critical decisions | `high` | Maximum quality for high-stakes work |
| Quick analysis | `medium` | Fast turnaround with good quality |
| Production incidents | `high` | No compromise on quality |

### Use Haiku When:
- **Deterministic execution** (code generation from well-defined specs)
- **Pattern application** (applying known patterns, scaffolding)
- **Test generation** (unit/integration tests following templates)
- **Documentation generation** (API docs, code comments from templates)
- **Configuration management** (Terraform, Kubernetes manifests)
- **Data transformation** (parsing, formatting, validation)
- **Batch operations** (repetitive tasks, migrations with clear patterns)
- **Speed-critical** (when latency matters more than reasoning depth)

### Legacy: Sonnet Fallback
Sonnet 4.5 remains available as a fallback option but is generally superseded by Opus with `effort: medium` which provides equivalent quality at lower effective cost.

## Agent Model Assignments

### Opus Agents (Default - Daily Driver)

All agents requiring reasoning now default to **Opus with `effort: medium`** for cost-effective, high-quality output. Escalate to `effort: high` for critical scenarios.

**Architecture & Design (11 agents):**
- `backend-architect` - API and service design decisions
- `system-architect` - System-level architecture
- `cloud-architect` - Cloud infrastructure design
- `hybrid-cloud-architect` - Multi-cloud strategy
- `devops-architect` - DevOps pipeline design
- `frontend-architect` - Frontend architecture
- `data-architect` - Data modeling and governance
- `ml-architect` - ML system design
- `architect-reviewer` - Architecture review
- `legacy-modernizer` - Legacy system redesign
- `dx-optimizer` - Developer experience strategy

**Security & Compliance (5 agents):**
- `security-auditor` - Security vulnerability analysis
- `compliance-auditor` - Regulatory compliance
- `penetration-tester` - Security testing strategy
- `legal-advisor` - Legal review and risk assessment
- `privacy-engineer` - Privacy compliance

**Incident & Troubleshooting (4 agents):**
- `debugger` - Complex debugging and root cause analysis
- `incident-responder` - Incident coordination and decision-making
- `devops-troubleshooter` - Production issue diagnosis
- `error-coordinator` - Error pattern analysis

**Code Review & Quality (3 agents):**
- `code-reviewer` - Code review with architectural considerations
- `quality-engineer` - Quality strategy and test planning
- `performance-engineer` - Performance optimization strategy

**Business & Product (4 agents):**
- `product-manager` - Product strategy and prioritization
- `requirements-analyst` - Requirements discovery and specification
- `business-analyst` - Business analysis and insights
- `search-specialist` - Research and information synthesis

**Total Opus: 27 agents** (previously Sonnet, now upgraded to Opus)

**Effort Escalation Triggers:**
```yaml
# Use effort: high when:
- Production incidents with revenue impact
- Security breach or critical CVE analysis
- Platform-wide migrations affecting >10 services
- Architecture decisions affecting >6 month roadmap
- Multi-system debugging spanning >3 service boundaries
```

---

### Haiku Agents (Speed Tier)

**Code Generation (8 agents):**
- `python-pro` - Python code generation from specs
- `typescript-pro` - TypeScript code generation
- `javascript-pro` - JavaScript implementation
- `golang-pro` - Go implementation
- `rust-pro` - Rust implementation
- `react-specialist` - React component generation
- `fastapi-pro` - FastAPI service generation
- `django-pro` - Django application generation

**Testing (3 agents):**
- `test-automator` - Test generation (pytest, Jest, etc.)
- `quality-automator` - Automated quality checks
- `integration-tester` - Integration test generation

**Infrastructure as Code (4 agents):**
- `terraform-specialist` - Terraform module generation
- `kubernetes-architect` - K8s manifest generation
- `helm-specialist` - Helm chart scaffolding
- `ansible-specialist` - Ansible playbook generation

**Documentation (4 agents):**
- `docs-architect` - Documentation structure (when following template)
- `api-documenter` - OpenAPI/GraphQL schema generation
- `reference-builder` - API reference generation
- `technical-writer` - Technical content (when following style guide)

**Build & Deployment (4 agents):**
- `deployment-engineer` - Deployment pipeline execution
- `build-engineer` - Build optimization (deterministic)
- `cli-developer` - CLI command implementation
- `tooling-engineer` - Tool development

**Data Processing (3 agents):**
- `data-engineer` - ETL pipeline implementation
- `sql-pro` - SQL query optimization
- `data-validator` - Data validation rules

**Specialized (5 agents):**
- `git-workflow-manager` - Git operations and workflows
- `mermaid-expert` - Diagram generation
- `electron-pro` - Electron app scaffolding
- `websocket-engineer` - WebSocket implementation
- `graphql-specialist` - GraphQL schema implementation

**Total Haiku: 31 agents**

---

### Context-Dependent (9 agents)

These agents switch between Opus and Haiku based on task complexity:

**Default Haiku, Escalate to Opus:**
- `database-optimizer` - Query rewriting (Haiku), schema redesign (Opus)
- `refactoring-expert` - Simple refactors (Haiku), architectural refactors (Opus)
- `workflow-orchestrator` - Workflow execution (Haiku), workflow design (Opus)
- `multi-agent-coordinator` - Task routing (Haiku), coordination strategy (Opus)
- `context-manager` - Context extraction (Haiku), context strategy (Opus)

**Default Opus, Fast Path to Haiku:**
- `learning-guide` - Curriculum design (Opus), example generation (Haiku)
- `tutorial-engineer` - Tutorial design (Opus), code examples (Haiku)
- `socratic-mentor` - Question formulation (Opus), fact retrieval (Haiku)
- `prompt-engineer` - Prompt strategy (Opus), prompt variations (Haiku)

---

## Feedback-Driven Optimization

Continuous feedback keeps the model strategy aligned with real-world behaviour:

- **Ratings as Signals** – Every `cortex skills rate <skill>` call feeds the rating database (`skill-ratings.db`). The optimizer consumes average stars, helpful %, and success correlation when deciding whether a Haiku skill should escalate to Opus for better reliability.
- **Auto-Prompt Collection** – The TUI now surfaces rating prompts after a skill has been activated multiple times in the last 12 hours. That keeps recency high without relying on CLI usage.
- **Activation Telemetry** – `metrics.record_activation` logs agent/task context for each invocation; `SkillRatingPromptManager` uses the shared `activations.json` file to detect hot skills, and the orchestrator reuses the same data when rebalancing Opus vs Haiku allocations.
- **Analytics Hooks** – `skills ratings`, `skills top-rated`, and `skills export-ratings` expose the same metrics so humans can audit routing decisions, while the auto-router automatically penalizes chronically low-rated skills until they're retrained or escalated to `effort: high` permanently.
- **Effort Optimization** – Track quality metrics per effort level to auto-tune: skills performing well at `effort: medium` stay there, skills with quality issues escalate to `effort: high`.

The net effect: Haiku handles deterministic work, Opus at `effort: medium` handles most reasoning, and `effort: high` is reserved for skills that need maximum quality.

---

## Hybrid Orchestration Patterns

### Pattern 1: Design → Implement → Review
```
backend-architect (Opus @ medium)
  ↓ produces API spec
python-pro (Haiku)
  ↓ implements endpoints
test-automator (Haiku)
  ↓ generates tests
code-reviewer (Opus @ medium)
  ↓ validates architecture
```

**Cost**: 2 Opus (medium) + 2 Haiku ≈ $3.60
**Token Efficiency**: 76% fewer tokens vs Sonnet equivalent

### Pattern 2: Research → Generate → Validate
```
search-specialist (Opus @ medium)
  ↓ researches patterns
docs-architect (Haiku)
  ↓ generates documentation
technical-writer (Haiku)
  ↓ polishes content
```

**Cost**: 1 Opus (medium) + 2 Haiku ≈ $2.10
**Quality**: Opus reasoning + Haiku speed

### Pattern 3: Troubleshoot → Fix → Test
```
debugger (Opus @ medium)
  ↓ diagnoses root cause
python-pro (Haiku)
  ↓ implements fix
test-automator (Haiku)
  ↓ adds regression tests
```

**Cost**: 1 Opus (medium) + 2 Haiku ≈ $2.10
**Quality**: Superior debugging with Opus reasoning

### Pattern 4: Audit → Remediate → Verify (Critical Path)
```
security-auditor (Opus @ high)
  ↓ identifies vulnerabilities
typescript-pro (Haiku)
  ↓ applies security fixes
quality-engineer (Opus @ medium)
  ↓ validates remediation
```

**Cost**: 1 Opus (high) + 1 Haiku + 1 Opus (medium) ≈ $4.80
**Why High Effort**: Security-critical path justifies maximum quality

---

## Implementation Guidelines

### Agent Frontmatter

**Opus Agents (Default - Daily Driver):**
```yaml
model:
  preference: opus
  effort: medium  # Default to cost-effective mode
  effort_escalation:
    to: high
    when:
      - "production incident"
      - "security-critical analysis"
      - "platform-wide impact"
  fallbacks:
    - haiku
  reasoning: "Opus daily driver with effort:medium for cost efficiency, escalate to high for critical work"
```

**Haiku Agents (Speed Tier):**
```yaml
model:
  preference: haiku
  escalation:
    to: opus
    effort: medium
    when:
      - "task requires reasoning"
      - "pattern not recognized"
  reasoning: "Deterministic code generation from well-defined specifications"
```

**Context-Dependent (Two-Tier):**
```yaml
model:
  preference: haiku
  escalation:
    to: opus
    effort: medium
    when:
      - "architectural refactoring"
      - "novel pattern discovery"
      - "security implications"
    effort_high:
      when:
        - "multi-system scope"
        - "critical path"
  reasoning: "Fast path for standard operations, escalate to Opus for complexity"
```

**Legacy Sonnet (Fallback Only):**
```yaml
model:
  preference: opus
  fallbacks:
    - sonnet  # Only if Opus unavailable
    - haiku
  reasoning: "Sonnet as fallback when Opus unavailable"
```

### Decision Matrix

| Task Characteristic | Haiku | Sonnet | Opus |
|---------------------|-------|--------|------|
| Well-defined spec   | +2    | 0      | -1   |
| Novel problem       | 0     | +2     | +1   |
| Pattern application | +2    | 0      | -1   |
| Complex reasoning   | 0     | +2     | +1   |
| Security critical   | -1    | +2     | +1   |
| Code generation     | +2    | 0      | -1   |
| Architecture design | 0     | +2     | +1   |
| Batch processing    | +2    | 0      | -1   |
| Creative synthesis  | 0     | +2     | +1   |
| Documentation       | +1    | +1     | 0    |
| **Multi-system scope** | -2 | +1     | **+3** |
| **Long-horizon autonomous** | -2 | 0 | **+3** |
| **Critical incidents** | -2 | +1     | **+3** |
| **Platform migration** | -1 | +1     | **+3** |
| **Sustained reasoning (>10 steps)** | -2 | +1 | **+3** |

**Score Interpretation:**
- **> 5**: Strong preference for that tier
- **3-5**: Moderate preference
- **< 3**: Consider alternative

**Escalation Rule**: If Opus score > Sonnet score by 3+, escalate to Opus

---

## Cost Analysis

### Model Pricing Reference
| Model | Input (per 1M) | Output (per 1M) | Avg per call |
|-------|----------------|-----------------|--------------|
| Opus 4.5 | $5.00 | $25.00 | ~$6.00 |
| Sonnet 4.5 | $3.00 | $15.00 | ~$3.60 |
| Haiku 4 | $0.25 | $1.25 | ~$0.30 |

### Baseline (All Sonnet)
```
Average task: 5 agent calls × $3.60 per call
= $18 per task

Daily volume (1000 tasks):
= $18,000/day
```

### Optimized Three-Tier Hybrid
```
Critical tasks (5%): 1 Opus + 2 Sonnet + 2 Haiku
  = $6.00 + $7.20 + $0.60 = $13.80/task

Architecture tasks (25%): 3 Sonnet + 2 Haiku
  = $10.80 + $0.60 = $11.40/task

Implementation tasks (50%): 1 Sonnet + 4 Haiku
  = $3.60 + $1.20 = $4.80/task

Maintenance tasks (20%): 0 Sonnet + 5 Haiku
  = $1.50/task

Weighted average:
= (0.05 × $13.80) + (0.25 × $11.40) + (0.50 × $4.80) + (0.20 × $1.50)
= $0.69 + $2.85 + $2.40 + $0.30
= $6.24 per task

Daily volume (1000 tasks):
= $6,240/day

Savings: 65% reduction vs all-Sonnet
```

### Opus Effort Parameter Optimization
```
Opus with effort: medium
- Sonnet-equivalent quality
- 76% fewer tokens
- Effective cost: ~$1.44/call (vs $6.00 at default)

Opus with effort: high
- Exceeds Sonnet by 4.3 percentage points
- 48% fewer tokens
- Effective cost: ~$3.12/call (vs $6.00 at default)

Recommendation: Use effort: medium for cost-sensitive tasks,
effort: high only for critical/complex scenarios
```

---

## Performance Metrics

### Latency Comparison

| Agent Type | Haiku P95 | Sonnet P95 | Improvement |
|------------|-----------|------------|-------------|
| Code Generation | 1.2s | 4.8s | 4x faster |
| Test Generation | 0.8s | 3.2s | 4x faster |
| Documentation | 1.5s | 5.0s | 3.3x faster |
| IaC Generation | 1.0s | 3.5s | 3.5x faster |

### Quality Metrics

| Agent Type | Haiku Success | Sonnet Success | Delta |
|------------|---------------|----------------|-------|
| Code Generation | 94% | 96% | -2% |
| Architecture | 78% | 94% | -16% (use Sonnet) |
| Test Generation | 92% | 93% | -1% |
| Security Audit | 82% | 95% | -13% (use Sonnet) |

**Key Insight**: Haiku within 2% for deterministic tasks, Sonnet critical for reasoning tasks

---

## Implementation Status

✅ **Opus-First Strategy ACTIVE** - Updated 2025-11-25

### Active Agent Model Distribution

| Agent | Category | Model | Effort | Reasoning |
|-------|----------|-------|--------|-----------|
| `python-pro` | Code Gen | **haiku** | N/A | Deterministic code generation, 4x faster |
| `typescript-pro` | Code Gen | **haiku** | N/A | Pattern-based TypeScript, 3.3x faster |
| `terraform-specialist` | IaC | **haiku** | N/A | Deterministic Terraform, 3.5x faster |
| `kubernetes-architect` | IaC | **haiku** | N/A | YAML manifest generation |
| `deployment-engineer` | CI/CD | **haiku** | N/A | Pipeline configuration |
| `cloud-architect` | Architecture | **opus** | medium → high | Daily driver, escalate for multi-cloud |
| `security-auditor` | Security | **opus** | medium → high | Daily driver, escalate for breaches |
| `code-reviewer` | Quality | **opus** | medium | Architectural review |
| `debugger` | Troubleshooting | **opus** | medium → high | Daily driver, escalate for distributed |

### Effort Escalation Triggers

| Agent | Effort High Trigger | When |
|-------|---------------------|------|
| `cloud-architect` | Multi-cloud migration, >10 services | Platform impact |
| `security-auditor` | Security breach, critical CVE | Security critical |
| `debugger` | Distributed system, >3 service boundaries | Complex debugging |
| `system-architect` | Platform rewrite, legacy modernization | Long-horizon |
| `incident-responder` | P0 incident, revenue impact | Critical path |

**Strategy**: Opus @ `effort: medium` as daily driver, Haiku for speed tier
**Token Efficiency**: 76% fewer tokens vs Sonnet at medium effort
**Quality**: Superior reasoning with state-of-the-art coding capabilities

---

## Migration Notes

The four-phase rollout (core agents → testing & IaC → architecture & security → validation & documentation) completed on **2025‑11‑14**. The tables above reflect the final state; keep them handy when onboarding new agents or evaluating future model swaps.

---

## Monitoring & Observability

### Key Metrics

**Cost Metrics:**
- Cost per agent call (by model)
- Daily/weekly cost trends
- Cost by agent category

**Performance Metrics:**
- P50, P95, P99 latency (by model)
- Success rate (by agent, by model)
- Escalation rate (context-dependent agents)

**Quality Metrics:**
- User satisfaction scores
- Correction/revision rates
- Fallback trigger frequency

### Alerts

**Cost Anomalies:**
- Daily cost > 120% of 7-day average
- Unexpected Sonnet/Opus usage spike
- Opus calls > 5% of total calls (review escalation criteria)

**Performance Degradation:**
- Success rate < 85% for any agent
- P95 latency > 2× baseline
- Opus calls not showing quality improvement over Sonnet

**Escalation Issues:**
- Escalation rate > 30% (may indicate wrong default)
- Opus escalation rate > 10% (review Opus triggers)
- Fallback rate > 10%

---

## Best Practices

### Opus-First Strategy
1. **Default to Opus** with `effort: medium` for all reasoning tasks
2. **Use Haiku** only for well-defined, deterministic, speed-critical tasks
3. **Escalate to `effort: high`** for critical paths, security, production incidents
4. **Sonnet is legacy fallback** - only use if Opus unavailable

### Effort Level Strategy
5. **`effort: medium`** is the sweet spot - Sonnet quality at 76% fewer tokens
6. **`effort: high`** for critical decisions - exceeds Sonnet by 4.3%
7. **Monitor effort-level ROI** - track when high effort adds value vs medium

### When to Use Haiku
8. **Pattern application**: Scaffolding, templates, deterministic generation
9. **Batch operations**: Repetitive tasks, migrations with clear patterns
10. **Speed-critical**: When latency matters more than reasoning depth
11. **Cost-sensitive bulk**: High-volume, low-complexity operations

### Monitoring & Optimization
12. **Track Opus effort levels** - ensure high effort shows quality improvement
13. **A/B test** effort levels before full rollout
14. **Document reasoning** in agent frontmatter
15. **Review monthly** as Opus capabilities evolve

---

## Future Enhancements

### Smart Two-Tier Routing
- Analyze task complexity before agent selection
- Route deterministic tasks to Haiku, reasoning tasks to Opus
- Learn from user corrections to refine boundaries
- Auto-detect when Haiku should escalate to Opus

### Effort Level Auto-Tuning
- Start with `effort: medium` (default)
- Auto-escalate to `effort: high` if:
  - Task complexity score > 0.8
  - Multi-system scope detected
  - Critical path indicators present
  - Previous medium-effort attempt had low confidence
- De-escalate to medium after successful high-effort completion

### Opus Effort Optimization
- Auto-select effort level based on task characteristics
- Track quality delta between effort levels
- Cost-optimize by defaulting to `medium` effort
- Escalate to `high` effort based on complexity signals

### Cost Budgets
- Per-agent and per-tier cost budgets
- Opus spend limits with approval workflow
- Auto-throttle expensive operations
- User-configurable cost limits per tier

### Performance Profiling
- Track which agents benefit most from Sonnet vs Opus
- Identify over-powered agents (Opus where Sonnet sufficient)
- Measure Opus ROI: quality improvement vs cost increase
- Continuous optimization loop

---

## Resources

- [Anthropic Model Documentation](https://docs.anthropic.com/en/docs/models-overview)
- [Claude Opus 4.5 Announcement](https://www.anthropic.com/news/claude-opus-4-5) - Latest model capabilities
- [Claude Model Comparison](https://docs.anthropic.com/en/docs/about-claude/models) - Opus vs Sonnet vs Haiku
- [Cost Calculator](https://docs.anthropic.com/en/docs/about-claude/pricing)
- Internal: `agents/dependencies.map` - Agent dependency graph
- Internal: `../agents.md` - Complete agent catalog

---

## Changelog

### 2025-11-25: Opus 4.5 as Daily Driver
- **BREAKING**: Opus 4.5 is now the default model for all reasoning tasks
- Sonnet demoted to legacy fallback (Opus with `effort: medium` supersedes it)
- Two-tier strategy: Opus (daily driver) + Haiku (speed tier)
- Effort parameter optimization:
  - `effort: medium` → Sonnet-equivalent quality, 76% fewer tokens
  - `effort: high` → Exceeds Sonnet by 4.3%, 48% fewer tokens
- Updated all 27 reasoning agents from Sonnet → Opus
- 31 Haiku agents retained for deterministic/speed tasks
- Updated orchestration patterns to use Opus @ medium/high
- New cost analysis reflecting effort parameter savings

### 2025-11-14: Initial Two-Tier Strategy
- Implemented Sonnet/Haiku hybrid strategy
- 68% cost reduction achieved
- 9 active agents optimized
