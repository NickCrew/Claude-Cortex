# Claude-ctx Command Namespaces

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
agents: [agent1, agent2]
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

## Agent Integration

Commands can invoke specialized agents:

**Development Agents:**
- `code-reviewer` - Code quality analysis
- `refactoring-expert` - Code refactoring
- `typescript-pro` / `python-pro` - Language specialists

**Testing Agents:**
- `test-automator` - Test generation
- `quality-engineer` - Quality assurance

**Deployment Agents:**
- `deployment-engineer` - Release preparation
- `devops-architect` - Infrastructure

**Analysis Agents:**
- `security-auditor` - Security assessment
- `performance-engineer` - Performance analysis

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