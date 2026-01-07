"""Unit tests for core.profiles module."""

from pathlib import Path
from unittest import mock
import pytest
from claude_ctx_py.core import profiles

# --------------------------------------------------------------------------- fixtures

@pytest.fixture
def temp_claude_dir(tmp_path):
    """Create a temporary .cortex directory structure."""
    claude_dir = tmp_path / ".cortex"
    claude_dir.mkdir()
    (claude_dir / "agents").mkdir()
    (claude_dir / "modes").mkdir()
    (claude_dir / "rules").mkdir()
    (claude_dir / "profiles").mkdir()
    (claude_dir / "FLAGS.md").touch()
    return claude_dir

# --------------------------------------------------------------------------- _apply_profile_flags

def test_apply_profile_flags_valid(temp_claude_dir):
    """Test applying profile flags modifies FLAGS.md correctly."""
    profiles._apply_profile_flags("minimal", temp_claude_dir)
    content = (temp_claude_dir / "FLAGS.md").read_text(encoding="utf-8")
    assert "@flags/mode-activation.md" in content
    assert "@flags/mcp-servers.md" in content
    assert "@flags/execution-control.md" in content

def test_apply_profile_flags_missing_flags_file(temp_claude_dir):
    """Test applying flags when FLAGS.md is missing (should do nothing)."""
    (temp_claude_dir / "FLAGS.md").unlink()
    profiles._apply_profile_flags("minimal", temp_claude_dir)
    assert not (temp_claude_dir / "FLAGS.md").exists()

def test_apply_profile_flags_existing_content(temp_claude_dir):
    """Test merging with existing content in FLAGS.md."""
    flags_path = temp_claude_dir / "FLAGS.md"
    flags_path.write_text("# Existing Header\n\n@flags/other.md\n", encoding="utf-8")
    
    profiles._apply_profile_flags("minimal", temp_claude_dir)
    content = flags_path.read_text(encoding="utf-8")
    
    assert "# Existing Header" in content
    # apply_profile_flags replaces existing flags with the profile's flags
    assert "@flags/other.md" not in content
    assert "@flags/mode-activation.md" in content

def test_apply_profile_flags_no_duplicates(temp_claude_dir):
    """Test idempotency of applying flags."""
    flags_path = temp_claude_dir / "FLAGS.md"
    profiles._apply_profile_flags("minimal", temp_claude_dir)
    content_first = flags_path.read_text(encoding="utf-8")
    
    profiles._apply_profile_flags("minimal", temp_claude_dir)
    content_second = flags_path.read_text(encoding="utf-8")
    
    assert content_first == content_second
    assert content_first.count("@flags/mode-activation.md") == 1

# --------------------------------------------------------------------------- profile_list

def test_profile_list_defaults(temp_claude_dir, monkeypatch):
    """Test listing built-in profiles."""
    monkeypatch.setattr(profiles, "_resolve_claude_dir", lambda h=None: temp_claude_dir)
    output = profiles.profile_list()
    assert "minimal (built-in)" in output
    assert "full (built-in)" in output

def test_profile_list_saved(temp_claude_dir, monkeypatch):
    """Test listing saved profiles."""
    monkeypatch.setattr(profiles, "_resolve_claude_dir", lambda h=None: temp_claude_dir)
    (temp_claude_dir / "profiles" / "custom.profile").touch()
    
    output = profiles.profile_list()
    assert "custom (saved)" in output

# --------------------------------------------------------------------------- profile_save

def test_profile_save_creates_file(temp_claude_dir, monkeypatch):
    """Test saving a profile creates the correct file."""
    monkeypatch.setattr(profiles, "_resolve_claude_dir", lambda h=None: temp_claude_dir)
    monkeypatch.setattr(profiles, "_parse_active_entries", lambda p: ["item1", "item2"])
    
    # Create some mock agents
    (temp_claude_dir / "agents" / "agent1.md").touch()
    
    exit_code, msg = profiles.profile_save("my-profile")
    
    assert exit_code == 0
    assert "Saved profile: my-profile" in msg
    
    profile_path = temp_claude_dir / "profiles" / "my-profile.profile"
    assert profile_path.exists()
    content = profile_path.read_text(encoding="utf-8")
    assert 'AGENTS="agent1.md"' in content
    assert 'MODES="item1 item2"' in content
    assert 'RULES="item1 item2"' in content

