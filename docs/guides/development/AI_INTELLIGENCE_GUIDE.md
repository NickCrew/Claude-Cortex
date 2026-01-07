# 🤖 AI Intelligence System - Complete Guide

## Overview

The AI Intelligence System is a **learning, predictive automation layer** that makes the cortex framework **think for you**. It analyzes your context, learns from successful patterns, and automatically recommends or activates the right agents—keeping you in the Claude Code flow without manual management.

## 🎯 Core Philosophy

**"Stay in Claude Code, let AI manage the framework"**

- ✅ Context-aware agent recommendations
- ✅ Pattern learning from successful sessions
- ✅ Predictive workflow generation
- ✅ Auto-activation of high-confidence agents
- ✅ Zero-configuration intelligence

## 🧠 What It Does

### 1. Context Detection
Automatically analyzes:
- **Files changed** (from git diff)
- **File types** (.py, .ts, .tsx, etc.)
- **Code patterns** (auth, API, tests, database, frontend, backend)
- **Error signals** (test failures, build errors)
- **Time patterns** (session duration, activity timing)

### 2. Pattern Learning
Learns from successful sessions:
- **Agent sequences** that work together
- **Context-to-agent** mappings
- **Success probabilities** for workflows
- **Duration estimates** for common patterns

### 3. Intelligent Recommendations
Provides:
- **Agent recommendations** with confidence scores
- **Urgency levels** (critical, high, medium, low)
- **Auto-activation** flags for high-confidence suggestions
- **Reasoning** for each recommendation

### 4. Workflow Prediction
Predicts optimal workflows:
- **Agent sequence** based on similar past sessions
- **Confidence score** for prediction
- **Estimated duration** from historical data
- **Success probability** from pattern analysis

## 🚀 Quick Start

### Launch TUI with AI Assistant

```bash
cortex tui
```

Then press **`8`** to open the AI Assistant view.

### CLI Commands

```bash
# Get AI recommendations
cortex ai recommend

# Auto-activate recommended agents
cortex ai auto-activate

# Export recommendations to JSON
cortex ai export --output recommendations.json

# Record successful session for learning
cortex ai record-success --outcome "feature complete"
```

## 📺 TUI AI Assistant View (Key 8)

The AI Assistant view shows:

### 🤖 INTELLIGENT RECOMMENDATIONS
```
Type        Recommendation          Confidence  Reason
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔴 Agent    security-auditor [AUTO]  95%        Auth code detected
🔵 Agent    code-reviewer            85%        8 files changed
⚪ Agent    performance-engineer     70%        API changes detected
```

### 🎯 WORKFLOW PREDICTION
```
Workflow:       auto_backend_api
Confidence:     87%
Est. Duration:  5m 30s
Success Rate:   91%

Agent Sequence:
  1. backend-architect
  2. security-auditor
  3. test-automator
  4. api-documenter
```

### 📊 CONTEXT ANALYSIS
```
Files Changed:  8
Detected:       Backend, API, Auth
Issues:         0 errors, 0 test failures
```

### ⚡ QUICK ACTIONS
- **Press `A`** → Auto-activate recommended agents
- **Press `R`** → Refresh recommendations

## 🎮 Keyboard Shortcuts

### In Any View:
- **`8`** - Switch to AI Assistant view
- **`A`** - Auto-activate high-confidence recommendations
- **`R`** - Refresh data/recommendations

### In AI Assistant View:
- **`↑` / `↓`** - Navigate (if scrollable)
- **`A`** - Execute auto-activation
- **`1-7`** - Switch to other views

## 🧪 How It Works

### Context Detection Flow

```
1. Git diff → Changed files
   ↓
2. File analysis → Detect patterns
   - auth.py → has_auth = True
   - api/routes.ts → has_api = True
   - test_*.py → has_tests = True
   ↓
3. Generate context key → "backend_api_auth"
   ↓
4. Look up historical patterns
   ↓
5. Generate recommendations
```

