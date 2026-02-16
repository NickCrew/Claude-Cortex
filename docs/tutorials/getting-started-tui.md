---
layout: default
title: Getting Started with TUI
parent: Tutorials
nav_order: 1
permalink: /tutorials/getting-started-tui/
---

# Getting Started with Cortex

Welcome! This tutorial will help you master the **cortex TUI** (Terminal User Interface) — an interactive dashboard for managing Claude agents, skills, MCP servers, and more.

## 📋 What You'll Learn

By the end of this tutorial, you'll be able to:

- Launch and navigate the TUI
- Activate/deactivate agents
- Browse and validate skills
- Manage MCP servers
- Export context bundles
- Use CLI commands for advanced operations

**⏱️ Time Estimate:** 20-30 minutes  
**💻 Prerequisites:** Python 3.8+, basic terminal familiarity

## 🎯 What You'll Build

You'll set up a working Cortex environment and learn to:

1. Navigate between views using keyboard shortcuts
2. Activate an agent configuration that matches your project type
3. Configure MCP servers for extended capabilities
4. Export a context bundle for Claude

---

## Part 1: Installation & First Launch

### Step 1: Install cortex

Choose your installation method:

**Installation:**

```bash
cd /path/to/claude-cortex
pip install -e ".[dev]"
cortex install link
cortex install post
```

This installs:

- ✅ The `cortex` CLI tool
- ✅ Links content to ~/.claude/
- ✅ Shell completions (bash/zsh/fish)
- ✅ Man pages for documentation

**Verify Installation:**

```bash
cortex --help
```

You should see a list of available commands.

### Step 2: Launch the TUI

```bash
cortex tui
```

**What You Should See:**

```
┌─────────────────────────────────────────────────────────────┐
│ cortex TUI                                    [View: Overview] │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ System Overview                                             │
│ ───────────────────────────────────────────────              │
│ 💻 Agents      5/12 active                                  │
│ 📝 Rules       7/15 active                                  │
│ 💻 Skills      24 installed                                 │
│ 🔌 MCP         3 servers configured                         │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ [View: Agents] Welcome to cortex TUI │ 25MB 0%        │
├─────────────────────────────────────────────────────────────┤
│ 1 Overview  2 Agents  3 Rules  4 Skills  5 Tasks  6 Commands │
│ 7 MCP  C Worktrees  E Export  0 AI  ? Help  Q Quit         │
└─────────────────────────────────────────────────────────────┘
```

**✅ Checkpoint:** You should see:

- System overview cards in the center
- Status bar showing memory/CPU at bottom (above footer)
- Footer with keyboard shortcuts at very bottom

**📝 Rules Note:** Rules are file-based. Active rules live in `rules/`; toggling
them in the TUI moves files to `inactive/rules/` and regenerates `CLAUDE.md`.

**🚨 Troubleshooting:**

| Problem | Solution |
|---------|----------|
| "Command not found" | Ensure installation succeeded; try `python -m claude_ctx_py.cli tui` |
| Blank screen | Press `1` to refresh Overview view |
| No colors | Use a modern terminal (iTerm2, Terminal.app, Windows Terminal) |

---

## Part 2: Understanding the Layout

The TUI has three main sections:

### 1. Header

- Shows current view name
- Updates as you navigate

### 2. Body

- Main content area
- Changes based on current view
- Supports scrolling and selection

### 3. Footer

- **Status Bar** (just above footer): Shows `[View: Name] Message │ Memory% CPU%`
- **Keyboard Reference**: Quick access shortcuts

### Navigation Keys

| Key | Action | Example |
|-----|--------|---------|
| `1-9, 0` | Switch views | Press `2` for Agents |
| `↑/↓` or `j/k` | Navigate list | Select items |
| `Space` | Toggle/activate | Activate agent |
| `Enter` | View details | See agent info |
| `/` | Filter | Search by name |
| `Ctrl+P` | Command palette | Universal search |
| `r` | Refresh | Reload data |
| `?` | Help | Show all shortcuts |
| `q` | Quit | Exit TUI |

**✅ Practice Exercise:**

1. Press `2` → You should see the Agents view
2. Press `3` → You should see the Rules view
3. Press `4` → You should see the Skills view
4. Press `1` → Return to Overview
5. Press `?` → Help overlay appears
6. Press `?` or `Esc` → Help closes

---

## Part 3: Working with Agents

