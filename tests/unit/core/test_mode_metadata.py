"""Tests for mode metadata parsing and conflict detection.

This module tests the mode_metadata.py module which handles mode
metadata parsing, conflict detection, and dependency management.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from claude_ctx_py.core.mode_metadata import (
    ModeMetadata,
    check_mode_dependencies,
    format_metadata_summary,
    get_mode_conflicts,
    get_priority_action,
    parse_mode_metadata,
    parse_yaml_frontmatter,
)


class TestModeMetadata:
    """Tests for ModeMetadata dataclass."""

    def test_default_values(self):
        """ModeMetadata has sensible defaults."""
        meta = ModeMetadata(name="test")
        assert meta.name == "test"
        assert meta.category == "general"
        assert meta.priority == "medium"
        assert meta.conflicts == []
        assert meta.dependencies == []
        assert meta.overrides == {}
        assert meta.group is None
        assert meta.tags == []
        assert meta.auto_activate_triggers == []

    def test_priority_value_low(self):
        """Low priority returns 1."""
        meta = ModeMetadata(name="test", priority="low")
        assert meta.priority_value == 1

    def test_priority_value_medium(self):
        """Medium priority returns 2."""
        meta = ModeMetadata(name="test", priority="medium")
        assert meta.priority_value == 2

    def test_priority_value_high(self):
        """High priority returns 3."""
        meta = ModeMetadata(name="test", priority="high")
        assert meta.priority_value == 3

    def test_priority_value_case_insensitive(self):
        """Priority is case-insensitive."""
        meta = ModeMetadata(name="test", priority="HIGH")
        assert meta.priority_value == 3

    def test_priority_value_unknown_defaults_to_medium(self):
        """Unknown priority defaults to medium (2)."""
        meta = ModeMetadata(name="test", priority="unknown")
        assert meta.priority_value == 2

    def test_with_all_fields(self):
        """ModeMetadata accepts all fields."""
        meta = ModeMetadata(
            name="architect",
            category="design",
            priority="high",
            conflicts=["speed", "minimal"],
            dependencies=["base-rules"],
            overrides={"thinking_budget": 32000},
            group="design_modes",
            tags=["architecture", "planning"],
            auto_activate_triggers=["design", "architecture"],
        )
        assert meta.name == "architect"
        assert meta.category == "design"
        assert meta.priority == "high"
        assert "speed" in meta.conflicts
        assert "base-rules" in meta.dependencies
        assert meta.overrides["thinking_budget"] == 32000
        assert meta.group == "design_modes"
        assert "architecture" in meta.tags
        assert "design" in meta.auto_activate_triggers


class TestParseYamlFrontmatter:
    """Tests for parse_yaml_frontmatter function."""

    def test_no_frontmatter(self):
        """Content without frontmatter returns None metadata."""
        content = "# Title\n\nSome content"
        metadata, remaining = parse_yaml_frontmatter(content)
        assert metadata is None
        assert remaining == content

    def test_valid_frontmatter(self):
        """Valid frontmatter is parsed correctly."""
        content = """---
name: test-mode
category: general
---

# Mode Content
"""
        metadata, remaining = parse_yaml_frontmatter(content)
        assert metadata is not None
        assert metadata["name"] == "test-mode"
        assert metadata["category"] == "general"
        assert "# Mode Content" in remaining

    def test_frontmatter_with_lists(self):
        """Frontmatter with lists is parsed correctly."""
        content = """---
name: test-mode
conflicts:
  - mode-a
  - mode-b
tags: [tag1, tag2]
---

Content
"""
        metadata, remaining = parse_yaml_frontmatter(content)
        assert metadata is not None
        assert metadata["conflicts"] == ["mode-a", "mode-b"]
        assert metadata["tags"] == ["tag1", "tag2"]

    def test_frontmatter_with_nested_dict(self):
        """Frontmatter with nested dict is parsed correctly."""
        content = """---
