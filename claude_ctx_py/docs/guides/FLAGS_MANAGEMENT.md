# Flag Management Guide

## Overview

The Cortex Flag Management System provides surgical control over behavioral flags while dramatically reducing token usage. Instead of loading all 3,380 tokens of flags in every conversation, you can selectively enable only the categories you need.

## Quick Start

### Using the TUI Flag Manager

1. **Open the Flag Manager:**

   ```bash
   cortex tui
   # Press Ctrl+G
   ```

2. **Navigate:**
   - `↑` / `↓` - Move between flag categories
   - `Space` - Toggle selected flag on/off
   - `Esc` or number keys - Return to other views

3. **See Results:**
   - Real-time token counts update
   - Changes save immediately to `~/.cortex/FLAGS.md`
   - Enabled flags show `✓ ON` in green
   - Disabled flags show `✗ OFF` in dim gray

### Using Profiles

Profiles automatically configure flags for you:

```bash
# Switch to frontend profile
cortex profile apply frontend
# Auto-enables: visual-excellence, testing-quality, domain-presets, debugging-trace

# Switch to backend profile
cortex profile apply backend
# Auto-enables: testing-quality, debugging-trace, refactoring-safety

# Switch to minimal profile
cortex profile apply minimal
# Enables only: mode-activation, mcp-servers, execution-control
```

## Flag Categories

### Core Flags (Always Recommended)

**Mode Activation** (120 tokens)

- Flags: `--brainstorm`, `--introspect`, `--task-manage`, `--orchestrate`, `--token-efficient`
- Use for: Collaborative discovery, transparent reasoning, multi-step orchestration
- Recommended: All profiles

**MCP Servers** (160 tokens)

- Flags: `--c7`, `--seq`, `--magic`, `--morph`, `--codanna`, `--play`, `--all-mcp`, `--no-mcp`
- Use for: External tool integration, documentation lookup, structured reasoning
- Recommended: Most profiles

**Execution Control** (150 tokens)

- Flags: `--delegate`, `--concurrency`, `--loop`, `--iterations`, `--validate`, `--safe-mode`
- Use for: Parallel execution, iterative improvement, validation gates
- Recommended: All profiles

### Development Flags

**Thinking Budget** (140 tokens)

- Flags: `--thinking-budget [4000|10000|32000|128000]`
- Use for: Explicit reasoning token allocation and cost control
- Recommended: Deep analysis, cost-sensitive workflows

**Analysis Depth** (130 tokens)

- Flags: `--think`, `--think-hard`, `--ultrathink`
- Use for: Complex debugging, architectural decisions, critical redesign
- Recommended: backend, web-dev, quality, meta

**Testing & Quality** (170 tokens)

- Flags: `--tdd`, `--coverage`, `--mutation-test`
- Use for: Test-driven development, quality assurance
- Recommended: frontend, backend, web-dev, quality, data-ai

**Debugging & Trace** (110 tokens)

- Flags: `--trace`, `--verbose`, `--quiet`
- Use for: Complex debugging, performance issues, mysterious failures
- Recommended: frontend, backend, web-dev, quality, devops

**Refactoring Safety** (140 tokens)

- Flags: `--refactor-safe`, `--preserve-behavior`, `--modernize`
- Use for: Large refactorings, legacy code changes, framework upgrades
- Recommended: backend, quality, meta

### UI/UX Flags

**Visual Excellence** (250 tokens)

- Flags: `--supersaiyan`, `--kamehameha`, `--over9000`
- Use for: UI work, visual polish, design systems
- Recommended: frontend, web-dev

**Domain Presets** (150 tokens)

- Flags: `--frontend`, `--backend`, `--fullstack`, `--data-science`
- Use for: Quick domain-specific stack activation
- Recommended: frontend, web-dev

### Productivity Flags

**Learning & Education** (160 tokens)

- Flags: `--teach-me`, `--eli5`, `--show-alternatives`, `--best-practices`
- Use for: Learning new concepts, understanding trade-offs
- Recommended: documentation, product

**Interactive Control** (130 tokens)

- Flags: `--confirm-changes`, `--auto-approve`, `--pair-programming`
- Use for: Production changes, learning sessions, collaboration
- Recommended: developer-experience

**Output Optimization** (120 tokens)

- Flags: `--uc`, `--scope`, `--focus`
- Use for: Context pressure, focused analysis, token efficiency
- Recommended: Default (already enabled)

### Cost & Automation Flags

**Cost Management** (120 tokens)

