"""Tests for the TUI tour system.

Tests cover:
- TourStep and TourDefinition types
- TourManager state persistence
- Tour definitions
"""

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from claude_ctx_py.tui.tour import (
    TourStep,
    TourDefinition,
    TourState,
    TourManager,
    QUICK_TOUR,
    get_tour_by_id,
)


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def tmp_state_path(tmp_path):
    """Create a temporary state file path."""
    return tmp_path / "tour-state.json"


@pytest.fixture
def tour_manager(tmp_state_path):
    """Create a TourManager with temporary state path."""
    return TourManager(state_path=tmp_state_path)


# =============================================================================
# Tests: TourStep
# =============================================================================


class TestTourStep:
    """Tests for TourStep dataclass."""

    def test_minimal_step(self):
        """TourStep should work with minimal required fields."""
        step = TourStep(
            id="test",
            title="Test Step",
            description="Test description",
        )

        assert step.id == "test"
        assert step.title == "Test Step"
        assert step.description == "Test description"
        assert step.target_widget is None
        assert step.target_view is None
        assert step.position == "center"
        assert step.action_hint is None

    def test_full_step(self):
        """TourStep should accept all fields."""
        step = TourStep(
            id="test",
            title="Test Step",
            description="Test description",
            target_widget="main-table",
            target_view="agents",
            position="right",
            action_hint="Press Enter",
        )

        assert step.target_widget == "main-table"
        assert step.target_view == "agents"
        assert step.position == "right"
        assert step.action_hint == "Press Enter"


# =============================================================================
# Tests: TourDefinition
# =============================================================================


class TestTourDefinition:
    """Tests for TourDefinition dataclass."""

    def test_empty_tour(self):
        """TourDefinition should work with no steps."""
        tour = TourDefinition(
            id="empty",
            name="Empty Tour",
            description="A tour with no steps",
        )

        assert len(tour) == 0
        assert tour.get_step(0) is None

    def test_tour_with_steps(self):
        """TourDefinition should handle steps correctly."""
        steps = [
            TourStep(id="step1", title="Step 1", description="First step"),
            TourStep(id="step2", title="Step 2", description="Second step"),
        ]
        tour = TourDefinition(
            id="test",
            name="Test Tour",
            description="A test tour",
            steps=steps,
        )

        assert len(tour) == 2
        assert tour.get_step(0).id == "step1"
        assert tour.get_step(1).id == "step2"
        assert tour.get_step(2) is None

    def test_estimated_minutes(self):
        """TourDefinition should have estimated_minutes field."""
        tour = TourDefinition(
            id="test",
            name="Test",
            description="Test",
            estimated_minutes=10,
        )
        assert tour.estimated_minutes == 10


# =============================================================================
# Tests: TourManager
# =============================================================================


class TestTourManager:
    """Tests for TourManager class."""

    def test_default_state(self, tour_manager):
        """TourManager should have default state on first creation."""
        assert tour_manager.completed_tours == []
        assert tour_manager.skipped_tours == []
        assert tour_manager.show_tour_on_startup is True

    def test_mark_tour_completed(self, tour_manager, tmp_state_path):
        """TourManager should mark tours as completed."""
        result = tour_manager.mark_tour_completed("quick_tour")

        assert result is True
        assert tour_manager.is_tour_completed("quick_tour")
        assert tmp_state_path.exists()

    def test_mark_tour_skipped(self, tour_manager, tmp_state_path):
        """TourManager should mark tours as skipped."""
        result = tour_manager.mark_tour_skipped("quick_tour")

        assert result is True
        assert tour_manager.is_tour_skipped("quick_tour")

    def test_completed_removes_from_skipped(self, tour_manager):
        """Completing a tour should remove it from skipped list."""
        tour_manager.mark_tour_skipped("quick_tour")
        assert tour_manager.is_tour_skipped("quick_tour")

        tour_manager.mark_tour_completed("quick_tour")
        assert tour_manager.is_tour_completed("quick_tour")
        assert not tour_manager.is_tour_skipped("quick_tour")

    def test_should_offer_tour_default(self, tour_manager):
        """should_offer_tour should return True by default."""
        assert tour_manager.should_offer_tour("quick_tour") is True

    def test_should_not_offer_completed_tour(self, tour_manager):
        """should_offer_tour should return False for completed tours."""
        tour_manager.mark_tour_completed("quick_tour")
        assert tour_manager.should_offer_tour("quick_tour") is False

    def test_should_not_offer_skipped_tour(self, tour_manager):
        """should_offer_tour should return False for skipped tours."""
        tour_manager.mark_tour_skipped("quick_tour")
        assert tour_manager.should_offer_tour("quick_tour") is False

    def test_should_not_offer_when_disabled(self, tour_manager):
        """should_offer_tour should return False when disabled."""
        tour_manager.set_show_on_startup(False)
        assert tour_manager.should_offer_tour("quick_tour") is False

    def test_set_show_on_startup(self, tour_manager):
        """set_show_on_startup should update state."""
        tour_manager.set_show_on_startup(False)
        assert tour_manager.show_tour_on_startup is False

        tour_manager.set_show_on_startup(True)
        assert tour_manager.show_tour_on_startup is True

    def test_reset_state(self, tour_manager):
        """reset_state should restore defaults."""
        tour_manager.mark_tour_completed("quick_tour")
        tour_manager.set_show_on_startup(False)

        tour_manager.reset_state()

        assert tour_manager.completed_tours == []
        assert tour_manager.show_tour_on_startup is True

    def test_load_existing_state(self, tmp_state_path):
        """TourManager should load existing state from file."""
        state_data = {
            "completed_tours": ["quick_tour"],
            "skipped_tours": [],
            "show_tour_on_startup": False,
            "last_tour_offer": "2024-01-01T00:00:00Z",
        }
        tmp_state_path.write_text(json.dumps(state_data))

        manager = TourManager(state_path=tmp_state_path)

        assert manager.is_tour_completed("quick_tour")
        assert manager.show_tour_on_startup is False


# =============================================================================
# Tests: Tour Definitions
# =============================================================================


class TestTourDefinitions:
    """Tests for predefined tours."""

    def test_quick_tour_exists(self):
        """QUICK_TOUR should be defined."""
        assert QUICK_TOUR is not None
        assert QUICK_TOUR.id == "quick_tour"

    def test_quick_tour_has_steps(self):
        """QUICK_TOUR should have steps."""
        assert len(QUICK_TOUR) > 0

    def test_quick_tour_steps_have_ids(self):
        """All QUICK_TOUR steps should have unique IDs."""
        ids = [step.id for step in QUICK_TOUR.steps]
        assert len(ids) == len(set(ids))  # All unique

    def test_quick_tour_estimated_time(self):
        """QUICK_TOUR should have reasonable estimated time."""
        assert 1 <= QUICK_TOUR.estimated_minutes <= 10

    def test_get_tour_by_id_returns_tour(self):
        """get_tour_by_id should return tour for valid ID."""
        tour = get_tour_by_id("quick_tour")
        assert tour is not None
        assert tour.id == "quick_tour"

    def test_get_tour_by_id_returns_none_for_invalid(self):
        """get_tour_by_id should return None for invalid ID."""
        tour = get_tour_by_id("nonexistent_tour")
        assert tour is None
