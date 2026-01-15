# Cortex TUI - Documentation Index

## Quick Links to Documentation

### 1. **TUI_EXPLORATION_SUMMARY.md** - Executive Overview

- 5-minute read of the entire TUI implementation
- Architecture overview and key findings
- Current state assessment and recommendations
- Performance characteristics and enhancement opportunities

### 2. **TUI_VISUAL_ANALYSIS.md** - Comprehensive Reference

- Detailed breakdown of all 10 views (Overview, Agents, Modes, Rules, Skills, Workflows, Orchestrate, Profile, Export, Help)
- Component documentation (tables, panels, layouts)
- Color schemes and styling system
- Keyboard navigation and interaction patterns
- State management architecture
- Rendering strategy and performance analysis

### 3. **TUI_ENHANCEMENT_ROADMAP.md** - Implementation Guide

- Prioritized enhancement opportunities (5 phases)
- Quick wins for immediate impact
- Phase-by-phase implementation strategy
- Configuration and theming design
- Testing strategy and success metrics

### 4. **tui/tui-entity-guide.md** - Entity Relationships in the TUI

- Explains how profiles, modes, workflows, scenarios, and agents differ
- Shows which TUI view or hotkey manages each entity
- Maps how scenarios trigger profiles/modes and feed workflows
- Includes practical end-to-end flow for staying oriented

---

## Current State Summary

### What Works Well

- Clean 3-part layout (header/body/footer)
- Consistent color scheme (6 main colors + modifiers)
- 10+ views with specialized functionality
- Good keyboard navigation (1-9 for views, arrow keys for navigation)
- Helpful status messages and context-aware hints
- Rich library provides excellent rendering

### What Could Be Better

- Hard-coded colors (no theming system)
- No animations or visual feedback
- Limited accessibility options
- Basic information visualization
- Full-screen refresh on every update

---

## Key Metrics at a Glance

| Metric | Value |
|--------|-------|
| Total Code | ~2,500 lines |
| Views | 10+ |
| Color Palette | 6 colors + 4 modifiers |
| Keyboard Shortcuts | 20+ |
| Hard-Coded Colors | 1,000+ references |
| Dependencies | Rich 13.0+, Textual 0.47+, PyYAML 6.0+ |

---

## Color Palette

```
CYAN        - Primary accent (names, highlights)
MAGENTA     - Bold magenta (table headers)
GREEN       - Active status, success (bold green)
YELLOW      - Inactive, warnings
BLUE        - Complete/finished states (bold blue)
RED         - Errors (bold red)
DIM         - Supplementary info
REVERSE     - Selected rows
```

---

## View Architecture

### Overview (1)

- Dashboard with system status
- Agent/Mode/Rule/Skill counts
- Quick action hints

### Agents (2)

- Table with toggle capability
- Details panel on Enter
- Filter on /

### Modes (3)

- Behavioral mode list
- Toggle activation
- Details panel

### Rules (4)

- Execution rules with categories
- Toggle activation
- Enabled rules live in `rules/`; disabling moves them to `inactive/rules/`
- Details panel

### Skills (5)

- Installed skills with metrics
- Validation (v), Metrics (m), Community (c)
- Token savings and usage stats

### Workflows (6)

- Workflow list with progress bars
- Status indicators and elapsed time
- Step-by-step tracking

### Orchestrate (7)

- Parallel execution dashboard
- Workstream layout diagram
- Agent task table with progress
- Parallel efficiency metrics

### Profile (8)

- Available profiles (built-in + saved)
- Apply, save, delete operations
- Type indicators (built-in vs saved)

### Export (9)

- Export options with checkboxes
- Format selector (JSON/XML/Markdown)
- Preview of export content

### Help (?)

- Comprehensive keyboard reference
- View-specific key hints
- Context-aware shortcuts

---

## Navigation Quick Reference

```
VIEWS:      1=Overview, 2=Agents, 3=Modes, 4=Rules
            p=Principles, 5=Skills, 6=Workflows, 7=Orchestrate
            8=Profile, 9=Export

MOVEMENT:   ↑/k=Up, ↓/j=Down
            PgUp=Page Up, PgDn=Page Down
            Home=Top, End=Bottom

ACTIONS:    Space=Toggle, Enter=Details
            /=Filter, Esc=Cancel
            ?=Help, r=Refresh, q=Quit

CONTEXT:    Agents: v=validate
            Skills: v=validate, m=metrics, c=community
```

---

## Code Structure

### Main Files

```
claude_ctx_py/
├── tui.py                    # Primary Rich-based TUI (1951 lines)
├── tui_extensions.py         # Mixins for profile/export/wizard (500 lines)
├── tui_textual.py            # Experimental Textual TUI (300 lines)
└── cli.py                    # CLI interface
```

### View Methods Pattern

All views follow similar structure:

```
create_[view]_table()          # Main data table
create_[view]_details_panel()  # Details panel (if applicable)
render_[view]_view()           # Complete view (for custom layouts)
```

### State Management

```
ViewState           # Per-view state (selected, filter, show_details)
TUIState            # Global state (current_view, agents, status)
Mixins              # ProfileViewMixin, ExportViewMixin, WizardViewMixin
```

---

## Priority Enhancement Recommendations

### Phase 1: Theme System (Highest Priority)

- Decouple styling from code
- Enable user customization
- Support dark/light modes
- Improve accessibility
- **Effort**: Medium | **Impact**: High

### Phase 2: Visual Polish (High Priority)

- Status icons (✓, ✗, ▶, ⏳)
- Colored progress bars
- Better date formatting
- Number abbreviations (1M tokens)
- **Effort**: Low | **Impact**: Medium