- Flags: `--cost-limit`, `--cost-aware`, `--frugal`
- Use for: Budget constraints, cost tracking
- Recommended: Enable when cost-conscious

**CI/CD** (100 tokens)

- Flags: `--ci-mode`, `--json-output`, `--exit-on-error`
- Use for: Automation, pipelines, scripting
- Recommended: devops

**Auto-Escalation** (180 tokens)

- Flags: `--auto-escalate [confidence|errors|complexity|adaptive]`
- Use for: Automatic reasoning depth adjustment
- Recommended: Advanced use only (expensive)

## Profile-to-Flag Mappings

### Minimal Profile (430 tokens, 87% savings)

```
✓ mode-activation.md
✓ mcp-servers.md
✓ execution-control.md
```

Use when: Starting new project, exploration, minimal overhead

### Frontend Profile (1,110 tokens, 67% savings)

```
✓ mode-activation.md
✓ mcp-servers.md
✓ execution-control.md
✓ visual-excellence.md
✓ testing-quality.md
✓ domain-presets.md
✓ debugging-trace.md
```

Use when: UI development, component work, visual polish

### Backend Profile (980 tokens, 71% savings)

```
✓ mode-activation.md
✓ mcp-servers.md
✓ analysis-depth.md
✓ execution-control.md
✓ testing-quality.md
✓ debugging-trace.md
✓ refactoring-safety.md
```

Use when: API development, database work, services

### Web-Dev Profile (1,360 tokens, 60% savings)

```
✓ mode-activation.md
✓ mcp-servers.md
✓ analysis-depth.md
✓ execution-control.md
✓ visual-excellence.md
✓ output-optimization.md
✓ testing-quality.md
✓ domain-presets.md
✓ debugging-trace.md
```

Use when: Full-stack development, end-to-end features

### DevOps Profile (640 tokens, 81% savings)

```
✓ mode-activation.md
✓ mcp-servers.md
✓ execution-control.md
✓ debugging-trace.md
✓ ci-cd.md
```

Use when: Infrastructure, deployment, automation

### Documentation Profile (430 tokens, 87% savings)

```
✓ mode-activation.md
✓ execution-control.md
✓ learning-education.md
```

Use when: Writing docs, guides, tutorials

### Quality Profile (980 tokens, 71% savings)

```
✓ mode-activation.md
✓ mcp-servers.md
✓ analysis-depth.md
✓ execution-control.md
✓ testing-quality.md
✓ refactoring-safety.md
✓ debugging-trace.md
```

Use when: QA work, security audits, code quality

### Data-AI Profile (730 tokens, 78% savings)

```
✓ mode-activation.md
✓ mcp-servers.md
✓ analysis-depth.md
✓ execution-control.md
✓ testing-quality.md
```

Use when: Data science, ML, analysis

### Full Profile (3,380 tokens, 0% savings)

```
✓ All 22 categories enabled
```

Use when: Complex multi-domain work requiring all capabilities

## File Structure

### Flag Files Location

```
~/.cortex/flags/
├── mode-activation.md
├── mcp-servers.md
├── thinking-budget.md
├── analysis-depth.md
├── execution-control.md
├── visual-excellence.md
├── output-optimization.md
├── testing-quality.md
├── learning-education.md
├── cost-budget.md
├── refactoring-safety.md
├── domain-presets.md
├── debugging-trace.md
├── interactive-control.md
├── ci-cd.md
├── auto-escalation.md
├── performance-optimization.md
├── security-hardening.md
├── documentation-generation.md
├── git-workflow.md
├── migration-upgrade.md
└── database-operations.md
```

### FLAGS.md References

```markdown
# Flag Categories (remove line to disable and save tokens)
# Core Flags (~120-160 tokens each)
@flags/mode-activation.md
@flags/mcp-servers.md
@flags/analysis-depth.md
@flags/execution-control.md

# Visual & Output (~140 tokens)
@flags/visual-excellence.md
@flags/output-optimization.md

# Quality & Testing (~170 tokens)
# (remove line to disable)

# Learning & Education (~160 tokens)
# (remove line to disable)

...
```

- **Active flags**: `@flags/filename.md`
- **Disabled flags**: line removed from `FLAGS.md`

## Manual Management

### Editing FLAGS.md Directly

1. Open `~/.cortex/FLAGS.md` in your editor
2. Find the flag you want to enable/disable
3. Remove or add the flag reference line:

**To disable a flag:**

```markdown
# Before
@flags/testing-quality.md

# After
# (line removed)
```

