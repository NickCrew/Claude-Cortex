"""Type definitions for the TUI tour system."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, List, Optional, TypedDict


@dataclass
class TourStep:
    """Definition of a single tour step.

    Attributes:
        id: Unique identifier for the step.
        title: Short title for the step.
        description: Detailed description/explanation.
        target_widget: Widget ID to highlight (optional).
        target_view: View to switch to before showing step (optional).
        position: Tooltip position relative to target.
        action_hint: Optional hint about what action to take.
        on_enter: Optional callback when step is entered.
        on_exit: Optional callback when step is exited.
    """

    id: str
    title: str
    description: str
    target_widget: Optional[str] = None
    target_view: Optional[str] = None
    position: str = "center"  # center, top, bottom, left, right
    action_hint: Optional[str] = None
    on_enter: Optional[Callable[[], None]] = None
    on_exit: Optional[Callable[[], None]] = None


@dataclass
class TourDefinition:
    """Definition of a complete tour.

    Attributes:
        id: Unique identifier for the tour.
        name: Human-readable name.
        description: What the tour covers.
        steps: List of tour steps.
        estimated_minutes: Estimated time to complete.
    """

    id: str
    name: str
    description: str
    steps: List[TourStep] = field(default_factory=list)
    estimated_minutes: int = 5

    def __len__(self) -> int:
        """Return number of steps in the tour."""
        return len(self.steps)

    def get_step(self, index: int) -> Optional[TourStep]:
        """Get step by index, or None if out of bounds."""
        if 0 <= index < len(self.steps):
            return self.steps[index]
        return None


class TourState(TypedDict, total=False):
    """Persisted tour state.

    Attributes:
        completed_tours: List of tour IDs that have been completed.
        skipped_tours: List of tour IDs that have been skipped.
        show_tour_on_startup: Whether to offer tour on TUI startup.
        last_tour_offer: ISO timestamp of last tour offer.
    """

    completed_tours: List[str]
    skipped_tours: List[str]
    show_tour_on_startup: bool
    last_tour_offer: Optional[str]
