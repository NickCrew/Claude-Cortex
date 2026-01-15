# Watch Mode: Real-Time Intelligence Architecture

**Version**: 1.0  
**Last Updated**: 2025-12-05  
**Status**: Current

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Core Components](#core-components)
4. [Polling Mechanism](#polling-mechanism)
5. [Git Integration](#git-integration)
6. [Notification System](#notification-system)
7. [Auto-Activation](#auto-activation)
8. [Resource Management](#resource-management)
9. [Statistics & Monitoring](#statistics--monitoring)
10. [CLI Usage](#cli-usage)
11. [Development Guide](#development-guide)

---

## Overview

### Purpose

**Watch Mode** provides real-time monitoring and intelligent recommendations by:
- ✅ Continuously monitoring git changes (commits, staged, unstaged)
- ✅ Detecting context changes from file modifications
- ✅ Making intelligent recommendations in real-time
- ✅ Auto-activating high-confidence agents
- ✅ Providing live notifications and statistics

### Key Characteristics

- **Real-Time**: 2-second polling interval (configurable)
- **Git-Aware**: Detects commits, staged, and unstaged changes
- **Intelligent**: Integrates with AI Intelligence System for recommendations
- **Non-Intrusive**: Runs in background, minimal output unless changes detected
- **Auto-Activation**: Automatically activates agents with ≥80% confidence
- **Statistics**: Tracks checks, recommendations, and activations

### Design Philosophy

```
Monitor > React > Automate | Background > Foreground | Signal > Noise
```

Watch Mode prioritizes **continuous monitoring** with **intelligent filtering**, **automatic action** on high-confidence signals, and **minimal noise** through smart notification thresholds.

---

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│ Watch Mode Main Loop (2s interval)                      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  while running:                                          │
│    ├─ sleep(check_interval)                             │
│    ├─ check_for_changes()                               │
│    │   ├─ Check git HEAD (commits)                      │
│    │   ├─ Get changed files                             │
│    │   └─ analyze_context()                             │
│    └─ handle_results()                                   │
│                                                          │
└────────────┬─────────────────────────────────────────────┘
             ↓
┌─────────────────────────────────────────────────────────┐
│ Context Analysis Layer                                   │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  IntelligentAgent.analyze_context(changed_files)        │
│  └─ Returns SessionContext                              │
│                                                          │
│  IntelligentAgent.get_recommendations()                 │
│  └─ Returns List[AgentRecommendation]                   │
│                                                          │
└────────────┬─────────────────────────────────────────────┘
             ↓
┌─────────────────────────────────────────────────────────┐
│ Action Layer                                             │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  if recommendations_changed():                           │
│    ├─ show_recommendations()                            │
│    └─ if auto_activate:                                 │
│        └─ handle_auto_activation()                      │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### Data Flow

```
1. Polling Timer (every 2s)
   └─ Check interval elapsed?

2. Git Status Check
   └─ subprocess.run(["git", "rev-parse", "HEAD"])
      └─ Compare with last_git_head

3. Get Changed Files
   └─ git diff --name-only HEAD           (unstaged)
   └─ git diff --name-only --cached       (staged)
   └─ Merge into changed_files list

4. Context Analysis
   └─ IntelligentAgent.analyze_context(changed_files)
      └─ SessionContext with signals detected

5. Generate Recommendations
   └─ IntelligentAgent.get_recommendations()
      └─ List[AgentRecommendation] sorted by confidence

6. Check if Changed
   └─ Compare agent_names with last_recommendations
      └─ If different → proceed
      └─ If same → skip (avoid spam)

7. Show Notifications
   └─ Print context summary
   └─ Print high-confidence recommendations (≥70%)

8. Auto-Activate (if enabled)
   └─ Filter recommendations: confidence ≥ 0.8
   └─ Exclude already activated
   └─ Call agent_activate() for each

9. Update State
   └─ last_recommendations = new_recommendations
   └─ activated_agents.add(agent_name)
   └─ Statistics counters++
```

---

## Core Components

### WatchMode Class

**Location**: `watch.py` - `WatchMode` class

The main controller for watch mode operations:

```python
class WatchMode:
    """Watch mode for real-time AI recommendations."""
    
    def __init__(
        self,
        auto_activate: bool = True,
        notification_threshold: float = 0.7,
        check_interval: float = 2.0,
    ):
        self.auto_activate = auto_activate
        self.notification_threshold = notification_threshold
        self.check_interval = check_interval
        
        # Initialize intelligent agent
        claude_dir = _resolve_claude_dir()
        self.intelligent_agent = IntelligentAgent(claude_dir / "intelligence")
        
        # State tracking
        self.running = False
        self.last_check_time = time.time()
        self.last_git_head = self._get_git_head()
        self.last_recommendations: List[AgentRecommendation] = []
        self.activated_agents: Set[str] = set()
        self.notification_history: Deque[Dict[str, str]] = deque(maxlen=50)
        
        # Statistics
        self.checks_performed = 0
        self.recommendations_made = 0
        self.auto_activations = 0
        self.start_time = datetime.now()
```

**Key Attributes**:

| Attribute | Type | Purpose |
|-----------|------|---------|
| `auto_activate` | bool | Enable auto-activation (default: True) |
| `notification_threshold` | float | Confidence threshold for notifications (0.7 = 70%) |
| `check_interval` | float | Seconds between checks (default: 2.0) |
| `intelligent_agent` | IntelligentAgent | AI Intelligence integration |
| `last_git_head` | str | Last known git HEAD hash |
| `last_recommendations` | List | Previous recommendations (for diff) |
| `activated_agents` | Set[str] | Agents activated this session |
| `notification_history` | Deque | Last 50 notifications |

---

## Polling Mechanism

### Main Loop

```python
def run(self) -> int:
    """Run watch mode main loop."""
    
    # Setup signal handlers for graceful shutdown
    def signal_handler(signum: int, frame: Optional[FrameType]) -> None:
        self.running = False
    
    signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # kill
    
    # Print banner
    self._print_banner()
    
    # Initial analysis
    self._analyze_context()
    
    # Main loop
    self.running = True
    
    try:
        while self.running:
            time.sleep(self.check_interval)  # Wait 2 seconds
            self._check_for_changes()        # Check for changes
    
    except KeyboardInterrupt:
        pass
    
    finally:
        # Cleanup and statistics
        self._print_notification("🛑", "Watch mode stopped", "", "yellow")
        self._print_statistics()
    
    return 0
```

### Check Cycle

```python
def _check_for_changes(self) -> None:
    """Check for changes and analyze context."""
    self.checks_performed += 1
    
    # 1. Check git HEAD changes (new commits)
    current_head = self._get_git_head()
    if current_head != self.last_git_head:
        self._print_notification(
            "📝",
            "Git commit detected",
            f"HEAD: {current_head[:8]}",
            "yellow",
        )
        self.last_git_head = current_head
    
    # 2. Analyze context (changed files)
    self._analyze_context()
```

### Performance Characteristics

| Metric | Value | Notes |
|--------|-------|-------|
| Poll interval | 2s | Configurable via `--interval` |
| Git check overhead | ~10-20ms | `git rev-parse HEAD` |
| File diff overhead | ~20-50ms | `git diff --name-only` |
| Context analysis | ~50-100ms | File pattern matching |
| Recommendation generation | ~100ms | Pattern matching + rules |
| Total cycle time | ~200ms | Leaves 1.8s idle |
| CPU usage | ~1% | Mostly sleeping |
| Memory usage | ~20MB | Loaded patterns + history |

---

## Git Integration

### Git Status Detection

**Detecting Commits**:
```python
def _get_git_head(self) -> Optional[str]:
    """Get current git HEAD hash."""
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()

# Usage:
current_head = self._get_git_head()
if current_head != self.last_git_head:
    # New commit detected!
    self.last_git_head = current_head
```

**Detecting File Changes**:
```python
def _get_changed_files(self) -> List[Path]:
    """Get list of changed files from git."""
    
    # Get unstaged changes
    result = subprocess.run(
        ["git", "diff", "--name-only", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    )
    
    # Get staged changes
    staged = subprocess.run(
        ["git", "diff", "--name-only", "--cached"],
        capture_output=True,
        text=True,
        check=True,
    )
    
    # Merge and deduplicate
    all_files = set(result.stdout.split("\n") + staged.stdout.split("\n"))
    return [Path(f) for f in all_files if f.strip()]
```

### Change Detection Strategy

**Three types of changes monitored**:

1. **Commits** (via `git rev-parse HEAD`)
   - Detects new commits
   - Triggers notification
   - Context re-analysis

2. **Staged Changes** (via `git diff --cached`)
   - Files added to index (`git add`)
   - Ready for commit
   - Included in context

3. **Unstaged Changes** (via `git diff HEAD`)
   - Modified but not staged
   - Working directory changes
   - Included in context

**Example Workflow**:
```bash
# User makes changes
$ vim src/auth.py          # Unstaged change detected
$ git add src/auth.py      # Staged change detected
$ git commit -m "..."      # Commit detected (HEAD change)
```

---

## Notification System

### Notification Types

**Context Detection**:
```
[14:30:15] 🔍 Context detected: Backend, API, Auth
  7 files changed
```

**Recommendations**:
```
  💡 Recommendations:

     🔴 security-auditor [AUTO]
        90% - Auth code detected - security review recommended

     🟡 test-automator
        75% - Used in 6/8 similar sessions

     🔵 quality-engineer [AUTO]
        85% - Changes detected - quality review recommended

     🔵 code-reviewer [AUTO]
        75% - Changes detected - code review recommended
```

**Auto-Activation**:
```
[14:30:16] ⚡ Auto-activating 3 agents...
     ✓ security-auditor
     ✓ quality-engineer
     ✓ code-reviewer
```

**Commit Detection**:
```
[14:31:42] 📝 Git commit detected
  HEAD: a3f8d2e1
```

**Status Changes**:
```
[14:32:00] 💤 No recommendations
  Current context doesn't warrant any suggestions
```

### Notification Filtering

**Threshold-Based**:
```python
# Only show recommendations with confidence >= threshold
high_confidence = [
    r for r in recommendations 
    if r.confidence >= self.notification_threshold
]

# Default: 0.7 (70% confidence)
```

**Change-Based**:
```python
def _recommendations_changed(self, new_recs: List[AgentRecommendation]) -> bool:
    """Check if recommendations changed significantly."""
    if not self.last_recommendations:
        return bool(new_recs)
    
    # Compare agent names
    old_agents = {r.agent_name for r in self.last_recommendations}
    new_agents = {r.agent_name for r in new_recs}
    
    # Only notify if different
    return old_agents != new_agents
```

**Benefits**:
- ✅ No spam from repeated identical recommendations
- ✅ Only notifies on meaningful context changes
- ✅ Configurable threshold for different sensitivity levels

### Color-Coded Output

```python
color_codes = {
    "red": "\033[91m",      # Critical urgency
    "green": "\033[92m",    # Success/activation
    "yellow": "\033[93m",   # Warning/commit
    "blue": "\033[94m",     # Info
    "magenta": "\033[95m",  # Unused
    "cyan": "\033[96m",     # Context detection
    "white": "\033[97m",    # Default
    "dim": "\033[2m",       # Low priority
}

# Example:
print(f"{cyan}[14:30:15] 🔍 Context detected{reset}")
```

### Urgency Icons

| Urgency | Icon | Meaning |
|---------|------|---------|
| Critical | 🔴 | Immediate action required (test failures, security) |
| High | 🟡 | Important recommendation (80%+ confidence) |
| Medium | 🔵 | Moderate priority (50-79% confidence) |
| Low | ⚪ | Optional suggestion (<50% confidence) |

---

## Auto-Activation

### Auto-Activation Logic

```python
def _handle_auto_activation(
    self, 
    recommendations: List[AgentRecommendation]
) -> None:
    """Handle auto-activation of agents."""
    
    # Filter candidates
    auto_agents = [
        r.agent_name
        for r in recommendations
        if r.auto_activate and r.agent_name not in self.activated_agents
    ]
    
    if not auto_agents:
        return
    
    # Notify
    self._print_notification(
        "⚡", 
        f"Auto-activating {len(auto_agents)} agents...", 
        "", 
        "green"
    )
    
    # Activate each agent
    for agent_name in auto_agents:
        try:
            exit_code, message = agent_activate(agent_name)
            if exit_code == 0:
                self.activated_agents.add(agent_name)
                self.auto_activations += 1
                print(f"     ✓ {agent_name}")
            else:
                print(f"     ✗ {agent_name}: Failed")
        except Exception as e:
            print(f"     ✗ {agent_name}: {str(e)}")
```

### Activation Criteria

An agent is auto-activated if **ALL** conditions are met:

1. ✅ `rec.auto_activate == True` (confidence ≥ 0.8)
2. ✅ `agent_name not in self.activated_agents` (not already activated)

**Example**:
```python
# Context: Modified src/auth.py
# Recommendation: security-auditor (confidence=0.9, auto_activate=True)

if 0.9 >= 0.8 and "security-auditor" not in activated_agents:
    agent_activate("security-auditor")  # AUTO-ACTIVATE
    activated_agents.add("security-auditor")
```

### Preventing Duplicate Activations

```python
# Track activated agents per session
self.activated_agents: Set[str] = set()

# Check before activating
if agent_name not in self.activated_agents:
    agent_activate(agent_name)
    self.activated_agents.add(agent_name)
else:
    # Already activated - skip
    pass
```

**Benefits**:
- ✅ No duplicate activations
- ✅ Agents only activated once per watch session
- ✅ Clean state tracking

---

## Resource Management

### Memory Management

**Fixed Size Structures**:
```python
# Notification history: bounded at 50 entries
self.notification_history: Deque[Dict[str, str]] = deque(maxlen=50)

# Activated agents: typically 5-10 agents max
self.activated_agents: Set[str] = set()

# Last recommendations: typically 3-7 recommendations
self.last_recommendations: List[AgentRecommendation] = []
```

**Memory Profile**:
- IntelligentAgent: ~5MB (loaded patterns)
- Notification history: ~5KB (50 notifications × 100 bytes)
- State tracking: ~1KB
- **Total**: ~20MB steady-state

### CPU Management

**Sleep-Dominated Loop**:
```python
while self.running:
    time.sleep(self.check_interval)  # 2s sleep (0% CPU)
    self._check_for_changes()        # ~200ms work (~10% CPU during check)

# Result: Average CPU usage ~1%
```

**Process Priority**:
- Runs at normal priority (not background)
- Can be nice'd down: `nice -n 10 cortex watch`
- Suitable for long-running background monitoring

### Signal Handling

**Graceful Shutdown**:
```python
def signal_handler(signum: int, frame: Optional[FrameType]) -> None:
    self.running = False  # Exit main loop

signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C
signal.signal(signal.SIGTERM, signal_handler)  # kill command

try:
    while self.running:
        # ... main loop
except KeyboardInterrupt:
    pass
finally:
    # Always print statistics before exit
    self._print_statistics()
```

**Handled Signals**:
- `SIGINT` (Ctrl+C): Graceful shutdown with statistics
- `SIGTERM` (kill): Graceful shutdown with statistics
- `KeyboardInterrupt`: Catch-all for interrupts

---

## Statistics & Monitoring

### Statistics Tracking

```python
# Statistics counters
self.checks_performed = 0        # Total polling cycles
self.recommendations_made = 0    # Times recommendations changed
self.auto_activations = 0        # Agents auto-activated
self.start_time = datetime.now() # Session start time

# Example increment:
def _check_for_changes(self) -> None:
    self.checks_performed += 1
    # ...
    if recommendations_changed:
        self.recommendations_made += 1
```

### Statistics Display

```python
def _print_statistics(self) -> None:
    """Print watch mode statistics."""
    duration = datetime.now() - self.start_time
    hours = int(duration.total_seconds() // 3600)
    minutes = int((duration.total_seconds() % 3600) // 60)
    
    print("\n" + "─" * 70)
    print("📊 WATCH MODE STATISTICS")
    print("─" * 70)
    print(f"  Duration: {hours}h {minutes}m")
    print(f"  Checks performed: {self.checks_performed}")
    print(f"  Recommendations: {self.recommendations_made}")
    print(f"  Auto-activations: {self.auto_activations}")
    print(f"  Agents activated: {len(self.activated_agents)}")
    if self.activated_agents:
        print(f"    {', '.join(sorted(self.activated_agents))}")
    print("─" * 70 + "\n")
```

**Example Output**:
```
──────────────────────────────────────────────────────────────────
📊 WATCH MODE STATISTICS
──────────────────────────────────────────────────────────────────
  Duration: 0h 15m
  Checks performed: 450
  Recommendations: 3
  Auto-activations: 5
  Agents activated: 3
    python-pro, security-auditor, test-automator
──────────────────────────────────────────────────────────────────
```

### Notification History

```python
# Store last 50 notifications with timestamp
self.notification_history.append({
    "timestamp": "14:30:15",
    "icon": "🔍",
    "title": "Context detected",
    "message": "Backend, API, Auth",
})

# Query history:
recent_notifications = list(self.notification_history)[-10:]
```

---

## CLI Usage

### Basic Usage

```bash
# Start watch mode with defaults
$ cortex watch

🤖 AI WATCH MODE - Real-time Intelligence
══════════════════════════════════════════════════════════════════

[14:30:00] Watch mode started
  Auto-activate: ON
  Threshold: 70% confidence
  Check interval: 2s

  Monitoring:
    • Git changes (commits, staged, unstaged)
    • File modifications
    • Context changes

  Press Ctrl+C to stop

──────────────────────────────────────────────────────────────────

[14:30:00] 🚀 Performing initial analysis...

[14:30:01] 🔍 Context detected: Backend, API
  3 files changed

  💡 Recommendations:

     🟡 python-pro
        75% - Used in 5/7 similar sessions

     🔵 api-documenter
        65% - API changes detected

[14:30:02] ⚡ Auto-activating 1 agents...
     ✓ python-pro

[14:32:15] 📝 Git commit detected
  HEAD: a3f8d2e1

[14:35:00] ^C

[14:35:00] 🛑 Watch mode stopped

──────────────────────────────────────────────────────────────────
📊 WATCH MODE STATISTICS
──────────────────────────────────────────────────────────────────
  Duration: 0h 5m
  Checks performed: 150
  Recommendations: 2
  Auto-activations: 1
  Agents activated: 1
    python-pro
──────────────────────────────────────────────────────────────────
```

### Command Options

```bash
# Disable auto-activation
$ cortex watch --no-auto

# Set custom threshold (50% confidence)
$ cortex watch --threshold 0.5

# Custom check interval (5 seconds)
$ cortex watch --interval 5

# Combine options
$ cortex watch --no-auto --threshold 0.8 --interval 1
```

### CLI Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--auto/--no-auto` | flag | True | Enable/disable auto-activation |
| `--threshold` | float | 0.7 | Confidence threshold (0.0-1.0) |
| `--interval` | float | 2.0 | Check interval in seconds |

---

## Development Guide

### Adding Custom Notifications

**Step 1**: Add notification method:
```python
def _notify_custom_event(self, details: str) -> None:
    """Notify about custom event."""
    self._print_notification(
        "🎯",                          # Icon
        "Custom Event Detected",       # Title
        details,                       # Message
        "magenta",                     # Color
    )
```

**Step 2**: Call in check cycle:
```python
def _check_for_changes(self) -> None:
    self.checks_performed += 1
    
    # Existing checks
    self._check_git_head()
    
    # NEW: Custom check
    if self._detect_custom_condition():
        self._notify_custom_event("Custom condition met!")
    
    self._analyze_context()
```

### Extending Context Detection

**Step 1**: Add detection logic:
```python
def _detect_dockerfile_changes(self) -> bool:
    """Check if Dockerfile changed."""
    changed_files = self._get_changed_files()
    return any("Dockerfile" in str(f) for f in changed_files)
```

**Step 2**: Integrate with analysis:
```python
def _analyze_context(self) -> bool:
    """Analyze context with Dockerfile detection."""
    changed_files = self._get_changed_files()
    
    # Custom detection
    if self._detect_dockerfile_changes():
        self._print_notification(
            "🐳",
            "Docker changes detected",
            "Dockerfile modified",
            "cyan",
        )
    
    # Standard analysis
    context = self.intelligent_agent.analyze_context(changed_files)
    # ...
```

### Testing Watch Mode

**Example Test** (`tests/unit/test_watch.py`):
```python
from claude_ctx_py.watch import WatchMode
from unittest.mock import patch, MagicMock

def test_watch_mode_initialization():
    """Test watch mode initialization."""
    watch = WatchMode(
        auto_activate=False,
        notification_threshold=0.8,
        check_interval=5.0,
    )
    
    assert watch.auto_activate is False
    assert watch.notification_threshold == 0.8
    assert watch.check_interval == 5.0
    assert watch.checks_performed == 0

@patch("subprocess.run")
def test_git_head_detection(mock_run):
    """Test git HEAD detection."""
    mock_run.return_value = MagicMock(
        stdout="abc123def456\n",
        returncode=0,
    )
    
    watch = WatchMode()
    head = watch._get_git_head()
    
    assert head == "abc123def456"
    mock_run.assert_called_once()

def test_recommendation_change_detection():
    """Test recommendation change detection."""
    from claude_ctx_py.intelligence import AgentRecommendation
    
    watch = WatchMode()
    
    # Initial recommendations
    rec1 = AgentRecommendation(
        agent_name="python-pro",
        confidence=0.8,
        reason="Test",
        urgency="medium",
        auto_activate=True,
        context_triggers=[],
    )
    
    watch.last_recommendations = [rec1]
    
    # Same recommendation
    new_recs = [rec1]
    assert not watch._recommendations_changed(new_recs)
    
    # Different recommendation
    rec2 = AgentRecommendation(
        agent_name="security-auditor",
        confidence=0.9,
        reason="Test",
        urgency="high",
        auto_activate=True,
        context_triggers=[],
    )
    
    new_recs = [rec2]
    assert watch._recommendations_changed(new_recs)
```

### Debugging Tips

**1. Dry-run mode (no auto-activation)**:
```bash
$ cortex watch --no-auto --threshold 0.5
```

**2. Verbose logging**:
```python
# Add debug prints
def _check_for_changes(self) -> None:
    print(f"[DEBUG] Check #{self.checks_performed}")
    print(f"[DEBUG] Git HEAD: {self._get_git_head()}")
    print(f"[DEBUG] Changed files: {len(self._get_changed_files())}")
    # ...
```

**3. Monitor in separate terminal**:
```bash
# Terminal 1: Watch mode
$ cortex watch

# Terminal 2: Make changes and observe
$ vim src/file.py
$ git add src/file.py
$ git commit -m "test"
```

---

## Performance Considerations

### Optimization Strategies

**1. Reduce Poll Interval**:
```bash
# Lower interval for more responsive monitoring
$ cortex watch --interval 1.0

# Higher interval for lower resource usage
$ cortex watch --interval 5.0
```

**2. Threshold Tuning**:
```bash
# Higher threshold = fewer notifications
$ cortex watch --threshold 0.9

# Lower threshold = more notifications
$ cortex watch --threshold 0.5
```

**3. Git Optimization**:
```python
# Cache git commands
@lru_cache(maxsize=1)
def _get_git_head() -> Optional[str]:
    # Cached for 1 call (invalidate on next check)
    pass
```

### Resource Limits

**Recommended Limits**:
- Max poll frequency: 0.5s (2 Hz)
- Min poll frequency: 10s (0.1 Hz)
- Notification history: 50 entries (configurable)
- Memory cap: ~50MB total

**Scaling Behavior**:
- Linear with number of changed files
- Constant with repository size
- Independent of total file count

---

## Integration Patterns

### With AI Intelligence

```python
# Watch mode delegates to IntelligentAgent
self.intelligent_agent = IntelligentAgent(claude_dir / "intelligence")

# On each check:
context = self.intelligent_agent.analyze_context(changed_files)
recommendations = self.intelligent_agent.get_recommendations()
```

### With Memory Vault

```python
# Can integrate auto-capture on session end
if watch_mode_stopping:
    if is_auto_capture_enabled():
        memory_capture(
            title=f"Watch session {duration}",
            summary=f"Auto-activated: {activated_agents}",
            implementations=changed_files,
        )
```

### With TUI

```bash
# Can run watch mode in background while TUI is active
$ cortex watch &
$ cortex tui

# Watch mode provides notifications
# TUI provides interactive control
```

---

## Related Documentation

- [AI Intelligence System](./AI_INTELLIGENCE_ARCHITECTURE.md)
- [Memory Vault System](./MEMORY_VAULT_ARCHITECTURE.md)
- [Master Architecture Document](../../architecture/MASTER_ARCHITECTURE.md)

---

## Revision History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2025-12-05 | Initial Watch Mode documentation | System Architect |

---

**Document Status**: ✅ Current  
**Maintainer**: Core Team
