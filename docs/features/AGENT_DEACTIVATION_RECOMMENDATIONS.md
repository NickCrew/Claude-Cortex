# Agent Deactivation Recommendations

**Feature**: Intelligent AI-powered recommendations to deactivate active agents that are not relevant to the current context.

**Created**: 2025-12-12
**Status**: ✅ Implemented and Tested

---

## Overview

The intelligent mode now suggests which active agents should be **deactivated** based on:
- Current project context (frontend, backend, database, etc.)
- Historical usage patterns in similar sessions
- Resource impact (high-resource agents get higher priority)
- Relevance to current work

This complements the existing agent **activation** recommendations to provide a complete agent lifecycle management system.

---

## Implementation

### 1. New Dataclass: `AgentDeactivationRecommendation`

**Location**: `claude_ctx_py/intelligence/base.py:88-102`

```python
@dataclass
class AgentDeactivationRecommendation:
    """Represents a recommendation to deactivate an active agent."""

    agent_name: str
    confidence: float  # 0.0 to 1.0
    reason: str
    urgency: str  # low, medium, high
    auto_deactivate: bool
    inactive_duration: int  # seconds since last relevant activity
    resource_impact: str  # low, medium, high

    def should_notify(self) -> bool:
        """Determine if this should notify the user."""
        return self.confidence >= 0.6 or self.urgency in ("medium", "high")
```

**Fields**:
- `agent_name`: Name of the agent to deactivate
- `confidence`: How confident we are that it should be deactivated (0-1)
- `reason`: Human-readable explanation
- `urgency`: Priority level (low/medium/high)
- `auto_deactivate`: Whether to auto-deactivate (only for high-confidence + high-resource agents)
- `inactive_duration`: Time since last relevant activity (for future enhancement)
- `resource_impact`: How much resources the agent consumes (low/medium/high)

---

### 2. New Method: `PatternLearner.predict_deactivations()`

**Location**: `claude_ctx_py/intelligence/base.py:450-549`

**Purpose**: Analyzes active agents and recommends which ones should be deactivated based on historical patterns.

**Logic**:
1. Get agents that SHOULD be active for current context (from activation predictions)
2. For each active agent:
   - Skip if it should definitely be active
   - Calculate historical usage score in similar contexts
   - If usage score < 30%, recommend deactivation
3. Assign urgency and auto-deactivate based on:
   - Resource impact (high-resource agents get higher urgency)
   - Usage score (very low usage gets higher urgency)
4. Sort recommendations by confidence

**Example**:
```python
# Frontend context with database-engineer active
deactivation_recs = learner.predict_deactivations(context, active_agents)
# Returns: [
#   AgentDeactivationRecommendation(
#     agent_name="database-engineer",
#     confidence=1.0,  # Never used in frontend sessions
#     reason="Low relevance to frontend context (used in 0% of similar sessions)",
#     urgency="medium",
#     auto_deactivate=False,
#     resource_impact="low"
#   )
# ]
```

---

### 3. New Method: `IntelligentAgent.get_deactivation_recommendations()`

**Location**: `claude_ctx_py/intelligence/base.py:769-789`

**Purpose**: Public API for getting deactivation recommendations from the intelligent agent.

**Usage**:
```python
agent = IntelligentAgent(data_dir)
deactivation_recs = agent.get_deactivation_recommendations(active_agents)
```

---

### 4. TUI Integration: `show_ai_assistant_view()` Update

**Location**: `claude_ctx_py/tui/main.py:3573-3650`

**Changes**:
- Added new "⚠ Deactivation Suggestions" section
- Displays top 5 deactivation recommendations
- Color-coded by urgency:
  - 🔸 Orange (high urgency)
  - 🔹 Yellow (medium urgency)
  - ⚪ Low (dim)
- Shows confidence percentage
- Displays resource impact (⚡HIGH, ⚡MED)
- Shows AUTO indicator for auto-deactivate recommendations

**Visual Format**:
```
⚠ Deactivation Suggestions
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔸 Agent  performance-engineer AUTO ⚡HIGH  100%  Low relevance to frontend context (used in 0% of similar sessions)
🔹 Agent  database-engineer                 100%  Low relevance to frontend context (used in 0% of similar sessions)
```

---

## How It Works

### Decision Logic

The system recommends deactivation when:

1. **Low Historical Usage**: Agent used in <30% of similar past sessions
2. **Not Contextually Relevant**: Agent not recommended for current context
3. **Resource Impact**: High-resource agents get priority for deactivation

### Confidence Calculation

```
confidence = 1.0 - usage_score
```

- If agent never used in similar contexts → 100% confidence to deactivate
- If agent used 10% of the time → 90% confidence to deactivate
- If agent used 30% of the time → 70% confidence to deactivate (threshold)

### Auto-Deactivate Criteria

