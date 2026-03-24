# Watch Mode Guide

This is the developer guide for Cortex watch mode, implemented in
`claude_ctx_py/watch.py`.

For the user-facing walkthrough, see
[AI Watch Mode Tutorial](../../tutorials/ai-watch-mode.md).

## Purpose

Watch mode provides a live terminal loop that reacts to git-backed file changes
and surfaces both halves of the recommendation system:

- **agent recommendations** from `IntelligentAgent`
- **skill suggestions** from keyword rules plus optional `SkillRecommender`

## CLI Surface

```bash
cortex ai watch
cortex ai watch --daemon
cortex ai watch --status
cortex ai watch --stop
```

Useful options:

```bash
cortex ai watch --no-auto-activate
cortex ai watch --threshold 0.8
cortex ai watch --interval 5
cortex ai watch --dir ~/repo-a --dir ~/repo-b
```

## Runtime Flow

1. Poll git for staged and unstaged changes
2. Build a `SessionContext` from those files
3. Ask `IntelligentAgent` for agent recommendations
4. Run `_match_skills()` against `skills/skill-rules.json`
5. Optionally enrich skill suggestions through `SkillRecommender`
6. Print context, agents, and skills
7. Auto-activate eligible agents when enabled

## Output Model

Watch mode prints three classes of information:

### Context summary

Example:

```text
[10:33:12] Context detected: Backend, Tests, Auth
  3 files changed
```

### Agent recommendations

Only recommendations above the notification threshold are displayed.

Example:

```text
  Agent Recommendations:

     🔴 security-auditor [AUTO]
        90% - Auth code detected - security review recommended
```

### Skill suggestions

Example:

```text
  Suggested skills: secure-coding-practices, python-testing-patterns
```

## Configuration

Defaults come from `~/.cortex/cortex-config.json`:

```json
{
  "watch": {
    "directories": ["~/projects/my-app"],
    "auto_activate": true,
    "threshold": 0.7,
    "interval": 2.0
  }
}
```

CLI flags override config values.

## Daemon Behavior

`start_watch_daemon()` launches:

```text
python -m claude_ctx_py.cli ai watch ...
```

It records:

- PID in `~/.cortex/watch.pid`
- logs in `~/.cortex/logs/watch.log`

The daemon path is intentionally thin. It reuses the normal CLI watch command
rather than implementing a separate background-only engine.

## TUI Integration

The TUI may auto-start the watch daemon from `AgentTUI.on_mount()`.

Important nuance:

- the raw CLI watch command defaults to auto-activation unless disabled
- the TUI auto-start path respects configured watch defaults and otherwise falls
  back to notification-only mode

This keeps the TUI from silently auto-activating agents on first launch in an
unconfigured environment.

## Testing And Maintenance Notes

When changing watch mode, verify:

- `cortex ai watch --help`
- `cortex ai watch --status`
- foreground watch output formatting
- daemon start/stop behavior
- TUI AI Assistant messaging when watch mode is active

Keep these docs in sync:

- `docs/AI_INTELLIGENCE.md`
- `docs/tutorials/ai-watch-mode.md`
- `docs/guides/development/WATCH_MODE_ARCHITECTURE.md`