name: test-mode
overrides:
  thinking_budget: 32000
  auto_escalate: true
---

Content
"""
        metadata, remaining = parse_yaml_frontmatter(content)
        assert metadata is not None
        assert metadata["overrides"]["thinking_budget"] == 32000
        assert metadata["overrides"]["auto_escalate"] is True

    def test_unclosed_frontmatter(self):
        """Unclosed frontmatter returns None metadata."""
        content = """---
name: test-mode
category: general

# No closing ---
"""
        metadata, remaining = parse_yaml_frontmatter(content)
        assert metadata is None
        assert remaining == content

    def test_invalid_yaml(self):
        """Invalid YAML returns None metadata."""
        content = """---
name: [invalid: yaml
---

Content
"""
        metadata, remaining = parse_yaml_frontmatter(content)
        assert metadata is None
        assert remaining == content

    def test_non_dict_yaml(self):
        """Non-dict YAML returns None metadata."""
        content = """---
- item1
- item2
---

Content
"""
        metadata, remaining = parse_yaml_frontmatter(content)
        assert metadata is None

    def test_short_content(self):
        """Content with fewer than 3 lines returns None."""
        content = "---\n"
        metadata, remaining = parse_yaml_frontmatter(content)
        assert metadata is None

    def test_whitespace_before_frontmatter(self):
        """Content with leading whitespace is stripped and parsed."""
        content = "  ---\nname: test\n---\n"
        metadata, remaining = parse_yaml_frontmatter(content)
        # Implementation uses content.strip().startswith("---")
        # so leading whitespace IS accepted
        assert metadata is not None
        assert metadata["name"] == "test"


class TestParseModeMetadata:
    """Tests for parse_mode_metadata function."""

    def test_nonexistent_file(self, tmp_path):
        """Non-existent file returns None."""
        result = parse_mode_metadata(tmp_path / "nonexistent.md")
        assert result is None

    def test_file_without_frontmatter(self, tmp_path):
        """File without frontmatter returns default metadata."""
        mode_file = tmp_path / "test-mode.md"
        mode_file.write_text("# Test Mode\n\nSome content")
        result = parse_mode_metadata(mode_file)
        assert result is not None
        assert result.name == "test-mode"  # From stem
        assert result.category == "general"  # Default

    def test_file_with_frontmatter(self, tmp_path):
        """File with frontmatter returns parsed metadata."""
        mode_file = tmp_path / "architect.md"
        mode_file.write_text("""---
name: Architect
category: design
priority: high
conflicts:
  - speed-mode
group: design_modes
---

# Architect Mode
""")
        result = parse_mode_metadata(mode_file)
        assert result is not None
        assert result.name == "Architect"
        assert result.category == "design"
        assert result.priority == "high"
        assert "speed-mode" in result.conflicts
        assert result.group == "design_modes"

    def test_file_with_partial_frontmatter(self, tmp_path):
        """File with partial frontmatter uses defaults for missing fields."""
        mode_file = tmp_path / "partial.md"
        mode_file.write_text("""---
name: Partial
---

Content
""")
        result = parse_mode_metadata(mode_file)
        assert result is not None
        assert result.name == "Partial"
        assert result.category == "general"  # Default
        assert result.priority == "medium"  # Default
        assert result.conflicts == []  # Default

    def test_directory_returns_none(self, tmp_path):
        """Directory path returns None."""
        result = parse_mode_metadata(tmp_path)
        assert result is None


class TestGetModeConflicts:
    """Tests for get_mode_conflicts function."""

    def test_no_conflicts(self):
        """No conflicts when none declared."""
        new_mode = ModeMetadata(name="new-mode")
        active_modes = [ModeMetadata(name="other-mode")]
        conflicts = get_mode_conflicts(new_mode, active_modes)
        assert len(conflicts) == 0

    def test_direct_conflict(self):
        """Detects direct conflict declaration."""
        new_mode = ModeMetadata(name="new-mode", conflicts=["conflicting-mode"])
        active_modes = [
            ModeMetadata(name="conflicting-mode"),
            ModeMetadata(name="other-mode"),
        ]
        conflicts = get_mode_conflicts(new_mode, active_modes)
        assert len(conflicts) == 1
        assert conflicts[0].name == "conflicting-mode"

    def test_group_conflict(self):
        """Detects group-based conflict."""
        new_mode = ModeMetadata(name="new-mode", group="visual_style")
        active_modes = [
            ModeMetadata(name="other-visual", group="visual_style"),
            ModeMetadata(name="unrelated", group="other_group"),
        ]
        conflicts = get_mode_conflicts(new_mode, active_modes)
        assert len(conflicts) == 1
        assert conflicts[0].name == "other-visual"

    def test_no_self_conflict(self):
        """Mode doesn't conflict with itself in group."""
        mode = ModeMetadata(name="test-mode", group="test_group")
        # Same mode in active list (shouldn't conflict with itself)
        active_modes = [mode]
        conflicts = get_mode_conflicts(mode, active_modes)
        assert len(conflicts) == 0

    def test_multiple_conflicts(self):
        """Detects multiple conflicts."""
        new_mode = ModeMetadata(
            name="new-mode", conflicts=["conflict1", "conflict2"], group="shared_group"
        )
        active_modes = [
            ModeMetadata(name="conflict1"),
            ModeMetadata(name="conflict2"),
            ModeMetadata(name="group-member", group="shared_group"),
        ]
        conflicts = get_mode_conflicts(new_mode, active_modes)
        assert len(conflicts) == 3

    def test_no_group_conflict_if_no_group(self):
        """No group conflict if new mode has no group."""
        new_mode = ModeMetadata(name="new-mode")  # No group
        active_modes = [ModeMetadata(name="grouped", group="some_group")]
        conflicts = get_mode_conflicts(new_mode, active_modes)
        assert len(conflicts) == 0


class TestCheckModeDependencies:
    """Tests for check_mode_dependencies function."""

    def test_no_dependencies(self):
        """No dependencies returns satisfied."""
        mode = ModeMetadata(name="test")
        satisfied, missing = check_mode_dependencies(mode, [], [])
        assert satisfied is True
        assert len(missing) == 0

    def test_mode_dependency_satisfied(self):
        """Mode dependency satisfied when active."""
        mode = ModeMetadata(name="test", dependencies=["base-mode"])
        satisfied, missing = check_mode_dependencies(mode, ["base-mode"], [])
        assert satisfied is True
        assert len(missing) == 0

    def test_mode_dependency_missing(self):
        """Mode dependency missing when not active."""
        mode = ModeMetadata(name="test", dependencies=["base-mode"])
        satisfied, missing = check_mode_dependencies(mode, [], [])
        assert satisfied is False
        assert "mode:base-mode" in missing

    def test_rule_dependency_suffix(self):
        """Rule dependency detected by -rules suffix."""
        mode = ModeMetadata(name="test", dependencies=["quality-rules"])
        # Implementation keeps full name "quality-rules" after replace operations
        satisfied, missing = check_mode_dependencies(mode, [], ["quality-rules"])
        assert satisfied is True

    def test_rule_dependency_prefix(self):
        """Rule dependency detected by rule: prefix."""
        mode = ModeMetadata(name="test", dependencies=["rule:quality"])
        satisfied, missing = check_mode_dependencies(mode, [], ["quality"])
        assert satisfied is True

    def test_rule_dependency_md_suffix(self):
        """Rule dependency detected by .md suffix."""
        mode = ModeMetadata(name="test", dependencies=["quality.md"])
        satisfied, missing = check_mode_dependencies(mode, [], ["quality"])
        assert satisfied is True

    def test_rule_dependency_missing(self):
        """Rule dependency missing when not active."""
        mode = ModeMetadata(name="test", dependencies=["quality-rules"])
        satisfied, missing = check_mode_dependencies(mode, [], [])
        assert satisfied is False
        assert "rule:quality-rules" in missing

    def test_mixed_dependencies(self):
        """Mixed mode and rule dependencies."""
        mode = ModeMetadata(name="test", dependencies=["base-mode", "quality-rules"])
        satisfied, missing = check_mode_dependencies(
            mode, ["base-mode"], ["quality-rules"]
        )
        assert satisfied is True

    def test_multiple_missing(self):
        """Multiple missing dependencies reported."""
        mode = ModeMetadata(
            name="test", dependencies=["mode1", "mode2", "rule:rule1"]
        )
        satisfied, missing = check_mode_dependencies(mode, [], [])
        assert satisfied is False
        assert len(missing) == 3


class TestGetPriorityAction:
    """Tests for get_priority_action function."""

    def test_higher_priority_auto_deactivates(self):
        """Higher priority mode auto-deactivates conflicting mode."""
        new_mode = ModeMetadata(name="high", priority="high")
        conflicting = ModeMetadata(name="low", priority="low")
        action = get_priority_action(new_mode, conflicting)
        assert action == "auto_deactivate"

    def test_equal_priority_prompts(self):
        """Equal priority modes prompt for decision."""
        new_mode = ModeMetadata(name="new", priority="medium")
        conflicting = ModeMetadata(name="existing", priority="medium")
        action = get_priority_action(new_mode, conflicting)
        assert action == "prompt"

    def test_lower_priority_prompts(self):
        """Lower priority mode prompts for decision."""
        new_mode = ModeMetadata(name="low", priority="low")
        conflicting = ModeMetadata(name="high", priority="high")
        action = get_priority_action(new_mode, conflicting)
        assert action == "prompt"

    def test_medium_vs_low(self):
        """Medium priority auto-deactivates low priority."""
        new_mode = ModeMetadata(name="medium", priority="medium")
        conflicting = ModeMetadata(name="low", priority="low")
        action = get_priority_action(new_mode, conflicting)
        assert action == "auto_deactivate"


class TestFormatMetadataSummary:
    """Tests for format_metadata_summary function."""

    def test_basic_summary(self):
        """Basic summary includes category and priority."""
        meta = ModeMetadata(name="test")
        summary = format_metadata_summary(meta)
        assert "Category: general" in summary
        assert "Priority: medium" in summary

    def test_summary_with_group(self):
        """Summary includes group when present."""
        meta = ModeMetadata(name="test", group="visual_style")
        summary = format_metadata_summary(meta)
        assert "Group: visual_style" in summary

    def test_summary_with_conflicts(self):
        """Summary includes conflicts when present."""
        meta = ModeMetadata(name="test", conflicts=["mode-a", "mode-b"])
        summary = format_metadata_summary(meta)
        assert "Conflicts: mode-a, mode-b" in summary

    def test_summary_with_dependencies(self):
        """Summary includes dependencies when present."""
        meta = ModeMetadata(name="test", dependencies=["base-mode", "base-rules"])
        summary = format_metadata_summary(meta)
        assert "Dependencies: base-mode, base-rules" in summary

    def test_summary_with_overrides(self):
        """Summary includes overrides when present."""
        meta = ModeMetadata(name="test", overrides={"budget": 1000, "auto": True})
        summary = format_metadata_summary(meta)
        assert "Overrides:" in summary
        assert "budget=1000" in summary

    def test_summary_with_tags(self):
        """Summary includes tags when present."""
        meta = ModeMetadata(name="test", tags=["design", "planning"])
        summary = format_metadata_summary(meta)
        assert "Tags: design, planning" in summary

    def test_summary_omits_empty_fields(self):
        """Summary omits empty/None fields."""
        meta = ModeMetadata(name="test")
        summary = format_metadata_summary(meta)
        assert "Group:" not in summary
        assert "Conflicts:" not in summary
        assert "Dependencies:" not in summary
        assert "Overrides:" not in summary
        assert "Tags:" not in summary
