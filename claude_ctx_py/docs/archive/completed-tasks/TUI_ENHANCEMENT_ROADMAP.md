# TUI Visual Enhancement Roadmap

## Quick Reference: Current Visual State

### Strengths
- Consistent color scheme (cyan/magenta/green/yellow/blue/red)
- Clean layout hierarchy (header/body/footer)
- Responsive table components with inline styling
- Good use of special characters (→, ✓, ○, █, ░)
- Context-aware status messages and help

### Current Limitations
- Hard-coded colors (no theme customization)
- No animations or transitions
- Basic text-only displays (could add icons/Unicode art)
- Limited accessibility options
- No dark/light mode support
- Static layouts (no responsive resizing)

---

## Enhancement Areas & Priorities

### Priority 1: Foundation (High Impact, Core Features)

#### 1.1 Theme System
**Goal**: Allow users to customize colors and styles

**Changes**:
- Create `themes/` directory structure
- Define theme configuration format (JSON or YAML)
- Implement theme loader and selector
- Support environment variable override

**Implementation**:
```python
# themes/default.json
{
  "name": "default",
  "colors": {
    "primary": "cyan",
    "secondary": "magenta",
    "active": "bold green",
    "inactive": "yellow",
    "complete": "bold blue",
    "error": "bold red",
    "dim": "dim",
    "selected": "reverse"
  }
}

# themes/dark.json - optimize for dark terminals
# themes/light.json - optimize for light terminals
# themes/accessible.json - high contrast
```

**Benefits**:
- User customization without code changes
- Dark/light mode support
- Accessibility improvements (high contrast themes)
- Corporate branding customization

---

#### 1.2 Configuration File
**Goal**: Persist user preferences

**File**: `~/.claude/tui-config.yaml`

```yaml
tui:
  theme: "default"
  color_mode: "auto"  # auto, dark, light
  show_icons: true
  show_unicode: true
  update_frequency: 500  # ms
  enable_animations: true
  font_size: "normal"  # normal, large, small
  accessibility:
    high_contrast: false
    reduce_motion: false
    screen_reader: false
```

---

### Priority 2: Visual Enhancements (Medium Impact, Better UX)

#### 2.1 Advanced Progress Indicators
**Current**: `[████████░░] 75%`

**Enhanced Options**:
- Percentage-based coloring:
  ```
  0-25%:   [████░░░░░░] 75% (red)
  25-50%:  [████████░░] 50% (yellow)
  50-75%:  [██████████] 75% (cyan)
  75-100%: [██████████] 100% (green)
  ```
- Animated spinners for indeterminate progress
- Step-based progress (Step 3/5 indicator)

#### 2.2 Status Icons
**Current**: Text labels only

**Enhanced**:
```
Active     → ✓ Active
Inactive   → ✗ Inactive (or ○)
Running    → ▶ Running
Complete   → ✓ Complete
Error      → ✗ Error
Warning    → ⚠ Warning
Pending    → ⏳ Pending
```

**Implementation**:
- Configurable via theme
- Fallback to text if terminal doesn't support Unicode

#### 2.3 Inline Status Badges
**Current**: Status as separate column

**Enhanced**: Color-coded status badges in name column
```
▼ [Active] Agent-1              → Better visual hierarchy
▼ [Ready]  Agent-2
▼ [Error]  Agent-3
```

---

### Priority 3: Interactive Improvements (Medium Impact, Better Features)

#### 3.1 Modal Dialogs
**For**: Confirmations, critical operations

**Example**:
```
┌────────────────────────────────┐
│    Confirm Agent Deactivation  │
├────────────────────────────────┤
│ Are you sure you want to       │
│ deactivate [agent-name]?       │
│                                │
│ This action cannot be undone.  │
│                                │
│  [Yes]  [No]  [Cancel]        │
└────────────────────────────────┘
```

#### 3.2 Loading Indicators
**For**: Long-running operations

**Options**:
- Spinner: `⠋ ⠙ ⠹ ⠸ ⠼ ⠴ ⠦ ⠧ ⠇ ⠏`
- Dots: `. .. ... ....`
- Bar: `▁ ▃ ▄ ▅ ▆ ▇ █`

#### 3.3 Expandable Tree Views
**For**: Agent dependencies, hierarchies

```
▼ Agents (5)
  ▼ Foundation (3)
    ✓ code-reviewer
    ✓ test-automator
    ✓ api-documenter
  ▼ Specialized (2)
    ✗ custom-agent-1
    ○ community-agent-2
```

---

### Priority 4: Information Architecture (Lower Priority, Nice-to-Have)

#### 4.1 Sidebar Navigation
**Current**: Key number switching (1-9)

**Enhanced**: Persistent sidebar
```
╭─────────────┬──────────────────╮
│ ▼ Views     │ Agents View      │
│ ✓ Overview  │ ──────────────── │
│ ✓ Agents    │ ▼ Name    Status │
│ ✓ Modes     │ . agent-1  ✓    │
│ ✓ Rules     │ . agent-2  ○    │
│ ✓ Skills    │ > agent-3  ✗    │
│ ✓ Workflows │                  │
│ ✓ Profile   │ [Space] Toggle   │
│ ○ Export    │ [?] Help         │
╰─────────────┴──────────────────╯
```

