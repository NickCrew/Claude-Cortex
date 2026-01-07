"""Comprehensive tests for metrics module."""

import json
import os
import pytest
import uuid
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock

from claude_ctx_py import metrics
from claude_ctx_py.exceptions import MetricsFileError


class TestGetMetricsPath:
    """Tests for get_metrics_path function."""

    def test_get_metrics_path_default(self, tmp_path, monkeypatch):
        """Test getting default metrics path (~/.cortex/.metrics/skills/)."""
        # Mock home directory
        monkeypatch.setenv("HOME", str(tmp_path))
        monkeypatch.delenv("CLAUDE_PLUGIN_ROOT", raising=False)

        path = metrics.get_metrics_path()

        expected = tmp_path / ".cortex" / ".metrics" / "skills"
        assert path == expected
        assert path.exists()  # Should create directory

    def test_get_metrics_path_with_plugin_root(self, tmp_path, monkeypatch):
        """Test getting metrics path when CLAUDE_PLUGIN_ROOT is set."""
        plugin_root = tmp_path / "plugin"
        plugin_root.mkdir(parents=True)

        monkeypatch.setenv("CLAUDE_PLUGIN_ROOT", str(plugin_root))

        path = metrics.get_metrics_path()

        expected = plugin_root / ".metrics" / "skills"
        assert path == expected

    def test_get_metrics_path_creates_directory(self, tmp_path, monkeypatch):
        """Test that metrics directory is created if it doesn't exist."""
        monkeypatch.setenv("HOME", str(tmp_path))
        monkeypatch.delenv("CLAUDE_PLUGIN_ROOT", raising=False)

        # Ensure directory doesn't exist
        metrics_dir = tmp_path / ".cortex" / ".metrics" / "skills"
        assert not metrics_dir.exists()

        path = metrics.get_metrics_path()

        # Should be created now
        assert path.exists()
        assert path.is_dir()


class TestLoadMetrics:
    """Tests for load_metrics function."""

    def test_load_metrics_file_exists(self, tmp_path, monkeypatch):
        """Test loading metrics when stats.json exists."""
        # Setup metrics directory
        metrics_dir = tmp_path / ".metrics" / "skills"
        metrics_dir.mkdir(parents=True)
        stats_file = metrics_dir / "stats.json"

        # Create stats file
        test_data = {
            "skills": {
                "pdf": {
                    "activation_count": 10,
                    "total_tokens_saved": 5000,
                    "avg_tokens": 500,
                    "last_activated": "2025-01-01T12:00:00Z",
                    "success_rate": 0.9
                }
            }
        }
        with open(stats_file, "w") as f:
            json.dump(test_data, f)

        # Mock get_metrics_path
        with patch("claude_ctx_py.metrics.get_metrics_path", return_value=metrics_dir):
            result = metrics.load_metrics()

        assert result == test_data
        assert "pdf" in result["skills"]

    def test_load_metrics_file_not_exists(self, tmp_path):
        """Test loading metrics when stats.json doesn't exist."""
        metrics_dir = tmp_path / ".metrics" / "skills"
        metrics_dir.mkdir(parents=True)

        with patch("claude_ctx_py.metrics.get_metrics_path", return_value=metrics_dir):
            result = metrics.load_metrics()

        # Should return default structure
        assert result == {"skills": {}}

    def test_load_metrics_invalid_json(self, tmp_path):
        """Test loading metrics with invalid JSON returns default."""
        metrics_dir = tmp_path / ".metrics" / "skills"
        metrics_dir.mkdir(parents=True)
        stats_file = metrics_dir / "stats.json"

        # Create invalid JSON
        stats_file.write_text("{invalid json")

        with patch("claude_ctx_py.metrics.get_metrics_path", return_value=metrics_dir):
            result = metrics.load_metrics()

        # Should return default structure on error
        assert result == {"skills": {}}


