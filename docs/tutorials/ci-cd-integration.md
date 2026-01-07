---
layout: default
title: CI/CD Integration
parent: Tutorials
nav_order: 5
permalink: /tutorials/ci-cd-integration/
---

# CI/CD Integration Tutorial

Integrate cortex with your continuous integration and deployment pipelines for automated context validation and workflow execution.

## What You'll Learn

By the end of this tutorial, you'll be able to:

- Add cortex validation to CI pipelines
- Automate context exports for build artifacts
- Create GitHub Actions workflows with cortex
- Integrate with semantic versioning
- Set up automated testing gates

**Time Estimate:** 25-30 minutes
**Prerequisites:** Familiarity with GitHub Actions or similar CI systems

---

## Part 1: CI Pipeline Basics

### Why Integrate cortex in CI?

| Benefit | Description |
|---------|-------------|
| **Validation** | Ensure configurations are valid before merge |
| **Consistency** | Verify agent/mode/skill setups across environments |
| **Automation** | Auto-export context for releases |
| **Quality Gates** | Block merges with invalid scenarios |

### Installation in CI

```yaml
# GitHub Actions example
- name: Install cortex
  run: |
    pip install claude-cortex
    # Or for development version:
    # pip install git+https://github.com/yourrepo/cortex-plugin.git
```

---

## Part 2: Basic Validation Workflow

### Validate on Pull Requests

Create `.github/workflows/cortex-validate.yml`:

```yaml
name: cortex Validation

on:
  pull_request:
    branches: [main, develop]
    paths:
      - '.claude/**'
      - 'agents/**'
      - 'modes/**'
      - 'skills/**'
      - 'scenarios/**'

jobs:
  validate:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install cortex
        run: pip install claude-cortex

      - name: Validate agents
        run: |
          echo "Validating agent configurations..."
          for agent in agents/*.md; do
            if [ -f "$agent" ]; then
              echo "Checking: $agent"
              # Verify YAML frontmatter if present
              head -50 "$agent" | grep -q "^---" && echo "  Has frontmatter"
            fi
          done

      - name: Validate scenarios
        run: |
          if [ -d "scenarios" ]; then
            cortex orchestrate validate --all
          fi

      - name: Check configuration syntax
        run: |
          # Validate YAML files
          for yaml in .claude/**/*.yaml scenarios/*.yaml; do
            if [ -f "$yaml" ]; then
              python -c "import yaml; yaml.safe_load(open('$yaml'))" || exit 1
              echo "Valid: $yaml"
            fi
          done
```

### What This Validates

1. **Agent files** - Check for valid markdown structure
2. **Scenarios** - Full schema validation via `orchestrate validate`
3. **YAML syntax** - All configuration files parse correctly

---

## Part 3: Type Checking and Tests

### Combined Validation and Type Check

```yaml
name: Full Validation

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  validate-and-test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.9', '3.10', '3.11', '3.12']

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e ".[dev]"

      - name: Run type checking
        run: |
          mypy claude_ctx_py/ --ignore-missing-imports

      - name: Run unit tests
        run: |
          pytest tests/unit/ -v --tb=short

      - name: Run integration tests
        run: |
          pytest tests/integration/ -v --tb=short

      - name: Check coverage
        run: |
          pytest --cov=claude_ctx_py --cov-fail-under=80
```

---

## Part 4: Context Export for Releases

### Export Context as Build Artifact

```yaml
name: Release Build

on:
  push:
    tags:
      - 'v*'

jobs:
  build-with-context:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install cortex
        run: pip install claude-cortex

      - name: Export context snapshot
        run: |
          # Create context export directory
          mkdir -p dist/context

          # Export current configuration
          cortex export context \
            --output dist/context/context-snapshot.md \
            --format markdown

          # Export agent graph
          cortex agent graph \
            --output dist/context/agent-dependencies.md

          # Export active configuration
          cortex status --json > dist/context/status.json

      - name: Upload context artifacts
        uses: actions/upload-artifact@v4
        with:
          name: context-snapshot
          path: dist/context/

      - name: Build package
        run: python -m build

      - name: Upload package artifacts
        uses: actions/upload-artifact@v4
        with:
          name: python-package
          path: dist/*.whl
```

