---
layout: default
title: Getting Started with TUI
parent: Tutorials
nav_order: 1
permalink: /tutorials/getting-started-tui/
---

# Getting Started with Cortex

Welcome! This tutorial will help you master the **claude-ctx TUI** (Terminal User Interface) — an interactive dashboard for managing Claude agents, skills, workflows, and more.

## 📋 What You'll Learn

By the end of this tutorial, you'll be able to:

- Launch and navigate the TUI
- Activate/deactivate agents and modes
- Browse and validate skills
- Run workflows and orchestrate scenarios
- Export context bundles
- Use CLI commands for advanced operations

**⏱️ Time Estimate:** 20-30 minutes  
**💻 Prerequisites:** Python 3.8+, basic terminal familiarity

## 🎯 What You'll Build

You'll set up a working Cortex environment and learn to:

1. Navigate between views using keyboard shortcuts
2. Activate an agent configuration that matches your project type
3. Run your first workflow
4. Export a context bundle for Claude

---

## Part 1: Installation & First Launch

### Step 1: Install claude-ctx

Choose your installation method:

**Quick Install (Recommended):**

```bash
cd /path/to/claude-ctx-plugin
./scripts/deprecated/install.sh
```

This installs:

- ✅ The `claude-ctx` CLI tool
- ✅ Shell completions (bash/zsh/fish)
- ✅ Man pages for documentation

**Manual Installation:**

```bash
cd /path/to/claude-ctx-plugin
python3 -m pip install -e .
```

**Verify Installation:**

```bash
claude-ctx --help
```

You should see a list of available commands.

### Step 2: Launch the TUI

```bash
claude-ctx tui
```

**What You Should See:**

```
┌─────────────────────────────────────────────────────────────┐
│ claude-ctx TUI                                    [View: Overview] │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ System Overview                                             │
│ ───────────────────────────────────────────────              │
│ 💻 Agents      5/12 active                                  │
│ ⚑ Modes        3/8 active                                   │
│ 📝 Rules       7/15 active                                  │
│ 💻 Skills      24 installed                                 │
│ ⏳ Workflows   2 available                                  │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ [View: Agents] Welcome to claude-ctx TUI │ 25MB 0%        │
├─────────────────────────────────────────────────────────────┤
│ 1 Overview  2 Agents  3 Modes  4 Rules  5 Skills  6 Workflows │
│ 7 MCP  8 Profiles  9 Export  0 AI  ? Help  Q Quit          │
└─────────────────────────────────────────────────────────────┘
```

**✅ Checkpoint:** You should see:

- System overview cards in the center
- Status bar showing memory/CPU at bottom (above footer)
- Footer with keyboard shortcuts at very bottom

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
2. Press `3` → You should see the Modes view
3. Press `1` → Return to Overview
4. Press `?` → Help overlay appears
5. Press `?` or `Esc` → Help closes

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
claude-ctx agent list

# Activate multiple agents at once (CLI-only: batch operation)
claude-ctx agent activate security-auditor test-engineer api-documenter

# View dependencies (CLI-only: detailed tree)
claude-ctx agent deps security-auditor

# Generate dependency graph (CLI-only: export to file)
claude-ctx agent graph --export agent-deps.md
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
claude-ctx skills info owasp-top-10

# Show which agents use a skill (CLI-only: dependency mapping)
claude-ctx skills agents owasp-top-10

# Show skill dependency tree (CLI-only: hierarchical view)
claude-ctx skills compose owasp-top-10

# Analytics dashboard (CLI-only: comprehensive report)
claude-ctx skills analytics --metric trending

# Generate full report (CLI-only: export to CSV/JSON)
claude-ctx skills report --format csv > skills-report.csv
```

**Community Features (CLI-only):**

```bash
# Search community skill registry
claude-ctx skills community search "kubernetes"

# Install community skill
claude-ctx skills community install awesome-k8s

# Rate community skill
claude-ctx skills community rate awesome-k8s --stars 5
```

---

## Part 5: Running Workflows

Workflows are multi-step automation sequences (like "test-and-deploy" or "code-review").

### Step 1: View Available Workflows

```bash
# Press 6 to open Workflows view
```

**What You'll See:**

```
╭──────────────────────────────────────────────────╮
│ Name              Status    Progress  Started   │
├──────────────────────────────────────────────────┤
│ test-and-deploy   ⏳ Running  █████░░░ 65%  5m ago│
│ code-review       ○ Ready    ░░░░░░░░  0%  -     │
│ security-audit    ✓ Complete ████████ 100% 2h ago│
╰──────────────────────────────────────────────────╯
```

### Step 2: Run a Workflow

**Goal:** Run the "code-review" workflow

1. Navigate to "code-review"
2. Press `Shift+R` (capital R = run)

**What Happens:**

- Workflow starts immediately
- Status changes to `⏳ Running`
- Progress bar shows completion percentage

### Step 3: Monitor Progress

With workflow selected:

- Progress bar updates in real-time
- Press `Enter` to see step details

**Step Details:**

```
┌─────────────────────────────────────┐
│ Workflow: code-review               │
├─────────────────────────────────────┤
│ Steps:                              │
│ ✓ Load files                        │
│ ✓ Run linter                        │
│ → Check style        (current)      │
│ ○ Generate report    (pending)      │
│                                     │
│ Elapsed: 2m 15s                     │
└─────────────────────────────────────┘
```

**Symbols:**

- `✓` Step complete
- `→` Current step
- `○` Pending step
- `✗` Failed step

### Step 4: Stop a Workflow

If you need to cancel:

1. Select the running workflow
2. Press `s` (stop)
3. Confirm in dialog

### 🔧 CLI Alternatives

```bash
# List workflows (CLI-only: shows all metadata)
claude-ctx workflow list

