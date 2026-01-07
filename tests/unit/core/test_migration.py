"""Comprehensive tests for claude_ctx_py/core/migration.py

Tests cover:
- migrate_to_file_activation() orchestration
- _migrate_category() for both rules and modes
- Test scenarios:
  - Items already in active directory (no action needed)
  - Items in inactive directory (should be moved)
  - Items missing from both directories (reported as missing)
  - Mixed scenarios with some active, some inactive, some missing
- .active-{category} file creation
- CLAUDE.md refresh after migration
- Error handling for various edge cases
"""

from pathlib import Path
from unittest.mock import MagicMock, patch, call

import pytest

from claude_ctx_py.core.migration import (
    migrate_to_file_activation,
    _migrate_category,
)


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def mock_claude_dir(tmp_path):
    """Create a mock .cortex directory structure."""
    claude_dir = tmp_path / ".cortex"
    claude_dir.mkdir(parents=True)
    return claude_dir


@pytest.fixture
def claude_dir_with_rules(mock_claude_dir):
    """Create a .cortex directory with rules structure."""
    rules_dir = mock_claude_dir / "rules"
    rules_dir.mkdir(parents=True)

    inactive_rules = mock_claude_dir / "inactive" / "rules"
    inactive_rules.mkdir(parents=True)

    return mock_claude_dir


@pytest.fixture
def claude_dir_with_modes(mock_claude_dir):
    """Create a .cortex directory with modes structure."""
    modes_dir = mock_claude_dir / "modes"
    modes_dir.mkdir(parents=True)

    inactive_modes = mock_claude_dir / "inactive" / "modes"
    inactive_modes.mkdir(parents=True)

    return mock_claude_dir


@pytest.fixture
def full_claude_dir(mock_claude_dir):
    """Create a full .cortex directory with rules, modes, and inactive dirs."""
    for category in ["rules", "modes"]:
        (mock_claude_dir / category).mkdir(parents=True, exist_ok=True)
        (mock_claude_dir / "inactive" / category).mkdir(parents=True, exist_ok=True)
    return mock_claude_dir


# =============================================================================
# Tests for _migrate_category()
# =============================================================================


