"""Integration test for file sync style commands."""

from __future__ import annotations

from pathlib import Path

import pytest

from claude_ctx_py import cli


@pytest.mark.integration
def test_agent_graph_export_creates_file(test_project: Path, sample_agents, capsys):
    output_path = test_project / "deps.txt"

    code = cli.main(["agent", "graph", "--export", str(output_path)])
    out = capsys.readouterr().out

    assert code == 0
    assert output_path.is_file()
    content = output_path.read_text(encoding="utf-8")
    assert "test-agent-1" in content or "test-agent-2" in content
    assert "Exported dependency map" in out
