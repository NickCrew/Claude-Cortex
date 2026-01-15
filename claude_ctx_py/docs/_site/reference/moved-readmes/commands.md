# Cortex Command Namespaces

Organized command library for efficient development workflows.

## Namespace Organization

Commands are organized by domain for better discoverability and logical grouping.

### 📦 /dev - Development Commands

Core development tasks and code management.

**Available Commands:**

- `code-review` - Comprehensive code quality review

**Usage:**

```bash
/dev:code-review [path] [--focus quality|security|performance|all]
```

---

### 🧪 /test - Testing Commands

Test generation, execution, and quality assurance.

**Available Commands:**

- `generate-tests` - Generate comprehensive test suite

**Usage:**

```bash
/test:generate-tests [path] [--type unit|integration|e2e|all] [--coverage-target 80]
```

---

### 🚀 /deploy - Deployment Commands

Release preparation and deployment automation.

**Available Commands:**

- `prepare-release` - Prepare application for production deployment

**Usage:**

```bash
/deploy:prepare-release [version] [--type major|minor|patch]
```

---

### 🔍 /analyze - Analysis Commands

Code analysis, security scanning, and optimization.

**Available Commands:**

- `security-scan` - Comprehensive security vulnerability assessment

**Usage:**

```bash
/analyze:security-scan [path] [--standard OWASP|GDPR|SOC2|HIPAA]
```

---

## Using Commands

### Via Claude Code Chat

Simply type the command in the chat:

```
/dev:code-review src/components
```

### Via CLI (Future)

```bash
claude-ctx cmd dev:code-review src/components
claude-ctx cmd test:generate-tests --coverage-target 90
```

## Command Structure

Each command file includes:

```yaml
---
name: command-name
description: What the command does
category: namespace
personas: [thinking, modes]           # Conceptual guidance
subagents: [claude, code, workers]   # Task tool delegation targets
mcp-servers: [external, integrations] # Optional MCP integrations
---

# Command Documentation
...
```

## Creating Custom Commands

1. Choose the appropriate namespace:
   - `/dev` - Development and code tasks
   - `/test` - Testing operations
   - `/deploy` - Deployment and release
   - `/analyze` - Analysis and auditing

2. Create a markdown file:

   ```bash
   touch ~/.claude/commands/[namespace]/[command-name].md
   ```

3. Follow the template structure:
   - YAML frontmatter with metadata
   - Purpose and triggers
   - Usage instructions
   - Detailed process steps
   - Output format
   - Examples

## Execution Architecture

Commands coordinate two types of guidance:

### Personas (Thinking Modes)

Conceptual roles that guide Claude's perspective and decision-making:

- `architect` - System design thinking
- `frontend` - UI/UX focus
- `backend` - API and data modeling
- `security` - Security-first mindset
- `qa-specialist` - Quality standards

*Personas influence HOW Claude thinks, not WHAT tools are used.*

### Subagents (Workers via Task Tool)

Specialized agents launched via Claude Code's Task tool for complex work:

**Development Subagents:**

- `general-purpose` - Versatile implementation work
- `code-reviewer` - Code quality and security analysis
- `typescript-pro` / `python-pro` - Language specialists

**Testing Subagents:**

- `test-automator` - Test generation and execution
- `quality-engineer` - Quality assurance

**Deployment Subagents:**

- `deployment-engineer` - Release preparation
- `devops-architect` - Infrastructure

**Analysis Subagents:**

- `Explore` - Codebase exploration and discovery
- `security-auditor` - Security assessment
- `performance-engineer` - Performance analysis

**When commands delegate** (use Task tool to launch subagents):

- ✅ Complex operations (>3 files, >5 steps)
- ✅ Multi-domain work (code + tests + docs)
- ✅ Parallel workstreams possible
- ✅ User needs progress visibility

**When commands use direct tools**:

- Simple operations (1-2 files)
- Quick reads/searches
- Atomic changes

See: [`docs/architecture/terminology.md`](../docs/architecture/terminology.md) for complete architecture explanation.

## Best Practices

1. **Clear Naming** - Use descriptive, action-oriented names
2. **Focused Purpose** - Each command does one thing well
3. **Consistent Structure** - Follow the template format
4. **Agent Composition** - Leverage multiple agents when needed
5. **Documentation** - Provide clear usage examples

## Future Namespaces

Planned additions:

- `/docs` - Documentation generation
- `/optimize` - Performance optimization
- `/refactor` - Code refactoring
- `/monitor` - Application monitoring
