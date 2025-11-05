"""Tests for skill composition and dependency resolution."""

import pytest
from pathlib import Path

from claude_ctx_py import composer


class TestLoadCompositionMap:
    """Tests for load_composition_map function."""

    def test_load_composition_map_success(self, temp_claude_dir, mock_yaml_file):
        """Test loading a valid composition map."""
        yaml_content = """skill-a:
  - dependency-1
  - dependency-2

skill-b:
  - skill-a
"""
        mock_yaml_file(yaml_content)

        result = composer.load_composition_map(temp_claude_dir)

        assert result == {
            "skill-a": ["dependency-1", "dependency-2"],
            "skill-b": ["skill-a"],
        }

    def test_load_composition_map_file_not_exists(self, temp_claude_dir):
        """Test loading when composition.yaml doesn't exist."""
        result = composer.load_composition_map(temp_claude_dir)

        assert result == {}

    def test_load_composition_map_empty_file(self, temp_claude_dir, mock_yaml_file):
        """Test loading an empty composition file."""
        mock_yaml_file("")

        result = composer.load_composition_map(temp_claude_dir)

        assert result == {}

    def test_load_composition_map_null_dependencies(self, temp_claude_dir, mock_yaml_file):
        """Test loading skills with null/empty dependencies."""
        yaml_content = """skill-a: null
skill-b: []
skill-c:
  - dependency-1
"""
        mock_yaml_file(yaml_content)

        result = composer.load_composition_map(temp_claude_dir)

        assert result == {
            "skill-a": [],
            "skill-b": [],
            "skill-c": ["dependency-1"],
        }

    def test_load_composition_map_invalid_yaml(self, temp_claude_dir, mock_yaml_file):
        """Test loading invalid YAML raises ValueError."""
        mock_yaml_file("invalid: yaml: content: [")

        with pytest.raises(ValueError, match="Invalid YAML"):
            composer.load_composition_map(temp_claude_dir)

    def test_load_composition_map_not_dict(self, temp_claude_dir, mock_yaml_file):
        """Test loading YAML that's not a dictionary."""
        mock_yaml_file("- item1\n- item2\n")

        with pytest.raises(ValueError, match="Expected dictionary"):
            composer.load_composition_map(temp_claude_dir)

    def test_load_composition_map_invalid_dependency_type(self, temp_claude_dir, mock_yaml_file):
        """Test loading with invalid dependency type raises ValueError."""
        yaml_content = """skill-a: "not-a-list"
"""
        mock_yaml_file(yaml_content)

        with pytest.raises(ValueError, match="Dependencies for 'skill-a' must be a list"):
            composer.load_composition_map(temp_claude_dir)

    def test_load_composition_map_skips_non_string_keys(self, temp_claude_dir, mock_yaml_file):
        """Test that non-string keys are skipped gracefully."""
        yaml_content = """skill-a:
  - dep-1

123: []

skill-b:
  - dep-2
"""
        mock_yaml_file(yaml_content)

        result = composer.load_composition_map(temp_claude_dir)

        assert "skill-a" in result
        assert "skill-b" in result
        assert 123 not in result

    def test_load_composition_map_filters_non_string_deps(self, temp_claude_dir, mock_yaml_file):
        """Test that non-string dependencies are filtered out."""
        yaml_content = """skill-a:
  - valid-dep
  - 123
  - another-valid
"""
        mock_yaml_file(yaml_content)

        result = composer.load_composition_map(temp_claude_dir)

        assert result["skill-a"] == ["valid-dep", "another-valid"]


class TestValidateNoCycles:
    """Tests for validate_no_cycles function."""

    def test_validate_no_cycles_valid_map(self, sample_composition_map):
        """Test validation passes for map without cycles."""
        is_valid, error_msg = composer.validate_no_cycles(sample_composition_map)

        assert is_valid is True
        assert error_msg == ""

    def test_validate_no_cycles_circular_dependency(self, circular_composition_map):
        """Test validation fails for map with circular dependencies."""
        is_valid, error_msg = composer.validate_no_cycles(circular_composition_map)

        assert is_valid is False
        assert "Circular dependency detected" in error_msg
        assert "→" in error_msg

    def test_validate_no_cycles_self_dependency(self):
        """Test validation fails for skill depending on itself."""
        comp_map = {
            "skill-a": ["skill-a"],
        }

        is_valid, error_msg = composer.validate_no_cycles(comp_map)

        assert is_valid is False
        assert "Circular dependency" in error_msg

    def test_validate_no_cycles_complex_cycle(self):
        """Test detection of complex multi-node cycles."""
        comp_map = {
            "skill-a": ["skill-b"],
            "skill-b": ["skill-c"],
            "skill-c": ["skill-d"],
            "skill-d": ["skill-b"],  # Cycle: b -> c -> d -> b
            "skill-e": [],
        }

        is_valid, error_msg = composer.validate_no_cycles(comp_map)

        assert is_valid is False
        assert "Circular dependency" in error_msg

    def test_validate_no_cycles_empty_map(self):
        """Test validation passes for empty map."""
        is_valid, error_msg = composer.validate_no_cycles({})

        assert is_valid is True
        assert error_msg == ""

    def test_validate_no_cycles_disconnected_graphs(self):
        """Test validation with multiple disconnected dependency graphs."""
        comp_map = {
            "group1-a": ["group1-b"],
            "group1-b": [],
            "group2-a": ["group2-b"],
            "group2-b": ["group2-c"],
            "group2-c": [],
        }

        is_valid, error_msg = composer.validate_no_cycles(comp_map)

        assert is_valid is True
        assert error_msg == ""


