"""Integration tests for installer, launcher, and MCP configuration."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, Any
from unittest.mock import patch

import pytest

from claude_ctx_py import installer
from claude_ctx_py.launcher import (
    resolve_config_path,
    start_claude,
)
from claude_ctx_py.wizard import (
    MCP_SERVERS,
    WizardConfig,
    _write_mcp_config,
)


@pytest.fixture
def isolated_cortex_home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Create an isolated ~/.cortex directory for testing."""
    cortex_home = tmp_path / ".cortex"
    cortex_home.mkdir(parents=True, exist_ok=True)

    # Override the home directory resolution
    monkeypatch.setenv("CORTEX_ROOT", str(cortex_home))
    monkeypatch.setenv("HOME", str(tmp_path))

    return cortex_home


@pytest.fixture
def isolated_claude_home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Create an isolated ~/.claude directory for testing."""
    claude_home = tmp_path / ".claude"
    claude_home.mkdir(parents=True, exist_ok=True)

    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(claude_home))

    return claude_home


@pytest.mark.integration
class TestBootstrap:
    """Integration tests for the bootstrap installer."""

    def test_bootstrap_creates_directory_structure(
        self, isolated_cortex_home: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Bootstrap should create the expected directory structure."""
        # Run bootstrap
        exit_code, message = installer.bootstrap(
            target_dir=isolated_cortex_home,
            force=False,
            dry_run=False,
            link_rules=False,
        )

        assert exit_code == 0, f"Bootstrap failed: {message}"

        # Verify core directories exist (bootstrap copies these from bundled assets)
        expected_dirs = [
            "modes",
            "rules",
            "flags",
            "templates",
        ]
        for dir_name in expected_dirs:
            dir_path = isolated_cortex_home / dir_name
            assert dir_path.is_dir(), f"Expected directory {dir_name} not created"

    def test_bootstrap_creates_config_file(
        self, isolated_cortex_home: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Bootstrap should create cortex-config.json."""
        exit_code, _ = installer.bootstrap(
            target_dir=isolated_cortex_home,
            force=False,
            dry_run=False,
            link_rules=False,
        )

        assert exit_code == 0

        config_path = isolated_cortex_home / "cortex-config.json"
        assert config_path.is_file(), "cortex-config.json not created"

        # Verify it's valid JSON
        config = json.loads(config_path.read_text())
        assert "plugin_id" in config
        assert config["plugin_id"] == "cortex"

    def test_bootstrap_dry_run_does_not_create_files(
        self, isolated_cortex_home: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Dry run should not create any files."""
        # Remove the directory to start fresh
        import shutil
        shutil.rmtree(isolated_cortex_home)

        exit_code, message = installer.bootstrap(
            target_dir=isolated_cortex_home,
            force=False,
            dry_run=True,
            link_rules=False,
        )

        assert exit_code == 0
        assert not isolated_cortex_home.exists(), "Dry run should not create directory"

    def test_bootstrap_idempotent(
        self, isolated_cortex_home: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Running bootstrap twice should succeed."""
        # First run
        exit_code1, _ = installer.bootstrap(
            target_dir=isolated_cortex_home,
            force=False,
            dry_run=False,
            link_rules=False,
        )
        assert exit_code1 == 0

        # Second run (should not fail)
        exit_code2, _ = installer.bootstrap(
            target_dir=isolated_cortex_home,
            force=False,
            dry_run=False,
            link_rules=False,
        )
        assert exit_code2 == 0


@pytest.mark.integration
class TestConfigResolution:
    """Integration tests for config path resolution."""

    def test_resolve_explicit_config(self, tmp_path: Path) -> None:
        """Explicit config path should be used when provided."""
        explicit_path = tmp_path / "custom-config.json"
        explicit_path.write_text("{}", encoding="utf-8")

        resolved = resolve_config_path(explicit=explicit_path)

        assert resolved == explicit_path

    def test_resolve_local_config(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Local .claude/cortex-config.json should be found when present."""
        # Create project structure
        project_dir = tmp_path / "my-project"
        project_dir.mkdir()
        local_config_dir = project_dir / ".claude"
        local_config_dir.mkdir()
        local_config = local_config_dir / "cortex-config.json"
        local_config.write_text('{"local": true}', encoding="utf-8")

        resolved = resolve_config_path(cwd=project_dir)

        assert resolved == local_config

    def test_resolve_config_walks_up_directories(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Config resolution should walk up directory tree."""
        # Create nested structure
        root_dir = tmp_path / "project"
        nested_dir = root_dir / "src" / "components" / "deep"
        nested_dir.mkdir(parents=True)

        # Put config at root
        config_dir = root_dir / ".claude"
        config_dir.mkdir()
        config_file = config_dir / "cortex-config.json"
        config_file.write_text('{"found": true}', encoding="utf-8")

        # Resolve from deep nested directory
        resolved = resolve_config_path(cwd=nested_dir)

        assert resolved == config_file


@pytest.mark.integration
class TestMCPConfiguration:
    """Integration tests for MCP server configuration."""

    def test_mcp_servers_have_valid_structure(self) -> None:
        """All MCP server definitions should have required fields."""
        required_fields = ["name", "description", "config"]
        config_required = ["command", "args"]

        for server_id, server in MCP_SERVERS.items():
            for field in required_fields:
                assert field in server, f"Server {server_id} missing {field}"

            config = server["config"]
            assert isinstance(config, dict), f"Server {server_id} config not a dict"
            for field in config_required:
                assert field in config, f"Server {server_id} config missing {field}"

    def test_write_mcp_config_creates_valid_json(self, tmp_path: Path) -> None:
        """_write_mcp_config should create valid .mcp.json."""
        selected = ["context7", "mcp-memory"]

        _write_mcp_config(tmp_path, selected)

        mcp_path = tmp_path / ".mcp.json"
        assert mcp_path.is_file()

        config = json.loads(mcp_path.read_text())
        assert "mcpServers" in config
        assert "context7" in config["mcpServers"]
        assert "mcp-memory" in config["mcpServers"]

    def test_write_mcp_config_empty_selection(self, tmp_path: Path) -> None:
        """Empty selection should create empty mcpServers."""
        _write_mcp_config(tmp_path, [])

        mcp_path = tmp_path / ".mcp.json"
        config = json.loads(mcp_path.read_text())

        assert config["mcpServers"] == {}

    def test_write_mcp_config_ignores_unknown_servers(self, tmp_path: Path) -> None:
        """Unknown server IDs should be silently ignored."""
        selected = ["context7", "nonexistent-server"]

        _write_mcp_config(tmp_path, selected)

        config = json.loads((tmp_path / ".mcp.json").read_text())

        assert "context7" in config["mcpServers"]
        assert "nonexistent-server" not in config["mcpServers"]

    def test_mcp_memory_config_uses_uvx(self) -> None:
        """MCP memory server should use uvx command."""
        assert "mcp-memory" in MCP_SERVERS
        config = MCP_SERVERS["mcp-memory"]["config"]

        assert config["command"] == "uvx"
        assert "mcp-memory-py" in config["args"]

    def test_context7_config_uses_npx(self) -> None:
        """Context7 server should use npx command."""
        assert "context7" in MCP_SERVERS
        config = MCP_SERVERS["context7"]["config"]

        assert config["command"] == "npx"
        assert "@upstash/context7-mcp" in config["args"]


@pytest.mark.integration
class TestLauncherDryRun:
    """Integration tests for launcher dry-run functionality."""

    def test_start_claude_dry_run_returns_config_info(
        self, isolated_cortex_home: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Dry run should return configuration information."""
        # First bootstrap to create config
        installer.bootstrap(
            target_dir=isolated_cortex_home,
            force=False,
            dry_run=False,
            link_rules=False,
        )

        # Patch the cortex root resolution to use our isolated home
        with patch("claude_ctx_py.launcher._resolve_cortex_root", return_value=isolated_cortex_home):
            with patch("claude_ctx_py.core.base._resolve_plugin_assets_root", return_value=isolated_cortex_home):
                # This should not actually launch claude, just return info
                result = start_claude(dry_run=True)

        # Dry run returns 0
        assert result == 0


@pytest.mark.integration
class TestWizardConfig:
    """Integration tests for wizard configuration."""

    def test_wizard_config_defaults(self) -> None:
        """WizardConfig should have sensible defaults."""
        config = WizardConfig()

        # Check MCP defaults
        assert "context7" in config.selected_mcp_servers
        assert "mcp-memory" in config.selected_mcp_servers

        # Check other defaults
        assert config.setup_mcp is True
        assert config.link_rules is True
        assert config.post_setup_action == "none"

    def test_wizard_config_mcp_servers_exist(self) -> None:
        """Default MCP servers in config should exist in MCP_SERVERS."""
        config = WizardConfig()

        for server_id in config.selected_mcp_servers:
            assert server_id in MCP_SERVERS, f"Default server {server_id} not in MCP_SERVERS"
