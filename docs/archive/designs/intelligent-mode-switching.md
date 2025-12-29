# Intelligent Mode Switching Design

## Overview

Design for intelligent mode switching with conflict detection, dependency resolution, auto-deactivation, and mode groups.

## Mode Metadata Schema

Modes will use YAML frontmatter to declare their metadata:

```yaml
---
name: Parallel_Orchestration
category: execution
priority: high
conflicts:
  - Deep_Analysis
  - Sequential_Processing
dependencies:
  - parallel-execution-rules  # Rule dependency
overrides:
  quality_score_min: 7  # From Quality_Gates rule
  test_coverage_min: 85  # From Quality_Gates rule
group: orchestration
tags:
  - performance
  - parallel
  - quality
auto_activate_triggers:
  - multi_file_operations
  - code_generation
---

# Parallel Orchestration Mode
...
```

### Metadata Fields

**Required:**
- `name`: Mode identifier (must match filename without .md)
- `category`: Mode category (execution, quality, communication, planning, visual)

**Optional:**
- `priority`: high|medium|low (default: medium) - for conflict resolution
- `conflicts`: List of mode names that cannot be active simultaneously
- `dependencies`: List of rules/modes that must be active
- `overrides`: Key-value pairs overriding rule thresholds
- `group`: Logical grouping (only one mode per group can be active)
- `tags`: Searchable keywords
- `auto_activate_triggers`: Conditions that suggest activating this mode

## Categories

### 1. **Execution** - How work is performed
- Examples: `Parallel_Orchestration`, `Sequential_Processing`, `Batch_Mode`
- Conflicts: Often mutually exclusive (parallel vs sequential)
- Affects: Agent coordination, task ordering, workstream management

### 2. **Quality** - Quality standards and enforcement
- Examples: `Quality_Focus`, `Fast_Iteration`, `Production_Ready`
- Conflicts: Different quality levels may conflict
- Affects: Code review thresholds, test coverage, documentation requirements

### 3. **Communication** - How Claude communicates
- Examples: `Token_Efficient`, `Verbose_Explanations`, `Teaching_Mode`
- Conflicts: Verbosity levels may conflict
- Affects: Output format, explanation depth, token usage

### 4. **Planning** - How tasks are organized
- Examples: `Task_Management`, `Agile_Sprint`, `Waterfall`
- Conflicts: Different planning methodologies
- Affects: TodoWrite usage, milestone tracking, reporting

### 5. **Visual** - UI/UX focus
- Examples: `Super_Saiyan`, `Minimal_UI`, `Accessibility_First`
- Conflicts: Different visual philosophies
- Affects: Animations, colors, interactions

## Conflict Resolution

### Priority-Based Resolution

When activating a mode that conflicts with active modes:

1. **Check conflicts**: Read mode metadata
2. **Find active conflicts**: Which active modes conflict?
3. **Compare priorities**:
   - If new mode has **higher priority** → Auto-deactivate conflicting modes
   - If new mode has **equal/lower priority** → Prompt user

```python
# Pseudo-code
def activate_mode_with_conflicts(mode_name):
    mode = load_mode_metadata(mode_name)
    active_modes = get_active_modes()

    conflicts = []
    for active in active_modes:
        if active.name in mode.conflicts:
            conflicts.append(active)

    if not conflicts:
        # No conflicts, just activate
        return mode_activate(mode_name)

    # Resolve conflicts
    for conflict in conflicts:
        if mode.priority > conflict.priority:
            # Auto-deactivate lower priority mode
            mode_deactivate(conflict.name)
            notify(f"Deactivated {conflict.name} (lower priority)")
        elif mode.priority == conflict.priority:
            # Prompt user
            choice = prompt_user(
                f"Activate {mode_name}? This will deactivate {conflict.name}",
                ["Yes, switch", "No, keep current", "Activate both (ignore conflict)"]
            )
            if choice == 0:  # Yes, switch
                mode_deactivate(conflict.name)
            elif choice == 1:  # No
                return False
            # choice == 2: Ignore conflict, activate anyway

    # Activate the new mode
    return mode_activate(mode_name)
```

### Group-Based Resolution

Modes in the same group are mutually exclusive:

