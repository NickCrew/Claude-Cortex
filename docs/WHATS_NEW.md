# What's New in Cortex

## 2025-12-28: Multi-Reviewer Auto-Activation & TUI Review Grouping

### ✅ Multi-Reviewer Auto-Activation

- AI recommendations now trigger **multiple reviewer agents at once** based on the change set.
- Always-on reviewers: `quality-engineer` + `code-reviewer` for any non-empty changeset.
- Specialized reviewers: `typescript-pro`, `react-specialist`, `ui-ux-designer`, `database-optimizer`, `sql-pro`, `performance-engineer`, `architect-review` (as applicable).

### 🧭 TUI AI Assistant Improvements

- The AI Assistant view now groups recommendations into **Review Requests** vs **Other Suggestions** for faster scanning.
- AUTO badges remain, but review requests are clearly labeled as review actions.

### 🎨 Quick TUI Theme Overrides

- Add a custom `.tcss` file via `cortex tui --theme`, `CORTEX_TUI_THEME`, or `~/.cortex/tui/theme.tcss`.
- Overrides load after the default theme, so palette variables can be swapped without code changes.

### 🧩 Principles Snippets (Option A)

- `PRINCIPLES.md` can now be generated from modular snippets in `principles/`.
- New CLI: `cortex principles list|status|activate|deactivate|build`.
- Activation is tracked in `.active-principles`, with filename ordering (use numeric prefixes).
- TUI support: press `p` for the Principles view; use `Space` to toggle snippets, `c` to rebuild, and `d` to open `PRINCIPLES.md`.

## 2025-12-31: Command Palette & Memory Vault Overhaul

### 🚀 Expanded Command Palette (Ctrl+P)

- Added **20+ new commands** covering every major view (Galaxy, Flags, Tasks, Watch Mode, etc.).
- Commands are now organized into logical categories: `AGENT`, `MODE`, `RULE`, `VIEW`, `CONFIG`, `TOOLS`, `SYSTEM`.
- Search results now display visual hotkey reminders, making the palette a great way to learn shortcuts.

### 🧠 TUI Memory Vault Viewer

- New dedicated **Memory Screen** (`M` or `Ctrl+P` -> "Memory") with split-pane browsing.
- **Real-time search**: Filter notes instantly by title or content.
- **Markdown viewer**: Read note content directly in the TUI without opening an external editor.

### 📦 Asset Manager Polish

- **Keyboard Shortcuts**: Added `i` for "Install All" in the Bulk Install dialog.
- **Button Hints**: Updated all modal buttons to explicitly show their hotkeys (e.g., "Install [i]", "Close [esc]").
- **Confirm Dialogs**: Added visible `[y]/[n]` hints to confirmation prompts.

## 2025-11-18: Task Log Streaming & Palette Hardening

### 🔍 Task Detail Panel + Log Actions

- The Tasks view now surfaces every workstream with inline summaries and a detail modal (`s`) that shows raw notes, timestamps, and the source log path.
- Two new shortcuts ship with the view: `L` tails the underlying `agent-*.jsonl` file inside the TUI log viewer, and `O` opens the same file via `open`/`xdg-open`/`start` so you can keep digging in your native editor.
- Docs updated: [Entity guide](guides/tui/tui-entity-guide.html) and [keyboard reference](guides/tui/tui-keyboard-reference.html) call out the new workflow, and the screenshots section now has placeholders for Tasks view details.

### 🎛 Command Palette Reliability

- Ctrl+P previously threw `NoActiveWorker` in edge cases (e.g., when other modals were open). The palette now launches on its own worker, so you can summon it repeatedly while logs stream or tasks refresh.
- The [Command Palette Guide](guides/COMMAND_PALETTE_GUIDE.html) has been refreshed to note the stability fix and reiterate the quick actions you can stack while workflows run.

## 2025-11-11: Major Enhancement - Three-Layer System & Visual Documentation

### 🎨 New Behavioral Modes (4 added)

Modes change HOW Claude operates:

1. **Brainstorm Mode** - Collaborative discovery through Socratic dialogue
   - Activates: `--brainstorm` or keywords like "maybe", "not sure"
   - Use for: Vague requirements, exploration, requirement gathering

