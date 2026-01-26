"""Tour state management and persistence."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from ...core.base import _resolve_cortex_root
from .types import TourState


class TourManager:
    """Manages tour state persistence and tracking.

    Handles:
    - Loading/saving tour completion state
    - Tracking completed and skipped tours
    - Determining if tour should be offered
    """

    @staticmethod
    def _default_state() -> TourState:
        """Get a fresh copy of default state."""
        return {
            "completed_tours": [],
            "skipped_tours": [],
            "show_tour_on_startup": True,
            "last_tour_offer": None,
        }

    def __init__(self, state_path: Optional[Path] = None):
        """Initialize the tour manager.

        Args:
            state_path: Path to state file. Defaults to ~/.cortex/tour-state.json.
        """
        if state_path is None:
            state_path = _resolve_cortex_root() / "tour-state.json"
        self._state_path = state_path
        self._state: TourState = self._load_state()

    def _load_state(self) -> TourState:
        """Load tour state from file."""
        if not self._state_path.exists():
            return self._default_state()

        try:
            data = json.loads(self._state_path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                # Merge with defaults to handle missing keys
                state: TourState = {
                    "completed_tours": data.get("completed_tours", []),
                    "skipped_tours": data.get("skipped_tours", []),
                    "show_tour_on_startup": data.get("show_tour_on_startup", True),
                    "last_tour_offer": data.get("last_tour_offer"),
                }
                return state
        except (json.JSONDecodeError, OSError):
            pass

        return dict(self.DEFAULT_STATE)

    def _save_state(self) -> bool:
        """Save tour state to file.

        Returns:
            True if saved successfully.
        """
        try:
            self._state_path.parent.mkdir(parents=True, exist_ok=True)
            self._state_path.write_text(
                json.dumps(self._state, indent=2) + "\n", encoding="utf-8"
            )
            return True
        except OSError:
            return False

    @property
    def completed_tours(self) -> List[str]:
        """Get list of completed tour IDs."""
        return self._state.get("completed_tours", [])

    @property
    def skipped_tours(self) -> List[str]:
        """Get list of skipped tour IDs."""
        return self._state.get("skipped_tours", [])

    @property
    def show_tour_on_startup(self) -> bool:
        """Whether to show tour offer on startup."""
        return self._state.get("show_tour_on_startup", True)

    def is_tour_completed(self, tour_id: str) -> bool:
        """Check if a tour has been completed."""
        return tour_id in self.completed_tours

    def is_tour_skipped(self, tour_id: str) -> bool:
        """Check if a tour has been skipped."""
        return tour_id in self.skipped_tours

    def should_offer_tour(self, tour_id: str = "quick_tour") -> bool:
        """Determine if tour should be offered to user.

        Returns True if:
        - Tour hasn't been completed
        - Tour hasn't been skipped
        - Show on startup is enabled
        """
        if not self.show_tour_on_startup:
            return False
        if self.is_tour_completed(tour_id):
            return False
        if self.is_tour_skipped(tour_id):
            return False
        return True

    def mark_tour_completed(self, tour_id: str) -> bool:
        """Mark a tour as completed.

        Args:
            tour_id: ID of the tour to mark.

        Returns:
            True if state was saved successfully.
        """
        completed = self._state.get("completed_tours", [])
        if tour_id not in completed:
            completed.append(tour_id)
            self._state["completed_tours"] = completed

        # Remove from skipped if present
        skipped = self._state.get("skipped_tours", [])
        if tour_id in skipped:
            skipped.remove(tour_id)
            self._state["skipped_tours"] = skipped

        return self._save_state()

    def mark_tour_skipped(self, tour_id: str) -> bool:
        """Mark a tour as skipped.

        Args:
            tour_id: ID of the tour to mark.

        Returns:
            True if state was saved successfully.
        """
        skipped = self._state.get("skipped_tours", [])
        if tour_id not in skipped:
            skipped.append(tour_id)
            self._state["skipped_tours"] = skipped

        return self._save_state()

    def set_show_on_startup(self, show: bool) -> bool:
        """Set whether to show tour offer on startup.

        Args:
            show: Whether to show tour offer.

        Returns:
            True if state was saved successfully.
        """
        self._state["show_tour_on_startup"] = show
        return self._save_state()

    def record_tour_offer(self) -> bool:
        """Record that a tour was offered.

        Returns:
            True if state was saved successfully.
        """
        self._state["last_tour_offer"] = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )
        return self._save_state()

    def reset_state(self) -> bool:
        """Reset tour state to defaults.

        Returns:
            True if state was saved successfully.
        """
        self._state = self._default_state()
        return self._save_state()
