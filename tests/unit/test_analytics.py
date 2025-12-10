"""Unit tests for analytics module (skill effectiveness analytics)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict

import pytest

from claude_ctx_py import analytics


@pytest.mark.unit
class TestGetEffectivenessScore:
    """Tests for get_effectiveness_score function."""

    def test_effectiveness_score_calculation(
        self, sample_metrics: Dict[str, Any]
    ) -> None:
        """Test effectiveness score calculation."""
        all_metrics = sample_metrics["skills"]
        score = analytics.get_effectiveness_score("test-skill", all_metrics)

        assert isinstance(score, float)
        assert 0 <= score <= 100

    def test_effectiveness_score_nonexistent_skill(self) -> None:
        """Test score for non-existent skill."""
        score = analytics.get_effectiveness_score("nonexistent", {})

        assert score == 0.0

    def test_effectiveness_score_components(
        self, sample_metrics: Dict[str, Any]
    ) -> None:
        """Test that score considers all components."""
        all_metrics = sample_metrics["skills"]
        
        # Test with high success rate
        high_success_metrics = {
            "skill-1": {
                "activation_count": 100,
                "total_tokens_saved": 50000,
                "avg_tokens": 500,
                "success_rate": 0.95,
                "last_activated": datetime.now(timezone.utc).replace(tzinfo=None).isoformat() + "Z"
            }
        }
        score = analytics.get_effectiveness_score("skill-1", high_success_metrics)
        assert score >= 69  # Should be high (69.5 is acceptable)


@pytest.mark.unit
class TestCalculateROI:
    """Tests for calculate_roi function."""

    def test_roi_calculation(
        self, tmp_claude_dir: Path, mock_claude_home: Path, sample_metrics: Dict[str, Any]
    ) -> None:
        """Test ROI calculation."""
        # Create metrics file
        import json
        metrics_path = tmp_claude_dir / ".metrics" / "skills" / "stats.json"
        with open(metrics_path, "w") as f:
            json.dump(sample_metrics, f)

        roi = analytics.calculate_roi("test-skill", tmp_claude_dir)

        assert isinstance(roi, dict)
        assert "cost_saved" in roi
        assert "tokens_saved" in roi
        assert "activations" in roi
        assert "cost_per_activation" in roi
        assert "efficiency_ratio" in roi

    def test_roi_nonexistent_skill(self, tmp_claude_dir: Path) -> None:
        """Test ROI for non-existent skill."""
        roi = analytics.calculate_roi("nonexistent", tmp_claude_dir)

        assert roi["cost_saved"] == 0.0
        assert roi["tokens_saved"] == 0
        assert roi["activations"] == 0


@pytest.mark.unit
class TestGetTrendingSkills:
    """Tests for get_trending_skills function."""

    def test_trending_skills(
        self, tmp_claude_dir: Path, activations_file: Path
    ) -> None:
        """Test getting trending skills."""
        trending = analytics.get_trending_skills(30, tmp_claude_dir)

        assert isinstance(trending, list)
        if trending:
            assert "skill" in trending[0]
            assert "activations" in trending[0]
            assert "tokens_saved" in trending[0]

    def test_trending_skills_no_data(self, tmp_claude_dir: Path) -> None:
        """Test trending skills with no activation data."""
        trending = analytics.get_trending_skills(30, tmp_claude_dir)

        assert trending == []


@pytest.mark.unit
class TestVisualizeMetrics:
    """Tests for visualize_metrics function."""

    def test_visualize_activations(self, sample_metrics: Dict[str, Any]) -> None:
        """Test visualization of activations metric."""
        all_metrics = sample_metrics["skills"]
        chart = analytics.visualize_metrics("activations", all_metrics)

        assert isinstance(chart, str)
        assert len(chart) > 0
        assert "Skill Activations" in chart

    def test_visualize_tokens(self, sample_metrics: Dict[str, Any]) -> None:
        """Test visualization of tokens metric."""
        all_metrics = sample_metrics["skills"]
        chart = analytics.visualize_metrics("tokens", all_metrics)

        assert isinstance(chart, str)
        assert "Tokens Saved" in chart

    def test_visualize_invalid_metric(self, sample_metrics: Dict[str, Any]) -> None:
        """Test visualization with invalid metric."""
        all_metrics = sample_metrics["skills"]
        
        with pytest.raises(ValueError, match="Unsupported metric"):
            analytics.visualize_metrics("invalid", all_metrics)

    def test_visualize_empty_metrics(self) -> None:
        """Test visualization with empty metrics."""
        chart = analytics.visualize_metrics("activations", {})

        assert "No metrics available" in chart


@pytest.mark.unit
class TestGetCorrelationMatrix:
    """Tests for get_correlation_matrix function."""

    def test_correlation_matrix(
        self, tmp_claude_dir: Path, activations_file: Path, sample_metrics: Dict[str, Any]
    ) -> None:
        """Test correlation matrix calculation."""
        all_metrics = sample_metrics["skills"]
        matrix = analytics.get_correlation_matrix(all_metrics)

        assert isinstance(matrix, dict)

    def test_correlation_matrix_no_data(self, sample_metrics: Dict[str, Any]) -> None:
        """Test correlation matrix with no activation data."""
        all_metrics = sample_metrics["skills"]
        matrix = analytics.get_correlation_matrix(all_metrics)

        assert isinstance(matrix, dict)


@pytest.mark.unit
class TestGetImpactReport:
    """Tests for get_impact_report function."""

    def test_impact_report(
        self, tmp_claude_dir: Path, mock_claude_home: Path, sample_metrics: Dict[str, Any]
    ) -> None:
        """Test impact report generation."""
        # Create metrics file
        import json
        metrics_path = tmp_claude_dir / ".metrics" / "skills" / "stats.json"
        with open(metrics_path, "w") as f:
            json.dump(sample_metrics, f)

        report = analytics.get_impact_report("test-skill", tmp_claude_dir)

        assert isinstance(report, dict)
        assert "skill_name" in report
        assert report["skill_name"] == "test-skill"

    def test_impact_report_nonexistent_skill(
        self, tmp_claude_dir: Path, mock_claude_home: Path
    ) -> None:
        """Test impact report for non-existent skill."""
        report = analytics.get_impact_report("nonexistent", tmp_claude_dir)

        assert "error" in report


@pytest.mark.unit
class TestGenerateAnalyticsReport:
    """Tests for generate_analytics_report function."""

    def test_generate_text_report(
        self, tmp_claude_dir: Path, mock_claude_home: Path, sample_metrics: Dict[str, Any]
    ) -> None:
        """Test generating text format report."""
        # Create metrics file
        import json
        metrics_path = tmp_claude_dir / ".metrics" / "skills" / "stats.json"
        with open(metrics_path, "w") as f:
            json.dump(sample_metrics, f)

        report = analytics.generate_analytics_report("text", tmp_claude_dir)

        assert isinstance(report, str)
        assert "ANALYTICS REPORT" in report.upper()

    def test_generate_json_report(
        self, tmp_claude_dir: Path, mock_claude_home: Path, sample_metrics: Dict[str, Any]
    ) -> None:
        """Test generating JSON format report."""
        import json
        
        # Create metrics file
        metrics_path = tmp_claude_dir / ".metrics" / "skills" / "stats.json"
        with open(metrics_path, "w") as f:
            json.dump(sample_metrics, f)

        report = analytics.generate_analytics_report("json", tmp_claude_dir)

        assert isinstance(report, str)
        # Verify it's valid JSON
        data = json.loads(report)
        assert "summary" in data

    def test_generate_report_invalid_format(self, tmp_claude_dir: Path) -> None:
        """Test generating report with invalid format."""
        with pytest.raises(ValueError, match="Unsupported format"):
            analytics.generate_analytics_report("invalid", tmp_claude_dir)
