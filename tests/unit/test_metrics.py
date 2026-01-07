"""Unit tests for metrics module (skill metrics tracking)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

import pytest

from claude_ctx_py import metrics


@pytest.mark.unit
class TestGetMetricsPath:
    """Tests for get_metrics_path function."""

    def test_get_metrics_path_default(self, mock_claude_home: Path) -> None:
        """Test getting metrics path with default home."""
        metrics_path = metrics.get_metrics_path()

        assert metrics_path.exists()
        assert metrics_path.name == "skills"
        assert metrics_path.parent.name == ".metrics"

    def test_get_metrics_path_creates_directory(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that get_metrics_path creates directory if it doesn't exist."""
        claude_dir = tmp_path / ".cortex"
        monkeypatch.setenv("CLAUDE_PLUGIN_ROOT", str(claude_dir))

        metrics_path = metrics.get_metrics_path()

        assert metrics_path.exists()
        assert metrics_path.is_dir()


@pytest.mark.unit
class TestLoadMetrics:
    """Tests for load_metrics function."""

    def test_load_metrics_existing(self, mock_claude_home: Path, metrics_file: Path) -> None:
        """Test loading existing metrics file."""
        loaded = metrics.load_metrics()

        assert isinstance(loaded, dict)
        assert "skills" in loaded
        assert "test-skill" in loaded["skills"]

    def test_load_metrics_missing_file(self, mock_claude_home: Path) -> None:
        """Test loading when metrics file doesn't exist."""
        loaded = metrics.load_metrics()

        assert loaded == {"skills": {}}

    def test_load_metrics_invalid_json(self, mock_claude_home: Path) -> None:
        """Test loading invalid JSON file."""
        metrics_path = mock_claude_home / ".metrics" / "skills" / "stats.json"
        
        with open(metrics_path, "w") as f:
            f.write("invalid json content {")

        loaded = metrics.load_metrics()

        assert loaded == {"skills": {}}


@pytest.mark.unit
class TestRecordActivation:
    """Tests for record_activation function."""

    def test_record_activation_new_skill(self, mock_claude_home: Path) -> None:
        """Test recording activation for a new skill."""
        metrics.record_activation("new-skill", 100, True)

        loaded = metrics.load_metrics()
        assert "new-skill" in loaded["skills"]
        assert loaded["skills"]["new-skill"]["activation_count"] == 1
        assert loaded["skills"]["new-skill"]["total_tokens_saved"] == 100
        assert loaded["skills"]["new-skill"]["success_rate"] == 1.0

    def test_record_activation_existing_skill(self, mock_claude_home: Path, metrics_file: Path) -> None:
        """Test recording activation for existing skill."""
        initial = metrics.load_metrics()
        initial_count = initial["skills"]["test-skill"]["activation_count"]

        metrics.record_activation("test-skill", 200, True)

        updated = metrics.load_metrics()
        assert updated["skills"]["test-skill"]["activation_count"] == initial_count + 1

    def test_record_activation_failure(self, mock_claude_home: Path) -> None:
        """Test recording failed activation."""
        metrics.record_activation("fail-skill", 50, False)

        loaded = metrics.load_metrics()
        assert loaded["skills"]["fail-skill"]["success_rate"] == 0.0

    def test_record_activation_updates_timestamp(self, mock_claude_home: Path) -> None:
        """Test that activation updates last_activated timestamp."""
        before = datetime.now(timezone.utc)
        metrics.record_activation("time-skill", 100, True)
        
        loaded = metrics.load_metrics()
        last_activated = loaded["skills"]["time-skill"]["last_activated"]
        
        assert last_activated is not None
        assert "Z" in last_activated  # UTC timestamp