```python
# Pseudo-code
def activate_mode_in_group(mode_name):
    mode = load_mode_metadata(mode_name)
    if not mode.group:
        return mode_activate(mode_name)

    # Find other active modes in same group
    active_in_group = [m for m in get_active_modes() if m.group == mode.group]

    if active_in_group:
        # Auto-deactivate all modes in same group
        for other in active_in_group:
            mode_deactivate(other.name)
            notify(f"Deactivated {other.name} (same group: {mode.group})")

    return mode_activate(mode_name)
```

## Dependency Resolution

Before activating a mode, ensure dependencies are met:

```python
# Pseudo-code
def check_dependencies(mode_name):
    mode = load_mode_metadata(mode_name)

    missing_deps = []
    for dep in mode.dependencies:
        if dep.startswith('rule:') or dep.endswith('-rules'):
            # Rule dependency
            if not is_rule_active(dep):
                missing_deps.append(dep)
        else:
            # Mode dependency
            if not is_mode_active(dep):
                missing_deps.append(dep)

    if missing_deps:
        # Option 1: Auto-activate dependencies
        for dep in missing_deps:
            if is_rule(dep):
                rules_activate(dep)
                notify(f"Activated rule: {dep} (required by {mode_name})")
            else:
                mode_activate(dep)
                notify(f"Activated mode: {dep} (required by {mode_name})")

        # Option 2: Prompt user
        # choice = prompt_user(f"Activate dependencies? {missing_deps}")

    return len(missing_deps) == 0
```

## Override System

Modes can override rule thresholds:

```yaml
# In Quality_Focus.md frontmatter
overrides:
  quality_score_min: 8  # Raises from 7 (quality-gate-rules)
  test_coverage_min: 90  # Raises from 85 (quality-gate-rules)
  doc_required: true     # Enforces documentation
```

**Implementation:**
- Store overrides in a global registry when mode is activated
- Deactivation removes overrides (reverts to rule defaults)
- Multiple active modes with overrides → take the **most restrictive** value

```python
# Pseudo-code
class OverrideRegistry:
    def __init__(self):
        self.overrides = {}  # {key: [(mode, value), ...]}

    def add_override(self, mode_name, key, value):
        if key not in self.overrides:
            self.overrides[key] = []
        self.overrides[key].append((mode_name, value))

    def remove_override(self, mode_name):
        for key in self.overrides:
            self.overrides[key] = [
                (m, v) for m, v in self.overrides[key] if m != mode_name
            ]

    def get_effective_value(self, key, default):
        if key not in self.overrides or not self.overrides[key]:
            return default

        # For numeric values, take max (most restrictive)
        # For boolean values, take True if any True
        values = [v for _, v in self.overrides[key]]

        if isinstance(default, (int, float)):
            return max(values)
        elif isinstance(default, bool):
            return any(values)
        else:
            return values[-1]  # Last wins
```

## TUI Integration

### Mode Details View Enhancements

When viewing mode details, show:

```
┌─ Parallel_Orchestration ──────────────────────────┐
│ Category: execution                                │
│ Priority: high                                     │
│ Group: orchestration                               │
│                                                    │
│ Conflicts:                                         │
│   • Deep_Analysis (will be deactivated)           │
│   • Sequential_Processing (will be deactivated)   │
│                                                    │
│ Dependencies:                                      │
│   ✓ parallel-execution-rules (active)             │
│   ✗ quality-gate-rules (inactive - will activate) │
│                                                    │
│ Overrides:                                         │
│   • quality_score_min: 7 → 8                      │
│   • test_coverage_min: 85 → 90                    │
│                                                    │
│ [Space] Activate | [ESC] Close                    │
└────────────────────────────────────────────────────┘
```

### Conflict Warning Dialog

When toggling a mode with conflicts:

```
┌─ Activate Parallel_Orchestration? ────────────────┐
│                                                    │
│ This will deactivate:                             │
│   • Deep_Analysis (priority: medium)              │
│                                                    │
│ And activate dependencies:                        │
│   • quality-gate-rules                            │
│                                                    │
│ Continue?                                          │
│                                                    │
│ [Y] Yes, switch  [N] No, cancel  [I] Ignore       │
└────────────────────────────────────────────────────┘
```

### Mode List View Indicators

Add visual indicators:

