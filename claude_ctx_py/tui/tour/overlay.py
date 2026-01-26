"""Tour overlay modal for guided onboarding."""

from __future__ import annotations

from typing import Callable, Optional

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, ProgressBar, Static

from .types import TourDefinition, TourStep


class TourOverlay(ModalScreen[Optional[str]]):
    """Modal overlay for displaying tour steps.

    Returns:
        - "completed" if tour was completed
        - "skipped" if tour was skipped
        - None if dismissed without completing
    """

    CSS = """
    TourOverlay {
        align: center middle;
        background: rgba(5, 7, 20, 0.85);
    }

    TourOverlay #tour-container {
        width: 70;
        max-width: 90%;
        height: auto;
        max-height: 80%;
        background: $surface;
        border: thick $primary;
        padding: 1 2;
    }

    TourOverlay #tour-header {
        height: 3;
        width: 100%;
        content-align: center middle;
    }

    TourOverlay #tour-title {
        text-align: center;
        text-style: bold;
        color: $primary;
    }

    TourOverlay #tour-step-indicator {
        text-align: center;
        color: $text-muted;
    }

    TourOverlay #tour-content {
        height: auto;
        min-height: 8;
        max-height: 20;
        padding: 1 0;
        overflow-y: auto;
    }

    TourOverlay #tour-description {
        width: 100%;
    }

    TourOverlay #tour-action-hint {
        text-align: center;
        color: $accent;
        padding-top: 1;
    }

    TourOverlay #tour-progress {
        height: 1;
        margin: 1 0;
    }

    TourOverlay #tour-buttons {
        height: 3;
        width: 100%;
        align: center middle;
    }

    TourOverlay #tour-buttons Button {
        margin: 0 1;
    }

    TourOverlay #btn-prev {
        min-width: 12;
    }

    TourOverlay #btn-next {
        min-width: 12;
    }

    TourOverlay #btn-skip {
        min-width: 10;
    }

    TourOverlay #tour-shortcuts {
        text-align: center;
        color: $text-muted;
        height: 1;
        margin-top: 1;
    }
    """

    BINDINGS = [
        Binding("n", "next_step", "Next", show=False),
        Binding("p", "prev_step", "Previous", show=False),
        Binding("q", "skip_tour", "Skip", show=False),
        Binding("escape", "skip_tour", "Skip", show=False),
        Binding("enter", "next_step", "Next", show=False),
    ]

    def __init__(
        self,
        tour: TourDefinition,
        on_view_change: Optional[Callable[[str], None]] = None,
        start_step: int = 0,
    ):
        """Initialize the tour overlay.

        Args:
            tour: Tour definition to display.
            on_view_change: Callback to switch views (receives view name).
            start_step: Index of step to start at.
        """
        super().__init__()
        self.tour = tour
        self._on_view_change = on_view_change
        self._current_step = start_step
        self._completed = False

    @property
    def current_step(self) -> Optional[TourStep]:
        """Get the current tour step."""
        return self.tour.get_step(self._current_step)

    def compose(self) -> ComposeResult:
        """Compose the tour overlay."""
        with Container(id="tour-container"):
            with Vertical():
                # Header
                with Container(id="tour-header"):
                    yield Static(f"[bold]{self.tour.name}[/bold]", id="tour-title")
                    yield Static("", id="tour-step-indicator")

                # Content
                with Container(id="tour-content"):
                    yield Static("", id="tour-description")
                    yield Static("", id="tour-action-hint")

                # Progress bar
                yield ProgressBar(
                    total=len(self.tour),
                    show_eta=False,
                    show_percentage=False,
                    id="tour-progress",
                )

                # Buttons
                with Horizontal(id="tour-buttons"):
                    yield Button("< Prev [p]", variant="default", id="btn-prev")
                    yield Button("Next [n] >", variant="primary", id="btn-next")
                    yield Button("Skip [q]", variant="warning", id="btn-skip")

                # Shortcuts hint
                yield Static(
                    "[dim]n=next  p=prev  q=skip  Enter=next[/dim]",
                    id="tour-shortcuts",
                )

    def on_mount(self) -> None:
        """Handle mount event."""
        self._update_display()

    def _update_display(self) -> None:
        """Update the display for the current step."""
        step = self.current_step
        if step is None:
            return

        # Update step indicator
        indicator = self.query_one("#tour-step-indicator", Static)
        indicator.update(f"Step {self._current_step + 1} of {len(self.tour)}")

        # Update description
        description = self.query_one("#tour-description", Static)
        description.update(step.description)

        # Update action hint
        action_hint = self.query_one("#tour-action-hint", Static)
        if step.action_hint:
            action_hint.update(f"[cyan]{step.action_hint}[/cyan]")
        else:
            action_hint.update("")

        # Update progress
        progress = self.query_one("#tour-progress", ProgressBar)
        progress.progress = self._current_step + 1

        # Update buttons
        prev_btn = self.query_one("#btn-prev", Button)
        next_btn = self.query_one("#btn-next", Button)

        prev_btn.disabled = self._current_step == 0

        if self._current_step >= len(self.tour) - 1:
            next_btn.label = "Finish [n]"
        else:
            next_btn.label = "Next [n] >"

        # Switch view if specified
        if step.target_view and self._on_view_change:
            self._on_view_change(step.target_view)

        # Call on_enter callback if defined
        if step.on_enter:
            step.on_enter()

    def action_next_step(self) -> None:
        """Go to the next step or finish the tour."""
        step = self.current_step
        if step and step.on_exit:
            step.on_exit()

        if self._current_step >= len(self.tour) - 1:
            # Tour complete
            self._completed = True
            self.dismiss("completed")
        else:
            self._current_step += 1
            self._update_display()

    def action_prev_step(self) -> None:
        """Go to the previous step."""
        if self._current_step > 0:
            step = self.current_step
            if step and step.on_exit:
                step.on_exit()

            self._current_step -= 1
            self._update_display()

    def action_skip_tour(self) -> None:
        """Skip the tour."""
        self.dismiss("skipped")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id
        if button_id == "btn-next":
            self.action_next_step()
        elif button_id == "btn-prev":
            self.action_prev_step()
        elif button_id == "btn-skip":
            self.action_skip_tour()
