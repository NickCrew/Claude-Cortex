"""Unit tests for core.skills module."""

from pathlib import Path
from unittest import mock
import pytest
from claude_ctx_py.core import skills

# --------------------------------------------------------------------------- fixtures

@pytest.fixture
def skills_dir(temp_claude_dir):
    """Return the path to the skills directory."""
    return temp_claude_dir / "skills"

@pytest.fixture
def valid_skill(skills_dir):
    """Create a valid skill for testing."""
    skill_path = skills_dir / "test-skill"
    skill_path.mkdir(parents=True, exist_ok=True)
    (skill_path / "SKILL.md").write_text(
        "---\nname: test-skill\ndescription: A test skill. Use when testing.\n---\nContent",
        encoding="utf-8"
    )
    return "test-skill"

@pytest.fixture
def invalid_skill(skills_dir):
    """Create an invalid skill (missing description) for testing."""
    skill_path = skills_dir / "invalid-skill"
    skill_path.mkdir(parents=True, exist_ok=True)
    (skill_path / "SKILL.md").write_text(
        "---\nname: invalid-skill\n---\nContent",
        encoding="utf-8"
    )
    return "invalid-skill"

# --------------------------------------------------------------------------- list_skills

def test_list_skills_empty(temp_claude_dir, monkeypatch):
    """Test listing skills when no skills exist."""
    monkeypatch.setattr(skills, "_resolve_claude_dir", lambda h=None: temp_claude_dir)
    result = skills.list_skills()
    assert "No skills found" in result

def test_list_skills_valid(temp_claude_dir, valid_skill, monkeypatch):
    """Test listing valid skills."""
    monkeypatch.setattr(skills, "_resolve_claude_dir", lambda h=None: temp_claude_dir)
    result = skills.list_skills()
    assert "Available skills:" in result
    assert "test-skill" in result
    assert "A test skill" in result

def test_list_skills_ignores_non_dirs(skills_dir, temp_claude_dir, monkeypatch):
    """Test that files in skills directory are ignored."""
    monkeypatch.setattr(skills, "_resolve_claude_dir", lambda h=None: temp_claude_dir)
    (skills_dir / "random.txt").touch()
    result = skills.list_skills()
    assert "No skills found" in result

def test_list_skills_ignores_missing_skill_md(skills_dir, temp_claude_dir, monkeypatch):
    """Test that directories without SKILL.md are ignored."""
    monkeypatch.setattr(skills, "_resolve_claude_dir", lambda h=None: temp_claude_dir)
    (skills_dir / "empty-skill").mkdir()
    result = skills.list_skills()
    assert "No skills found" in result

def test_list_skills_handles_missing_frontmatter(skills_dir, temp_claude_dir, monkeypatch):
    """Test handling of skills with missing frontmatter."""
    monkeypatch.setattr(skills, "_resolve_claude_dir", lambda h=None: temp_claude_dir)
    skill_path = skills_dir / "bad-skill"
    skill_path.mkdir()
    (skill_path / "SKILL.md").write_text("Just content", encoding="utf-8")
    
    result = skills.list_skills()
    assert "bad-skill" in result
    assert "No description" in result

def test_list_skills_truncates_long_description(skills_dir, temp_claude_dir, monkeypatch):
    """Test that long descriptions are truncated."""
    monkeypatch.setattr(skills, "_resolve_claude_dir", lambda h=None: temp_claude_dir)
    skill_path = skills_dir / "long-skill"
    skill_path.mkdir()
    long_desc = "A" * 100
    (skill_path / "SKILL.md").write_text(
        f"---\nname: long-skill\ndescription: {long_desc}\n---\nContent",
        encoding="utf-8"
    )
    
    result = skills.list_skills()
    assert "long-skill" in result
    assert "..." in result
    assert len(result.splitlines()[-1]) < 120  # Ensure it's reasonably short

# --------------------------------------------------------------------------- skill_info

