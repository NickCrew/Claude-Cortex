"""Tests for cross-harness hook installation.

The same `cortex hooks <name>` subcommand can be registered against
either the Claude Code config (~/.claude/settings.json, default) or the
Codex config (~/.codex/hooks.json) via `install_hook_command(...,
target=...)`. Both files share the JSON shape `{"hooks": {<event>:
[...]}}`. These tests pin the routing.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from claude_ctx_py.hooks import install_hook_command


@pytest.mark.unit
class TestInstallTarget:
    def test_codex_target_writes_hooks_json(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """target='codex' creates ~/.codex/hooks.json with the expected entry."""
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        ok, msg = install_hook_command(
            subcommand="skill-suggest",
            event="UserPromptSubmit",
            matcher="",
            target="codex",
        )
        assert ok, msg
        config_path = tmp_path / ".codex" / "hooks.json"
        assert config_path.exists()
        data = json.loads(config_path.read_text())
        events = data["hooks"]["UserPromptSubmit"]
        assert events[0]["matcher"] == ""
        assert events[0]["hooks"][0]["command"] == "cortex hooks skill-suggest"

    def test_codex_target_idempotent(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Installing the same hook twice produces no duplicate entries."""
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        for _ in range(2):
            ok, _ = install_hook_command(
                subcommand="skill-suggest",
                event="UserPromptSubmit",
                matcher="",
                target="codex",
            )
            assert ok
        data = json.loads((tmp_path / ".codex" / "hooks.json").read_text())
        events = data["hooks"]["UserPromptSubmit"]
        # One matcher entry with one hooks entry — not two
        assert len(events) == 1
        assert len(events[0]["hooks"]) == 1

    def test_codex_target_preserves_unrelated_existing_hooks(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """An existing hooks.json entry for a different event is preserved."""
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        codex_dir = tmp_path / ".codex"
        codex_dir.mkdir()
        existing = {
            "hooks": {
                "PreToolUse": [
                    {
                        "matcher": "Bash",
                        "hooks": [
                            {"type": "command", "command": "some-other-command"}
                        ],
                    }
                ]
            }
        }
        (codex_dir / "hooks.json").write_text(json.dumps(existing))

        ok, _ = install_hook_command(
            subcommand="skill-suggest",
            event="UserPromptSubmit",
            matcher="",
            target="codex",
        )
        assert ok
        data = json.loads((codex_dir / "hooks.json").read_text())
        assert "PreToolUse" in data["hooks"]
        assert data["hooks"]["PreToolUse"][0]["hooks"][0]["command"] == "some-other-command"
        assert "UserPromptSubmit" in data["hooks"]
