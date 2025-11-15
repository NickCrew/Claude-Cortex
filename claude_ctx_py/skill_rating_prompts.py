"""Auto-prompt orchestration for collecting skill ratings."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from .core.base import _resolve_claude_dir
from . import metrics
from .skill_rating import SkillRatingCollector, SkillRating


def _parse_timestamp(value: Optional[str]) -> Optional[datetime]:
    """Parse ISO timestamps that may end with 'Z'."""

    if not value:
        return None

    try:
        normalized = value.replace("Z", "+00:00")
        return datetime.fromisoformat(normalized)
    except (ValueError, TypeError):
        return None


@dataclass
class RatingPrompt:
    """Pending rating that should be surfaced to the user."""

    skill: str
    reason: str
    last_used: datetime
    usage_count: int
    success_rate: Optional[float] = None
    task_types: Optional[List[str]] = None


class SkillRatingPromptManager:
    """Detect which skills should prompt the user for ratings."""

    PROMPT_COOLDOWN_HOURS = 24
    RATING_FRESHNESS_DAYS = 14
    ACTIVATION_LOOKBACK_HOURS = 12

    def __init__(self, home: Path | None = None):
        self.home = _resolve_claude_dir(home)
        self.state_path = self.home / "data" / "skill-rating-prompts.json"
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self.collector: Optional[SkillRatingCollector] = None
        self._state: Optional[Dict[str, Any]] = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def detect_due_prompts(self, limit: int = 3) -> List[RatingPrompt]:
        """Return up to `limit` skills that should be rated."""

        usage_map = self._gather_recent_usage()
        if not usage_map:
            return []

        prompts: List[RatingPrompt] = []
        for skill, info in usage_map.items():
            if not self._should_prompt(skill, info):
                continue

            reason = self._build_reason(info)
            prompt = RatingPrompt(
                skill=skill,
                reason=reason,
                last_used=info["last_used"],
                usage_count=info["count"],
                success_rate=info.get("success_rate"),
                task_types=sorted(info["task_types"])
                if info.get("task_types")
                else None,
            )
            prompts.append(prompt)

        prompts.sort(key=lambda p: p.last_used, reverse=True)
        return prompts[:limit]

    def mark_prompted(self, skill: str) -> None:
        """Record that a prompt was shown for a skill."""

        state = self._load_state()
        state.setdefault("last_prompted", {})[skill] = self._now_iso()
        self._save_state()

    def mark_snoozed(self, skill: str) -> None:
        """Treat a dismissal as a regular prompt to enforce cooldown."""

        self.mark_prompted(skill)

    def mark_rated(self, skill: str) -> None:
        """Record that a skill was rated to avoid duplicate prompts."""

        state = self._load_state()
        iso = self._now_iso()
        state.setdefault("last_prompted", {})[skill] = iso
        state.setdefault("last_rated", {})[skill] = iso
        self._save_state()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _gather_recent_usage(self) -> Dict[str, Dict[str, Any]]:
        """Aggregate activation data within the lookback window."""

        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(hours=self.ACTIVATION_LOOKBACK_HOURS)
        usage: Dict[str, Dict[str, Any]] = {}

        # Detailed activations provide best signal when available
        detailed = self._load_activation_log()
        for activation in detailed:
            skill = activation.get("skill_name")
            if not skill:
                continue

            ts = _parse_timestamp(activation.get("timestamp"))
            if not ts or ts < cutoff:
                continue

            info = usage.setdefault(
                skill,
                {
                    "count": 0,
                    "last_used": ts,
                    "successes": [],
                    "task_types": set(),
                },
            )
            info["count"] += 1
            if ts > info["last_used"]:
                info["last_used"] = ts

            success = activation.get("metrics", {}).get("success")
            if success is not None:
                info["successes"].append(bool(success))

            task_type = activation.get("context", {}).get("task_type")
            if task_type:
                info["task_types"].add(task_type)

        # Fallback to summarized metrics to ensure recent usage still prompts
        if not usage:
            summarized = metrics.get_all_metrics()
            for skill, data in summarized.items():
                last_activated = _parse_timestamp(data.get("last_activated"))
                if not last_activated or last_activated < cutoff:
                    continue
                usage[skill] = {
                    "count": 1,
                    "last_used": last_activated,
                    "successes": [data.get("success_rate", 0.0) >= 0.5],
                    "task_types": set(),
                }

        for info in usage.values():
            successes = info.get("successes", [])
            if successes:
                info["success_rate"] = sum(1 for s in successes if s) / len(successes)
            else:
                info["success_rate"] = None

        return usage

    def _load_activation_log(self) -> List[Dict[str, Any]]:
        path = metrics.get_metrics_path() / "activations.json"
        if not path.exists():
            return []
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return []

        activations = raw.get("activations", [])
        if not isinstance(activations, list):
            return []

        # Keep the newest ~200 entries to limit processing time
        return activations[-200:]

    def _should_prompt(self, skill: str, usage_info: Dict[str, Any]) -> bool:
        if usage_info.get("count", 0) == 0:
            return False

        now = datetime.now(timezone.utc)
        last_prompted = _parse_timestamp(
            self._load_state().get("last_prompted", {}).get(skill)
        )
        if last_prompted and now - last_prompted < timedelta(
            hours=self.PROMPT_COOLDOWN_HOURS
        ):
            return False

        rating = self._get_user_rating(skill)
        if rating:
            if now - rating.timestamp < timedelta(days=self.RATING_FRESHNESS_DAYS):
                # Recently rated – only prompt if there were multiple uses since
                if usage_info.get("count", 0) < 3:
                    return False

        return True

    def _build_reason(self, usage_info: Dict[str, Any]) -> str:
        count = usage_info.get("count", 0)
        last_used = usage_info.get("last_used")
        success_rate = usage_info.get("success_rate")
        task_types = usage_info.get("task_types") or []

        parts = [f"Used {count} time{'s' if count != 1 else ''} recently"]
        if task_types:
            sample = ", ".join(sorted(task_types))
            parts.append(f"Tasks: {sample}")
        if success_rate is not None:
            parts.append(f"Success rate {success_rate * 100:.0f}%")
        if isinstance(last_used, datetime):
            elapsed = datetime.now(timezone.utc) - last_used
            hours = max(1, int(elapsed.total_seconds() // 3600))
            parts.append(f"Last used ~{hours}h ago")
        return " · ".join(parts)

    def _get_user_rating(self, skill: str) -> Optional[SkillRating]:
        collector = self._get_collector()
        if not collector:
            return None
        try:
            return collector.get_user_rating(skill)
        except Exception:
            return None

    def _get_collector(self) -> Optional[SkillRatingCollector]:
        if self.collector is not None:
            return self.collector
        try:
            self.collector = SkillRatingCollector(home=self.home)
        except Exception:
            self.collector = None
        return self.collector

    def _load_state(self) -> Dict[str, Any]:
        if self._state is not None:
            return self._state
        if not self.state_path.exists():
            self._state = {}
            return self._state
        try:
            self._state = json.loads(self.state_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            self._state = {}
        return self._state

    def _save_state(self) -> None:
        if self._state is None:
            return
        try:
            self.state_path.write_text(
                json.dumps(self._state, indent=2, sort_keys=True), encoding="utf-8"
            )
        except OSError:
            pass

    def _now_iso(self) -> str:
        return datetime.now(timezone.utc).isoformat()

