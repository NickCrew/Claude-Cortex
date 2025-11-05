"""Tests for semantic versioning utilities."""

import pytest
from pathlib import Path

from claude_ctx_py import versioner


class TestParseVersion:
    """Tests for parse_version function."""

    def test_parse_version_valid_simple(self):
        """Test parsing simple semantic version."""
        major, minor, patch = versioner.parse_version("1.2.3")

        assert major == 1
        assert minor == 2
        assert patch == 3

    def test_parse_version_with_v_prefix(self):
        """Test parsing version with 'v' prefix."""
        major, minor, patch = versioner.parse_version("v2.0.1")

        assert major == 2
        assert minor == 0
        assert patch == 1

    def test_parse_version_zeros(self):
        """Test parsing version with zeros."""
        major, minor, patch = versioner.parse_version("0.0.0")

        assert major == 0
        assert minor == 0
        assert patch == 0

    def test_parse_version_large_numbers(self):
        """Test parsing version with large numbers."""
        major, minor, patch = versioner.parse_version("10.25.100")

        assert major == 10
        assert minor == 25
        assert patch == 100

    @pytest.mark.parametrize("invalid_version", [
        "1.2",           # Missing patch
        "1",             # Missing minor and patch
        "1.2.3.4",       # Too many components
        "a.b.c",         # Non-numeric
        "1.2.3-beta",    # Pre-release tag not supported
        "1.2.3+build",   # Build metadata not supported
        "",              # Empty string
        "v",             # Just prefix
    ])
    def test_parse_version_invalid_formats(self, invalid_version):
        """Test parsing invalid version formats raises ValueError."""
        with pytest.raises(ValueError, match="Invalid semantic version"):
            versioner.parse_version(invalid_version)


class TestCheckCompatibility:
    """Tests for check_compatibility function."""

    # Exact version tests
    def test_check_compatibility_exact_match(self):
        """Test exact version match."""
        assert versioner.check_compatibility("1.2.3", "1.2.3") is True

    def test_check_compatibility_exact_mismatch(self):
        """Test exact version mismatch."""
        assert versioner.check_compatibility("1.2.3", "1.2.4") is False
        assert versioner.check_compatibility("1.2.3", "1.3.3") is False
        assert versioner.check_compatibility("1.2.3", "2.2.3") is False

    # Caret (^) tests
    def test_check_compatibility_caret_patch_update(self):
        """Test caret allows patch updates."""
        assert versioner.check_compatibility("^1.2.0", "1.2.5") is True

    def test_check_compatibility_caret_minor_update(self):
        """Test caret allows minor updates."""
        assert versioner.check_compatibility("^1.2.0", "1.3.0") is True
        assert versioner.check_compatibility("^1.2.0", "1.10.5") is True

    def test_check_compatibility_caret_major_mismatch(self):
        """Test caret blocks major version changes."""
        assert versioner.check_compatibility("^1.2.0", "2.0.0") is False
        assert versioner.check_compatibility("^1.2.0", "0.9.9") is False

    def test_check_compatibility_caret_exact_version(self):
        """Test caret accepts exact version."""
        assert versioner.check_compatibility("^1.2.0", "1.2.0") is True

    def test_check_compatibility_caret_downgrade(self):
        """Test caret blocks downgrades."""
        assert versioner.check_compatibility("^1.2.5", "1.2.3") is False

    # Tilde (~) tests
    def test_check_compatibility_tilde_patch_update(self):
        """Test tilde allows patch updates."""
        assert versioner.check_compatibility("~1.2.0", "1.2.5") is True

    def test_check_compatibility_tilde_minor_blocked(self):
        """Test tilde blocks minor updates."""
        assert versioner.check_compatibility("~1.2.0", "1.3.0") is False

    def test_check_compatibility_tilde_major_blocked(self):
        """Test tilde blocks major updates."""
        assert versioner.check_compatibility("~1.2.0", "2.2.0") is False

    def test_check_compatibility_tilde_exact_version(self):
        """Test tilde accepts exact version."""
        assert versioner.check_compatibility("~1.2.0", "1.2.0") is True

    def test_check_compatibility_tilde_downgrade(self):
        """Test tilde blocks downgrades."""
        assert versioner.check_compatibility("~1.2.5", "1.2.3") is False

    # Minimum (>=) tests
    def test_check_compatibility_minimum_exact(self):
        """Test minimum accepts exact version."""
        assert versioner.check_compatibility(">=1.2.0", "1.2.0") is True

    def test_check_compatibility_minimum_higher(self):
        """Test minimum accepts higher versions."""
        assert versioner.check_compatibility(">=1.2.0", "1.2.5") is True
        assert versioner.check_compatibility(">=1.2.0", "1.3.0") is True
        assert versioner.check_compatibility(">=1.2.0", "2.0.0") is True

    def test_check_compatibility_minimum_lower(self):
        """Test minimum blocks lower versions."""
        assert versioner.check_compatibility(">=1.2.0", "1.1.9") is False
        assert versioner.check_compatibility(">=1.2.0", "0.9.9") is False

    # Latest tests
    def test_check_compatibility_latest_always_matches(self):
        """Test that 'latest' always matches."""
        assert versioner.check_compatibility("latest", "0.0.1") is True
        assert versioner.check_compatibility("latest", "999.999.999") is True
        assert versioner.check_compatibility("LATEST", "1.0.0") is True

    # Invalid version tests
    def test_check_compatibility_invalid_available_version(self):
        """Test compatibility check with invalid available version."""
        assert versioner.check_compatibility("1.2.0", "invalid") is False
        assert versioner.check_compatibility("^1.2.0", "not-a-version") is False

    def test_check_compatibility_invalid_requirement(self):
        """Test compatibility check with invalid requirement."""
        assert versioner.check_compatibility("invalid", "1.2.0") is False