Agents are specialized AI behaviors (like "security-auditor" or "test-engineer") that enhance Claude's capabilities.

### Step 1: Browse Available Agents

```bash
# Press 2 to open Agents view
```

**What You'll See:**

```
╭─────────────────────────────────────────────────╮
│ Name               Status    Category  Desc     │
├─────────────────────────────────────────────────┤
│ security-auditor   ○ Ready   Security  Scans... │
│ test-engineer      ✓ Active  Testing   Writes...|
│ api-documenter     ○ Ready   Docs      Creates..|
│ performance-opt    ○ Ready   Speed     Analyzes.|
╰─────────────────────────────────────────────────╯
```

**Status Icons:**

- `○` Ready — Available but not active
- `✓` Active — Currently enabled
- `⏳` Running — Executing task

### Step 2: Activate an Agent

**Goal:** Activate the "test-engineer" agent

1. **Navigate to agent:**
   - Press `↑` or `↓` until "test-engineer" is highlighted
   - The row will show in reverse colors

2. **Activate:**
   - Press `Space`
   - Status changes from `○ Ready` → `✓ Active`

3. **View details:**
   - Press `Enter` with agent selected
   - Details panel appears on the right

**What Details Show:**

- Dependencies (what other agents it needs)
- Description and purpose
- Activation date
- Metadata

1. **Close details:**
   - Press `Esc` or `Enter` again

**✅ Checkpoint:**

- Status bar shows "Agent activated: test-engineer"
- Agent row shows `✓ Active` status

### Step 3: Filter Agents

**Goal:** Find all security-related agents

1. Press `/` (forward slash)
2. Type: `security`
3. Press `Enter`

Only agents matching "security" are displayed.

**Clear filter:** Press `Esc`

### 🔧 CLI Alternative (CLI-only)

While the TUI is best for exploration, some operations are faster via CLI:

```bash
# List all agents (CLI-only: shows raw list)
cortex agent list

# Activate multiple agents at once (CLI-only: batch operation)
cortex agent activate security-auditor test-engineer api-documenter

# View dependencies (CLI-only: detailed tree)
cortex agent deps security-auditor

# Generate dependency graph (CLI-only: export to file)
cortex agent graph --export agent-deps.md
```

**When to use CLI:**

- Batch operations (activating 5+ agents)
- Scripting and automation
- Exporting dependency graphs
- Integration with other tools

---

## Part 4: Working with Skills

Skills are reusable knowledge modules (like "owasp-top-10" or "git-workflow") that agents can leverage.

### Step 1: Browse Skills

```bash
# Press 5 to open Skills view
```

**What You'll See:**

```
╭─────────────────────────────────────────────────────╮
│ Name              Rating   Activations  Tokens     │
├─────────────────────────────────────────────────────┤
│ owasp-top-10      ⭐⭐⭐⭐⭐    127       -15.2K    │
│ git-workflow      ⭐⭐⭐⭐      89        -8.1K     │
│ api-design        ⭐⭐⭐       45        -12.4K    │
╰─────────────────────────────────────────────────────╯
```

**Columns Explained:**

- **Rating:** Community star rating (1-5 stars)
- **Activations:** Times this skill was used
- **Tokens:** Token savings (negative = efficiency gain)

### Step 2: View Skill Details

1. Select a skill (e.g., "owasp-top-10")
2. Press `Enter` to see details

**Details Include:**

- Full description
- Which agents use it
- Version information
- Validation status

### Step 3: Validate a Skill

**Why Validate?** Ensures skill metadata is correct and dependencies are met.

1. Select "owasp-top-10"
2. Press `v` (validate shortcut)

**Result Dialog:**

```
┌───────────────────────────────────────┐
│ Skill Validation · owasp-top-10       │
├───────────────────────────────────────┤
│ ✓ Metadata valid                      │
│ ✓ Schema conforms                     │
│ ✓ All dependencies available          │
│                                       │
│ Status: PASSED                        │
└───────────────────────────────────────┘
```

### Step 4: View Skill Metrics

1. Select a skill
2. Press `m` (metrics shortcut)

**Metrics Include:**

- Usage count over time
- Token efficiency
- Success rate
- Associated agents

### Step 5: Rate a Skill

**Goal:** Provide feedback on skill quality

1. Select a skill
2. Press `Ctrl+R`
3. Rating dialog appears:

