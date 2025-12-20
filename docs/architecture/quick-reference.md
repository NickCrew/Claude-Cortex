# Claude Cortex - Quick Reference

## Quick Start

### Installation
```bash
# Clone repository
git clone https://github.com/NickCrew/claude-ctx-plugin.git
cd claude-ctx-plugin

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Run CLI
claude-ctx --help

# Run TUI
claude-ctx tui
```

### Running Tests
```bash
# Run all tests with coverage
pytest

# Run specific test file
pytest tests/test_agents.py

# Run with verbose output
pytest -v

# Run only unit tests
pytest -m unit
```

## Key File Locations

### Source Code
```
claude_ctx_py/
├── cli.py                  # CLI entry point
├── intelligence.py         # AI recommendations
├── core/                   # Business logic
│   ├── agents.py          # Agent management
│   ├── skills.py          # Skill management
│   ├── modes.py           # Mode management
│   ├── workflows.py       # Workflow orchestration
│   └── ...
└── tui/                    # TUI application
    ├── main.py            # TUI entry point
    ├── types.py           # Type definitions
    └── constants.py       # View constants
```

### User Configuration
```
~/.claude/
├── CLAUDE.md              # Active components
├── modes/                 # Available modes
├── agents/                # Available agents
├── skills/                # Available skills
├── rules/                 # Rule modules
├── inactive/              # Disabled components
└── data/                  # Metrics & ratings
```

## Common Commands

### CLI Commands
```bash
# Mode management
claude-ctx mode list
claude-ctx mode status
claude-ctx mode activate Brainstorming
claude-ctx mode deactivate Brainstorming

# Agent management
claude-ctx agent list
claude-ctx agent status
claude-ctx agent activate code-reviewer
claude-ctx agent deps code-reviewer
claude-ctx agent graph

# Skill management
claude-ctx skills list
claude-ctx skills info api-design-patterns
claude-ctx skills rate owasp-top-10 --stars 5
claude-ctx skills ratings owasp-top-10
claude-ctx skills trending

# AI automation
claude-ctx ai recommend
claude-ctx ai auto-activate
claude-ctx ai watch

# MCP servers
claude-ctx mcp list
claude-ctx mcp show context7
claude-ctx mcp docs sequential

# Workflows
claude-ctx workflow list
claude-ctx workflow run workflow-name

# TUI
claude-ctx tui
```

### TUI Key Bindings
```
Navigation:
  0-8          - Switch to view (Agents, Modes, Rules, etc.)
  Ctrl+P       - Command palette
  Ctrl+C/Q     - Quit

View Actions:
  Enter        - Activate selected item
  Space        - Deactivate selected item
  d            - Show details
  i            - Show info
  Ctrl+R       - Rate skill (Skills view)

Agents View (0):
  g            - Show dependency graph
  v            - Validate agents

MCP View (7):
  t            - Test server
  d            - View docs
  c            - Copy config
  v            - Validate

AI Assistant (8):
  A            - Auto-activate recommendations
  r            - Refresh recommendations
```

## Quick Reference: Core APIs

### Agent Management
```python
from claude_ctx_py.core import (
    agent_activate,
    agent_deactivate,
    build_agent_graph,
    agent_deps,
)

# Activate agent (with dependencies)
agent_activate("code-reviewer")

# Deactivate agent
agent_deactivate("code-reviewer", force=True)

# Build dependency graph
graph = build_agent_graph()

# Show agent dependencies
agent_deps("code-reviewer")
```

### Intelligence System
```python
from claude_ctx_py.intelligence import (
    SessionContext,
    AgentRecommendation,
    PatternLearner,
)

# Build session context
context = SessionContext(
    files_changed=["src/auth.py", "tests/test_auth.py"],
    file_types={"py"},
    directories={"src", "tests"},
    has_auth=True,
    has_tests=True,
    # ... other fields
)

# Get recommendations
learner = PatternLearner()
recommendations = learner.recommend_agents(context)

# Filter high-confidence
auto_activate = [r for r in recommendations if r.confidence >= 0.8]
```

### Skill Management
```python
from claude_ctx_py.core import (
    skill_rate,
    skill_metrics,
    skill_recommend,
)

# Rate a skill
skill_rate("owasp-top-10", stars=5, review="Excellent security guide")

# Get skill metrics
metrics = skill_metrics("owasp-top-10")

# Get recommendations
recommendations = skill_recommend(context="security audit")
```

## Architecture Quick View

### System Layers
```
┌─────────────┐
│  CLI / TUI  │ ← User Interface
├─────────────┤
│Intelligence │ ← AI Recommendations
├─────────────┤
│ Core Logic  │ ← Business Logic
├─────────────┤
│  File I/O   │ ← Data Access
└─────────────┘
```