class TestGetSkillVersions:
    """Tests for get_skill_versions function."""

    def test_get_skill_versions_multiple_versions(self, temp_claude_dir, skill_versions_dir):
        """Test getting all versions of a skill."""
        versions = versioner.get_skill_versions("pdf", temp_claude_dir)

        assert versions == ["2.1.0", "2.0.0", "1.5.3", "1.0.0"]

    def test_get_skill_versions_no_versions(self, temp_claude_dir):
        """Test getting versions for nonexistent skill."""
        versions = versioner.get_skill_versions("nonexistent", temp_claude_dir)

        assert versions == []

    def test_get_skill_versions_skills_dir_not_exists(self, tmp_path):
        """Test getting versions when skills directory doesn't exist."""
        non_existent_dir = tmp_path / "nonexistent"
        versions = versioner.get_skill_versions("pdf", non_existent_dir)

        assert versions == []

    def test_get_skill_versions_ignores_invalid_versions(self, temp_claude_dir):
        """Test that invalid version strings are skipped."""
        skills_dir = temp_claude_dir / "skills"

        # Create valid and invalid version directories
        (skills_dir / "test@1.0.0").mkdir()
        (skills_dir / "test@invalid").mkdir()
        (skills_dir / "test@2.0.0").mkdir()
        (skills_dir / "test@").mkdir()

        versions = versioner.get_skill_versions("test", temp_claude_dir)

        assert versions == ["2.0.0", "1.0.0"]

    def test_get_skill_versions_ignores_files(self, temp_claude_dir):
        """Test that non-directory entries are ignored."""
        skills_dir = temp_claude_dir / "skills"

        # Create directories
        (skills_dir / "test@1.0.0").mkdir()

        # Create a file (should be ignored)
        (skills_dir / "test@2.0.0").touch()

        versions = versioner.get_skill_versions("test", temp_claude_dir)

        assert versions == ["1.0.0"]