# Run workflow from command line (CLI-only: scripting)
claude-ctx workflow run code-review

# Check workflow status (CLI-only: JSON output)
claude-ctx workflow status

# Resume paused workflow (CLI-only: state management)
claude-ctx workflow resume

# Stop specific workflow (CLI-only: by name)
claude-ctx workflow stop code-review
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
│   Show Modes       View active modes  │
│   Show Rules       View active rules  │
│   Run Workflow     Execute workflow   │
│   ...                                 │
└───────────────────────────────────────┘
```

### Step 2: Use Fuzzy Search

**Try these searches:**

| Type | Matches | Result |
|------|---------|--------|
| `agent` | "Show **Agent**s" | Opens Agents view |
| `val` | "**Val**idate Skill" | Validates current skill |
| `wf` | "Run **W**orkflow" | Workflow picker |
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

Export creates a Markdown bundle of your active agents, modes, and rules for Claude.

### Step 1: Open Export View

```bash
# Press 9 to open Export view
```

**What You'll See:**

```
╭──────────────────────────────────────╮
│ Category         Include   Count     │
├──────────────────────────────────────┤
│ [✓] Agents       Yes       5 active  │
│ [✓] Modes        Yes       3 active  │
│ [✓] Rules        Yes       7 active  │
│ [✓] Skills       Yes       24 total  │
│ [ ] Workflows    No        2 total   │
╰──────────────────────────────────────╯

Format: Agent Generic (press 'f' to change)
```

### Step 2: Choose What to Export

1. Navigate to category (e.g., "Workflows")
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
claude-ctx export list

# Export to file (CLI-only: advanced filtering)
claude-ctx export context ~/my-export.md \
  --exclude workflows \
  --exclude-file some-agent.md

# Include only specific categories
claude-ctx export context ~/my-export.md \
  --include rules \
  --include core

# Export to stdout (CLI-only: pipe to other tools)
claude-ctx export context - | less

# Different format (CLI-only)
claude-ctx export context ~/export.md --no-agent-generic
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
claude-ctx ai recommend

# Auto-activate high-confidence agents (CLI-only: scripting)
claude-ctx ai auto-activate

# Watch mode - real-time monitoring (CLI-only)
claude-ctx ai watch

# Record successful session for learning (CLI-only)
claude-ctx ai record-success --outcome "feature complete"

# Export recommendations to JSON (CLI-only)
claude-ctx ai export --output recommendations.json
```

**Watch Mode Example (CLI-only):**

```bash
claude-ctx ai watch
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
- `Ctrl+D` — Diagnose all servers

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

### Profiles — Quick Configurations

**Profiles** are pre-configured agent sets for common scenarios.

```bash
# Press 8 to open Profiles view
```

**Built-in Profiles:**

- `frontend` — React, Vue, Angular development
- `backend` — API, database, server-side
- `devops` — Infrastructure, CI/CD
- `data-ai` — ML, data science
- `full` — Everything enabled

**Apply Profile:**

1. Select profile (e.g., "frontend")
2. Press `Space`
3. All associated agents/modes activate

**Save Custom Profile:**

1. Activate your desired agents/modes
2. Press `n` (new)
3. Enter profile name
4. Press `Enter`

Your custom profile is saved for reuse!

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
│ 3 Modes        │ /      Filter         │
│ 4 Rules        │ Esc    Clear/Cancel   │
│ 5 Skills       │ r      Refresh        │
│ 6 Workflows    │ ?      Help           │
│ 7 MCP          │ q      Quit           │
│ 8 Profiles     │ Ctrl+P Palette        │
│ 9 Export       │ ↑↓ jk  Navigate       │
│ 0 AI           │                       │
└────────────────┴───────────────────────┘
```

---

## Part 11: Next Steps

### 🎓 Continue Learning

**Beginner Level:** ✅ You are here!

- Explore each view (`1-9, 0`)
- Practice activating agents
- Run a simple workflow

**Intermediate Level:**

- Create custom profiles for your projects
- Set up AI watch mode for your workflow
- Export and use context bundles with Claude

**Advanced Level:**

- Write custom workflows (YAML)
- Create custom skills
- Integrate with CI/CD pipelines

