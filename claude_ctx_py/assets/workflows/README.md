# Cortex Workflow Templates

Pre-defined multi-agent sequences for common development tasks.

## Available Workflows

### 🚀 [Feature Development](feature-development.yaml)

**Purpose**: Complete workflow for developing new features from design to deployment

**Trigger**: `new feature`, `implement`, `build`, `create feature`

**Steps**: Architecture → Planning → Implementation → Review → Security → Testing → Performance → Documentation → Deployment

**Use when**: Starting a new feature, adding functionality

---

### 🐛 [Bug Fix](bug-fix.yaml)

**Purpose**: Systematic bug identification, fixing, and validation

**Trigger**: `bug`, `fix`, `error`, `issue`, `broken`

**Steps**: Root Cause Analysis → Fix → Review → Regression Testing → Security → Validation → Documentation → Deployment

**Use when**: Fixing bugs, resolving issues, addressing errors

---

### 🔒 [Security Audit](security-audit.yaml)

**Purpose**: Comprehensive security assessment and remediation

**Trigger**: `security`, `vulnerability`, `audit`, `penetration test`
**Schedule**: Monthly

**Steps**: Threat Assessment → Vulnerability Scanning → Code Review → Penetration Testing → Remediation → Validation → Documentation → Compliance

**Use when**: Security reviews, compliance checks, vulnerability assessments

---

### ⚡ [Performance Optimization](performance-optimize.yaml)

**Purpose**: Systematic performance analysis and optimization

**Trigger**: `slow`, `performance`, `optimize`, `speed up`, `bottleneck`
**Threshold**: Response time >500ms, Memory >500MB, CPU >80%

**Steps**: Baseline → Bottleneck ID → Planning → DB Optimization → Code Optimization → Frontend → Infrastructure → Validation → Load Testing → Monitoring

**Use when**: Performance issues, optimization needs, scaling preparation

---

## Usage

### Via CLI

```bash
# Run a workflow
cortex workflow run feature-development

# List available workflows
cortex workflow list

# Check workflow status
cortex workflow status

# Resume interrupted workflow
cortex workflow resume
```

### Via Natural Language

Workflows are automatically suggested when you use trigger keywords:

```
"I need to implement a new dashboard feature"
→ Suggests: feature-development workflow

"Fix the login bug"
→ Suggests: bug-fix workflow

"Check for security vulnerabilities"
→ Suggests: security-audit workflow

"The app is running slow"
→ Suggests: performance-optimize workflow
```

## Workflow Structure

Each workflow defines:

- **Trigger Conditions**: Keywords and events that activate the workflow
- **Steps**: Ordered sequence of agents/modes to execute
- **Success Criteria**: Requirements for workflow completion
- **Outputs**: Expected deliverables from the workflow

### Example Workflow YAML

```yaml
name: Example Workflow
description: Description of what this workflow does
version: 1.0

trigger:
  keywords: ["keyword1", "keyword2"]
  manual: true

steps:
  - name: Step Name
    agent: agent-name
    description: What this step does
    outputs:
      - output1
      - output2

success_criteria:
  - criterion1
  - criterion2
```

## Creating Custom Workflows

1. Create a new YAML file in `~/.claude/workflows/`
2. Define the workflow structure (see example above)
3. Add trigger conditions
4. Define the step sequence
5. Specify success criteria

## Best Practices

1. **Use Existing Workflows** - Start with templates, customize as needed
2. **Chain Agents Logically** - Each step should build on previous outputs
3. **Define Clear Success Criteria** - Know when the workflow is complete
4. **Document Outputs** - Track what each workflow produces
5. **Review and Iterate** - Improve workflows based on experience

## Agent Reference

Workflows can invoke these agents:

- `system-architect` - Architecture design
- `requirements-analyst` - Requirements analysis
- `code-reviewer` - Code review
- `security-auditor` - Security assessment
- `test-automator` - Test generation
- `performance-engineer` - Performance analysis
- `deployment-engineer` - Deployment preparation
- `technical-writer` - Documentation
- `root-cause-analyst` - Problem diagnosis
- `database-optimizer` - Database optimization
- `devops-architect` - Infrastructure
- `quality-engineer` - Quality assurance

## Modes Reference

Workflows can activate these modes:

- `Task_Management` - Complex multi-step operations
- `Token_Efficiency` - Token-optimized communication
- `Brainstorming` - Collaborative discovery
- `Introspection` - Meta-cognitive analysis