class TestGetLatestVersion:
    """Tests for get_latest_version function."""

    def test_get_latest_version_with_versions(self, temp_claude_dir, skill_versions_dir):
        """Test getting latest version when versions exist."""
        latest = versioner.get_latest_version("pdf", temp_claude_dir)

        assert latest == "2.1.0"

    def test_get_latest_version_no_versions(self, temp_claude_dir):
        """Test getting latest version when no versions exist."""
        latest = versioner.get_latest_version("nonexistent", temp_claude_dir)

        assert latest == "latest"


class TestValidateVersionRequirement:
    """Tests for validate_version_requirement function."""

    @pytest.mark.parametrize("valid_req", [
        "1.2.3",
        "0.0.0",
        "^1.2.3",
        "~1.2.3",
        ">=1.2.3",
        "latest",
        "LATEST",
    ])
    def test_validate_version_requirement_valid(self, valid_req):
        """Test validation of valid version requirements."""
        assert versioner.validate_version_requirement(valid_req) is True

    @pytest.mark.parametrize("invalid_req", [
        "invalid",
        "1.2",
        "a.b.c",
        "^invalid",
        "~not-a-version",
        ">=bad",
        "",
        "1.2.3-beta",
    ])
    def test_validate_version_requirement_invalid(self, invalid_req):
        """Test validation of invalid version requirements."""
        assert versioner.validate_version_requirement(invalid_req) is False


class TestParseSkillWithVersion:
    """Tests for parse_skill_with_version function."""

    def test_parse_skill_with_version_exact(self):
        """Test parsing skill with exact version."""
        name, version = versioner.parse_skill_with_version("pdf@1.2.3")

        assert name == "pdf"
        assert version == "1.2.3"

    def test_parse_skill_with_version_caret(self):
        """Test parsing skill with caret version."""
        name, version = versioner.parse_skill_with_version("pdf@^1.2.0")

        assert name == "pdf"
        assert version == "^1.2.0"

    def test_parse_skill_with_version_tilde(self):
        """Test parsing skill with tilde version."""
        name, version = versioner.parse_skill_with_version("pdf@~1.2.0")

        assert name == "pdf"
        assert version == "~1.2.0"

    def test_parse_skill_with_version_minimum(self):
        """Test parsing skill with minimum version."""
        name, version = versioner.parse_skill_with_version("pdf@>=1.2.0")

        assert name == "pdf"
        assert version == ">=1.2.0"

    def test_parse_skill_with_version_latest(self):
        """Test parsing skill with latest."""
        name, version = versioner.parse_skill_with_version("pdf@latest")

        assert name == "pdf"
        assert version == "latest"

    def test_parse_skill_with_version_no_version(self):
        """Test parsing skill without version defaults to latest."""
        name, version = versioner.parse_skill_with_version("pdf")

        assert name == "pdf"
        assert version == "latest"

    def test_parse_skill_with_version_whitespace(self):
        """Test parsing skill with whitespace is trimmed."""
        name, version = versioner.parse_skill_with_version("  pdf  @  1.2.3  ")

        assert name == "pdf"
        assert version == "1.2.3"

    def test_parse_skill_with_version_invalid_version(self):
        """Test parsing skill with invalid version raises ValueError."""
        with pytest.raises(ValueError, match="Invalid semantic version"):
            versioner.parse_skill_with_version("pdf@invalid")


