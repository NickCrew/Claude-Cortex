# TUI Asset Manager Implementation Plan

## Overview

Add an Asset Manager view to the TUI that allows users to:
1. Discover available assets from the plugin
2. Find `.claude` directories (local and global)
3. Install/uninstall assets to chosen locations
4. View installation status and diff conflicts

## Current State Analysis

### TUI Architecture
- **Pattern**: Single-screen app with view switching via `ContentSwitcher`
- **Views**: Rendered in `DataTable`, switched via reactive `current_view` variable
- **Entry Point**: `/claude_ctx_py/tui/main.py` (~3700 lines)
- **Styling**: TCSS (`styles.tcss`) + Rich markup for dynamic content
- **Dialogs**: `ModalScreen` subclasses in `tui_dialogs.py`

### Available Assets to Manage

| Category | Count | Location | Install Target |
|----------|-------|----------|----------------|
| Hooks | 3 | `hooks/examples/` | `~/.claude/hooks/` |
| Commands | 49 | `commands/` | `~/.claude/commands/` |
| Agents | 9 | `agents/` | `~/.claude/agents/` |
| Skills | 50+ | `skills/` | `~/.claude/skills/` |
| Modes | 4 | `modes/` | `~/.claude/modes/` |
| Workflows | 4 | `workflows/` | `~/.claude/workflows/` |

### Metadata Sources
- **Hooks**: README + inline comments
- **Commands**: YAML frontmatter (name, description, category)
- **Agents**: YAML frontmatter (summary, description, tier, category)
- **Skills**: YAML frontmatter in SKILL.md + versions.yaml
- **Modes**: Markdown structure (Purpose section)
- **Workflows**: YAML (name, description, version)

---

## Implementation Plan

### Phase 1: Core Infrastructure

#### 1.1 Asset Discovery Module
**File**: `claude_ctx_py/core/asset_discovery.py`

```python
# Data structures
@dataclass
class Asset:
    name: str
    category: str  # hooks, commands, agents, skills, modes, workflows
    source_path: Path
    description: str
    version: Optional[str]
    dependencies: List[str]
    metadata: dict

@dataclass
class ClaudeDir:
    path: Path
    scope: str  # "project", "parent", "global"
    installed_assets: Dict[str, List[str]]  # category -> [names]

# Functions
def discover_plugin_assets() -> Dict[str, List[Asset]]
def find_claude_directories(start_path: Path) -> List[ClaudeDir]
def get_installed_assets(claude_dir: Path) -> Dict[str, List[str]]
def check_installation_status(asset: Asset, claude_dir: Path) -> InstallStatus
```

**InstallStatus enum**:
- `NOT_INSTALLED` - Asset not present
- `INSTALLED_SAME` - Installed, matches source
- `INSTALLED_DIFFERENT` - Installed, differs from source
- `INSTALLED_NEWER` - Installed version is newer
- `INSTALLED_OLDER` - Installed version is older

#### 1.2 Asset Installer Module
**File**: `claude_ctx_py/core/asset_installer.py`

```python
def install_asset(asset: Asset, target_dir: Path) -> Tuple[int, str]
def uninstall_asset(category: str, name: str, target_dir: Path) -> Tuple[int, str]
def get_asset_diff(asset: Asset, installed_path: Path) -> str
def bulk_install(assets: List[Asset], target_dir: Path) -> List[Tuple[Asset, int, str]]
```

**Installation logic by category**:
- **Hooks**: Copy to `hooks/`, add to settings.json if not present
- **Commands**: Copy to `commands/<namespace>/`
- **Agents**: Copy to `agents/` (active or inactive based on user choice)
- **Skills**: Copy entire skill directory to `skills/`
- **Modes**: Copy to `modes/`
- **Workflows**: Copy to `workflows/`

---

### Phase 2: TUI Views

#### 2.1 Asset Manager View (Main View)
**View key**: `A` (for Assets)
**View name**: `assets`

**Table Columns**:
| Column | Width | Content |
|--------|-------|---------|
| Category | 12 | hooks/commands/agents/etc |
| Name | 30 | Asset name |
| Status | 15 | ● Installed / ○ Available / ⚠ Differs |
| Description | 40+ | Truncated description |

**Actions**:
- `Enter` - Open asset detail dialog
- `i` - Install selected asset
- `u` - Uninstall selected asset
- `d` - Show diff (if installed differs)
- `t` - Change target directory
- `c` - Filter by category
- `I` - Bulk install category

**View Rendering Pattern**:
```python
def show_assets_view(self, table: AnyDataTable) -> None:
    table.add_column("Category", key="category", width=12)
    table.add_column("Name", key="name", width=30)
    table.add_column("Status", key="status", width=15)
    table.add_column("Description", key="description")

    # Group by category or flat list based on filter
    for asset in self.available_assets:
        status = self._get_install_status(asset)
        status_text = self._format_status(status)
        # ...
```

