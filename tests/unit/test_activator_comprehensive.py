"""Comprehensive tests for activator module."""

import pytest
import yaml
from pathlib import Path

from claude_ctx_py import activator


class TestLoadActivationMap:
    """Tests for load_activation_map function."""

    def test_load_activation_map_valid_file(self, tmp_path):
        """Test loading valid activation.yaml file."""
        claude_dir = tmp_path / ".cortex"
        skills_dir = claude_dir / "skills"
        skills_dir.mkdir(parents=True)

        # Create valid activation.yaml
        activation_data = {
            "skills": {
                "pdf": {"keywords": ["PDF", "document", "Adobe"]},
                "xlsx": {"keywords": ["Excel", "spreadsheet", "XLS"]},
                "data-analysis": {"keywords": ["pandas", "numpy", "analysis"]}
            }
        }
        activation_file = skills_dir / "activation.yaml"
        with open(activation_file, "w") as f:
            yaml.dump(activation_data, f)

        # Load activation map
        result = activator.load_activation_map(claude_dir)

        # Verify all skills loaded with lowercased keywords
        assert len(result) == 3
        assert "pdf" in result
        assert "xlsx" in result
        assert "data-analysis" in result
        assert result["pdf"] == ["pdf", "document", "adobe"]
        assert result["xlsx"] == ["excel", "spreadsheet", "xls"]
        assert result["data-analysis"] == ["pandas", "numpy", "analysis"]

    def test_load_activation_map_file_not_found(self, tmp_path):
        """Test loading when activation.yaml doesn't exist."""
        claude_dir = tmp_path / ".cortex"
        claude_dir.mkdir(parents=True)

        with pytest.raises(FileNotFoundError, match="Activation file not found"):
            activator.load_activation_map(claude_dir)

    def test_load_activation_map_empty_file(self, tmp_path):
        """Test loading empty activation.yaml returns empty dict."""
        claude_dir = tmp_path / ".cortex"
        skills_dir = claude_dir / "skills"
        skills_dir.mkdir(parents=True)

        # Create empty file
        activation_file = skills_dir / "activation.yaml"
        activation_file.write_text("")

        result = activator.load_activation_map(claude_dir)
        assert result == {}

    def test_load_activation_map_no_skills_key(self, tmp_path):
        """Test loading file without 'skills' key returns empty dict."""
        claude_dir = tmp_path / ".cortex"
        skills_dir = claude_dir / "skills"
        skills_dir.mkdir(parents=True)

        # Create YAML without skills key
        activation_data = {"other_key": "value"}
        activation_file = skills_dir / "activation.yaml"
        with open(activation_file, "w") as f:
            yaml.dump(activation_data, f)

        result = activator.load_activation_map(claude_dir)
        assert result == {}

    def test_load_activation_map_skills_without_keywords(self, tmp_path):
        """Test loading skills that don't have keywords are skipped."""
        claude_dir = tmp_path / ".cortex"
        skills_dir = claude_dir / "skills"
        skills_dir.mkdir(parents=True)

        # Create YAML with skills but no keywords
        activation_data = {
            "skills": {
                "pdf": {"description": "PDF handling"},
                "xlsx": {"keywords": ["Excel"]},
            }
        }
        activation_file = skills_dir / "activation.yaml"
        with open(activation_file, "w") as f:
            yaml.dump(activation_data, f)

        result = activator.load_activation_map(claude_dir)

        # Only xlsx should be included (has keywords)
        assert len(result) == 1
        assert "xlsx" in result
        assert "pdf" not in result

    def test_load_activation_map_invalid_yaml(self, tmp_path):
        """Test loading malformed YAML raises yaml.YAMLError."""
        claude_dir = tmp_path / ".cortex"
        skills_dir = claude_dir / "skills"
        skills_dir.mkdir(parents=True)

        # Create invalid YAML
        activation_file = skills_dir / "activation.yaml"
        activation_file.write_text("skills:\n  pdf:\n    keywords: [unclosed")

        with pytest.raises(yaml.YAMLError):
            activator.load_activation_map(claude_dir)

    def test_load_activation_map_case_normalization(self, tmp_path):
        """Test that keywords are normalized to lowercase."""
        claude_dir = tmp_path / ".cortex"
        skills_dir = claude_dir / "skills"
        skills_dir.mkdir(parents=True)

        # Create activation with mixed-case keywords
        activation_data = {
            "skills": {
                "test": {"keywords": ["Test", "TESTING", "TeSt"]}
            }
        }
        activation_file = skills_dir / "activation.yaml"
        with open(activation_file, "w") as f:
            yaml.dump(activation_data, f)

        result = activator.load_activation_map(claude_dir)

        # Verify all keywords are lowercase
        assert result["test"] == ["test", "testing", "test"]