### 📚 Documentation Resources

**TUI Specific:**

- `docs/guides/tui/tui-keyboard-reference.md` — Complete shortcut list
- `docs/guides/tui-quick-start.md` — New features guide
- `docs/guides/tui.md` — Architecture and implementation
- `man claude-ctx-tui` — Man page (if installed)

**CLI Reference:**

- `man claude-ctx` — Complete command reference
- `claude-ctx --help` — Built-in help
- `claude-ctx <command> --help` — Command-specific help

**Advanced Topics:**

- `docs/guides/features/SUPER_SAIYAN_INTEGRATION.md` — Visual enhancements
- `docs/guides/development/AI_INTELLIGENCE_GUIDE.md` — AI assistant deep-dive
- `docs/guides/development/WATCH_MODE_GUIDE.md` — Watch mode details
- `docs/guides/mcp/MCP_MANAGEMENT.md` — MCP server management

### 🛠️ Extend Your Setup

**Shell Integration (CLI-only):**

```bash
# Install shell aliases
claude-ctx install aliases

# View available aliases
claude-ctx install aliases --show
```

**Completions:**

```bash
# Generate completions
claude-ctx completion bash > ~/.bash_completion.d/claude-ctx
claude-ctx completion zsh > ~/.zsh/completions/_claude-ctx
claude-ctx completion fish > ~/.config/fish/completions/claude-ctx.fish
```

**Man Pages:**

```bash
# View documentation
man claude-ctx        # Main reference
man claude-ctx-tui    # TUI guide
man claude-ctx-workflow  # Workflow orchestration
```

### 💡 Pro Workflow

**Daily Development Workflow:**

1. **Morning Setup:**

   ```bash
   claude-ctx tui
   ```

   - Press `8` → Apply project profile
   - Press `0` → Check AI recommendations

2. **During Development:**

   ```bash
   # Terminal 1: AI Watch Mode (CLI-only)
   claude-ctx ai watch
   
   # Terminal 2: TUI for quick adjustments
   claude-ctx tui
   ```

3. **Before Commits:**

   ```bash
   claude-ctx tui
   ```

   - Press `6` → Run "pre-commit" workflow
   - Press `9` → Export context for review

4. **Context for Claude:**

   ```bash
   # Quick clipboard export (TUI)
   claude-ctx tui
   # Press 9, then x (clipboard)
   
   # Or CLI for automation
   claude-ctx export context - | pbcopy  # macOS
   claude-ctx export context - | xclip   # Linux
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
| Launch interface | `claude-ctx tui` | N/A |
| Activate agent | Press `2`, `Space` | `claude-ctx agent activate <name>` |
| Run workflow | Press `6`, `Shift+R` | `claude-ctx workflow run <name>` |
| Export context | Press `9`, `e` | `claude-ctx export context <path>` |
| AI recommendations | Press `0` | `claude-ctx ai recommend` |
| Watch mode | N/A (CLI-only) | `claude-ctx ai watch` |
| Batch operations | N/A (CLI better) | `claude-ctx agent activate a b c` |

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
   - Integrate claude-ctx into your CI pipeline
   - Build a shell script that auto-configures based on project type

---

## 📖 Appendix: Quick Command Reference

### TUI Navigation

```bash
# Launch
claude-ctx tui

# Views: 1=Overview, 2=Agents, 3=Modes, 4=Rules, 5=Skills
#        6=Workflows, 7=MCP, 8=Profiles, 9=Export, 0=AI

# Actions: Space=Toggle, Enter=Details, /=Filter, r=Refresh
#          Ctrl+P=Palette, ?=Help, q=Quit
```

### Essential CLI Commands

```bash
# Status
claude-ctx status                    # System overview

# Agents
claude-ctx agent list                # List available
claude-ctx agent status              # Show active
claude-ctx agent activate <name>     # Enable agent
claude-ctx agent graph --export map.md  # Dependency graph

# Skills
claude-ctx skills list               # List all skills
claude-ctx skills info <skill>       # Show details
claude-ctx skills validate --all     # Validate all

# Workflows
claude-ctx workflow list             # Available workflows
claude-ctx workflow run <name>       # Execute workflow
claude-ctx workflow status           # Check progress

# AI Assistant
claude-ctx ai recommend              # Get recommendations
claude-ctx ai watch                  # Real-time monitoring
claude-ctx ai auto-activate          # Auto-enable agents

# Export
claude-ctx export context <file>     # Create bundle
claude-ctx export context - | pbcopy # To clipboard (macOS)

# MCP
claude-ctx mcp list                  # List servers
claude-ctx mcp diagnose              # Check all servers
```

---

**🚀 Ready to become a claude-ctx power user? Start with the TUI, explore the views, and gradually incorporate CLI commands for advanced workflows. Happy coding!**

---

*Last Updated: 2025-11-15*  
*Tutorial Version: 1.0*  
*Target: claude-ctx v1.0+*