class TestGetDependencies:
    """Tests for get_dependencies function."""

    def test_get_dependencies_no_deps(self, sample_composition_map):
        """Test getting dependencies for skill with no dependencies."""
        deps = composer.get_dependencies("skill-a", sample_composition_map)

        assert deps == []

    def test_get_dependencies_direct_only(self, sample_composition_map):
        """Test getting direct dependencies."""
        deps = composer.get_dependencies("skill-b", sample_composition_map)

        assert deps == ["skill-a"]

    def test_get_dependencies_transitive(self, sample_composition_map):
        """Test getting transitive dependencies."""
        deps = composer.get_dependencies("skill-c", sample_composition_map)

        # skill-c depends on skill-a and skill-b
        # skill-b depends on skill-a
        # Result should be in topological order: skill-a, skill-b
        assert "skill-a" in deps
        assert "skill-b" in deps
        assert deps.index("skill-a") < deps.index("skill-b")

    def test_get_dependencies_deep_chain(self, sample_composition_map):
        """Test getting dependencies from deep chain."""
        deps = composer.get_dependencies("skill-d", sample_composition_map)

        # skill-d -> skill-c -> [skill-a, skill-b] -> skill-a
        assert "skill-a" in deps
        assert "skill-b" in deps
        assert "skill-c" in deps

        # Verify topological order
        assert deps.index("skill-a") < deps.index("skill-b")
        assert deps.index("skill-b") < deps.index("skill-c")

    def test_get_dependencies_nonexistent_skill(self, sample_composition_map):
        """Test getting dependencies for nonexistent skill."""
        deps = composer.get_dependencies("nonexistent", sample_composition_map)

        assert deps == []

    def test_get_dependencies_diamond_pattern(self):
        """Test getting dependencies with diamond pattern (shared dependency)."""
        comp_map = {
            "skill-a": [],
            "skill-b": ["skill-a"],
            "skill-c": ["skill-a"],
            "skill-d": ["skill-b", "skill-c"],
        }

        deps = composer.get_dependencies("skill-d", comp_map)

        # skill-d depends on skill-b and skill-c, both depend on skill-a
        # skill-a should appear only once, before both skill-b and skill-c
        assert deps.count("skill-a") == 1
        assert deps.count("skill-b") == 1
        assert deps.count("skill-c") == 1

    def test_get_dependencies_with_visited_prevents_cycles(self):
        """Test that visited set prevents infinite loops on circular deps."""
        # Note: This shouldn't happen in production as validate_no_cycles
        # should catch it, but test defensive programming
        circular_map = {
            "skill-a": ["skill-b"],
            "skill-b": ["skill-a"],
        }

        deps = composer.get_dependencies("skill-a", circular_map)

        # Should not hang, and skill-a shouldn't appear in its own deps
        assert "skill-a" not in deps


class TestGetDependencyTree:
    """Tests for get_dependency_tree function."""

    def test_get_dependency_tree_no_deps(self, sample_composition_map):
        """Test dependency tree for skill with no dependencies."""
        tree = composer.get_dependency_tree("skill-a", sample_composition_map)

        assert tree["name"] == "skill-a"
        assert tree["level"] == 0
        assert tree["dependencies"] == []
        assert tree["circular"] is False

    def test_get_dependency_tree_single_level(self, sample_composition_map):
        """Test dependency tree with single level."""
        tree = composer.get_dependency_tree("skill-b", sample_composition_map)

        assert tree["name"] == "skill-b"
        assert tree["level"] == 0
        assert len(tree["dependencies"]) == 1
        assert tree["dependencies"][0]["name"] == "skill-a"
        assert tree["dependencies"][0]["level"] == 1

    def test_get_dependency_tree_multi_level(self, sample_composition_map):
        """Test dependency tree with multiple levels."""
        tree = composer.get_dependency_tree("skill-d", sample_composition_map)

        assert tree["name"] == "skill-d"
        assert tree["level"] == 0
        assert len(tree["dependencies"]) == 1

        skill_c = tree["dependencies"][0]
        assert skill_c["name"] == "skill-c"
        assert skill_c["level"] == 1

    def test_get_dependency_tree_circular_marked(self, circular_composition_map):
        """Test that circular dependencies are marked in tree."""
        tree = composer.get_dependency_tree("skill-a", circular_composition_map)

        # Navigate down: skill-a -> skill-b -> skill-c -> skill-a (circular)
        assert tree["name"] == "skill-a"

        skill_b = tree["dependencies"][0]
        assert skill_b["name"] == "skill-b"

        skill_c = skill_b["dependencies"][0]
        assert skill_c["name"] == "skill-c"

        # skill-a appears again but should be marked circular
        skill_a_again = skill_c["dependencies"][0]
        assert skill_a_again["name"] == "skill-a"
        assert skill_a_again["circular"] is True

    def test_get_dependency_tree_multiple_children(self):
        """Test dependency tree with multiple children at same level."""
        comp_map = {
            "skill-a": [],
            "skill-b": [],
            "skill-c": ["skill-a", "skill-b"],
        }

        tree = composer.get_dependency_tree("skill-c", comp_map)

        assert tree["name"] == "skill-c"
        assert len(tree["dependencies"]) == 2

        dep_names = {dep["name"] for dep in tree["dependencies"]}
        assert dep_names == {"skill-a", "skill-b"}


