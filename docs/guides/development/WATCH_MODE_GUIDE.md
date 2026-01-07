# 🔍 Watch Mode - Real-Time AI Intelligence

## Overview

**Watch Mode** is the "stay in flow" feature—it monitors your work in real-time and automatically manages the framework for you. No daemons, no system services, just an opt-in foreground process that watches while you code.

## 🚀 Quick Start

```bash
# Terminal 1: Start watch mode
cortex ai watch

# Terminal 2: Code normally
# Watch mode will monitor and notify you
```

That's it! Watch mode will:
- ✅ Monitor git changes (commits, staged, unstaged)
- ✅ Analyze context in real-time
- ✅ Recommend agents automatically
- ✅ Auto-activate high-confidence agents
- ✅ Show notifications for important changes

**Stop anytime**: Press `Ctrl+C`

## 📺 What You'll See

### Startup
```
══════════════════════════════════════════════════════════════════════
🤖 AI WATCH MODE - Real-time Intelligence
══════════════════════════════════════════════════════════════════════

[10:30:15] Watch mode started
  Auto-activate: ON
  Threshold: 70% confidence
  Check interval: 2.0s

  Monitoring:
    • Git changes (commits, staged, unstaged)
    • File modifications
    • Context changes

  Press Ctrl+C to stop

──────────────────────────────────────────────────────────────────────

[10:30:15] 🚀 Performing initial analysis...

[10:30:16] 🔍 Context detected: Backend, API
  8 files changed

  💡 Recommendations:

     🔵 quality-engineer [AUTO]
        85% - Changes detected - quality review recommended

     🔵 code-reviewer [AUTO]
        75% - Changes detected - code review recommended

     🟡 api-documenter [AUTO]
        90% - API changes detected

[10:30:16] ⚡ Auto-activating 3 agents...
     ✓ quality-engineer
     ✓ code-reviewer
     ✓ api-documenter
```

### During Coding
```
[10:32:45] 📝 Git commit detected
  HEAD: a3f2b5c1

[10:33:12] 🔍 Context detected: Backend, Auth
  3 files changed

  💡 Recommendations:

     🔴 security-auditor [AUTO]
        95% - Auth code detected - security review recommended

[10:33:12] ⚡ Auto-activating 1 agents...
     ✓ security-auditor
```

### On Exit
```
──────────────────────────────────────────────────────────────────────
📊 WATCH MODE STATISTICS
──────────────────────────────────────────────────────────────────────
  Duration: 0h 45m
  Checks performed: 135
  Recommendations: 8
  Auto-activations: 3
  Agents activated: api-documenter, code-reviewer, security-auditor
──────────────────────────────────────────────────────────────────────
```

## ⚙️ Options

### Basic Usage
```bash
# Default: auto-activate ON, 70% threshold, 2s interval
cortex ai watch
```

### Disable Auto-Activation
```bash
# Just show recommendations, don't activate
cortex ai watch --no-auto-activate
```

### Adjust Threshold
```bash
# Only show 80%+ confidence recommendations
cortex ai watch --threshold 0.8

# Show all recommendations (50%+)
cortex ai watch --threshold 0.5
```

### Change Check Interval
```bash
# Check every 5 seconds (less CPU)
cortex ai watch --interval 5.0

# Check every second (more responsive)
cortex ai watch --interval 1.0
```

### Combined Options
```bash
# Conservative: manual activation, high threshold, slow checks
cortex ai watch --no-auto-activate --threshold 0.9 --interval 5.0

# Aggressive: auto-activate, low threshold, fast checks
cortex ai watch --threshold 0.6 --interval 1.0
```

## 🎯 What It Monitors

### Git Changes
- **Commits**: Detects new commits (git HEAD changes)
- **Staged files**: Files added to git index
- **Unstaged files**: Modified but not staged
- **New files**: Untracked files in git

### Context Detection
Automatically detects when you're working on:
- **Auth code** (auth.py, authentication.ts, etc.)
- **API code** (routes, endpoints, controllers)
- **Frontend code** (.tsx, .jsx, .vue, .svelte)
- **Backend code** (.py, .go, .java, .rs)
- **Database code** (migrations, schema, models)
- **Tests** (test files, spec files)