### Phase 3: Interactive Features (Medium Priority)

- Modal dialogs
- Loading spinners
- Tree views for hierarchies
- Confirmation prompts
- **Effort**: Medium | **Impact**: Medium

### Phase 4-5: Information Architecture & Visualizations (Lower Priority)

- Sidebar navigation
- Breadcrumbs
- Tabs
- Dependency graphs
- Heatmaps
- Timelines
- **Effort**: High | **Impact**: Medium-Low

---

## Testing Recommendations

### Visual Testing

- [ ] Screenshot comparisons across themes
- [ ] Terminal sizes: 80x24, 120x30, 200x50
- [ ] Color modes: 256-color, truecolor
- [ ] Unicode character support

### Accessibility Testing

- [ ] High contrast theme
- [ ] Keyboard-only navigation
- [ ] Screen reader compatibility
- [ ] Reduce motion mode

### Performance Testing

- [ ] Rendering speed: goal <100ms
- [ ] Memory usage stability
- [ ] File I/O optimization
- [ ] Caching effectiveness

---

## File Locations

### Documentation

- `/TUI_EXPLORATION_SUMMARY.md` - This overview
- `/TUI_VISUAL_ANALYSIS.md` - Detailed component analysis
- `/TUI_ENHANCEMENT_ROADMAP.md` - Implementation guide

### Code

- `/claude_ctx_py/tui.py` - Main implementation
- `/claude_ctx_py/tui_extensions.py` - View mixins
- `/claude_ctx_py/tui_textual.py` - Alternative framework

---

## Getting Started with Enhancement

### For Quick Wins (2-4 hours)

1. Read TUI_ENHANCEMENT_ROADMAP.md - "Quick Wins" section
2. Add status icons to status indicators
3. Implement colored progress bars
4. Add better date/number formatting
5. Test with different terminal themes

### For Theme System (1 week)

1. Read TUI_ENHANCEMENT_ROADMAP.md - "Phase 1" section
2. Design theme JSON format
3. Create theme loader module
4. Extract colors from tui.py
5. Create default/dark/light/accessible themes
6. Update all views to use theme
7. Test across different terminal configurations

### For Complete Enhancement (3-4 months)

1. Follow all phases in TUI_ENHANCEMENT_ROADMAP.md
2. Implement parallel workstreams for testing
3. Create comprehensive test suite
4. Build user documentation
5. Gather feedback and iterate

---

## Notes for Developers

### Color Usage Pattern

Most views follow this pattern:

```python
# Data column
style="cyan"

# Headers
header_style="bold magenta"

# Status (context-dependent)
status_style = "bold green" if active else "yellow"

# Selected row
row_style = "reverse" if is_selected else None
```

### Quick Theme Overrides (CSS-only)

You can override the default TUI palette without touching Python by supplying a
custom Textual `.tcss` file. The override loads after `styles.tcss` so it can
redefine variables like `$primary`, `$accent`, `$surface`, etc.

**Options (highest priority first):**

1. `cortex tui --theme /path/to/theme.tcss`
2. `CORTEX_TUI_THEME=/path/to/theme.tcss`
3. `~/.cortex/tui/theme.tcss` (or `$CLAUDE_PLUGIN_ROOT/tui/theme.tcss`)

**Example override:**

```tcss
$primary: #22c55e;
$accent: #f97316;
$surface: #0b1020;
$surface-lighten-1: #111827;
$surface-lighten-2: #1f2937;
$text: #f9fafb;
$text-muted: #94a3b8;
```

Note: This is a quick override only; hard-coded Rich markup colors in Python
remain unchanged until a full theme system is added.

### Table Pattern

All data tables follow similar structure:

```python
table = Table(
    title="View Name",
    show_header=True,
    header_style="bold magenta",
    show_lines=False,
    expand=True,
)

table.add_column("", width=2)              # Selector
table.add_column("Name", style="cyan")     # Primary data
table.add_column("Status", width=10)       # Status
# ... more columns
table.add_column("Desc", overflow="fold")  # Last column wraps
```

### Special Characters Reference

- Selection: `>`
- Steps: `→` (current), `✓` (done), `○` (pending)
- Progress: `█` (filled), `░` (empty)
- Dividers: `━`, `─`, `═`
- Connection: `●`

---

## Performance Notes

### Current Bottlenecks

- Full-screen refresh on state change
- File I/O on view load (agents, modes, rules, skills)
- Repeated metadata parsing
- No caching

### Optimization Opportunities

- Cache agents/modes/rules between renders
- Use Rich Live for incremental updates
- Lazy load large lists
- Profile rendering with benchmarks
- Implement virtual scrolling

---

## Next Steps

1. **Read** TUI_EXPLORATION_SUMMARY.md (5 min)
2. **Review** TUI_VISUAL_ANALYSIS.md (20 min)
3. **Assess** TUI_ENHANCEMENT_ROADMAP.md (15 min)
4. **Choose** one enhancement phase from roadmap
5. **Implement** using guidelines from analysis documents
6. **Test** with recommendations from roadmap
7. **Iterate** based on feedback

---

## Questions & Support

For questions about:

- **Current implementation**: See TUI_VISUAL_ANALYSIS.md
- **Enhancement ideas**: See TUI_ENHANCEMENT_ROADMAP.md
- **Code structure**: See claude_ctx_py/tui.py
- **Visual design**: See color/component sections in analysis
- **Performance**: See performance characteristics in exploration summary

---

Last Updated: November 3, 2025
Exploration Thoroughness: Medium
Total Documentation: 3 files, ~20,000 words
