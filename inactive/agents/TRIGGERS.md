# Agent Trigger System

Automatic agent activation based on context, keywords, and file patterns.

## Overview

The trigger system intelligently suggests or auto-activates agents based on:
- **Keywords** in your requests
- **File patterns** being modified
- **Events** (pre-commit, post-commit, pre-deploy)
- **Context** (environment, git status, thresholds)

## Configuration

Triggers are defined in `triggers.yaml`:

```yaml
agent-name:
  keywords:          # Words that trigger this agent
  file_patterns:     # File glob patterns
  events:            # Git/workflow events
  auto:              # Auto-activate (true) or suggest (false)
  priority:          # critical, high, medium, low
  threshold:         # Performance/metric thresholds
```

## Trigger Modes

### Auto-Activation (auto: true)
Agent is automatically activated when conditions match.

**Example**: `security-auditor` auto-activates for security-related files
```yaml
security-auditor:
  auto: true
  priority: critical
  file_patterns:
    - "**/auth/**"
    - "**/*security*.{js,ts,py}"
```

### Suggestion Mode (auto: false)
Agent is suggested but requires confirmation.

**Example**: `code-reviewer` is suggested for code reviews
```yaml
code-reviewer:
  auto: false
  priority: high
  keywords:
    - "review"
    - "PR"
```

## Trigger Types

### Keyword Triggers
Activated when specific words appear in requests:

```
"Review this code" → Suggests: code-reviewer
"Check for security issues" → Auto-activates: security-auditor
"Optimize performance" → Suggests: performance-engineer
```

### File Pattern Triggers
Activated when modifying matched files:

```
Editing: auth/login.ts → Suggests: security-auditor
Editing: *.test.ts → Suggests: test-automator
Editing: migrations/*.sql → Suggests: database-optimizer
```

### Event Triggers
Activated during specific workflow events:

```
pre-commit → test-automator, code-reviewer
pre-deploy → security-auditor, deployment-engineer
post-commit → code-reviewer
```

### Threshold Triggers
Activated when metrics exceed thresholds:

```
Response time >500ms → performance-engineer
Memory usage >500MB → performance-engineer
CPU usage >80% → performance-engineer
```

## Priority Levels

**Critical** - Must-run agents (security, blocking issues)
**High** - Important agents (code review, deployment)
**Medium** - Helpful agents (optimization, analysis)
**Low** - Nice-to-have agents (language-specific helpers)

## Agent Combinations

Pre-defined agent suites for common scenarios:

### Code Review Suite
```yaml
code_review_suite:
  agents:
    - code-reviewer
    - security-auditor
    - test-automator
  keywords:
    - "full review"
    - "PR review"
```

### Security Audit Suite
```yaml
security_audit_suite:
  agents:
    - security-auditor
    - code-reviewer
  keywords:
    - "security audit"
```

### Performance Suite
```yaml
performance_suite:
  agents:
    - performance-engineer
    - database-optimizer
  keywords:
    - "performance audit"
```

## Activation Rules

### Rule 1: Multiple Keyword Match + Auto
```yaml
when: keywords_match >= 2
and: auto == true
action: activate_agent
```

### Rule 2: File Pattern + Critical Priority
```yaml
when: file_pattern_match
and: priority == critical
action: suggest_agent
```

### Rule 3: Single Keyword Match
```yaml
when: keywords_match == 1
action: suggest_agent
```

## Usage Examples

### Example 1: Security Review
```
User: "Check for security vulnerabilities in auth module"

Triggers:
- Keywords: "security", "vulnerabilities", "auth"
- File patterns: **/auth/**
- Priority: critical
- Auto: true

Result: Auto-activates security-auditor
```

### Example 2: Code Review
```
User: "Review this pull request"

Triggers:
- Keywords: "review", "pull request"
- Priority: high
- Auto: false

Result: Suggests code-reviewer
```

### Example 3: Performance Optimization
```
User: "The API is slow, need to optimize"

Triggers:
- Keywords: "slow", "optimize"
- Priority: high
- Auto: false

Result: Suggests performance-engineer
```

### Example 4: Full Review Suite
```
User: "Do a comprehensive review before deployment"

Triggers:
- Keywords: "comprehensive review", "deployment"
- Combination: code_review_suite + deployment_suite

Result: Activates:
- code-reviewer
- security-auditor
- test-automator
- deployment-engineer
```

## Event-Based Triggers

### Pre-Commit Hook
```bash
# Automatically runs before git commit
Triggers:
- test-automator (run tests)
- code-reviewer (check quality)
```

### Pre-Deploy Hook
```bash
# Automatically runs before deployment
Triggers:
- security-auditor (security scan)
- deployment-engineer (deployment prep)
```

## Context-Aware Triggering

### Environment-Based
```yaml
development:   relaxed_triggers (suggestions only)
staging:       moderate_triggers (some auto-activation)
production:    strict_triggers (mandatory security/tests)
```

### Git Context
```yaml
branch_name: feature/* → Suggests test-automator
branch_name: hotfix/* → Auto-activates security-auditor
modified_files: *.test.ts → Suggests test-automator
```

## Customization

### Add New Trigger
```yaml
my-custom-agent:
  keywords:
    - "custom keyword"
  file_patterns:
    - "**/*custom*.ts"
  auto: false
  priority: medium
```

### Modify Existing Trigger
```yaml
code-reviewer:
  keywords:
    - "review"
    - "check"
    - "my custom keyword"  # Add your keyword
  auto: true  # Change to auto-activate
```

### Create Agent Combination
```yaml
my_custom_suite:
  agents:
    - agent1
    - agent2
  trigger_keywords:
    - "my suite trigger"
```

## Best Practices

1. **Use auto-activation sparingly** - Only for critical agents
2. **Set appropriate priorities** - Critical for security, Medium for optimization
3. **Combine related agents** - Create suites for common workflows
4. **Test triggers** - Verify keywords and patterns work as expected
5. **Update regularly** - Add patterns as new code patterns emerge

## Disable Triggers

Temporarily disable triggers:

```bash
# Disable all triggers
export CORTEX_TRIGGERS=false

# Disable specific agent
export CORTEX_NO_SECURITY_AUDITOR=true
```

## Debugging Triggers

View what triggered an agent:

```bash
cortex triggers explain
cortex triggers list-active
cortex triggers test "your request text"
```