class TestMigrateCategory:
    """Tests for _migrate_category function."""

    def test_no_refs_found(self, mock_claude_dir):
        """Test when no references are found in CLAUDE.md."""
        with patch("claude_ctx_py.core.migration._parse_claude_md_refs", return_value=set()):
            with patch("claude_ctx_py.core.migration._color", side_effect=lambda x, y: x):
                code, msg = _migrate_category(mock_claude_dir, "rules")

        assert code == 0
        assert "No rules references found" in msg

    def test_items_already_active(self, full_claude_dir):
        """Test when items are already in active directory."""
        # Create active rules
        active_rule = full_claude_dir / "rules" / "my-rule.md"
        active_rule.write_text("# My Rule")

        with patch("claude_ctx_py.core.migration._parse_claude_md_refs", return_value={"rules/my-rule"}):
            with patch("claude_ctx_py.core.migration._inactive_category_dir", return_value=full_claude_dir / "inactive" / "rules"):
                with patch("claude_ctx_py.core.migration._write_active_entries") as mock_write:
                    with patch("claude_ctx_py.core.migration._color", side_effect=lambda x, y: x):
                        code, msg = _migrate_category(full_claude_dir, "rules")

        assert code == 0
        assert "Activated 1 rules" in msg
        mock_write.assert_called_once()

    def test_items_moved_from_inactive(self, full_claude_dir):
        """Test when items are in inactive directory and need to be moved."""
        # Create inactive rule
        inactive_rule = full_claude_dir / "inactive" / "rules" / "inactive-rule.md"
        inactive_rule.write_text("# Inactive Rule")

        with patch("claude_ctx_py.core.migration._parse_claude_md_refs", return_value={"rules/inactive-rule"}):
            with patch("claude_ctx_py.core.migration._inactive_category_dir", return_value=full_claude_dir / "inactive" / "rules"):
                with patch("claude_ctx_py.core.migration._write_active_entries") as mock_write:
                    with patch("claude_ctx_py.core.migration._color", side_effect=lambda x, y: x):
                        code, msg = _migrate_category(full_claude_dir, "rules")

        # Should have moved file
        assert not inactive_rule.exists()
        active_rule = full_claude_dir / "rules" / "inactive-rule.md"
        assert active_rule.exists()

        assert code == 0
        assert "Activated 1 rules" in msg

    def test_items_missing(self, full_claude_dir):
        """Test when items are missing from both directories."""
        with patch("claude_ctx_py.core.migration._parse_claude_md_refs", return_value={"rules/missing-rule"}):
            with patch("claude_ctx_py.core.migration._inactive_category_dir", return_value=full_claude_dir / "inactive" / "rules"):
                with patch("claude_ctx_py.core.migration._write_active_entries"):
                    with patch("claude_ctx_py.core.migration._color", side_effect=lambda x, y: x):
                        code, msg = _migrate_category(full_claude_dir, "rules")

        assert code == 1  # Returns 1 when there are missing items
        assert "Missing rules" in msg
        assert "missing-rule.md" in msg

    def test_mixed_scenario(self, full_claude_dir):
        """Test with mix of active, inactive, and missing items."""
        # Create active rule
        (full_claude_dir / "rules" / "active-rule.md").write_text("# Active")
        # Create inactive rule
        (full_claude_dir / "inactive" / "rules" / "inactive-rule.md").write_text("# Inactive")

        refs = {"rules/active-rule", "rules/inactive-rule", "rules/missing-rule"}

        with patch("claude_ctx_py.core.migration._parse_claude_md_refs", return_value=refs):
            with patch("claude_ctx_py.core.migration._inactive_category_dir", return_value=full_claude_dir / "inactive" / "rules"):
                with patch("claude_ctx_py.core.migration._write_active_entries") as mock_write:
                    with patch("claude_ctx_py.core.migration._color", side_effect=lambda x, y: x):
                        code, msg = _migrate_category(full_claude_dir, "rules")

        # Should report both activated and missing
        assert code == 1  # Missing items cause code 1
        assert "Activated 2 rules" in msg
        assert "Missing rules" in msg

    def test_creates_active_entries_file(self, full_claude_dir):
        """Test that .active-{category} file is created."""
        (full_claude_dir / "rules" / "test-rule.md").write_text("# Test")

        with patch("claude_ctx_py.core.migration._parse_claude_md_refs", return_value={"rules/test-rule"}):
            with patch("claude_ctx_py.core.migration._inactive_category_dir", return_value=full_claude_dir / "inactive" / "rules"):
                with patch("claude_ctx_py.core.migration._write_active_entries") as mock_write:
                    with patch("claude_ctx_py.core.migration._color", side_effect=lambda x, y: x):
                        _migrate_category(full_claude_dir, "rules")

        # Verify _write_active_entries was called with correct path
        mock_write.assert_called_once()
        call_args = mock_write.call_args
        assert ".active-rules" in str(call_args[0][0])

    def test_handles_md_extension_correctly(self, full_claude_dir):
        """Test handling of .md extension in slug names."""
        # Rule already has .md in slug
        (full_claude_dir / "rules" / "my-rule.md").write_text("# Rule")

        with patch("claude_ctx_py.core.migration._parse_claude_md_refs", return_value={"rules/my-rule.md"}):
            with patch("claude_ctx_py.core.migration._inactive_category_dir", return_value=full_claude_dir / "inactive" / "rules"):
                with patch("claude_ctx_py.core.migration._write_active_entries"):
                    with patch("claude_ctx_py.core.migration._color", side_effect=lambda x, y: x):
                        code, msg = _migrate_category(full_claude_dir, "rules")

        assert code == 0

    def test_modes_category(self, full_claude_dir):
        """Test migration of modes category."""
        (full_claude_dir / "modes" / "architect.md").write_text("# Architect Mode")

        with patch("claude_ctx_py.core.migration._parse_claude_md_refs", return_value={"modes/architect"}):
            with patch("claude_ctx_py.core.migration._inactive_category_dir", return_value=full_claude_dir / "inactive" / "modes"):
                with patch("claude_ctx_py.core.migration._write_active_entries") as mock_write:
                    with patch("claude_ctx_py.core.migration._color", side_effect=lambda x, y: x):
                        code, msg = _migrate_category(full_claude_dir, "modes")

        assert code == 0
        assert "Activated 1 modes" in msg

    def test_multiple_refs_sorted(self, full_claude_dir):
        """Test that refs are processed in sorted order."""
        for name in ["z-rule", "a-rule", "m-rule"]:
            (full_claude_dir / "rules" / f"{name}.md").write_text(f"# {name}")

        refs = {"rules/z-rule", "rules/a-rule", "rules/m-rule"}

        with patch("claude_ctx_py.core.migration._parse_claude_md_refs", return_value=refs):
            with patch("claude_ctx_py.core.migration._inactive_category_dir", return_value=full_claude_dir / "inactive" / "rules"):
                with patch("claude_ctx_py.core.migration._write_active_entries") as mock_write:
                    with patch("claude_ctx_py.core.migration._color", side_effect=lambda x, y: x):
                        _migrate_category(full_claude_dir, "rules")

        # Check that activated list is sorted
        call_args = mock_write.call_args[0][1]
        assert call_args == sorted(call_args)

    def test_no_changes_message(self, full_claude_dir):
        """Test message when all items are missing (edge case)."""
        # Empty refs that won't match anything
        with patch("claude_ctx_py.core.migration._parse_claude_md_refs", return_value=set()):
            with patch("claude_ctx_py.core.migration._color", side_effect=lambda x, y: x):
                code, msg = _migrate_category(full_claude_dir, "rules")

        assert "No rules references found" in msg


