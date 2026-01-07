# Auto-Escalation Flags

Flags for automatic reasoning depth adjustment based on task signals.

**Estimated tokens: ~180**

---

**--auto-escalate [confidence|errors|complexity|adaptive]**
- Trigger: Need for automatic reasoning depth adjustment based on task signals
- Behavior: Monitor task execution and escalate reasoning depth when needed
- Modes:
  - `confidence`: Escalate when confidence scores < 0.6 after initial analysis
  - `errors`: Escalate after 3+ failed solution attempts
  - `complexity`: Escalate when detecting circular dependencies, >100 files, >10 services
  - `adaptive`: Combine all triggers with intelligent threshold adjustment
- Escalation Path: Current depth → +1 level (e.g., medium→high, not medium→ultra)
- De-escalation: Returns to base level after successful subtask completion
- Max Escalations: 2 per task (prevents runaway costs)
- Cost Protection: Requires confirmation for escalation to Extended (128K)
- Related Commands: `/reasoning:adjust`, `/reasoning:budget`
- Example: `--think --auto-escalate adaptive` starts at 4K, escalates to 10K if needed

**Escalation Triggers by Type:**

**confidence:**
- Confidence score <0.6 after analysis
- Multiple competing solutions with similar scores
- High uncertainty in recommendations
- Threshold: Activates after initial solution attempt

**errors:**
- 3+ failed compilation/test attempts
- Repeated similar error patterns
- Solutions that don't resolve root cause
- Threshold: Tracks per-subtask error count

**complexity:**
- Circular dependency detection (imports, services)
- File count >100 in affected scope
- Service boundary count >10
- Nested abstraction depth >7 levels
- Code complexity score >0.8
- Threshold: Structural analysis triggers

**adaptive:**
- Learns from metrics history (`/reasoning:metrics`)
- Adjusts thresholds based on command patterns
- Task-specific complexity scoring
- Balances cost vs quality dynamically
- Threshold: Context-dependent optimization