### Data Flow
```
User Input → CLI/TUI → Core Module → File System → CLAUDE.md
                ↓
          Intelligence
                ↓
        Recommendations
                ↓
         Auto-Activate
```

### Component Types
```
Agents    - Claude subagents (code-reviewer, test-automator)
Modes     - Behavioral contexts (Brainstorming, Super_Saiyan)
Rules     - Reusable rule sets (workflow-rules, quality-gate-rules)
Skills    - Knowledge modules (api-design-patterns, python-testing)
Workflows - Multi-step processes (test → build → deploy)
Profiles  - Component bundles (frontend, backend, devops)
```

## Common Patterns

### Creating a New Agent
```markdown
---
name: my-agent
description: Brief description of what this agent does
dependencies:
  - code-reviewer
priority: medium
auto_activate: false
triggers:
  - pattern: "*.py"
  - context: "python"
---

# My Agent

Agent instructions and prompt go here...
```

### Creating a New Mode
```markdown
---
name: my-mode
description: What this mode enables
priority: normal
---

# My Mode

Mode-specific instructions...
```

### Creating a Skill
```markdown
---
name: my-skill
description: Skill overview
category: patterns
difficulty: intermediate
tags:
  - python
  - testing
---

# My Skill

Skill content with examples...
```

## Testing Patterns

### Unit Test Example
```python
def test_agent_activate():
    # Arrange
    agent_name = "test-agent"

    # Act
    result = agent_activate(agent_name)

    # Assert
    assert result is not None
    assert agent_name in get_active_agents()
```

### TUI Test Example
```python
async def test_agent_view():
    app = AgentTUI()
    async with app.run_test() as pilot:
        # Switch to agents view
        await pilot.press("0")

        # Verify table rendered
        table = app.query_one(DataTable)
        assert table.row_count > 0
```

## Debugging Tips

### Enable Debug Logging
```bash
# Set environment variable
export CLAUDE_CTX_DEBUG=1

# Run command
claude-ctx ai recommend
```

### TUI Debugging
```python
# Add to tui/main.py
self.log("Debug message", severity="debug")

# View logs
tail -f ~/.textual/claude-ctx.log
```

### Intelligence Debugging
```python
# Add verbose output
from claude_ctx_py.intelligence import PatternLearner

learner = PatternLearner(verbose=True)
recommendations = learner.recommend_agents(context)
```

## Configuration

### Environment Variables
```bash
CLAUDE_PLUGIN_ROOT=...           # Plugin context directory (optional; set by Claude Code)
CLAUDE_CTX_DEBUG=1               # Enable debug logging
CLAUDE_CTX_NO_COLOR=1            # Disable color output
```

### Config File Locations
```
~/.claude/CLAUDE.md              # Main config
~/.claude/data/sessions/         # Session history
~/.claude/data/metrics/          # Performance metrics
~/.claude/data/skill-ratings.db  # SQLite database
```

## Performance Tips

### CLI Performance
- Use `--no-color` in scripts for faster output
- Enable shell completion for faster typing
- Cache expensive operations (already done internally)

### TUI Performance
- Large tables render incrementally
- Search is debounced for responsiveness
- Background data loading where possible

### Intelligence Performance
- Pattern database auto-prunes old sessions
- Confidence scoring optimized for speed
- Parallel recommendation generation

## Troubleshooting

### Common Issues

**Issue**: `ModuleNotFoundError: No module named 'claude_ctx_py'`
- **Solution**: Install package: `pip install -e .`

**Issue**: TUI doesn't render correctly
- **Solution**: Update terminal or use different emulator
- **Check**: `echo $TERM` should be `xterm-256color` or similar

**Issue**: Agent activation fails with dependency errors
- **Solution**: Check dependency graph: `claude-ctx agent graph`
- **Activate dependencies**: `claude-ctx agent deps <agent-name>`

**Issue**: Intelligence recommendations not working
- **Solution**: Record some sessions: `claude-ctx ai record-success`
- **Check**: Session data exists: `ls ~/.claude/data/sessions/`

**Issue**: MCP servers not detected
- **Solution**: Verify Claude Desktop config exists
- **Check**: `~/.config/claude-desktop/config.json`

## Quick Links

- [Full Architecture Documentation](README.md)
- [AI Intelligence Guide](../guides/development/AI_INTELLIGENCE_GUIDE.md)
- [Contributing Guide](../../CONTRIBUTING.md)
- [GitHub Repository](https://github.com/NickCrew/claude-ctx-plugin)
- [Documentation Site](https://nickcrew.github.io/claude-ctx-plugin/)