---

## Part 5: Semantic Versioning Integration

### Automated Releases with Validation

```yaml
name: Semantic Release

on:
  push:
    branches:
      - main
  workflow_dispatch:

permissions:
  contents: write

jobs:
  release:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install ".[dev]"

      - name: Validate before release
        run: |
          # Run full test suite
          pytest -m "unit and not slow"

          # Validate all scenarios
          if [ -d "scenarios" ]; then
            cortex orchestrate validate --all
          fi

      - name: Python Semantic Release
        id: release
        uses: python-semantic-release/python-semantic-release@v10
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          build: false

      - name: Export release context
        if: ${{ steps.release.outputs.released == 'true' }}
        run: |
          # Tag the context state
          cortex export context \
            --output RELEASE_CONTEXT.md \
            --format markdown

      - name: Build distribution
        if: ${{ steps.release.outputs.released == 'true' }}
        run: python -m build

      - name: Publish to PyPI
        if: ${{ steps.release.outputs.released == 'true' }}
        uses: pypa/gh-action-pypi-publish@v1
        with:
          password: ${{ secrets.PYPI_API_TOKEN }}
```

---

## Part 6: Quality Gates

### Block Merges on Invalid Configuration

```yaml
name: Quality Gate

on:
  pull_request:
    branches: [main]

jobs:
  quality-gate:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install claude-cortex pyyaml

      - name: Validate scenario syntax
        id: scenarios
        run: |
          if [ -d "scenarios" ]; then
            cortex orchestrate validate --all 2>&1 | tee validation.log
            if grep -q "ERROR" validation.log; then
              echo "scenario_valid=false" >> $GITHUB_OUTPUT
              exit 1
            fi
          fi
          echo "scenario_valid=true" >> $GITHUB_OUTPUT

      - name: Check agent dependencies
        id: agents
        run: |
          # Verify no circular dependencies
          cortex agent graph --check-cycles
          echo "agents_valid=true" >> $GITHUB_OUTPUT

      - name: Validate YAML schemas
        run: |
          python << 'EOF'
          import yaml
          import sys
          from pathlib import Path

          errors = []
          for pattern in ['scenarios/*.yaml', '.claude/**/*.yaml']:
              for path in Path('.').glob(pattern):
                  try:
                      yaml.safe_load(path.read_text())
                      print(f"OK: {path}")
                  except yaml.YAMLError as e:
                      errors.append(f"FAIL: {path} - {e}")

          if errors:
              for err in errors:
                  print(err)
              sys.exit(1)
          EOF

      - name: Post status comment
        if: always()
        uses: actions/github-script@v7
        with:
          script: |
            const scenarioValid = '${{ steps.scenarios.outputs.scenario_valid }}' === 'true';
            const agentsValid = '${{ steps.agents.outputs.agents_valid }}' === 'true';

            const body = `## Quality Gate Results

            | Check | Status |
            |-------|--------|
            | Scenarios | ${scenarioValid ? '✅ Valid' : '❌ Invalid'} |
            | Agents | ${agentsValid ? '✅ Valid' : '❌ Invalid'} |

            ${!scenarioValid || !agentsValid ? '⚠️ Please fix the issues above before merging.' : '✅ All checks passed!'}
            `;

            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: body
            });
```

---

## Part 7: Advanced Patterns

### Matrix Testing for Multiple Configurations

```yaml
name: Configuration Matrix

on: [push, pull_request]

jobs:
  test-configs:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        config:
          - name: minimal
            profile: minimal
          - name: development
            profile: development
          - name: production
            profile: production

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install cortex
        run: pip install claude-cortex

      - name: Test with ${{ matrix.config.name }} profile
        run: |
          # Apply profile
          cortex profile apply ${{ matrix.config.profile }}

          # Verify configuration loads
          cortex status

          # Run profile-specific tests
          pytest tests/ -k "${{ matrix.config.name }}" -v
```

### Scheduled Health Checks

