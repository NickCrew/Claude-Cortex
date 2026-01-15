---
layout: default
title: AI Watch Mode
parent: Tutorials
nav_order: 3
permalink: /tutorials/ai-watch-mode/
---

# AI Watch Mode Tutorial

Learn how to leverage cortex's intelligent recommendation system for context-aware agent activation and workflow optimization.

## What You'll Learn

By the end of this tutorial, you'll be able to:

- Understand the AI Intelligence System architecture
- Use the AI Assistant view for recommendations
- Configure auto-activation for high-confidence suggestions
- Interpret context health scores
- Record successful sessions for pattern learning

**Time Estimate:** 15-20 minutes
**Prerequisites:** Completed [Getting Started with TUI](../getting-started-tui/)

---

## Part 1: Understanding AI Watch Mode

### What is AI Watch Mode?

AI Watch Mode is an intelligent layer that analyzes your work context and automatically recommends the right agents and modes. It answers the question: *"Which agents should I activate for this task?"*

### Core Capabilities

| Feature | Description |
|---------|-------------|
| **Context Detection** | Analyzes git diff, file types, and code patterns |
| **Pattern Learning** | Learns from successful sessions |
| **Recommendations** | Suggests agents with confidence scores |
| **Auto-Activation** | Activates high-confidence agents automatically |
| **Health Scoring** | Identifies misalignments between context and active agents |

### How It Works

```
┌─────────────────────────────────────────────────────────────┐
│  Your Code Changes                                          │
│  ├── auth.py (modified)                                    │
│  ├── api/routes.ts (modified)                              │
│  └── tests/test_auth.py (added)                            │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  Context Analysis                                           │
│  ├── Detected: Python, TypeScript, Auth code, API routes   │
│  ├── Pattern: Backend + API + Security                     │
│  └── Historical match: 87% similar to past sessions        │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  Recommendations                                            │
│  ├── security-auditor (95% confidence) [AUTO]              │
│  ├── python-pro (90% confidence) [AUTO]                    │
│  ├── api-documenter (75% confidence)                       │
│  └── test-automator (70% confidence)                       │
└─────────────────────────────────────────────────────────────┘
```

**Checkpoint:** You understand the conceptual flow of AI Watch Mode.

---

## Part 2: Accessing the AI Assistant View

### Launch the TUI

```bash
cortex tui
```

### Open AI Assistant (Key 0)

Press **`0`** to switch to the AI Assistant view.

**What You Should See:**

```
┌─────────────────────────────────────────────────────────────┐
│ cortex TUI                            [View: AI Watch]  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  🤖 INTELLIGENT RECOMMENDATIONS                             │
│  ─────────────────────────────────────────────────          │
│  Type     Recommendation           Conf   Reason            │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━    │
│  🔴 Agent  security-auditor [AUTO]  95%   Auth code detected│
│  🔵 Agent  python-pro [AUTO]        90%   .py files changed │
│  ⚪ Agent  code-reviewer            75%   8 files modified  │
│                                                             │
│  📊 CONTEXT HEALTH                                          │
│  ─────────────────────────────────────────────────          │
│  Score: 85/100 [Healthy]                                    │
│                                                             │
│  Issues:                                                    │
│  ⚠️ typescript-pro active but no .ts files                   │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ [A]uto-activate  [R]efresh  [H]ealth details                │
└─────────────────────────────────────────────────────────────┘
```

### Understanding the Display

**Recommendation Types:**
- **🔴 Critical** - High urgency, strongly recommended
- **🔵 Suggested** - Good match for current context
- **⚪ Optional** - Might be helpful

**Confidence Levels:**
- **[AUTO]** - Will auto-activate if enabled (≥85% confidence)
- **75-84%** - Strong recommendation
- **50-74%** - Worth considering
- **<50%** - Low confidence

**Checkpoint:** You can navigate to and read the AI Assistant view.

---

## Part 3: Context Health Analysis

### What is Context Health?