### Pattern Learning Flow

```
Session Start
   ↓
Context detected: backend_api
   ↓
Agents activated: backend-architect, security-auditor, test-automator
   ↓
Duration: 8m 30s
   ↓
Outcome: SUCCESS
   ↓
Record for learning:
{
  "context": "backend_api",
  "agents": ["backend-architect", "security-auditor", "test-automator"],
  "duration": 510,
  "outcome": "success"
}
   ↓
Future sessions with "backend_api" context:
→ Recommend same agents with 90%+ confidence
→ Predict 8-9 minute duration
→ Suggest same workflow sequence
```

### Recommendation Algorithm

**Rule-Based** (Hard-coded intelligence):
- Auth code detected → `security-auditor` (95% confidence, auto-activate)
- Test failures > 0 → `test-automator` (95% confidence, auto-activate)
- Any changeset → `quality-engineer` (85% confidence, auto-activate)
- Any changeset → `code-reviewer` (75% confidence, auto-activate)
- TypeScript/TSX → `typescript-pro` (85% confidence, auto-activate)
- React/JSX/TSX → `react-specialist` (80% confidence, auto-activate)
- User-facing UI → `ui-ux-designer` (80% confidence, auto-activate)
- Database/SQL changes → `database-optimizer`, `sql-pro` (80% confidence, auto-activate)
- Cross-cutting changes → `architect-review` (75% confidence, auto-activate)
- Database/API changes → `performance-engineer` (70% confidence, auto-activate)

**Pattern-Based** (Learned intelligence):
- Used in 80% of similar sessions → 80% confidence, auto-activate
- Used in 50% of similar sessions → 50% confidence
- Used in <30% of similar sessions → Not recommended

**Combined Score**:
- Takes maximum confidence from both sources
- Auto-activates if ≥80% confidence
- Shows urgency based on confidence + context signals

## 📈 Auto-Activation Logic

Agents are **automatically activated** when:

1. **Confidence ≥ 80%** from pattern learning
2. **Rule-based urgency** is "critical" or "high"
3. **Context signals** strong need (e.g., auth changes)

Examples:
- ✅ Auth file changed → `security-auditor` (95%, AUTO)
- ✅ Test failures detected → `test-automator` (95%, AUTO)
- ✅ Any changeset → `quality-engineer`, `code-reviewer` (AUTO)
- ✅ React UI changes → `react-specialist`, `ui-ux-designer` (AUTO)

## 💾 Data Storage

All learning data is stored in the active Claude directory:
- default: `~/.claude/`
- override: `$CLAUDE_PLUGIN_ROOT` or project `.claude/` via `--scope project`

Paths (relative to the active Claude directory):
```
intelligence/
  └── session_history.json
```

### session_history.json Structure

```json
{
  "patterns": {
    "backend_api": [
      {
        "timestamp": "2025-11-04T16:00:00",
        "context": {
          "files_changed": ["api/routes.ts", "auth.ts"],
          "has_backend": true,
          "has_api": true,
          "has_auth": true
        },
        "agents": ["backend-architect", "security-auditor"],
        "duration": 510,
        "outcome": "success"
      }
    ]
  },
  "agent_sequences": [
    ["backend-architect", "security-auditor", "test-automator"]
  ],
  "success_contexts": [...],
  "last_updated": "2025-11-04T16:30:00"
}
```

## 🎓 Learning Examples

### Example 1: Security Pattern

**Session 1-3**: Work on auth module
- Manually activate `security-auditor`
- Record successes

**Session 4+**: AI auto-detects
```
🤖 AI detected auth changes
   Recommending: security-auditor (95% confidence)
   [AUTO-ACTIVATED]
```

### Example 2: API Development Pattern

**Sessions with API work**:
- Pattern emerges: `backend-architect` → `api-documenter` → `test-automator`

**Future API work**:
```
🎯 Workflow Prediction
   1. backend-architect
   2. api-documenter
   3. test-automator
   Confidence: 87%
   Duration: 6m 15s
```

