"""Tests for MCP server management functionality."""

import json
import platform
from pathlib import Path
from unittest.mock import patch, mock_open

import pytest

from claude_ctx_py.core.mcp import (
    MCPServerInfo,
    MCPServerCapabilities,
    MCPConfigError,
    MCPServerNotFoundError,
    discover_servers,
    get_server_info,
    list_server_tools,
    get_server_docs_path,
    validate_server_config,
    generate_config_snippet,
    list_available_servers,
    get_server_command_line,
    export_servers_list,
    _get_claude_config_path,
    list_doc_only_servers,
)


@pytest.fixture
def mock_config_path(tmp_path: Path) -> Path:
    """Create a temporary config file path."""
    return tmp_path / "claude_desktop_config.json"


@pytest.fixture
def sample_config() -> dict:
    """Sample Claude Desktop config with MCP servers."""
    return {
        "mcpServers": {
            "context7": {
                "command": "npx",
                "args": ["-y", "@context7/mcp-server"],
                "env": {
                    "CONTEXT7_API_KEY": "test-key-123"
                }
            },
            "sequential": {
                "command": "python",
                "args": ["-m", "sequential_mcp"],
            },
            "filesystem": {
                "command": "/usr/local/bin/mcp-filesystem",
                "args": ["--root", "/tmp"],
            }
        }
    }


@pytest.fixture
def mock_config_file(mock_config_path: Path, sample_config: dict) -> Path:
    """Create a mock config file."""
    mock_config_path.write_text(json.dumps(sample_config, indent=2))
    return mock_config_path


class TestGetClaudeConfigPath:
    """Tests for platform-specific config path detection."""

    @patch("platform.system")
    def test_macos_path(self, mock_system):
        """Test macOS config path."""
        mock_system.return_value = "Darwin"
        path = _get_claude_config_path()
        assert "Library/Application Support/Claude" in str(path)
        assert path.name == "claude_desktop_config.json"

    @patch("platform.system")
    def test_linux_path(self, mock_system):
        """Test Linux config path."""
        mock_system.return_value = "Linux"
        path = _get_claude_config_path()
        assert ".config/Claude" in str(path)
        assert path.name == "claude_desktop_config.json"

    @patch("platform.system")
    @patch.dict("os.environ", {"APPDATA": "C:\\Users\\Test\\AppData\\Roaming"})
    def test_windows_path_with_appdata(self, mock_system):
        """Test Windows config path with APPDATA."""
        mock_system.return_value = "Windows"
        path = _get_claude_config_path()
        assert "Claude" in str(path)
        assert path.name == "claude_desktop_config.json"

    @patch("platform.system")
    @patch.dict("os.environ", {}, clear=True)
    def test_windows_path_without_appdata(self, mock_system):
        """Test Windows config path without APPDATA."""
        mock_system.return_value = "Windows"
        path = _get_claude_config_path()
        assert "AppData" in str(path) or "Claude" in str(path)
        assert path.name == "claude_desktop_config.json"

    @patch("platform.system")
    def test_unknown_platform_fallback(self, mock_system):
        """Test fallback for unknown platforms."""
        mock_system.return_value = "UnknownOS"
        path = _get_claude_config_path()
        assert ".config/Claude" in str(path)


class TestMCPServerInfo:
    """Tests for MCPServerInfo dataclass."""

    def test_creation(self):
        """Test creating server info."""
        server = MCPServerInfo(
            name="test-server",
            command="node",
            args=["server.js"],
            env={"API_KEY": "test"},
        )
        assert server.name == "test-server"
        assert server.command == "node"
        assert server.args == ["server.js"]
        assert server.env == {"API_KEY": "test"}
        assert server.doc_only is False

    def test_to_dict(self):
        """Test converting to dictionary."""
        server = MCPServerInfo(
            name="test-server",
            command="node",
            args=["server.js"],
        )
        data = server.to_dict()
        assert data["name"] == "test-server"
        assert data["command"] == "node"
        assert data["args"] == ["server.js"]
        assert data["doc_only"] is False

    def test_is_valid_success(self):
        """Test validation of valid server."""
        server = MCPServerInfo(
            name="test-server",
            command="python",
            args=["-m", "server"],
        )
        is_valid, errors = server.is_valid()
        assert is_valid
        assert len(errors) == 0

    def test_is_valid_missing_name(self):
        """Test validation with missing name."""
        server = MCPServerInfo(
            name="",
            command="python",
        )
        is_valid, errors = server.is_valid()
        assert not is_valid
        assert "name is required" in errors[0].lower()

    def test_is_valid_missing_command(self):
        """Test validation with missing command."""
        server = MCPServerInfo(
            name="test-server",
            command="",
        )
        is_valid, errors = server.is_valid()
        assert not is_valid
        assert "command is required" in errors[0].lower()

    def test_is_valid_nonexistent_absolute_path(self, tmp_path: Path):
        """Test validation with nonexistent absolute path."""
        nonexistent = tmp_path / "does_not_exist"
        server = MCPServerInfo(
            name="test-server",
            command=str(nonexistent),
        )
        is_valid, errors = server.is_valid()
        assert not is_valid
        assert "not found" in errors[0].lower()


