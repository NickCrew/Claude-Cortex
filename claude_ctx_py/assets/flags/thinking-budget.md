# Thinking Budget Flags

Control internal reasoning token allocation and cost trade-offs.

**Estimated tokens: ~140**

---

**--thinking-budget [4000|10000|32000|128000]**
- Trigger: Need explicit control over internal reasoning token allocation
- Behavior: Set token budget for internal thinking and analysis
- Levels:
  - `4000`: Standard reasoning (~$0.012 per request) - routine tasks
  - `10000`: Deep reasoning (~$0.030 per request) - architectural decisions
  - `32000`: Maximum reasoning (~$0.096 per request) - critical redesign
  - `128000`: Extended thinking (~$0.384 per request) - extreme complexity
- Options:
  - `--auto-adjust`: Allow automatic budget escalation based on complexity
  - `--show-usage`: Display real-time token consumption and cost
- Related Commands: `/reasoning:budget`, `/reasoning:adjust`
- Note: 5x cheaper than OpenAI o1 at equivalent depth (128K)
