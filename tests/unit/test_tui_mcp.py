"""Tests for TUI MCP server management view."""

import pytest

# Skip entire module if rich (tui dependency) is not available in the test env
pytest.importorskip("rich")

from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from claude_ctx_py.tui_mcp import MCPViewMixin
from claude_ctx_py.core.mcp import MCPServerInfo


class MockTUIState:
    """Mock TUI state for testing."""

    def __init__(self):
        self.selected_index = 0
        self.status_message = ""


class TestMCPView(MCPViewMixin):
    """Test class that uses MCPViewMixin."""

    def __init__(self):
        self.state = MockTUIState()
        super().__init__()


@pytest.fixture
def mcp_view():
    """Create a test MCP view instance."""
    return TestMCPView()


@pytest.fixture
def sample_servers():
    """Create sample MCP server info objects."""
    return [
        MCPServerInfo(
            name="context7",
            command="npx",
            args=["-y", "@context7/mcp-server"],
            env={"API_KEY": "test-key"},
            description="Context7 documentation server",
            docs_path=Path("/tmp/context7.md"),
        ),
        MCPServerInfo(
            name="sequential",
            command="npx",
            args=["-y", "@sequential/mcp-server"],
            description="Sequential reasoning server",
        ),
        MCPServerInfo(
            name="browser",
            command="npx",
            args=["-y", "@browser/mcp-server"],
            description="Browser automation server",
        ),
    ]


