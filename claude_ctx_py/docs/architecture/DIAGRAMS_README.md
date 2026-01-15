# Architecture Diagrams

This document provides visual representations of the Cortex architecture to help developers understand the system structure and data flows.

## System Architecture Diagrams

### 1. High-Level System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Interfaces                           │
├─────────────────┬───────────────────────────────────────────────┤
│                 │                                                │
│   CLI Layer     │              TUI Layer                        │
│   (cli.py)      │           (tui/main.py)                       │
│                 │                                                │
│  ┌───────────┐  │  ┌────────────────────────────────────────┐  │
│  │ Commands  │  │  │  9 Interactive Views                   │  │
│  │ - mode    │  │  │  0: Agents  4: Workflows  8: AI        │  │
│  │ - agent   │  │  │  1: Modes   5: Scenarios               │  │
│  │ - skill   │  │  │  2: Rules   6: Profiles                │  │
│  │ - ai      │  │  │  3: Skills  7: MCP Servers             │  │
│  │ - workflow│  │  │                                         │  │
│  │ - mcp     │  │  │  + Command Palette (Ctrl+P)            │  │
│  └─────┬─────┘  │  └──────────────────┬──────────────────────┘  │
│        │        │                     │                         │
└────────┼────────┴─────────────────────┼─────────────────────────┘
         │                              │
         └──────────────┬───────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Intelligence Layer                            │
│                  (intelligence.py)                               │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐   │
│  │SessionContext│  │ PatternLearner│  │AgentRecommendation │   │
│  ├──────────────┤  ├──────────────┤  ├────────────────────┤   │
│  │- Files       │  │- Learn       │  │- Agent Name        │   │
│  │- Types       │  │- Patterns    │  │- Confidence 0-1    │   │
│  │- Auth/API    │  │- Predict     │  │- Auto-activate?    │   │
│  │- Tests       │  │- Recommend   │  │- Reasoning         │   │
│  └──────────────┘  └──────────────┘  └────────────────────┘   │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Core Business Logic                           │
│                     (core/ modules)                              │
│                                                                  │
│  ┌─────────┐ ┌────────┐ ┌───────┐ ┌────────┐ ┌──────────┐     │
│  │ agents  │ │ skills │ │ modes │ │ rules  │ │workflows │     │
│  │  .py    │ │  .py   │ │  .py  │ │  .py   │ │   .py    │     │
│  └────┬────┘ └───┬────┘ └───┬───┘ └───┬────┘ └────┬─────┘     │
│       │          │           │          │           │           │
│  ┌────┴──────────┴───────────┴──────────┴───────────┴────┐     │
│  │                  base.py                              │     │
│  │  - File operations  - Parsing  - Utilities            │     │
│  └───────────────────────────────────────────────────────┘     │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Data Layer                                │
│                                                                  │
│  File System (~/.cortex/)          Runtime Data                 │
│  ┌─────────────────────┐           ┌──────────────────────┐    │
│  │ CLAUDE.md           │           │ data/metrics/        │    │
│  │ modes/*.md          │           │ data/sessions/       │    │
│  │ agents/*.md         │           │ data/skill-ratings.db│    │
│  │ skills/*.md         │           └──────────────────────┘    │
│  │ rules/*.md          │                                        │
│  │ inactive/*/         │                                        │
│  └─────────────────────┘                                        │
└─────────────────────────────────────────────────────────────────┘
```

### 2. Component Interaction Flow

```
┌───────┐
│ User  │
└───┬───┘
    │
    ├─────────────────┬──────────────────┐
    ▼                 ▼                  ▼
┌────────┐      ┌──────────┐      ┌─────────┐
│  CLI   │      │   TUI    │      │ Watch   │
│Command │      │Interactive│      │  Mode   │
└───┬────┘      └────┬─────┘      └────┬────┘
    │                │                  │
    └────────────────┼──────────────────┘
                     │
                     ▼
            ┌────────────────┐
            │  Intelligence  │
            │   (optional)   │
            └────────┬───────┘
                     │
    ┌────────────────┼────────────────┐
    ▼                ▼                ▼
