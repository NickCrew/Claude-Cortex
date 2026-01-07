---
layout: default
title: Modes
nav_order: 6
---

# Modes

Modes are opinionated behavioral presets that shape how Cortex works: planning depth, tone, trade-off bias, and emphasis on speed vs quality. They are designed to be lightweight, composable, and easy to toggle per task.

## How Modes Activate

You can enable modes in three ways:

1. **CLI**

   ```bash
   cortex mode list
   cortex mode status
   cortex mode activate Architect
   cortex mode deactivate Architect
   ```

2. **TUI**

   ```bash
   cortex tui
   # Press 3 for Modes, Space to toggle
   ```

3. **Flags**

   Add mode flags to `FLAGS.md` (for example `--brainstorm` or `--token-efficient`) to auto-activate modes on load.

Active state is stored in `.active-modes`, which makes mode activation consistent across CLI, TUI, and export. Use `cortex setup migrate` to move legacy `CLAUDE.md` references into `.active-modes`.

## Mode Catalog

| Mode | Purpose | Best For |
| --- | --- | --- |
| **Amphetamine** | Maximum-velocity MVP prototyping | Hackathons, spikes, proof-of-concepts |
| **Architect** | Strategic system design and trade-offs | Architecture planning, large refactors |
| **Brainstorming** | Collaborative discovery and exploration | Vague requirements, early ideation |
| **Idea_Lab** | Timeboxed option generation | Rapid alternatives and experiments |
| **Introspection** | Meta-cognitive reflection | Root cause analysis, process review |
| **Security_Audit** | Security-first review mindset | Threat modeling, hardening passes |
| **Super_Saiyan** | Visual excellence & UX polish | UI work across web/TUI/docs |
| **Teacher** | Educational explanations | Onboarding, mentoring, walkthroughs |
| **Token_Efficiency** | Concise, token-aware responses | Long sessions, cost control |

### Super Saiyan Variants

`Super_Saiyan` includes platform-specific extensions in `modes/supersaiyan/` for CLI, TUI, docs, and detection heuristics. Start with the core mode, then apply the variant that matches your target surface.

## Mode Metadata, Conflicts & Dependencies

Modes can include YAML frontmatter metadata to declare:

- **conflicts** (modes that should not run together)
- **dependencies** (required modes or rule modules)
- **group** (mutually exclusive groups)
- **priority** (auto-deactivation vs prompt)
- **auto_activate_triggers** (contexts that can switch modes automatically)

The CLI and TUI surface conflicts and dependency warnings when activating a mode so you can resolve overlaps intentionally.

## Tips

- Use **Architect** for multi-phase system work, **Amphetamine** for fast spikes.
- Combine **Teacher** with **Brainstorming** for guided discovery sessions.
- Turn on **Token_Efficiency** when context size is growing.

---

**Related guides**: [Asset Manager](asset-manager.html) • [Worktree Manager](worktrees.html) • [Flags Management](FLAGS_MANAGEMENT.html)