class TestRecordActivation:
    """Tests for record_activation function."""

    def test_record_activation_new_skill(self, tmp_path):
        """Test recording activation for a new skill."""
        metrics_dir = tmp_path / ".metrics" / "skills"
        metrics_dir.mkdir(parents=True)

        with patch("claude_ctx_py.metrics.get_metrics_path", return_value=metrics_dir):
            metrics.record_activation("pdf", tokens_used=500, success=True)

            # Verify metrics were saved
            stats_file = metrics_dir / "stats.json"
            assert stats_file.exists()

            with open(stats_file) as f:
                data = json.load(f)

            assert "pdf" in data["skills"]
            skill = data["skills"]["pdf"]
            assert skill["activation_count"] == 1
            assert skill["total_tokens_saved"] == 500
            assert skill["avg_tokens"] == 500
            assert skill["success_rate"] == 1.0
            assert skill["last_activated"] is not None

    def test_record_activation_existing_skill(self, tmp_path):
        """Test recording activation for existing skill."""
        metrics_dir = tmp_path / ".metrics" / "skills"
        metrics_dir.mkdir(parents=True)

        # Create initial metrics
        initial_data = {
            "skills": {
                "pdf": {
                    "activation_count": 5,
                    "total_tokens_saved": 2500,
                    "avg_tokens": 500,
                    "last_activated": "2025-01-01T12:00:00Z",
                    "success_rate": 0.8
                }
            }
        }
        stats_file = metrics_dir / "stats.json"
        with open(stats_file, "w") as f:
            json.dump(initial_data, f)

        with patch("claude_ctx_py.metrics.get_metrics_path", return_value=metrics_dir):
            metrics.record_activation("pdf", tokens_used=600, success=True)

            # Verify metrics were updated
            with open(stats_file) as f:
                data = json.load(f)

            skill = data["skills"]["pdf"]
            assert skill["activation_count"] == 6
            assert skill["total_tokens_saved"] == 3100
            assert skill["avg_tokens"] == 516  # 3100 // 6
            # Success rate: (5 * 0.8 + 1) / 6 = 5/6 ≈ 0.833
            assert abs(skill["success_rate"] - 0.833) < 0.01

    def test_record_activation_with_failure(self, tmp_path):
        """Test recording failed activation updates success rate."""
        metrics_dir = tmp_path / ".metrics" / "skills"
        metrics_dir.mkdir(parents=True)

        with patch("claude_ctx_py.metrics.get_metrics_path", return_value=metrics_dir):
            # Record success
            metrics.record_activation("pdf", tokens_used=500, success=True)
            # Record failure
            metrics.record_activation("pdf", tokens_used=0, success=False)

            stats_file = metrics_dir / "stats.json"
            with open(stats_file) as f:
                data = json.load(f)

            skill = data["skills"]["pdf"]
            assert skill["activation_count"] == 2
            assert skill["success_rate"] == 0.5  # 1 success out of 2

    def test_record_activation_zero_tokens(self, tmp_path):
        """Test recording activation with zero tokens."""
        metrics_dir = tmp_path / ".metrics" / "skills"
        metrics_dir.mkdir(parents=True)

        with patch("claude_ctx_py.metrics.get_metrics_path", return_value=metrics_dir):
            metrics.record_activation("pdf", tokens_used=0, success=True)

            stats_file = metrics_dir / "stats.json"
            with open(stats_file) as f:
                data = json.load(f)

            skill = data["skills"]["pdf"]
            assert skill["total_tokens_saved"] == 0
            assert skill["avg_tokens"] == 0

    def test_record_activation_negative_tokens(self, tmp_path):
        """Test recording activation with negative tokens (cost)."""
        metrics_dir = tmp_path / ".metrics" / "skills"
        metrics_dir.mkdir(parents=True)

        with patch("claude_ctx_py.metrics.get_metrics_path", return_value=metrics_dir):
            metrics.record_activation("pdf", tokens_used=-100, success=True)

            stats_file = metrics_dir / "stats.json"
            with open(stats_file) as f:
                data = json.load(f)

            skill = data["skills"]["pdf"]
            assert skill["total_tokens_saved"] == -100
            assert skill["avg_tokens"] == -100


