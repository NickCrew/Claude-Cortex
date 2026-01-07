"""Unit tests for core.asset_installer module."""

import json
import shutil
from pathlib import Path
from unittest import mock
import pytest

from claude_ctx_py.core.asset_discovery import Asset, AssetCategory
from claude_ctx_py.core import asset_installer

# --------------------------------------------------------------------------- fixtures

@pytest.fixture
def temp_claude_dir(tmp_path):
    """Create a temporary .cortex directory structure."""
    claude_dir = tmp_path / ".cortex"
    claude_dir.mkdir()
    # Create required files
    (claude_dir / "CLAUDE.md").touch()
    (claude_dir / "FLAGS.md").touch()
    return claude_dir

@pytest.fixture
def mock_source_dir(tmp_path):
    """Create a mock source directory for assets."""
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    return source_dir

def create_mock_asset(source_dir, category, name, content="content", namespace=None):
    """Helper to create a mock asset."""
    if category == AssetCategory.SKILLS:
        asset_dir = source_dir / name
        asset_dir.mkdir(parents=True, exist_ok=True)
        (asset_dir / "SKILL.md").write_text(content, encoding="utf-8")
        source_path = asset_dir
    else:
        filename = f"{name}.md" if category != AssetCategory.WORKFLOWS else f"{name}.yaml"
        source_path = source_dir / filename
        source_path.write_text(content, encoding="utf-8")
    
    return Asset(
        name=name,
        category=category,
        source_path=source_path,
        description=f"Description for {name}",
        namespace=namespace
    )

# --------------------------------------------------------------------------- _add_commented_reference

def test_add_commented_reference_success(temp_claude_dir):
    """Test adding a reference to CLAUDE.md."""
    installed_file = temp_claude_dir / "agents" / "test.md"
    installed_file.parent.mkdir()
    installed_file.touch()
    
    asset_installer._add_commented_reference(temp_claude_dir, installed_file)
    
    content = (temp_claude_dir / "CLAUDE.md").read_text()
    assert "<!-- @agents/test.md -->" in content

def test_add_commented_reference_already_present(temp_claude_dir):
    """Test that duplicates are not added to CLAUDE.md."""
    installed_file = temp_claude_dir / "agents" / "test.md"
    installed_file.parent.mkdir()
    installed_file.touch()
    
    claude_md = temp_claude_dir / "CLAUDE.md"
    claude_md.write_text("@agents/test.md\n")
    
    asset_installer._add_commented_reference(temp_claude_dir, installed_file)
    
    content = claude_md.read_text()
    assert content.count("@agents/test.md") == 1

# --------------------------------------------------------------------------- install_asset

@pytest.mark.parametrize("category, name, target_subdir, filename", [
    (AssetCategory.AGENTS, "test-agent", "agents", "test-agent.md"),
    (AssetCategory.MODES, "test-mode", "modes", "test-mode.md"),
    (AssetCategory.WORKFLOWS, "test-workflow", "workflows", "test-workflow.yaml"),
    (AssetCategory.FLAGS, "test-flag", "flags", "test-flag.md"),
    (AssetCategory.PROFILES, "test-profile", "profiles", "test-profile.md"),
    (AssetCategory.SCENARIOS, "test-scenario", "scenarios", "test-scenario.md"),
    (AssetCategory.TASKS, "test-task", "tasks", "test-task.md"),
])
def test_install_simple_assets(temp_claude_dir, mock_source_dir, category, name, target_subdir, filename):
    """Test installation of various simple file-based assets."""
    asset = create_mock_asset(mock_source_dir, category, name)
    exit_code, msg = asset_installer.install_asset(asset, temp_claude_dir)
    
    assert exit_code == 0
    assert (temp_claude_dir / target_subdir / filename).exists()

def test_install_skill(temp_claude_dir, mock_source_dir):
    """Test skill installation (directory copy)."""
    asset = create_mock_asset(mock_source_dir, AssetCategory.SKILLS, "test-skill")
    exit_code, msg = asset_installer.install_asset(asset, temp_claude_dir)
    
    assert exit_code == 0
    assert (temp_claude_dir / "skills" / "test-skill" / "SKILL.md").exists()

def test_install_hook(temp_claude_dir, mock_source_dir):
    """Test hook installation and executable bit."""
    asset = create_mock_asset(mock_source_dir, AssetCategory.HOOKS, "test-hook")
    exit_code, msg = asset_installer.install_asset(asset, temp_claude_dir)
    
    assert exit_code == 0
    target_path = temp_claude_dir / "hooks" / "test-hook.md"
    assert target_path.exists()
    assert target_path.stat().st_mode & 0o111

def test_install_command_namespaced(temp_claude_dir, mock_source_dir):
    """Test namespaced command installation."""
    asset = create_mock_asset(mock_source_dir, AssetCategory.COMMANDS, "test-cmd", namespace="ns")
    exit_code, msg = asset_installer.install_asset(asset, temp_claude_dir)
    
    assert exit_code == 0
    assert (temp_claude_dir / "commands" / "ns" / "test-cmd.md").exists()

def test_install_agent_inactive(temp_claude_dir, mock_source_dir):
    """Test installing an agent as inactive."""
    asset = create_mock_asset(mock_source_dir, AssetCategory.AGENTS, "test-agent")
    exit_code, msg = asset_installer.install_asset(asset, temp_claude_dir, activate=False)
    
    assert exit_code == 0
    assert (temp_claude_dir / "inactive" / "agents" / "test-agent.md").exists()