# --------------------------------------------------------------------------- profile_minimal

@mock.patch("claude_ctx_py.core.profiles.agent_activate")
@mock.patch("claude_ctx_py.core.profiles.agent_deactivate")
@mock.patch("claude_ctx_py.core.profiles.mode_deactivate")
def test_profile_minimal_resets_state(mock_mode_deact, mock_agent_deact, mock_agent_act, temp_claude_dir, monkeypatch):
    """Test loading minimal profile resets state."""
    monkeypatch.setattr(profiles, "_resolve_claude_dir", lambda h=None: temp_claude_dir)
    
    # Mock return values
    mock_agent_act.return_value = (0, "Activated")
    mock_agent_deact.return_value = (0, "Deactivated")
    mock_mode_deact.return_value = (0, "Deactivated")
    
    # Create dummy active files to trigger deactivation logic
    (temp_claude_dir / "agents" / "extra-agent.md").touch()
    (temp_claude_dir / "modes" / "extra-mode.md").touch()
    (temp_claude_dir / ".active-rules").write_text("some-rule\n", encoding="utf-8")
    
    exit_code, msg = profiles.profile_minimal()
    
    assert exit_code == 0
    assert "Loaded profile: minimal" in msg
    assert not (temp_claude_dir / ".active-rules").exists()
    
    # Verify calls
    mock_agent_deact.assert_called()
    mock_mode_deact.assert_called()
    mock_agent_act.assert_called()

# --------------------------------------------------------------------------- _load_profile_with_agents

@mock.patch("claude_ctx_py.core.profiles._profile_reset")
@mock.patch("claude_ctx_py.core.profiles.agent_activate")
def test_load_profile_with_agents_success(mock_activate, mock_reset, temp_claude_dir, monkeypatch):
    """Test generic profile loader success path."""
    monkeypatch.setattr(profiles, "_resolve_claude_dir", lambda h=None: temp_claude_dir)
    
    mock_reset.return_value = (0, "Reset complete")
    mock_activate.return_value = (0, "Activated agent")
    
    exit_code, msg = profiles._load_profile_with_agents(
        "test-profile",
        ["agent1", "agent2"]
    )
    
    assert exit_code == 0
    assert "Loaded profile: test-profile" in msg
    assert mock_activate.call_count == 2

@mock.patch("claude_ctx_py.core.profiles._profile_reset")
@mock.patch("claude_ctx_py.core.profiles.agent_activate")
def test_load_profile_with_agents_activation_failure(mock_activate, mock_reset, temp_claude_dir, monkeypatch):
    """Test generic profile loader handles activation failure."""
    monkeypatch.setattr(profiles, "_resolve_claude_dir", lambda h=None: temp_claude_dir)
    
    mock_reset.return_value = (0, "Reset complete")
    mock_activate.return_value = (1, "Failed to activate")
    
    exit_code, msg = profiles._load_profile_with_agents(
        "test-profile",
        ["agent1"]
    )
    
    assert exit_code == 1
    assert "Failed to activate" in msg

@mock.patch("claude_ctx_py.core.profiles._profile_reset")
def test_load_profile_with_agents_reset_failure(mock_reset, temp_claude_dir, monkeypatch):
    """Test generic profile loader handles reset failure."""
    monkeypatch.setattr(profiles, "_resolve_claude_dir", lambda h=None: temp_claude_dir)
    
    mock_reset.return_value = (1, "Reset failed")
    
    exit_code, msg = profiles._load_profile_with_agents(
        "test-profile",
        ["agent1"]
    )
    
    assert exit_code == 1
    assert "Reset failed" in msg
