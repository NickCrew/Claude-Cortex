---
layout: default
title: bin/ Utilities
parent: Reference
nav_order: 5
summary: Standalone scripts and CLI helpers in the bin/ directory
read_when:
  - Using tmux with agents
  - Running Chrome DevTools automation
  - Auditing skill quality
  - Working with Claude Skills API or Files API
  - Making safe git commits from scripts
---

# bin/ Utilities

Agent-facing tools for routine development work. These are the scripts agents (and humans) reach for during day-to-day sessions — tmux interaction, browser automation, safe commits, and Claude API helpers. They live in `bin/` and can be run directly or sourced into your shell.

> For project-internal maintenance scripts (manpage generation, registry validation, uninstall), see [scripts/ Utilities](scripts-utilities.md).

## Overview

| Script | Language | Purpose |
|--------|----------|---------|
| [`tx`](#tx) | Bash | Tmux helper for agents — send commands, read output, wait for completion |
| [`browser_tools.ts`](#browser_toolsts) | TypeScript | Chrome DevTools automation without MCP |
| [`committer`](#committer) | Bash | Safe git commit wrapper with guardrails |
| [`claude_wrapper.sh`](#claude_wrappersh) | Zsh | Terminal title management for Claude sessions |
| [`cortex_statusline.py`](#cortex_statuslinepy) | Python | Status line for Powerlevel10k-style prompts |
| [`audit_skill.py`](#audit_skillpy) | Python | Skill quality auditor with scoring and recommendations |
| [`file_utils.py`](#file_utilspy) | Python | Claude Files API helpers (extract, download, save) |
| [`skill_utils.py`](#skill_utilspy) | Python | Claude Skills API helpers (create, list, test, delete) |
| [`docs_list.ts`](#docs_listts) | TypeScript | List docs with frontmatter metadata for context loading |

---

## tx

Tmux helper for agents. Manages windows, sends commands, reads output, and waits for processes — designed for agent workflows that need to interact with long-running processes in other terminal panes.

**Requires:** tmux, a running session (default: `labs`, override with `TMUX_SESSION`).

### Usage

```bash
tx <command> [args]
```

### Commands

**Window management:**

| Command | Description |
|---------|-------------|
| `tx list` | List windows in the session |
| `tx new <window>` | Create a new window |
| `tx kill <window>` | Kill a window |

**Sending input:**

| Command | Description |
|---------|-------------|
| `tx send <window> <cmd>` | Send a command (presses Enter) |
| `tx type <window> <text>` | Type text without pressing Enter |
| `tx keys <window> <keys>` | Send key sequence (e.g., `C-c`, `Enter`, `Up`) |
| `tx interrupt <window>` | Send Ctrl-C |

**Reading output:**

| Command | Description |
|---------|-------------|
| `tx read <window> [lines]` | Capture last N lines (default: 50) |
| `tx tail <window> [lines]` | Alias for `read` |
| `tx dump <window>` | Dump entire scrollback buffer |
| `tx watch <window> [pattern]` | Wait for pattern to appear (or prompt if no pattern) |

**Process status:**

| Command | Description |
|---------|-------------|
| `tx status <window>` | Check if window exists and show last line |
| `tx running <window>` | Exit 0 if command appears running, 1 if at prompt |
| `tx wait <window> [timeout]` | Wait for command to complete (default: 60s) |

### Examples

```bash
# Start a build in another window and wait for it
tx send synapse-pingora "cargo build"
tx wait synapse-pingora 120

# Check output
tx read synapse-pingora 20

# Watch for a specific pattern
tx watch synapse-pingora "Finished"

# Interrupt a running process
tx interrupt synapse-pingora
```

---

## browser_tools.ts

Lightweight Chrome DevTools helpers using Puppeteer. Drives Chrome directly via the DevTools protocol without requiring an MCP server.

**Requires:** Node.js, `tsx` or `ts-node`, `puppeteer-core`, `commander`.

### Usage

```bash
./bin/browser_tools.ts <command> [args]
```

### Commands

| Command | Description |
|---------|-------------|
| `start` | Launch Chrome with remote debugging enabled |
| `nav <url>` | Navigate the current tab or open a new tab |
| `eval <code>` | Evaluate JavaScript in the active page context |
| `screenshot` | Capture the current viewport and print the temp PNG path |
| `pick <message>` | Interactive DOM picker — prints metadata for clicked elements |
| `console` | Capture and display console logs from the active tab |
| `search <query>` | Google search with optional readable content extraction |
| `content <url>` | Extract readable content from a URL as markdown-like text |
| `cookies` | Dump cookies from the active tab as JSON |
| `inspect` | List Chrome processes with DevTools ports and their open tabs |
| `kill` | Terminate Chrome instances that have DevTools ports open |

### Options for `start`

| Option | Default | Description |
|--------|---------|-------------|
| `-p, --port` | `9222` | Remote debugging port |
| `--profile` | `false` | Copy default Chrome profile before launch |
| `--profile-dir` | `~/.cache/scraping` | Directory for the temporary Chrome profile |
| `--chrome-path` | `/Applications/Google Chrome.app/...` | Path to Chrome binary |
| `--kill-existing` | `false` | Stop any running Chrome before launch |

### Examples

```bash
# Start Chrome with debugging
./bin/browser_tools.ts start

# Navigate and screenshot
./bin/browser_tools.ts nav https://example.com
./bin/browser_tools.ts screenshot

# Extract page content as text
./bin/browser_tools.ts content https://example.com

# Run JavaScript in the page
./bin/browser_tools.ts eval "document.title"
```

---

## committer

Safe git commit wrapper with guardrails. Prevents common mistakes: empty messages, staging entire repos, committing directories.

### Usage

```bash
committer [--force] "commit message" file1 [file2 ...]
```

### Behavior

1. Validates the commit message is non-empty and not a file path.
2. Rejects `.` (staging everything) and directory paths.
3. Unstages all files first (`git restore --staged :/`), then stages only the listed files.
4. Attempts `git commit`. If it fails with a stale lock and `--force` is set, removes the lock file and retries.
5. Reports the number of files committed.

### Options

| Option | Description |
|--------|-------------|
| `--force` | Remove stale `.git/index.lock` on commit failure and retry |

### Examples

```bash
# Commit specific files
committer "fix(auth): prevent token refresh race" src/auth.py tests/test_auth.py

# Force past a stale lock
committer --force "chore: update deps" requirements.txt
```

---

## claude_wrapper.sh

Zsh shell function that wraps Claude Code with terminal title management. Prevents Claude from overwriting your terminal title during a session.

### Usage

Source it in your `.zshrc`:

```bash
source /path/to/bin/claude_wrapper.sh
```

Then use `cly` instead of `claude`:

```bash
cly                    # launch Claude with title management
cly --resume           # resume with title management
```

### What it does

- Sets the terminal title to `<folder> — Claude` while Claude runs.
- Spawns a background process that resets the title every 0.5s (prevents Claude from changing it).
- Restores the normal directory title on exit.
- Runs Claude with `--dangerously-skip-permissions`.

---

## cortex_statusline.py

Thin entry point for the cortex status line, designed for Powerlevel10k-style terminal prompts.

### Usage

```bash
python3 bin/cortex_statusline.py
```

Delegates to `claude_ctx_py.statusline.main()`. See the cortex Python package for configuration details.

---

## audit_skill.py

Audits skills for quality, completeness, and adherence to standards. Generates scored reports with actionable recommendations.

### Usage

```bash
python3 bin/audit_skill.py <skill-name>
python3 bin/audit_skill.py <skill-name> --quick
python3 bin/audit_skill.py <skill-name> --full --output report.md
```

### Scoring dimensions

| Dimension | Weight | What it checks |
|-----------|--------|----------------|
| Clarity | 25% | Writing quality, structure, readability |
| Completeness | 25% | Required sections present, metadata populated |
| Accuracy | 30% | Claims match code, examples work |
| Usefulness | 20% | Practical value, actionable guidance |

### Required sections

Skills are checked for these sections: "When to Use", "Core Principles". Recommended: "Implementation Patterns", "Best Practices", "Anti-Patterns", "Troubleshooting".

### Required metadata

Frontmatter must include `name` and `description`. Recommended: `author`, `version`, `tags`, `triggers`.

---

## file_utils.py

Python utility library for working with the Claude Files API. Not a standalone CLI — import it in your scripts.

### Functions

| Function | Description |
|----------|-------------|
| `extract_file_ids(response)` | Extract all file IDs from a Claude API response |
| *(additional helpers)* | Download files, save to disk |

### Example

```python
from file_utils import extract_file_ids

response = client.beta.messages.create(...)
file_ids = extract_file_ids(response)
```

**Requires:** `anthropic` Python package.

---

## skill_utils.py

Python utility library for managing custom skills with the Claude Skills API. Not a standalone CLI — import it in your scripts.

### Functions

| Function | Description |
|----------|-------------|
| `create_skill(client, skill_path, display_title)` | Create a skill from a directory containing `SKILL.md` |
| *(additional helpers)* | List, retrieve, version, test, and delete skills |

### Example

```python
from skill_utils import create_skill

client = Anthropic(api_key="...", default_headers={"anthropic-beta": "skills-2025-10-02"})
result = create_skill(client, "custom_skills/financial_analyzer", "Financial Analyzer")
```

**Requires:** `anthropic` Python package.

---

## docs_list.ts

TypeScript script that walks the `docs/` directory, extracts frontmatter metadata (`summary`, `read_when`), and prints a catalog. Used by agents to discover which docs to read before starting work.

### Usage

```bash
npx tsx bin/docs_list.ts
```

### Output format

```
guides/skills.md - Progressive disclosure architecture for specialized knowledge
  Read when: creating new skills; reviewing skill quality
reference/configuration.md - All configuration files with schemas and examples
  Read when: modifying cortex settings
```

Excludes `docs/archive/` and `docs/research/` directories. Files missing frontmatter are flagged with the reason (e.g., `[missing front matter]`, `[summary key missing]`).