Auto-deactivate is enabled when:
```
confidence > 0.8 AND resource_impact == "high"
```

This means:
- Only very confident recommendations (>80%)
- Only for high-resource agents (performance-engineer, security-auditor, code-reviewer)

---

## Usage in TUI

### Viewing Deactivation Suggestions

1. Open the TUI: `cortex tui`
2. Navigate to "AI Assistant" view (press `a` or use navigation)
3. Scroll to "⚠ Deactivation Suggestions" section

### Interpreting Recommendations

**Confidence Levels**:
- 🟠 80-100%: Strong recommendation (highly confident)
- 🟡 60-80%: Moderate recommendation
- ⚪ <60%: Weak recommendation

**Urgency Levels**:
- 🔸 High: Should deactivate soon (high resource impact)
- 🔹 Medium: Consider deactivating
- ⚪ Low: Optional deactivation

**Resource Impact**:
- ⚡HIGH: Agent consumes significant resources (CPU/memory)
- ⚡MED: Moderate resource usage
- (none): Low resource impact

---

## Example Scenarios

### Scenario 1: Frontend Work with Backend Agents Active

**Context**: Working on React components
**Active Agents**: `react-specialist`, `database-engineer`, `performance-engineer`

**Recommendations**:
```
🔸 performance-engineer AUTO ⚡HIGH  100%  Low relevance to frontend context
🔹 database-engineer                 100%  Low relevance to frontend context
```

**Action**: Auto-deactivate `performance-engineer`, consider deactivating `database-engineer`

---

### Scenario 2: All Agents Relevant

**Context**: Full-stack API development
**Active Agents**: `backend-engineer`, `api-documenter`, `test-automator`

**Recommendations**:
```
No deactivation needed
All active agents are relevant to current context
```

**Action**: No changes needed

---

### Scenario 3: No Active Agents

**Context**: Any
**Active Agents**: (none)

**Recommendations**:
```
No active agents
Activate agents to see deactivation suggestions
```

---

## Benefits

### Resource Optimization
- Automatically identifies unused agents consuming resources
- Prioritizes high-resource agents for deactivation
- Reduces memory and CPU usage

### Context Awareness
- Learns from historical patterns
- Adapts to your workflow
- Only suggests relevant deactivations

### User Guidance
- Clear explanations for each recommendation
- Confidence scores for decision-making
- Auto-deactivate for obvious cases

---

## Testing

**Test Coverage**:
- ✅ Dataclass imports successfully
- ✅ Method logic correctly identifies irrelevant agents
- ✅ Confidence calculation works as expected
- ✅ Auto-deactivate logic applies correctly
- ✅ Resource impact assignments are accurate
- ✅ TUI display integration works without errors

**Test Results**:
```
🧪 Testing Agent Deactivation Recommendations

📊 Context: frontend (React components)
🔧 Active agents: ['react-specialist', 'performance-engineer', 'database-engineer']

⚠️  Deactivation Recommendations (2 found):

1. Agent: performance-engineer
   Confidence: 100%
   Urgency: medium
   Resource Impact: high
   Auto-deactivate: True
   ✅ PASS

2. Agent: database-engineer
   Confidence: 100%
   Urgency: medium
   Resource Impact: low
   Auto-deactivate: False
   ✅ PASS

✅ react-specialist correctly NOT recommended (relevant to frontend)
✅ Test completed successfully!
```

---

## Future Enhancements

### Planned Improvements:

1. **Activity Tracking**: Track actual usage time and surface inactive agents
2. **Cost Analysis**: Show estimated cost savings from deactivation
3. **One-Click Deactivate**: Add button to deactivate directly from TUI
4. **Bulk Deactivate**: Deactivate multiple agents at once
5. **Smart Re-activation**: Automatically re-activate when context changes
6. **Usage Analytics**: Show agent usage statistics over time

---

## Related Files

- **Intelligence Base**: `claude_ctx_py/intelligence/base.py`
  - AgentDeactivationRecommendation dataclass
  - PatternLearner.predict_deactivations()
  - IntelligentAgent.get_deactivation_recommendations()

- **TUI Integration**: `claude_ctx_py/tui/main.py`
  - show_ai_assistant_view() updates

- **Documentation**: `docs/features/AGENT_DEACTIVATION_RECOMMENDATIONS.md`

---

## Summary

The agent deactivation recommendation system provides:
- ✅ Intelligent analysis of active agents
- ✅ Historical pattern-based recommendations
- ✅ Resource-aware prioritization
- ✅ Clear visual presentation in TUI
- ✅ Auto-deactivate for high-confidence cases
- ✅ Complete agent lifecycle management

**Status**: Fully implemented, tested, and integrated into TUI.

---

**Last Updated**: 2025-12-12
**Version**: 1.0.0
**Author**: Implemented via Claude Code