```
Name                      Status   Category    Conflicts
Parallel_Orchestration    ● ACTIVE execution   2 conflicts
Quality_Focus             ● ACTIVE quality     0 conflicts
Deep_Analysis             ○ inactive execution ⚠ conflicts with active
```

## Implementation Files

### 1. `claude_ctx_py/core/mode_metadata.py`

New file for mode metadata handling:

```python
@dataclass
class ModeMetadata:
    name: str
    category: str
    priority: str = "medium"
    conflicts: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    overrides: Dict[str, Any] = field(default_factory=dict)
    group: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    auto_activate_triggers: List[str] = field(default_factory=list)

def parse_mode_metadata(mode_path: Path) -> Optional[ModeMetadata]:
    """Parse YAML frontmatter from mode file."""
    ...

def get_mode_conflicts(mode_name: str) -> List[str]:
    """Get list of modes that conflict with given mode."""
    ...

def check_mode_dependencies(mode_name: str) -> Tuple[bool, List[str]]:
    """Check if mode dependencies are satisfied."""
    ...
```

### 2. `claude_ctx_py/core/modes.py` (update)

Add intelligent switching:

```python
def mode_activate_intelligent(
    mode: str,
    auto_resolve: bool = True,
    home: Path | None = None
) -> tuple[int, str, List[str]]:
    """
    Activate mode with intelligent conflict resolution.

    Returns:
        (exit_code, message, deactivated_modes)
    """
    ...

def mode_deactivate_intelligent(
    mode: str,
    check_dependents: bool = True,
    home: Path | None = None
) -> tuple[int, str, List[str]]:
    """
    Deactivate mode and warn about dependent modes.

    Returns:
        (exit_code, message, affected_modes)
    """
    ...
```

### 3. `claude_ctx_py/tui_textual.py` (update)

Update mode toggle action:

```python
def action_toggle(self) -> None:
    """Toggle selected item."""
    if self.current_view == "modes":
        # Use intelligent toggle
        self._toggle_mode_intelligent()
```

## Migration Path

### Phase 1: Add Metadata (Non-Breaking)
1. Add YAML frontmatter parser
2. Parse metadata but don't enforce
3. Display metadata in TUI (read-only)

### Phase 2: Enable Conflict Detection (Opt-In)
1. Implement conflict detection
2. Show warnings but allow override
3. Add `--strict` flag to enforce

### Phase 3: Full Intelligent Switching (Default)
1. Make intelligent switching default
2. Add auto-resolution logic
3. Update all mode files with metadata

### Phase 4: Dependency & Override System
1. Implement dependency resolution
2. Implement override registry
3. Integrate with rule system

## Example Mode Metadata

### Parallel_Orchestration.md
```yaml
---
name: Parallel_Orchestration
category: execution
priority: high
conflicts:
  - Deep_Analysis
  - Sequential_Processing
dependencies:
  - parallel-execution-rules
  - quality-gate-rules
group: orchestration
overrides:
  quality_score_min: 7
  test_coverage_min: 85
tags:
  - performance
  - parallel
  - quality
  - agents
---
```

### Quality_Focus.md
```yaml
---
name: Quality_Focus
category: quality
priority: high
dependencies:
  - quality-gate-rules
overrides:
  quality_score_min: 8
  test_coverage_min: 90
  doc_required: true
tags:
  - quality
  - production
  - security
---
```

### Token_Efficient.md
```yaml
---
name: Token_Efficient
category: communication
priority: medium
conflicts:
  - Verbose_Explanations
  - Teaching_Mode
group: communication_style
tags:
  - efficiency
  - tokens
  - cost
---
```

## Benefits

1. **Prevents Invalid States**: Can't have conflicting modes active
2. **Automatic Cleanup**: Deactivates conflicting modes automatically
3. **Dependency Management**: Ensures required modes/rules are active
4. **User Guidance**: Shows what will happen before activation
5. **Flexible Overrides**: Modes can elevate standards dynamically
6. **Better UX**: Clear visual indicators and warnings

## Testing Strategy

1. **Unit Tests**: Test metadata parsing, conflict detection, dependency resolution
2. **Integration Tests**: Test mode activation flows with conflicts
3. **TUI Tests**: Test dialog flows and visual indicators
4. **Migration Tests**: Ensure backward compatibility with modes without metadata
