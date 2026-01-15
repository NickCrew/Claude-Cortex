# Claude Code Hooks

This directory contains example hooks for Claude Code that work with the claude-ctx plugin.

## What Are Hooks?

Hooks are shell commands that execute in response to Claude Code events. They enable:
- Quality gates and validation
- Automated workflows
- Policy enforcement
- Custom integrations

## Available Hooks

### Implementation Quality Gate

**File:** `examples/implementation-quality-gate.sh`

A comprehensive three-phase quality gate that enforces professional development standards:

1. **Phase 1: Testing** - test-automator, ≥85% coverage
2. **Phase 2: Documentation** - Intelligent routing, ≥7.5/10 review
3. **Phase 3: Code Review** - quality-engineer + code-reviewer, HIGH/MEDIUM issues resolved

**Features:**
- ✅ Automatic test generation and validation
- ✅ Intelligent documentation routing (user-facing vs API)
- ✅ Code quality and security review
- ✅ Priority-based issue resolution
- ✅ Multi-agent orchestration (7 agents)

**Documentation:** See `examples/HOOK_DOCUMENTATION.md` for complete details.

### Skill Auto-Suggester (New)

**File:** `examples/skill_auto_suggester.py`

Inspired by diet103/claude-code-infrastructure-showcase, this hook scans the user prompt (and optionally changed files) and surfaces relevant `/ctx:*` skills. It reads rules from `skills/skill-rules.json`, so adding new skills only requires updating that JSON.

**Install:**

```bash
cp hooks/examples/skill_auto_suggester.py ~/.claude/hooks/
chmod +x ~/.claude/hooks/skill_auto_suggester.py
```

Add to `~/.claude/settings.json` alongside other hooks:

```json
{
  "hooks": {
    "user-prompt-submit": [
      {"command": "python3", "args": ["~/.claude/hooks/skill_auto_suggester.py"]}
    ]
  }
}
```

The hook looks for `CLAUDE_HOOK_PROMPT` (set automatically by Claude Code). If you also export `CLAUDE_CHANGED_FILES`, it factors filenames into the keyword matching.

## Installation

### Quick Install

Copy the hook to your Claude configuration:

```bash
# Copy hook
cp hooks/examples/implementation-quality-gate.sh ~/.claude/hooks/

# Make executable
chmod +x ~/.claude/hooks/implementation-quality-gate.sh

# Register in settings.json
```

Add to `~/.claude/settings.json`:

```json
{
  "hooks": {
    "user-prompt-submit": [
      {
        "command": "bash",
        "args": ["~/.claude/hooks/implementation-quality-gate.sh"]
      }
    ]
  }
}
```

### Activate Required Agents

```bash
claude-ctx agent activate test-automator api-documenter tutorial-engineer \
  technical-writer docs-architect quality-engineer code-reviewer
```

### Verify Installation

```bash
# Test the hook
CLAUDE_USER_PROMPT="implement a feature" \
  bash ~/.claude/hooks/implementation-quality-gate.sh

# Should show three-phase workflow
```

## Configuration

Edit the hook file to adjust thresholds:

```bash
vim ~/.claude/hooks/implementation-quality-gate.sh

# Key configuration:
COVERAGE_THRESHOLD=85              # Test coverage minimum (%)
DOCS_REVIEW_THRESHOLD=7.5          # Documentation review minimum (0-10)
CODE_REVIEW_REQUIRED=true          # Enable code review phase
```

### Recommended Settings by Project Type

| Project Type | Coverage | Docs Review | Code Review |
|--------------|----------|-------------|-------------|
| Production API | 90% | 8.5 | Required |
| Internal Tool | 80% | 7.0 | Required |
| Prototype | 70% | 6.5 | Optional |
| Open Source | 85% | 8.0 | Required |
| Enterprise | 95% | 9.0 | Required |

## How It Works

### Workflow

```
User submits implementation prompt
         ↓
Hook detects implementation keywords
         ↓
Activates appropriate agents
         ↓
Injects quality gate instructions
         ↓
Claude follows three-phase workflow:
  1. Testing (test-automator)
  2. Documentation (intelligent routing)
  3. Code Review (quality-engineer + code-reviewer)
         ↓
Implementation complete only when all phases pass
```

### Change Type Detection

**User-Facing Changes:**
- Keywords: "UI", "UX", "frontend", "user interface", "tutorial"
- Agents: tutorial-engineer + technical-writer
- Output: User guides, tutorials, walkthroughs

**API/Library Changes:**
- Keywords: "API", "endpoint", "function", "class", "library"
- Agents: api-documenter
- Output: API reference, docstrings, developer docs