class TestFormatDependencyTree:
    """Tests for format_dependency_tree function."""

    def test_format_dependency_tree_single_node(self):
        """Test formatting tree with single node."""
        tree = {
            "name": "skill-a",
            "level": 0,
            "dependencies": [],
            "circular": False,
        }

        result = composer.format_dependency_tree(tree)

        assert "└── skill-a" in result
        assert "(circular)" not in result

    def test_format_dependency_tree_with_children(self):
        """Test formatting tree with children."""
        tree = {
            "name": "skill-a",
            "level": 0,
            "dependencies": [
                {
                    "name": "skill-b",
                    "level": 1,
                    "dependencies": [],
                    "circular": False,
                }
            ],
            "circular": False,
        }

        result = composer.format_dependency_tree(tree)

        assert "└── skill-a" in result
        assert "skill-b" in result

    def test_format_dependency_tree_circular_marker(self):
        """Test that circular dependencies are marked in output."""
        tree = {
            "name": "skill-a",
            "level": 0,
            "dependencies": [
                {
                    "name": "skill-b",
                    "level": 1,
                    "dependencies": [],
                    "circular": True,
                }
            ],
            "circular": False,
        }

        result = composer.format_dependency_tree(tree)

        assert "(circular)" in result

    def test_format_dependency_tree_complex_structure(self):
        """Test formatting complex tree structure."""
        tree = {
            "name": "root",
            "level": 0,
            "dependencies": [
                {
                    "name": "child1",
                    "level": 1,
                    "dependencies": [
                        {
                            "name": "grandchild1",
                            "level": 2,
                            "dependencies": [],
                            "circular": False,
                        }
                    ],
                    "circular": False,
                },
                {
                    "name": "child2",
                    "level": 1,
                    "dependencies": [],
                    "circular": False,
                },
            ],
            "circular": False,
        }

        result = composer.format_dependency_tree(tree)

        # Check all names are present
        assert "root" in result
        assert "child1" in result
        assert "child2" in result
        assert "grandchild1" in result

        # Check for tree structure characters
        assert "├──" in result or "└──" in result


class TestGetAllSkillsWithDependencies:
    """Tests for get_all_skills_with_dependencies function."""

    def test_get_all_skills_with_dependencies_mixed(self, sample_composition_map):
        """Test getting skills with dependencies from mixed map."""
        result = composer.get_all_skills_with_dependencies(sample_composition_map)

        # skill-a and skill-e have no dependencies
        # skill-b, skill-c, skill-d have dependencies
        assert result == ["skill-b", "skill-c", "skill-d"]

    def test_get_all_skills_with_dependencies_none(self):
        """Test getting skills when none have dependencies."""
        comp_map = {
            "skill-a": [],
            "skill-b": [],
        }

        result = composer.get_all_skills_with_dependencies(comp_map)

        assert result == []

    def test_get_all_skills_with_dependencies_all(self):
        """Test getting skills when all have dependencies."""
        comp_map = {
            "skill-a": ["dep-1"],
            "skill-b": ["dep-2"],
        }

        result = composer.get_all_skills_with_dependencies(comp_map)

        assert result == ["skill-a", "skill-b"]

    def test_get_all_skills_with_dependencies_sorted(self):
        """Test that result is sorted alphabetically."""
        comp_map = {
            "zebra": ["dep"],
            "alpha": ["dep"],
            "middle": ["dep"],
        }

        result = composer.get_all_skills_with_dependencies(comp_map)

        assert result == ["alpha", "middle", "zebra"]

    def test_get_all_skills_with_dependencies_empty_map(self):
        """Test with empty composition map."""
        result = composer.get_all_skills_with_dependencies({})

        assert result == []
