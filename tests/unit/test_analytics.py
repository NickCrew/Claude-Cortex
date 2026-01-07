"""Unit tests for analytics module."""

import json
from pathlib import Path
from unittest import mock
import pytest
from datetime import datetime, timedelta, timezone

from claude_ctx_py import analytics
from claude_ctx_py.exceptions import ExportError

# --------------------------------------------------------------------------- fixtures

@pytest.fixture
def mock_claude_dir(tmp_path):
    """Create a mock .cortex directory with metrics."""
    claude_dir = tmp_path / ".cortex"
    metrics_dir = claude_dir / ".metrics" / "skills"
    metrics_dir.mkdir(parents=True, exist_ok=True)
    return claude_dir

@pytest.fixture
def sample_metrics_data():
    """Sample metrics data map."""
    return {
        "skill-high-value": {
            "activation_count": 100,
            "total_tokens_saved": 500000,
            "avg_tokens": 5000,
            "success_rate": 0.95,
            "last_activated": datetime.now(timezone.utc).isoformat()
        },
        "skill-low-success": {
            "activation_count": 50,
            "total_tokens_saved": 5000,
            "avg_tokens": 100,
            "success_rate": 0.4,
            "last_activated": datetime.now(timezone.utc).isoformat()
        },
        "skill-stale": {
            "activation_count": 10,
            "total_tokens_saved": 1000,
            "avg_tokens": 100,
            "success_rate": 0.8,
            "last_activated": (datetime.now(timezone.utc) - timedelta(days=60)).isoformat()
        },
        "skill-underutilized": {
            "activation_count": 2,
            "total_tokens_saved": 20000,
            "avg_tokens": 10000,
            "success_rate": 1.0,
            "last_activated": datetime.now(timezone.utc).isoformat()
        }
    }

@pytest.fixture
def sample_activations_data():
    """Sample activations data for correlation matrix."""
    return {
        "activations": [
            {
                "skill_name": "skill-a",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "context": {"co_activated_skills": ["skill-b"]},
                "metrics": {"tokens_loaded": 1000, "tokens_saved": 500}
            },
            {
                "skill_name": "skill-b",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "context": {"co_activated_skills": ["skill-a"]},
                "metrics": {"tokens_loaded": 1000, "tokens_saved": 500}
            },
            {
                "skill_name": "skill-a",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "context": {"co_activated_skills": []},
                "metrics": {"tokens_loaded": 1000, "tokens_saved": 500}
            }
        ]
    }

# --------------------------------------------------------------------------- get_effectiveness_score

class TestGetEffectivenessScore:
    def test_score_calculation(self, sample_metrics_data):
        score = analytics.get_effectiveness_score("skill-high-value", sample_metrics_data)
        # Success (0.95 * 40 = 38) + Efficiency (0.5 * 30 = 15) + Usage (100/100 * 20 = 20) + Recency (~10)
        assert score > 80
        assert score <= 100

    def test_score_missing_skill(self, sample_metrics_data):
        assert analytics.get_effectiveness_score("missing", sample_metrics_data) == 0.0

    def test_score_components(self, sample_metrics_data):
        # High success rate should boost score
        high_success = sample_metrics_data["skill-high-value"]
        score_high = analytics.get_effectiveness_score("skill-high-value", sample_metrics_data)
        
        low_success = sample_metrics_data["skill-low-success"]
        score_low = analytics.get_effectiveness_score("skill-low-success", sample_metrics_data)
        
        assert score_high > score_low

    def test_score_stale_recency(self, sample_metrics_data):
        stale_score = analytics.get_effectiveness_score("skill-stale", sample_metrics_data)
        # Recency component should be low
        # e^(-60/30) * 10 ~= 1.35
        # Usage: 10/100 * 20 = 2
        # Efficiency: 100/10000 * 30 = 0.3
        # Success: 0.8 * 40 = 32
        # Total ~ 35.65
        assert 30 < stale_score < 40

# --------------------------------------------------------------------------- get_recommendations

