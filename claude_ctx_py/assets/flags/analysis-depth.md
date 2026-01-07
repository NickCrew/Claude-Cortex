# Analysis Depth Flags

Control the depth and thoroughness of analysis and reasoning.

**Estimated tokens: ~130**

---

**--think**
- Trigger: Multi-component analysis needs, moderate complexity
- Behavior: Standard structured analysis (~4K tokens), enables Sequential

**--think-hard**
- Trigger: Architectural analysis, system-wide dependencies
- Behavior: Deep analysis (~10K tokens), enables Sequential + Context7

**--ultrathink**
- Trigger: Critical system redesign, legacy modernization, complex debugging
- Behavior: Maximum depth analysis (~32K tokens), enables all MCP servers
- Options:
  - `--summary brief`: Key findings only (~25% output reduction)
  - `--summary detailed`: Full analysis with reasoning (default)
  - `--summary comprehensive`: Include rationale, alternatives, trade-offs (~50% output increase)
- Auto-enables: `--introspect` transparency markers (🤔 thinking, 🎯 focus, ⚡ insight, 📊 data, 💡 decision)