┌────────┐      ┌────────┐      ┌─────────┐
│ agents │      │ skills │      │  modes  │
│  core  │      │  core  │      │  core   │
└───┬────┘      └───┬────┘      └────┬────┘
    │               │                 │
    └───────────────┼─────────────────┘
                    │
                    ▼
            ┌───────────────┐
            │  File System  │
            │  (~/.cortex)  │
            └───────────────┘
```

### 3. Intelligence System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    File System Watcher (Optional)                │
└─────────────────────────┬───────────────────────────────────────┘
                          │ File Changes
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Context Detection                             │
│                   (SessionContext)                               │
│                                                                  │
│  Input:                          Output:                         │
│  - Changed files                 - File types                    │
│  - File contents                 - Code patterns                 │
│  - Directory structure           - has_auth, has_api, has_tests  │
│  - Recent errors                 - Error/failure counts          │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Pattern Matching                              │
│                   (PatternLearner)                               │
│                                                                  │
│  ┌────────────────┐              ┌────────────────────┐         │
│  │ Session        │    Compare   │ Pattern Database   │         │
│  │ Context        │◄────────────►│ (past sessions)    │         │
│  └────────────────┘              └────────────────────┘         │
│                                                                  │
│  Similarity Score: context ↔ historical_patterns                │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Agent Recommendation                            │
│                                                                  │
│  For each agent:                                                 │
│  ┌─────────────────────────────────────────────────────┐        │
│  │ 1. Match context triggers (file patterns, keywords) │        │
│  │ 2. Check pattern similarity (historical success)    │        │
│  │ 3. Calculate confidence score (0.0 - 1.0)          │        │
│  │ 4. Determine urgency (low/medium/high/critical)    │        │
│  └─────────────────────────────────────────────────────┘        │
│                                                                  │
│  Filter: confidence ≥ threshold (0.8 for auto-activate)         │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Output & Actions                              │
│                                                                  │
│  Display Recommendations:          Auto-Activate:               │
│  - Agent name                      - confidence ≥ 0.8           │
│  - Confidence %                    - Call agent_activate()       │
│  - Reasoning                       - Update CLAUDE.md            │
│  - Urgency level                   - Notify user                │
└─────────────────────────────────────────────────────────────────┘
```

### 4. Agent Activation Sequence

```
User: "activate code-reviewer"
         │
         ▼
┌─────────────────────┐
│ CLI/TUI Handler     │
└─────────┬───────────┘
          │ agent_activate("code-reviewer")
          ▼
┌─────────────────────┐
│ agents.py           │
│ _find_agent_file()  │◄── Search: active & inactive dirs
└─────────┬───────────┘
          │ Found: agents/code-reviewer.md
          ▼
┌─────────────────────┐
│ Parse Frontmatter   │
│ _extract_front_     │
│    _matter()        │
└─────────┬───────────┘
          │ dependencies: [quality-engineer]
          ▼
┌─────────────────────┐
│ Build Dependency    │
│ Graph               │
│ build_agent_graph() │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ Check Dependencies  │
└─────────┬───────────┘
          │
          ├─ quality-engineer: ❌ Not Active
          │
          ▼
┌─────────────────────┐
│ Recursive Activate  │
│ _agent_activate_    │
│    recursive()      │
└─────────┬───────────┘
          │
          ├─ Activate: quality-engineer
          ├─ Activate: code-reviewer
          │
          ▼
┌─────────────────────┐
│ Update CLAUDE.md    │
│ Uncomment refs:     │
│ @agents/quality-    │
│   engineer.md       │
│ @agents/code-       │
│   reviewer.md       │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ Success Response    │
│ - Activated agents  │
│ - Dependency chain  │
└─────────────────────┘
```

### 5. Data Flow: Context Detection → Auto-Activation