# =============================================================================
# Tests for migrate_to_file_activation()
# =============================================================================


class TestMigrateToFileActivation:
    """Tests for migrate_to_file_activation function."""

    def test_calls_migrate_for_both_categories(self, tmp_path):
        """Test that migrate is called for both rules and modes."""
        mock_claude_dir = tmp_path / ".cortex"
        mock_claude_dir.mkdir()

        with patch("claude_ctx_py.core.migration._resolve_claude_dir", return_value=mock_claude_dir):
            with patch("claude_ctx_py.core.migration._migrate_category") as mock_migrate:
                mock_migrate.return_value = (0, "Success")
                with patch("claude_ctx_py.core.migration._refresh_claude_md"):
                    code, msg = migrate_to_file_activation(tmp_path)

        # Should be called for rules and modes
        assert mock_migrate.call_count == 2
        calls = mock_migrate.call_args_list
        categories_called = [c[0][1] for c in calls]
        assert "rules" in categories_called
        assert "modes" in categories_called

    def test_refreshes_claude_md(self, tmp_path):
        """Test that CLAUDE.md is refreshed after migration."""
        mock_claude_dir = tmp_path / ".cortex"
        mock_claude_dir.mkdir()

        with patch("claude_ctx_py.core.migration._resolve_claude_dir", return_value=mock_claude_dir):
            with patch("claude_ctx_py.core.migration._migrate_category", return_value=(0, "Success")):
                with patch("claude_ctx_py.core.migration._refresh_claude_md") as mock_refresh:
                    migrate_to_file_activation(tmp_path)

        mock_refresh.assert_called_once_with(mock_claude_dir)

    def test_returns_0_when_all_succeed(self, tmp_path):
        """Test overall code is 0 when all migrations succeed."""
        mock_claude_dir = tmp_path / ".cortex"
        mock_claude_dir.mkdir()

        with patch("claude_ctx_py.core.migration._resolve_claude_dir", return_value=mock_claude_dir):
            with patch("claude_ctx_py.core.migration._migrate_category", return_value=(0, "Success")):
                with patch("claude_ctx_py.core.migration._refresh_claude_md"):
                    code, msg = migrate_to_file_activation(tmp_path)

        assert code == 0

    def test_returns_1_when_any_fails(self, tmp_path):
        """Test overall code is 1 when any migration has issues."""
        mock_claude_dir = tmp_path / ".cortex"
        mock_claude_dir.mkdir()

        def side_effect(claude_dir, category):
            if category == "rules":
                return (0, "Rules OK")
            else:
                return (1, "Modes have missing items")

        with patch("claude_ctx_py.core.migration._resolve_claude_dir", return_value=mock_claude_dir):
            with patch("claude_ctx_py.core.migration._migrate_category", side_effect=side_effect):
                with patch("claude_ctx_py.core.migration._refresh_claude_md"):
                    code, msg = migrate_to_file_activation(tmp_path)

        assert code == 1

    def test_combines_messages(self, tmp_path):
        """Test that messages from both categories are combined."""
        mock_claude_dir = tmp_path / ".cortex"
        mock_claude_dir.mkdir()

        def side_effect(claude_dir, category):
            return (0, f"{category} migrated")

        with patch("claude_ctx_py.core.migration._resolve_claude_dir", return_value=mock_claude_dir):
            with patch("claude_ctx_py.core.migration._migrate_category", side_effect=side_effect):
                with patch("claude_ctx_py.core.migration._refresh_claude_md"):
                    code, msg = migrate_to_file_activation(tmp_path)

        assert "rules migrated" in msg
        assert "modes migrated" in msg
        assert " | " in msg

    def test_uses_home_parameter(self, tmp_path):
        """Test that home parameter is passed to _resolve_claude_dir."""
        with patch("claude_ctx_py.core.migration._resolve_claude_dir") as mock_resolve:
            mock_resolve.return_value = tmp_path / ".cortex"
            (tmp_path / ".cortex").mkdir()

            with patch("claude_ctx_py.core.migration._migrate_category", return_value=(0, "OK")):
                with patch("claude_ctx_py.core.migration._refresh_claude_md"):
                    migrate_to_file_activation(tmp_path)

        mock_resolve.assert_called_once_with(tmp_path)

    def test_uses_none_home_parameter(self):
        """Test that None home parameter uses default."""
        with patch("claude_ctx_py.core.migration._resolve_claude_dir") as mock_resolve:
            mock_resolve.return_value = Path.home() / ".cortex"

            with patch("claude_ctx_py.core.migration._migrate_category", return_value=(0, "OK")):
                with patch("claude_ctx_py.core.migration._refresh_claude_md"):
                    migrate_to_file_activation(None)

        mock_resolve.assert_called_once_with(None)