class TestGetSkillMetrics:
    """Tests for get_skill_metrics function."""

    def test_get_skill_metrics_exists(self, tmp_path):
        """Test getting metrics for existing skill."""
        metrics_dir = tmp_path / ".metrics" / "skills"
        metrics_dir.mkdir(parents=True)

        test_data = {
            "skills": {
                "pdf": {
                    "activation_count": 10,
                    "total_tokens_saved": 5000
                }
            }
        }
        stats_file = metrics_dir / "stats.json"
        with open(stats_file, "w") as f:
            json.dump(test_data, f)

        with patch("claude_ctx_py.metrics.get_metrics_path", return_value=metrics_dir):
            result = metrics.get_skill_metrics("pdf")

        assert result is not None
        assert result["activation_count"] == 10
        assert result["total_tokens_saved"] == 5000

    def test_get_skill_metrics_not_exists(self, tmp_path):
        """Test getting metrics for non-existent skill returns None."""
        metrics_dir = tmp_path / ".metrics" / "skills"
        metrics_dir.mkdir(parents=True)

        test_data = {"skills": {}}
        stats_file = metrics_dir / "stats.json"
        with open(stats_file, "w") as f:
            json.dump(test_data, f)

        with patch("claude_ctx_py.metrics.get_metrics_path", return_value=metrics_dir):
            result = metrics.get_skill_metrics("nonexistent")

        assert result is None

    def test_get_skill_metrics_no_file(self, tmp_path):
        """Test getting metrics when stats.json doesn't exist."""
        metrics_dir = tmp_path / ".metrics" / "skills"
        metrics_dir.mkdir(parents=True)

        with patch("claude_ctx_py.metrics.get_metrics_path", return_value=metrics_dir):
            result = metrics.get_skill_metrics("pdf")

        assert result is None


class TestGetAllMetrics:
    """Tests for get_all_metrics function."""

    def test_get_all_metrics_with_data(self, tmp_path):
        """Test getting all metrics when data exists."""
        metrics_dir = tmp_path / ".metrics" / "skills"
        metrics_dir.mkdir(parents=True)

        test_data = {
            "skills": {
                "pdf": {"activation_count": 10},
                "xlsx": {"activation_count": 5},
            }
        }
        stats_file = metrics_dir / "stats.json"
        with open(stats_file, "w") as f:
            json.dump(test_data, f)

        with patch("claude_ctx_py.metrics.get_metrics_path", return_value=metrics_dir):
            result = metrics.get_all_metrics()

        assert len(result) == 2
        assert "pdf" in result
        assert "xlsx" in result

    def test_get_all_metrics_empty(self, tmp_path):
        """Test getting all metrics when no metrics exist."""
        metrics_dir = tmp_path / ".metrics" / "skills"
        metrics_dir.mkdir(parents=True)

        with patch("claude_ctx_py.metrics.get_metrics_path", return_value=metrics_dir):
            result = metrics.get_all_metrics()

        assert result == {}


class TestResetMetrics:
    """Tests for reset_metrics function."""

    def test_reset_metrics_file_exists(self, tmp_path):
        """Test resetting metrics deletes stats.json."""
        metrics_dir = tmp_path / ".metrics" / "skills"
        metrics_dir.mkdir(parents=True)

        # Create stats file
        stats_file = metrics_dir / "stats.json"
        stats_file.write_text('{"skills": {}}')
        assert stats_file.exists()

        with patch("claude_ctx_py.metrics.get_metrics_path", return_value=metrics_dir):
            metrics.reset_metrics()

        assert not stats_file.exists()

    def test_reset_metrics_file_not_exists(self, tmp_path):
        """Test resetting metrics when file doesn't exist (no error)."""
        metrics_dir = tmp_path / ".metrics" / "skills"
        metrics_dir.mkdir(parents=True)

        stats_file = metrics_dir / "stats.json"
        assert not stats_file.exists()

        # Should not raise error
        with patch("claude_ctx_py.metrics.get_metrics_path", return_value=metrics_dir):
            metrics.reset_metrics()