```yaml
name: Scheduled Health Check

on:
  schedule:
    # Run daily at 6 AM UTC
    - cron: '0 6 * * *'
  workflow_dispatch:

jobs:
  health-check:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install cortex
        run: pip install claude-cortex

      - name: Run health checks
        run: |
          # Check for outdated configurations
          echo "=== Configuration Health ==="
          cortex status --json | python -c "
          import json, sys
          data = json.load(sys.stdin)
          print(f'Active agents: {len(data.get(\"agents\", []))}')
          print(f'Active modes: {len(data.get(\"modes\", []))}')
          print(f'Active skills: {len(data.get(\"skills\", []))}')
          "

          # Validate all configurations still valid
          if [ -d "scenarios" ]; then
            cortex orchestrate validate --all
          fi

      - name: Create issue on failure
        if: failure()
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: 'Daily Health Check Failed',
              body: `The scheduled health check failed. Please investigate.

              Workflow run: ${context.serverUrl}/${context.repo.owner}/${context.repo.repo}/actions/runs/${context.runId}
              `,
              labels: ['bug', 'health-check']
            });
```

---

## Part 8: Local Development Hooks

### Pre-commit Validation

Add to `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: validate-cortex
        name: Validate cortex configurations
        entry: python -c "
          import subprocess
          import sys
          result = subprocess.run(['cortex', 'orchestrate', 'validate', '--all'],
                                  capture_output=True, text=True)
          if result.returncode != 0:
              print(result.stderr)
              sys.exit(1)
          print('cortex configurations valid')
          "
        language: system
        pass_filenames: false
        files: ^(scenarios/|\.claude/|agents/|modes/).*\.(yaml|yml|md)$

      - id: validate-yaml
        name: Validate YAML syntax
        entry: python -c "
          import yaml
          import sys
          for path in sys.argv[1:]:
              try:
                  yaml.safe_load(open(path))
              except yaml.YAMLError as e:
                  print(f'Invalid YAML in {path}: {e}')
                  sys.exit(1)
          "
        language: system
        types: [yaml]
```

### Git Hooks for Scenarios

Create `.git/hooks/pre-push`:

```bash
#!/bin/bash

# Validate scenarios before push
if [ -d "scenarios" ]; then
    echo "Validating scenarios..."
    if ! cortex orchestrate validate --all; then
        echo "ERROR: Invalid scenarios detected. Push aborted."
        exit 1
    fi
fi

echo "All validations passed!"
```

---

## Troubleshooting

### Common CI Issues

**Module not found:**
```yaml
# Ensure proper installation
- name: Install with all dependencies
  run: pip install "claude-cortex[all]"
```

**Permission denied:**
```yaml
# Add proper permissions for release
permissions:
  contents: write
  packages: write
```

**YAML validation fails silently:**
```yaml
# Add verbose output
- name: Validate with verbose
  run: |
    set -x  # Enable command tracing
    cortex orchestrate validate --all --verbose
```

**Cache for faster builds:**
```yaml
- name: Cache pip packages
  uses: actions/cache@v4
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements*.txt') }}
```

---

## Summary

You've learned how to:

- Add cortex validation to CI pipelines
- Create quality gates that block invalid configurations
- Export context snapshots for releases
- Integrate with semantic versioning
- Set up scheduled health checks
- Use pre-commit hooks for local validation

**Next Steps:**
- [Workflow Orchestration](../workflow-orchestration/) - Complex scenario management
- [Skill Authoring](../skill-authoring-cookbook/) - Create custom skills
- [AI Watch Mode](../ai-watch-mode/) - Intelligent recommendations

---

## Quick Reference

### GitHub Actions Examples

```yaml
# Basic validation
cortex orchestrate validate --all

# Export context
cortex export context --output context.md

# Check agent graph
cortex agent graph --check-cycles

# Apply profile
cortex profile apply production

# Get status as JSON
cortex status --json
```

### Quality Gate Checklist

- [ ] Scenario syntax validation
- [ ] YAML schema compliance
- [ ] Agent dependency check
- [ ] Type checking (mypy)
- [ ] Unit tests passing
- [ ] Integration tests passing
- [ ] Coverage threshold met