### Triggers Recommendations When:
- ✅ Context changes (new file types detected)
- ✅ File count increases significantly
- ✅ High-risk code modified (auth, security)
- ✅ Test failures detected (if integrated with test runner)
- ✅ Build errors detected (if integrated with build system)

## 🤖 Auto-Activation Rules

Agents are **automatically activated** when:

### Critical (95% confidence)
- Auth/security code changed → `security-auditor`
- Test failures detected → `test-automator`

### High (75-90% confidence)
- Any changeset → `quality-engineer`
- Any changeset → `code-reviewer`
- TypeScript/TSX → `typescript-pro`
- React/JSX/TSX → `react-specialist`
- User-facing UI → `ui-ux-designer`
- Database/SQL → `database-optimizer`, `sql-pro`
- Cross-cutting changes → `architect-review`
- Database/API/perf-sensitive changes → `performance-engineer`
- API changes + learned pattern → `api-documenter`

### Medium (70-80% confidence)
- Pattern-based from history

### Won't Auto-Activate (<70% confidence)
- Low-confidence pattern matches → manual review
- Exploratory changes → various (manual)

## 💡 Workflows

### Workflow 1: Security-Sensitive Work

```bash
# Terminal 1: Start watch mode
cortex ai watch

# Terminal 2: Edit auth code
vim src/auth/security.py

# Watch mode detects:
[10:45:23] 🔍 Context detected: Backend, Auth
  1 file changed

  💡 Recommendations:
     🔴 security-auditor [AUTO]
        95% - Auth code detected

[10:45:23] ⚡ Auto-activating 1 agents...
     ✓ security-auditor

# You continue coding, security-auditor is already active!
```

### Workflow 2: Large Refactoring

```bash
# Start watch mode with lower threshold
cortex ai watch --threshold 0.6

# Refactor 15 files

# Watch mode detects:
[11:15:45] 🔍 Context detected: Backend
  15 files changed

  💡 Recommendations:
     🔵 quality-engineer [AUTO]
        85% - Changes detected - quality review recommended
     🔵 code-reviewer [AUTO]
        75% - Changes detected - code review recommended
     🔵 test-automator
        75% - Large changeset - test updates needed

[11:15:45] ⚡ Auto-activating 2 agents...
     ✓ code-reviewer
     ✓ test-automator

# Quality gates automatically activated!
```

### Workflow 3: API Development

```bash
# Start watch with manual control
cortex ai watch --no-auto-activate

# Add new API endpoint

# Watch mode shows recommendations:
[12:30:12] 🔍 Context detected: Backend, API
  3 files changed

  💡 Recommendations:
     🟡 backend-architect
        80% - API changes detected
     🟡 api-documenter
        85% - API documentation needed

# Review recommendations, then manually:
# cortex agent activate api-documenter
```

## 🎓 Learning Integration

Watch mode works WITH the learning system:

### Recording Sessions
```bash
# Terminal 1: Watch mode running
cortex ai watch

# Terminal 2: After successful work
cortex ai record-success --outcome "API feature complete"

# Watch mode learns:
# - You used backend-architect + api-documenter
# - For API development context
# - Pattern strengthened for future API work
```

### Pattern Recognition
After 3-5 successful sessions:
```bash
# Future API work triggers:
[14:20:10] 🎯 Workflow prediction detected
  Pattern: auto_backend_api
  Confidence: 87%
  Agents: backend-architect, api-documenter, test-automator

# Watch mode follows learned pattern!
```

## 🔧 Integration with Other Tools

### With TUI
```bash
# Terminal 1: Watch mode
cortex ai watch

# Terminal 2: TUI for manual control
cortex tui

# Both work together:
# - Watch mode monitors and auto-activates
# - TUI shows current state and recommendations
# - Press '0' in TUI to see AI assistant view
```

### With Git Hooks (Future)
```bash
# Install git hooks
cortex ai install-hooks

# Watch mode + pre-commit hook:
# - Watch mode monitors during development
# - Pre-commit hook enforces quality gates
# - Both use same AI intelligence
```

## 📊 Statistics Tracking

Watch mode tracks:
- **Duration**: How long it's been running
- **Checks performed**: Number of analysis cycles
- **Recommendations made**: Times it suggested agents
- **Auto-activations**: Agents it activated automatically
- **Agents activated**: Which agents were activated

View anytime: Press `Ctrl+C` to stop and see stats

## ⚡ Performance