### Priority System (Code Review)

- **HIGH:** Must fix immediately (security, critical bugs)
- **MEDIUM:** Must fix (quality, maintainability)
- **LOW:** Nice to have (ask user)

Claude cannot skip HIGH/MEDIUM issues without explicit user permission.

## Example Usage

### Simple API Implementation

```
You: "implement user authentication API"

Claude:
Phase 1: Testing
✅ test-automator generates auth tests
✅ Coverage: 92%

Phase 2: Documentation
✅ api-documenter creates API docs
✅ docs-architect review: 8.0/10

Phase 3: Code Review
✅ quality-engineer: 2 MEDIUM issues found
✅ code-reviewer: 1 HIGH issue (hardcoded secret)
✅ All issues fixed

Implementation complete!
```

### User Interface Feature

```
You: "implement user profile settings UI"

Claude:
Phase 1: Testing
✅ test-automator generates component tests
✅ Coverage: 88%

Phase 2: Documentation
✅ tutorial-engineer creates step-by-step guide
✅ technical-writer documents feature
✅ docs-architect review: 8.5/10

Phase 3: Code Review
✅ quality-engineer: Code quality good
✅ code-reviewer: 1 MEDIUM issue (accessibility)
✅ Issue fixed

Implementation complete!
```

## Disabling the Hook

### Temporary (Per Request)

Tell Claude: "disable quality gate for this task"

### Permanent

Comment out in `~/.claude/settings.json`:

```json
{
  "hooks": {
    "user-prompt-submit": [
      // {
      //   "command": "bash",
      //   "args": ["~/.claude/hooks/implementation-quality-gate.sh"]
      // }
    ]
  }
}
```

### Disable Code Review Only

Edit the hook:

```bash
CODE_REVIEW_REQUIRED=false
```

## Troubleshooting

### Hook Not Triggering

**Check 1:** File is executable
```bash
ls -l ~/.claude/hooks/implementation-quality-gate.sh
# Should show -rwxr-xr-x
```

**Check 2:** Registered in settings.json
```bash
cat ~/.claude/settings.json | jq '.hooks'
```

**Check 3:** Prompt contains implementation keywords
```bash
# These trigger: "implement", "add feature", "create function", "build"
# These don't: "explain", "analyze", "debug"
```

### Agents Not Activating

**Check status:**
```bash
claude-ctx agent status | grep -E "(test-automator|api-documenter|quality-engineer|code-reviewer)"
```

**Activate all:**
```bash
claude-ctx agent activate test-automator api-documenter \
  tutorial-engineer technical-writer docs-architect \
  quality-engineer code-reviewer
```

### Too Strict

Lower thresholds in hook:
```bash
COVERAGE_THRESHOLD=70          # From 85
DOCS_REVIEW_THRESHOLD=6.5      # From 7.5
CODE_REVIEW_REQUIRED=false     # Disable Phase 3
```

### False Positives

Hook triggers on non-implementation prompts. Update keyword detection in hook:

```bash
# Edit is_implementation_task() function
# Add exclusion keywords or adjust detection logic
```

## Creating Custom Hooks

### Hook Template

```bash
#!/usr/bin/env bash
set -euo pipefail

# Your hook logic here
# Access environment variables:
# - CLAUDE_USER_PROMPT: User's input
# - CLAUDE_TOOL_NAME: Tool being called (for tool-call hooks)
# - CLAUDE_FILE_PATH: File path (for file operation hooks)

# Exit codes:
# 0 = success/proceed
# non-zero = block operation

exit 0
```

### Available Hook Types

- `user-prompt-submit` - Runs when user submits a prompt
- `tool-call` - Runs before/after tool execution
- `session-start` - Runs when Claude Code session starts
- `session-end` - Runs when Claude Code session ends

### Registration

Add to `~/.claude/settings.json`:

```json
{
  "hooks": {
    "user-prompt-submit": [...],
    "tool-call": [
      {
        "command": "python3",
        "args": ["/path/to/your-hook.py"]
      }
    ]
  }
}
```

## Resources

- **Hook Documentation:** `examples/HOOK_DOCUMENTATION.md`
- **Plugin Documentation:** `../docs/`
- **Claude Code Hooks Docs:** https://docs.claude.com/claude-code/hooks

## Contributing

Have a useful hook? Submit a PR!

1. Add hook to `hooks/examples/`
2. Include documentation
3. Add to this README
4. Test thoroughly

## License

MIT - Same as claude-ctx plugin
