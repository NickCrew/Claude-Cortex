"""Unit tests for asset discovery and installation."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from claude_ctx_py.core.asset_discovery import (
    Asset,
    AssetCategory,
    ClaudeDir,
    InstallStatus,
    discover_plugin_assets,
    find_claude_directories,
    get_installed_assets,
    check_installation_status,
    get_plugin_root,
)
from claude_ctx_py.core.asset_installer import (
    install_asset,
    uninstall_asset,
    get_asset_diff,
    bulk_install,
    get_installed_path,
)


class TestAsset:
    """Tests for Asset dataclass."""

    def test_asset_creation(self):
        """Test Asset dataclass creation."""
        asset = Asset(
            name="test-asset",
            category=AssetCategory.AGENTS,
            source_path=Path("/test/path"),
            description="Test description",
            version="1.0",
            dependencies=["dep1"],
            metadata={"key": "value"},
            namespace=None,
        )
        assert asset.name == "test-asset"
        assert asset.category == AssetCategory.AGENTS
        assert asset.description == "Test description"

    def test_asset_display_name_with_namespace(self):
        """Test Asset display_name with namespace."""
        asset = Asset(
            name="test",
            category=AssetCategory.COMMANDS,
            source_path=Path("/test"),
            description="",
            version=None,
            dependencies=[],
            metadata={},
            namespace="analyze",
        )
        assert asset.display_name == "analyze:test"

    def test_asset_display_name_without_namespace(self):
        """Test Asset display_name without namespace."""
        asset = Asset(
            name="test",
            category=AssetCategory.HOOKS,
            source_path=Path("/test"),
            description="",
            version=None,
            dependencies=[],
            metadata={},
            namespace=None,
        )
        assert asset.display_name == "test"

    def test_asset_install_target(self):
        """Test Asset install_target property."""
        asset = Asset(
            name="test",
            category=AssetCategory.AGENTS,
            source_path=Path("/test/test.md"),
            description="",
            version=None,
            dependencies=[],
            metadata={},
            namespace=None,
        )
        assert asset.install_target == "agents/test.md"


class TestClaudeDir:
    """Tests for ClaudeDir dataclass."""

    def test_claude_dir_creation(self):
        """Test ClaudeDir dataclass creation."""
        claude_dir = ClaudeDir(
            path=Path("/test/.cortex"),
            scope="project",
            installed_assets={"agents": ["test"]},
        )
        assert claude_dir.scope == "project"
        assert claude_dir.installed_assets == {"agents": ["test"]}


class TestPluginRoot:
    """Tests for plugin root detection."""

    def test_get_plugin_root(self):
        """Test that plugin root is detected."""
        root = get_plugin_root()
        assert root is not None
        assert root.exists()


class TestAssetDiscovery:
    """Tests for asset discovery functions."""

    def test_discover_plugin_assets(self):
        """Test full asset discovery."""
        assets = discover_plugin_assets()
        assert isinstance(assets, dict)
        # Should have at least some categories
        for category in [
            "hooks",
            "commands",
            "agents",
            "skills",
            "modes",
            "workflows",
            "flags",
            "rules",
            "profiles",
            "scenarios",
            "tasks",
            "settings",
        ]:
            assert category in assets

    def test_discover_hooks(self):
        """Test hook discovery via discover_plugin_assets."""
        assets = discover_plugin_assets()
        hooks = assets.get("hooks", [])
        assert isinstance(hooks, list)
        for hook in hooks:
            assert isinstance(hook, Asset)
            assert hook.category == AssetCategory.HOOKS

    def test_discover_commands(self):
        """Test command discovery via discover_plugin_assets."""
        assets = discover_plugin_assets()
        commands = assets.get("commands", [])
        assert isinstance(commands, list)
        for cmd in commands:
            assert isinstance(cmd, Asset)
            assert cmd.category == AssetCategory.COMMANDS

    def test_discover_agents(self):
        """Test agent discovery via discover_plugin_assets."""
        assets = discover_plugin_assets()
        agents = assets.get("agents", [])
        assert isinstance(agents, list)
        for agent in agents:
            assert isinstance(agent, Asset)
            assert agent.category == AssetCategory.AGENTS

    def test_discover_skills(self):
        """Test skill discovery via discover_plugin_assets."""
        assets = discover_plugin_assets()
        skills = assets.get("skills", [])
        assert isinstance(skills, list)
        for skill in skills:
            assert isinstance(skill, Asset)
            assert skill.category == AssetCategory.SKILLS

    def test_discover_modes(self):
        """Test mode discovery via discover_plugin_assets."""
        assets = discover_plugin_assets()
        modes = assets.get("modes", [])
        assert isinstance(modes, list)
        for mode in modes:
            assert isinstance(mode, Asset)
            assert mode.category == AssetCategory.MODES

    def test_discover_workflows(self):
        """Test workflow discovery via discover_plugin_assets."""
        assets = discover_plugin_assets()
        workflows = assets.get("workflows", [])
        assert isinstance(workflows, list)
        for wf in workflows:
            assert isinstance(wf, Asset)
            assert wf.category == AssetCategory.WORKFLOWS

    def test_discover_flags(self):
        """Test flag discovery via discover_plugin_assets."""
        assets = discover_plugin_assets()
        flags = assets.get("flags", [])
        assert isinstance(flags, list)
        for flag in flags:
            assert isinstance(flag, Asset)
            assert flag.category == AssetCategory.FLAGS

    def test_discover_settings(self):
        """Test settings discovery via discover_plugin_assets."""
        assets = discover_plugin_assets()
        settings = assets.get("settings", [])
        assert isinstance(settings, list)
        for setting in settings:
            assert isinstance(setting, Asset)
            assert setting.category == AssetCategory.SETTINGS


class TestClaudeDirectoryDiscovery:
    """Tests for cortex directory discovery."""

    def test_find_claude_directories(self):
        """Test finding cortex directories."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            # Create a project .claude directory
            project_claude = tmp_path / ".claude"
            project_claude.mkdir()

            dirs = find_claude_directories(tmp_path)
            assert isinstance(dirs, list)
            # Should find at least the global ~/.cortex (if exists) or project dir

    def test_get_installed_assets(self):
        """Test getting installed assets from a directory."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)

            # Create some installed assets
            agents_dir = tmp_path / "agents"
            agents_dir.mkdir()
            (agents_dir / "test-agent.md").write_text("# Test Agent")

            hooks_dir = tmp_path / "hooks"
            hooks_dir.mkdir()
            (hooks_dir / "test-hook.py").write_text("# Test hook")

            installed = get_installed_assets(tmp_path)
            assert "agents" in installed
            assert "test-agent" in installed["agents"]
            assert "hooks" in installed
            assert "test-hook" in installed["hooks"]


class TestInstallStatus:
    """Tests for installation status checking."""

    def test_check_installation_status_not_installed(self):
        """Test status for uninstalled asset."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            asset = Asset(
                name="test",
                category=AssetCategory.AGENTS,
                source_path=Path("/nonexistent/test.md"),
                description="",
                version=None,
                dependencies=[],
                metadata={},
                namespace=None,
            )
            status = check_installation_status(asset, tmp_path)
            assert status == InstallStatus.NOT_INSTALLED

    def test_check_installation_status_installed_same(self):
        """Test status for installed asset with same content."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            source_dir = Path(tmp) / "source"
            source_dir.mkdir()
            source_file = source_dir / "test.md"
            source_file.write_text("# Test Content")

            # Install to target
            target_agents = tmp_path / "agents"
            target_agents.mkdir()
            target_file = target_agents / "test.md"
            target_file.write_text("# Test Content")

            asset = Asset(
                name="test",
                category=AssetCategory.AGENTS,
                source_path=source_file,
                description="",
                version=None,
                dependencies=[],
                metadata={},
                namespace=None,
            )
            status = check_installation_status(asset, tmp_path)
            assert status == InstallStatus.INSTALLED_SAME

    def test_check_installation_status_installed_different(self):
        """Test status for installed asset with different content."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            source_dir = Path(tmp) / "source"
            source_dir.mkdir()
            source_file = source_dir / "test.md"
            source_file.write_text("# Source Content")

            # Install to target with different content
            target_agents = tmp_path / "agents"
            target_agents.mkdir()
            target_file = target_agents / "test.md"
            target_file.write_text("# Different Content")

            asset = Asset(
                name="test",
                category=AssetCategory.AGENTS,
                source_path=source_file,
                description="",
                version=None,
                dependencies=[],
                metadata={},
                namespace=None,
            )
            status = check_installation_status(asset, tmp_path)
            assert status == InstallStatus.INSTALLED_DIFFERENT