# =============================================================================
# Integration-style tests
# =============================================================================


class TestMigrationIntegration:
    """Integration-style tests for migration workflow."""

    def test_full_migration_workflow(self, full_claude_dir):
        """Test complete migration workflow with real file operations."""
        # Setup: Create some rules and modes
        (full_claude_dir / "rules" / "active-rule.md").write_text("# Active Rule")
        (full_claude_dir / "inactive" / "rules" / "inactive-rule.md").write_text("# Inactive Rule")
        (full_claude_dir / "modes" / "active-mode.md").write_text("# Active Mode")

        rules_refs = {"rules/active-rule", "rules/inactive-rule", "rules/missing-rule"}
        modes_refs = {"modes/active-mode"}

        def parse_refs(claude_dir, category):
            return rules_refs if category == "rules" else modes_refs

        with patch("claude_ctx_py.core.migration._resolve_claude_dir", return_value=full_claude_dir):
            with patch("claude_ctx_py.core.migration._parse_claude_md_refs", side_effect=parse_refs):
                with patch("claude_ctx_py.core.migration._inactive_category_dir",
                          side_effect=lambda d, c: d / "inactive" / c):
                    with patch("claude_ctx_py.core.migration._write_active_entries"):
                        with patch("claude_ctx_py.core.migration._refresh_claude_md"):
                            with patch("claude_ctx_py.core.migration._color", side_effect=lambda x, y: x):
                                code, msg = migrate_to_file_activation()

        # Verify inactive rule was moved
        assert not (full_claude_dir / "inactive" / "rules" / "inactive-rule.md").exists()
        assert (full_claude_dir / "rules" / "inactive-rule.md").exists()

        # Should have code 1 due to missing rule
        assert code == 1

    def test_empty_migration(self, full_claude_dir):
        """Test migration when there's nothing to migrate."""
        with patch("claude_ctx_py.core.migration._resolve_claude_dir", return_value=full_claude_dir):
            with patch("claude_ctx_py.core.migration._parse_claude_md_refs", return_value=set()):
                with patch("claude_ctx_py.core.migration._refresh_claude_md"):
                    with patch("claude_ctx_py.core.migration._color", side_effect=lambda x, y: x):
                        code, msg = migrate_to_file_activation()

        assert code == 0
        assert "No rules references found" in msg


