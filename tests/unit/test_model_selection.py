"""Tests for model selection and cost optimization features."""

import pytest

from claude_ctx_py.intelligence.semantic import ModelSelector, CLAUDE_PRICING
from claude_ctx_py.analytics import calculate_llm_cost, CLAUDE_PRICING as ANALYTICS_PRICING


class TestModelSelector:
    """Test smart model selection logic."""

    def test_select_haiku_for_simple_task(self):
        """Should select Haiku for simple tasks with small context."""
        model, max_tokens = ModelSelector.select_model(
            context_size=1000,  # Small context
            agent_count=5,  # Few agents
            confidence_threshold=0.3,  # Low confidence needed
        )

        assert model == "claude-haiku-4-20250514"
        assert max_tokens == 512  # Smaller output

    def test_select_sonnet_for_standard_task(self):
        """Should select Sonnet for standard complexity tasks."""
        model, max_tokens = ModelSelector.select_model(
            context_size=3000,  # Medium context
            agent_count=15,  # Medium agent count
            confidence_threshold=0.5,  # Standard confidence
        )

        assert model == "claude-sonnet-4-20250514"
        assert max_tokens == 1024

    def test_select_opus_for_complex_task(self):
        """Should select Opus for complex tasks with large context."""
        model, max_tokens = ModelSelector.select_model(
            context_size=7000,  # Large context
            agent_count=40,  # Many agents
            confidence_threshold=0.9,  # High confidence needed
        )

        assert model == "claude-opus-4-20250514"
        assert max_tokens == 2048

    def test_calculate_haiku_cost(self):
        """Should calculate Haiku costs correctly."""
        cost = ModelSelector.calculate_cost(
            model="claude-haiku-4-20250514",
            input_tokens=1000,
            output_tokens=500,
        )

        # Haiku: $0.25/MTok input, $1.25/MTok output
        # 1000 tokens input = $0.00025
        # 500 tokens output = $0.000625
        # Total = $0.000875
        assert cost["input_cost"] == pytest.approx(0.00025, abs=0.000001)
        assert cost["output_cost"] == pytest.approx(0.000625, abs=0.000001)
        assert cost["total_cost"] == pytest.approx(0.000875, abs=0.000001)
        assert cost["model_name"] == "Haiku 4"
        assert "savings_vs_sonnet" in cost

    def test_calculate_sonnet_cost(self):
        """Should calculate Sonnet costs correctly."""
        cost = ModelSelector.calculate_cost(
            model="claude-sonnet-4-20250514",
            input_tokens=1000,
            output_tokens=500,
        )

        # Sonnet: $3/MTok input, $15/MTok output
        # 1000 tokens input = $0.003
        # 500 tokens output = $0.0075
        # Total = $0.0105
        assert cost["input_cost"] == pytest.approx(0.003, abs=0.000001)
        assert cost["output_cost"] == pytest.approx(0.0075, abs=0.000001)
        assert cost["total_cost"] == pytest.approx(0.0105, abs=0.000001)
        assert cost["model_name"] == "Sonnet 4"
        assert "savings_vs_sonnet" not in cost  # Baseline model

    def test_calculate_opus_cost(self):
        """Should calculate Opus costs correctly."""
        cost = ModelSelector.calculate_cost(
            model="claude-opus-4-20250514",
            input_tokens=1000,
            output_tokens=500,
        )

        # Opus: $15/MTok input, $75/MTok output
        # 1000 tokens input = $0.015
        # 500 tokens output = $0.0375
        # Total = $0.0525
        assert cost["input_cost"] == pytest.approx(0.015, abs=0.000001)
        assert cost["output_cost"] == pytest.approx(0.0375, abs=0.000001)
        assert cost["total_cost"] == pytest.approx(0.0525, abs=0.000001)
        assert cost["model_name"] == "Opus 4"

    def test_haiku_savings_calculation(self):
        """Should calculate savings when using Haiku vs Sonnet."""
        cost = ModelSelector.calculate_cost(
            model="claude-haiku-4-20250514",
            input_tokens=10000,
            output_tokens=5000,
        )

        # Haiku total: $0.00875
        # Sonnet would be: $0.105
        # Savings: ~$0.09625 (91.7% reduction)
        assert "savings_vs_sonnet" in cost
        assert cost["savings_vs_sonnet"] > 0
        assert cost["savings_percentage"] > 90  # >90% savings

    def test_pricing_consistency(self):
        """Pricing should be consistent between modules."""
        # Check all models exist in both pricing dictionaries
        assert set(CLAUDE_PRICING.keys()) == set(ANALYTICS_PRICING.keys())

        # Check prices match
        for model in CLAUDE_PRICING:
            assert CLAUDE_PRICING[model]["input"] == ANALYTICS_PRICING[model]["input"]
            assert CLAUDE_PRICING[model]["output"] == ANALYTICS_PRICING[model]["output"]