class TestDiscoverServers:
    """Tests for discover_servers function."""

    def test_success(self, mock_config_file: Path):
        """Test successful server discovery."""
        success, servers, error = discover_servers(mock_config_file)
        assert success
        assert len(servers) == 3
        assert error == ""

        names = [s.name for s in servers]
        assert "context7" in names
        assert "sequential" in names
        assert "filesystem" in names

    def test_missing_config(self, tmp_path: Path):
        """Test with missing config file."""
        missing_path = tmp_path / "nonexistent.json"
        success, servers, error = discover_servers(missing_path)
        assert not success
        assert len(servers) == 0
        assert "not found" in error.lower()

    def test_invalid_json(self, mock_config_path: Path):
        """Test with invalid JSON."""
        mock_config_path.write_text("{ invalid json }")
        success, servers, error = discover_servers(mock_config_path)
        assert not success
        assert "invalid json" in error.lower()

    def test_empty_config(self, mock_config_path: Path):
        """Test with empty config."""
        mock_config_path.write_text("{}")
        success, servers, error = discover_servers(mock_config_path)
        assert success
        assert len(servers) == 0

    def test_no_mcp_servers(self, mock_config_path: Path):
        """Test config without mcpServers section."""
        config = {"other": "data"}
        mock_config_path.write_text(json.dumps(config))
        success, servers, error = discover_servers(mock_config_path)
        assert success
        assert len(servers) == 0

    def test_malformed_server_config(self, mock_config_path: Path):
        """Test with malformed server entries."""
        config = {
            "mcpServers": {
                "good-server": {
                    "command": "python",
                    "args": ["-m", "server"],
                },
                "bad-server": "not-a-dict",  # Invalid
            }
        }
        mock_config_path.write_text(json.dumps(config))
        success, servers, error = discover_servers(mock_config_path)
        assert success
        # Should skip bad entry but process good one
        assert len(servers) == 1
        assert servers[0].name == "good-server"

    def test_server_with_env_vars(self, mock_config_file: Path):
        """Test server with environment variables."""
        success, servers, error = discover_servers(mock_config_file)
        assert success

        context7 = next(s for s in servers if s.name == "context7")
        assert "CONTEXT7_API_KEY" in context7.env
        assert context7.env["CONTEXT7_API_KEY"] == "test-key-123"


class TestGetServerInfo:
    """Tests for get_server_info function."""

    def test_success(self, mock_config_file: Path):
        """Test getting server info."""
        success, server, error = get_server_info("context7", mock_config_file)
        assert success
        assert server is not None
        assert server.name == "context7"
        assert server.command == "npx"
        assert error == ""

    def test_case_insensitive(self, mock_config_file: Path):
        """Test case-insensitive lookup."""
        success, server, error = get_server_info("CONTEXT7", mock_config_file)
        assert success
        assert server is not None
        assert server.name == "context7"

    def test_not_found(self, mock_config_file: Path):
        """Test server not found."""
        success, server, error = get_server_info("nonexistent", mock_config_file)
        assert not success
        assert server is None
        assert "not found" in error.lower()
        assert "available" in error.lower()

    def test_config_error(self, tmp_path: Path):
        """Test with config error."""
        missing_path = tmp_path / "missing.json"
        success, server, error = get_server_info("test", missing_path)
        assert not success
        assert server is None


class TestListServerTools:
    """Tests for list_server_tools function."""

    def test_placeholder_implementation(self, mock_config_file: Path):
        """Test placeholder tool listing."""
        success, tools, error = list_server_tools("context7", mock_config_file)
        assert success
        assert isinstance(tools, list)
        assert "not yet implemented" in error.lower()

    def test_server_not_found(self, tmp_path: Path):
        """Test with nonexistent server."""
        missing_path = tmp_path / "missing.json"
        success, tools, error = list_server_tools("test", missing_path)
        assert not success
        assert len(tools) == 0


