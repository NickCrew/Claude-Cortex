# Cortex: Master Architecture Document

**Version**: 1.1  
**Last Updated**: 2025-12-05  
**Status**: Living Document  
**Recent Updates**: Component Toggle System, Doctor Diagnostics, TUI Refactoring

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [System Overview](#system-overview)
3. [Architectural Principles](#architectural-principles)
4. [Core Subsystems](#core-subsystems)
   - [4.1 CLI Layer](#41-cli-layer)
   - [4.2 TUI Layer](#42-tui-layer)
   - [4.3 Intelligence System](#43-intelligence-system)
   - [4.4 Memory Vault](#44-memory-vault)
   - [4.5 Core Business Logic](#45-core-business-logic)
   - [4.6 Skills System](#46-skills-system)
   - [4.7 MCP Integration](#47-mcp-integration)
   - [4.8 Component Toggle System](#48-component-toggle-system)
   - [4.9 Doctor Diagnostic System](#49-doctor-diagnostic-system)
   - [4.10 Data Layer](#410-data-layer)
5. [Data Models and Formats](#data-models-and-formats)
6. [Component Interactions](#component-interactions)
7. [Key Workflows](#key-workflows)
8. [Technology Stack](#technology-stack)
9. [Performance Architecture](#performance-architecture)
10. [Security Architecture](#security-architecture)
11. [Extension Points](#extension-points)
12. [Deployment Architecture](#deployment-architecture)
13. [Troubleshooting Guide](#troubleshooting-guide)
14. [Appendices](#appendices)

---

## 1. Executive Summary

### 1.1 Purpose

The Cortex is a **comprehensive context management and intelligent automation system** for Claude Code. It provides developers with a framework to organize, activate, and intelligently manage agents, modes, rules, skills, and workflows through both command-line (CLI) and terminal user interface (TUI) interactions.

### 1.2 Key Capabilities

**Context Management**

- Organize agents, modes, rules, and skills as reusable markdown components
- Dependency-aware activation and deactivation
- Profile-based configuration for different project types

**Intelligent Automation**

- AI-powered agent recommendations based on file changes and patterns
- Pattern learning from successful sessions
- Auto-activation of high-confidence agents (≥80%)
- Real-time watch mode for continuous monitoring

**Interactive Experience**

- Rich terminal UI with 9 specialized views
- Command palette with fuzzy search
- Real-time notifications and status updates
- Keyboard-driven navigation

**Persistent Memory**

- Knowledge vault for domain knowledge, gotchas, and fixes
- Session capture and replay
- Auto-capture hooks for seamless workflow integration

**Integration & Extensibility**

- MCP (Model Context Protocol) server management
- Skill rating and analytics system
- Profile and scenario templates
- Community skill sharing

### 1.3 Target Users

**Primary Audience**: Software developers using Claude Code for daily development tasks

**User Personas**:

- **Solo Developer**: Quick context switching, productivity automation
- **Team Lead**: Standard profiles, team conventions, quality gates
- **DevOps Engineer**: Infrastructure-as-code workflows, deployment automation
- **Security Engineer**: Security audit workflows, compliance checking
- **Documentation Writer**: Technical writing modes, style guides

### 1.4 System Scale

```
70 Python modules
~10,000 lines of production code
74 agent definitions
50+ skill definitions
20+ modes and profiles
9 TUI views
30+ CLI commands
SQLite + JSON + Markdown data stores
```

---

## 2. System Overview

### 2.1 Conceptual Architecture

The system follows a **layered architecture** with clear separation of concerns:

```
┌──────────────────────────────────────────────────────────────────┐
│                        Presentation Layer                         │
│  ┌────────────────┐                    ┌─────────────────────┐   │
│  │   CLI Layer    │                    │     TUI Layer       │   │
│  │  (cli.py)      │                    │  (tui/main.py)      │   │
│  │                │                    │                     │   │
│  │ • argparse     │                    │ • Textual framework │   │
│  │ • Commands     │                    │ • 9 views           │   │
│  │ • Workflows    │                    │ • Command palette   │   │
│  └───────┬────────┘                    └──────────┬──────────┘   │
└──────────┼──────────────────────────────────────┼───────────────┘
           │                                       │
           │         ┌─────────────────────────────┘
           │         │
           ▼         ▼
┌──────────────────────────────────────────────────────────────────┐
│                      Intelligence Layer                           │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  intelligence.py                                           │  │
│  │  ┌──────────────┬─────────────┬────────────┬────────────┐ │  │
│  │  │SessionContext│PatternLearner│Recommender│AutoActivator│ │  │
│  │  └──────────────┴─────────────┴────────────┴────────────┘ │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  skill_recommender.py                                      │  │
│  │  • Pattern-based skill suggestions                         │  │
│  │  • Feedback loop integration                               │  │
│  └────────────────────────────────────────────────────────────┘  │
└──────────────────────┬────────────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────────┐
│                     Core Business Logic Layer                     │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────────┐   │
│  │ agents   │ skills   │  modes   │  rules   │  profiles    │   │
│  │  .py     │  .py     │  .py     │  .py     │  .py         │   │
│  ├──────────┼──────────┼──────────┼──────────┼──────────────┤   │
│  │workflows │   mcp    │  memory  │components│   doctor     │   │
│  │  .py     │  .py     │ (module) │  .py     │   .py        │   │
│  └──────────┴──────────┴──────────┴──────────┴──────────────┘   │
└──────────────────────┬────────────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────────┐
│                          Data Layer                               │
│  ┌────────────────┬───────────────┬──────────────────────────┐   │
│  │ File System    │ SQLite DB     │ JSON State               │   │
│  │                │               │                          │   │
│  │ ~/.claude/     │ skill-        │ metrics/, sessions/      │   │
│  │ • CLAUDE.md    │ ratings.db    │ • activity.json          │   │
│  │ • modes/       │               │ • patterns.json          │   │
│  │ • agents/      │ memory vault  │ • recommendations.json   │   │
│  │ • skills/      │ ~/basic-      │                          │   │
│  │ • rules/       │ memory/       │                          │   │
│  └────────────────┴───────────────┴──────────────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
```

### 2.2 Design Philosophy

**Simplicity First**

- Human-readable markdown configuration
- No daemons or background services
- File-based state management
- Opt-in complexity

**Progressive Enhancement**

- Start with basic agent activation
- Add intelligence when ready
- Enable watch mode for automation
- Adopt memory vault for persistence

**User in Control**

- Explicit actions by default
- Auto-activation only for high-confidence (≥80%)
- Easy disable of automation features
- Transparent decision-making

**Extensibility by Design**

- Plugin architecture for agents/modes/skills
- Markdown-based component definitions
- Hook system for custom integrations
- Open for community contributions

---

## 3. Architectural Principles

### 3.1 Separation of Concerns

**UI Layer** (`cli.py`, `tui/main.py`)

- ✅ **Responsible for**: User interaction, input validation, output formatting
- ❌ **Not responsible for**: Business logic, file I/O, data persistence

**Intelligence Layer** (`intelligence.py`, `skill_recommender.py`)

- ✅ **Responsible for**: Context analysis, pattern matching, recommendations
- ❌ **Not responsible for**: UI rendering, direct file manipulation

**Core Business Logic** (`core/` modules)

- ✅ **Responsible for**: Component management, validation, CRUD operations
- ❌ **Not responsible for**: UI concerns, intelligence algorithms

**Data Layer** (file system, SQLite)

- ✅ **Responsible for**: Persistence, retrieval, schema management
- ❌ **Not responsible for**: Business rules, presentation logic

### 3.2 Dependency Injection

All core modules accept directory paths as constructor parameters:

```python
# ✅ Good: Testable, configurable
class AgentManager:
    def __init__(self, agents_dir: Path, inactive_dir: Path):
        self.agents_dir = agents_dir
        self.inactive_dir = inactive_dir

# ❌ Bad: Hard-coded, untestable
class AgentManager:
    def __init__(self):
        self.agents_dir = Path.home() / ".claude" / "agents"
```

**Benefits**:

- Easy unit testing with temp directories
- Support for multiple environments (dev, test, prod)
- Plugin sandbox isolation

### 3.3 Plugin Architecture

Components are **data, not code**:

```markdown
---
name: security-auditor
description: Security vulnerability assessment
dependencies:
  - code-reviewer
priority: high
auto_activate: true
triggers:
  - pattern: "**/auth/**/*.py"
  - context: "auth"
---

# Security Auditor

[Agent description and behavior...]
```

**Advantages**:

- Add agents without code changes
- Easy community sharing (just markdown files)
- Version control friendly
- Non-programmers can create agents

### 3.4 Event-Driven TUI

The TUI uses Textual's reactive properties for state management:

```python
class AgentsView(Screen):
    active_agents: Reactive[List[str]] = Reactive([])
    
    def watch_active_agents(self, new_value: List[str]) -> None:
        """Called automatically when active_agents changes."""
        self.refresh_table()
```

**Benefits**:

- No manual polling
- Efficient updates (only changed components re-render)
- Clean separation of state and presentation

### 3.5 Fail-Safe Defaults

**Conservative Automation**:

- Auto-activation OFF by default in interactive mode
- Requires explicit opt-in for watch mode
- High threshold (80%) for auto-activation
- Easy to disable with `--no-auto-activate`

**Graceful Degradation**:

- Missing dependencies → warning, continue with available
- Parse errors → skip file, log error, continue
- Network errors (MCP) → cached data, offline mode
- SQLite locked → retry with backoff, fallback to JSON

### 3.6 Zero-Configuration Intelligence

AI features work out-of-the-box:

- No training required
- Uses rule-based heuristics initially
- Learns from usage over time
- Improves recommendations automatically

---

## 4. Core Subsystems

### 4.1 CLI Layer

**Location**: `claude_ctx_py/cli.py` (main entry point)

#### Architecture

The CLI uses Python's `argparse` for command routing with a hierarchical subcommand structure:

```
cortex
├── mode (subcommand)
│   ├── list
│   ├── activate <name>
│   ├── deactivate <name>
│   └── info <name>
├── agent (subcommand)
│   ├── list [--active]
│   ├── activate <name>
│   ├── deactivate <name>
│   ├── deps <name>
│   └── graph
├── skill (subcommand)
│   ├── list
│   ├── info <name>
│   ├── rate <name> --stars <1-5>
│   └── analytics
├── ai (subcommand)
│   ├── recommend
│   ├── auto-activate
│   ├── watch
│   └── record-success
├── memory (subcommand)
│   ├── list [type]
│   ├── remember <fact>
│   ├── capture <summary>
│   └── search <query>
├── workflow (subcommand)
│   └── run <workflow-name>
├── mcp (subcommand)
│   ├── list
│   ├── docs <server>
│   └── diagnose
└── tui
```

#### Command Processing Flow

```python
def main() -> int:
    """Main CLI entry point."""
    # 1. Parse arguments
    parser = create_parser()
    args = parser.parse_args()
    
    # 2. Initialize core modules
    claude_dir = _resolve_claude_dir()
    agents_mgr = AgentManager(claude_dir / "agents")
    modes_mgr = ModeManager(claude_dir / "modes")
    
    # 3. Route to appropriate handler
    if args.command == "agent":
        return handle_agent_command(args, agents_mgr)
    elif args.command == "mode":
        return handle_mode_command(args, modes_mgr)
    # ...
    
    return 0
```

#### Output Formatting

The CLI uses **Rich** library for terminal formatting:

```python
from rich.console import Console
from rich.table import Table

console = Console()

# Rich tables for list commands
table = Table(title="Active Agents")
table.add_column("Name", style="cyan")
table.add_column("Dependencies", style="yellow")
for agent in active_agents:
    table.add_row(agent.name, ", ".join(agent.deps))
console.print(table)

# Colored output for status
console.print("[green]✓[/green] Agent activated")
console.print("[red]✗[/red] Agent not found")
```

#### Shell Completion

The CLI includes built-in shell completion generation:

```bash
# Generate completions
cortex completion bash > ~/.bash_completion.d/cortex
cortex completion zsh > ~/.zsh/completions/_cortex
cortex completion fish > ~/.config/fish/completions/cortex.fish

# Show installation instructions
cortex completion bash --install
```

**Implementation**:

- Uses `argcomplete` library for intelligent completion
- Completes subcommands, flags, and arguments
- Dynamic completion for agent/mode/skill names

#### Error Handling

The CLI follows Unix conventions:

```python
# Exit codes
EXIT_SUCCESS = 0
EXIT_ERROR = 1
EXIT_USAGE_ERROR = 2

# Error patterns
try:
    result = agent_activate(name)
except AgentNotFoundError as e:
    console.print(f"[red]Error:[/red] {e}", err=True)
    return EXIT_ERROR
except DependencyMissingError as e:
    console.print(f"[yellow]Warning:[/yellow] {e}", err=True)
    # Continue with partial activation
    return EXIT_SUCCESS
```

---

### 4.2 TUI Layer

**Location**: `claude_ctx_py/tui/` package

#### TUI Architecture

The TUI is built on **Textual**, a reactive TUI framework. It follows a single-page application pattern with view switching:

```
tui/
├── main.py              # Main app, view coordinator (230KB consolidated)
├── styles.tcss          # Textual CSS styling definitions
├── types.py             # Type definitions and constants
├── constants.py         # Global constants
├── widgets.py           # Custom widget implementations
├── screens/             # Screen/view definitions
│   ├── agents.py        # Agents view (key 0)
│   ├── modes.py         # Modes view (key 1)
│   ├── rules.py         # Rules view (key 2)
│   ├── skills.py        # Skills view (key 3)
│   ├── workflows.py     # Workflows view (key 4)
│   ├── scenarios.py     # Scenarios view (key 5)
│   ├── profiles.py      # Profiles view (key 6)
│   ├── mcp.py           # MCP servers view (key 7)
│   ├── ai_assistant.py  # AI assistant view (key 8)
│   └── memory.py        # Memory vault view (key m)
├── widgets/             # Reusable widget components
│   ├── data_table.py    # Enhanced data table
│   ├── status_bar.py    # Status bar component
│   └── notification.py  # Toast notifications
├── dialogs/             # Modal dialog components
│   ├── rating.py        # Skill rating dialog
│   ├── confirm.py       # Confirmation dialog
│   └── input.py         # Text input dialog
└── layouts/             # Layout components
    └── command_palette.py
```

**Key Improvements** (Recent Refactoring):

- **Package Structure**: Proper Python package with `__init__.py`
- **Centralized Main**: `main.py` consolidated from 1,000+ LOC scattered file
- **TCSS Styling**: External CSS-like styling for maintainability
- **Type Safety**: Dedicated `types.py` for type definitions
- **Modular Widgets**: Reusable components in dedicated directories

#### View Lifecycle

Each view follows a consistent lifecycle:

```python
class AgentsView(Screen):
    """Agents management view (key: 0)."""
    
    def __init__(self):
        super().__init__()
        self.agents_mgr = None  # Injected on mount
    
    async def on_mount(self) -> None:
        """Called when view is mounted."""
        # 1. Inject dependencies
        self.agents_mgr = self.app.agents_mgr
        
        # 2. Load data
        await self.load_agents()
        
        # 3. Setup UI
        self.setup_table()
        
        # 4. Start refresh timer (optional)
        self.set_interval(5.0, self.refresh_data)
    
    async def load_agents(self) -> None:
        """Load agents from core module."""
        self.agents = await self.agents_mgr.list_all()
        self.active = await self.agents_mgr.list_active()
    
    def on_key(self, event: events.Key) -> None:
        """Handle key presses."""
        if event.key == "enter":
            await self.activate_selected()
        elif event.key == "d":
            await self.deactivate_selected()
        elif event.key == "i":
            await self.show_info()
```

#### Command Palette

The command palette provides fuzzy search across all TUI commands:

**Trigger**: `Ctrl+P`

**Features**:

- Fuzzy matching on command names
- Real-time filtering
- Keyboard navigation
- Quick action execution

**Implementation**:

```python
class CommandPalette(Container):
    """Command palette for fuzzy search."""
    
    commands = [
        ("Agent: List All", "agents_list"),
        ("Agent: Activate", "agents_activate"),
        ("Mode: List", "modes_list"),
        ("AI: Recommend", "ai_recommend"),
        ("Skill: Rate", "skills_rate"),
        # ... 50+ commands
    ]
    
    def on_input_changed(self, event: Input.Changed) -> None:
        """Filter commands as user types."""
        query = event.value.lower()
        matches = fuzzy_match(query, self.commands)
        self.update_results(matches)
```

#### Keyboard Navigation

The TUI is fully keyboard-driven:

**Global Keys**:

- `0-8`: Switch to view
- `m`: Memory vault view
- `Ctrl+P`: Command palette
- `Ctrl+C`, `q`: Quit
- `?`: Help overlay
- `r`: Refresh current view

**View-Specific Keys**:

- `↑`, `↓`: Navigate table rows
- `Enter`: Activate/select item
- `Space`: Toggle selection
- `d`: Deactivate/disable
- `i`: Show info/details
- `e`: Edit (if applicable)
- `/`: Search within view

**Agent View (0)**:

- `a`: Activate agent
- `d`: Deactivate agent
- `g`: Show dependency graph
- `x`: Export active agents

**Skills View (3)**:

- `Ctrl+R`: Rate selected skill
- `v`: View skill details
- `f`: Filter by category

**AI Assistant View (8)**:

- `A`: Auto-activate recommendations
- `R`: Refresh recommendations

#### TUI State Management

The TUI uses Textual's reactive properties for state:

```python
class ClaudeCtxApp(App):
    """Main TUI application."""
    
    # Reactive properties
    active_agents: Reactive[List[str]] = Reactive([])
    active_modes: Reactive[List[str]] = Reactive([])
    current_view: Reactive[str] = Reactive("agents")
    notifications: Reactive[List[Notification]] = Reactive([])
    
    def watch_active_agents(self, new_value: List[str]) -> None:
        """React to agent changes."""
        self.notify(f"{len(new_value)} agents active")
        self.refresh_views()
    
    def watch_notifications(self, new_value: List[Notification]) -> None:
        """Show toast notifications."""
        for notif in new_value:
            self.show_toast(notif.message, notif.level)
```

#### TUI Styling

Styles are defined in TCSS (Textual CSS):

```tcss
/* tui/styles.tcss */

AgentsView {
    layout: grid;
    grid-size: 2;
    grid-columns: 1fr 3fr;
}

DataTable {
    height: 100%;
    border: solid $accent;
}

DataTable:focus {
    border: solid $accent-darken-2;
}

StatusBar {
    dock: bottom;
    height: 1;
    background: $primary;
    color: $text;
}
```

---

### 4.3 Intelligence System

**Location**: `claude_ctx_py/intelligence.py`

The Intelligence System is the **brain** of cortex—it analyzes context, learns patterns, and makes recommendations.

#### Core Components

**1. SessionContext**

Captures the current development context:

```python
@dataclass
class SessionContext:
    """Represents current session state for intelligent decisions."""
    
    # File context
    files_changed: List[str]
    file_types: Set[str]
    directories: Set[str]
    
    # Code context (detected patterns)
    has_tests: bool
    has_auth: bool
    has_api: bool
    has_frontend: bool
    has_backend: bool
    has_database: bool
    
    # Activity context
    errors_count: int
    test_failures: int
    build_failures: int
    
    # Time context
    session_start: datetime
    last_activity: datetime
    
    # Current state
    active_agents: List[str]
    active_modes: List[str]
    active_rules: List[str]
```

**Detection Logic**:

```python
class ContextDetector:
    """Detects context from file changes and git diff."""
    
    def detect_context(self, files: List[str]) -> SessionContext:
        """Build context from changed files."""
        context = SessionContext(
            files_changed=files,
            file_types=self._extract_file_types(files),
            directories=self._extract_directories(files),
            has_tests=self._has_test_files(files),
            has_auth=self._has_auth_code(files),
            has_api=self._has_api_code(files),
            has_frontend=self._has_frontend_code(files),
            has_backend=self._has_backend_code(files),
            has_database=self._has_database_code(files),
            # ... more detection logic
        )
        return context
    
    def _has_auth_code(self, files: List[str]) -> bool:
        """Detect auth-related code."""
        patterns = [
            r'auth',
            r'login',
            r'password',
            r'token',
            r'jwt',
            r'session',
            r'security',
        ]
        return any(
            any(re.search(pat, f, re.IGNORECASE) for pat in patterns)
            for f in files
        )
```

**2. PatternLearner**

Learns from successful sessions:

```python
class PatternLearner:
    """Learns patterns from session history."""
    
    def __init__(self, history_file: Path):
        self.history_file = history_file
        self.patterns: Dict[str, List[Dict]] = defaultdict(list)
        self._load_history()
    
    def record_success(
        self,
        context: SessionContext,
        agents_used: List[str],
        duration: int,
        outcome: str
    ) -> None:
        """Record successful session for learning."""
        session_data = {
            "timestamp": datetime.now().isoformat(),
            "context": context.to_dict(),
            "agents": agents_used,
            "duration": duration,
            "outcome": outcome,
        }
        
        # Store by context key
        context_key = self._generate_context_key(context)
        self.patterns[context_key].append(session_data)
        
        # Persist to disk
        self._save_history()
    
    def predict_agents(
        self,
        context: SessionContext
    ) -> List[AgentRecommendation]:
        """Predict agents based on learned patterns."""
        context_key = self._generate_context_key(context)
        historical = self.patterns.get(context_key, [])
        
        # Count agent usage in similar contexts
        agent_counts = Counter()
        for session in historical:
            for agent in session["agents"]:
                agent_counts[agent] += 1
        
        # Generate recommendations
        total = len(historical)
        recommendations = []
        for agent, count in agent_counts.most_common():
            confidence = count / total if total > 0 else 0.0
            if confidence >= 0.3:  # Minimum threshold
                recommendations.append(AgentRecommendation(
                    agent_name=agent,
                    confidence=confidence,
                    reason=f"Used in {count}/{total} similar sessions",
                    urgency="medium",
                    auto_activate=(confidence >= 0.8),
                    context_triggers=[context_key],
                ))
        
        return recommendations
```

**3. Intelligent Recommender**

Combines rule-based and pattern-based recommendations:

```python
class IntelligentAgent:
    """Main intelligence orchestrator."""
    
    def __init__(self, claude_dir: Path):
        self.claude_dir = claude_dir
        self.detector = ContextDetector()
        self.learner = PatternLearner(
            claude_dir / "data" / "patterns.json"
        )
    
    def recommend_agents(
        self,
        context: SessionContext
    ) -> List[AgentRecommendation]:
        """Generate agent recommendations."""
        recommendations = []
        
        # 1. Rule-based recommendations (hard-coded intelligence)
        recommendations.extend(self._rule_based_recommendations(context))
        
        # 2. Pattern-based recommendations (learned intelligence)
        recommendations.extend(self.learner.predict_agents(context))
        
        # 3. Deduplicate and merge scores
        merged = self._merge_recommendations(recommendations)
        
        # 4. Sort by confidence
        merged.sort(key=lambda r: r.confidence, reverse=True)
        
        return merged
    
    def _rule_based_recommendations(
        self,
        context: SessionContext
    ) -> List[AgentRecommendation]:
        """Hard-coded intelligence rules."""
        recommendations = []
        
        # Auth code → security-auditor
        if context.has_auth:
            recommendations.append(AgentRecommendation(
                agent_name="security-auditor",
                confidence=0.95,
                reason="Auth code detected",
                urgency="critical",
                auto_activate=True,
                context_triggers=["auth"],
            ))
        
        # Test failures → test-automator
        if context.test_failures > 0:
            recommendations.append(AgentRecommendation(
                agent_name="test-automator",
                confidence=0.95,
                reason=f"{context.test_failures} test failures",
                urgency="critical",
                auto_activate=True,
                context_triggers=["test_failures"],
            ))
        
        # Large changeset → code-reviewer
        if len(context.files_changed) >= 8:
            recommendations.append(AgentRecommendation(
                agent_name="code-reviewer",
                confidence=0.85,
                reason=f"{len(context.files_changed)} files changed",
                urgency="high",
                auto_activate=False,
                context_triggers=["large_changeset"],
            ))
        
        # Database changes → performance-engineer
        if context.has_database:
            recommendations.append(AgentRecommendation(
                agent_name="performance-engineer",
                confidence=0.70,
                reason="Database changes detected",
                urgency="medium",
                auto_activate=False,
                context_triggers=["database"],
            ))
        
        return recommendations
```

#### Auto-Activation Logic

Auto-activation happens when:

1. **Confidence ≥ 80%** (rule-based or pattern-based)
2. **Urgency is "critical" or "high"**
3. **User has not disabled auto-activation**

```python
def auto_activate(
    self,
    recommendations: List[AgentRecommendation],
    dry_run: bool = False
) -> List[str]:
    """Auto-activate high-confidence agents."""
    activated = []
    
    for rec in recommendations:
        if rec.auto_activate and rec.confidence >= 0.8:
            if not dry_run:
                agent_activate(rec.agent_name)
            activated.append(rec.agent_name)
    
    return activated
```

#### Watch Mode

Watch mode monitors the file system and triggers recommendations in real-time:

```python
class WatchMode:
    """Real-time monitoring and auto-activation."""
    
    def __init__(
        self,
        claude_dir: Path,
        interval: float = 2.0,
        auto_activate: bool = True,
        threshold: float = 0.7
    ):
        self.claude_dir = claude_dir
        self.interval = interval
        self.auto_activate_enabled = auto_activate
        self.threshold = threshold
        self.intelligence = IntelligentAgent(claude_dir)
        self.last_git_head = None
    
    async def run(self) -> None:
        """Main watch loop."""
        console.print("🤖 AI WATCH MODE - Real-time Intelligence")
        console.print(f"  Auto-activate: {'ON' if self.auto_activate_enabled else 'OFF'}")
        console.print(f"  Threshold: {self.threshold:.0%} confidence")
        console.print(f"  Check interval: {self.interval}s")
        console.print()
        
        stats = {"checks": 0, "recommendations": 0, "activations": 0}
        start_time = datetime.now()
        
        try:
            while True:
                await asyncio.sleep(self.interval)
                stats["checks"] += 1
                
                # Check for git changes
                current_head = self._get_git_head()
                if current_head != self.last_git_head:
                    console.print(f"[{self._timestamp()}] 📝 Git commit detected")
                    self.last_git_head = current_head
                
                # Detect context
                changed_files = self._get_changed_files()
                if not changed_files:
                    continue
                
                context = self.intelligence.detector.detect_context(changed_files)
                
                # Get recommendations
                recommendations = self.intelligence.recommend_agents(context)
                filtered = [r for r in recommendations if r.confidence >= self.threshold]
                
                if filtered:
                    stats["recommendations"] += len(filtered)
                    self._display_recommendations(context, filtered)
                    
                    # Auto-activate if enabled
                    if self.auto_activate_enabled:
                        activated = self.intelligence.auto_activate(filtered)
                        if activated:
                            stats["activations"] += len(activated)
                            console.print(f"[{self._timestamp()}] ⚡ Auto-activating {len(activated)} agents...")
                            for agent in activated:
                                console.print(f"     ✓ {agent}")
        
        except KeyboardInterrupt:
            self._display_stats(start_time, stats)
```

---

### 4.4 Memory Vault

**Location**: `claude_ctx_py/memory/` package

The Memory Vault provides **persistent knowledge storage** for Claude Code sessions.

#### Architecture

```
memory/
├── config.py        # Configuration management
├── notes.py         # Note CRUD operations
├── capture.py       # Session capture
├── search.py        # Full-text search
└── templates.py     # Note templates
```

#### Note Types

The vault organizes notes into four categories:

```python
class NoteType(Enum):
    """Note categories."""
    KNOWLEDGE = "knowledge"  # 📚 Domain knowledge, gotchas
    PROJECTS = "projects"    # 📁 Project context
    SESSIONS = "sessions"    # 📅 Session summaries
    FIXES = "fixes"          # 🔧 Bug fixes, solutions
```

#### Directory Structure

```
~/basic-memory/
├── knowledge/
│   ├── python-asyncio-gotchas.md
│   ├── kubernetes-networking-guide.md
│   └── sql-optimization-tips.md
├── projects/
│   ├── ecommerce-platform-context.md
│   └── mobile-app-architecture.md
├── sessions/
│   ├── 2025-12-01-auth-implementation.md
│   ├── 2025-12-02-api-refactoring.md
│   └── 2025-12-03-bug-fixes.md
└── fixes/
    ├── memory-leak-fix.md
    ├── race-condition-solution.md
    └── cors-policy-fix.md
```

#### Note Format

Notes use Markdown with YAML frontmatter:

```markdown
# Stream Processor Delay Investigation

tags: #knowledge #debugging #performance
created: 2025-12-01T10:30:00Z
updated: 2025-12-01T14:45:00Z

## Context

Investigation into 500ms delays in the stream processing pipeline.

## Root Cause

The delay was caused by synchronous database queries blocking the event loop.

## Solution

Replaced `psycopg2` with `asyncpg` for async database operations:

\`\`\`python
# Before
conn = psycopg2.connect(DSN)
cursor = conn.execute("SELECT * FROM events")

# After
conn = await asyncpg.connect(DSN)
rows = await conn.fetch("SELECT * FROM events")
\`\`\`

## Results

- Latency reduced from 500ms to 50ms (90% improvement)
- Throughput increased from 200/s to 2000/s (10x)

## Lessons Learned

- Always use async database drivers in async Python code
- Profile before optimizing
- Monitor event loop blocking

## Related

- [[python-async-patterns]]
- [[database-performance-guide]]
```

#### Core Operations

**Note Creation**:

```python
class NoteManager:
    """Manages memory vault notes."""
    
    def __init__(self, vault_path: Path):
        self.vault_path = vault_path
    
    def create_note(
        self,
        note_type: NoteType,
        title: str,
        content: str,
        tags: Optional[List[str]] = None
    ) -> Path:
        """Create a new note."""
        # Generate slug from title
        slug = self._slugify(title)
        
        # Determine file path
        note_dir = self.vault_path / note_type.value
        note_dir.mkdir(parents=True, exist_ok=True)
        note_path = note_dir / f"{slug}.md"
        
        # Build frontmatter
        frontmatter = {
            "created": datetime.now().isoformat(),
            "updated": datetime.now().isoformat(),
        }
        if tags:
            frontmatter["tags"] = tags
        
        # Write note
        full_content = self._format_note(title, frontmatter, content)
        note_path.write_text(full_content, encoding="utf-8")
        
        return note_path
```

**Auto-Capture**:

The vault can automatically capture session summaries:

```python
class SessionCapture:
    """Automatic session capture."""
    
    def __init__(self, vault_path: Path, config: Dict[str, Any]):
        self.vault_path = vault_path
        self.config = config
        self.note_mgr = NoteManager(vault_path)
    
    def should_capture(self, session: Dict[str, Any]) -> bool:
        """Determine if session should be captured."""
        # Check minimum duration
        min_duration = self.config.get("min_session_length", 5)
        if session["duration_minutes"] < min_duration:
            return False
        
        # Check exclude patterns
        exclude = self.config.get("exclude_patterns", [])
        query = session.get("query", "").lower()
        if any(pat in query for pat in exclude):
            return False
        
        return True
    
    def capture_session(self, session: Dict[str, Any]) -> Optional[Path]:
        """Capture session summary."""
        if not self.should_capture(session):
            return None
        
        # Generate summary
        title = self._generate_title(session)
        content = self._generate_content(session)
        tags = self._extract_tags(session)
        
        # Create note
        return self.note_mgr.create_note(
            NoteType.SESSIONS,
            title,
            content,
            tags
        )
```

**Search**:

Full-text search across all notes:

```python
class NoteSearch:
    """Search memory vault notes."""
    
    def search(
        self,
        query: str,
        note_type: Optional[NoteType] = None,
        limit: int = 10
    ) -> List[SearchResult]:
        """Search notes by content and metadata."""
        results = []
        
        # Search directories
        search_dirs = [self.vault_path / note_type.value] if note_type else \
                      [self.vault_path / t.value for t in NoteType]
        
        for dir_path in search_dirs:
            if not dir_path.exists():
                continue
            
            for note_path in dir_path.glob("*.md"):
                # Load note
                content = note_path.read_text(encoding="utf-8")
                frontmatter, body = self._parse_note(content)
                
                # Calculate relevance score
                score = self._score_relevance(query, frontmatter, body)
                
                if score > 0:
                    results.append(SearchResult(
                        path=note_path,
                        title=frontmatter.get("title", note_path.stem),
                        score=score,
                        excerpt=self._generate_excerpt(query, body),
                        tags=frontmatter.get("tags", []),
                    ))
        
        # Sort by relevance and limit
        results.sort(key=lambda r: r.score, reverse=True)
        return results[:limit]
```

#### Configuration

**Config File**: `~/.claude/memory-config.json`

```json
{
  "vault_path": "~/basic-memory",
  "auto_capture": {
    "enabled": true,
    "min_session_length": 5,
    "exclude_patterns": [
      "explain",
      "what is",
      "how do"
    ]
  },
  "search": {
    "index_enabled": false,
    "index_path": "~/.claude/data/memory-index"
  }
}
```

#### TUI Integration

The Memory view (key: `m`) displays notes in a table:

```
┌─────────────────────────────────────────────────────────────────┐
│                          Memory Vault                            │
├─────┬────────────────────────────────────┬──────────┬───────────┤
│ Type│ Title                              │ Modified │ Tags      │
├─────┼────────────────────────────────────┼──────────┼───────────┤
│ 📚  │ Python Asyncio Gotchas             │ 2d ago   │ #python   │
│ 📁  │ E-commerce Platform Context        │ 1w ago   │ #project  │
│ 📅  │ 2025-12-01 Auth Implementation     │ 4d ago   │ #session  │
│ 🔧  │ Memory Leak Fix                    │ 3d ago   │ #bugfix   │
└─────┴────────────────────────────────────┴──────────┴───────────┘

Keys: Enter=View | e=Edit | d=Delete | n=New | /=Search | r=Refresh
```

---

### 4.5 Core Business Logic

**Location**: `claude_ctx_py/core/` package

The core business logic is organized into specialized modules, each responsible for a specific domain.

#### 4.5.1 Agents Module (`core/agents.py`)

Manages Claude subagents with dependency resolution.

**Key Functions**:

```python
def agent_list(
    agents_dir: Path,
    inactive_dir: Path,
    active_only: bool = False
) -> List[Agent]:
    """List available agents."""
    agents = []
    
    # Scan active directory
    for path in _iter_md_files(agents_dir):
        agent = _parse_agent(path)
        agents.append(agent)
    
    # Scan inactive directory (if not active_only)
    if not active_only:
        for path in _iter_md_files(inactive_dir):
            agent = _parse_agent(path)
            agent.active = False
            agents.append(agent)
    
    return sorted(agents, key=lambda a: a.name)

def agent_activate(
    agent_name: str,
    claude_dir: Path,
    auto_deps: bool = True
) -> Tuple[List[str], List[str]]:
    """Activate an agent and its dependencies.
    
    Returns:
        (activated_agents, missing_dependencies)
    """
    # Find agent file
    agent_path = _find_agent(agent_name, claude_dir)
    if not agent_path:
        raise AgentNotFoundError(f"Agent '{agent_name}' not found")
    
    # Parse agent metadata
    agent = _parse_agent(agent_path)
    
    # Build dependency graph
    dep_graph = _build_dependency_graph(agent, claude_dir)
    
    # Topological sort for activation order
    activation_order = _topological_sort(dep_graph)
    
    activated = []
    missing = []
    
    for dep_name in activation_order:
        dep_path = _find_agent(dep_name, claude_dir)
        if not dep_path:
            missing.append(dep_name)
            continue
        
        # Activate by updating CLAUDE.md
        _update_claude_md(claude_dir, dep_name, activate=True)
        activated.append(dep_name)
    
    return activated, missing

def agent_graph(
    agents_dir: Path,
    inactive_dir: Path,
    format: str = "text"
) -> str:
    """Generate dependency graph visualization.
    
    Args:
        format: "text", "mermaid", or "dot"
    """
    agents = agent_list(agents_dir, inactive_dir)
    
    if format == "mermaid":
        return _generate_mermaid_graph(agents)
    elif format == "dot":
        return _generate_dot_graph(agents)
    else:
        return _generate_text_graph(agents)
```

**Dependency Resolution**:

```python
def _build_dependency_graph(
    agent: Agent,
    claude_dir: Path
) -> Dict[str, Set[str]]:
    """Build dependency graph using DFS."""
    graph: Dict[str, Set[str]] = defaultdict(set)
    visited: Set[str] = set()
    
    def visit(name: str) -> None:
        if name in visited:
            return
        visited.add(name)
        
        agent_path = _find_agent(name, claude_dir)
        if not agent_path:
            return
        
        agent_obj = _parse_agent(agent_path)
        for dep in agent_obj.dependencies:
            graph[name].add(dep)
            visit(dep)
    
    visit(agent.name)
    return graph

def _topological_sort(graph: Dict[str, Set[str]]) -> List[str]:
    """Topological sort for activation order."""
    in_degree = {node: 0 for node in graph}
    for node in graph:
        for neighbor in graph[node]:
            in_degree[neighbor] = in_degree.get(neighbor, 0) + 1
    
    queue = [node for node, degree in in_degree.items() if degree == 0]
    result = []
    
    while queue:
        node = queue.pop(0)
        result.append(node)
        for neighbor in graph.get(node, []):
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
    
    return result
```

#### 4.5.2 Skills Module (`core/skills.py`)

Manages reusable skills with ratings and analytics.

**Skill Discovery**:

```python
def skill_list(
    skills_dir: Path,
    category: Optional[str] = None
) -> List[Skill]:
    """List available skills."""
    skills = []
    
    for path in skills_dir.glob("**/*.md"):
        if _is_disabled(path):
            continue
        
        skill = _parse_skill(path)
        
        if category and skill.category != category:
            continue
        
        skills.append(skill)
    
    return sorted(skills, key=lambda s: s.name)
```

**Skill Rating**:

```python
def skill_rate(
    skill_name: str,
    stars: int,
    review: Optional[str] = None,
    db_path: Path
) -> None:
    """Rate a skill (1-5 stars)."""
    if not 1 <= stars <= 5:
        raise ValueError("Stars must be 1-5")
    
    with sqlite3.connect(db_path) as conn:
        conn.execute("""
            INSERT INTO ratings (skill_name, stars, review, timestamp)
            VALUES (?, ?, ?, ?)
        """, (skill_name, stars, review, datetime.now().isoformat()))

def skill_analytics(db_path: Path) -> Dict[str, Any]:
    """Get skill analytics."""
    with sqlite3.connect(db_path) as conn:
        # Average ratings
        avg_ratings = dict(conn.execute("""
            SELECT skill_name, AVG(stars) as avg_rating
            FROM ratings
            GROUP BY skill_name
        """))
        
        # Rating distribution
        distribution = dict(conn.execute("""
            SELECT skill_name, stars, COUNT(*) as count
            FROM ratings
            GROUP BY skill_name, stars
        """))
        
        # Top rated skills
        top_rated = list(conn.execute("""
            SELECT skill_name, AVG(stars) as avg_rating, COUNT(*) as num_ratings
            FROM ratings
            GROUP BY skill_name
            HAVING num_ratings >= 3
            ORDER BY avg_rating DESC
            LIMIT 10
        """))
    
    return {
        "average_ratings": avg_ratings,
        "distribution": distribution,
        "top_rated": top_rated,
    }
```

#### 4.5.3 Modes Module (`core/modes.py`)

Manages behavioral modes with intelligent activation.

**Mode Operations**:

```python
def mode_activate(
    mode_name: str,
    claude_dir: Path,
    exclusive: bool = False
) -> None:
    """Activate a mode.
    
    Args:
        mode_name: Mode to activate
        exclusive: If True, deactivate other modes first
    """
    # Find mode file
    mode_path = _find_mode(mode_name, claude_dir)
    if not mode_path:
        raise ModeNotFoundError(f"Mode '{mode_name}' not found")
    
    # Deactivate other modes if exclusive
    if exclusive:
        active_modes = mode_list_active(claude_dir)
        for mode in active_modes:
            mode_deactivate(mode, claude_dir)
    
    # Update CLAUDE.md
    _update_claude_md(claude_dir, mode_name, activate=True, category="modes")

def mode_smart_select(
    context: SessionContext,
    modes_dir: Path
) -> Optional[str]:
    """Intelligently select mode based on context."""
    # Load all modes
    modes = mode_list(modes_dir)
    
    # Score each mode
    scores = []
    for mode in modes:
        score = _score_mode_relevance(mode, context)
        if score > 0:
            scores.append((mode.name, score))
    
    # Return highest scoring mode
    if scores:
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[0][0]
    
    return None
```

#### 4.5.4 Workflows Module (`core/workflows.py`)

Orchestrates multi-step workflows.

**Workflow Execution**:

```python
class WorkflowRunner:
    """Executes multi-step workflows."""
    
    def __init__(self, claude_dir: Path):
        self.claude_dir = claude_dir
    
    def run_workflow(
        self,
        workflow_name: str,
        context: Optional[Dict[str, Any]] = None
    ) -> WorkflowResult:
        """Execute a workflow."""
        # Load workflow definition
        workflow = self._load_workflow(workflow_name)
        
        # Initialize state
        state = WorkflowState(
            workflow_name=workflow_name,
            current_step=0,
            context=context or {},
            start_time=datetime.now(),
        )
        
        # Execute steps
        for step in workflow.steps:
            try:
                step_result = self._execute_step(step, state)
                state.step_results.append(step_result)
                state.current_step += 1
            except StepFailedError as e:
                state.failed_step = step.name
                state.error = str(e)
                break
        
        # Build result
        return WorkflowResult(
            success=(state.failed_step is None),
            steps_completed=state.current_step,
            total_steps=len(workflow.steps),
            duration=(datetime.now() - state.start_time).total_seconds(),
            state=state,
        )
    
    def _execute_step(
        self,
        step: WorkflowStep,
        state: WorkflowState
    ) -> StepResult:
        """Execute a single workflow step."""
        if step.type == "agent_activate":
            return self._step_activate_agent(step, state)
        elif step.type == "mode_activate":
            return self._step_activate_mode(step, state)
        elif step.type == "command":
            return self._step_run_command(step, state)
        elif step.type == "wait":
            return self._step_wait(step, state)
        else:
            raise ValueError(f"Unknown step type: {step.type}")
```

---

### 4.6 Skills System

**Location**: `claude_ctx_py/core/skills.py`, `claude_ctx_py/skill_recommender.py`, `claude_ctx_py/skill_rating.py`

The Skills System provides **reusable, specialized knowledge modules** that agents can load on-demand.

#### Skills Architecture

```
Skills System
├── Skill Definitions (markdown files)
│   └── skills/
│       ├── api-design-patterns.md
│       ├── python-testing-patterns.md
│       └── ...
├── Skill Manager (core/skills.py)
│   ├── Discovery
│   ├── Validation
│   └── Loading
├── Skill Recommender (skill_recommender.py)
│   ├── Pattern-based recommendations
│   ├── Context analysis
│   └── Feedback loop
└── Skill Rating (skill_rating.py)
    ├── SQLite database
    ├── Rating analytics
    └── Auto-prompts
```

#### Skill Definition Format

```markdown
---
name: api-design-patterns
category: architecture
description: REST API design patterns and best practices
version: 1.2.0
tags: [api, rest, design, architecture]
complexity: intermediate
estimated_read_time: 15
dependencies: []
---

# API Design Patterns

## RESTful Principles

### Resource Naming
- Use nouns, not verbs
- Plural for collections: `/users`, `/products`
- Singular for specific resources: `/users/123`

### HTTP Methods
- `GET` - Retrieve resource(s)
- `POST` - Create new resource
- `PUT` - Replace entire resource
- `PATCH` - Partial update
- `DELETE` - Remove resource

## Common Patterns

### Pagination
```json
GET /users?page=2&limit=20

Response:
{
  "data": [...],
  "pagination": {
    "page": 2,
    "limit": 20,
    "total": 150,
    "pages": 8
  }
}
```

[... more patterns ...]

```

#### Skill Recommender

The skill recommender suggests relevant skills based on context:

```python
class SkillRecommender:
    """Recommends skills based on context and patterns."""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._init_database()
    
    def recommend(
        self,
        context: SessionContext,
        agent_name: Optional[str] = None,
        limit: int = 5
    ) -> List[SkillRecommendation]:
        """Generate skill recommendations."""
        recommendations = []
        
        # 1. Rule-based recommendations
        rule_recs = self._rule_based_recommendations(context)
        recommendations.extend(rule_recs)
        
        # 2. Pattern-based recommendations
        pattern_recs = self._pattern_based_recommendations(context)
        recommendations.extend(pattern_recs)
        
        # 3. Agent-specific recommendations
        if agent_name:
            agent_recs = self._agent_based_recommendations(agent_name)
            recommendations.extend(agent_recs)
        
        # 4. Deduplicate and merge scores
        merged = self._merge_recommendations(recommendations)
        
        # 5. Apply rating boost
        merged = self._apply_rating_boost(merged)
        
        # 6. Sort by confidence
        merged.sort(key=lambda r: r.confidence, reverse=True)
        
        return merged[:limit]
    
    def _rule_based_recommendations(
        self,
        context: SessionContext
    ) -> List[SkillRecommendation]:
        """Hard-coded skill recommendations."""
        recommendations = []
        
        if context.has_api:
            recommendations.append(SkillRecommendation(
                skill_name="api-design-patterns",
                confidence=0.85,
                reason="API code detected",
            ))
        
        if context.has_tests:
            recommendations.append(SkillRecommendation(
                skill_name="python-testing-patterns",
                confidence=0.80,
                reason="Test files detected",
            ))
        
        if context.has_database:
            recommendations.append(SkillRecommendation(
                skill_name="sql-optimization",
                confidence=0.75,
                reason="Database code detected",
            ))
        
        return recommendations
    
    def record_activation(
        self,
        skill_name: str,
        context: SessionContext,
        agent_name: Optional[str] = None
    ) -> None:
        """Record skill activation for learning."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO skill_activations 
                (skill_name, context_key, agent_name, timestamp)
                VALUES (?, ?, ?, ?)
            """, (
                skill_name,
                self._generate_context_key(context),
                agent_name,
                datetime.now().isoformat()
            ))
```

#### Skill Rating System

**Database Schema**:

```sql
CREATE TABLE ratings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    skill_name TEXT NOT NULL,
    stars INTEGER NOT NULL CHECK (stars >= 1 AND stars <= 5),
    review TEXT,
    helpful INTEGER DEFAULT 0,
    not_helpful INTEGER DEFAULT 0,
    timestamp TEXT NOT NULL
);

CREATE TABLE skill_activations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    skill_name TEXT NOT NULL,
    context_key TEXT NOT NULL,
    agent_name TEXT,
    timestamp TEXT NOT NULL
);

CREATE INDEX idx_ratings_skill ON ratings(skill_name);
CREATE INDEX idx_activations_skill ON skill_activations(skill_name);
```

**Rating Operations**:

```python
def rate_skill(
    skill_name: str,
    stars: int,
    review: Optional[str] = None,
    db_path: Path
) -> None:
    """Rate a skill."""
    with sqlite3.connect(db_path) as conn:
        conn.execute("""
            INSERT INTO ratings (skill_name, stars, review, timestamp)
            VALUES (?, ?, ?, ?)
        """, (skill_name, stars, review, datetime.now().isoformat()))

def get_skill_analytics(skill_name: str, db_path: Path) -> Dict[str, Any]:
    """Get analytics for a skill."""
    with sqlite3.connect(db_path) as conn:
        # Average rating
        avg = conn.execute("""
            SELECT AVG(stars) FROM ratings WHERE skill_name = ?
        """, (skill_name,)).fetchone()[0]
        
        # Rating distribution
        dist = dict(conn.execute("""
            SELECT stars, COUNT(*) FROM ratings 
            WHERE skill_name = ? 
            GROUP BY stars
        """, (skill_name,)))
        
        # Activation count
        activations = conn.execute("""
            SELECT COUNT(*) FROM skill_activations WHERE skill_name = ?
        """, (skill_name,)).fetchone()[0]
        
        # Success correlation (skills used in successful sessions)
        # (requires session outcomes table)
        
    return {
        "average_rating": avg or 0.0,
        "distribution": dist,
        "total_ratings": sum(dist.values()),
        "total_activations": activations,
    }
```

#### Auto-Prompts

The TUI shows auto-prompts for recently used skills:

```python
class SkillRatingPrompt:
    """Auto-prompt for skill ratings."""
    
    def should_prompt(
        self,
        skill_name: str,
        db_path: Path
    ) -> bool:
        """Determine if we should prompt for rating."""
        with sqlite3.connect(db_path) as conn:
            # Check recent activations
            recent = conn.execute("""
                SELECT COUNT(*) FROM skill_activations
                WHERE skill_name = ?
                AND timestamp > datetime('now', '-7 days')
            """, (skill_name,)).fetchone()[0]
            
            # Check if already rated recently
            rated = conn.execute("""
                SELECT COUNT(*) FROM ratings
                WHERE skill_name = ?
                AND timestamp > datetime('now', '-30 days')
            """, (skill_name,)).fetchone()[0]
            
            # Prompt if used 3+ times but not rated
            return recent >= 3 and rated == 0
    
    def generate_prompt(
        self,
        skill_name: str,
        db_path: Path
    ) -> str:
        """Generate prompt message."""
        with sqlite3.connect(db_path) as conn:
            # Get usage stats
            activations = conn.execute("""
                SELECT COUNT(*) FROM skill_activations
                WHERE skill_name = ?
            """, (skill_name,)).fetchone()[0]
            
            # Get context types
            contexts = list(conn.execute("""
                SELECT DISTINCT context_key FROM skill_activations
                WHERE skill_name = ?
                ORDER BY timestamp DESC
                LIMIT 3
            """, (skill_name,)))
        
        return f"""
You've used "{skill_name}" {activations} times.

Context types: {', '.join(c[0] for c in contexts)}

Would you like to rate this skill?
(This helps improve recommendations for you and the community)
"""
```

---

### 4.7 MCP Integration

**Location**: `claude_ctx_py/core/mcp.py`, `claude_ctx_py/core/mcp_registry.py`

The MCP (Model Context Protocol) Integration provides management and documentation for MCP servers.

#### MCP Architecture

```
MCP Integration
├── Server Discovery
│   ├── Parse Claude Desktop config
│   ├── Detect installed servers
│   └── Extract server metadata
├── Configuration Validation
│   ├── Schema validation
│   ├── Connection testing
│   └── Diagnostics
├── Curated Documentation
│   ├── Built-in guides
│   ├── Server-specific docs
│   └── Best practices
└── TUI View (key 7)
    ├── Server list
    ├── Status indicators
    ├── Quick actions
    └── Docs viewer
```

#### Server Discovery

```python
class MCPManager:
    """Manages MCP server integrations."""
    
    def __init__(self, claude_desktop_config: Path):
        self.config_path = claude_desktop_config
    
    def discover_servers(self) -> List[MCPServer]:
        """Discover MCP servers from Claude Desktop config."""
        # Load config
        with open(self.config_path) as f:
            config = json.load(f)
        
        servers = []
        for name, server_config in config.get("mcpServers", {}).items():
            server = MCPServer(
                name=name,
                command=server_config.get("command"),
                args=server_config.get("args", []),
                env=server_config.get("env", {}),
                installed=self._check_installed(server_config),
            )
            servers.append(server)
        
        return servers
    
    def validate_server(self, server: MCPServer) -> ValidationResult:
        """Validate server configuration."""
        issues = []
        
        # Check command exists
        command_path = shutil.which(server.command)
        if not command_path:
            issues.append(f"Command not found: {server.command}")
        
        # Check environment variables
        for env_var in server.env:
            if not os.getenv(env_var):
                issues.append(f"Environment variable not set: {env_var}")
        
        # Try to connect (if installed)
        if server.installed:
            try:
                self._test_connection(server)
            except ConnectionError as e:
                issues.append(f"Connection failed: {e}")
        
        return ValidationResult(
            valid=(len(issues) == 0),
            issues=issues,
        )
```

#### Curated Documentation

Built-in documentation for popular MCP servers:

```python
class MCPDocumentation:
    """Curated MCP server documentation."""
    
    BUILT_IN_DOCS = {
        "context7": """
# Context7 MCP Server

**Purpose**: Semantic code search and analysis

## Features
- Semantic search across codebase
- Symbol finding and references
- Impact analysis
- Call graph exploration

## Installation
```bash
npm install -g @context7/mcp-server
```

## Configuration

```json
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": ["-y", "@context7/mcp-server"],
      "env": {
        "CONTEXT7_API_KEY": "your-key"
      }
    }
  }
}
```

## Best Practices

- Use semantic_search_with_context for broad queries
- Use find_symbol for specific symbol lookups
- Use analyze_impact before making changes
""",
        "sequential-thinking": """

# Sequential Thinking MCP Server

**Purpose**: Step-by-step reasoning and complex problem solving

## Features

- Break down complex problems
- Sequential reasoning steps
- Persistent thought chains
- Progress tracking

## Installation

```bash
npm install -g @sequential/mcp-server
```

[... more docs ...]
""",
    }

    def get_docs(self, server_name: str) -> Optional[str]:
        """Get documentation for a server."""
        return self.BUILT_IN_DOCS.get(server_name)

```

#### TUI MCP View

The MCP view (key 7) provides an interactive interface:

```

┌─────────────────────────────────────────────────────────────────┐
│                         MCP Servers                              │
├────────────┬──────────┬────────────┬─────────────────────────────┤
│ Name       │ Status   │ Installed  │ Tools                       │
├────────────┼──────────┼────────────┼─────────────────────────────┤
│ context7   │ ✅ Active│ ✅ Yes     │ 5 (search, find, analyze)   │
│ sequential │ ✅ Active│ ✅ Yes     │ 3 (think, chain, resume)    │
│ playwright │ ⚠️ Config│ ❌ No      │ 0 (not installed)           │
│ serena     │ ✅ Active│ ✅ Yes     │ 8 (file ops, search)        │
└────────────┴──────────┴────────────┴─────────────────────────────┘

Keys: Enter=Docs | t=Test | c=Copy config | v=Validate | r=Refresh

```

**Actions**:
- `t`: Test server connection
- `d`: Show curated documentation
- `c`: Copy config snippet to clipboard
- `v`: Run full validation
- `i`: Install server (if NPM/pip package)

---

### 4.8 Component Toggle System

**Location**: `claude_ctx_py/core/components.py`

The Component Toggle System provides **unified management** for activating and deactivating components (modes, rules, and other CLAUDE.md references) using HTML comments.

#### Architecture

Prior to this system, each component type (modes, rules, agents) had separate activation logic. The Component Toggle System consolidates this into a single, generic mechanism.

**Unification Pattern**:
```python
# Before: Separate functions for each type
mode_activate(name)
rule_activate(name)

# After: Unified component management
component_activate(component_type="modes", name=name)
component_activate(component_type="rules", name=name)
```

#### HTML Comment-Based Activation

Components are toggled via HTML comments in CLAUDE.md:

```markdown
# Active component (visible to Claude)
@modes/Brainstorming.md

# Inactive component (commented out)
<!-- @modes/Deep_Focus.md -->
```

**Activation**: Remove HTML comment  
**Deactivation**: Add HTML comment

#### Core Functions

**Parse Components**:

```python
def parse_claude_md_components(
    claude_dir: Path,
    component_type: str
) -> Tuple[List[str], List[str]]:
    """Parse CLAUDE.md to find active and inactive components.
    
    Args:
        claude_dir: Path to Claude directory
        component_type: Type of component (e.g., "modes", "rules")
    
    Returns:
        Tuple of (active_components, inactive_components)
    """
    claude_md = claude_dir / "CLAUDE.md"
    content = claude_md.read_text(encoding="utf-8")
    
    # Active: @{type}/{Name}.md
    active_pattern = re.compile(
        rf'^@{re.escape(component_type)}/([^/]+)\\.md\\s*$',
        re.MULTILINE
    )
    # Inactive: <!-- @{type}/{Name}.md -->
    inactive_pattern = re.compile(
        rf'^<!--\\s*@{re.escape(component_type)}/([^/]+)\\.md\\s*-->',
        re.MULTILINE
    )
    
    active = active_pattern.findall(content)
    inactive = inactive_pattern.findall(content)
    
    return active, inactive
```

**Toggle Component**:

```python
def toggle_component_in_claude_md(
    claude_dir: Path,
    component_type: str,
    name: str,
    activate: bool
) -> Tuple[bool, str]:
    """Toggle a component in CLAUDE.md.
    
    Args:
        claude_dir: Path to Claude directory
        component_type: Type ("modes", "rules", etc.)
        name: Component name (without .md)
        activate: True to activate, False to deactivate
    
    Returns:
        (success, error_message)
    """
    claude_md = claude_dir / "CLAUDE.md"
    content = claude_md.read_text(encoding="utf-8")
    
    if activate:
        # Remove HTML comment
        pattern = re.compile(
            rf'^<!--\\s*@{re.escape(component_type)}/{re.escape(name)}\\.md\\s*-->',
            re.MULTILINE
        )
        replacement = f'@{component_type}/{name}.md'
        content = pattern.sub(replacement, content)
    else:
        # Add HTML comment
        pattern = re.compile(
            rf'^@{re.escape(component_type)}/{re.escape(name)}\\.md\\s*$',
            re.MULTILINE
        )
        replacement = f'<!-- @{component_type}/{name}.md -->'
        content = pattern.sub(replacement, content)
    
    _update_with_backup(claude_md, lambda _: content)
    return True, ""
```

**High-Level Interface**:

```python
def component_activate(
    component_type: str,
    name: str,
    home: Path | None = None
) -> Tuple[int, str]:
    """Activate a component.
    
    Returns:
        (exit_code, message)
    """
    claude_dir = _resolve_claude_dir(home)
    
    # Verify component file exists
    component_path = claude_dir / component_type / f"{name}.md"
    if not component_path.is_file():
        return 1, f"Component file not found: {component_type}/{name}.md"
    
    success, error = toggle_component_in_claude_md(
        claude_dir, component_type, name, activate=True
    )
    
    if success:
        return 0, f"Activated {component_type.rstrip('s')}: {name}"
    else:
        return 1, error

def component_deactivate(
    component_type: str,
    name: str,
    home: Path | None = None
) -> Tuple[int, str]:
    """Deactivate a component.
    
    Returns:
        (exit_code, message)
    """
    claude_dir = _resolve_claude_dir(home)
    
    success, error = toggle_component_in_claude_md(
        claude_dir, component_type, name, activate=False
    )
    
    if success:
        return 0, f"Deactivated {component_type.rstrip('s')}: {name}"
    else:
        return 1, error
```

#### Benefits

**1. Consistency**

- All component types use the same activation mechanism
- Predictable behavior across modes, rules, and future component types
- Easier to maintain and extend

**2. Simplicity**

- HTML comments are human-readable
- Easy to manually edit CLAUDE.md
- No separate state files to manage

**3. Backward Compatibility**

- Existing CLAUDE.md files work without migration
- Supports both active and inactive sections

**4. Extensibility**

- Easy to add new component types
- Generic implementation works for any `@{type}/{name}.md` pattern

#### Usage Examples

**CLI Usage**:

```bash
# Activate a mode
$ cortex mode activate Brainstorming

# Deactivate a rule
$ cortex rules deactivate quality-gate-rules

# List active/inactive
$ cortex mode list
```

**Programmatic Usage**:

```python
from claude_ctx_py.core.components import (
    component_activate,
    component_deactivate,
    parse_claude_md_components
)

# Activate a mode
exit_code, message = component_activate("modes", "Brainstorming")

# Parse current state
active, inactive = parse_claude_md_components(
    claude_dir, "modes"
)
print(f"Active: {active}")
print(f"Inactive: {inactive}")
```

---

### 4.9 Doctor Diagnostic System

**Location**: `claude_ctx_py/core/doctor.py`

The Doctor Diagnostic System provides **system health checks and validation** for the cortex environment.

#### Architecture

```
Doctor System
├── Consistency Checks
│   ├── Active state vs filesystem
│   ├── Reference integrity
│   └── Missing dependencies
├── Duplicate Detection
│   ├── Content hash comparison
│   ├── Identical file detection
│   └── Deduplication suggestions
├── Redundancy Analysis
│   ├── Unused resources
│   ├── Orphaned files
│   └── Cleanup recommendations
└── Optimization Checks
    ├── Large file detection
    ├── Performance bottlenecks
    └── Best practice violations
```

#### Diagnostic Categories

**1. Consistency Checks**

Validates that active components actually exist on disk:

```python
def check_consistency(claude_dir: Path) -> List[Diagnosis]:
    """Check consistency between active state and file system."""
    diagnoses = []
    
    # Active Modes
    active_modes_file = claude_dir / ".active-modes"
    if active_modes_file.exists():
        modes = _parse_active_entries(active_modes_file)
        for mode in modes:
            mode_path = claude_dir / "modes" / f"{mode}.md"
            if not mode_path.is_file():
                diagnoses.append(Diagnosis(
                    category="Consistency",
                    level="ERROR",
                    message=f"Active mode '{mode}' references missing file",
                    resource=str(mode_path),
                    suggestion=f"Run 'cortex mode deactivate {mode}'"
                ))
    
    # Active Rules
    active_rules_file = claude_dir / ".active-rules"
    if active_rules_file.exists():
        rules = _parse_active_entries(active_rules_file)
        for rule in rules:
            rule_path = claude_dir / "rules" / f"{rule}.md"
            if not rule_path.is_file():
                diagnoses.append(Diagnosis(
                    category="Consistency",
                    level="ERROR",
                    message=f"Active rule '{rule}' references missing file",
                    resource=str(rule_path),
                    suggestion=f"Run 'cortex rules deactivate {rule}'"
                ))
    
    return diagnoses
```

**2. Duplicate Detection**

Identifies identical files using MD5 hash comparison:

```python
def check_duplicates(claude_dir: Path) -> List[Diagnosis]:
    """Check for duplicate definitions."""
    diagnoses = []
    hashes: Dict[str, List[str]] = {}
    
    agents_dir = claude_dir / "agents"
    if agents_dir.exists():
        for agent_file in _iter_md_files(agents_dir):
            content = agent_file.read_bytes()
            file_hash = hashlib.md5(content).hexdigest()
            if file_hash not in hashes:
                hashes[file_hash] = []
            hashes[file_hash].append(agent_file.name)
    
    for file_hash, files in hashes.items():
        if len(files) > 1:
            diagnoses.append(Diagnosis(
                category="Duplicate",
                level="WARNING",
                message=f"Identical content found: {', '.join(files)}",
                suggestion="Delete duplicate files."
            ))
    
    return diagnoses
```

**3. Optimization Checks**

Identifies performance issues and best practice violations:

```python
def check_optimizations(claude_dir: Path) -> List[Diagnosis]:
    """Check for optimization opportunities."""
    diagnoses = []
    
    agents_dir = claude_dir / "agents"
    if agents_dir.exists():
        for agent_file in _iter_md_files(agents_dir):
            size = agent_file.stat().st_size
            if size > 10 * 1024:  # 10KB
                diagnoses.append(Diagnosis(
                    category="Optimization",
                    level="WARNING",
                    message=f"Large agent file ({size/1024:.1f}KB)",
                    resource=agent_file.name,
                    suggestion="Consider splitting or removing verbose examples."
                ))
    
    return diagnoses
```

#### Diagnosis Data Model

```python
@dataclass
class Diagnosis:
    category: str          # Consistency, Duplicate, Optimization, etc.
    level: str            # ERROR, WARNING, INFO
    message: str          # Human-readable description
    resource: Optional[str]  # Affected file/component
    suggestion: Optional[str]  # Actionable remediation
```

#### CLI Usage

**Run Diagnostics**:

```bash
# Full diagnostic report
$ cortex doctor

[PASS] Consistency check
[WARN] Duplicate check
  - Identical content found in agents: backend-architect.md, api-architect.md
    Suggestion: Delete duplicate files.
[PASS] Redundancy check
[WARN] Optimization check
  - Agent definition is large (12.3KB) (code-reviewer.md)
    Suggestion: Consider splitting this agent or removing verbose examples.
```

**Auto-Fix Mode** (Future):

```bash
# Attempt automatic fixes
$ cortex doctor --fix

[PASS] Consistency check
[FIX] Duplicate check
  ✓ Deleted duplicate: api-architect.md
[PASS] Redundancy check
[WARN] Optimization check (manual review required)
```

#### Integration with Workflows

**Pre-Commit Hook**:

```bash
#!/bin/bash
# .git/hooks/pre-commit

cortex doctor
if [ $? -ne 0 ]; then
    echo "❌ Doctor diagnostics failed. Fix issues before committing."
    exit 1
fi
```

**CI/CD Pipeline**:

```yaml
# .github/workflows/quality.yml
steps:
  - name: Run cortex diagnostics
    run: |
      cortex doctor
      if [ $? -ne 0 ]; then
        echo "::error::Context health checks failed"
        exit 1
      fi
```

#### Benefits

**1. Proactive Issue Detection**

- Catch problems before they cause failures
- Validate configuration integrity
- Identify performance bottlenecks

**2. Automated Maintenance**

- Suggest cleanup actions
- Detect duplicates and redundancy
- Optimize resource usage

**3. Developer Experience**

- Clear, actionable suggestions
- Categorized diagnostics (error vs warning)
- Integration with existing workflows

**4. System Health Monitoring**

- Track configuration quality over time
- Prevent configuration drift
- Enforce best practices

---

### 4.10 Data Layer

The data layer uses multiple storage backends optimized for different use cases.

#### Storage Backends

**1. Markdown Files** (Primary configuration)

- **Location**: `~/.claude/agents/`, `modes/`, `rules/`, `skills/`
- **Format**: Markdown with YAML frontmatter
- **Use case**: Component definitions, human-readable, version control friendly

**2. JSON Files** (Runtime state)

- **Location**: `~/.claude/data/`
- **Files**:
  - `patterns.json` - Session history for pattern learning
  - `activity.json` - Activity metrics
  - `recommendations.json` - Cached recommendations
- **Use case**: Fast serialization, structured data

**3. SQLite Database** (Skill ratings)

- **Location**: `~/.claude/data/skill-ratings.db`
- **Schema**: Ratings, feedback, analytics
- **Use case**: Relational queries, aggregations, transactions

**4. Memory Vault** (Knowledge persistence)

- **Location**: `~/basic-memory/` (configurable)
- **Format**: Markdown with YAML frontmatter
- **Use case**: Long-term knowledge storage, searchable

#### CLAUDE.md Format

The central configuration file uses a custom markdown format:

```markdown
# Core Rules
@rules/workflow-rules.md
@rules/quality-gate-rules.md

# Active Modes
@modes/Brainstorming.md
<!-- @modes/Super_Saiyan.md -->

# Active Agents
@agents/code-reviewer.md
@agents/security-auditor.md
<!-- @agents/performance-engineer.md -->

# Skills (loaded on-demand)
<!-- No explicit references, discovered dynamically -->
```

**Operations**:

```python
def update_claude_md(
    claude_dir: Path,
    component_name: str,
    activate: bool,
    category: str = "agents"
) -> None:
    """Update CLAUDE.md to activate/deactivate component."""
    claude_md = claude_dir / "CLAUDE.md"
    content = claude_md.read_text(encoding="utf-8")
    
    # Build reference line
    ref_line = f"@{category}/{component_name}.md"
    
    if activate:
        # Uncomment if commented, add if missing
        if f"<!-- {ref_line} -->" in content:
            content = content.replace(
                f"<!-- {ref_line} -->",
                ref_line
            )
        elif ref_line not in content:
            # Add to appropriate section
            content = _insert_in_section(content, category, ref_line)
    else:
        # Comment out if active
        if ref_line in content and f"<!-- {ref_line} -->" not in content:
            content = content.replace(
                ref_line,
                f"<!-- {ref_line} -->"
            )
    
    # Write back with backup
    _write_with_backup(claude_md, content)
```

---

## 5. Data Models and Formats

### 5.1 Component Metadata (YAML Frontmatter)

**Agent Metadata**:

```yaml
---
name: security-auditor
description: Security vulnerability assessment and threat modeling
model: Sonnet
category: Security
priority: high
dependencies:
  - code-reviewer
auto_activate: true
triggers:
  - pattern: "**/auth/**/*.py"
  - pattern: "**/security/**/*.py"
  - context: "auth"
  - context: "security"
metrics:
  - findings_count
  - remediation_rate
  - coverage_score
workflow: reconnaissance → analysis → verification
---
```

**Skill Metadata**:

```yaml
---
name: api-design-patterns
category: architecture
description: REST API design patterns and best practices
version: 1.2.0
tags: [api, rest, design, architecture]
complexity: intermediate
estimated_read_time: 15
dependencies: []
author: community
license: MIT
updated: 2025-12-01
---
```

### 5.2 Intelligence Data Structures

**SessionContext** (Python dataclass):

```python
@dataclass
class SessionContext:
    files_changed: List[str]
    file_types: Set[str]
    directories: Set[str]
    has_tests: bool
    has_auth: bool
    has_api: bool
    has_frontend: bool
    has_backend: bool
    has_database: bool
    errors_count: int
    test_failures: int
    build_failures: int
    session_start: datetime
    last_activity: datetime
    active_agents: List[str]
    active_modes: List[str]
    active_rules: List[str]
```

**Pattern Database** (JSON):

```json
{
  "patterns": {
    "backend_api": [
      {
        "timestamp": "2025-12-01T10:30:00Z",
        "context": {
          "has_backend": true,
          "has_api": true,
          "files_changed": ["api/routes.py", "api/models.py"]
        },
        "agents": ["backend-architect", "security-auditor", "test-automator"],
        "duration": 510,
        "outcome": "success"
      }
    ]
  },
  "agent_sequences": [
    ["backend-architect", "security-auditor", "test-automator"],
    ["code-reviewer", "test-automator"]
  ],
  "success_contexts": [...]
}
```

### 5.3 Skill Rating Schema

**SQLite Tables**:

```sql
-- Ratings table
CREATE TABLE ratings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    skill_name TEXT NOT NULL,
    stars INTEGER NOT NULL CHECK (stars >= 1 AND stars <= 5),
    review TEXT,
    helpful INTEGER DEFAULT 0,
    not_helpful INTEGER DEFAULT 0,
    timestamp TEXT NOT NULL,
    user_id TEXT,
    session_id TEXT
);

-- Activation history
CREATE TABLE skill_activations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    skill_name TEXT NOT NULL,
    context_key TEXT NOT NULL,
    agent_name TEXT,
    timestamp TEXT NOT NULL,
    session_id TEXT,
    outcome TEXT
);

-- Indexes
CREATE INDEX idx_ratings_skill ON ratings(skill_name);
CREATE INDEX idx_ratings_timestamp ON ratings(timestamp);
CREATE INDEX idx_activations_skill ON skill_activations(skill_name);
CREATE INDEX idx_activations_context ON skill_activations(context_key);
```

---

## 6. Component Interactions

### 6.1 Sequence Diagram: Agent Activation

```
User → CLI/TUI: activate agent X
    CLI/TUI → AgentManager: agent_activate("X")
        AgentManager → FileSystem: find agent X
        AgentManager → FileSystem: parse frontmatter
        AgentManager → AgentManager: build dependency graph
        AgentManager → FileSystem: check dependencies
        AgentManager → FileSystem: update CLAUDE.md
        FileSystem → AgentManager: success
    AgentManager → CLI/TUI: (activated=[X, dep1, dep2], missing=[])
CLI/TUI → User: "✓ Activated X (with deps: dep1, dep2)"
```

### 6.2 Sequence Diagram: AI Recommendation

```
FileSystem → Intelligence: file changes detected
    Intelligence → ContextDetector: detect_context(files)
        ContextDetector → ContextDetector: parse file types
        ContextDetector → ContextDetector: detect patterns
    ContextDetector → Intelligence: SessionContext
    Intelligence → PatternLearner: load_patterns(context_key)
        PatternLearner → FileSystem: read patterns.json
    PatternLearner → Intelligence: historical_patterns
    Intelligence → Recommender: generate_recommendations()
        Recommender → Recommender: rule_based_scoring()
        Recommender → Recommender: pattern_based_scoring()
        Recommender → Recommender: merge_and_sort()
    Recommender → Intelligence: recommendations
Intelligence → AutoActivator: filter(confidence >= 0.8)
    AutoActivator → AgentManager: activate_agents(high_confidence)
AutoActivator → User: notify("Auto-activated: security-auditor")
```

### 6.3 Data Flow Diagram: Skill Rating Feedback Loop

```
User rates skill (5 stars)
    ↓
skill_rating.py: record_rating()
    ↓
SQLite: INSERT INTO ratings
    ↓
skill_recommender.py: periodic refresh
    ↓
skill_recommender.py: calculate_rating_boost()
    ↓
Recommendations: apply boost to highly-rated skills
    ↓
Intelligence: recommend skills with adjusted confidence
    ↓
TUI/CLI: display recommendations (boosted skills ranked higher)
    ↓
User activates skill
    ↓
skill_recommender.py: record_activation()
    ↓
SQLite: INSERT INTO skill_activations
    ↓
[Loop continues]
```

---

## 7. Key Workflows

### 7.1 First-Time Setup

```
1. Install CLI
   $ ./scripts/deprecated/install.sh
   
2. Verify installation
   $ cortex --version
   $ cortex mode list
   
3. (Optional) Set up shell completion
   $ cortex completion bash --install
   
4. Launch TUI to explore
   $ cortex tui
   
5. Activate first agent
   TUI: Press '0' → Select 'code-reviewer' → Press Enter
   
6. (Optional) Enable AI intelligence
   $ cortex ai recommend
```

### 7.2 Daily Development Workflow

```
# Morning: Start watch mode
Terminal 1:
$ cortex ai watch

# Code as normal
Terminal 2:
$ vim src/auth/security.py
[Watch mode detects auth code, auto-activates security-auditor]

# Review recommendations
Terminal 2:
$ cortex ai recommend
# or
$ cortex tui
[Press '8' for AI Assistant view]

# Commit changes
$ git add .
$ git commit -m "feat: add 2FA support"
[Watch mode detects new commit, analyzes changes]

# End of day: Capture session
$ cortex memory capture "Implemented 2FA authentication"
```

### 7.3 Security Audit Workflow

```
# 1. Activate security profile
$ cortex profile load security-audit

# 2. Review active agents
$ cortex agent list --active
# Activated: security-auditor, compliance-auditor, penetration-tester

# 3. Run workflow
$ cortex workflow run security-comprehensive

# 4. Review findings
[Agents provide security findings in Claude Code]

# 5. Document issues
$ cortex memory fix "Found SQL injection in /api/users endpoint"

# 6. Deactivate profile
$ cortex profile unload
```

---

## 8. Technology Stack

### 8.1 Core Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.9+ | Runtime |
| **argcomplete** | 3.x | Shell completion |
| **rich** | 13.x | Terminal formatting |
| **textual** | 0.47+ | TUI framework |
| **PyYAML** | 6.x | YAML parsing |
| **psutil** | 5.x | System monitoring |

### 8.2 Development Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| **pytest** | 7.x | Testing framework |
| **pytest-cov** | 4.x | Coverage reporting |
| **pytest-mock** | 3.x | Mocking support |
| **pytest-asyncio** | 0.21.x | Async test support |
| **mypy** | 1.7+ | Type checking |
| **black** | 23.x | Code formatting |

### 8.3 External Integrations

- **Claude Desktop**: MCP server configuration
- **Git**: Version control integration
- **SQLite**: Embedded database (no server required)
- **Shell**: bash, zsh, fish completion support

---

## 9. Performance Architecture

### 9.1 Performance Considerations

**File System Operations**:

- ✅ Lazy loading of markdown files
- ✅ Caching of parsed frontmatter
- ✅ Incremental CLAUDE.md updates (not full rewrites)
- ✅ Memory-mapped files for large skill documents

**TUI Responsiveness**:

- ✅ Async data loading (non-blocking)
- ✅ Progressive rendering (pagination)
- ✅ Debounced search inputs (300ms delay)
- ✅ Virtual scrolling for large lists (>100 items)

**Intelligence System**:

- ✅ Pattern database pruning (keep last 1000 sessions)
- ✅ Fast confidence scoring (<10ms per agent)
- ✅ Background pattern learning (non-blocking)
- ✅ Recommendation caching (5-minute TTL)

**Database Queries**:

- ✅ Indexed queries (skill_name, timestamp)
- ✅ Connection pooling (reuse connections)
- ✅ Prepared statements (parameterized queries)
- ✅ Batched inserts for bulk operations

### 9.2 Benchmark Targets

| Operation | Target | Actual |
|-----------|--------|--------|
| Agent activation | <100ms | ~50ms |
| TUI view switch | <200ms | ~150ms |
| AI recommendation | <500ms | ~300ms |
| Skill search | <300ms | ~200ms |
| Pattern learning | <1s | ~800ms |
| CLAUDE.md update | <50ms | ~30ms |

### 9.3 Resource Usage

**Memory**:

- CLI: ~20MB (minimal)
- TUI: ~50MB (with all views loaded)
- Watch mode: ~30MB (polling process)

**Disk**:

- Installation: ~5MB (Python package)
- Data directory: ~10MB (patterns, ratings, cache)
- Memory vault: Variable (user-generated content)

**CPU**:

- Idle: <1% (event-driven, no polling)
- Active: ~5-10% (during analysis/rendering)
- Watch mode: ~2-5% (periodic git checks)

---

## 10. Security Architecture

### 10.1 Threat Model

**Assets**:

- User configuration (CLAUDE.md)
- Session history (patterns.json)
- Skill ratings database
- Memory vault notes

**Threats**:

- Malicious agents/skills (code injection)
- Unauthorized access to sensitive notes
- Data exfiltration via MCP servers
- CLAUDE.md corruption

**Mitigations**:

- ✅ No code execution in agents/skills (markdown only)
- ✅ File permissions (0600 for sensitive files)
- ✅ Input validation (XSS prevention in markdown)
- ✅ Atomic file writes with backups (.bak files)
- ✅ MCP server sandboxing (Claude Desktop handles isolation)

### 10.2 Secrets Management

**Best Practices**:

- ❌ Never store API keys in CLAUDE.md
- ✅ Use environment variables for secrets
- ✅ Reference secrets indirectly: `${OPENAI_API_KEY}`
- ✅ Exclude `.env` files from version control

**Example**:

```bash
# .env (gitignored)
OPENAI_API_KEY=sk-...
GITHUB_TOKEN=ghp_...

# CLAUDE.md (safe to commit)
Environment:
- API Key: ${OPENAI_API_KEY}
- GitHub: ${GITHUB_TOKEN}
```

### 10.3 Data Privacy

**User Data**:

- ✅ All data stored locally (no cloud sync)
- ✅ No telemetry or analytics sent
- ✅ Memory vault fully under user control
- ✅ SQLite database encrypted at rest (OS-level)

**Community Features**:

- ⚠️ Skill ratings are local by default
- ⚠️ Optional: Export ratings for community sharing (opt-in)
- ✅ No PII collected in skill metadata

---

## 11. Extension Points

### 11.1 Adding Custom Agents

**Steps**:

1. Create agent file in `~/.claude/agents/`:

```markdown
---
name: my-custom-agent
description: My specialized agent
model: Haiku
dependencies: []
---

# My Custom Agent

[Agent behavior description...]
```

1. Activate via CLI or TUI:

```bash
cortex agent activate my-custom-agent
```

1. Agent is auto-discovered, no code changes needed.

### 11.2 Adding Custom Skills

**Steps**:

1. Create skill file in `~/.claude/skills/`:

```markdown
---
name: my-domain-knowledge
category: custom
description: Specialized knowledge for my domain
version: 1.0.0
tags: [custom, domain]
---

# My Domain Knowledge

[Skill content...]
```

1. Reference in agent frontmatter:

```yaml
---
name: my-agent
skills:
  - my-domain-knowledge
---
```

### 11.3 Extending the TUI

**Adding a New View**:

1. Create view class in `tui/screens/`:

```python
# tui/screens/my_view.py
from textual.screen import Screen
from textual.widgets import DataTable

class MyView(Screen):
    """My custom view."""
    
    def __init__(self):
        super().__init__()
    
    async def on_mount(self) -> None:
        """Load data and setup UI."""
        self.setup_table()
    
    def setup_table(self) -> None:
        """Setup the data table."""
        table = DataTable()
        table.add_column("Column 1")
        table.add_column("Column 2")
        # ...
```

1. Register in main app:

```python
# tui/main.py
class ClaudeCtxApp(App):
    def on_key(self, event: events.Key) -> None:
        if event.key == "9":  # New key binding
            self.push_screen(MyView())
```

### 11.4 Custom Intelligence Rules

**Extending Recommendations**:

```python
# custom_intelligence.py
from claude_ctx_py.intelligence import IntelligentAgent

class CustomIntelligence(IntelligentAgent):
    """Extended intelligence with custom rules."""
    
    def _rule_based_recommendations(self, context):
        recommendations = super()._rule_based_recommendations(context)
        
        # Add custom rule
        if self._detect_custom_pattern(context):
            recommendations.append(AgentRecommendation(
                agent_name="my-custom-agent",
                confidence=0.90,
                reason="Custom pattern detected",
                urgency="high",
                auto_activate=True,
                context_triggers=["custom_pattern"],
            ))
        
        return recommendations
    
    def _detect_custom_pattern(self, context):
        """Custom detection logic."""
        # Your logic here
        return False
```

---

## 12. Deployment Architecture

### 12.1 Installation Methods

**1. Script Installation** (Recommended):

```bash
$ ./scripts/deprecated/install.sh
# Installs CLI, completions, manpage
```

**2. Manual Installation**:

```bash
python3 -m pip install .
cortex completion bash --install
sudo cp docs/reference/cortex.1 /usr/local/share/man/man1/
```

**3. Claude Code Plugin**:

```bash
# From Claude Code
/plugin install cortex@marketplace-name
```

### 12.2 Directory Structure (Post-Install)

```
~/.claude/
├── CLAUDE.md                  # Main config
├── modes/                     # Modes (copied from plugin)
├── agents/                    # Agents (copied from plugin)
├── skills/                    # Skills (copied from plugin)
├── rules/                     # Rules (copied from plugin)
├── inactive/                  # Disabled components
│   ├── modes/
│   └── agents/
├── data/                      # Runtime data
│   ├── patterns.json          # Pattern learning
│   ├── activity.json          # Activity metrics
│   ├── skill-ratings.db       # SQLite database
│   └── cache/                 # Temporary cache
├── profiles/                  # Profile templates
│   ├── minimal.yaml
│   ├── frontend.yaml
│   └── backend.yaml
└── memory-config.json         # Memory vault config

~/basic-memory/                # Memory vault (default location)
├── knowledge/
├── projects/
├── sessions/
└── fixes/
```

### 12.3 Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `CLAUDE_PLUGIN_ROOT` | Plugin sandbox (set by Claude Code) | - |
| `CORTEX_MEMORY_VAULT` | Memory vault location | `~/basic-memory` |
| `CORTEX_DEBUG` | Enable debug logging | `false` |

### 12.4 Multi-User / Team Setup

**Shared Configuration**:

```bash
# Team repo
team-cortex/
├── agents/             # Team-specific agents
├── modes/              # Team modes
├── rules/              # Team rules
├── skills/             # Team skills
└── profiles/           # Team profiles

# Each developer
export CLAUDE_PLUGIN_ROOT=/path/to/team-cortex
cortex mode list  # Sees team modes
```

**Personal Overrides**:

```bash
# Personal additions (layered on top)
~/.claude/
├── agents/
│   └── my-personal-agent.md   # Personal agent
└── local-config.json           # Personal preferences
```

---

## 13. Troubleshooting Guide

### 13.1 Common Issues

#### Issue: "Agent not found"

**Symptoms**: `cortex agent activate X` fails with "Agent 'X' not found"

**Diagnosis**:

```bash
# Check if agent exists
$ ls ~/.claude/agents/ | grep -i X
$ ls ~/.claude/inactive/agents/ | grep -i X

# Check CLAUDE_PLUGIN_ROOT (if you are running via Claude Code/plugin)
$ echo $CLAUDE_PLUGIN_ROOT
```

**Resolution**:

- If agent is in `inactive/`, move to `agents/`
- Verify agent filename matches exactly (case-sensitive)
- Ensure you are editing the correct Claude directory (plugin cache vs `~/.claude`)

#### Issue: TUI not loading

**Symptoms**: `cortex tui` crashes or shows blank screen

**Diagnosis**:

```bash
# Check Textual version
$ python3 -m pip show textual

# Run with debug mode
$ TEXTUAL_LOG=1 cortex tui
```

**Resolution**:

- Update Textual: `pip install --upgrade textual`
- Check terminal supports 256 colors: `echo $TERM`
- Try different terminal emulator (iTerm2, Alacritty)

#### Issue: Watch mode not detecting changes

**Symptoms**: `cortex ai watch` runs but doesn't show recommendations

**Diagnosis**:

```bash
# Check git status
$ git status

# Check watch interval
$ cortex ai watch --interval 1.0  # Faster polling

# Check if auto-activate is disabled
$ cortex ai watch --no-auto-activate
```

**Resolution**:

- Ensure you're in a git repository
- Make a git commit (watch mode detects commits)
- Lower the check interval
- Verify files are actually changing: `git diff`

#### Issue: Skill ratings not saving

**Symptoms**: Ratings not persisting after TUI restart

**Diagnosis**:

```bash
# Check database exists
$ ls ~/.claude/data/skill-ratings.db

# Check permissions
$ ls -l ~/.claude/data/skill-ratings.db

# Try manual insert
$ sqlite3 ~/.claude/data/skill-ratings.db \
  "SELECT * FROM ratings LIMIT 5;"
```

**Resolution**:

- Ensure data directory exists: `mkdir -p ~/.claude/data`
- Check disk space: `df -h ~`
- Check SQLite is not locked: `lsof ~/.claude/data/skill-ratings.db`
- Rebuild database: `rm ~/.claude/data/skill-ratings.db && cortex tui`

### 13.2 Performance Issues

#### Issue: TUI is slow

**Symptoms**: View switching takes >1 second

**Diagnosis**:

```bash
# Count total agents/skills
$ find ~/.claude/agents -name "*.md" | wc -l
$ find ~/.claude/skills -name "*.md" | wc -l

# Check system resources
$ top -p $(pgrep -f "cortex tui")
```

**Resolution**:

- Move unused agents to `inactive/`
- Reduce skill count (archive old skills)
- Increase Python heap: `PYTHONMALLOC=malloc cortex tui`
- Use faster terminal emulator

#### Issue: High CPU usage in watch mode

**Symptoms**: Watch mode uses >20% CPU constantly

**Diagnosis**:

```bash
# Check polling interval
$ ps aux | grep "cortex ai watch"

# Monitor git operations
$ strace -p $(pgrep -f "cortex ai watch") 2>&1 | grep git
```

**Resolution**:

- Increase check interval: `cortex ai watch --interval 5.0`
- Reduce repository size (if very large)
- Disable watch mode, use manual recommendations instead

### 13.3 Data Corruption

#### Issue: CLAUDE.md is malformed

**Symptoms**: Can't activate/deactivate agents

**Diagnosis**:

```bash
# Check for syntax errors
$ cat ~/.claude/CLAUDE.md

# Look for backup
$ ls -t ~/.claude/*.bak | head -1
```

**Resolution**:

```bash
# Restore from backup
$ cp ~/.claude/CLAUDE.md.bak ~/.claude/CLAUDE.md

# Or regenerate from scratch
$ cortex doctor --fix-claude-md
```

---

## 14. Appendices

### Appendix A: Glossary

| Term | Definition |
|------|------------|
| **Agent** | A specialized Claude subagent with specific skills and behavior |
| **Mode** | A behavioral modifier that changes Claude's approach without changing agents |
| **Rule** | A reusable rule module that defines constraints and guidelines |
| **Skill** | A markdown document containing specialized knowledge that agents can reference |
| **Profile** | A preconfigured set of agents, modes, and rules for a specific workflow |
| **Scenario** | A test scenario that validates agent behavior |
| **Workflow** | A multi-step automated process that orchestrates agents |
| **Context** | The current state of the development session (files, patterns, errors) |
| **Pattern** | A learned association between context and agent recommendations |
| **Auto-Activation** | Automatic agent activation based on high-confidence (≥80%) recommendations |
| **Watch Mode** | Real-time monitoring mode that analyzes changes and makes recommendations continuously |
| **Memory Vault** | Persistent knowledge storage for domain knowledge, fixes, and session summaries |
| **MCP** | Model Context Protocol - a standard for tool/resource integration with Claude |

### Appendix B: File Locations

| Path | Contents |
|------|----------|
| `~/.claude/` | Main configuration directory |
| `~/.claude/CLAUDE.md` | Central config file (active components) |
| `~/.claude/agents/` | Agent definitions (markdown) |
| `~/.claude/modes/` | Mode definitions (markdown) |
| `~/.claude/skills/` | Skill definitions (markdown) |
| `~/.claude/rules/` | Rule modules (markdown) |
| `~/.claude/inactive/` | Disabled components |
| `~/.claude/data/` | Runtime data (JSON, SQLite) |
| `~/.claude/profiles/` | Profile templates (YAML) |
| `~/.claude/memory-config.json` | Memory vault configuration |
| `~/basic-memory/` | Memory vault (default location) |

### Appendix C: Key Algorithms

**Dependency Resolution** (Topological Sort):

```python
def topological_sort(graph: Dict[str, Set[str]]) -> List[str]:
    """
    Kahn's algorithm for topological sort.
    
    Time complexity: O(V + E)
    Space complexity: O(V)
    """
    in_degree = {node: 0 for node in graph}
    for node in graph:
        for neighbor in graph[node]:
            in_degree[neighbor] = in_degree.get(neighbor, 0) + 1
    
    queue = [node for node, degree in in_degree.items() if degree == 0]
    result = []
    
    while queue:
        node = queue.pop(0)
        result.append(node)
        for neighbor in graph.get(node, []):
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
    
    if len(result) != len(graph):
        raise ValueError("Cycle detected in dependency graph")
    
    return result
```

**Confidence Scoring**:

```python
def calculate_confidence(
    rule_score: float,
    pattern_score: float,
    rating_boost: float
) -> float:
    """
    Combine scores into final confidence.
    
    Strategy: Take max of rule and pattern, then apply rating boost.
    """
    base_confidence = max(rule_score, pattern_score)
    boosted = base_confidence * (1.0 + rating_boost * 0.1)
    return min(boosted, 1.0)  # Cap at 100%
```

**Fuzzy Matching** (Command Palette):

```python
def fuzzy_match(query: str, candidates: List[str]) -> List[Tuple[str, float]]:
    """
    Simple fuzzy matching based on character overlap.
    
    Better alternative: Use rapidfuzz library for production.
    """
    query = query.lower()
    matches = []
    
    for candidate in candidates:
        candidate_lower = candidate.lower()
        
        # Exact match: score = 1.0
        if query == candidate_lower:
            matches.append((candidate, 1.0))
            continue
        
        # Substring match: score = 0.8
        if query in candidate_lower:
            matches.append((candidate, 0.8))
            continue
        
        # Character overlap: score = overlap / len(query)
        overlap = sum(1 for c in query if c in candidate_lower)
        score = overlap / len(query)
        
        if score >= 0.5:  # Minimum threshold
            matches.append((candidate, score))
    
    # Sort by score descending
    matches.sort(key=lambda x: x[1], reverse=True)
    return matches
```

### Appendix D: Architecture Decision Records (ADRs)

**ADR-001: Use Markdown for Component Definitions**

**Context**: Need human-readable, version-control-friendly format for agents/modes/skills.

**Decision**: Use Markdown with YAML frontmatter.

**Rationale**:

- Human-readable and editable in any text editor
- Version control friendly (line-based diffs)
- No code execution required (safe for community sharing)
- Familiar format for developers
- Easy to parse with existing libraries

**Consequences**:

- ✅ Easy to create new components
- ✅ Safe to share (no code injection)
- ⚠️ Requires parsing on every load (mitigated by caching)
- ⚠️ No schema validation by default (added validation step)

---

**ADR-002: Use SQLite for Skill Ratings**

**Context**: Need fast queries for ratings analytics and aggregations.

**Decision**: Use embedded SQLite database for ratings.

**Rationale**:

- No server setup required
- Excellent for read-heavy workloads (analytics)
- ACID transactions for data integrity
- Supports complex queries (JOIN, GROUP BY, AVG)
- Battle-tested and stable

**Consequences**:

- ✅ Fast analytics queries
- ✅ No external dependencies
- ⚠️ File-based locking (one writer at a time)
- ⚠️ Not suitable for concurrent multi-user editing (acceptable for single-user tool)

---

**ADR-003: Textual for TUI Framework**

**Context**: Need rich terminal UI with modern features.

**Decision**: Use Textual framework for TUI.

**Rationale**:

- Modern, reactive architecture
- Rich widgets (tables, modals, command palette)
- CSS-like styling (TCSS)
- Active development and community
- Python 3.9+ compatible

**Consequences**:

- ✅ Beautiful, responsive UI
- ✅ Easy to extend with new views
- ⚠️ Requires Python 3.9+ (acceptable given target audience)
- ⚠️ Learning curve for TCSS (mitigated by examples)

---

### Appendix E: References

**Claude Code Documentation**:

- Plugin System: <https://docs.claude.ai/plugins>
- MCP Specification: <https://modelcontextprotocol.org>

**Python Libraries**:

- Textual: <https://textual.textualize.io>
- Rich: <https://rich.readthedocs.io>
- argparse: <https://docs.python.org/3/library/argparse.html>
- PyYAML: <https://pyyaml.org>

**Inspired By**:

- obra/superpowers: Debugging patterns
- VoltAgent/awesome-claude-code-subagents: Agent architecture
- SuperClaude-Org/SuperClaude_Framework: Mode system
- just-every/code: Multi-agent orchestration

---

## Revision History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2025-12-05 | Initial comprehensive architecture document | System Architect |
| 1.1 | 2025-12-05 | Added Component Toggle System, Doctor Diagnostic System, TUI refactoring updates | System Architect |

---

**Document Status**: ✅ Complete  
**Next Review**: 2026-01-05  
**Maintainer**: Core Team

---

*This master architecture document is maintained as a living document. Please update it as the system evolves.*