class TestRecordDetailedActivation:
    """Tests for record_detailed_activation function."""

    def test_record_detailed_activation_new_file(self, tmp_path):
        """Test recording detailed activation creates activations.json."""
        metrics_dir = tmp_path / ".metrics" / "skills"
        metrics_dir.mkdir(parents=True)

        context = {
            "tokens_loaded": 100,
            "tokens_saved": 500,
            "duration_ms": 50,
            "success": True,
            "agent": "test-agent",
            "task_type": "test-task"
        }

        with patch("claude_ctx_py.metrics.get_metrics_path", return_value=metrics_dir):
            with patch("claude_ctx_py.metrics.record_activation"):
                metrics.record_detailed_activation("pdf", context)

            # Verify activations file was created
            activations_file = metrics_dir / "activations.json"
            assert activations_file.exists()

            with open(activations_file) as f:
                data = json.load(f)

            assert "activations" in data
            assert len(data["activations"]) == 1

            activation = data["activations"][0]
            assert activation["skill_name"] == "pdf"
            assert activation["context"]["agent"] == "test-agent"
            assert activation["metrics"]["tokens_saved"] == 500
            assert "activation_id" in activation
            assert "timestamp" in activation

    def test_record_detailed_activation_appends(self, tmp_path):
        """Test recording detailed activation appends to existing file."""
        metrics_dir = tmp_path / ".metrics" / "skills"
        metrics_dir.mkdir(parents=True)

        # Create existing activations file
        existing_data = {
            "activations": [
                {
                    "activation_id": "existing-1",
                    "skill_name": "xlsx",
                    "timestamp": "2025-01-01T00:00:00Z"
                }
            ]
        }
        activations_file = metrics_dir / "activations.json"
        with open(activations_file, "w") as f:
            json.dump(existing_data, f)

        context = {"tokens_saved": 500, "success": True}

        with patch("claude_ctx_py.metrics.get_metrics_path", return_value=metrics_dir):
            with patch("claude_ctx_py.metrics.record_activation"):
                metrics.record_detailed_activation("pdf", context)

            with open(activations_file) as f:
                data = json.load(f)

            # Should have 2 activations now
            assert len(data["activations"]) == 2
            assert data["activations"][0]["activation_id"] == "existing-1"
            assert data["activations"][1]["skill_name"] == "pdf"

    def test_record_detailed_activation_limits_to_1000(self, tmp_path):
        """Test that activations are limited to last 1000."""
        metrics_dir = tmp_path / ".metrics" / "skills"
        metrics_dir.mkdir(parents=True)

        # Create file with 1000 activations
        existing_data = {
            "activations": [
                {"activation_id": f"act-{i}", "skill_name": "test"}
                for i in range(1000)
            ]
        }
        activations_file = metrics_dir / "activations.json"
        with open(activations_file, "w") as f:
            json.dump(existing_data, f)

        context = {"tokens_saved": 500, "success": True}

        with patch("claude_ctx_py.metrics.get_metrics_path", return_value=metrics_dir):
            with patch("claude_ctx_py.metrics.record_activation"):
                metrics.record_detailed_activation("pdf", context)

            with open(activations_file) as f:
                data = json.load(f)

            # Should still be 1000 (oldest removed)
            assert len(data["activations"]) == 1000
            # First item should now be act-1 (act-0 removed)
            assert data["activations"][0]["activation_id"] == "act-1"
            # Last item should be the new one
            assert data["activations"][-1]["skill_name"] == "pdf"

    def test_record_detailed_activation_default_values(self, tmp_path):
        """Test that default values are used when context fields are missing."""
        metrics_dir = tmp_path / ".metrics" / "skills"
        metrics_dir.mkdir(parents=True)

        context = {}  # Empty context

        with patch("claude_ctx_py.metrics.get_metrics_path", return_value=metrics_dir):
            with patch("claude_ctx_py.metrics.record_activation"):
                metrics.record_detailed_activation("pdf", context)

            activations_file = metrics_dir / "activations.json"
            with open(activations_file) as f:
                data = json.load(f)

            activation = data["activations"][0]
            # Check default values
            assert activation["context"]["agent"] == "unknown"
            assert activation["context"]["task_type"] == "unknown"
            assert activation["metrics"]["tokens_loaded"] == 0
            assert activation["metrics"]["tokens_saved"] == 0
            assert activation["metrics"]["success"] is True
            assert activation["effectiveness"]["relevance_score"] == 0.8