Context Health measures the alignment between your **active agents/modes** and your **actual work**. A high score means your context is optimized; a low score indicates misalignment.

### Health Score Ranges

| Score | Status | Meaning |
|-------|--------|---------|
| **81-100** | Healthy | Agents well-aligned with activity |
| **51-80** | Warning | Some misalignment detected |
| **0-50** | Critical | Significant context issues |

### Common Health Issues

**1. Missing Language Agents**
```
Issue: Editing Python files but 'python-pro' agent is inactive.
Fix: Activate python-pro agent
```

**2. Unused Agents (Context Bloat)**
```
Issue: Agent 'typescript-pro' is active but no TypeScript files edited.
Fix: Deactivate typescript-pro to reduce context
```

**3. Mode Conflicts**
```
Issue: 'Amphetamine' (speed) and 'Security_Audit' (caution) are both active.
Fix: Choose one mode based on current priority
```

**4. Agent Overload**
```
Issue: High cognitive load: 5 agents active. Context may be diluted.
Fix: Deactivate less relevant agents
```

### Viewing Health Details

Press **`H`** in the AI Assistant view to see detailed health analysis:

```
┌─────────────────────────────────────────────────────────────┐
│  CONTEXT HEALTH DETAILS                                     │
├─────────────────────────────────────────────────────────────┤
│  Overall Score: 65/100 [Warning]                            │
│                                                             │
│  Active Agents: 4                                           │
│  Active Modes: 2                                            │
│  Recent Files: 8                                            │
│                                                             │
│  Issues Found:                                              │
│  ────────────────────────────────────────────               │
│  ⚠️ -15pts: python-pro inactive, editing .py files          │
│  ⚠️ -5pts:  typescript-pro active, no .ts files             │
│  ⚠️ -10pts: 4 agents active, consider reducing              │
│  ⚠️ -5pts:  High file churn, consider Amphetamine mode      │
│                                                             │
│  Recommendations:                                           │
│  ────────────────────────────────────────────               │
│  ✓ Enable python-pro                                        │
│  ✓ Disable typescript-pro                                   │
│  ✓ Enable Amphetamine mode                                  │
└─────────────────────────────────────────────────────────────┘
```

**Checkpoint:** You understand context health scoring and can identify issues.

---

## Part 4: Auto-Activation

### What is Auto-Activation?

Auto-activation automatically enables recommended agents when confidence exceeds a threshold (default: 85%).

### Using Auto-Activation

**Manual Trigger (Recommended for Learning):**

Press **`A`** in the AI Assistant view to activate all high-confidence recommendations.

```
┌─────────────────────────────────────────────────────────────┐
│  AUTO-ACTIVATION RESULTS                                    │
├─────────────────────────────────────────────────────────────┤
│  ✓ Activated: security-auditor (95% confidence)            │
│  ✓ Activated: python-pro (90% confidence)                  │
│  ✗ Skipped: code-reviewer (75% - below threshold)          │
│                                                             │
│  2 agents activated, 1 skipped                              │
└─────────────────────────────────────────────────────────────┘
```

**CLI Alternative:**

```bash
# View recommendations
cortex ai recommend

# Auto-activate high-confidence agents
cortex ai auto-activate

# With custom threshold
cortex ai auto-activate --threshold 80
```

### Auto-Activation Safety

Auto-activation has built-in safeguards:

1. **Threshold Gate** - Only activates agents above confidence threshold
2. **Conflict Detection** - Won't activate conflicting modes
3. **Undo Support** - Press `U` to undo recent auto-activation
4. **Audit Log** - All auto-activations are logged

**Checkpoint:** You can trigger auto-activation and understand its safeguards.

---

## Part 5: Pattern Learning

### Recording Successful Sessions

The AI system learns from your successful sessions to improve future recommendations.

**After completing a task successfully:**

```bash
# Record success with outcome
cortex ai record-success --outcome "feature complete"

# Or with more detail
cortex ai record-success \
  --outcome "API authentication implemented" \
  --duration 45m
```

