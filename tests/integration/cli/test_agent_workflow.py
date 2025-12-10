"""Integration test for agent management workflow."""

from __future__ import annotations

from pathlib import Path

import pytest

from claude_ctx_py import cli


@pytest.mark.integration
def test_agent_activate_deactivate_workflow(
    test_project: Path, sample_agents, capsys
) -> None:
    """End-to-end agent workflow: list → activate → status → deactivate."""

    def run(args):
        code = cli.main(args)
        output = capsys.readouterr().out
        return code, output

    # Initial list should show one active, one disabled
    code, out = run(["agent", "list"])
    assert code == 0
    assert "test-agent-1" in out
    assert "test-agent-2" in out  # disabled listing

    # Activate the disabled agent
    code, out = run(["agent", "activate", "test-agent-2"])
    assert code == 0
    assert "Activated agent" in out

    # Status should now include both
    code, out = run(["agent", "status"])
    assert code == 0
    assert "test-agent-1" in out
    assert "test-agent-2" in out

    # Deactivate back to inactive
    code, out = run(["agent", "deactivate", "test-agent-2"])
    assert code == 0
    assert "Deactivated agent" in out

    # Validate metadata (uses schema created in fixture)
    code, out = run(["agent", "validate", "--all"])
    assert code == 0
    assert "Agent metadata conforms" in out
