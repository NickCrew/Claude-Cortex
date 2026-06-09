---
layout: default
title: Statusline Reference
parent: Reference
nav_order: 7
---

# Statusline Reference

Cortex ships a custom Claude Code status line that renders context-window usage,
session duration, token throughput, git state, rate-limit headroom, and the
active model on a compact multi-line display. This page documents how to enable
it, the `statusline.yaml` configuration keys, and the runtime environment
variables it reads.

## Enabling the statusline

Cortex writes the `statusLine` command into Claude Code's `settings.json`:

```sh
cortex install statusline                         # uses "cortex statusline --color"
cortex install statusline --command "cortex statusline -f oneline"
cortex install statusline --force                 # overwrite an existing entry
```

This sets `"statusLine": "cortex statusline --color"` in the resolved
`<claude-dir>/settings.json`. Claude Code invokes that command on each render,
piping a JSON status payload on stdin; the command prints the formatted line(s)
to stdout.

{: .note }
> The wizard (`cortex` first-run setup) also offers to configure the statusline.
> An existing `statusLine` entry is left untouched unless you pass `--force`.

## Configuration file

| File | Location | Format |
|:-----|:---------|:-------|
| `statusline.yaml` | `<claude-dir>/statusline.yaml` (default `~/.claude/statusline.yaml`) | YAML (falls back to JSON if PyYAML is unavailable) |

`<claude-dir>` is the resolved `.claude/` directory — see the
[Configuration Reference]({{ '/reference/configuration/' | relative_url }})
Resolution Model. Write a defaults file you can edit with:

```sh
cortex statusline --init-config
```

Any keys you omit fall back to the built-in defaults below, so the file only
needs the keys you want to change.

### Top-level keys

| Key | Type | Default | Description |
|:----|:-----|:--------|:------------|
| `show_git` | bool | `true` | Render the git segment (branch, ahead/behind, dirty counts) |
| `show_venv` | bool | `true` | Render the active Python virtualenv |
| `show_kube` | bool | `false` | Render the current Kubernetes context |
| `show_aws` | bool | `false` | Render the active AWS profile/region |
| `show_docker` | bool | `false` | Render the current Docker context |
| `show_node` | bool | `false` | Render the active Node.js version |
| `show_cost` | `"auto"` \| bool | `"auto"` | Cost segment visibility — see [Cost display](#cost-display) |
| `cache_ttl` | int | `5` | Seconds to cache expensive probes (git, etc.); `0` disables caching |
| `separator` | string | `" \| "` | String placed between segments on a line |
| `icons` | map | *(see below)* | Per-segment glyph overrides |

### Git extras

These refine the git segment and apply only when `show_git` is `true`. The
worktree indicator and last-commit age are always shown.

| Key | Type | Default | Description |
|:----|:-----|:--------|:------------|
| `git_show_conflicts` | bool | `true` | Show a count of conflicted paths during a merge |
| `git_show_state` | bool | `true` | Show in-progress operations (merge, rebase, cherry-pick, bisect) |
| `git_show_tag` | bool | `false` | Show the nearest tag |
| `git_show_assume_unchanged` | bool | `false` | Show a count of assume-unchanged paths |
| `git_show_submodules` | bool | `false` | Show a count of dirty submodules |

### Icons

`icons` is a map of segment name to glyph. Override individual entries; unset
keys keep their defaults. Recognized keys: `dir`, `git`, `tokens`, `in_tokens`,
`out_tokens`, `added`, `removed`, `model`, `kube`, `aws`, `docker`, `python`,
`node`, `worktree`, `conflict`, `state`, `tag`, `time`, `cache`, `output_style`.

{: .note }
> Most icons are [Nerd Font](https://www.nerdfonts.com/) glyphs. If your
> terminal font lacks them, override the relevant `icons` keys with plain ASCII
> or emoji.

### Example `statusline.yaml`

```yaml
show_git: true
show_venv: true
show_node: true        # opt in to the Node version segment
show_cost: auto        # hidden on a subscription, shown under metered billing
cache_ttl: 5
separator: "  •  "
icons:
  dir: ""
  model: ""
```

## Cost display

The cost segment shows the session's running spend. Because that figure is only
money actually charged under **metered, per-token billing**, the segment is
suppressed by default on subscription (Pro/Max) sessions — there, Claude Code
reports what the usage *would* cost on the API, not what you are billed.

`show_cost` controls the behavior:

| Value | Behavior |
|:------|:---------|
| `"auto"` *(default)* | Show the cost only when metered billing is detected (see below) |
| `true` | Always show the cost |
| `false` | Never show the cost |

### Billing detection

Claude Code's statusline payload carries no auth-method field, so detection is
based on the environment the statusline subprocess inherits. The cost segment
renders under `"auto"` when **any** of these is set:

| Variable | Billing path |
|:---------|:-------------|
| `ANTHROPIC_API_KEY` | Direct Anthropic API key |
| `ANTHROPIC_AUTH_TOKEN` | Gateway / proxy auth token |
| `CLAUDE_CODE_USE_BEDROCK` | AWS Bedrock |
| `CLAUDE_CODE_USE_VERTEX` | GCP Vertex AI |

Under Bedrock the displayed amount is scaled by 1.25× and tagged `(b5k)`.

{: .important }
> An API key configured through `/login` is stored in Claude Code's credential
> store, **not** exported to the environment — so `"auto"` cannot detect it and
> the cost stays hidden. Set `show_cost: true` in `statusline.yaml` to force the
> segment on for that setup.

## Command-line options

`cortex statusline` accepts overrides that take precedence over `statusline.yaml`
for a single invocation. These are most useful when embedding the command with
flags in the `statusLine` setting.

| Flag | Description |
|:-----|:------------|
| `-f`, `--format {default,oneline,json}` | Output format (default: `default`) |
| `--color` / `--no-color` | Force ANSI colors on / off (auto-disabled when stdout is not a TTY) |
| `--git` / `--no-git` | Override `show_git` |
| `--venv` / `--no-venv` | Override `show_venv` |
| `--kube` / `--no-kube` | Override `show_kube` |
| `--aws` / `--no-aws` | Override `show_aws` |
| `--docker` / `--no-docker` | Override `show_docker` |
| `--node` / `--no-node` | Override `show_node` |
| `--init-config` | Write the default `statusline.yaml` and exit |

### Output formats

| Format | Use |
|:-------|:----|
| `default` | Multi-line display for the Claude Code status line |
| `oneline` | Single line for tmux / i3bar embedding |
| `json` | Machine-readable fields for scripting (always includes `cost_usd`) |

{: .note }
> The `json` format always emits `cost_usd` regardless of `show_cost` — the key
> is a billing-display preference for the visual line, not a data filter.
