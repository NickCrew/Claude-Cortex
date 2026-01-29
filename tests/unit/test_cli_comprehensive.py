"Comprehensive unit tests for CLI module."

import argparse
import os
import sys
from unittest import mock
from typing import Any

import pytest

from claude_ctx_py import cli

# --------------------------------------------------------------------------- Fixtures

@pytest.fixture
def mock_core():
    """Mock the entire core module."""
    with mock.patch("claude_ctx_py.cli.core") as mock_core:
        yield mock_core

@pytest.fixture
def mock_print():
    """Mock _print function."""
    with mock.patch("claude_ctx_py.cli._print") as mock_print:
        yield mock_print

@pytest.fixture
def mock_sys_argv():
    """Reset sys.argv."""
    with mock.patch.object(sys, "argv", ["cortex"]):
        yield

# --------------------------------------------------------------------------- Main Entry Point

def test_main_env_setup(mock_core, mock_print):
    """Test environment variable setup in main."""
    with mock.patch.dict(os.environ, {}, clear=True):
        cli.main(["--scope", "global", "--plugin-root", "/tmp/test", "status"])
        assert os.environ["CLAUDE_PLUGIN_ROOT"] == "/tmp/test"
        assert os.environ["CORTEX_SCOPE"] == "global"

def test_main_dispatch_status(mock_core, mock_print):
    """Test dispatching to status command."""
    mock_core.show_status.return_value = "Status OK"
    exit_code = cli.main(["status"])
    assert exit_code == 0
    mock_core.show_status.assert_called_once()
    mock_print.assert_called_with("Status OK")

def test_main_dispatch_unknown(mock_core, capsys):
    """Test dispatching with no command."""
    # argparse prints help and exits 0 or 2 depending on version/config
    # Here we just check it doesn't crash
    try:
        cli.main([])
    except SystemExit:
        pass

def test_main_tui_dispatch(mock_core, mock_print):
    """Test dispatching to TUI."""
    with mock.patch("claude_ctx_py.tui.main.main") as mock_tui_main:
        mock_tui_main.return_value = 0
        exit_code = cli.main(["tui"])
        assert exit_code == 0
        mock_tui_main.assert_called_once()

# --------------------------------------------------------------------------- Agent Command

def test_handle_agent_activate(mock_core, mock_print):
    args = argparse.Namespace(agent_command="activate", agents=["a1"])
    mock_core.agent_activate.return_value = (0, "OK")
    assert cli._handle_agent_command(args) == 0
    mock_core.agent_activate.assert_called_with("a1")

def test_handle_agent_validate(mock_core, mock_print):
    args = argparse.Namespace(agent_command="validate", agents=["a1"], include_all=True)
    mock_core.agent_validate.return_value = (0, "Valid")
    assert cli._handle_agent_command(args) == 0
    mock_core.agent_validate.assert_called_with("a1", include_all=True)

# --------------------------------------------------------------------------- Skills Command

def test_handle_skills_validate(mock_core, mock_print):
    args = argparse.Namespace(skills_command="validate", skills=["s1"], validate_all=True)
    mock_core.skill_validate.return_value = (0, "Valid")
    assert cli._handle_skills_command(args) == 0
    # Logic inserts --all if validate_all is set
    mock_core.skill_validate.assert_called_with("--all", "s1")

def test_handle_skills_rate(mock_core, mock_print):
    args = argparse.Namespace(
        skills_command="rate",
        skill="s1",
        stars=5,
        not_helpful=False,
        task_failed=False,
        review="Great"
    )
    mock_core.skill_rate.return_value = (0, "Rated")
    assert cli._handle_skills_command(args) == 0
    mock_core.skill_rate.assert_called_with("s1", 5, True, True, "Great")

def test_handle_skills_community_list(mock_core, mock_print):
    args = argparse.Namespace(
        skills_command="community",
        community_command="list",
        community_list_tag="tag1",
        community_list_search="query",
        community_list_verified=True,
        community_list_sort="rating"
    )
    mock_core.skill_community_list.return_value = (0, "List")
    assert cli._handle_skills_command(args) == 0
    mock_core.skill_community_list.assert_called_with(
        tags=["tag1"], search="query", verified=True, sort_by="rating"
    )

