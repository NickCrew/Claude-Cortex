# TUI Quick Start Guide - New Features

## Launch the TUI
```bash
cortex tui
```

## 🎯 What You Should See

### 1. Status Bar (Bottom of Screen)
**Location**: Very bottom, above the footer with key bindings

**What it shows**:
```
[View: Agents] Welcome to cortex TUI │ 25MB 0%
```

- **Left**: Current view and status message
- **Right**: Real-time memory usage and CPU percentage
- **Updates**: Every second automatically

**Colors**:
- 🟢 Green: Healthy (Memory <60%, CPU <50%)
- 🟡 Yellow: Moderate (Memory 60-80%, CPU 50-80%)
- 🔴 Red: High (Memory >80%, CPU >80%)

---

### 2. Command Palette (Press Ctrl+P)
**How to open**: Press `Ctrl+P` (or `^P` on Mac)

**What you'll see**: A centered modal dialog with:
```
🔍 Command Palette
┌─────────────────────────────────────┐
│ Type to search commands...          │
├─────────────────────────────────────┤
│ → Show Agents      View and manage  │
│   Show Skills      Browse available  │
│   Show Modes       View active modes │
│   Show Rules       View active rules │
│   ...                                │
└─────────────────────────────────────┘
↑/↓ Navigate  ✓ Select  Esc Close
```

**How to use**:
1. Press `Ctrl+P`
2. Type to filter (try typing "agent")
3. Use ↑/↓ arrow keys to select
4. Press Enter to execute
5. Press Esc to close

**Fuzzy Search**: It's smart!
- Type "agt" → matches "Show **Ag**en**t**s"
- Type "skill" → matches "Show **Skill**s", "Create **Skill**"
- Consecutive characters get priority

---

### 3. Enhanced Overview (Press 1)
**How to access**: Press `1` key

**What you'll see**: Dashboard cards showing:
```
System Overview

💻 Agents      13/78 active
⚑ Modes        3/9 active
📝 Rules       3/6 active
💻 Skills      54 installed
⏳ Workflows   0 running

Performance Metrics
⏳ 5m 23s │ 📊 45MB │ CPU 12% │ ├─ 8 threads
```

**Colors indicate status**:
- Green: Active/running
- Dim: Inactive/none

---

### 4. All Views Enhanced
Every view now has:
- **Icons**: 💻 📝 ⚑ ▶ for visual clarity
- **Status Indicators**: ✓ Active, ○ Ready, ⏳ Running, ✗ Failed
- **Progress Bars**: Visual progress in Workflows and Orchestrate views
- **Smart Truncation**: Long text is trimmed with `...`
- **Relative Time**: "5m ago" instead of timestamps

---

## 🎹 Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Ctrl+P` | **Command Palette** (NEW!) |
| `1-9` | Switch primary views |
| `0` | AI Assistant |
| `A` | Asset Manager |
| `C` | Worktrees |
| `F` | Flags |
| `M` | Memory Vault |
| `w` | Watch Mode |
| `S` | Scenarios |
| `o` | Orchestrate |
| `Alt+g` | Galaxy |
| `t` | Tasks |
| `/` | Slash Commands catalog |
| `R` | Refresh current view |
| `Space` | Toggle selected item |
| `?` | Show help |
| `Q` | Quit |

---

## 🧪 Testing the Features

### Test 1: Status Bar
1. Launch TUI: `cortex tui`
2. Look at **very bottom** of screen
3. Should see: `[View: ...] ... │ <memory> <cpu>`
4. Wait 1 second - numbers should update

**If you don't see it**:
- Make sure your terminal is tall enough
- The status bar is ABOVE the footer (the line with "1 Overview  2 Agents  ...")

---

### Test 2: Command Palette
1. Press `Ctrl+P` (hold Control and press P)
2. A dialog should pop up in the center
3. Type "agent"
4. Should see "Show Agents" highlighted
5. Press Enter - should go to Agents view
6. Try again with different searches

**If it doesn't open**:
- Make sure you're pressing Ctrl+P together
- Some terminals might need Ctrl+Shift+P

---

### Test 3: Dashboard
1. Press `1` key
2. Should see "System Overview" header
3. Should see colored cards with stats
4. Should see "Performance Metrics" section at bottom

---

### Test 4: Performance Updates
1. Watch the status bar for 5 seconds
2. The memory and CPU values should change
3. They update automatically every second

---

## 🐛 Troubleshooting

### Status bar is empty or shows no metrics
**Cause**: psutil not installed
**Fix**: Already fixed! Just restart the TUI

### Command palette doesn't open with Ctrl+P
**Possible causes**:
1. Terminal is intercepting Ctrl+P
2. Try in a different terminal
3. Check if textual keybindings are working (try other keys like 1-9, A, C, R, Q)

### Dashboard looks plain (no colors/icons)
**Cause**: Terminal doesn't support Unicode or colors
**Fix**: Use a modern terminal (iTerm2, Terminal.app, Windows Terminal, etc.)

### "Module not found" errors
**Fix**: Reinstall the package:
```bash
uv pip install -e . --force-reinstall
```

---

## 📊 What's New Summary

| Feature | What it does |
|---------|-------------|
| **Command Palette** | Universal search for all commands (Ctrl+P) |
| **Performance Monitor** | Real-time memory/CPU in status bar |
| **Dashboard Cards** | Visual stats with icons in Overview |
| **Enhanced Icons** | Professional Unicode icons everywhere |
| **Progress Bars** | Visual progress in Workflows/Orchestrate |
| **Smart Formatting** | Better time display, text truncation |

---

## 🎨 Visual Examples

### Before
```
Status: Active
Workflow: workflow-1 | running | 75 | 1699123456
```

### After
```
✓ Active
▶ workflow-1 │ ⏳ Running │ ███████░░░ 75% │ 5m ago
```

---

## 🚀 Pro Tips

1. **Quick Navigation**: Press `Ctrl+P`, type first few letters, Enter
   - Faster than pressing number keys!

2. **Watch Performance**: Keep an eye on status bar while working
   - Catch performance issues early

3. **Dashboard Overview**: Press `1` to see everything at a glance
   - Quick health check of your setup

4. **Fuzzy Search**: Don't type full words
   - "agt" finds "Show Agents"
   - "wf" finds "Show Workflows"

---

## ✅ Success Checklist

After launching `cortex tui`, verify:
- [ ] Status bar shows memory and CPU at bottom
- [ ] Ctrl+P opens command palette in center
- [ ] Typing in command palette filters results
- [ ] Pressing 1 shows dashboard with cards
- [ ] All views have colorful icons
- [ ] Performance metrics update every second

If all checked, you're ready to go! 🎉