#### 2.2 Target Selector Dialog
**Type**: `ModalScreen`

Show discovered `.claude` directories with radio selection:
```
┌─ Select Installation Target ─────────────────┐
│                                              │
│  ◉ ~/.claude (global)                        │
│  ○ ./project/.claude (project)               │
│  ○ ../parent/.claude (parent project)        │
│                                              │
│  [Select]  [Cancel]                          │
└──────────────────────────────────────────────┘
```

#### 2.3 Asset Detail Dialog
**Type**: `ModalScreen`

Show full asset details:
```
┌─ Asset: code-reviewer ───────────────────────┐
│                                              │
│  Category: agents                            │
│  Version: 2.0                                │
│  Status: ⚠ Installed (differs from source)  │
│                                              │
│  Description:                                │
│  Expert code review specialist with deep     │
│  expertise in security, performance...       │
│                                              │
│  Dependencies:                               │
│  • debugger (agent)                          │
│  • security-auditor (agent)                  │
│                                              │
│  [Install]  [View Diff]  [Close]             │
└──────────────────────────────────────────────┘
```

#### 2.4 Diff Viewer Dialog
**Type**: `ModalScreen` with scrollable content

Show unified diff between source and installed:
```
┌─ Diff: code-reviewer.md ─────────────────────┐
│  --- installed                               │
│  +++ source                                  │
│  @@ -5,7 +5,8 @@                             │
│   summary: "Senior reviewer..."              │
│  -tier: standard                             │
│  +tier: core                                 │
│  +priority: critical                         │
│                                              │
│  [Apply Update]  [Keep Installed]  [Close]   │
└──────────────────────────────────────────────┘
```

---

### Phase 3: Memory Vault Browser (Bonus)

#### 3.1 Memory View
**View key**: `M` (for Memory)
**View name**: `memory`

**Table Columns**:
| Column | Width | Content |
|--------|-------|---------|
| Type | 12 | knowledge/projects/sessions/fixes |
| Title | 35 | Note title |
| Modified | 12 | Date or "5m ago" |
| Tags | 20+ | #tag1 #tag2 |

**Actions**:
- `Enter` - View note content
- `s` - Search notes
- `/` - Quick search
- `d` - Delete note (with confirm)
- `n` - New note (opens prompt)

---

### Phase 4: Integration

#### 4.1 Constants Updates
**File**: `claude_ctx_py/tui/constants.py`

```python
PRIMARY_VIEW_BINDINGS = [
    # ... existing ...
    ("a", "assets", "Assets"),
    ("m", "memory", "Memory"),
]

VIEW_TITLES = {
    # ... existing ...
    "assets": "📦 Asset Manager",
    "memory": "🧠 Memory Vault",
}
```

#### 4.2 Types Updates
**File**: `claude_ctx_py/tui/types.py`

```python
@dataclass
class AssetInfo:
    name: str
    category: str
    source_path: str
    description: str
    status: str  # "installed", "available", "differs"
    version: Optional[str] = None

@dataclass
class MemoryNote:
    title: str
    note_type: str
    path: str
    modified: datetime
    tags: List[str]
    snippet: str
```

#### 4.3 Main TUI Updates
**File**: `claude_ctx_py/tui/main.py`

Add:
- `load_assets()` - Load available assets
- `load_memory_notes()` - Load memory vault
- `show_assets_view()` - Render assets table
- `show_memory_view()` - Render memory table
- `action_install_asset()` - Install handler
- `action_view_asset_detail()` - Detail dialog
- Action handlers for all new keybindings

---

## File Structure

```
claude_ctx_py/
├── core/
│   ├── asset_discovery.py    # NEW: Asset discovery
│   └── asset_installer.py    # NEW: Install/uninstall logic
├── memory/                   # EXISTING: Memory module
│   └── ...
└── tui/
    ├── main.py               # UPDATE: Add views
    ├── constants.py          # UPDATE: Add bindings
    ├── types.py              # UPDATE: Add types
    ├── styles.tcss           # UPDATE: Add styles
    └── dialogs/              # NEW: Asset dialogs
        ├── __init__.py
        ├── target_selector.py
        ├── asset_detail.py
        └── diff_viewer.py
```

---

## Implementation Order

### Sprint 1: Core Infrastructure (Day 1)
1. [ ] Create `asset_discovery.py` with:
   - `Asset` dataclass
   - `discover_plugin_assets()` for each category
   - `find_claude_directories()`
   - `get_installed_assets()`
   - `check_installation_status()`

2. [ ] Create `asset_installer.py` with:
   - `install_asset()`
   - `uninstall_asset()`
   - `get_asset_diff()`

3. [ ] Unit tests for discovery and install

### Sprint 2: TUI Asset View (Day 2)
4. [ ] Add Asset view to TUI:
   - Add bindings in `constants.py`
   - Add types in `types.py`
   - Add `load_assets()` method
   - Add `show_assets_view()` method
   - Wire up in `update_view()`

