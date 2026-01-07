# Cost Management & Budget Flags

Flags for controlling API costs and optimizing token usage.

**Estimated tokens: ~120**

---

**--cost-limit [5|10|25|50]**
- Trigger: Budget constraints, experimental projects
- Behavior: Hard dollar limit per session (stops at threshold)
- Example: `--cost-limit 10` stops execution at $10
- Related: Tracks cumulative cost, warns at 80%
- Prevents: Runaway costs from complex operations
- Displays: Real-time cost counter in status

**--cost-aware**
- Trigger: Budget-conscious development, client projects
- Behavior: Show cost estimates before expensive operations
- Related: Displays token usage, estimated cost, prompts for confirmation
- Shows: Cost per operation, cumulative session cost
- Warns: Before operations exceeding 10% of remaining budget
- Format: "$X.XX (Y tokens)" for transparency

**--frugal**
- Trigger: Tight budgets, high-frequency operations
- Behavior: Optimize for minimum cost without sacrificing quality
- Auto-enables: Smaller thinking budgets, caching, minimal context
- Prefers: Simpler solutions, less verbose output
- Avoids: Deep analysis unless necessary
- Targets: 30-50% cost reduction vs default behavior