class TestFormatSkillWithVersion:
    """Tests for format_skill_with_version function."""

    def test_format_skill_with_version_exact(self):
        """Test formatting skill with exact version."""
        result = versioner.format_skill_with_version("pdf", "1.2.3")

        assert result == "pdf@1.2.3"

    def test_format_skill_with_version_caret(self):
        """Test formatting skill with caret version."""
        result = versioner.format_skill_with_version("pdf", "^1.2.0")

        assert result == "pdf@^1.2.0"

    def test_format_skill_with_version_latest(self):
        """Test formatting skill with latest."""
        result = versioner.format_skill_with_version("pdf", "latest")

        assert result == "pdf@latest"

    def test_format_skill_with_version_empty_version(self):
        """Test formatting skill with empty version defaults to latest."""
        result = versioner.format_skill_with_version("pdf", "")

        assert result == "pdf@latest"

    def test_format_skill_with_version_empty_name(self):
        """Test formatting with empty skill name raises ValueError."""
        with pytest.raises(ValueError, match="Skill name cannot be empty"):
            versioner.format_skill_with_version("", "1.2.3")

    def test_format_skill_with_version_invalid_version(self):
        """Test formatting with invalid version raises ValueError."""
        with pytest.raises(ValueError, match="Invalid semantic version"):
            versioner.format_skill_with_version("pdf", "invalid")


class TestResolveVersion:
    """Tests for resolve_version function."""

    def test_resolve_version_latest(self, temp_claude_dir, skill_versions_dir):
        """Test resolving 'latest' returns highest version."""
        resolved = versioner.resolve_version("pdf", "latest", temp_claude_dir)

        assert resolved == "2.1.0"

    def test_resolve_version_exact_match(self, temp_claude_dir, skill_versions_dir):
        """Test resolving exact version match."""
        resolved = versioner.resolve_version("pdf", "1.5.3", temp_claude_dir)

        assert resolved == "1.5.3"

    def test_resolve_version_exact_no_match(self, temp_claude_dir, skill_versions_dir):
        """Test resolving exact version with no match."""
        resolved = versioner.resolve_version("pdf", "9.9.9", temp_claude_dir)

        assert resolved is None

    def test_resolve_version_caret(self, temp_claude_dir, skill_versions_dir):
        """Test resolving caret version requirement."""
        resolved = versioner.resolve_version("pdf", "^1.0.0", temp_claude_dir)

        # Should return highest 1.x.x version (1.5.3)
        assert resolved == "1.5.3"

    def test_resolve_version_tilde(self, temp_claude_dir, skill_versions_dir):
        """Test resolving tilde version requirement."""
        resolved = versioner.resolve_version("pdf", "~2.0.0", temp_claude_dir)

        # Should return highest 2.0.x version (2.0.0 is the only one)
        assert resolved == "2.0.0"

    def test_resolve_version_minimum(self, temp_claude_dir, skill_versions_dir):
        """Test resolving minimum version requirement."""
        resolved = versioner.resolve_version("pdf", ">=1.5.0", temp_claude_dir)

        # Should return highest version >= 1.5.0 (2.1.0)
        assert resolved == "2.1.0"

    def test_resolve_version_no_versions(self, temp_claude_dir):
        """Test resolving version when no versions exist."""
        resolved = versioner.resolve_version("nonexistent", "1.0.0", temp_claude_dir)

        assert resolved is None

    def test_resolve_version_no_compatible(self, temp_claude_dir, skill_versions_dir):
        """Test resolving when no compatible version exists."""
        resolved = versioner.resolve_version("pdf", "^3.0.0", temp_claude_dir)

        assert resolved is None