2. **Deep Analysis Mode** - Maximum-depth reasoning (~32K tokens)
   - Activates: `--ultrathink`, `--think-hard`, or `--think`
   - Use for: Complex debugging, architecture decisions, system redesign

3. **Quality Focus Mode** - Enhanced quality enforcement (8/10, 90% coverage)
   - Activates: `--focus quality`, `--validate`, or `--safe-mode`
   - Use for: Production code, security-critical features

4. **Token Efficient Mode** - Symbol-enhanced communication (30-50% reduction)
   - Activates: `--uc` or auto-activates at 75% context usage
   - Use for: Large operations, cost optimization

**Total Modes**: Now 8 behavioral modes

### 🔄 New Workflows (5 added)

Multi-step processes with agent coordination:

1. **Refactoring** - Safe, incremental code refactoring (10 steps)
   - Modes: Deep_Analysis, Parallel_Orchestration, Quality_Focus
   - Features: Impact assessment, continuous testing, quality gates

2. **API Design** - End-to-end API design and implementation (15 steps)
   - Modes: Brainstorm, Deep_Analysis, Parallel_Orchestration
   - Produces: OpenAPI spec, mock API, implementation, tests, SDKs

3. **Technical Debt Reduction** - Quarterly debt cleanup (13 steps)
   - Modes: Deep_Analysis, Quality_Focus
   - Features: Debt inventory, prioritization, prevention plan

4. **Architecture Review** - Comprehensive assessment (15 steps)
   - Mode: Deep_Analysis
   - Features: Quality/performance/security/scalability assessment

5. **Developer Onboarding** - 4-week onboarding program (17 steps)
   - Modes: Brainstorm, Deep_Analysis, Task_Management
   - Milestones: Day 1, Week 1, Week 2, Week 4 checkpoints

**Total Workflows**: Now 9 multi-step workflows

### 🎯 New Slash Commands (7 added)

Quick-action commands across 3 new namespaces:

**New Namespaces**:

- `/refactor:*` - Code refactoring operations
- `/workflow:*` - Workflow execution
- `/mode:*` - Mode management

**Commands**:

1. `/refactor:analyze` - Analyze code for refactoring opportunities
2. `/refactor:execute` - Execute refactoring plan safely
3. `/workflow:run` - Execute multi-step workflows
4. `/mode:activate` - Manually activate behavioral modes
5. `/docs:diagrams` - View architecture diagrams

**Total Commands**: Now 43 commands across 16 namespaces

### 📐 Architecture Documentation (NEW!)

Comprehensive visual documentation ships with the plugin:

**Files Included**:

1. **architecture-diagrams.md** (15K)
   - 10+ Mermaid diagrams
   - System architecture, flows, decision trees
   - Compatibility matrix

2. **quick-reference.md** (9.4K)
   - One-page cheat sheet
   - Command/mode/workflow tables
   - Integration patterns

3. **VISUAL_SUMMARY.txt** (7.2K)
   - Beautiful ASCII art diagram
   - Terminal-friendly display
   - Quick overview

4. **DIAGRAMS_README.md** (8.1K)
   - How to use diagrams
   - Reading guide with symbols/colors
   - Update checklist

**Installation**:

- Automatically installs to `~/.cortex/docs/`
- Included in package distribution
- View via `/docs:diagrams` command

**Quick View**:

```bash
cat ~/.cortex/docs/VISUAL_SUMMARY.txt
```

### 🏗️ System Architecture

The three-layer automation system:

```
Layer 1: USER COMMANDS (43 commands, 16 namespaces)
         → What to do
         Examples: /refactor:analyze, /workflow:run

Layer 2: BEHAVIORAL MODES (8 modes)
         → How to operate
         Examples: Brainstorm, Deep_Analysis, Quality_Focus

Layer 3: WORKFLOWS (9 multi-step processes)
         → Step-by-step execution
         Examples: feature-development, refactoring, api-design

Layer 4: EXECUTION (Agents + MCP + Tools)
         → Coordinates specialized agents and tools
```

### 📊 System Statistics

- **43** Slash Commands (up from 36)
- **16** Command Namespaces (up from 13)
- **8** Behavioral Modes (up from 4)
- **9** Multi-step Workflows (up from 4)
- **25+** Specialized Agents
- **3** MCP Servers (Codanna, Context7, Sequential)