**To enable a flag:**

```markdown
# Before
# (line absent)

# After
@flags/learning-education.md
```

1. Save the file - changes take effect in next conversation

## Token Savings Calculator

### Formula

```
Savings % = (Inactive Tokens / Total Tokens) × 100
Total Tokens = 3,380
```

### Examples

**Minimal Profile:**

- Active: 430 tokens (3 categories)
- Inactive: 2,950 tokens (19 categories)
- Savings: 87%

**Custom Selection (5 categories):**

- Active: ~730 tokens
- Inactive: ~2,650 tokens
- Savings: 78%

**Full Profile:**

- Active: 3,380 tokens (22 categories)
- Inactive: 0 tokens
- Savings: 0%

## Best Practices

### 1. Start Minimal, Add As Needed

- Begin with minimal profile
- Add categories when you encounter specific needs
- Remove categories after specialized work is done

### 2. Use Profiles for Consistency

- Profile switching ensures optimal flag sets
- Less cognitive overhead than manual selection
- Consistent experience across sessions

### 3. Review Flag Usage

- Check `~/.cortex/FLAGS.md` periodically
- Disable unused categories
- Consider creating custom profiles for common workflows

### 4. Context-Aware Selection

- Frontend work → Enable visual-excellence
- Debugging → Enable debugging-trace
- Learning → Enable learning-education
- Production changes → Enable interactive-control

### 5. Monitor Token Usage

- Use TUI Flag Manager to see real-time counts
- Track savings percentage
- Optimize for your most common workflows

## Troubleshooting

### Flags Not Taking Effect

**Problem**: Changed flags in FLAGS.md but behavior unchanged

**Solutions**:

1. Verify syntax: `@flags/filename.md` (active) or remove the line (inactive)
2. Check file exists in `~/.cortex/flags/`
3. Start new conversation (changes apply to new sessions only)

### TUI Manager Not Updating

**Problem**: Flag Manager shows old state

**Solutions**:

1. Exit and re-enter Flag Manager view (Ctrl+G)
2. Restart TUI (`cortex tui`)
3. Verify `~/.cortex/FLAGS.md` exists and is writable

### Profile Flags Not Applying

**Problem**: Profile applied but flags didn't change

**Solutions**:

1. Check profile application succeeded: `cortex profile list`
2. Manually verify FLAGS.md was updated
3. Re-apply profile: `cortex profile apply <name>`

### Token Counts Don't Match

**Problem**: TUI shows different token counts than expected

**Solutions**:

1. Verify `**Estimated tokens: ~XXX**` in each flag file
2. Check for file modifications
3. Refresh flag metadata: Restart TUI

## Advanced Usage

### Creating Custom Profiles

You can create custom profiles with specific flag combinations:

```bash
# Configure flags manually in FLAGS.md
# Then save as a profile
cortex profile save my-custom-profile
```

The profile will save current agents, modes, rules, AND flag state.

### Programmatic Flag Management

The flag system uses simple text manipulation:

```python
from pathlib import Path

flags_md = Path.home() / ".claude" / "FLAGS.md"
content = flags_md.read_text()

# Enable a flag (add line if missing)
if "@flags/testing-quality.md" not in content:
    content = content.rstrip() + "\n@flags/testing-quality.md\n"

# Disable a flag (remove line)
content = "\n".join(
    line for line in content.splitlines()
    if line.strip() != "@flags/learning-education.md"
) + "\n"

flags_md.write_text(content)
```

### Flag File Format

Each flag file follows this structure:

```markdown
# Flag Category Name

Description of the flag category.

**Estimated tokens: ~XXX**

---

**--flag-name**
- Trigger: When to use this flag
- Behavior: What this flag does
- Related: Associated concepts
- Example: Usage example
```

## Migration from Monolithic FLAGS.md

If you're upgrading from an older version:

1. **Backup**: Save your current `~/.cortex/FLAGS.md`
2. **Install**: The new split flag files are in `~/.cortex/flags/`
3. **Update**: Replace monolithic `FLAGS.md` content with `@flags/*.md` references
4. **Migrate**: Any custom flags can be added to appropriate category files
5. **Verify**: `CLAUDE.md` still includes `@FLAGS.md`

## See Also

- [Profile Management](../reference/PROFILES.md)
- [TUI Guide](TUI_GUIDE.md)
- [CLAUDE.md Reference](../reference/CLAUDE_MD.md)
- [Token Optimization](TOKEN_OPTIMIZATION.md)