class TestLoadSkillMetadata:
    """Tests for load_skill_metadata function."""

    def test_load_skill_metadata_yaml(self, temp_claude_dir):
        """Test loading metadata from .yaml file."""
        skill_dir = temp_claude_dir / "skills" / "test@1.0.0"
        skill_dir.mkdir(parents=True)

        metadata_file = skill_dir / "skill.yaml"
        metadata_file.write_text(
            "name: test\nversion: 1.0.0\ndescription: Test skill\n",
            encoding="utf-8"
        )

        metadata = versioner.load_skill_metadata(skill_dir)

        assert metadata["name"] == "test"
        assert metadata["version"] == "1.0.0"
        assert metadata["description"] == "Test skill"

    def test_load_skill_metadata_yml(self, temp_claude_dir):
        """Test loading metadata from .yml file."""
        skill_dir = temp_claude_dir / "skills" / "test@1.0.0"
        skill_dir.mkdir(parents=True)

        metadata_file = skill_dir / "skill.yml"
        metadata_file.write_text(
            "name: test\nversion: 1.0.0\n",
            encoding="utf-8"
        )

        metadata = versioner.load_skill_metadata(skill_dir)

        assert metadata["name"] == "test"
        assert metadata["version"] == "1.0.0"

    def test_load_skill_metadata_no_yaml(self, temp_claude_dir):
        """Test loading metadata when no YAML file exists."""
        skill_dir = temp_claude_dir / "skills" / "test@1.0.0"
        skill_dir.mkdir(parents=True)

        metadata = versioner.load_skill_metadata(skill_dir)

        assert metadata == {}

    def test_load_skill_metadata_invalid_yaml(self, temp_claude_dir):
        """Test loading metadata with invalid YAML."""
        skill_dir = temp_claude_dir / "skills" / "test@1.0.0"
        skill_dir.mkdir(parents=True)

        metadata_file = skill_dir / "skill.yaml"
        metadata_file.write_text("invalid: yaml: content: [", encoding="utf-8")

        metadata = versioner.load_skill_metadata(skill_dir)

        assert metadata == {}

    def test_load_skill_metadata_not_dict(self, temp_claude_dir):
        """Test loading metadata that's not a dictionary."""
        skill_dir = temp_claude_dir / "skills" / "test@1.0.0"
        skill_dir.mkdir(parents=True)

        metadata_file = skill_dir / "skill.yaml"
        metadata_file.write_text("- item1\n- item2\n", encoding="utf-8")

        metadata = versioner.load_skill_metadata(skill_dir)

        assert metadata == {}


class TestCompareVersions:
    """Tests for compare_versions function."""

    def test_compare_versions_equal(self):
        """Test comparing equal versions."""
        assert versioner.compare_versions("1.2.3", "1.2.3") == 0

    def test_compare_versions_less_than(self):
        """Test comparing when first is less than second."""
        assert versioner.compare_versions("1.2.3", "1.2.4") == -1
        assert versioner.compare_versions("1.2.3", "1.3.0") == -1
        assert versioner.compare_versions("1.2.3", "2.0.0") == -1

    def test_compare_versions_greater_than(self):
        """Test comparing when first is greater than second."""
        assert versioner.compare_versions("1.2.4", "1.2.3") == 1
        assert versioner.compare_versions("1.3.0", "1.2.3") == 1
        assert versioner.compare_versions("2.0.0", "1.2.3") == 1

    def test_compare_versions_major_difference(self):
        """Test major version differences."""
        assert versioner.compare_versions("2.0.0", "1.9.9") == 1
        assert versioner.compare_versions("1.0.0", "2.0.0") == -1

    def test_compare_versions_minor_difference(self):
        """Test minor version differences."""
        assert versioner.compare_versions("1.2.0", "1.1.9") == 1
        assert versioner.compare_versions("1.1.0", "1.2.0") == -1

    def test_compare_versions_patch_difference(self):
        """Test patch version differences."""
        assert versioner.compare_versions("1.2.3", "1.2.2") == 1
        assert versioner.compare_versions("1.2.2", "1.2.3") == -1

    def test_compare_versions_with_v_prefix(self):
        """Test comparing versions with v prefix."""
        assert versioner.compare_versions("v1.2.3", "v1.2.3") == 0
        assert versioner.compare_versions("v1.2.3", "1.2.4") == -1

    def test_compare_versions_invalid_first(self):
        """Test comparing with invalid first version."""
        with pytest.raises(ValueError):
            versioner.compare_versions("invalid", "1.2.3")

    def test_compare_versions_invalid_second(self):
        """Test comparing with invalid second version."""
        with pytest.raises(ValueError):
            versioner.compare_versions("1.2.3", "invalid")
