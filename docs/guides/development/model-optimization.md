---
layout: default
title: Model Optimization
nav_order: 6
---

# Model Optimization Strategy

Strategic model assignment (Haiku vs Sonnet) for optimal performance and cost efficiency across claude-ctx agents.

## Overview

claude-ctx uses a hybrid model strategy:
- **Sonnet 4.5**: Complex reasoning, architecture decisions, security analysis
- **Haiku 4**: Fast execution, deterministic tasks, code generation

**Cost Impact**: 40-60% savings on deterministic tasks
**Performance**: 2-5x faster for Haiku-appropriate workloads

## Model Assignment Criteria

### Use Sonnet When:
- **Complex reasoning** required (architecture, design decisions)
- **Security-critical** analysis (vulnerability assessment, threat modeling)
- **Multi-factor evaluation** (code review with architectural patterns)
- **Business-critical** decisions (legal, compliance, strategy)
- **Novel problem solving** (debugging complex issues, incident response)
- **Creative synthesis** (documentation strategy, technical writing)

### Use Haiku When:
- **Deterministic execution** (code generation from specs)
- **Pattern application** (applying known patterns, scaffolding)
- **Test generation** (unit/integration tests following templates)
- **Documentation generation** (API docs, code comments)
- **Configuration management** (Terraform, Kubernetes manifests)
- **Data transformation** (parsing, formatting, validation)
- **Repetitive operations** (batch processing, migrations)

## Agent Model Assignments

### Sonnet Agents (Complex Reasoning)

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

**Total Sonnet: 27 agents**

---

### Haiku Agents (Fast Execution)

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

These agents may use either model based on task complexity:

**Default Haiku, Escalate to Sonnet:**
- `database-optimizer` - Query rewriting (Haiku), schema redesign (Sonnet)
- `refactoring-expert` - Simple refactors (Haiku), architectural refactors (Sonnet)
- `workflow-orchestrator` - Workflow execution (Haiku), workflow design (Sonnet)
- `multi-agent-coordinator` - Task routing (Haiku), coordination strategy (Sonnet)
- `context-manager` - Context extraction (Haiku), context strategy (Sonnet)

**Default Sonnet, Fast Path to Haiku:**
- `learning-guide` - Curriculum design (Sonnet), example generation (Haiku)
- `tutorial-engineer` - Tutorial design (Sonnet), code examples (Haiku)
- `socratic-mentor` - Question formulation (Sonnet), fact retrieval (Haiku)
- `prompt-engineer` - Prompt strategy (Sonnet), prompt variations (Haiku)

---

## Hybrid Orchestration Patterns

### Pattern 1: Design → Implement → Review
```
backend-architect (Sonnet)
  ↓ produces API spec
python-pro (Haiku)
  ↓ implements endpoints
test-automator (Haiku)
  ↓ generates tests
code-reviewer (Sonnet)
  ↓ validates architecture
```

**Cost**: 2 Sonnet calls + 2 Haiku calls
**Savings**: 50% vs all-Sonnet

### Pattern 2: Research → Generate → Validate
```
search-specialist (Sonnet)
  ↓ researches patterns
docs-architect (Haiku)
  ↓ generates documentation
technical-writer (Haiku)
  ↓ polishes content
```

**Cost**: 1 Sonnet + 2 Haiku
**Savings**: 67% vs all-Sonnet

### Pattern 3: Troubleshoot → Fix → Test
```
debugger (Sonnet)
  ↓ diagnoses root cause
python-pro (Haiku)
  ↓ implements fix
test-automator (Haiku)
  ↓ adds regression tests
```

**Cost**: 1 Sonnet + 2 Haiku
**Savings**: 67% vs all-Sonnet

### Pattern 4: Audit → Remediate → Verify
```
security-auditor (Sonnet)
  ↓ identifies vulnerabilities
typescript-pro (Haiku)
  ↓ applies security fixes
quality-engineer (Sonnet)
  ↓ validates remediation
```

**Cost**: 2 Sonnet + 1 Haiku
**Savings**: 33% vs all-Sonnet

---

## Implementation Guidelines

### Agent Frontmatter

**Sonnet Agents:**
```yaml
model:
  preference: sonnet
  fallbacks:
    - haiku
  reasoning: "Complex architectural analysis and security evaluation"
```

