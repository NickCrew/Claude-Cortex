"""Unit tests for the SkillRatingPromptManager."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

import pytest

from claude_ctx_py import metrics
from claude_ctx_py.skill_rating_prompts import SkillRatingPromptManager
from claude_ctx_py.skill_rating import SkillRatingCollector


@pytest.mark.unit
class TestSkillRatingPrompts:
    def test_detects_prompt_from_recent_activation(self, mock_claude_home) -> None:
        """A recent activation should produce a pending prompt."""
        metrics.record_activation("skill-alpha", 120, True)

        manager = SkillRatingPromptManager()
        prompts = manager.detect_due_prompts()

        assert len(prompts) == 1
        assert prompts[0].skill == "skill-alpha"

    def test_respects_prompt_cooldown(self, mock_claude_home) -> None:
        """Skills acknowledged within the cooldown window should not re-prompt."""
        metrics.record_activation("skill-beta", 50, True)

        manager = SkillRatingPromptManager()
        manager.mark_prompted("skill-beta")

        refreshed = SkillRatingPromptManager()
        assert refreshed.detect_due_prompts() == []

    def test_skips_recently_rated_skills_until_more_usage(self, mock_claude_home) -> None:
        """Skills rated within the freshness window require multiple new uses."""
        metrics.record_activation("skill-gamma", 30, True)

        collector = SkillRatingCollector()
        collector.record_rating(
            skill="skill-gamma",
            stars=5,
            helpful=True,
            task_succeeded=True,
        )

        refreshed = SkillRatingPromptManager()
        assert refreshed.detect_due_prompts() == []

    def test_prompts_after_multiple_uses_following_recent_rating(self, mock_claude_home) -> None:
        """After enough new activations, the skill should prompt again."""
        metrics.record_activation("skill-delta", 30, True)

        collector = SkillRatingCollector()
        collector.record_rating(
            skill="skill-delta",
            stars=4,
            helpful=True,
            task_succeeded=True,
        )

        manager = SkillRatingPromptManager()
        old_timestamp = (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()
        state = manager._load_state()
        state.setdefault("last_prompted", {})["skill-delta"] = old_timestamp
        state.setdefault("last_rated", {})["skill-delta"] = old_timestamp
        manager._save_state()

        for _ in range(3):
            metrics.record_activation("skill-delta", 10, True)

        refreshed = SkillRatingPromptManager()
        prompts = refreshed.detect_due_prompts()

        assert prompts and prompts[0].skill == "skill-delta"

    def test_metrics_fallback_when_activation_log_missing(self, mock_claude_home) -> None:
        """If the activation log is missing, summary metrics should drive prompts."""
        activations_path = metrics.get_metrics_path() / "activations.json"
        if activations_path.exists():
            activations_path.unlink()

        stats_path = metrics.get_metrics_path() / "stats.json"
        recent = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
        stats_path.write_text(
            json.dumps(
                {
                    "skills": {
                        "fallback-skill": {
                            "activation_count": 1,
                            "total_tokens_saved": 0,
                            "avg_tokens": 0,
                            "success_rate": 1.0,
                            "last_activated": recent,
                        }
                    }
                },
                indent=2,
            ),
            encoding="utf-8",
        )

        manager = SkillRatingPromptManager()
        prompts = manager.detect_due_prompts()

        assert prompts and prompts[0].skill == "fallback-skill"