class TestAnalyzeText:
    """Tests for analyze_text function."""

    @pytest.fixture
    def setup_activation_map(self, tmp_path):
        """Setup activation.yaml for tests."""
        claude_dir = tmp_path / ".cortex"
        skills_dir = claude_dir / "skills"
        skills_dir.mkdir(parents=True)

        activation_data = {
            "skills": {
                "pdf": {"keywords": ["pdf", "document", "adobe"]},
                "xlsx": {"keywords": ["excel", "spreadsheet", "xls"]},
                "python": {"keywords": ["python", "py", "django", "flask"]},
                "typescript": {"keywords": ["typescript", "ts", "react", "angular"]},
            }
        }
        activation_file = skills_dir / "activation.yaml"
        with open(activation_file, "w") as f:
            yaml.dump(activation_data, f)

        return claude_dir

    def test_analyze_text_single_match(self, setup_activation_map):
        """Test analyzing text with single skill match."""
        text = "I need help with a PDF document."
        matches = activator.analyze_text(text, setup_activation_map)

        assert len(matches) == 1
        assert "pdf" in matches

    def test_analyze_text_multiple_matches(self, setup_activation_map):
        """Test analyzing text with multiple skill matches."""
        text = "Convert Excel spreadsheet to PDF document using Python."
        matches = activator.analyze_text(text, setup_activation_map)

        assert len(matches) == 3
        assert "pdf" in matches
        assert "xlsx" in matches
        assert "python" in matches

    def test_analyze_text_no_matches(self, setup_activation_map):
        """Test analyzing text with no matches."""
        text = "Just some random text without any skill keywords."
        matches = activator.analyze_text(text, setup_activation_map)

        assert len(matches) == 0

    def test_analyze_text_case_insensitive(self, setup_activation_map):
        """Test that text matching is case-insensitive."""
        text = "I need PYTHON and EXCEL help."
        matches = activator.analyze_text(text, setup_activation_map)

        assert len(matches) == 2
        assert "python" in matches
        assert "xlsx" in matches

    def test_analyze_text_partial_word_matches(self, setup_activation_map):
        """Test that keywords match within words."""
        text = "Using typescript-based framework for react development."
        matches = activator.analyze_text(text, setup_activation_map)

        assert len(matches) == 1
        assert "typescript" in matches

    def test_analyze_text_multiple_keywords_same_skill(self, setup_activation_map):
        """Test that multiple keywords for same skill only count once."""
        text = "Using Python and Django and Flask together."
        matches = activator.analyze_text(text, setup_activation_map)

        # Should only have python once (not 3 times)
        assert len(matches) == 1
        assert "python" in matches

    def test_analyze_text_missing_activation_file(self, tmp_path):
        """Test analyzing text when activation.yaml doesn't exist."""
        claude_dir = tmp_path / ".cortex"
        claude_dir.mkdir(parents=True)

        # Should return empty list (no exception)
        matches = activator.analyze_text("test text", claude_dir)
        assert matches == []

    def test_analyze_text_empty_input(self, setup_activation_map):
        """Test analyzing empty text."""
        matches = activator.analyze_text("", setup_activation_map)
        assert matches == []

    def test_analyze_text_whitespace_only(self, setup_activation_map):
        """Test analyzing whitespace-only text."""
        matches = activator.analyze_text("   \n\t  ", setup_activation_map)
        assert matches == []

    def test_analyze_text_sorted_results(self, setup_activation_map):
        """Test that results are returned in sorted order."""
        text = "Using typescript, python, and excel together."
        matches = activator.analyze_text(text, setup_activation_map)

        # Results should be alphabetically sorted
        assert matches == ["python", "typescript", "xlsx"]


class TestSuggestSkills:
    """Tests for suggest_skills function."""

    @pytest.fixture
    def setup_activation_map(self, tmp_path):
        """Setup activation.yaml for tests."""
        claude_dir = tmp_path / ".cortex"
        skills_dir = claude_dir / "skills"
        skills_dir.mkdir(parents=True)

        activation_data = {
            "skills": {
                "pdf": {"keywords": ["pdf", "document"]},
                "xlsx": {"keywords": ["excel", "spreadsheet"]},
                "python": {"keywords": ["python", "django"]},
            }
        }
        activation_file = skills_dir / "activation.yaml"
        with open(activation_file, "w") as f:
            yaml.dump(activation_data, f)

        return claude_dir

    def test_suggest_skills_with_matches(self, setup_activation_map):
        """Test suggesting skills when matches are found."""
        text = "I need help with Python and Excel."
        result = activator.suggest_skills(text, setup_activation_map)

        # Should contain count
        assert "Found 2 matching skill(s)" in result

        # Should contain skill names
        assert "python" in result
        assert "xlsx" in result

        # Should contain help text
        assert "cortex skills info" in result

    def test_suggest_skills_single_match(self, setup_activation_map):
        """Test suggesting skills with single match."""
        text = "I need help with PDF documents."
        result = activator.suggest_skills(text, setup_activation_map)

        assert "Found 1 matching skill(s)" in result
        assert "pdf" in result

    def test_suggest_skills_no_matches(self, setup_activation_map):
        """Test suggesting skills when no matches found."""
        text = "Just some random text."
        result = activator.suggest_skills(text, setup_activation_map)

        assert "No matching skills found" in result
        assert "cortex skills info" not in result

    def test_suggest_skills_formatting(self, setup_activation_map):
        """Test that output is properly formatted with bullets."""
        text = "Python and Excel help needed."
        result = activator.suggest_skills(text, setup_activation_map)

        # Check for bullet points
        assert "  - python" in result
        assert "  - xlsx" in result

        # Check for newlines (proper formatting)
        lines = result.split("\n")
        assert len(lines) >= 4  # Header, skill 1, skill 2, help text

    def test_suggest_skills_empty_text(self, setup_activation_map):
        """Test suggesting skills with empty text."""
        result = activator.suggest_skills("", setup_activation_map)
        assert "No matching skills found" in result

    def test_suggest_skills_missing_activation_file(self, tmp_path):
        """Test suggesting skills when activation file doesn't exist."""
        claude_dir = tmp_path / ".cortex"
        claude_dir.mkdir(parents=True)

        result = activator.suggest_skills("test text", claude_dir)
        assert "No matching skills found" in result