# =============================================================================
# Edge cases tests
# =============================================================================


class TestMigrationEdgeCases:
    """Tests for edge cases in migration."""

    def test_slug_with_nested_path(self, full_claude_dir):
        """Test handling of slugs with nested paths."""
        # Create nested rule
        nested_dir = full_claude_dir / "rules" / "subdir"
        nested_dir.mkdir(parents=True)
        # The implementation extracts only the last part of the slug
        (full_claude_dir / "rules" / "nested-rule.md").write_text("# Nested")

        with patch("claude_ctx_py.core.migration._parse_claude_md_refs", return_value={"rules/subdir/nested-rule"}):
            with patch("claude_ctx_py.core.migration._inactive_category_dir", return_value=full_claude_dir / "inactive" / "rules"):
                with patch("claude_ctx_py.core.migration._write_active_entries"):
                    with patch("claude_ctx_py.core.migration._color", side_effect=lambda x, y: x):
                        code, msg = _migrate_category(full_claude_dir, "rules")

        # Should process the nested path (extracts last part)
        assert "nested-rule" in msg or "Missing" in msg

    def test_special_characters_in_name(self, full_claude_dir):
        """Test handling of special characters in rule names."""
        (full_claude_dir / "rules" / "my_rule-v2.0.md").write_text("# Rule v2.0")

        with patch("claude_ctx_py.core.migration._parse_claude_md_refs", return_value={"rules/my_rule-v2.0"}):
            with patch("claude_ctx_py.core.migration._inactive_category_dir", return_value=full_claude_dir / "inactive" / "rules"):
                with patch("claude_ctx_py.core.migration._write_active_entries"):
                    with patch("claude_ctx_py.core.migration._color", side_effect=lambda x, y: x):
                        code, msg = _migrate_category(full_claude_dir, "rules")

        assert code == 0

    def test_directory_creation(self, mock_claude_dir):
        """Test that directories are created if they don't exist."""
        # Start with no rules/inactive directories
        with patch("claude_ctx_py.core.migration._parse_claude_md_refs", return_value={"rules/test"}):
            with patch("claude_ctx_py.core.migration._inactive_category_dir", return_value=mock_claude_dir / "inactive" / "rules"):
                with patch("claude_ctx_py.core.migration._write_active_entries"):
                    with patch("claude_ctx_py.core.migration._color", side_effect=lambda x, y: x):
                        _migrate_category(mock_claude_dir, "rules")

        # Directories should be created
        assert (mock_claude_dir / "rules").exists()
        assert (mock_claude_dir / "inactive" / "rules").exists()

    def test_color_function_integration(self, full_claude_dir):
        """Test that _color function is called with correct parameters."""
        (full_claude_dir / "rules" / "test.md").write_text("# Test")

        with patch("claude_ctx_py.core.migration._parse_claude_md_refs", return_value={"rules/test"}):
            with patch("claude_ctx_py.core.migration._inactive_category_dir", return_value=full_claude_dir / "inactive" / "rules"):
                with patch("claude_ctx_py.core.migration._write_active_entries"):
                    with patch("claude_ctx_py.core.migration._color") as mock_color:
                        mock_color.side_effect = lambda x, y: x
                        _migrate_category(full_claude_dir, "rules")

        # Color should be called for success messages
        mock_color.assert_called()

    def test_empty_active_list_no_write(self, full_claude_dir):
        """Test that _write_active_entries is not called when no items activated."""
        # All items missing - nothing to activate
        with patch("claude_ctx_py.core.migration._parse_claude_md_refs", return_value={"rules/missing"}):
            with patch("claude_ctx_py.core.migration._inactive_category_dir", return_value=full_claude_dir / "inactive" / "rules"):
                with patch("claude_ctx_py.core.migration._write_active_entries") as mock_write:
                    with patch("claude_ctx_py.core.migration._color", side_effect=lambda x, y: x):
                        _migrate_category(full_claude_dir, "rules")

        # Should not call write when nothing was activated
        mock_write.assert_not_called()