def test_handle_skills_analytics(mock_core, mock_print):
    args = argparse.Namespace(skills_command="analytics", analytics_metric="roi")
    mock_core.skill_analytics.return_value = (0, "ROI")
    assert cli._handle_skills_command(args) == 0
    mock_core.skill_analytics.assert_called_with("roi")

# --------------------------------------------------------------------------- Init Command

def test_handle_init_status_json(mock_core, capsys):
    """Test init status with JSON output (goes to stdout, not _print)."""
    args = argparse.Namespace(init_command="status", target=".", json=True)
    mock_core.init_status.return_value = (0, '{"status": "ok"}', "")
    
    assert cli._handle_init_command(args) == 0
    captured = capsys.readouterr()
    assert '{"status": "ok"}' in captured.out

def test_handle_init_status_warnings(mock_core, capsys):
    """Test init status warnings go to stderr."""
    args = argparse.Namespace(init_command="status", target=".", json=False)
    mock_core.init_status.return_value = (0, "Status OK", "Warning!")
    
    with mock.patch("claude_ctx_py.cli._print") as mock_print:
        assert cli._handle_init_command(args) == 0
        mock_print.assert_called_with("Status OK")
    
    captured = capsys.readouterr()
    assert "Warning!" in captured.err

# --------------------------------------------------------------------------- Memory Command

def test_handle_memory_capture(mock_core, mock_print):
    args = argparse.Namespace(
        memory_command="capture",
        title="Session",
        capture_summary="Did stuff",
        capture_decisions="A|B",
        capture_implementations="X|Y",
        capture_open="Z",
        capture_project="proj",
        capture_quick=False
    )
        # Ensure memory submodule is mocked if lazy loaded
    with mock.patch("claude_ctx_py.memory.memory_capture") as mock_capture:
        mock_capture.return_value = (0, "Captured")
        assert cli._handle_memory_command(args) == 0
        mock_capture.assert_called_with(
            title="Session",
            summary="Did stuff",
            decisions=["A", "B"],
            implementations=["X", "Y"],
            open_items=["Z"],
            project="proj",
            quick=False
        )
# --------------------------------------------------------------------------- AI Command

def test_handle_ai_watch(mock_core):
    args = argparse.Namespace(
        ai_command="watch",
        status=False,
        stop=False,
        daemon=False,
        no_auto_activate=False,
        threshold=0.8,
        interval=5.0,
        directories=None
    )
    with mock.patch("claude_ctx_py.watch.load_watch_defaults") as mock_defaults:
        mock_defaults.return_value = mock.MagicMock(
            warnings=[],
            directories=None,
            auto_activate=True,
            threshold=0.7,
            interval=10.0
        )
        with mock.patch("claude_ctx_py.watch.watch_main") as mock_watch:
            mock_watch.return_value = 0
            assert cli._handle_ai_command(args) == 0

# --------------------------------------------------------------------------- MCP Command

def test_handle_mcp_activate(mock_core, mock_print):
    args = argparse.Namespace(mcp_command="activate", docs=["doc1"])
    mock_core.mcp_activate.return_value = (0, "Activated")
    assert cli._handle_mcp_command(args) == 0
    mock_core.mcp_activate.assert_called_with("doc1")

# --------------------------------------------------------------------------- Install Command

def test_handle_install_aliases(mock_print):
    args = argparse.Namespace(
        install_command="aliases",
        show=False,
        uninstall=False,
        shell="bash",
        rc_file=None,
        force=True,
        dry_run=False
    )
    with mock.patch("claude_ctx_py.shell_integration.install_aliases") as mock_install:
        mock_install.return_value = (0, "Installed")
        assert cli._handle_install_command(args) == 0
        mock_install.assert_called_with(
            shell="bash", rc_file=None, force=True, dry_run=False
        )