### 🎯 New Integration Patterns

**Example: Refactoring Flow**

```
User: /refactor:analyze src/auth
  ↓
Command activates: Deep_Analysis + Quality_Focus modes
  ↓
Triggers: Refactoring workflow (steps 1-3)
  ↓
Uses: code-reviewer agent + Codanna MCP
  ↓
Output: Refactoring plan with priorities
```

### 🛠️ Installation Changes

**New Files Installed**:

- `~/.cortex/docs/architecture-diagrams.md`
- `~/.cortex/docs/quick-reference.md`
- `~/.cortex/docs/VISUAL_SUMMARY.txt`
- `~/.cortex/docs/DIAGRAMS_README.md`

**New Scripts**:

- `scripts/deprecated/post-install-docs.sh` - Auto-installs documentation
- Updated `scripts/deprecated/install.sh` - Calls post-install script

**Package Configuration**:

- `pyproject.toml` - Includes docs in package data
- `MANIFEST.in` - Ensures docs in distribution

### 📚 Documentation Improvements

**New Sections in docs/README.md**:

- Architecture Documentation section (top of page)
- Links to all diagram files
- Quick view commands

**New Directory Structure**:

```
docs/
├── reference/
│   └── architecture/
│       ├── architecture-diagrams.md
│       ├── quick-reference.md
│       ├── VISUAL_SUMMARY.txt
│       ├── DIAGRAMS_README.md
│       └── README.md
```

### 🚀 Usage Examples

**View Documentation**:

```bash
# ASCII art overview
cat ~/.cortex/docs/VISUAL_SUMMARY.txt

# Via command
/docs:diagrams
/docs:diagrams quick
/docs:diagrams full
```

**Activate Modes**:

```bash
/mode:activate Brainstorm              # Collaborative discovery
/mode:activate Deep_Analysis           # Maximum reasoning
/mode:activate Quality_Focus           # Enhanced quality
```

**Run Workflows**:

```bash
/workflow:run refactoring              # Safe refactoring
/workflow:run api-design               # API design
/workflow:run technical-debt           # Quarterly cleanup
```

**Execute Refactoring**:

```bash
/refactor:analyze src/auth             # Analyze for opportunities
/refactor:execute refactor-plan.md     # Execute safely
```

### 🎨 Visual Enhancements

**Color-Coded Diagrams**:

- Light Blue - User/Input
- Light Red - Commands
- Light Orange - Modes
- Light Green - Workflows
- Light Purple - Agents/Tools
- Green - Success states
- Red - Error states

**Diagram Types**:

- System architecture (graph)
- Sequence diagrams (flows)
- Flowcharts (decisions)
- Pie charts (statistics)
- Compatibility matrices

### 📖 Learning Resources

**For New Users**:

1. View `VISUAL_SUMMARY.txt` for overview
2. Read `quick-reference.md` for patterns
3. Study `architecture-diagrams.md` for details

**For Developers**:

- Keep `quick-reference.md` open for command lookup
- Use TUI (press 3 for Modes, 6 for Workflows)
- Reference integration patterns

**For Architects**:

- Present `architecture-diagrams.md` in reviews
- Use compatibility matrix for planning
- Reference decision trees

### 🔧 Maintenance

**Updating Documentation**:

```bash
# Edit source files
vim docs/reference/architecture/architecture-diagrams.md

# Reinstall to update ~/.cortex/docs/
just install
# or
bash scripts/deprecated/post-install-docs.sh
```

**Adding New Components**:

- Update component counts in VISUAL_SUMMARY.txt
- Add to tables in quick-reference.md
- Update diagrams in architecture-diagrams.md
- Follow update checklist in DIAGRAMS_README.md

### 🎯 What's Next

Planned features:

- More slash commands for common tasks
- Additional workflows for specialized scenarios
- More behavioral modes for different contexts
- Enhanced diagram interactivity
- Video tutorials using diagrams

---

## Previous Updates

### 2025-11-08: TUI Enhancements

- Enhanced visual interface
- Keyboard shortcuts
- Entity guides

### 2025-11-05: Scenario Management

- Scenario definitions
- Progress tracking
- Status monitoring

---

*For full changelog, see git commit history*
*For architecture details, see docs/reference/architecture/*