```
┌─────────────────────────────────┐
│ Rate Skill: owasp-top-10        │
├─────────────────────────────────┤
│ Stars: ⭐⭐⭐⭐⭐               │
│                                 │
│ Review (optional):              │
│ [ Still the best security... ] │
│                                 │
│ [Submit]  [Cancel]              │
└─────────────────────────────────┘
```

### 🔧 CLI Alternatives (Advanced Features)

Some skill operations are CLI-only:

```bash
# Show detailed skill info (CLI-only: structured output)
cortex skills info owasp-top-10

# Show which agents use a skill (CLI-only: dependency mapping)
cortex skills agents owasp-top-10

# Show skill dependency tree (CLI-only: hierarchical view)
cortex skills compose owasp-top-10

# Analytics dashboard (CLI-only: comprehensive report)
cortex skills analytics --metric trending

# Generate full report (CLI-only: export to CSV/JSON)
cortex skills report --format csv > skills-report.csv
```

**Community Features (CLI-only):**

```bash
# Search community skill registry
cortex skills community search "kubernetes"

# Install community skill
cortex skills community install awesome-k8s

# Rate community skill
cortex skills community rate awesome-k8s --stars 5
```

---

## Part 5: Managing MCP Servers

MCP (Model Context Protocol) servers provide additional tools and context to Claude.

### Step 1: View MCP Servers

```bash
# Press 7 to open MCP view
```

**What You'll See:**

```
╭──────────────────────────────────────────────────╮
│ Name          Status    Tools  Description      │
├──────────────────────────────────────────────────┤
│ codanna       ✓ Active  12     Code intelligence │
│ context7      ✓ Active  3      Documentation     │
│ sequential    ○ Ready   5      Thinking tools    │
╰──────────────────────────────────────────────────╯
```

### Step 2: Test an MCP Server

**Goal:** Verify an MCP server is working

1. Navigate to a server (e.g., "codanna")
2. Press `t` (test)
3. Wait for connection test

**Test Results:**

```
┌─────────────────────────────────────┐
│ MCP Test: codanna                   │
├─────────────────────────────────────┤
│ ✓ Connection successful             │
│ ✓ 12 tools available                │
│ ✓ Response time: 45ms               │
│                                     │
│ Available tools:                    │
│ - semantic_search_docs              │
│ - find_symbol                       │
│ - find_callers                      │
│ ...                                 │
└─────────────────────────────────────┘
```

### Step 3: View Server Details

Press `Enter` on any server to see:

- Full tool list
- Server configuration
- Connection status
- Documentation links

### 🔧 CLI Alternatives

```bash
# List MCP servers
cortex mcp list

# Test specific server
cortex mcp test codanna

# Diagnose all servers
cortex mcp diagnose

# View server documentation
cortex mcp docs codanna
```

---

## Part 6: Command Palette Power-User Feature

The Command Palette is your shortcut to everything.

### Step 1: Open Command Palette

Press `Ctrl+P`

**What Appears:**

```
┌───────────────────────────────────────┐
│ 🔍 Command Palette                    │
├───────────────────────────────────────┤
│ Type to search commands...            │
├───────────────────────────────────────┤
│ → Show Agents      View and manage    │
│   Show Skills      Browse available   │
│   Show Rules       View active rules  │
│   Show MCP         MCP servers        │
│   Export Context   Create bundle      │
│   ...                                 │
└───────────────────────────────────────┘
```

### Step 2: Use Fuzzy Search

**Try these searches:**

| Type | Matches | Result |
|------|---------|--------|
| `agent` | "Show **Agent**s" | Opens Agents view |
| `val` | "**Val**idate Skill" | Validates current skill |
| `mcp` | "Show **MCP**" | MCP servers view |
| `exp` | "**Exp**ort Context" | Export dialog |

**The Magic:** You don't need to type full words!

- Type first letters
- Consecutive characters prioritized
- Smart matching

### Step 3: Execute Commands

1. Type search term
2. Use `↑/↓` to select command
3. Press `Enter` to execute
4. Press `Esc` to close

**💡 Pro Tip:** `Ctrl+P` is faster than remembering number keys for views!

---

## Part 7: Exporting Context

Export creates a Markdown bundle of your active agents and rules for Claude.

### Step 1: Open Export View

```bash
# Press E to open Export view
```

**What You'll See:**

