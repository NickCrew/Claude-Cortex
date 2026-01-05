# Create plugins

> Build a Claude Code plugin by organizing commands, agents, hooks, and optional servers under a single plugin root.

## Quick layout

```text
your-plugin/
├── .claude-plugin/
│   └── plugin.json
├── commands/
├── agents/
├── hooks/
│   └── hooks.json
└── scripts/
```

## Hook configuration

Keep hook configuration in `hooks/hooks.json` at the plugin root (not in `settings.json`). Use `${CLAUDE_PLUGIN_ROOT}` for any file paths so hooks resolve correctly no matter where the plugin is installed.

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "python3",
            "args": [
              "${CLAUDE_PLUGIN_ROOT}/hooks/examples/skill_auto_suggester.py"
            ]
          }
        ]
      }
    ]
  }
}
```

## Reference the hooks file

Point the plugin manifest at the hooks file:

```json
{
  "name": "your-plugin",
  "version": "0.1.0",
  "hooks": "./hooks/hooks.json"
}
```
