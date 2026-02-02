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
                "Cortex enhances Claude Code with reusable rules, "
                "agents, skills, and MCP servers.\n\n"
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
            id="rules_view",
            title="Rules View",
            description=(
                "Rules define constraints and guidelines for Claude.\n\n"
                "Key features:\n"
                "  * Toggle rules with [Space]\n"
                "  * View and edit with [Enter] or [Ctrl+e]\n"
                "  * Active rules are enforced in Claude Code\n\n"
                "Rules help maintain consistency and quality "
                "in your codebase."
            ),
            target_view="rules",
            target_widget="main-table",
            position="right",
            action_hint="Press [3] to switch to Rules view",
        ),
        TourStep(
            id="skills_view",
            title="Skills View",
            description=(
                "Skills are reusable workflows invoked with slash commands.\n\n"
                "Key features:\n"
                "  * Browse available skills\n"
                "  * View skill details with [Enter]\n"
                "  * Skills are invoked via /skill-name in Claude Code\n\n"
                "Skills extend Claude's capabilities with specialized workflows."
            ),
            target_view="skills",
            target_widget="main-table",
            position="right",
            action_hint="Press [4] to switch to Skills view",
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
            action_hint="Press [E] to access Export view",
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
