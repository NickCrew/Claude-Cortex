"""Integration test for export context command."""

from __future__ import annotations

from pathlib import Path

import pytest

from claude_ctx_py import cli


@pytest.mark.integration
def test_export_context_to_file(test_project: Path, sample_agents, capsys, tmp_path: Path):
    output_file = tmp_path / "context.md"

    code = cli.main(["export", "context", str(output_file)])
    out = capsys.readouterr().out

    assert code == 0
    assert output_file.is_file()
    content = output_file.read_text(encoding="utf-8")
    # Ensure export contains at least one known section and agent reference
    assert "# AI Agent Context Export" in content
    assert "agents" in content
    # export command prints nothing on success; ensure no argparse error leaked
    assert "usage:" not in out
