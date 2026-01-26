"""TUI Tour System for guided onboarding.

This package provides an interactive tour system for the Cortex TUI,
helping new users understand key features through spotlight highlighting
and step-by-step guidance.
"""

from .types import TourStep, TourDefinition, TourState
from .manager import TourManager
from .overlay import TourOverlay
from .definitions import QUICK_TOUR, get_tour_by_id

__all__ = [
    "TourStep",
    "TourDefinition",
    "TourState",
    "TourManager",
    "TourOverlay",
    "QUICK_TOUR",
    "get_tour_by_id",
]