class TestGetRecommendations:
    @mock.patch("claude_ctx_py.metrics.get_all_metrics")
    def test_recommendations_underutilized(self, mock_metrics, sample_metrics_data, mock_claude_dir):
        mock_metrics.return_value = sample_metrics_data
        recs = analytics.get_recommendations({}, mock_claude_dir)
        assert any("Consider using 'skill-underutilized' more often" in r for r in recs)

    @mock.patch("claude_ctx_py.metrics.get_all_metrics")
    def test_recommendations_low_success(self, mock_metrics, sample_metrics_data, mock_claude_dir):
        mock_metrics.return_value = sample_metrics_data
        recs = analytics.get_recommendations({}, mock_claude_dir)
        assert any("Review 'skill-low-success'" in r for r in recs)

    @mock.patch("claude_ctx_py.metrics.get_all_metrics")
    def test_recommendations_stale(self, mock_metrics, sample_metrics_data, mock_claude_dir):
        mock_metrics.return_value = sample_metrics_data
        recs = analytics.get_recommendations({}, mock_claude_dir)
        assert any("'skill-stale' hasn't been used in 30+ days" in r for r in recs)

    @mock.patch("claude_ctx_py.metrics.get_all_metrics")
    def test_recommendations_empty(self, mock_metrics, mock_claude_dir):
        mock_metrics.return_value = {}
        recs = analytics.get_recommendations({}, mock_claude_dir)
        assert len(recs) == 1
        assert "No metrics available" in recs[0]

    @mock.patch("claude_ctx_py.metrics.get_all_metrics")
    @mock.patch("claude_ctx_py.analytics.get_correlation_matrix")
    def test_recommendations_co_activation(self, mock_corr, mock_metrics, sample_metrics_data, mock_claude_dir):
        mock_metrics.return_value = sample_metrics_data
        mock_corr.return_value = {"skill-a": {"skill-b": 0.8}, "skill-b": {"skill-a": 0.8}}
        
        recs = analytics.get_recommendations({}, mock_claude_dir)
        assert any("'skill-a' and 'skill-b' are frequently used together" in r for r in recs)

# --------------------------------------------------------------------------- visualize_metrics

class TestVisualizeMetrics:
    def test_visualize_activations(self, sample_metrics_data):
        chart = analytics.visualize_metrics("activations", sample_metrics_data)
        assert "Skill Activations" in chart
        assert "skill-high-value" in chart
        assert "█" in chart

    def test_visualize_tokens(self, sample_metrics_data):
        chart = analytics.visualize_metrics("tokens", sample_metrics_data)
        assert "Tokens Saved" in chart
        assert "500,000" in chart

    def test_visualize_effectiveness(self, sample_metrics_data):
        chart = analytics.visualize_metrics("effectiveness", sample_metrics_data)
        assert "Effectiveness Score" in chart

    def test_visualize_success_rate(self, sample_metrics_data):
        chart = analytics.visualize_metrics("success_rate", sample_metrics_data)
        assert "Success Rate" in chart
        assert "95.0" in chart

    def test_visualize_unsupported_metric(self, sample_metrics_data):
        with pytest.raises(ValueError):
            analytics.visualize_metrics("invalid", sample_metrics_data)

    def test_visualize_empty_metrics(self):
        assert "No metrics available" in analytics.visualize_metrics("tokens", {})

# --------------------------------------------------------------------------- export_analytics

class TestExportAnalytics:
    @mock.patch("claude_ctx_py.metrics.get_all_metrics")
    def test_export_json(self, mock_metrics, sample_metrics_data, mock_claude_dir):
        mock_metrics.return_value = sample_metrics_data
        
        path = analytics.export_analytics("json", mock_claude_dir)
        assert path.endswith(".json")
        assert Path(path).exists()
        
        content = json.loads(Path(path).read_text())
        assert "exported_at" in content
        assert "skills" in content
        assert "skill-high-value" in content["skills"]

    @mock.patch("claude_ctx_py.metrics.get_all_metrics")
    def test_export_csv(self, mock_metrics, sample_metrics_data, mock_claude_dir):
        mock_metrics.return_value = sample_metrics_data
        
        path = analytics.export_analytics("csv", mock_claude_dir)
        assert path.endswith(".csv")
        assert Path(path).exists()
        
        lines = Path(path).read_text().splitlines()
        assert "Skill Name,Activation Count" in lines[0]
        assert any("skill-high-value" in line for line in lines)

    @mock.patch("claude_ctx_py.metrics.get_all_metrics")
    def test_export_text(self, mock_metrics, sample_metrics_data, mock_claude_dir):
        mock_metrics.return_value = sample_metrics_data
        
        path = analytics.export_analytics("text", mock_claude_dir)
        assert path.endswith(".text")
        assert Path(path).exists()
        
        content = Path(path).read_text()
        assert "SKILL ANALYTICS REPORT" in content
        assert "SUMMARY" in content
        assert "skill-high-value" in content

    @mock.patch("claude_ctx_py.metrics.get_all_metrics")
    def test_export_unsupported_format(self, mock_metrics, mock_claude_dir):
        mock_metrics.return_value = {}
        with pytest.raises(ExportError):
            analytics.export_analytics("xml", mock_claude_dir)

    @mock.patch("claude_ctx_py.metrics.get_all_metrics")
    def test_export_directory_creation_failure(self, mock_metrics, mock_claude_dir):
        mock_metrics.return_value = {}
        with mock.patch("pathlib.Path.mkdir", side_effect=OSError("Access denied")):
            with pytest.raises(ExportError) as exc:
                analytics.export_analytics("json", mock_claude_dir)
            assert "Failed to create exports directory" in str(exc.value)