def test_skill_info_valid(temp_claude_dir, valid_skill, monkeypatch):
    """Test retrieving info for a valid skill."""
    monkeypatch.setattr(skills, "_resolve_claude_dir", lambda h=None: temp_claude_dir)
    code, result = skills.skill_info("test-skill")
    assert code == 0
    assert "Skill: test-skill" in result
    assert "Description:" in result
    assert "A test skill" in result
    assert "Size:" in result
    assert "Location:" in result

def test_skill_info_not_found(temp_claude_dir, monkeypatch):
    """Test info for non-existent skill."""
    monkeypatch.setattr(skills, "_resolve_claude_dir", lambda h=None: temp_claude_dir)
    code, result = skills.skill_info("missing-skill")
    assert code == 1
    assert "not found" in result

def test_skill_info_missing_name(temp_claude_dir, monkeypatch):
    """Test info with empty name."""
    monkeypatch.setattr(skills, "_resolve_claude_dir", lambda h=None: temp_claude_dir)
    code, result = skills.skill_info("")
    assert code == 1
    assert "Usage:" in result

def test_skill_info_invalid_frontmatter(skills_dir, temp_claude_dir, monkeypatch):
    """Test info for skill with invalid frontmatter."""
    monkeypatch.setattr(skills, "_resolve_claude_dir", lambda h=None: temp_claude_dir)
    skill_path = skills_dir / "bad-skill"
    skill_path.mkdir()
    (skill_path / "SKILL.md").write_text("No frontmatter", encoding="utf-8")
    
    code, result = skills.skill_info("bad-skill")
    assert code == 1
    assert "no valid frontmatter" in result

# --------------------------------------------------------------------------- skill_validate

def test_skill_validate_valid(temp_claude_dir, valid_skill, monkeypatch):
    """Test validation of a valid skill."""
    monkeypatch.setattr(skills, "_resolve_claude_dir", lambda h=None: temp_claude_dir)
    code, result = skills.skill_validate("test-skill")
    assert code == 0
    assert "test-skill: Valid" in result

def test_skill_validate_invalid(temp_claude_dir, invalid_skill, monkeypatch):
    """Test validation of an invalid skill."""
    monkeypatch.setattr(skills, "_resolve_claude_dir", lambda h=None: temp_claude_dir)
    code, result = skills.skill_validate("invalid-skill")
    assert code == 1
    assert "Missing 'description' field" in result

def test_skill_validate_all(temp_claude_dir, valid_skill, invalid_skill, monkeypatch):
    """Test validation of all skills."""
    monkeypatch.setattr(skills, "_resolve_claude_dir", lambda h=None: temp_claude_dir)
    code, result = skills.skill_validate("--all")
    assert code == 1  # Should fail because one skill is invalid
    assert "test-skill: Valid" in result
    assert "Missing 'description' field" in result
    assert "Validated: 1 passed, 1 issues" in result

def test_skill_validate_missing_use_when(skills_dir, temp_claude_dir, monkeypatch):
    """Test validation detects missing 'Use when' trigger."""
    monkeypatch.setattr(skills, "_resolve_claude_dir", lambda h=None: temp_claude_dir)
    skill_path = skills_dir / "missing-trigger"
    skill_path.mkdir()
    (skill_path / "SKILL.md").write_text(
        "---\nname: missing-trigger\ndescription: A valid description but no trigger\n---\nContent",
        encoding="utf-8"
    )
    
    code, result = skills.skill_validate("missing-trigger")
    assert code == 1
    assert "Description missing 'Use when' trigger" in result

def test_skill_validate_no_skills_dir(tmp_path, monkeypatch):
    """Test validation when skills directory is missing."""
    empty_home = tmp_path / "empty_home"
    empty_home.mkdir()
    monkeypatch.setattr(skills, "_resolve_claude_dir", lambda h=None: empty_home)
    
    code, result = skills.skill_validate("any")
    assert code == 1
    assert "No skills directory found" in result

def test_skill_validate_no_skills_to_validate(temp_claude_dir, monkeypatch):
    """Test validation when no skills are specified or found."""
    monkeypatch.setattr(skills, "_resolve_claude_dir", lambda h=None: temp_claude_dir)
    code, result = skills.skill_validate()
    assert code == 1
    assert "No skills to validate" in result