```
Step 1: File System Event
┌────────────────────────┐
│ Files Changed:         │
│ - src/auth.py          │
│ - tests/test_auth.py   │
└────────┬───────────────┘
         │
         ▼
Step 2: Context Building
┌────────────────────────┐
│ SessionContext:        │
│ - file_types: {py}     │
│ - has_auth: True       │
│ - has_tests: True      │
│ - directories: {src,   │
│   tests}               │
└────────┬───────────────┘
         │
         ▼
Step 3: Pattern Analysis
┌────────────────────────┐
│ Pattern DB Query:      │
│ - Similar contexts     │
│ - Success history      │
│ - Agent usage          │
└────────┬───────────────┘
         │
         ▼
Step 4: Scoring
┌────────────────────────┐
│ Agent Scores:          │
│ security-auditor: 0.95 │
│ test-automator: 0.87   │
│ code-reviewer: 0.72    │
└────────┬───────────────┘
         │
         ▼
Step 5: Filter & Sort
┌────────────────────────┐
│ Auto-activate (≥0.8):  │
│ ✓ security-auditor     │
│ ✓ test-automator       │
│                        │
│ Suggest only (<0.8):   │
│ • code-reviewer        │
└────────┬───────────────┘
         │
         ▼
Step 6: Activation
┌────────────────────────┐
│ Actions:               │
│ 1. agent_activate(     │
│      security-auditor) │
│ 2. agent_activate(     │
│      test-automator)   │
│ 3. Update CLAUDE.md    │
│ 4. Notify user         │
└────────────────────────┘
```

### 6. TUI View Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        AgentTUI (main.py)                        │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │                Header (title, status)                   │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │                  ContentSwitcher                        │    │
│  │                                                         │    │
│  │  Current View (one active at a time):                  │    │
│  │  ┌──────────────────────────────────────────────────┐  │    │
│  │  │ View 0: Agents Table                             │  │    │
│  │  │ - DataTable with agent list                      │  │    │
│  │  │ - Actions: activate, deactivate, deps, graph     │  │    │
│  │  └──────────────────────────────────────────────────┘  │    │
│  │                                                         │    │
│  │  Other views: Modes, Rules, Skills, Workflows,         │    │
│  │               Scenarios, Profiles, MCP, AI Assistant   │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │            Footer (key bindings, status)                │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                  │
│  Overlays (modal):                                              │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ - Command Palette (Ctrl+P)                             │    │
│  │ - Dialogs (confirm, input, rating)                     │    │
│  │ - Notifications (toast messages)                       │    │
│  └────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘

Key Bindings:
  0-8: Switch views
  Ctrl+P: Command palette
  Ctrl+C/Q: Quit
  View-specific bindings in footer
```

## Sequence Diagrams

### 1. AI Watch Mode Workflow

```
User                 Watch Process         Intelligence        File System
 │                         │                     │                  │
 │ cortex ai watch     │                     │                  │
 ├────────────────────────►│                     │                  │
 │                         │                     │                  │
 │                         │ Start monitoring    │                  │
 │                         ├────────────────────►│                  │
 │                         │                     │                  │
 │                         │                     │ Poll changes     │
 │                         │                     ├─────────────────►│
 │                         │                     │                  │
 │                         │                     │◄─────────────────┤
 │                         │                     │ Changed files    │
 │                         │                     │                  │
 │                         │ Build context       │                  │
 │                         │◄────────────────────┤                  │
 │                         │                     │                  │
 │                         │ Get recommendations │                  │
 │                         │─────────────────────►                  │
 │                         │                     │                  │
 │                         │◄────────────────────┤                  │
 │                         │ Agents + confidence │                  │
 │                         │                     │                  │
 │◄────────────────────────┤                     │                  │
 │ Display recommendations │                     │                  │
 │                         │                     │                  │
 │                         │ Auto-activate (≥80%)│                  │
 │                         ├────────────────────►│                  │
 │                         │                     │                  │
 │◄────────────────────────┤                     │                  │
 │ Activation confirmation │                     │                  │
 │                         │                     │                  │
 │                   [repeat every 5 seconds]    │                  │