class TestFormatMetrics:
    """Tests for format_metrics function."""

    def test_format_metrics_empty(self):
        """Test formatting empty metrics."""
        result = metrics.format_metrics({})
        assert "No metrics recorded yet" in result

    def test_format_metrics_single_skill(self):
        """Test formatting metrics for single skill."""
        test_metrics = {
            "pdf": {
                "activation_count": 10,
                "total_tokens_saved": 5000,
                "avg_tokens": 500,
                "success_rate": 0.9,
                "last_activated": "2025-01-01T12:00:00Z"
            }
        }

        result = metrics.format_metrics(test_metrics, skill_name="pdf")

        assert "Skill: pdf" in result
        assert "Activation Count:    10" in result
        assert "5,000" in result  # Formatted with comma
        assert "90.0%" in result
        assert "Last Activated:" in result

    def test_format_metrics_single_skill_not_found(self):
        """Test formatting when requested skill doesn't exist."""
        test_metrics = {"xlsx": {"activation_count": 5}}

        result = metrics.format_metrics(test_metrics, skill_name="pdf")
        assert "No metrics found for skill: pdf" in result

    def test_format_metrics_all_skills(self):
        """Test formatting all skills."""
        test_metrics = {
            "pdf": {
                "activation_count": 10,
                "total_tokens_saved": 5000,
                "avg_tokens": 500,
                "success_rate": 0.9,
                "last_activated": "2025-01-01T12:00:00Z"
            },
            "xlsx": {
                "activation_count": 5,
                "total_tokens_saved": 2500,
                "avg_tokens": 500,
                "success_rate": 0.8,
                "last_activated": "2025-01-02T12:00:00Z"
            }
        }

        result = metrics.format_metrics(test_metrics)

        # Should contain header
        assert "Skill Metrics Summary" in result

        # Should contain both skills
        assert "pdf" in result
        assert "xlsx" in result

        # Should contain totals
        assert "Total: 2 skills, 15 activations" in result
        assert "7,500 tokens saved" in result

    def test_format_metrics_sorted_by_usage(self):
        """Test that skills are sorted by activation count."""
        test_metrics = {
            "skill-a": {
                "activation_count": 5,
                "total_tokens_saved": 1000,
                "avg_tokens": 200,
                "success_rate": 0.8,
                "last_activated": None
            },
            "skill-b": {
                "activation_count": 10,
                "total_tokens_saved": 2000,
                "avg_tokens": 200,
                "success_rate": 0.9,
                "last_activated": None
            }
        }

        result = metrics.format_metrics(test_metrics)
        lines = result.split("\n")

        # Find lines with skill names
        skill_lines = [l for l in lines if "skill-" in l and "activation_count" not in l]

        # skill-b (10 uses) should come before skill-a (5 uses)
        assert skill_lines[0].startswith("skill-b")
        assert skill_lines[1].startswith("skill-a")

    def test_format_metrics_never_activated(self):
        """Test formatting skill that was never activated."""
        test_metrics = {
            "pdf": {
                "activation_count": 1,
                "total_tokens_saved": 500,
                "avg_tokens": 500,
                "success_rate": 1.0,
                "last_activated": None
            }
        }

        result = metrics.format_metrics(test_metrics, skill_name="pdf")
        assert "Never" in result