5. [ ] Create Target Selector dialog

6. [ ] Create Asset Detail dialog

### Sprint 3: Install Actions (Day 3)
7. [ ] Implement install action:
   - `action_install_asset()`
   - Progress/confirmation dialogs
   - Refresh after install

8. [ ] Implement uninstall action

9. [ ] Implement diff viewer dialog

10. [ ] Implement bulk install

### Sprint 4: Memory View (Day 4)
11. [ ] Add Memory view to TUI:
    - Integrate with existing `memory` module
    - Add `show_memory_view()`
    - Note viewer dialog

12. [ ] Add memory actions:
    - Search
    - Delete with confirm
    - New note

### Sprint 5: Polish (Day 5)
13. [ ] Add styles for new views
14. [ ] Add to command palette
15. [ ] Integration testing
16. [ ] Documentation

---

## UI Mockups

### Assets View
```
╭─ 📦 Asset Manager ───────────────────────────────────────────────────────────╮
│ Target: ~/.claude (global)                                    [t] change     │
├──────────────────────────────────────────────────────────────────────────────┤
│ Category     │ Name                           │ Status        │ Description  │
├──────────────┼────────────────────────────────┼───────────────┼──────────────┤
│ hooks        │ 📎 implementation-quality-gate │ ● Installed   │ Quality ga...│
│ hooks        │ 📎 skill_auto_suggester        │ ● Installed   │ Auto-sugge...│
│ hooks        │ 📎 memory_auto_capture         │ ● Installed   │ Auto-captu...│
│ commands     │ 📝 analyze:code                │ ○ Available   │ Comprehens...│
│ commands     │ 📝 analyze:security-scan       │ ○ Available   │ Security v...│
│ commands     │ 📝 dev:test                    │ ⚠ Differs     │ Execute te...│
│ agents       │ 🤖 code-reviewer               │ ● Installed   │ Senior rev...│
│ agents       │ 🤖 debugger                    │ ○ Available   │ Expert deb...│
│ skills       │ 🎯 api-design-patterns         │ ○ Available   │ REST and G...│
╰──────────────────────────────────────────────────────────────────────────────╯
 [i]Install [u]Uninstall [d]Diff [Enter]Details [c]Category [I]Bulk Install
```

### Memory View
```
╭─ 🧠 Memory Vault ────────────────────────────────────────────────────────────╮
│ Vault: ~/basic-memory                                         [/] search    │
├──────────────────────────────────────────────────────────────────────────────┤
│ Type         │ Title                          │ Modified      │ Tags         │
├──────────────┼────────────────────────────────┼───────────────┼──────────────┤
│ knowledge    │ 📚 threatx-gateway             │ 2h ago        │ #knowledge   │
│ projects     │ 📁 waf-gauntlet                │ 2h ago        │ #project     │
│ sessions     │ 📅 2025-11-30-memory-system    │ 1h ago        │ #session     │
│ fixes        │ 🔧 docker-arm64-fix            │ 3d ago        │ #fix #docker │
╰──────────────────────────────────────────────────────────────────────────────╯
 [Enter]View [s]Search [n]New [d]Delete [r]Refresh
```

---

## Key Technical Decisions

1. **Plugin Source Detection**
   - Use `__file__` to find plugin installation path
   - Or check `CLAUDE_PLUGIN_ROOT` env var
   - Fallback to package resources

2. **Claude Directory Detection**
   - Walk up from cwd looking for `.claude/`
   - Always include `~/.claude` as global
   - Prefer `CLAUDE_PLUGIN_ROOT` when running as a plugin

3. **Diff Implementation**
   - Use `difflib.unified_diff` from stdlib
   - Show in scrollable dialog
   - Highlight additions/deletions with Rich markup

4. **Settings.json Updates for Hooks**
   - Parse existing settings.json
   - Merge new hook configuration
   - Preserve existing hooks/settings

5. **Installation Atomicity**
   - Copy to temp location first
   - Move atomically on success
   - Rollback on failure

---

## Acceptance Criteria

- [ ] Users can see all available assets from plugin
- [ ] Users can see which assets are installed
- [ ] Users can select installation target (.claude directory)
- [ ] Users can install individual assets
- [ ] Users can bulk install by category
- [ ] Users can uninstall assets
- [ ] Users can view diffs when installed differs from source
- [ ] Users can browse memory vault
- [ ] Users can search memory notes
- [ ] Users can view note contents
- [ ] All actions have keyboard shortcuts
- [ ] Views integrate with existing TUI navigation

---

## Dependencies

- Existing: `difflib` (stdlib)
- Existing: Textual framework
- Existing: `memory` module
- New: None required

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Large asset list overwhelming | Category filtering, search |
| Settings.json corruption | Backup before modify, atomic writes |
| Path resolution edge cases | Extensive path normalization, tests |
| TUI main.py too large | Extract dialogs to separate module |