# --------------------------------------------------------------------------- get_correlation_matrix

class TestGetCorrelationMatrix:
    @mock.patch("claude_ctx_py.metrics.get_metrics_path")
    @mock.patch("claude_ctx_py.analytics.safe_load_json")
    def test_correlation_calculation(self, mock_load, mock_path, sample_activations_data, mock_claude_dir):
        mock_path.return_value = mock_claude_dir / ".metrics" / "skills"
        # Mock file existence
        activations_path = mock_claude_dir / ".metrics" / "skills" / "activations.json"
        activations_path.parent.mkdir(parents=True, exist_ok=True)
        activations_path.touch()
        
        mock_load.return_value = sample_activations_data
        
        matrix = analytics.get_correlation_matrix({})
        
        # skill-a used 2 times, skill-b used 1 time
        # co-occurrence = 2 (counted bidirectionally from both events)
        # Union = 2 + 1 - 2 = 1
        # Jaccard = 2/1 = 2.0
        assert "skill-a" in matrix
        assert "skill-b" in matrix["skill-a"]
        assert matrix["skill-a"]["skill-b"] == 2.0

    @mock.patch("claude_ctx_py.metrics.get_metrics_path")
    def test_correlation_missing_file(self, mock_path, mock_claude_dir):
        mock_path.return_value = mock_claude_dir / "missing"
        matrix = analytics.get_correlation_matrix({})
        assert matrix == {}

# --------------------------------------------------------------------------- helpers

class TestHelpers:
    def test_calculate_efficiency_ratio(self, mock_claude_dir, sample_activations_data):
        activations_path = mock_claude_dir / ".metrics" / "skills" / "activations.json"
        activations_path.parent.mkdir(parents=True, exist_ok=True)
        activations_path.write_text(json.dumps(sample_activations_data))
        
        ratio = analytics._calculate_efficiency_ratio("skill-a", mock_claude_dir)
        # skill-a used twice: (500+500)/(1000+1000) = 0.5
        assert ratio == 0.5

    def test_calculate_efficiency_ratio_no_file(self, mock_claude_dir):
        ratio = analytics._calculate_efficiency_ratio("skill-a", mock_claude_dir)
        assert ratio == 1.0

    def test_count_activations_in_period(self, mock_claude_dir, sample_activations_data):
        activations_path = mock_claude_dir / ".metrics" / "skills" / "activations.json"
        activations_path.parent.mkdir(parents=True, exist_ok=True)
        activations_path.write_text(json.dumps(sample_activations_data))
        
        count = analytics._count_activations_in_period("skill-a", 7, mock_claude_dir)
        assert count == 2
        
        # Future date shouldn't count
        # (Though sample data is 'now', so it should count unless we look very far back?)
        # Logic: timestamp >= cutoff. cutoff = now - days.
        # So 'now' is always >= cutoff.
        
        # Test expired data
        old_data = {"activations": [{
            "skill_name": "skill-a",
            "timestamp": "2000-01-01T00:00:00Z"
        }]}
        activations_path.write_text(json.dumps(old_data))
        count_old = analytics._count_activations_in_period("skill-a", 7, mock_claude_dir)
        assert count_old == 0

# --------------------------------------------------------------------------- get_impact_report

class TestGetImpactReport:
    @mock.patch("claude_ctx_py.metrics.get_all_metrics")
    @mock.patch("claude_ctx_py.metrics.get_skill_metrics")
    def test_impact_report_valid(self, mock_skill, mock_all, sample_metrics_data, mock_claude_dir):
        mock_all.return_value = sample_metrics_data
        mock_skill.return_value = sample_metrics_data["skill-high-value"]
        
        report = analytics.get_impact_report("skill-high-value", mock_claude_dir)
        assert report["skill_name"] == "skill-high-value"
        assert "basic_metrics" in report
        assert "roi" in report
        assert "effectiveness_score" in report
        assert "trends" in report

    @mock.patch("claude_ctx_py.metrics.get_all_metrics")
    @mock.patch("claude_ctx_py.metrics.get_skill_metrics")
    def test_impact_report_missing_skill(self, mock_skill, mock_all, sample_metrics_data, mock_claude_dir):
        mock_all.return_value = sample_metrics_data
        mock_skill.return_value = None
        
        report = analytics.get_impact_report("missing", mock_claude_dir)
        assert "error" in report
        assert report["skill_name"] == "missing"
