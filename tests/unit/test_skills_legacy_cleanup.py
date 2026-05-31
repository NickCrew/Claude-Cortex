"""Regression tests for retired legacy skill metadata commands."""

from __future__ import annotations

from pathlib import Path

import pytest

from claude_ctx_py import core
from claude_ctx_py.cli import build_parser
from claude_ctx_py.core.asset_discovery import _SETTINGS_RELATIVE_PATHS
from claude_ctx_py.tui_command_palette import DEFAULT_COMMANDS


def _parse(args: list[str]):
    return build_parser().parse_args(args)


@pytest.mark.unit
def test_skills_parser_keeps_current_commands() -> None:
    ns = _parse(["skills", "deps", "agent-loops"])

    assert ns.skills_command == "deps"
    assert ns.skill == "agent-loops"


@pytest.mark.unit
@pytest.mark.parametrize("command", ["compose", "versions"])
def test_skills_parser_rejects_retired_legacy_commands(command: str) -> None:
    with pytest.raises(SystemExit):
        _parse(["skills", command, "agent-loops"])


@pytest.mark.unit
def test_settings_assets_exclude_retired_skill_metadata_files() -> None:
    settings_paths = set(_SETTINGS_RELATIVE_PATHS)

    assert Path("skills/registry.yaml") in settings_paths
    assert Path("skills/skill-index.json") not in settings_paths
    assert Path("skills/composition.yaml") not in settings_paths
    assert Path("skills/versions.yaml") not in settings_paths
    assert Path("skills/composition.schema.json") not in settings_paths
    assert Path("skills/versions.schema.json") not in settings_paths


@pytest.mark.unit
def test_retired_skill_actions_are_not_exported_or_listed() -> None:
    palette_actions = {command[2] for command in DEFAULT_COMMANDS}

    assert "skill_compose" not in palette_actions
    assert "skill_versions" not in palette_actions
    assert not hasattr(core, "skill_compose")
    assert not hasattr(core, "skill_versions")