#### 4.2 Breadcrumb Navigation
**For**: Context awareness

```
Home > Agents > Details > Agent-1
```

#### 4.3 Tab-Based Views
**For**: Multi-view sections

```
┌─ Agents ─┬─ Modes ─┬─ Rules ─┐
│ [table]  │ [table] │ [table] │
│          │         │         │
```

---

### Priority 5: Data Visualization (Lower Priority, Advanced)

#### 5.1 Dependency Graphs
**For**: Agent relationships

```
code-reviewer ──┬─→ test-automator
                └─→ api-documenter
```

#### 5.2 Heatmaps
**For**: Skill usage frequency

```
Skill Name     | Mon | Tue | Wed | Thu | Fri
───────────────┼─────┼─────┼─────┼─────┼─────
skill-1        | ░░░ | ░░░ | ███ | ███ | ░░░
skill-2        | ░░░ | ███ | ███ | ░░░ | ░░░
skill-3        | ███ | ░░░ | ░░░ | ███ | ░░░
```

#### 5.3 Timeline Views
**For**: Workflow execution

```
09:00 ├─ Step 1 (completed) ─────────────────────┤ 09:15
09:15 ├─ Step 2 (running) ───────────────────────► 09:30
09:30 ├─ Step 3 (pending) ──────────────────────┐ pending
```

---

## Implementation Strategy

### Phase 1: Theme System (Week 1)
1. Design theme file format
2. Implement theme loader
3. Create default, dark, light, accessible themes
4. Update all views to use theme colors
5. Add configuration file support

**Files to Create**:
- `claude_ctx_py/theme.py` (new)
- `claude_ctx_py/config.py` (new)
- `themes/default.json` (new)
- `themes/dark.json` (new)
- `themes/accessible.json` (new)

**Files to Modify**:
- `claude_ctx_py/tui.py` - Use theme colors
- All view rendering methods

### Phase 2: Visual Polish (Week 2)
1. Add status icons
2. Enhance progress bars with coloring
3. Add loading indicators
4. Implement modal dialogs

**Files to Create**:
- `claude_ctx_py/ui_components.py` (new)

**Files to Modify**:
- `claude_ctx_py/tui.py` - Use new components

### Phase 3: Interactive Features (Week 3)
1. Add expandable tree views
2. Implement keyboard shortcuts
3. Add input validation dialogs
4. Create confirmation modals

### Phase 4: Information Architecture (Future)
1. Implement sidebar navigation
2. Add breadcrumb trails
3. Create tab-based views
4. Add drag-and-drop if possible

### Phase 5: Advanced Visualizations (Future)
1. Add dependency graphs
2. Implement heatmaps
3. Create timeline views

---

## Quick Wins (Easy Wins, High Impact)

### 1. Status Emoji/Icons
Replace text with Unicode:
```python
STATUS_ICONS = {
    "active": "✓",
    "inactive": "✗",
    "running": "▶",
    "complete": "✓",
    "error": "✗",
    "pending": "⏳",
}
```

### 2. Colored Progress Bars
```python
def get_progress_color(percentage: int) -> str:
    if percentage < 25:
        return "red"
    elif percentage < 50:
        return "yellow"
    elif percentage < 75:
        return "cyan"
    else:
        return "green"
```

### 3. Better Date Formatting
```python
from humanize import naturaldate  # library
last_used_str = naturaldate(dt)  # "2 hours ago"
```

### 4. Number Formatting
```python
def format_large_number(n: int) -> str:
    for unit in ['', 'K', 'M', 'B']:
        if n < 1000:
            return f"{n:.1f}{unit}"
        n /= 1000
    return f"{n:.1f}T"
```

---

## Testing Strategy

### Visual Testing
- Terminal screenshots for different themes
- Size testing (80x24, 120x30, 200x50)
- Color mode testing (256 color, truecolor)
- Unicode support testing

### Accessibility Testing
- High contrast theme
- Screen reader compatibility
- Keyboard-only navigation
- Reduce motion mode

### Performance Testing
- Rendering speed benchmarks
- Memory usage monitoring
- File I/O optimization

---

## Dependencies to Consider Adding

- `humanize` - Better date/number formatting
- `rich-pixels` - Pixel art in terminal (advanced)
- `asciichartpy` - ASCII charts (optional)
- `pydantic` - Config validation (optional)

---

## Configuration Examples

### User Theme Customization
```yaml
tui:
  theme: "dark"
  overrides:
    colors:
      active: "bold green"
      primary: "bright_cyan"
```

### Accessibility Profile
```yaml
tui:
  theme: "accessible"
  accessibility:
    high_contrast: true
    reduce_motion: true
    larger_text: true
    screen_reader: true
```

---

## Success Metrics

1. **User Satisfaction**: Survey on visual improvements
2. **Accessibility**: WCAG compliance score
3. **Performance**: Render time < 100ms
4. **Customization**: 5+ built-in themes available
5. **Adoption**: Configuration file usage rate

