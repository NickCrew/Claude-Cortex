# Debugging & Tracing Flags

Flags for debugging, verbose output, and execution tracing.

**Estimated tokens: ~110**

---

**--trace**
- Trigger: Complex bugs, performance issues, mysterious failures
- Behavior: Detailed execution trace with instrumentation
- Related: Logs reasoning, decisions, tool calls, timing information
- Includes: Call stack, variable states, decision points
- Format: Timestamped trace with indentation showing depth
- Overhead: Increased token usage for detailed logging

**--verbose**
- Trigger: Debugging, learning, transparency needs
- Behavior: Maximum output detail and visibility
- Auto-enables: Extended logs, intermediate results, thought process
- Shows: All steps, all decisions, all data transformations
- Opposite of: --quiet
- Use when: Troubleshooting or understanding behavior

**--quiet**
- Trigger: CI/CD, automation, minimal noise
- Behavior: Minimal output (errors and final results only)
- Suppresses: Progress indicators, intermediate steps, verbose logs
- Shows: Only critical information and outcomes
- Opposite of: --verbose
- Use when: Scripting, automation, clean output needed