@pytest.mark.unit
class TestGetSkillMetrics:
    """Tests for get_skill_metrics function."""

    def test_get_skill_metrics_existing(self, mock_claude_home: Path, metrics_file: Path) -> None:
        """Test getting metrics for existing skill."""
        skill_metrics = metrics.get_skill_metrics("test-skill")

        assert skill_metrics is not None
        assert skill_metrics["activation_count"] == 10

    def test_get_skill_metrics_nonexistent(self, mock_claude_home: Path, metrics_file: Path) -> None:
        """Test getting metrics for non-existent skill."""
        skill_metrics = metrics.get_skill_metrics("nonexistent")

        assert skill_metrics is None


@pytest.mark.unit
class TestGetAllMetrics:
    """Tests for get_all_metrics function."""

    def test_get_all_metrics(self, mock_claude_home: Path, metrics_file: Path) -> None:
        """Test getting all metrics."""
        all_metrics = metrics.get_all_metrics()

        assert isinstance(all_metrics, dict)
        assert "test-skill" in all_metrics
        assert "another-skill" in all_metrics


@pytest.mark.unit
class TestResetMetrics:
    """Tests for reset_metrics function."""

    def test_reset_metrics(self, mock_claude_home: Path, metrics_file: Path) -> None:
        """Test resetting all metrics."""
        # Verify file exists
        assert metrics_file.exists()

        metrics.reset_metrics()

        # Verify file is deleted
        assert not metrics_file.exists()


@pytest.mark.unit
class TestRecordDetailedActivation:
    """Tests for record_detailed_activation function."""

    def test_record_detailed_activation(self, mock_claude_home: Path) -> None:
        """Test recording detailed activation."""
        context = {
            "tokens_loaded": 1000,
            "tokens_saved": 500,
            "duration_ms": 100,
            "success": True,
            "agent": "test-agent",
            "task_type": "implementation"
        }

        metrics.record_detailed_activation("detail-skill", context)

        # Verify activations file was created
        activations_file = mock_claude_home / ".metrics" / "skills" / "activations.json"
        assert activations_file.exists()

        # Load and verify data
        with open(activations_file, "r") as f:
            data = json.load(f)

        assert "activations" in data
        assert len(data["activations"]) == 1
        assert data["activations"][0]["skill_name"] == "detail-skill"

    def test_record_detailed_activation_limit(self, mock_claude_home: Path) -> None:
        """Test that activations are limited to 1000 records."""
        context = {
            "tokens_loaded": 100,
            "tokens_saved": 50,
            "success": True
        }

        # Record 1100 activations
        for i in range(1100):
            metrics.record_detailed_activation(f"skill-{i % 10}", context)

        # Verify only last 1000 are kept
        activations_file = mock_claude_home / ".metrics" / "skills" / "activations.json"
        with open(activations_file, "r") as f:
            data = json.load(f)

        assert len(data["activations"]) == 1000


@pytest.mark.unit
class TestFormatMetrics:
    """Tests for format_metrics function."""

    def test_format_single_skill(self, sample_metrics: Dict[str, Any]) -> None:
        """Test formatting metrics for a single skill."""
        all_metrics = sample_metrics["skills"]
        formatted = metrics.format_metrics(all_metrics, "test-skill")

        assert isinstance(formatted, str)
        assert "test-skill" in formatted
        assert "10" in formatted  # activation count

    def test_format_all_skills(self, sample_metrics: Dict[str, Any]) -> None:
        """Test formatting metrics for all skills."""
        all_metrics = sample_metrics["skills"]
        formatted = metrics.format_metrics(all_metrics)

        assert isinstance(formatted, str)
        assert "test-skill" in formatted
        assert "another-skill" in formatted
        assert "Total:" in formatted

    def test_format_empty_metrics(self) -> None:
        """Test formatting empty metrics."""
        formatted = metrics.format_metrics({})

        assert "No metrics recorded" in formatted

    def test_format_nonexistent_skill(self, sample_metrics: Dict[str, Any]) -> None:
        """Test formatting non-existent skill."""
        all_metrics = sample_metrics["skills"]
        formatted = metrics.format_metrics(all_metrics, "nonexistent")

        assert "No metrics found" in formatted