```

### 2. Skill Rating Workflow

```
User              TUI                  skills.py           SQLite DB
 │                 │                       │                    │
 │ Press 'Ctrl+R'  │                       │                    │
 ├────────────────►│                       │                    │
 │                 │ Show rating dialog    │                    │
 │◄────────────────┤                       │                    │
 │                 │                       │                    │
 │ Enter rating    │                       │                    │
 ├────────────────►│                       │                    │
 │ (stars, review) │                       │                    │
 │                 │ skill_rate()          │                    │
 │                 ├──────────────────────►│                    │
 │                 │                       │ INSERT rating      │
 │                 │                       ├───────────────────►│
 │                 │                       │                    │
 │                 │                       │◄───────────────────┤
 │                 │                       │ Success            │
 │                 │◄──────────────────────┤                    │
 │                 │ Confirmation          │                    │
 │◄────────────────┤                       │                    │
 │ "Rating saved"  │                       │                    │
 │                 │                       │                    │
 │                 │ Refresh metrics       │                    │
 │                 ├──────────────────────►│                    │
 │                 │                       │ SELECT stats       │
 │                 │                       ├───────────────────►│
 │                 │                       │◄───────────────────┤
 │                 │◄──────────────────────┤                    │
 │                 │ Updated metrics       │                    │
 │                 │                       │                    │
```

## State Diagrams

### Agent Lifecycle States

```
┌──────────────┐
│   Disabled   │ (in inactive/agents/)
└───────┬──────┘
        │ activate
        ▼
┌──────────────┐
│    Active    │ (referenced in CLAUDE.md)
└───────┬──────┘
        │ deactivate
        ▼
┌──────────────┐
│   Disabled   │ (moved to inactive/agents/)
└──────────────┘

Special states:
- Active with dependencies
- Active with dependents (cannot deactivate without --force)
- Validation error (metadata issues)
```

### Workflow Execution States

```
┌──────────┐
│  Ready   │
└────┬─────┘
     │ start
     ▼
┌──────────┐
│ Running  │
└────┬─────┘
     │
     ├─► Phase 1 ─► Phase 2 ─► Phase N
     │                              │
     │                              ▼
     │                         ┌──────────┐
     │ error                   │Complete  │
     ├────────────────────────►└──────────┘
     ▼
┌──────────┐      resume
│  Paused  ├─────────────────► Running
└────┬─────┘
     │ stop
     ▼
┌──────────┐
│ Stopped  │
└──────────┘
```

## Directory Structure Diagram

```
cortex-plugin/
│
├── claude_ctx_py/              # Python package
│   ├── cli.py                  # CLI entry point
│   ├── intelligence.py         # AI system
│   ├── core/                   # Core modules
│   │   ├── agents.py
│   │   ├── skills.py
│   │   ├── modes.py
│   │   ├── workflows.py
│   │   ├── mcp.py
│   │   └── ...
│   └── tui/                    # TUI package
│       ├── main.py             # TUI app
│       ├── types.py
│       └── constants.py
│
├── agents/                     # Agent definitions
├── modes/                      # Mode definitions
├── skills/                     # Skill definitions
├── rules/                      # Rule modules
├── commands/                   # Slash commands
├── workflows/                  # Workflow templates
├── profiles/                   # Profile templates
├── scenarios/                  # Test scenarios
├── inactive/                   # Disabled components
│   ├── agents/
│   ├── modes/
│   └── ...
│
├── tests/                      # Test suite
├── docs/                       # Documentation
│   ├── architecture/           # This directory
│   ├── guides/
│   ├── reference/
│   └── workstreams/
│
├── pyproject.toml             # Package config
├── README.md                  # Main readme
└── CONTRIBUTING.md            # Contributor guide
```

## Notes

- All diagrams use ASCII/Unicode for maximum compatibility
- Mermaid diagrams are available in the main [README.md](README.md)
- For complex diagrams, consider using Draw.io or similar tools
- Keep diagrams up-to-date with code changes

## Tools Used

- **ASCII Art**: Hand-crafted box diagrams
- **Mermaid**: Sequence and flow diagrams (in README.md)
- **Plain Text**: Maximum compatibility, version control friendly

## Next Steps

1. Add sequence diagrams for remaining workflows
2. Create component interaction matrix
3. Document error handling flows
4. Add performance optimization diagrams
5. Create deployment architecture diagram