class TestMCPViewMixin:
    """Test suite for MCPViewMixin."""

    def test_init(self, mcp_view):
        """Test mixin initialization."""
        assert mcp_view.mcp_servers == []
        assert mcp_view.mcp_filter == ""
        assert mcp_view.mcp_show_details is False
        assert mcp_view.mcp_selected_server is None

    @patch("claude_ctx_py.tui_mcp.discover_servers")
    def test_load_mcp_servers_success(self, mock_discover, mcp_view, sample_servers):
        """Test successful MCP servers loading."""
        mock_discover.return_value = (True, sample_servers, "")

        mcp_view.load_mcp_servers()

        assert len(mcp_view.mcp_servers) == 3
        assert mcp_view.state.status_message == "Loaded 3 MCP server(s)"
        mock_discover.assert_called_once()

    @patch("claude_ctx_py.tui_mcp.discover_servers")
    def test_load_mcp_servers_failure(self, mock_discover, mcp_view):
        """Test MCP servers loading failure."""
        mock_discover.return_value = (False, [], "Config not found")

        mcp_view.load_mcp_servers()

        assert mcp_view.mcp_servers == []
        assert "Error loading MCP servers" in mcp_view.state.status_message

    @patch("claude_ctx_py.tui_mcp.discover_servers")
    def test_load_mcp_servers_exception(self, mock_discover, mcp_view):
        """Test MCP servers loading with exception."""
        mock_discover.side_effect = Exception("Network error")

        mcp_view.load_mcp_servers()

        assert mcp_view.mcp_servers == []
        assert "Failed to load MCP servers" in mcp_view.state.status_message

    def test_get_filtered_servers_no_filter(self, mcp_view, sample_servers):
        """Test getting servers with no filter."""
        mcp_view.mcp_servers = sample_servers

        filtered = mcp_view.get_filtered_servers()

        assert len(filtered) == 3
        assert filtered == sample_servers

    def test_get_filtered_servers_with_filter(self, mcp_view, sample_servers):
        """Test filtering servers by name."""
        mcp_view.mcp_servers = sample_servers
        mcp_view.mcp_filter = "context"

        filtered = mcp_view.get_filtered_servers()

        assert len(filtered) == 1
        assert filtered[0].name == "context7"

    def test_get_filtered_servers_by_command(self, mcp_view, sample_servers):
        """Test filtering servers by command."""
        mcp_view.mcp_servers = sample_servers
        mcp_view.mcp_filter = "npx"

        filtered = mcp_view.get_filtered_servers()

        assert len(filtered) == 3  # All use npx

    def test_get_filtered_servers_no_match(self, mcp_view, sample_servers):
        """Test filtering with no matches."""
        mcp_view.mcp_servers = sample_servers
        mcp_view.mcp_filter = "nonexistent"

        filtered = mcp_view.get_filtered_servers()

        assert len(filtered) == 0

    @patch("claude_ctx_py.tui_mcp.Panel")
    def test_render_mcp_view_list(self, mock_panel, mcp_view):
        """Test rendering MCP list view."""
        mcp_view.mcp_show_details = False

        mcp_view.render_mcp_view()

        mock_panel.assert_called_once()

    @patch("claude_ctx_py.tui_mcp.Panel")
    def test_render_mcp_view_details(self, mock_panel, mcp_view, sample_servers):
        """Test rendering MCP details view."""
        mcp_view.mcp_show_details = True
        mcp_view.mcp_selected_server = sample_servers[0]

        mcp_view.render_mcp_view()

        mock_panel.assert_called_once()

    def test_handle_mcp_keys_down(self, mcp_view, sample_servers):
        """Test down arrow key navigation."""
        mcp_view.mcp_servers = sample_servers
        mcp_view.state.selected_index = 0

        handled = mcp_view.handle_mcp_keys("j")

        assert handled is True
        assert mcp_view.state.selected_index == 1

    def test_handle_mcp_keys_down_at_end(self, mcp_view, sample_servers):
        """Test down arrow at end of list."""
        mcp_view.mcp_servers = sample_servers
        mcp_view.state.selected_index = 2

        handled = mcp_view.handle_mcp_keys("j")

        assert handled is True
        assert mcp_view.state.selected_index == 2  # Stays at end

    def test_handle_mcp_keys_up(self, mcp_view, sample_servers):
        """Test up arrow key navigation."""
        mcp_view.mcp_servers = sample_servers
        mcp_view.state.selected_index = 1

        handled = mcp_view.handle_mcp_keys("k")

        assert handled is True
        assert mcp_view.state.selected_index == 0

    def test_handle_mcp_keys_up_at_start(self, mcp_view, sample_servers):
        """Test up arrow at start of list."""
        mcp_view.mcp_servers = sample_servers
        mcp_view.state.selected_index = 0

        handled = mcp_view.handle_mcp_keys("k")

        assert handled is True
        assert mcp_view.state.selected_index == 0  # Stays at start

    def test_handle_mcp_keys_enter(self, mcp_view, sample_servers):
        """Test Enter key to show details."""
        mcp_view.mcp_servers = sample_servers
        mcp_view.state.selected_index = 0

        handled = mcp_view.handle_mcp_keys("\n")

        assert handled is True
        assert mcp_view.mcp_show_details is True
        assert mcp_view.mcp_selected_server == sample_servers[0]

    def test_handle_mcp_keys_escape(self, mcp_view, sample_servers):
        """Test Escape key to exit details."""
        mcp_view.mcp_show_details = True
        mcp_view.mcp_selected_server = sample_servers[0]

        handled = mcp_view.handle_mcp_keys("\x1b")

        assert handled is True
        assert mcp_view.mcp_show_details is False
        assert mcp_view.mcp_selected_server is None

    def test_handle_mcp_keys_test(self, mcp_view, sample_servers):
        """Test 't' key to test server."""
        mcp_view.mcp_servers = sample_servers
        mcp_view.state.selected_index = 0

        handled = mcp_view.handle_mcp_keys("t")

        assert handled is True
        assert "Testing" in mcp_view.state.status_message

    def test_handle_mcp_keys_docs(self, mcp_view, sample_servers):
        """Test 'd' key to view docs."""
        mcp_view.mcp_servers = sample_servers
        mcp_view.state.selected_index = 0

        # Mock the docs file
        with patch.object(Path, "exists", return_value=True):
            with patch.object(Path, "read_text", return_value="# Documentation\nContent here"):
                handled = mcp_view.handle_mcp_keys("d")

        assert handled is True

    def test_handle_mcp_keys_copy(self, mcp_view, sample_servers):
        """Test 'c' key to copy config."""
        mcp_view.mcp_servers = sample_servers
        mcp_view.state.selected_index = 0

        handled = mcp_view.handle_mcp_keys("c")

        assert handled is True
        assert "Config snippet" in mcp_view.state.status_message

    def test_handle_mcp_keys_filter(self, mcp_view):
        """Test '/' key to start filtering."""
        handled = mcp_view.handle_mcp_keys("/")

        assert handled is True
        assert "Filter" in mcp_view.state.status_message

    @patch("claude_ctx_py.tui_mcp.discover_servers")
    def test_handle_mcp_keys_reload(self, mock_discover, mcp_view, sample_servers):
        """Test 'r' key to reload servers."""
        mock_discover.return_value = (True, sample_servers, "")

        handled = mcp_view.handle_mcp_keys("r")

        assert handled is True
        assert mcp_view.state.selected_index == 0
        mock_discover.assert_called_once()

    @patch("claude_ctx_py.tui_mcp.validate_server_config")
    def test_handle_mcp_keys_validate(self, mock_validate, mcp_view, sample_servers):
        """Test 'v' key to validate server."""
        mock_validate.return_value = (True, [], [])
        mcp_view.mcp_servers = sample_servers
        mcp_view.state.selected_index = 0

        handled = mcp_view.handle_mcp_keys("v")

        assert handled is True
        mock_validate.assert_called_once()

    def test_handle_mcp_keys_unknown(self, mcp_view):
        """Test unknown key returns False."""
        handled = mcp_view.handle_mcp_keys("x")

        assert handled is False

    def test_test_mcp_server(self, mcp_view, sample_servers):
        """Test server testing (placeholder)."""
        server = sample_servers[0]

        mcp_view.test_mcp_server(server)

        assert "Testing" in mcp_view.state.status_message
        assert "not yet implemented" in mcp_view.state.status_message

    def test_view_mcp_docs_with_docs(self, mcp_view, sample_servers):
        """Test viewing docs when available."""
        server = sample_servers[0]

        with patch.object(Path, "exists", return_value=True):
            with patch.object(Path, "read_text", return_value="# Documentation\nContent"):
                mcp_view.view_mcp_docs(server)

        assert "Docs preview" in mcp_view.state.status_message

    def test_view_mcp_docs_without_docs(self, mcp_view, sample_servers):
        """Test viewing docs when not available."""
        server = sample_servers[1]  # No docs_path

        mcp_view.view_mcp_docs(server)

        assert "No documentation found" in mcp_view.state.status_message

    def test_view_mcp_docs_read_error(self, mcp_view, sample_servers):
        """Test viewing docs with read error."""
        server = sample_servers[0]

        with patch.object(Path, "exists", return_value=True):
            with patch.object(Path, "read_text", side_effect=Exception("Read error")):
                mcp_view.view_mcp_docs(server)

        assert "Error reading docs" in mcp_view.state.status_message

    @patch("claude_ctx_py.tui_mcp.generate_config_snippet")
    def test_copy_mcp_config_success(self, mock_generate, mcp_view, sample_servers):
        """Test copying config snippet."""
        mock_generate.return_value = '{"mcpServers": {...}}'
        server = sample_servers[0]

        mcp_view.copy_mcp_config(server)

        assert "Config snippet generated" in mcp_view.state.status_message
        mock_generate.assert_called_once_with(
            server.name,
            server.command,
            args=server.args,
            env=server.env,
        )

    @patch("claude_ctx_py.tui_mcp.generate_config_snippet")
    def test_copy_mcp_config_error(self, mock_generate, mcp_view, sample_servers):
        """Test copying config with error."""
        mock_generate.side_effect = Exception("Generation error")
        server = sample_servers[0]

        mcp_view.copy_mcp_config(server)

        assert "Error generating config" in mcp_view.state.status_message

    @patch("claude_ctx_py.tui_mcp.validate_server_config")
    def test_validate_mcp_server_valid(self, mock_validate, mcp_view, sample_servers):
        """Test validating valid server."""
        mock_validate.return_value = (True, [], [])
        server = sample_servers[0]

        mcp_view.validate_mcp_server(server)

        assert "configuration is valid" in mcp_view.state.status_message

    @patch("claude_ctx_py.tui_mcp.validate_server_config")
    def test_validate_mcp_server_with_warnings(self, mock_validate, mcp_view, sample_servers):
        """Test validating server with warnings."""
        mock_validate.return_value = (True, [], ["Missing docs"])
        server = sample_servers[0]

        mcp_view.validate_mcp_server(server)

        assert "configuration is valid" in mcp_view.state.status_message
        assert "warning" in mcp_view.state.status_message

    @patch("claude_ctx_py.tui_mcp.validate_server_config")
    def test_validate_mcp_server_invalid(self, mock_validate, mcp_view, sample_servers):
        """Test validating invalid server."""
        mock_validate.return_value = (False, ["Command not found"], [])
        server = sample_servers[0]

        mcp_view.validate_mcp_server(server)

        assert "Validation failed" in mcp_view.state.status_message

    @patch("claude_ctx_py.tui_mcp.validate_server_config")
    def test_validate_mcp_server_exception(self, mock_validate, mcp_view, sample_servers):
        """Test validating server with exception."""
        mock_validate.side_effect = Exception("Validation error")
        server = sample_servers[0]

        mcp_view.validate_mcp_server(server)

        assert "Error validating server" in mcp_view.state.status_message