```
╭──────────────────────────────────────╮
│ Category         Include   Count     │
├──────────────────────────────────────┤
│ [✓] Agents       Yes       5 active  │
│ [✓] Rules        Yes       7 active  │
│ [✓] Skills       Yes       24 total  │
│ [ ] Assets       No        12 total  │
╰──────────────────────────────────────╯

Format: Agent Generic (press 'f' to change)
```

### Step 2: Choose What to Export

1. Navigate to category (e.g., "Skills")
2. Press `Space` to toggle inclusion
   - `[✓]` = Include
   - `[ ]` = Exclude

### Step 3: Select Format

Press `f` to cycle through formats:

- **Agent Generic** — Works with any AI assistant
- **Claude Format** — Optimized for Claude Code

### Step 4: Export to File

Press `e` to export:

**Export Dialog:**

```
┌─────────────────────────────────────────┐
│ Export Context                          │
├─────────────────────────────────────────┤
│ Write export to path:                   │
│ [ ~/claude-context-export.md ]          │
│                                         │
│ [OK]  [Cancel]                          │
└─────────────────────────────────────────┘
```

1. Edit path if desired
2. Press `Enter`
3. Success notification appears

**Result:** File created at specified path!

### Step 5: Copy to Clipboard

**Quick Copy:**
Press `x` → Export copied to clipboard directly

**Use Case:** Paste into Claude chat without saving file

### 🔧 CLI Alternatives

```bash
# List exportable components (CLI-only)
cortex export list

# Export to file (CLI-only: advanced filtering)
cortex export context ~/my-export.md \
  --exclude skills \
  --exclude-file some-agent.md

# Include only specific categories
cortex export context ~/my-export.md \
  --include rules \
  --include core

# Export to stdout (CLI-only: pipe to other tools)
cortex export context - | less

# Different format (CLI-only)
cortex export context ~/export.md --no-agent-generic
```

---

## Part 8: AI Assistant & Recommendations

The AI Assistant analyzes your project and recommends optimal agent configurations.

### Step 1: Open AI Assistant

```bash
# Press 0 (zero) to open AI Assistant view
```

**What You'll See:**

```
╭─────────────────────────────────────────────────╮
│ 🤖 AI Recommendations                           │
├─────────────────────────────────────────────────┤
│ Context: Backend, Auth, Testing                 │
│                                                 │
│ Review Requests:                                │
│ 🔴 security-auditor        [AUTO]   95%         │
│     Reason: Auth code detected                  │
│ 🔵 quality-engineer        [AUTO]   85%         │
│     Reason: Changes detected                    │
│ 🔵 code-reviewer           [AUTO]   75%         │
│     Reason: Changes detected                    │
│                                                 │
│ Other Suggestions:                              │
│ 🟢 api-documenter          [MANUAL] 60%         │
│     Reason: API endpoints found                 │
╰─────────────────────────────────────────────────╯
```

**Confidence Colors:**

- 🔴 Red (≥80%) — Auto-activate recommended
- 🟡 Yellow (60-80%) — Review suggested
- 🟢 Green (<60%) — Optional

### Step 2: Auto-Activate High-Confidence Agents

Press `A` → All agents ≥80% confidence activate automatically

### Step 3: Manually Activate Suggestions

1. Navigate to an agent recommendation
2. Press `Space` to activate

### 🔧 CLI Features (Advanced Intelligence)

The AI system has powerful CLI-only features:

```bash
# Get recommendations (CLI-only: structured output)
cortex ai recommend

# Auto-activate high-confidence agents (CLI-only: scripting)
cortex ai auto-activate

# Watch mode - real-time monitoring (CLI-only)
cortex ai watch

# Record successful session for learning (CLI-only)
cortex ai record-success --outcome "feature complete"

# Export recommendations to JSON (CLI-only)
cortex ai export --output recommendations.json
```

**Watch Mode Example (CLI-only):**

```bash
cortex ai watch
```

**Output:**

```
══════════════════════════════════════════════════════
🤖 AI WATCH MODE - Real-time Intelligence
══════════════════════════════════════════════════════

[10:33:12] 🔍 Context detected: Backend, Auth
  3 files changed

  💡 Recommendations:
     🔴 security-auditor [AUTO]
        95% - Auth code detected

[10:33:12] ⚡ Auto-activating 1 agents...
     ✓ security-auditor
```

Watch mode monitors file changes and recommends agents in real-time!

---

## Part 9: Advanced TUI Features

### MCP Server Management

**MCP (Model Context Protocol)** servers provide external tool integrations.

```bash
# Press 7 to open MCP view
```

