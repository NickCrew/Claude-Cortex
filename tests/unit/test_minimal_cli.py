"""Unit tests for the ``cortex-minimal`` entrypoint."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Set

import pytest

from claude_ctx_py import hooks
from claude_ctx_py import minimal_cli


def _top_level_commands(parser: argparse.ArgumentParser) -> Set[str]:
    for action in parser._subparsers._actions:
        if isinstance(action, argparse._SubParsersAction):
            return set(action.choices)
    return set()


@pytest.mark.unit
class TestMinimalParser:
    def test_exposes_only_minimal_commands(self) -> None:
        parser = minimal_cli.build_parser()

        assert _top_level_commands(parser) == {
            "completions",
            "git",
            "hooks",
            "statusline",
            "tmux",
        }

    def test_parses_shared_git_surface(self) -> None:
        ns = minimal_cli.build_parser().parse_args(
            ["git", "commit", "fix: bug", "file.py"]
        )

        assert ns.command == "git"
        assert ns.git_command == "commit"
        assert ns.message == "fix: bug"
        assert ns.files == ["file.py"]

    def test_parses_shared_tmux_surface(self) -> None:
        ns = minimal_cli.build_parser().parse_args(["tmux", "read", "build", "20"])

        assert ns.command == "tmux"
        assert ns.tmux_command == "read"
        assert ns.window == "build"
        assert ns.lines == 20

    def test_rejects_hook_management_name_collisions(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setitem(
            hooks.HOOK_SUBCOMMANDS,
            "install",
            {
                "event": "UserPromptSubmit",
                "matcher": "",
                "help": "collision",
            },
        )

        with pytest.raises(ValueError, match="Hook names collide"):
            minimal_cli.build_parser()


@pytest.mark.unit
class TestMinimalCompletions:
    def test_bash_completion_targets_cortex_minimal(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        code = minimal_cli.main(["completions", "bash"])

        assert code == 0
        output = capsys.readouterr().out
        assert "complete -F _cortex_minimal_completion cortex-minimal" in output
        assert 'local commands="completions git hooks statusline tmux"' in output
        assert 'install) COMPREPLY=($(compgen -W "--target" -- ${cur})) ;;' in output
        assert " agent" not in output

    def test_zsh_completion_targets_cortex_minimal(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        code = minimal_cli.main(["completions", "zsh"])

        assert code == 0
        output = capsys.readouterr().out
        assert "#compdef cortex-minimal" in output
        assert "_cortex_minimal() {" in output
        assert "_describe -t commands 'cortex-minimal command' commands" in output

    def test_fish_completion_anchors_nested_flags_to_parent(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        code = minimal_cli.main(["completions", "fish"])

        assert code == 0
        output = capsys.readouterr().out
        assert (
            "__fish_seen_subcommand_from tmux; and __fish_seen_subcommand_from say"
            in output
        )


@pytest.mark.unit
class TestMinimalHooks:
    def test_install_registers_cortex_minimal_hook_command(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        settings_file = tmp_path / "settings.json"
        monkeypatch.setattr(
            "claude_ctx_py.core.hooks.get_settings_path",
            lambda: settings_file,
        )

        code = minimal_cli.main(["hooks", "install", "skill-suggest"])

        assert code == 0
        assert "cortex-minimal hooks skill-suggest" in capsys.readouterr().out
        data = json.loads(settings_file.read_text(encoding="utf-8"))
        command = data["hooks"]["UserPromptSubmit"][0]["hooks"][0]["command"]
        assert command == "cortex-minimal hooks skill-suggest"

    def test_missing_hook_implementation_returns_clear_error(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        def raise_import_error(_name: str, package: str | None = None) -> None:
            raise ImportError("missing")

        monkeypatch.setattr(minimal_cli.importlib, "import_module", raise_import_error)

        code = minimal_cli._run_hook_subcommand("missing-hook")

        assert code == 1
        assert (
            "Hook implementation failed to import: missing-hook"
            in capsys.readouterr().out
        )