### Example 3: Code Review Pattern

**Any changeset**:
- AI always triggers quality + code review
- Additional reviewers add based on file types

**Future changesets**:
```
🔵 Recommendation: quality-engineer
   Reason: Changes detected
   Confidence: 85%
🔵 Recommendation: code-reviewer
   Reason: Changes detected
   Confidence: 75%
```

## 🛠️ CLI Usage Examples

### Get Recommendations

```bash
$ cortex ai recommend

🤖 AI RECOMMENDATIONS
══════════════════════════════════════════════════════════════════════

1. 🔴 security-auditor [AUTO]
   Confidence: 95%
   Reason: Auth code detected - security review recommended

2. 🔵 quality-engineer [AUTO]
   Confidence: 85%
   Reason: Changes detected - quality review recommended

3. 🔵 code-reviewer [AUTO]
   Confidence: 75%
   Reason: Changes detected - code review recommended

══════════════════════════════════════════════════════════════════════

🎯 WORKFLOW PREDICTION

Workflow: auto_backend_api_auth
Confidence: 87%
Estimated Duration: 5m 30s
Success Probability: 91%

Agent Sequence:
  1. backend-architect
  2. security-auditor
  3. test-automator

══════════════════════════════════════════════════════════════════════

💡 TIP: Press '0' in the TUI for interactive AI assistant
        Press 'A' to auto-activate recommended agents
```

### Auto-Activate Agents

```bash
$ cortex ai auto-activate

🤖 Auto-activating 2 agents...

✓ security-auditor
✓ test-automator

✓ Activated 2/2 agents
```

### Export to JSON

```bash
$ cortex ai export --output my-recommendations.json

✓ Exported AI recommendations to my-recommendations.json
  2 agent recommendations
  1 workflow prediction (87% confidence)
```

### Record Success

```bash
$ cortex ai record-success --outcome "feature complete"

✓ Recorded successful session for learning
  Context: 8 files changed
  Agents: backend-architect, security-auditor, test-automator
  Outcome: feature complete

💡 This session will improve future recommendations!
```

## 🎯 Use Cases

### 1. **Security-Sensitive Work**
**Context**: Changing auth/authentication code
**AI Action**: Auto-activates `security-auditor`
**Benefit**: Never forget security review on critical code

### 2. **Large Refactoring**
**Context**: Changing 10+ files across multiple modules
**AI Action**: Recommends `code-reviewer` + `test-automator`
**Benefit**: Systematic quality checks on complex changes

### 3. **API Development**
**Context**: Adding/modifying API endpoints
**AI Action**: Predicts workflow → architect → test → document
**Benefit**: Consistent API development process

### 4. **Bug Fixing**
**Context**: Test failures detected
**AI Action**: Auto-activates `test-automator`
**Benefit**: Immediate focus on fixing tests

### 5. **Team Patterns**
**Context**: Similar work to past successful sessions
**AI Action**: Replicates successful agent combinations
**Benefit**: Learn from team's best practices

## 🔬 Advanced Features

### Custom Context Detection

The system detects these contexts automatically:
- `frontend` - .tsx, .jsx, .vue, .svelte files
- `backend` - .py, .go, .java, .rs files
- `database` - migration, schema, db files
- `api` - api, routes files
- `auth` - auth files
- `tests` - test files

### Confidence Scoring

```python
# Rule-based recommendations
if has_auth:
    recommend(security-auditor, confidence=0.95, auto=True)

# Pattern-based recommendations
usage_rate = times_used / similar_sessions
if usage_rate >= 0.8:
    recommend(agent, confidence=usage_rate, auto=True)
elif usage_rate >= 0.3:
    recommend(agent, confidence=usage_rate, auto=False)
```

### Workflow Prediction Algorithm

