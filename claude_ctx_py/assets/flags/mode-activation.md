# Mode Activation Flags

Behavioral flags to activate specific execution modes and mindsets.

**Estimated tokens: ~120**

---

**--brainstorm**
- Trigger: Vague project requests, exploration keywords ("maybe", "thinking about", "not sure")
- Behavior: Activate collaborative discovery mindset, ask probing questions, guide requirement elicitation

**--introspect**
- Trigger: Self-analysis requests, error recovery, complex problem solving requiring meta-cognition
- Behavior: Expose thinking process with transparency markers
- Auto-enabled by: `--ultrathink` (maximum depth analysis)
- Levels:
  - `--introspect-level markers`: Emoji indicators only (🤔 thinking, 🎯 focus, ⚡ insight, 📊 data, 💡 decision) - default
  - `--introspect-level steps`: Numbered reasoning steps with rationale
  - `--introspect-level full`: Complete thought process including alternatives considered
- Use cases:
  - `markers`: Quick visibility into reasoning phases without verbosity
  - `steps`: Learning from reasoning process, debugging complex decisions
  - `full`: Maximum transparency for critical decisions, educational purposes

**--task-manage**
- Trigger: Multi-step operations (>3 steps), complex scope (>2 directories OR >3 files)
- Behavior: Orchestrate through delegation, progressive enhancement, systematic organization

**--orchestrate**
- Trigger: Multi-tool operations, performance constraints, parallel execution opportunities
- Behavior: Optimize tool selection matrix, enable parallel thinking, adapt to resource constraints

**--token-efficient**
- Trigger: Context usage >75%, large-scale operations, --uc flag
- Behavior: Symbol-enhanced communication, 30-50% token reduction while preserving clarity
