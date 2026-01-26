"""Tour definitions for the TUI.

This module contains predefined tours that guide users through
Cortex features.
"""

from __future__ import annotations

from typing import Dict, Optional

from .types import TourDefinition, TourStep


# Quick Tour - 5 steps covering key features
QUICK_TOUR = TourDefinition(
    id="quick_tour",
    name="Quick Tour",
    description="A quick introduction to Cortex TUI's key features",
    estimated_minutes=3,
    steps=[
        TourStep(
            id="welcome",
            title="Welcome to Cortex",
            description=(
                "Cortex enhances Claude Code with reusable rules, modes, "
                "agents, and skills.\n\n"
                "This quick tour will show you the key features. "
                "You can navigate using:\n"
                "  * [n] Next step\n"
                "  * [p] Previous step\n"
                "  * [q] Quit tour\n\n"
                "Let's get started!"
            ),
            position="center",
            action_hint="Press [n] to continue",
        ),
        TourStep(
            id="agents_view",
            title="Agents View",
            description=(
                "Agents are specialized Claude personas that excel at "
                "specific tasks.\n\n"
                "Key features:\n"
                "  * Toggle agents with [Space]\n"
                "  * View details with [Enter]\n"
                "  * Agents activate instantly in Claude Code\n\n"
                "Active agents appear with a checkmark and are included "
                "in your context."
            ),
            target_view="agents",
            target_widget="main-table",
            position="right",
            action_hint="Press [2] to switch to Agents view anytime",
        ),
        TourStep(
            id="profiles_view",
            title="Profiles",
            description=(
                "Profiles are quick configuration presets that activate "
                "groups of agents.\n\n"
                "Available profiles:\n"
                "  * minimal - Essential agents only\n"
                "  * frontend - React, Vue, TypeScript\n"
                "  * backend - Python, Go, APIs\n"
                "  * full - All agents enabled\n\n"
                "Apply a profile with [Space] to instantly configure "
                "your environment."
            ),
            target_view="profiles",
            target_widget="main-table",
            position="right",
            action_hint="Press [8] to switch to Profiles view",
        ),
        TourStep(
            id="ai_assistant",
            title="AI Assistant",
            description=(
                "The AI Assistant provides intelligent recommendations "
                "based on your project.\n\n"
                "Features:\n"
                "  * Suggests relevant agents for your codebase\n"
                "  * Auto-activate recommendations with [a]\n"
                "  * Get task-specific suggestions\n\n"
                "This uses semantic analysis to match your project "
                "with the best agents."
            ),
            target_view="ai_assistant",
            target_widget="main-table",
            position="right",
            action_hint="Press [0] to access AI Assistant",
        ),
        TourStep(
            id="export",
            title="Export & Next Steps",
            description=(
                "Export your context for sharing or documentation.\n\n"
                "Export options:\n"
                "  * Toggle categories with [Space]\n"
                "  * Cycle formats with [f] (MD/JSON/YAML)\n"
                "  * Copy to clipboard with [x]\n"
                "  * Execute export with [e]\n\n"
                "That completes the quick tour! Press [?] anytime "
                "for keyboard shortcuts.\n\n"
                "Happy coding with Cortex!"
            ),
            target_view="export",
            target_widget="main-table",
            position="right",
            action_hint="Press [9] to access Export view",
        ),
    ],
)


# Registry of all available tours
AVAILABLE_TOURS: Dict[str, TourDefinition] = {
    "quick_tour": QUICK_TOUR,
}


def get_tour_by_id(tour_id: str) -> Optional[TourDefinition]:
    """Get a tour definition by ID.

    Args:
        tour_id: ID of the tour to retrieve.

    Returns:
        TourDefinition if found, None otherwise.
    """
    return AVAILABLE_TOURS.get(tour_id)


def list_available_tours() -> Dict[str, TourDefinition]:
    """Get all available tour definitions.

    Returns:
        Dictionary of tour ID to TourDefinition.
    """
    return dict(AVAILABLE_TOURS)