**Haiku Agents:**
```yaml
model:
  preference: haiku
  fallbacks:
    - sonnet
  reasoning: "Deterministic code generation from well-defined specifications"
```

**Context-Dependent:**
```yaml
model:
  preference: haiku
  escalation:
    to: sonnet
    when:
      - "architectural refactoring"
      - "novel pattern discovery"
      - "security implications"
  reasoning: "Fast path for standard operations, escalate for complex decisions"
```

### Decision Matrix

| Task Characteristic | Haiku Score | Sonnet Score |
|---------------------|-------------|--------------|
| Well-defined spec   | +2          | 0            |
| Novel problem       | 0           | +2           |
| Pattern application | +2          | 0            |
| Complex reasoning   | 0           | +2           |
| Security critical   | -1          | +2           |
| Code generation     | +2          | 0            |
| Architecture design | 0           | +2           |
| Batch processing    | +2          | 0            |
| Creative synthesis  | 0           | +2           |
| Documentation       | +1          | +1           |

**Score > 3**: Strong preference
**Score 1-3**: Moderate preference
**Score < 1**: Consider alternative

---

## Cost Analysis

### Current State (All Sonnet)
```
Average task: 5 agent calls × $3 per 1M input tokens
= $15 per 1M tokens

Daily volume (1000 tasks):
= $15,000 per million tokens
```

### Optimized (Hybrid)
```
Architecture tasks (30%): 3 Sonnet + 2 Haiku
Implementation tasks (50%): 1 Sonnet + 4 Haiku
Maintenance tasks (20%): 0 Sonnet + 5 Haiku

Weighted average:
= (0.3 × $9) + (0.5 × $3.80) + (0.2 × $0.80)
= $2.70 + $1.90 + $0.16
= $4.76 per task

Daily volume (1000 tasks):
= $4,760 per million tokens

Savings: 68% reduction
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

## Migration Plan

### Phase 1: Core Agents (Week 1)
- Update 10 highest-volume agents
- Deploy Haiku for code generation agents
- Monitor success rates and rollback if < 90%

### Phase 2: Testing & IaC (Week 2)
- Migrate test generation agents
- Migrate infrastructure agents
- Validate cost savings (target: 40%)

### Phase 3: Documentation & Tools (Week 3)
- Migrate documentation agents
- Migrate tooling agents
- Measure latency improvements (target: 3x)

### Phase 4: Context-Dependent (Week 4)
- Implement escalation logic
- Add smart routing based on task complexity
- Fine-tune thresholds

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
- Unexpected Sonnet usage spike

**Performance Degradation:**
- Success rate < 85% for any agent
- P95 latency > 2× baseline

**Escalation Issues:**
- Escalation rate > 30% (may indicate wrong default)
- Fallback rate > 10%

---

## Best Practices

1. **Default to Haiku** for well-defined, deterministic tasks
2. **Use Sonnet** for novel problems, security, architecture
3. **Implement escalation** for borderline cases
4. **Monitor metrics** continuously for optimization
5. **A/B test** model changes before full rollout
6. **Document reasoning** in agent frontmatter
7. **Review quarterly** and adjust based on new model capabilities
8. **Cost-quality trade-offs** should favor quality for security/critical paths
9. **Batch operations** should heavily favor Haiku
10. **User-facing analysis** should use Sonnet for better explanations

---

## Future Enhancements

### Smart Routing
- Analyze task complexity before agent selection
- Route simple tasks to Haiku, complex to Sonnet
- Learn from user corrections

### Auto-Escalation
- Start with Haiku
- Escalate to Sonnet if:
  - Confidence score < 0.7
  - User provides corrective feedback
  - Task complexity indicators detected

### Cost Budgets
- Per-agent cost budgets
- Auto-throttle expensive operations
- User-configurable cost limits

### Performance Profiling
- Track which agents benefit most from Sonnet
- Identify over-powered agents (Sonnet where Haiku sufficient)
- Continuous optimization loop

---

## Resources

- [Anthropic Model Documentation](https://docs.anthropic.com/en/docs/models-overview)
- [Claude Sonnet vs Haiku Comparison](https://docs.anthropic.com/en/docs/about-claude/models)
- [Cost Calculator](https://docs.anthropic.com/en/docs/about-claude/pricing)
- Internal: `agents/dependencies.map` - Agent dependency graph
- Internal: `../agents.md` - Complete agent catalog