class TestGetServerDocsPath:
    """Tests for get_server_docs_path function."""

    def test_found_exact_match(self, tmp_path: Path):
        """Test finding docs with exact name match."""
        claude_dir = tmp_path / ".cortex"
        docs_dir = claude_dir / "mcp" / "docs"
        docs_dir.mkdir(parents=True)

        doc_file = docs_dir / "context7.md"
        doc_file.write_text("# Context7 docs")

        path = get_server_docs_path("context7", claude_dir)
        assert path is not None
        assert path == doc_file

    def test_found_case_insensitive(self, tmp_path: Path):
        """Test finding docs with case-insensitive match."""
        claude_dir = tmp_path / ".cortex"
        docs_dir = claude_dir / "mcp" / "docs"
        docs_dir.mkdir(parents=True)

        doc_file = docs_dir / "Context7.md"
        doc_file.write_text("# Context7 docs")

        path = get_server_docs_path("context7", claude_dir)
        assert path is not None
        # Check stem matches case-insensitively
        assert path.stem.lower() == "context7"
        assert path.exists()

    def test_not_found(self, tmp_path: Path):
        """Test when docs don't exist."""
        claude_dir = tmp_path / ".cortex"
        path = get_server_docs_path("nonexistent", claude_dir)
        assert path is None

    def test_no_docs_dir(self, tmp_path: Path):
        """Test when docs directory doesn't exist."""
        claude_dir = tmp_path / ".cortex"
        path = get_server_docs_path("test", claude_dir)
        assert path is None


class TestValidateServerConfig:
    """Tests for validate_server_config function."""

    def test_valid_server(self, mock_config_file: Path):
        """Test validating valid server."""
        valid, errors, warnings = validate_server_config("sequential", mock_config_file)
        assert valid
        assert len(errors) == 0

    def test_invalid_server(self, mock_config_path: Path):
        """Test validating invalid server."""
        config = {
            "mcpServers": {
                "bad-server": {
                    "command": "",  # Empty command
                }
            }
        }
        mock_config_path.write_text(json.dumps(config))

        valid, errors, warnings = validate_server_config("bad-server", mock_config_path)
        assert not valid
        assert len(errors) > 0
        assert any("command" in e.lower() for e in errors)

    def test_warnings_no_docs(self, mock_config_file: Path):
        """Test warnings for missing documentation."""
        valid, errors, warnings = validate_server_config("sequential", mock_config_file)
        assert valid
        assert any("documentation" in w.lower() for w in warnings)

    def test_server_not_found(self, tmp_path: Path):
        """Test validating nonexistent server."""
        missing_path = tmp_path / "missing.json"
        valid, errors, warnings = validate_server_config("test", missing_path)
        assert not valid
        assert len(errors) > 0


class TestGenerateConfigSnippet:
    """Tests for generate_config_snippet function."""

    def test_basic_snippet(self):
        """Test generating basic config snippet."""
        snippet = generate_config_snippet(
            "myserver",
            "python",
            args=["-m", "myserver"],
        )
        assert "myserver" in snippet
        assert "python" in snippet
        assert "-m" in snippet
        assert "mcpServers" in snippet

    def test_with_env_vars(self):
        """Test generating snippet with environment variables."""
        snippet = generate_config_snippet(
            "myserver",
            "node",
            env={"API_KEY": "test-key"},
        )
        assert "API_KEY" in snippet
        assert "test-key" in snippet
        assert "env" in snippet

    def test_custom_indent(self):
        """Test custom indentation."""
        snippet = generate_config_snippet(
            "myserver",
            "python",
            indent=4,
        )
        assert "    " in snippet  # 4 spaces


class TestListAvailableServers:
    """Tests for list_available_servers function."""

    def test_success(self, mock_config_file: Path):
        """Test listing available servers."""
        servers = list_available_servers(mock_config_file)
        assert len(servers) == 3
        assert "context7" in servers
        assert "sequential" in servers
        assert "filesystem" in servers

    def test_empty_config(self, mock_config_path: Path):
        """Test with empty config."""
        mock_config_path.write_text("{}")
        servers = list_available_servers(mock_config_path)
        assert len(servers) == 0

    def test_config_error(self, tmp_path: Path):
        """Test with config error."""
        missing_path = tmp_path / "missing.json"
        servers = list_available_servers(missing_path)
        assert len(servers) == 0


class TestGetServerCommandLine:
    """Tests for get_server_command_line function."""

    def test_success(self, mock_config_file: Path):
        """Test getting command line."""
        success, cmd, error = get_server_command_line("context7", mock_config_file)
        assert success
        assert "npx" in cmd
        assert "-y" in cmd
        assert "@context7/mcp-server" in cmd
        assert error == ""

    def test_server_not_found(self, tmp_path: Path):
        """Test with nonexistent server."""
        missing_path = tmp_path / "missing.json"
        success, cmd, error = get_server_command_line("test", missing_path)
        assert not success
        assert cmd == ""


