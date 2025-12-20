# Interactive Control Flags

Flags for controlling user interaction and approval workflows.

**Estimated tokens: ~130**

---

**--confirm-changes**
- Trigger: Production changes, critical files, risky operations
- Behavior: Confirm each file change before applying
- Related: Interactive approval, preview diffs, selective application
- Shows: Full diff for each change with explanation
- Allows: Accept, reject, or modify individual changes
- Safety: Prevents unwanted modifications

**--auto-approve [low|medium]**
- Trigger: Trusted operations, repetitive tasks
- Behavior: Auto-approve changes below risk threshold
- Example: `--auto-approve low` → auto-approve formatting, docs, tests
- Risk levels:
  - `low`: Formatting, comments, documentation, tests
  - `medium`: New features, refactoring (but not deletions)
- Never auto-approves: Deletions, security changes, production code
- Logs: All auto-approved changes for review

**--pair-programming**
- Trigger: Learning, collaboration, complex problems
- Behavior: Interactive collaborative mode with frequent check-ins
- Auto-enables: Explanation at each step, asks for input, shows alternatives
- Cadence: Check-in every 3-5 steps or major decision
- Includes: "What do you think?" prompts, encourages questions
- Best for: Learning sessions, tackling unfamiliar territory
