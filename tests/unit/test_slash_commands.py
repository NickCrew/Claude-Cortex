"""Tests for slash command discovery utilities."""

from pathlib import Path

from claude_ctx_py.slash_commands import scan_slash_commands


def _write_command(commands_dir: Path, relative: str, content: str) -> Path:
    target = commands_dir / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return target


def test_scan_slash_commands_parses_metadata(tmp_path):
    commands_dir = tmp_path / "commands"
    commands_dir.mkdir()
    _write_command(
        commands_dir,
        "dev/code-review.md",
        """---
name: code-review
description: Comprehensive code review
category: development
complexity: advanced
agents: [code-reviewer, security-auditor]
personas: [backend]
mcp-servers: [context7]
---
# /dev:code-review
""",
    )

    commands = scan_slash_commands(commands_dir, home_dir=tmp_path)

    assert len(commands) == 1
    cmd = commands[0]
    assert cmd.command == "/dev:code-review"
    assert cmd.namespace == "dev"
    assert cmd.category == "development"
    assert cmd.complexity == "advanced"
    assert cmd.location == "user"
    assert cmd.agents == ["code-reviewer", "security-auditor"]
    assert cmd.personas == ["backend"]
    assert cmd.mcp_servers == ["context7"]


def test_scan_slash_commands_falls_back_to_parent_namespace(tmp_path):
    commands_dir = tmp_path / "commands"
    commands_dir.mkdir()
    _write_command(
        commands_dir,
        "deploy/prepare-release.md",
        """---
name: prepare-release
description: Prepare a release
category: deploy
---
No explicit slash heading here.
""",
    )

    commands = scan_slash_commands(commands_dir, home_dir=tmp_path)

    assert len(commands) == 1
    cmd = commands[0]
    assert cmd.namespace == "deploy"
    assert cmd.command == "/deploy:prepare-release"


def test_scan_slash_commands_ignores_non_command_files(tmp_path):
    commands_dir = tmp_path / "commands"
    commands_dir.mkdir()
    _write_command(
        commands_dir,
        "README.md",
        "# Command catalog\n",
    )
    _write_command(
        commands_dir,
        "extras/notes.md",
        "# Just some notes",
    )

    commands = scan_slash_commands(commands_dir, home_dir=tmp_path)

    assert commands == []