class TestAssetInstaller:
    """Tests for asset installation functions."""

    def test_install_agent(self):
        """Test installing an agent."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            source_dir = tmp_path / "source"
            source_dir.mkdir()
            source_file = source_dir / "test-agent.md"
            source_file.write_text("# Test Agent\n\nContent here")

            target_dir = tmp_path / "target"
            target_dir.mkdir()
            # Provide CLAUDE.md so commented reference can be added
            (target_dir / "CLAUDE.md").write_text("# CLAUDE assets\n")

            asset = Asset(
                name="test-agent",
                category=AssetCategory.AGENTS,
                source_path=source_file,
                description="Test agent",
                version=None,
                dependencies=[],
                metadata={},
                namespace=None,
            )

            exit_code, message = install_asset(asset, target_dir, activate=True)
            assert exit_code == 0
            assert "Installed agent" in message

            # Verify file was created
            installed = target_dir / "agents" / "test-agent.md"
            assert installed.exists()
            assert installed.read_text() == "# Test Agent\n\nContent here"

            # Ensure a commented CLAUDE.md reference was appended
            claude_md = (target_dir / "CLAUDE.md").read_text()
            assert "<!-- @agents/test-agent.md -->" in claude_md

    def test_install_command(self):
        """Test installing a command."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            source_dir = tmp_path / "source"
            source_dir.mkdir()
            source_file = source_dir / "test-cmd.md"
            source_file.write_text("# Test Command")

            target_dir = tmp_path / "target"
            target_dir.mkdir()

            asset = Asset(
                name="test-cmd",
                category=AssetCategory.COMMANDS,
                source_path=source_file,
                description="Test command",
                version=None,
                dependencies=[],
                metadata={},
                namespace="analyze",
            )

            exit_code, message = install_asset(asset, target_dir)
            assert exit_code == 0

            # Verify file was created in namespace dir
            installed = target_dir / "commands" / "analyze" / "test-cmd.md"
            assert installed.exists()

    def test_install_skill(self):
        """Test installing a skill."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            source_dir = tmp_path / "source" / "test-skill"
            source_dir.mkdir(parents=True)
            (source_dir / "SKILL.md").write_text("# Test Skill")
            (source_dir / "examples").mkdir()
            (source_dir / "examples" / "example.py").write_text("# example")

            target_dir = tmp_path / "target"
            target_dir.mkdir()

            asset = Asset(
                name="test-skill",
                category=AssetCategory.SKILLS,
                source_path=source_dir,
                description="Test skill",
                version=None,
                dependencies=[],
                metadata={},
                namespace=None,
            )

            exit_code, message = install_asset(asset, target_dir)
            assert exit_code == 0

            # Verify skill directory was copied
            installed = target_dir / "skills" / "test-skill"
            assert installed.is_dir()
            assert (installed / "SKILL.md").exists()
            assert (installed / "examples" / "example.py").exists()

    def test_uninstall_agent(self):
        """Test uninstalling an agent."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            agents_dir = tmp_path / "agents"
            agents_dir.mkdir()
            agent_file = agents_dir / "test.md"
            agent_file.write_text("# Test")

            exit_code, message = uninstall_asset("agents", "test", tmp_path)
            assert exit_code == 0
            assert not agent_file.exists()

    def test_uninstall_not_installed(self):
        """Test uninstalling non-existent asset."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            exit_code, message = uninstall_asset("agents", "nonexistent", tmp_path)
            assert exit_code == 1
            assert "not installed" in message

    def test_get_asset_diff(self):
        """Test getting diff between source and installed."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            source_dir = tmp_path / "source"
            source_dir.mkdir()
            source_file = source_dir / "test.md"
            source_file.write_text("line1\nline2\nline3")

            # Install with different content
            target_agents = tmp_path / "agents"
            target_agents.mkdir()
            target_file = target_agents / "test.md"
            target_file.write_text("line1\nmodified\nline3")

            asset = Asset(
                name="test",
                category=AssetCategory.AGENTS,
                source_path=source_file,
                description="",
                version=None,
                dependencies=[],
                metadata={},
                namespace=None,
            )

            diff = get_asset_diff(asset, tmp_path)
            assert diff is not None
            assert "-modified" in diff or "+line2" in diff

    def test_get_asset_diff_identical(self):
        """Test diff returns None for identical files."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            source_dir = tmp_path / "source"
            source_dir.mkdir()
            source_file = source_dir / "test.md"
            source_file.write_text("identical content")

            target_agents = tmp_path / "agents"
            target_agents.mkdir()
            target_file = target_agents / "test.md"
            target_file.write_text("identical content")

            asset = Asset(
                name="test",
                category=AssetCategory.AGENTS,
                source_path=source_file,
                description="",
                version=None,
                dependencies=[],
                metadata={},
                namespace=None,
            )

            diff = get_asset_diff(asset, tmp_path)
            assert diff is None

    def test_bulk_install(self):
        """Test bulk installing multiple assets."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            source_dir = tmp_path / "source"
            source_dir.mkdir()

            assets = []
            for i in range(3):
                source_file = source_dir / f"agent{i}.md"
                source_file.write_text(f"# Agent {i}")
                assets.append(Asset(
                    name=f"agent{i}",
                    category=AssetCategory.AGENTS,
                    source_path=source_file,
                    description=f"Agent {i}",
                    version=None,
                    dependencies=[],
                    metadata={},
                    namespace=None,
                ))

            target_dir = tmp_path / "target"
            target_dir.mkdir()

            results = bulk_install(assets, target_dir)
            assert len(results) == 3
            for asset, exit_code, message in results:
                assert exit_code == 0

    def test_get_installed_path(self):
        """Test getting installed path for an asset."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            agents_dir = tmp_path / "agents"
            agents_dir.mkdir()
            agent_file = agents_dir / "test.md"
            agent_file.write_text("# Test")

            asset = Asset(
                name="test",
                category=AssetCategory.AGENTS,
                source_path=Path("/source/test.md"),
                description="",
                version=None,
                dependencies=[],
                metadata={},
                namespace=None,
            )

            path = get_installed_path(asset, tmp_path)
            assert path == agent_file

    def test_get_installed_path_not_found(self):
        """Test installed path returns None when not installed."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)

            asset = Asset(
                name="nonexistent",
                category=AssetCategory.AGENTS,
                source_path=Path("/source/test.md"),
                description="",
                version=None,
                dependencies=[],
                metadata={},
                namespace=None,
            )

            path = get_installed_path(asset, tmp_path)
            assert path is None
