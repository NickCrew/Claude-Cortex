"""SkillPickerScreen — reusable per-skill checkbox picker grouped by category.

Returns a list of selected skill slugs (empty list if cancelled).
Used by ``cortex project init --pick`` and any TUI flow that needs the user
to select a subset of available skills.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional, Tuple

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Button, Checkbox, Static

from ...tui_icons import Icons


class SkillPickerScreen(ModalScreen[Optional[List[str]]]):
    """Checkbox list of skills grouped by category; returns selected slugs."""

    CSS = """
    SkillPickerScreen {
        align: center middle;
    }

    SkillPickerScreen #dialog {
        width: 80;
        max-width: 95%;
        max-height: 80%;
        padding: 1 2;
        background: $surface;
        border: thick $primary;
        opacity: 1;
    }

    SkillPickerScreen #dialog-title {
        text-align: center;
        text-style: bold;
        padding-bottom: 1;
    }

    SkillPickerScreen #dialog-hint {
        color: $text-muted;
        padding: 0 0 1 0;
    }

    SkillPickerScreen #skill-list {
        height: auto;
        max-height: 50;
        padding: 0 0 1 0;
    }

    SkillPickerScreen .category-header {
        text-style: bold;
        color: $accent;
        padding: 1 0 0 0;
    }

    SkillPickerScreen .skill-row {
        padding: 0;
    }

    SkillPickerScreen #dialog-buttons {
        width: 100%;
        align: center middle;
        padding-top: 1;
    }
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("enter", "confirm", "Confirm"),
    ]

    def __init__(
        self,
        skills_by_category: List[Tuple[str, List[Tuple[str, str]]]],
        pre_selected: Optional[List[str]] = None,
    ) -> None:
        """Initialise the picker.

        Args:
            skills_by_category: List of (category_name, [(slug, display_name), ...]).
            pre_selected: Slugs that should be checked by default.
        """
        super().__init__()
        self.skills_by_category = skills_by_category
        self.pre_selected: set[str] = set(pre_selected or [])

    def compose(self) -> ComposeResult:
        """Compose the picker dialog."""
        with Container(id="dialog", classes="visible"):
            with Vertical():
                yield Static(
                    f"{Icons.CODE} [bold]Select Skills[/bold]",
                    id="dialog-title",
                )
                yield Static(
                    "[dim]Space to toggle • Enter to confirm • Esc to cancel[/dim]",
                    id="dialog-hint",
                )

                with VerticalScroll(id="skill-list"):
                    for category, skills in self.skills_by_category:
                        if not skills:
                            continue
                        yield Static(
                            f"[bold]{category}[/bold]",
                            classes="category-header",
                        )
                        for slug, display in skills:
                            # Sanitise slug for use as widget id (replace non-alnum)
                            safe_id = f"pick-{slug.replace('.', '-').replace('/', '-')}"
                            yield Checkbox(
                                display,
                                value=slug in self.pre_selected,
                                id=safe_id,
                                classes="skill-row",
                            )

                with Horizontal(id="dialog-buttons"):
                    yield Button("Confirm", variant="primary", id="confirm")
                    yield Button("Cancel", variant="default", id="cancel")

    def action_cancel(self) -> None:
        self.dismiss(None)

    def action_confirm(self) -> None:
        selected: List[str] = []
        for _category, skills in self.skills_by_category:
            for slug, _display in skills:
                safe_id = f"pick-{slug.replace('.', '-').replace('/', '-')}"
                try:
                    cb = self.query_one(f"#{safe_id}", Checkbox)
                    if cb.value:
                        selected.append(slug)
                except Exception:
                    continue
        self.dismiss(selected)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "confirm":
            self.action_confirm()
        else:
            self.action_cancel()


def run_skill_picker(
    cortex_root: Any,
    pre_selected: Optional[Iterable[str]] = None,
) -> Optional[List[str]]:
    """Launch :class:`SkillPickerScreen` as a standalone modal app.

    Returns the selected slugs on confirm (possibly an empty list), or
    ``None`` if the user cancelled (Esc / Cancel button).

    Distinguishing ``None`` from ``[]`` is load-bearing for the curate flow:
    ``None`` means "abort, change nothing" while ``[]`` means "deselect
    everything" — a legitimate replace that empties the manifest. The
    callback therefore forwards the screen's dismiss value verbatim rather
    than coercing it to a list.
    """
    from textual.app import App

    categories = build_skills_by_category(cortex_root)
    pre = list(pre_selected or [])

    class _PickerApp(App[Optional[List[str]]]):
        def on_mount(self) -> None:
            self.push_screen(
                SkillPickerScreen(categories, pre_selected=pre),
                callback=self.on_picked,
            )

        def on_picked(self, selected: Optional[List[str]]) -> None:
            self.exit(selected)

    return _PickerApp().run()


def build_skills_by_category(
    cortex_root: Any,
) -> List[Tuple[str, List[Tuple[str, str]]]]:
    """Build the (category → [(slug, display_name)]) structure for SkillPickerScreen.

    Args:
        cortex_root: Path to the bundle root (from _resolve_cortex_root()).

    Returns:
        Sorted list of (category_name, [(slug, display_name)]).
    """
    from pathlib import Path
    from ...core.skills import load_skills_registry, skill_categories_map

    cortex_root = Path(cortex_root)
    registry = load_skills_registry(cortex_root)
    cat_map = skill_categories_map(registry)

    # Collect all skill slugs that have a SKILL.md
    skills_dir = cortex_root / "skills"
    slugs: List[str] = sorted(
        p.name
        for p in skills_dir.iterdir()
        if p.is_dir() and (p / "SKILL.md").is_file()
    ) if skills_dir.is_dir() else []

    # Group by primary category (first in the list, else "other")
    groups: Dict[str, List[Tuple[str, str]]] = {}
    for slug in slugs:
        cats = cat_map.get(slug, [])
        cat = cats[0] if cats else "other"
        groups.setdefault(cat, []).append((slug, slug))

    return sorted(groups.items())