class TestAnalyticsCostCalculation:
    """Test cost calculation in analytics module."""

    def test_calculate_llm_cost_haiku(self):
        """Should calculate Haiku costs in analytics module."""
        cost = calculate_llm_cost(
            model="claude-haiku-4-20250514",
            input_tokens=2000,
            output_tokens=1000,
        )

        assert cost["input_cost"] == pytest.approx(0.0005, abs=0.000001)
        assert cost["output_cost"] == pytest.approx(0.00125, abs=0.000001)
        assert cost["total_cost"] == pytest.approx(0.00175, abs=0.000001)

    def test_calculate_llm_cost_sonnet(self):
        """Should calculate Sonnet costs in analytics module."""
        cost = calculate_llm_cost(
            model="claude-sonnet-4-20250514",
            input_tokens=2000,
            output_tokens=1000,
        )

        assert cost["input_cost"] == pytest.approx(0.006, abs=0.000001)
        assert cost["output_cost"] == pytest.approx(0.015, abs=0.000001)
        assert cost["total_cost"] == pytest.approx(0.021, abs=0.000001)

    def test_unknown_model_defaults_to_sonnet(self):
        """Should default to Sonnet pricing for unknown models."""
        cost = calculate_llm_cost(
            model="unknown-model",
            input_tokens=1000,
            output_tokens=500,
        )

        # Should use Sonnet pricing as fallback
        assert cost["total_cost"] == pytest.approx(0.0105, abs=0.000001)


class TestCostOptimizationScenarios:
    """Test real-world cost optimization scenarios."""

    def test_typical_agent_recommendation_haiku(self):
        """Typical agent recommendation should use Haiku and be cheap."""
        # Typical scenario: Small context, few agents, simple recommendation
        model, max_tokens = ModelSelector.select_model(
            context_size=1500,  # ~375 tokens
            agent_count=10,
            confidence_threshold=0.5,
        )

        # Should select Haiku
        assert model == "claude-haiku-4-20250514"

        # Estimate cost for typical usage
        # Input: ~400 tokens (context + system)
        # Output: ~200 tokens (recommendations)
        cost = ModelSelector.calculate_cost(
            model=model, input_tokens=400, output_tokens=200
        )

        # Should be very cheap (< $0.001)
        assert cost["total_cost"] < 0.001
        print(f"Typical recommendation cost: ${cost['total_cost']:.6f}")

    def test_complex_analysis_opus(self):
        """Complex analysis should use Opus when needed."""
        # Complex scenario: Large context, many agents, high confidence
        model, max_tokens = ModelSelector.select_model(
            context_size=8000,  # ~2000 tokens
            agent_count=50,
            confidence_threshold=0.9,
        )

        # Should select Opus
        assert model == "claude-opus-4-20250514"

    def test_cost_comparison_across_models(self):
        """Compare costs across all models for same workload."""
        input_tokens = 1000
        output_tokens = 500

        haiku_cost = ModelSelector.calculate_cost(
            "claude-haiku-4-20250514", input_tokens, output_tokens
        )
        sonnet_cost = ModelSelector.calculate_cost(
            "claude-sonnet-4-20250514", input_tokens, output_tokens
        )
        opus_cost = ModelSelector.calculate_cost(
            "claude-opus-4-20250514", input_tokens, output_tokens
        )

        # Verify cost hierarchy
        assert haiku_cost["total_cost"] < sonnet_cost["total_cost"]
        assert sonnet_cost["total_cost"] < opus_cost["total_cost"]

        # Haiku should be 10-12x cheaper than Sonnet
        savings_multiplier = (
            sonnet_cost["total_cost"] / haiku_cost["total_cost"]
        )
        assert 10 <= savings_multiplier <= 13

        print(f"\nCost Comparison (1K input + 500 output tokens):")
        print(f"Haiku:  ${haiku_cost['total_cost']:.6f}")
        print(f"Sonnet: ${sonnet_cost['total_cost']:.6f}")
        print(f"Opus:   ${opus_cost['total_cost']:.6f}")
        print(f"Haiku is {savings_multiplier:.1f}x cheaper than Sonnet")

    def test_monthly_savings_estimate(self):
        """Estimate monthly savings with Haiku for typical usage."""
        # Assume: 100 agent recommendations per month
        # Typical: 500 input tokens, 200 output tokens each

        recommendations_per_month = 100
        input_per_rec = 500
        output_per_rec = 200

        # Cost if always using Sonnet (old behavior)
        sonnet_monthly = sum(
            ModelSelector.calculate_cost(
                "claude-sonnet-4-20250514", input_per_rec, output_per_rec
            )["total_cost"]
            for _ in range(recommendations_per_month)
        )

        # Cost with smart selection (assume 80% Haiku, 20% Sonnet)
        haiku_count = int(recommendations_per_month * 0.8)
        sonnet_count = int(recommendations_per_month * 0.2)

        haiku_monthly = sum(
            ModelSelector.calculate_cost(
                "claude-haiku-4-20250514", input_per_rec, output_per_rec
            )["total_cost"]
            for _ in range(haiku_count)
        )

        sonnet_smart_monthly = sum(
            ModelSelector.calculate_cost(
                "claude-sonnet-4-20250514", input_per_rec, output_per_rec
            )["total_cost"]
            for _ in range(sonnet_count)
        )

        smart_monthly = haiku_monthly + sonnet_smart_monthly
        savings = sonnet_monthly - smart_monthly
        savings_pct = (savings / sonnet_monthly) * 100

        print(f"\nMonthly Cost Estimate (100 recommendations):")
        print(f"Always Sonnet: ${sonnet_monthly:.2f}")
        print(f"Smart Selection (80% Haiku): ${smart_monthly:.2f}")
        print(f"Monthly Savings: ${savings:.2f} ({savings_pct:.1f}%)")

        # Should save at least 70% with smart selection
        assert savings_pct > 70


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