### What Gets Recorded

When you record success, the system saves:
- **Active agents** at session end
- **Context key** (file types, patterns detected)
- **Duration** of session
- **Outcome description**

### How Learning Improves Recommendations

```
Session 1: Backend API work → Used security-auditor → Success
Session 2: Backend API work → Recommended security-auditor (70% confidence)
Session 3: Backend API work → Recommended security-auditor (85% confidence)
Session 4: Backend API work → Auto-activates security-auditor (92% confidence)
```

Over time, the system builds a model of which agents work best for which contexts.

**Checkpoint:** You understand how to record successful sessions for learning.

---

## Part 6: CLI Commands Reference

### AI Commands

```bash
# Get recommendations for current context
cortex ai recommend

# Get detailed recommendations with reasoning
cortex ai recommend --verbose

# Auto-activate recommended agents
cortex ai auto-activate

# Auto-activate with custom threshold
cortex ai auto-activate --threshold 75

# Export recommendations to JSON
cortex ai export --output recommendations.json

# Record successful session
cortex ai record-success --outcome "description"

# View learning history
cortex ai history

# Reset learned patterns (use with caution)
cortex ai reset-patterns
```

### Integration with Other Commands

```bash
# Combine with context export
cortex ai auto-activate && cortex export --full

# Check health before export
cortex ai health && cortex export
```

---

## Part 7: Best Practices

### 1. Start Sessions with a Health Check

```bash
cortex ai health
```

Or press `0` in TUI to see the AI Assistant view first.

### 2. Record Successful Sessions

Build the learning model by recording successful outcomes:

```bash
cortex ai record-success --outcome "bug fixed"
```

### 3. Trust High-Confidence Recommendations

Agents with 85%+ confidence are usually correct. Use auto-activation for speed.

### 4. Review Low-Confidence Suggestions

Recommendations below 70% warrant manual review before activation.

### 5. Monitor Context Health

Keep health score above 80 for optimal Claude performance:
- Deactivate unused agents
- Enable missing language agents
- Resolve mode conflicts

### 6. Don't Over-Activate

More agents ≠ better context. 2-4 focused agents typically outperform 6+ diluted agents.

---

## Troubleshooting

### Problem: No Recommendations Appearing

**Symptoms:** AI Assistant view shows "No recommendations"

**Solutions:**
1. Ensure you have uncommitted changes (`git status`)
2. Check that files have recognizable extensions
3. Run `cortex ai recommend --verbose` for diagnostics

### Problem: Auto-Activation Not Working

**Symptoms:** Pressing `A` does nothing

**Solutions:**
1. Verify recommendations exist with confidence ≥85%
2. Check for agent conflicts that prevent activation
3. Try `cortex ai auto-activate` from CLI for detailed output

### Problem: Low Health Score

**Symptoms:** Health consistently below 70

**Solutions:**
1. Review active agents - deactivate unused ones
2. Activate agents matching your file types
3. Resolve any mode conflicts
4. Consider reducing total active agents

---

## Summary

You've learned how to:

- Access and interpret the AI Assistant view
- Understand context health scoring
- Use auto-activation for efficient agent management
- Record successful sessions for pattern learning
- Troubleshoot common AI Watch Mode issues

## Next Steps

- **[Skill Authoring Cookbook](../skill-authoring-cookbook/)** - Create custom skills
- **[Workflow Orchestration](../workflow-orchestration/)** - Multi-step automation
- **[CI/CD Integration](../ci-cd-integration/)** - Automate context in pipelines

---

## Quick Reference

| Key | Action |
|-----|--------|
| `0` | Open AI Assistant view |
| `A` | Auto-activate recommendations |
| `R` | Refresh recommendations |
| `H` | View health details |
| `U` | Undo recent auto-activation |

| CLI Command | Purpose |
|-------------|---------|
| `ai recommend` | View current recommendations |
| `ai auto-activate` | Activate high-confidence agents |
| `ai health` | Check context health |
| `ai record-success` | Record successful session |