```python
# Find most common agent sequence for context
context_key = generate_context_key(current_context)
similar_sessions = get_sessions_by_context(context_key)

if len(similar_sessions) >= 3:  # Minimum for prediction
    most_common_sequence = find_most_common_sequence(similar_sessions)
    confidence = frequency / total_sessions
    avg_duration = calculate_average_duration(similar_sessions)

    return WorkflowPrediction(
        agents=most_common_sequence,
        confidence=confidence,
        duration=avg_duration,
        success_rate=confidence
    )
```

## 📊 Analytics

Track learning effectiveness:
```bash
# View intelligence data
cat ~/.claude/intelligence/session_history.json | jq '.patterns | keys'

# See pattern count
cat ~/.claude/intelligence/session_history.json | jq '.patterns | to_entries | map({key: .key, count: (.value | length)}) | sort_by(.count) | reverse'
```

## 🚨 Best Practices

### 1. Record Successful Sessions
```bash
# After completing work successfully
cortex ai record-success --outcome "feature complete"
```

### 2. Review Recommendations
- Check AI assistant view (Key 8) at session start
- Understand WHY agents are recommended
- Trust high-confidence (≥80%) recommendations

### 3. Let It Learn
- Use consistent agent combinations for similar work
- Record outcomes after successful sessions
- Review patterns after 5-10 sessions

### 4. Override When Needed
- AI is advisory, not mandatory
- You can always manually activate/deactivate
- Use your judgment for edge cases

## 🎉 Benefits

### For Individual Developers:
- ✅ **Fewer decisions** - AI recommends the right agents
- ✅ **Faster setup** - Auto-activation saves time
- ✅ **Learn patterns** - See what works best
- ✅ **Stay in flow** - Less context switching

### For Teams:
- ✅ **Consistent practices** - Learn from successful patterns
- ✅ **Onboarding** - New members see recommended workflows
- ✅ **Best practices** - AI captures what works
- ✅ **Quality gates** - Auto-activate reviewers/testers

## 🔮 Future Enhancements

Potential future features:
- [ ] Team-wide pattern sharing
- [ ] Multi-project learning
- [ ] Time-of-day patterns
- [ ] Developer-specific preferences
- [ ] Integration with CI/CD results
- [ ] Automatic quality gate enforcement
- [ ] Cost/benefit analysis per agent
- [ ] Collaborative filtering across projects

## 🆘 Troubleshooting

### No Recommendations

**Problem**: AI shows "No recommendations"
**Causes**:
1. No files changed (git diff empty)
2. Not enough learning data yet
3. Context doesn't match any patterns

**Solutions**:
- Make some changes, commit, then check again
- Record successful sessions to build patterns
- Manually activate agents a few times

### Low Confidence Scores

**Problem**: All recommendations <50% confidence
**Cause**: Limited learning data for this context

**Solution**: Record 3-5 successful sessions with similar context

### Wrong Recommendations

**Problem**: AI recommends irrelevant agents
**Causes**:
1. Context detection is too broad
2. Past sessions included unnecessary agents

**Solutions**:
- Don't record sessions with failed outcomes
- Deactivate unused agents before recording
- Pattern will improve with more data

## 💡 Tips & Tricks

1. **Start of Day**: Check AI assistant (Key 8) to see recommendations

2. **After Git Commits**: AI analyzes diff, refresh for updates

3. **Before Complex Work**: Check workflow prediction for guidance

4. **End of Day**: Record successful work to improve learning

5. **Team Sharing**: Export JSON and share successful patterns

6. **Quick Activation**: Just press `A` key when recommendations look good

---

## 🎓 Learning Curve

**Week 1**: Manual usage, record 5-10 sessions
**Week 2**: Start seeing good recommendations (60-70% confidence)
**Week 3**: High-confidence auto-activation for common patterns
**Week 4+**: AI handles 80%+ of agent management automatically

---

**The AI Intelligence System learns YOUR patterns and makes the framework work FOR you, not the other way around.**

Stay in Claude Code. Let AI handle the rest. 🚀
