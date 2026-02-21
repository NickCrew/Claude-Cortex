---
layout: default
title: AI Intelligence
parent: Guides
nav_order: 3
---

# AI Intelligence

Cortex includes an AI intelligence engine that analyzes your project context and recommends the right agents and skills.

## How It Works

1. **Context Detection** -- analyzes changed files, detects tech stack, auth patterns, test files, frontend/backend code
2. **Pattern Learning** -- learns from successful sessions and recommends optimal agent combinations
3. **Workflow Prediction** -- predicts agent sequences based on similar past work
4. **Auto-Activation** -- high-confidence agents activate automatically (threshold: 80%)

## Getting Recommendations

```bash
cortex ai recommend
```

Example output:

```
=== AI Recommendations ===

Based on project type: python-fastapi
Active context: Building REST API with authentication

1. security-auditor (Confidence: 95%)
   Why: Auth code detected

2. api-design-patterns (Confidence: 90%)
   Why: FastAPI project with REST API requirements

3. code-reviewer (Confidence: 85%)
   Why: Changes detected - code review recommended
```

## Auto-Activation

```bash
cortex ai auto-activate
```

Agents with confidence scores above 80% are activated automatically.

## Watch Mode

Watch mode monitors your project for changes in real-time:

```bash
# Foreground (Ctrl+C to stop)
cortex ai watch

# Background daemon
cortex ai watch --daemon
cortex ai watch --status   # Check daemon status
cortex ai watch --stop     # Stop daemon
```

Example watch mode output:

```
[10:33:12] Context detected: Backend, Auth
  3 files changed

  Recommendations:
     security-auditor [AUTO] 95% - Auth code detected
     code-reviewer [AUTO]    75% - Changes detected

[10:33:12] Auto-activating 2 agents...
     security-auditor
     code-reviewer
```

## Recording Sessions

After a successful session, record it so the intelligence engine can learn:

```bash
cortex ai record-success --outcome "feature complete"
```

## TUI Integration

Press `0` in the TUI to open the AI Assistant view:

- View recommendations with confidence scores
- Press `A` to auto-activate recommended agents
- See workflow predictions and context analysis

## Exporting

```bash
cortex ai export --output recommendations.json
```