class TestExportServersList:
    """Tests for export_servers_list function."""

    def test_text_format(self, mock_config_file: Path):
        """Test exporting as text."""
        success, output, error = export_servers_list(mock_config_file, "text")
        assert success
        assert "context7" in output
        assert "sequential" in output
        assert "Command:" in output

    def test_json_format(self, mock_config_file: Path):
        """Test exporting as JSON."""
        success, output, error = export_servers_list(mock_config_file, "json")
        assert success
        data = json.loads(output)
        assert len(data) == 3
        assert any(s["name"] == "context7" for s in data)

    def test_markdown_format(self, mock_config_file: Path):
        """Test exporting as Markdown."""
        success, output, error = export_servers_list(mock_config_file, "markdown")
        assert success
        assert "# MCP Servers" in output
        assert "| Name |" in output
        assert "context7" in output

    def test_empty_config(self, mock_config_path: Path):
        """Test with no servers."""
        mock_config_path.write_text("{}")
        success, output, error = export_servers_list(mock_config_path, "text")
        assert success
        assert "no" in output.lower() or "configured" in output.lower()

    def test_config_error(self, tmp_path: Path):
        """Test with config error."""
        missing_path = tmp_path / "missing.json"
        success, output, error = export_servers_list(missing_path, "text")
        assert not success


class TestMCPExceptions:
    """Tests for MCP-specific exceptions."""

    def test_mcp_config_error(self):
        """Test MCPConfigError."""
        error = MCPConfigError("Config invalid", Path("/test/config.json"))
        assert "Config invalid" in str(error)
        assert "configuration" in error.recovery_hint.lower()

    def test_mcp_server_not_found_error(self):
        """Test MCPServerNotFoundError."""
        error = MCPServerNotFoundError("test-server", ["server1", "server2"])
        assert "test-server" in str(error)
        assert "server1" in str(error)
        assert error.server_name == "test-server"
        assert error.available_servers == ["server1", "server2"]


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_unicode_in_config(self, mock_config_path: Path):
        """Test handling unicode in config."""
        config = {
            "mcpServers": {
                "测试服务器": {  # Chinese characters
                    "command": "python",
                    "args": ["服务.py"],
                }
            }
        }
        mock_config_path.write_text(json.dumps(config, ensure_ascii=False))

        success, servers, error = discover_servers(mock_config_path)
        assert success
        assert len(servers) == 1

    def test_very_long_args_list(self, mock_config_path: Path):
        """Test handling very long args list."""
        config = {
            "mcpServers": {
                "test": {
                    "command": "python",
                    "args": [f"arg{i}" for i in range(100)],
                }
            }
        }
        mock_config_path.write_text(json.dumps(config))

        success, servers, error = discover_servers(mock_config_path)
        assert success
        assert len(servers[0].args) == 100

    def test_empty_env_values(self, mock_config_path: Path):
        """Test handling empty environment variable values."""
        config = {
            "mcpServers": {
                "test": {
                    "command": "python",
                    "env": {
                        "VAR1": "",
                        "VAR2": None,
                    }
                }
            }
        }
        mock_config_path.write_text(json.dumps(config))

        success, servers, error = discover_servers(mock_config_path)
        assert success
        # Validation should warn about empty values
        valid, errors, warnings = validate_server_config("test", mock_config_path)
        assert any("empty" in w.lower() for w in warnings)


class TestDocOnlyServers:
    """Tests for discovering documentation-only MCP entries."""

    def test_list_doc_only_servers_detects_docs_without_config(self, tmp_path: Path):
        """Doc files without config entries should produce placeholder servers."""
        claude_dir = tmp_path
        docs_dir = claude_dir / "mcp" / "docs"
        docs_dir.mkdir(parents=True)
        browser_doc = docs_dir / "BrowserTools.md"
        browser_doc.write_text("# Browser Tools docs", encoding="utf-8")

        placeholders = list_doc_only_servers([], claude_dir=claude_dir)

        assert len(placeholders) == 1
        server = placeholders[0]
        assert server.name == "BrowserTools"
        assert server.doc_only is True
        assert server.docs_path == browser_doc
        assert server.command == ""

    def test_list_doc_only_servers_respects_existing_configs(self, tmp_path: Path):
        """Doc helper should ignore servers that are already configured."""
        claude_dir = tmp_path
        docs_dir = claude_dir / "mcp" / "docs"
        docs_dir.mkdir(parents=True)
        (docs_dir / "Context7.md").write_text("# docs", encoding="utf-8")

        placeholders = list_doc_only_servers({"context7"}, claude_dir=claude_dir)

        assert placeholders == []