### Resource Usage
- **CPU**: ~0.5-1% (polling every 2s)
- **Memory**: ~50-80MB (Python process)
- **Disk**: Git commands + file reads (minimal)

### Optimization Tips
```bash
# Reduce CPU usage
cortex ai watch --interval 5.0  # Check every 5s

# Reduce responsiveness for battery savings
cortex ai watch --interval 10.0  # Check every 10s
```

## 🐛 Troubleshooting

### No Notifications

**Problem**: Watch mode running but no notifications

**Causes**:
1. No files changed since last check
2. Threshold too high
3. Git not initialized

**Solutions**:
```bash
# Lower threshold
cortex ai watch --threshold 0.5

# Check git status
git status

# Check interval
cortex ai watch --interval 1.0
```

### Too Many Notifications

**Problem**: Getting flooded with notifications

**Solutions**:
```bash
# Raise threshold
cortex ai watch --threshold 0.9

# Slower checking
cortex ai watch --interval 5.0

# Disable auto-activation
cortex ai watch --no-auto-activate
```

### Auto-Activation Not Working

**Problem**: No agents being auto-activated

**Causes**:
1. Confidence < 80% (auto-activation threshold)
2. Auto-activate disabled

**Solutions**:
```bash
# Check if enabled
cortex ai watch  # Should show "Auto-activate: ON"

# Lower confidence threshold won't help
# (auto-activation is hardcoded at 80%+)

# Review recommendations manually:
cortex ai recommend
```

## 💡 Tips & Tricks

### 1. **Start Watch Mode at Beginning of Day**
```bash
# Open terminal, start watch mode
cortex ai watch

# Keep it running all day
# Monitors all your work sessions
```

### 2. **Use with tmux/screen**
```bash
# Create persistent session
tmux new -s claude-watch

# Start watch mode
cortex ai watch

# Detach: Ctrl+b, d
# Reattach anytime: tmux attach -t claude-watch
```

### 3. **Project-Specific Settings**
```bash
# Security-sensitive project
alias watch-secure='cortex ai watch --threshold 0.95'

# Exploratory project
alias watch-explore='cortex ai watch --no-auto-activate --threshold 0.5'
```

### 4. **Combine with Workflow**
```bash
# Start watch mode when entering project
cd ~/project && cortex ai watch &

# Or add to .zshrc/.bashrc:
cd() {
  builtin cd "$@"
  if [ -d ".git" ]; then
    # Start watch mode in background
    (cortex ai watch > /tmp/claude-watch.log 2>&1 &)
  fi
}
```

### 5. **Log Output**
```bash
# Save watch mode output
cortex ai watch 2>&1 | tee claude-watch.log

# Review later
less claude-watch.log
```

## 🔮 Future Enhancements

Planned features:
- [ ] File system watcher (faster, less CPU)
- [ ] Test runner integration (auto-detect failures)
- [ ] Build system integration (auto-detect errors)
- [ ] IDE integration (VS Code, JetBrains)
- [ ] Notification center integration (macOS, Linux)
- [ ] Slack/Teams notifications
- [ ] Multiple project monitoring
- [ ] Web dashboard (view from browser)

## 📚 Related Commands

```bash
# Get AI recommendations (one-time)
cortex ai recommend

# Auto-activate agents (one-time)
cortex ai auto-activate

# View in TUI
cortex tui
# Press '0' for AI assistant view

# Record successful session
cortex ai record-success
```

## 🎯 When to Use Watch Mode

### ✅ Great For:
- Long coding sessions (1+ hours)
- Security-sensitive work (auto-activates security-auditor)
- Learning phase (builds AI patterns)
- Team environments (consistent practices)
- Complex projects (many agents)

### ❌ Not Needed For:
- Quick edits (< 5 minutes)
- Single-file changes (no context shift)
- Non-git projects (can't detect changes)
- Battery-critical situations (uses CPU)

## 🚀 Summary

**Watch Mode = "Set it and forget it" AI intelligence**

```bash
# Start once
cortex ai watch

# Code normally
# AI monitors and manages framework
# Stay in Claude Code flow
# Press Ctrl+C when done
```

**Philosophy**: Let AI handle the framework, you focus on coding.

---

**Pro Tip**: Start watch mode at the beginning of your work session and let it run. Check the TUI (key 8) periodically to see what the AI has done for you!
