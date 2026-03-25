---
layout: default
title: First 20 Minutes in the TUI
parent: Tutorials
nav_order: 3
---

# First 20 Minutes in the TUI

This tutorial is a guided first session in the Cortex terminal UI. The goal is
not to learn every screen. The goal is to get comfortable moving through the
core views, understand what the TUI is good at, and know when to switch back to
the CLI.

## What You'll Learn

- how to launch the TUI and orient yourself quickly
- how to move between the most important views
- how to inspect agents, skills, commands, and exports
- how the Command Palette fits into day-to-day use
- when the TUI is the best interface and when the CLI is faster

## Prerequisites

- Cortex installed locally
- a terminal session in a project where you want to use Cortex

## Time Estimate

~20 minutes

---

## Step 1: Launch the TUI

Start with the normal entrypoint:

```bash
cortex tui
```

If you want a guided first-run entry:

```bash
cortex tui --tour
```

The TUI can also start on a specific view:

```bash
cortex tui --view agents
```

For this walkthrough, start from the default screen so you can practice moving
between views.

## Step 2: Learn the Main Navigation Pattern

The fastest way to get comfortable is to learn the top-level view keys.

Most useful early on:

- `0` = AI Assistant
- `1` = Overview
- `2` = Agents
- `4` = Skills
- `6` = Commands
- `8` = Memory
- `9` = Watch Mode
- `E` = Export
- `W` = Worktrees
- `F` = Settings

There are more views, but these are enough for a strong first session.

### Checkpoint

- [ ] Opened the TUI
- [ ] Switched between at least three views
- [ ] Confirmed that the number and letter bindings feel predictable

## Step 3: Start with the AI Assistant and Overview

Press `0` for **AI Assistant**.

This is the best first stop when you want Cortex to analyze the current repo
and suggest where to pay attention. It is centered on agent-oriented guidance,
not on browsing the whole asset catalog.

Then press `1` for **Overview**.

Use the Overview screen to get your bearings before you start changing
anything. This is the "what state is Cortex in right now?" view.

Use these two views together when you want:

- a quick read on the current session
- a recommendation-oriented starting point
- a sanity check before activating assets or exporting context

## Step 4: Inspect Agents

Press `2` for **Agents**.

This is where the TUI becomes more useful than a plain command list. The Agents
view is good for:

- browsing what is available
- understanding dependencies
- seeing what Cortex considers activatable

For a first session, do not worry about mastering every action. Focus on these
questions:

- which agents exist for the type of work I am doing?
- does this task need an agent workflow at all?
- which agent relationships are visible here that would be annoying to inspect
  one command at a time?

## Step 5: Inspect Skills and Commands Together

Press `4` for **Skills**.

This is the right TUI surface for browsing skill entries and thinking about
what knowledge packs belong in the current task.

Then press `6` for **Commands**.

This matters because Cortex commands are generated from installed skills rather
than maintained as a separate slash-command catalog. A good first-session habit
is:

1. look at skills to understand the capability
2. look at commands to see how that capability is exposed

While you are in the Skills view:

- use `Ctrl+R` to open the skill rating dialog for the selected skill

### Checkpoint

- [ ] Opened the Skills view with `4`
- [ ] Opened the Commands view with `6`
- [ ] Confirmed that commands and skills are related, not separate systems

## Step 6: Try the Command Palette

Press `Ctrl+P` to open the **Command Palette**.

This is one of the fastest ways to use the TUI once you know roughly what you
want but do not remember where it lives.

Use it to search for actions such as:

- skill-oriented actions
- LLM provider configuration
- navigation or management actions by name

The Command Palette is especially helpful once the number of views and actions
starts to exceed what you want to keep in memory.

## Step 7: Practice Export from the TUI

Press `E` for the **Export** view.

This view is worth visiting in your first session because export is one of the
most practical cross-interface workflows in Cortex. It helps answer:

- what can I hand to another worker?
- how much context should I package?
- when should I export instead of trying to restate everything manually?

You can also trigger export directly with:

```text
Ctrl+E
```

If you like the export workflow but need more precise or scriptable control,
that is usually the point where the CLI becomes the better tool.

## Step 8: Know When to Stay in the TUI vs Switch to CLI

Use the **TUI** when you want:

- visual orientation across agents, skills, commands, and exports
- fast browsing without remembering every command
- interactive discovery
- cross-cutting visibility across several Cortex systems at once

Use the **CLI** when you want:

- repeatable commands you can paste into notes or scripts
- tighter task-specific workflows such as `cortex skills`, `cortex export`, or
  `cortex git`
- automation or stdout-friendly output

The best mental model is:

- TUI for understanding and navigating
- CLI for exact execution and repeatability

## Suggested First-Session Loop

A reliable first session looks like this:

```text
1. cortex tui
2. 0 for AI Assistant
3. 2 for Agents
4. 4 for Skills
5. 6 for Commands
6. Ctrl+P for Command Palette
7. E or Ctrl+E for Export
8. Switch to CLI if you need a precise repeatable command
```

That is enough to make the TUI feel like a useful control surface instead of a
wall of screens.

## Summary

After one guided session, the important habits are:

1. use numeric and letter bindings to move quickly
2. treat Agents, Skills, and Commands as complementary views
3. use the Command Palette when you know the goal but not the location
4. use Export as a bridge to downstream workers
5. switch back to CLI for exact repeatable workflows

## Related

- [Terminal UI]({% link guides/tui.md %}) -- reference guide to TUI views and shortcuts
- [Skills to Context Handoff]({% link tutorials/skill-recommendations.md %}) -- use the CLI alongside the TUI skill workflow
- [Export Context for Handoffs]({% link tutorials/export-context.md %}) -- continue from the Export view into a full handoff workflow