# --------------------------------------------------------------------------- uninstall_asset

@pytest.mark.parametrize("category, name, target_subdir, filename", [
    ("agents", "test-agent", "agents", "test-agent.md"),
    ("modes", "test-mode", "modes", "test-mode.md"),
    ("workflows", "test-workflow", "workflows", "test-workflow.yaml"),
    ("profiles", "test-profile", "profiles", "test-profile.md"),
    ("scenarios", "test-scenario", "scenarios", "test-scenario.md"),
    ("tasks", "test-task", "tasks", "test-task.md"),
])
def test_uninstall_simple_assets(temp_claude_dir, category, name, target_subdir, filename):
    """Test uninstallation of various simple assets."""
    target_path = temp_claude_dir / target_subdir / filename
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.touch()
    
    exit_code, msg = asset_installer.uninstall_asset(category, name, temp_claude_dir)
    assert exit_code == 0
    assert not target_path.exists()

def test_uninstall_skill(temp_claude_dir):
    """Test skill uninstallation."""
    skill_dir = temp_claude_dir / "skills" / "test-skill"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").touch()
    
    exit_code, msg = asset_installer.uninstall_asset("skills", "test-skill", temp_claude_dir)
    assert exit_code == 0
    assert not skill_dir.exists()

def test_uninstall_flag_updates_flags_md(temp_claude_dir):
    """Test that uninstalling a flag removes reference from FLAGS.md."""
    flag_path = temp_claude_dir / "flags" / "test-flag.md"
    flag_path.parent.mkdir()
    flag_path.touch()
    
    flags_md = temp_claude_dir / "FLAGS.md"
    flags_md.write_text("@flags/test-flag.md\n@flags/other.md\n")
    
    exit_code, msg = asset_installer.uninstall_asset("flags", "test-flag", temp_claude_dir)
    assert exit_code == 0
    assert not flag_path.exists()
    assert "@flags/test-flag.md" not in flags_md.read_text()
    assert "@flags/other.md" in flags_md.read_text()

# --------------------------------------------------------------------------- diff & paths

def test_get_asset_diff(temp_claude_dir, mock_source_dir):
    """Test unified diff generation."""
    asset = create_mock_asset(mock_source_dir, AssetCategory.AGENTS, "test-agent", content="source content")
    
    target_path = temp_claude_dir / "agents" / "test-agent.md"
    target_path.parent.mkdir()
    target_path.write_text("installed content")
    
    diff = asset_installer.get_asset_diff(asset, temp_claude_dir)
    assert diff is not None
    assert "-installed content" in diff
    assert "+source content" in diff

def test_get_installed_path(temp_claude_dir):
    """Test resolving installed path for an asset."""
    # Test agent path (active)
    asset = Asset(name="test", category=AssetCategory.AGENTS, source_path=Path("test.md"), description="desc")
    target_path = temp_claude_dir / "agents" / "test.md"
    target_path.parent.mkdir()
    target_path.touch()
    
    assert asset_installer.get_installed_path(asset, temp_claude_dir) == target_path

# --------------------------------------------------------------------------- register_hook_in_settings

def test_register_hook_in_settings_new_file(tmp_path):
    """Test registering a hook in a new settings.json file."""
    settings_path = tmp_path / "settings.json"
    exit_code, msg = asset_installer.register_hook_in_settings(
        "test-hook", "echo hello", "UserPromptSubmit", settings_path
    )
    
    assert exit_code == 0
    data = json.loads(settings_path.read_text())
    assert data["hooks"]["UserPromptSubmit"][0]["hooks"][0]["command"] == "echo hello"

def test_register_hook_in_settings_existing_file(tmp_path):
    """Test registering a hook in an existing settings.json file."""
    settings_path = tmp_path / "settings.json"
    initial_settings = {"foo": "bar"}
    settings_path.write_text(json.dumps(initial_settings))
    
    exit_code, msg = asset_installer.register_hook_in_settings(
        "test-hook", "echo hello", "UserPromptSubmit", settings_path
    )
    
    assert exit_code == 0
    data = json.loads(settings_path.read_text())
    assert data["foo"] == "bar"
    assert data["hooks"]["UserPromptSubmit"][0]["hooks"][0]["command"] == "echo hello"
    assert settings_path.with_suffix(".json.bak").exists()

def test_register_hook_in_settings_duplicate(tmp_path):
    """Test that duplicate hooks are not registered."""
    settings_path = tmp_path / "settings.json"
    settings = {
        "hooks": {
            "UserPromptSubmit": [
                {"hooks": [{"command": "echo hello"}]}
            ]
        }
    }
    settings_path.write_text(json.dumps(settings))
    
    exit_code, msg = asset_installer.register_hook_in_settings(
        "test-hook", "echo hello", "UserPromptSubmit", settings_path
    )
    
    assert exit_code == 0
    assert "already registered" in msg
    data = json.loads(settings_path.read_text())
    assert len(data["hooks"]["UserPromptSubmit"]) == 1

# --------------------------------------------------------------------------- error handling

def test_install_asset_exception_handling(temp_claude_dir):
    """Test that install_asset handles exceptions gracefully."""
    asset = Asset(name="bad", category=AssetCategory.AGENTS, source_path=Path("/nonexistent"), description="desc")
    exit_code, msg = asset_installer.install_asset(asset, temp_claude_dir)
    assert exit_code == 1
    assert "Installation failed" in msg