**Available Actions:**

- `v` — Validate server configuration
- `d` — View server documentation
- `t` — Test server connection
- `c` — Copy config snippet
- `D` — Diagnose all servers

**Example:**

```
╭────────────────────────────────────────────╮
│ Name        Status    Type       Tools     │
├────────────────────────────────────────────┤
│ context7    ✓ Active  Library    5 tools   │
│ codanna     ✓ Active  Code       12 tools  │
│ serena      ○ Ready   Task       3 tools   │
╰────────────────────────────────────────────╯
```

---

## Part 10: Troubleshooting & Tips

### Common Issues

#### TUI Not Responding

**Symptom:** Keys don't work  
**Fix:**

1. Press `Esc` to clear any active mode
2. Press `?` to verify responsiveness
3. Press `q` to quit and restart

#### Filters Not Clearing

**Symptom:** View shows limited items  
**Fix:**

1. Press `Esc` to clear filter
2. Press `r` to refresh view
3. Look for "Filter: ..." in status bar

#### Details Panel Stuck Open

**Symptom:** Can't close details panel  
**Fix:**

1. Press `Esc`
2. If stuck, press `Enter` to toggle
3. Switch views (`1-9`) and return

#### Status Bar Missing Metrics

**Symptom:** No memory/CPU shown  
**Fix:** Install psutil:

```bash
pip install psutil
```

### Performance Tips

**Speed Up Navigation:**

- Use `Ctrl+P` instead of number keys
- Type abbreviations (e.g., "agt" finds "Agents")
- Keep filters active while working

**Reduce File I/O:**

- Use `r` to manually refresh instead of switching views
- Filter large lists before scrolling

**Terminal Configuration:**

- Use hardware acceleration
- Enable truecolor support
- 120x30 minimum terminal size recommended

### Keyboard Shortcuts Reference Card

**Print this for quick reference:**

```
┌────────────────────────────────────────┐
│ VIEWS          │ ACTIONS               │
├────────────────┼───────────────────────┤
│ 1 Overview     │ Space  Toggle         │
│ 2 Agents       │ Enter  Details        │
│ 3 Rules        │ /      Filter         │
│ 4 Skills       │ Esc    Clear/Cancel   │
│ 5 Tasks        │ r      Refresh        │
│ 6 Commands     │ ?      Help           │
│ 7 MCP          │ q      Quit           │
│ C Worktrees    │ Ctrl+P Palette        │
│ 9 Export       │ ↑↓ jk  Navigate       │
│ 0 AI           │                       │
└────────────────┴───────────────────────┘
```

---

## Part 11: Next Steps

### 🎓 Continue Learning

**Beginner Level:** ✅ You are here!

- Explore each view (1-7, C, E, 0, w, A, M, X)
- Practice activating agents
- Test MCP server connections

**Intermediate Level:**

- Set up AI watch mode for your projects
- Configure custom MCP servers
- Export and use context bundles with Claude

**Advanced Level:**

- Create custom skills
- Write custom agents
- Integrate with CI/CD pipelines

### 📚 Documentation Resources

**TUI Specific:**

- `docs/guides/tui/tui-keyboard-reference.md` — Complete shortcut list
- `docs/guides/tui-quick-start.md` — New features guide
- `docs/guides/tui.md` — Architecture and implementation
- `man cortex-tui` — Man page (if installed)

**CLI Reference:**

- `man cortex` — Complete command reference
- `cortex --help` — Built-in help
- `cortex <command> --help` — Command-specific help

**Advanced Topics:**

- `docs/guides/features/SUPER_SAIYAN_INTEGRATION.md` — Visual enhancements
- `docs/guides/development/AI_INTELLIGENCE_GUIDE.md` — AI assistant deep-dive
- `docs/guides/development/WATCH_MODE_GUIDE.md` — Watch mode details
- `docs/guides/mcp/MCP_MANAGEMENT.md` — MCP server management

### 🛠️ Extend Your Setup

**Shell Integration (CLI-only):**

```bash
# Install shell aliases
cortex install aliases

# View available aliases
cortex install aliases --show
```

**Completions:**

```bash
# Generate completions
cortex completion bash > ~/.bash_completion.d/cortex
cortex completion zsh > ~/.zsh/completions/_cortex
cortex completion fish > ~/.config/fish/completions/cortex.fish
```

**Man Pages:**

