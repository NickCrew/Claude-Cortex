<p align="center">
  <img src="docs/assets/images/cortex-banner.png" alt="Cortex — Multi-Model Development Orchestration" width="100%" />
</p>

<p align="center">
  <a href="https://github.com/NickCrew/claude-cortex/actions/workflows/test.yml"><img src="https://github.com/NickCrew/claude-cortex/actions/workflows/test.yml/badge.svg" alt="Tests" /></a>
  <a href="https://github.com/NickCrew/claude-cortex/actions/workflows/type-check.yml"><img src="https://github.com/NickCrew/claude-cortex/actions/workflows/type-check.yml/badge.svg" alt="Type Check" /></a>
  <a href="https://pypi.org/project/claude-cortex/"><img src="https://img.shields.io/pypi/v/claude-cortex" alt="PyPI" /></a>
  <a href="https://github.com/NickCrew/claude-cortex/blob/main/LICENSE"><img src="https://img.shields.io/github/license/NickCrew/claude-cortex" alt="License" /></a>
</p>

<p align="center">
  Multi-model development orchestration for Claude Code, Codex, and Gemini.
</p>

<p align="center">
  <a href="https://cortex.atlascrew.dev/">Documentation</a> &middot;
  <a href="#install">Install</a> &middot;
  <a href="#quick-start">Quick Start</a>
</p>

---

Cortex is a development orchestration framework that coordinates AI agents across model providers. It enforces quality gates — independent code review, test coverage audits, and lint checks — so that no agent grades its own homework. The result is a structured, auditable development workflow where Claude, Codex, and Gemini collaborate with built-in verification at every step.

## How It Works

### Multi-model review with no self-review

Cortex's core principle: **the agent that writes the code never reviews it.** When Codex implements a feature, the review is routed to Claude first, then to a different model family, with same-model review as a last resort. Every review produces a structured artifact with severity levels and a pass/fail verdict.

```
Codex implements → Claude reviews → Codex remediates → Claude re-reviews
                   ↓ (unavailable)
                   Gemini reviews (fallback)
                   ↓ (unavailable)
                   Fresh-context Codex reviews (last resort)
```

### Agent-loops: progressive quality gates

Every code change flows through three sequential loops, each with circuit breakers and escalation rules:

```
Code Change Loop    →  Implement → Independent review → Remediate P0/P1 → Re-review (max 3 cycles)
Test Writing Loop   →  Audit gaps → Write tests → Verify → Re-audit (max 3 cycles)
Lint Gate           →  Discover linter → Auto-fix → Check → Remediate (max 2 cycles)
```

P0/P1 findings must be resolved before the loop exits. P2/P3 findings are filed as issues automatically. If circuit breakers trigger, the agent stops and escalates to a human — no infinite remediation loops.

### Skill recommendations

Skills are suggested automatically as you work via a two-layer pipeline: fast keyword matching on every prompt (~50ms), with optional semantic matching for deeper recommendations. The TUI runs a background watch daemon for continuous suggestions.

## What's Inside

| Path | Purpose |
|---|---|
| `agents/` | Agent definitions (specialized reviewers, implementers) |
| `skills/` | Reusable skill modules — workflow guidance, review prompts, quality standards |
| `rules/` | Behavioral guardrails and coding conventions |
| `hooks/` | Automation hooks (skill suggestions, validation gates) |
| `claude_ctx_py/` | Python CLI and TUI implementation |

### Key skills

- **`agent-loops`** — The core workflow: structured implementation with independent review, test audit, and lint gates. Includes provider-aware review scripts with fallback chains.
- **`test-review`** — Test quality and coverage auditing across modules.
- **`doc-claim-validator`** — Validates documentation claims against actual code.
- **`doc-maintenance`** — Systematic documentation audit and lifecycle management.

## Install

### macOS (Homebrew)

```bash
brew tap NickCrew/cortex
brew install cortex
```

`post_install` symlinks bundled agents, skills, rules, and schemas into
`~/.claude/` automatically. Opt out with `CORTEX_SKIP_LINK=1 brew install cortex`.

### Python (any platform)

```bash
# Recommended
pipx install claude-cortex

# Alternative
pip install claude-cortex
```

If you install via Homebrew **and** pip, whichever binary comes first in your
`$PATH` wins. Uninstall one to avoid ambiguity.

### Development

```bash
git clone https://github.com/NickCrew/claude-cortex.git
cd claude-cortex
pip install -e ".[dev]"
```

## Quick Start

```bash
cortex install link          # Symlink bundled assets into ~/.claude
cortex install post          # Shell completions + man pages (optional)
cortex status                # Check what's active
cortex tui                   # Launch the terminal UI
```

## CLI Overview

```bash
cortex <command> [options]
```

| Command | What it does |
|---|---|
| `status` | Show active agents, rules, hooks, skills |
| `agent list\|status` | Manage agent definitions |
| `skills list\|info\|recommend` | Discover and inspect skills |
| `rules list\|activate` | Manage behavioral rules |
| `hooks list\|install` | Install and validate hooks |
| `mcp list\|diagnose` | MCP server discovery and diagnostics |
| `ai recommend\|watch` | AI-powered skill recommendations |
| `review` | Run review workflows |
| `tui` | Launch terminal UI |
| `docs` | Browse bundled documentation |
| `install\|uninstall` | Manage Cortex installation |

Run `cortex --help` or `cortex <command> --help` for details.

## Development

```bash
just test                    # Run test suite
just lint                    # Check formatting (Black)
just type-check              # Strict mypy
just docs                    # Serve docs locally
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Documentation

Full documentation at **[cortex.atlascrew.dev](https://cortex.atlascrew.dev/)**.

- [Getting Started](docs/guides/getting-started.md)
- [Commands Reference](docs/guides/commands.md)
- [Skills Guide](docs/guides/skills.md)
- [Architecture](docs/architecture/README.md)
- [Skill Recommendation Engine](docs/architecture/skill-recommendation-engine.md)
- [CHANGELOG](CHANGELOG.md)

## License

MIT. See [LICENSE](LICENSE).
