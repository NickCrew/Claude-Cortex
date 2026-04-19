"""Unit tests for claude_ctx_py.hooks.install_hook_command."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from claude_ctx_py.hooks import install_hook_command


@pytest.fixture
def settings_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Redirect load_settings/save_settings to a temp settings.json."""
    path = tmp_path / "settings.json"
    monkeypatch.setattr(
        "claude_ctx_py.core.hooks.get_settings_path",
        lambda: path,
    )
    return path


@pytest.mark.unit
class TestInstallHookCommand:
    def test_registers_subcommand_on_empty_settings(
        self, settings_file: Path
    ) -> None:
        ok, message = install_hook_command(
            subcommand="skill-suggest",
            event="UserPromptSubmit",
        )

        assert ok is True
        assert "cortex hooks skill-suggest" in message
        data = json.loads(settings_file.read_text(encoding="utf-8"))
        entries = data["hooks"]["UserPromptSubmit"]
        assert len(entries) == 1
        assert entries[0]["hooks"][0]["command"] == "cortex hooks skill-suggest"

    def test_idempotent_second_install(self, settings_file: Path) -> None:
        install_hook_command("skill-suggest", "UserPromptSubmit")
        ok, message = install_hook_command("skill-suggest", "UserPromptSubmit")

        assert ok is True
        assert "Already registered" in message
        data = json.loads(settings_file.read_text(encoding="utf-8"))
        entries = data["hooks"]["UserPromptSubmit"]
        commands = [h["command"] for e in entries for h in e["hooks"]]
        assert commands.count("cortex hooks skill-suggest") == 1

    def test_migrates_legacy_script_entry(self, settings_file: Path) -> None:
        """A settings.json pointing at the old script is rewritten cleanly."""
        settings_file.write_text(
            json.dumps(
                {
                    "hooks": {
                        "UserPromptSubmit": [
                            {
                                "matcher": "",
                                "hooks": [
                                    {
                                        "type": "command",
                                        "command": "python3 /home/user/.claude/hooks/skill_auto_suggester.py",
                                    }
                                ],
                            }
                        ]
                    }
                }
            ),
            encoding="utf-8",
        )

        ok, message = install_hook_command("skill-suggest", "UserPromptSubmit")

        assert ok is True
        assert "Migrated from legacy" in message
        data = json.loads(settings_file.read_text(encoding="utf-8"))
        commands = [
            h["command"]
            for e in data["hooks"]["UserPromptSubmit"]
            for h in e["hooks"]
        ]
        assert commands == ["cortex hooks skill-suggest"]

    def test_preserves_unrelated_hooks_on_same_event(
        self, settings_file: Path
    ) -> None:
        settings_file.write_text(
            json.dumps(
                {
                    "hooks": {
                        "UserPromptSubmit": [
                            {
                                "matcher": "",
                                "hooks": [
                                    {
                                        "type": "command",
                                        "command": "python3 /some/other/hook.py",
                                    }
                                ],
                            }
                        ]
                    }
                }
            ),
            encoding="utf-8",
        )

        ok, _ = install_hook_command("skill-suggest", "UserPromptSubmit")

        assert ok is True
        data = json.loads(settings_file.read_text(encoding="utf-8"))
        commands = sorted(
            h["command"]
            for e in data["hooks"]["UserPromptSubmit"]
            for h in e["hooks"]
        )
        assert commands == [
            "cortex hooks skill-suggest",
            "python3 /some/other/hook.py",
        ]

    def test_preserves_other_events(self, settings_file: Path) -> None:
        settings_file.write_text(
            json.dumps(
                {
                    "hooks": {
                        "PostToolUse": [
                            {
                                "matcher": "Write",
                                "hooks": [
                                    {
                                        "type": "command",
                                        "command": "python3 /tmp/post-write.py",
                                    }
                                ],
                            }
                        ]
                    }
                }
            ),
            encoding="utf-8",
        )

        install_hook_command("skill-suggest", "UserPromptSubmit")

        data = json.loads(settings_file.read_text(encoding="utf-8"))
        assert "PostToolUse" in data["hooks"]
        assert data["hooks"]["PostToolUse"][0]["hooks"][0]["command"] == (
            "python3 /tmp/post-write.py"
        )
