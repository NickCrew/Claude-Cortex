"""Unit tests for community module (community skill management)."""

from __future__ import annotations

import json
from pathlib import Path
import pytest
from unittest import mock

from claude_ctx_py import community
from claude_ctx_py.exceptions import (
    SkillNotFoundError,
    SkillValidationError,
    SkillInstallationError,
    RatingError,
)


@pytest.fixture
def valid_community_skill(temp_claude_dir):
    """Create a valid community skill file."""
    skill_dir = temp_claude_dir / "community" / "skills"
    skill_dir.mkdir(parents=True, exist_ok=True)
    skill_path = skill_dir / "test-skill.md"
    content = """---
name: test-skill
version: 1.0.0
author: Test Author
license: Apache-2.0
description: A valid test skill
tags:
  - testing
  - automation
token_budget: 1000
---

## Purpose
Test purpose.

## Usage
Test usage.
"""
    skill_path.write_text(content, encoding="utf-8")
    return skill_path


@pytest.fixture
def invalid_community_skill(temp_claude_dir):
    """Create an invalid community skill file."""
    skill_dir = temp_claude_dir / "community" / "skills"
    skill_dir.mkdir(parents=True, exist_ok=True)
    skill_path = skill_dir / "invalid-skill.md"
    content = """---
name: Invalid Skill
description: Missing fields
---
Content
"""
    skill_path.write_text(content, encoding="utf-8")
    return skill_path


@pytest.mark.unit
class TestCommunitySkillManagement:
    """Tests for community skill management functions."""

    def test_validate_contribution_valid(self, valid_community_skill):
        """Test validation of a valid skill."""
        is_valid, errors = community.validate_contribution(valid_community_skill)
        assert is_valid
        assert not errors

    def test_validate_contribution_invalid(self, invalid_community_skill):
        """Test validation of an invalid skill."""
        is_valid, errors = community.validate_contribution(invalid_community_skill)
        assert not is_valid
        assert any("hyphen-case" in e for e in errors)
        assert any("Missing required field" in e for e in errors)

    def test_validate_contribution_missing_file(self, tmp_path):
        """Test validation of a non-existent file."""
        is_valid, errors = community.validate_contribution(tmp_path / "missing.md")
        assert not is_valid
        assert any("File not found" in e for e in errors)

    def test_validate_contribution_invalid_yaml(self, temp_claude_dir):
        """Test validation with invalid YAML."""
        skill_path = temp_claude_dir / "bad-yaml.md"
        # Tabs are not allowed in YAML
        skill_path.write_text("---\nkey:\n\tvalue\n---\n", encoding="utf-8")
        is_valid, errors = community.validate_contribution(skill_path)
        assert not is_valid
        assert any("Invalid YAML" in e for e in errors)

    def test_get_community_skills(self, temp_claude_dir, valid_community_skill):
        """Test listing community skills."""
        # Exact name match
        skills = community.get_community_skills(temp_claude_dir)
        assert len(skills) == 1
        skill = skills[0]
        assert skill["name"] == "test-skill"
        assert skill["author"] == "Test Author"
        assert skill["installed"] is False

    def test_get_community_skills_empty(self, temp_claude_dir):
        """Test listing when no skills exist."""
        # Ensure directory is empty
        skills_dir = temp_claude_dir / "community" / "skills"
        if skills_dir.exists():
            for f in skills_dir.iterdir():
                f.unlink()
        
        skills = community.get_community_skills(temp_claude_dir)
        assert skills == []

    def test_install_community_skill_success(self, temp_claude_dir, valid_community_skill):
        """Test successful installation of a community skill."""
        success = community.install_community_skill("test-skill", temp_claude_dir)
        assert success
        
        installed_path = temp_claude_dir / "skills" / "test-skill.md"
        assert installed_path.exists()
        assert installed_path.read_text() == valid_community_skill.read_text()

    def test_install_community_skill_not_found(self, temp_claude_dir):
        """Test installing a non-existent skill."""
        with pytest.raises(SkillNotFoundError):
            community.install_community_skill("missing-skill", temp_claude_dir)

    def test_install_community_skill_validation_failure(self, temp_claude_dir, invalid_community_skill):
        """Test installing an invalid skill."""
        with pytest.raises(SkillValidationError):
            community.install_community_skill("invalid-skill", temp_claude_dir)

    def test_rate_skill_success(self, temp_claude_dir):
        """Test successful rating submission."""
        success = community.rate_skill("test-skill", 5, temp_claude_dir)
        assert success
        
        rating_file = temp_claude_dir / "community" / "ratings" / "test-skill.json"
        assert rating_file.exists()
        data = json.loads(rating_file.read_text())
        assert data["ratings"] == [5]
        assert data["average"] == 5.0

    def test_rate_skill_multiple(self, temp_claude_dir):
        """Test calculating average rating."""
        community.rate_skill("test-skill", 5, temp_claude_dir)
        community.rate_skill("test-skill", 3, temp_claude_dir)
        
        rating_file = temp_claude_dir / "community" / "ratings" / "test-skill.json"
        data = json.loads(rating_file.read_text())
        assert data["ratings"] == [5, 3]
        assert data["average"] == 4.0

    def test_rate_skill_invalid_value(self, temp_claude_dir):
        """Test validation of rating value."""
        with pytest.raises(RatingError):
            community.rate_skill("test-skill", 6, temp_claude_dir)
        with pytest.raises(RatingError):
            community.rate_skill("test-skill", 0, temp_claude_dir)

    def test_search_skills(self, temp_claude_dir, valid_community_skill):
        """Test searching skills."""
        # Exact name match
        results = community.search_skills("test-skill", [], temp_claude_dir)
        assert len(results) == 1
        assert results[0]["name"] == "test-skill"

        # Partial match
        results = community.search_skills("test", [], temp_claude_dir)
        assert len(results) == 1

        # Tag match
        results = community.search_skills("", ["automation"], temp_claude_dir)
        assert len(results) == 1

        # No match
        results = community.search_skills("nonexistent", [], temp_claude_dir)
        assert len(results) == 0