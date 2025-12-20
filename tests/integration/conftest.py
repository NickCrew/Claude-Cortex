"""Integration-level fixtures."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pytest


def _write_agent(path: Path, *, name: str, active: bool = True) -> Path:
    """Create a minimal v2 agent file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    front = "\n".join(
        [
            "---",
            "version: 2.0",
            f"name: {name}",
            "category: core",
            "tier:",
            "  id: bronze",
            "  activation_strategy: auto",
            "tools:",
            "  catalog:",
            "    - tool-a",
            "dependencies:",
            "  requires: []",
            "  recommends: []",
            "---",
            "# body",
        ]
    )
    path.write_text(front, encoding="utf-8")
    return path


@pytest.fixture
def test_project(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Create a throwaway project with a .claude directory."""
    project_dir = tmp_path / "project"
    claude_dir = project_dir / ".claude"
    (claude_dir / "agents").mkdir(parents=True, exist_ok=True)
    (claude_dir / "inactive" / "agents").mkdir(parents=True, exist_ok=True)
    (claude_dir / "schema").mkdir(parents=True, exist_ok=True)

    # Minimal schema to satisfy validation commands
    schema = (
        "required:\n"
        "  - name\n"
        "  - category\n"
        "  - tier.id\n"
        "  - tools.catalog\n"
        "fields:\n"
        "  category:\n"
        "    enum: [core]\n"
        "  tier:\n"
        "    properties:\n"
        "      id:\n"
        "        enum: [bronze]\n"
        "      activation_strategy:\n"
        "        enum: [auto]\n"
    )
    (claude_dir / "schema" / "agent-schema-v2.yaml").write_text(schema, encoding="utf-8")

    # Ensure CLI resolves to this .claude
    monkeypatch.setenv("CLAUDE_PLUGIN_ROOT", str(claude_dir))
    monkeypatch.chdir(project_dir)
    return project_dir


@pytest.fixture
def sample_agents(test_project: Path) -> Iterable[Path]:
    """Create one active and one inactive agent for workflow tests."""
    claude_dir = test_project / ".claude"
    active = _write_agent(claude_dir / "agents" / "test-agent-1.md", name="test-agent-1")
    inactive = _write_agent(
        claude_dir / "inactive" / "agents" / "test-agent-2.md", name="test-agent-2"
    )
    return [active, inactive]