```bash
# View documentation
man cortex        # Main reference
man cortex-tui    # TUI guide
man cortex-workflow  # Workflow orchestration
```

### 💡 Pro Workflow

**Daily Development Workflow:**

1. **Morning Setup:**

   ```bash
   cortex tui
   ```

   - Press `8` → Apply project profile
   - Press `0` → Check AI recommendations

2. **During Development:**

   ```bash
   # Terminal 1: AI Watch Mode (CLI-only)
   cortex ai watch
   
   # Terminal 2: TUI for quick adjustments
   cortex tui
   ```

3. **Before Commits:**

   ```bash
   cortex tui
   ```

   - Press `6` → Run "pre-commit" workflow
   - Press `9` → Export context for review

4. **Context for Claude:**

   ```bash
   # Quick clipboard export (TUI)
   cortex tui
   # Press 9, then x (clipboard)
   
   # Or CLI for automation
   cortex export context - | pbcopy  # macOS
   cortex export context - | xclip   # Linux
   ```

---

## 🎉 Congratulations

You've completed the getting started tutorial! You now know how to:

- ✅ Navigate the TUI efficiently
- ✅ Manage agents, modes, and skills
- ✅ Run workflows and monitor progress
- ✅ Use the command palette
- ✅ Export context bundles
- ✅ Leverage AI recommendations
- ✅ Switch between TUI and CLI for optimal workflow

### Quick Reference Summary

**Most Used Actions:**

| Task | TUI | CLI |
|------|-----|-----|
| Launch interface | `cortex tui` | N/A |
| Activate agent | Press `2`, `Space` | `cortex agent activate <name>` |
| Test MCP server | Press `7`, `t` | `cortex mcp test <name>` |
| Export context | Press `E`, `e` | `cortex export context <path>` |
| AI recommendations | Press `0` | `cortex ai recommend` |
| Watch mode | Press `w` | `cortex ai watch` |
| Batch operations | N/A (CLI better) | `cortex agent activate a b c` |

### When to Use TUI vs CLI

**Use TUI when:**

- 👀 Exploring and discovering features
- 🎯 Quick interactive changes
- 📊 Monitoring status and progress
- 🧪 Learning and experimentation

**Use CLI when:**

- 🤖 Scripting and automation
- ⚡ Batch operations (multiple agents)
- 📈 Detailed reports and exports
- 🔗 Integration with other tools
- 📦 CI/CD pipelines

### Keep Practicing

**Challenge Yourself:**

1. **Beginner Challenge:**
   - Activate 3 agents that match your current project
   - Create a custom profile with your preferred configuration
   - Export context and paste into Claude

2. **Intermediate Challenge:**
   - Set up AI watch mode for a project
   - Run a workflow and monitor its execution
   - Validate all your active skills

3. **Advanced Challenge:**
   - Create a custom workflow (YAML)
   - Integrate cortex into your CI pipeline
   - Build a shell script that auto-configures based on project type

---

## 📖 Appendix: Quick Command Reference

### TUI Navigation

```bash
# Launch
cortex tui

# Views: 1=Overview, 2=Agents, 3=Rules, 4=Skills, 5=Tasks
#        6=Commands, 7=MCP, C=Worktrees, E=Export, 0=AI
#        w=Watch, A=Assets, M=Memory, X=Codex

# Actions: Space=Toggle, Enter=Details, /=Filter, r=Refresh
#          Ctrl+P=Palette, ?=Help, q=Quit
```

### Essential CLI Commands

```bash
# Status
cortex status                    # System overview

# Agents
cortex agent list                # List available
cortex agent status              # Show active
cortex agent activate <name>     # Enable agent
cortex agent graph --export map.md  # Dependency graph

# Skills
cortex skills list               # List all skills
cortex skills info <skill>       # Show details
cortex skills validate --all     # Validate all

# AI Assistant
cortex ai recommend              # Get recommendations
cortex ai watch                  # Real-time monitoring
cortex ai auto-activate          # Auto-enable agents

# Export
cortex export context <file>     # Create bundle
cortex export context - | pbcopy # To clipboard (macOS)

# MCP
cortex mcp list                  # List servers
cortex mcp diagnose              # Check all servers
```

---

**🚀 Ready to become a cortex power user? Start with the TUI, explore the views, and gradually incorporate CLI commands for advanced workflows. Happy coding!**

---

*Last Updated: 2025-11-15*  
*Tutorial Version: 1.0*  
*Target: cortex v1.0+*
