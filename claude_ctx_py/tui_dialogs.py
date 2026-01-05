"""Modal dialog system for TUI using Textual."""

from __future__ import annotations

from typing import Dict, List, Optional, TypedDict, cast

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Static

from .tui_icons import Icons
from .tui_format import Format

class TaskEditorData(TypedDict, total=False):
    name: str
    workstream: str
    category: str
    status: str
    progress: str
    description: str
    raw_notes: str


class MCPServerData(TypedDict, total=False):
    name: str
    command: str
    args: List[str]
    description: str


class ConfirmDialog(ModalScreen[bool]):
    """Confirmation dialog modal."""

    CSS = """
    ConfirmDialog {
        align: center middle;
    }
    
    ConfirmDialog #dialog {
        opacity: 1;
    }
    """

    BINDINGS = [
        Binding("y", "confirm_yes", "Yes"),
        Binding("n", "confirm_no", "No"),
        Binding("escape", "confirm_no", "Cancel"),
    ]

    def __init__(self, title: str, message: str, default: bool = False):
        """Initialize confirmation dialog.

        Args:
            title: Dialog title
            message: Dialog message
            default: Default choice (True = Yes, False = No)
        """
        super().__init__()
        self.title = title
        self.message = message
        self.default = default

    def compose(self) -> ComposeResult:
        """Compose the dialog."""
        with Container(id="dialog"):
            with Vertical():
                yield Static(
                    f"{Icons.WARNING} [bold]{self.title}[/bold]", id="dialog-title"
                )
                yield Static(self.message, id="dialog-message")
                yield Static("[dim][y] Yes • [n] No • [esc] Cancel[/dim]", id="dialog-hint")
                with Container(id="dialog-buttons"):
                    yield Button(
                        "Yes [y]",
                        variant="success" if self.default else "default",
                        id="yes",
                    )
                    yield Button(
                        "No [n]",
                        variant="error" if not self.default else "default",
                        id="no",
                    )

    def action_confirm_yes(self) -> None:
        """Confirm with Yes."""
        self.dismiss(True)

    def action_confirm_no(self) -> None:
        """Confirm with No."""
        self.dismiss(False)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        self.dismiss(event.button.id == "yes")


class ErrorDialog(ModalScreen[None]):
    """Error dialog modal."""

    CSS = """
    ErrorDialog {
        align: center middle;
    }
    
    ErrorDialog #dialog {
        opacity: 1;
    }
    """

    BINDINGS = [
        Binding("escape", "close", "Close"),
        Binding("enter", "close", "Close"),
    ]

    def __init__(self, title: str, message: str, details: str = ""):
        """Initialize error dialog.

        Args:
            title: Error title
            message: Error message
            details: Optional error details
        """
        super().__init__()
        self.title = title
        self.message = message
        self.details = details

    def compose(self) -> ComposeResult:
        """Compose the dialog."""
        with Container(id="dialog"):
            with Vertical():
                yield Static(
                    f"{Icons.ERROR} [bold red]{self.title}[/bold red]",
                    id="dialog-title",
                )
                yield Static(self.message, id="dialog-message")
                if self.details:
                    yield Static(
                        f"[dim]{Format.truncate(self.details, 200)}[/dim]",
                        id="dialog-details",
                    )
                yield Button("Close", variant="error", id="close")

    def action_close(self) -> None:
        """Close the dialog."""
        self.dismiss()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        self.dismiss()


class InfoDialog(ModalScreen[None]):
    """Information dialog modal."""

    CSS = """
    InfoDialog {
        align: center middle;
    }
    
    InfoDialog #dialog {
        opacity: 1;
    }
    """

    BINDINGS = [
        Binding("escape", "close", "Close"),
        Binding("enter", "close", "Close"),
    ]

    def __init__(self, title: str, message: str):
        """Initialize info dialog.

        Args:
            title: Dialog title
            message: Dialog message
        """
        super().__init__()
        self.title = title
        self.message = message

    def compose(self) -> ComposeResult:
        """Compose the dialog."""
        with Container(id="dialog"):
            with Vertical():
                yield Static(
                    f"{Icons.INFO} [bold blue]{self.title}[/bold blue]",
                    id="dialog-title",
                )
                yield Static(self.message, id="dialog-message")
                yield Button("OK", variant="primary", id="ok")

    def action_close(self) -> None:
        """Close the dialog."""
        self.dismiss()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        self.dismiss()


class LoadingOverlay(ModalScreen[None]):
    """Loading overlay modal - non-dismissible."""

    def __init__(self, message: str = "Loading..."):
        """Initialize loading overlay.

        Args:
            message: Loading message
        """
        super().__init__()
        self.message = message

    def compose(self) -> ComposeResult:
        """Compose the overlay."""
        with Container(id="loading-overlay"):
            yield Static(
                f"{Icons.RUNNING} [yellow]{self.message}[/yellow]", id="loading-message"
            )
            yield Static("[dim]Please wait...[/dim]", id="loading-subtitle")

    # No bindings - loading overlay can't be dismissed by user


class TaskEditorDialog(ModalScreen[Optional[TaskEditorData]]):
    """Dialog for creating or editing orchestration tasks."""

    CSS = """
    TaskEditorDialog {
        align: center middle;
    }
    
    TaskEditorDialog #dialog {
        opacity: 1;
    }
    """

    BINDINGS = [
        Binding("escape", "close", "Cancel"),
        Binding("enter", "submit", "Save"),
        Binding("ctrl+s", "submit", "Save"),
    ]

    def __init__(self, title: str, defaults: Optional[TaskEditorData] = None):
        super().__init__()
        self.title = title
        self.defaults: TaskEditorData = cast(TaskEditorData, dict(defaults or {}))

    def compose(self) -> ComposeResult:
        with Container(id="dialog"):
            with Vertical():
                yield Static(
                    f"{Icons.CODE} [bold]{self.title}[/bold]", id="dialog-title"
                )
                yield Input(
                    value=self.defaults.get("name", ""),
                    placeholder="Task name",
                    id="task-name",
                )
                yield Input(
                    value=self.defaults.get("workstream", "primary"),
                    placeholder="Workstream",
                    id="task-workstream",
                )
                yield Input(
                    value=self.defaults.get("category", "general"),
                    placeholder="Category (e.g. development)",
                    id="task-category",
                )
                yield Input(
                    value=self.defaults.get("status", "pending"),
                    placeholder="Status (pending/running/complete)",
                    id="task-status",
                )
                yield Input(
                    value=str(self.defaults.get("progress", 0)),
                    placeholder="Progress 0-100",
                    id="task-progress",
                )
                yield Input(
                    value=self.defaults.get("description", ""),
                    placeholder="Details / notes (optional)",
                    id="task-description",
                )
                with Container(id="dialog-buttons"):
                    yield Button("Save", variant="success", id="save")
                    yield Button("Cancel", variant="error", id="cancel")

    def action_close(self) -> None:
        self.dismiss(None)

    def action_submit(self) -> None:
        self._submit()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save":
            self._submit()
        else:
            self.dismiss(None)

    def _submit(self) -> None:
        name = self.query_one("#task-name", Input).value.strip()
        workstream = self.query_one("#task-workstream", Input).value.strip()
        category = self.query_one("#task-category", Input).value.strip()
        status = self.query_one("#task-status", Input).value.strip()
        progress = self.query_one("#task-progress", Input).value.strip()
        description = self.query_one("#task-description", Input).value.strip()

        if not name:
            self.dismiss(None)
            return

        self.dismiss(
            {
                "name": name,
                "workstream": workstream or "primary",
                "category": category or "general",
                "status": status or "pending",
                "progress": progress or "0",
                "description": description,
                "raw_notes": description,
            }
        )


class PromptDialog(ModalScreen[Optional[str]]):
    """Simple prompt dialog to capture a single line of text."""

    CSS = """
    PromptDialog {
        align: center middle;
    }
    
    PromptDialog #dialog {
        opacity: 1;
    }
    """

    BINDINGS = [
        Binding("escape", "close", "Cancel"),
        Binding("enter", "submit", "Save"),
    ]

    def __init__(
        self, title: str, prompt: str, *, placeholder: str = "", default: str = ""
    ):
        super().__init__()
        self.title = title
        self.prompt = prompt
        self.placeholder = placeholder
        self.default = default

    def compose(self) -> ComposeResult:
        with Container(id="dialog"):
            with Vertical():
                yield Static(
                    f"{Icons.INFO} [bold]{self.title}[/bold]", id="dialog-title"
                )
                yield Static(self.prompt, id="dialog-message")
                yield Input(
                    value=self.default, placeholder=self.placeholder, id="prompt-input"
                )
                with Container(id="dialog-buttons"):
                    yield Button("Save", variant="success", id="save")
                    yield Button("Cancel", variant="error", id="cancel")

    def action_close(self) -> None:
        self.dismiss(None)

    def action_submit(self) -> None:
        value = self.query_one("#prompt-input", Input).value.strip()
        self.dismiss(value or None)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.action_submit()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save":
            self.action_submit()
        else:
            self.dismiss(None)


class TextViewerDialog(ModalScreen[None]):
    """Scrollable text viewer for long-form content (docs, snippets, logs)."""

    CSS = """
    TextViewerDialog {
        align: center middle;
    }

    TextViewerDialog #dialog {
        opacity: 1;
    }

    TextViewerDialog #dialog-scroll {
        max-height: 60vh;
        width: 80%;
        max-width: 95vw;
    }

    TextViewerDialog #dialog-message {
        text-style: none;
        text-align: left;
    }

    TextViewerDialog #dialog-hint {
        text-align: center;
        color: $text-muted;
        padding: 0 1;
    }
    """

    BINDINGS = [
        Binding("escape", "close", "Close"),
        Binding("enter", "close", "Close"),
    ]

    def __init__(self, title: str, body: str):
        super().__init__()
        self.title = title
        self.body = body

    def compose(self) -> ComposeResult:
        with Container(id="dialog"):
            with Vertical():
                yield Static(
                    f"{Icons.DOC} [bold]{self.title}[/bold]", id="dialog-title"
                )
                with VerticalScroll(id="dialog-scroll"):
                    yield Static(
                        self.body,
                        id="dialog-message",
                        markup=False,
                    )
                yield Static(
                    "[dim]Use ↑/↓, PageUp/PageDown, or mouse wheel to scroll[/dim]",
                    id="dialog-hint",
                )
                yield Button("Close", variant="primary", id="close")

    def action_close(self) -> None:
        self.dismiss()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss()

    def on_mount(self) -> None:
        """Focus the scroll region so keyboard scrolling works immediately."""
        try:
            self.query_one("#dialog-scroll", VerticalScroll).focus()
        except Exception:
            pass


class MCPServerDialog(ModalScreen[Optional[MCPServerData]]):
    """Dialog for adding or editing MCP server configuration."""

    CSS = """
    MCPServerDialog {
        align: center middle;
    }
    
    MCPServerDialog #dialog {
        opacity: 1;
    }
    """

    BINDINGS = [
        Binding("escape", "close", "Cancel"),
        Binding("ctrl+s", "submit", "Save"),
    ]

    def __init__(self, title: str, defaults: Optional[MCPServerData] = None):
        super().__init__()
        self.title = title
        self.defaults: MCPServerData = cast(MCPServerData, dict(defaults or {}))

    def compose(self) -> ComposeResult:
        with Container(id="dialog"):
            with Vertical():
                yield Static(
                    f"{Icons.CODE} [bold]{self.title}[/bold]", id="dialog-title"
                )
                yield Input(
                    value=self.defaults.get("name", ""),
                    placeholder="Server name (e.g., context7)",
                    id="mcp-name",
                    disabled=bool(self.defaults.get("name")),  # Can't change name when editing
                )
                yield Input(
                    value=self.defaults.get("command", ""),
                    placeholder="Command (e.g., npx, uvx)",
                    id="mcp-command",
                )
                args_value = self.defaults.get("args", "")
                if isinstance(args_value, list):
                    args_text = " ".join(args_value)
                else:
                    args_text = str(args_value or "")
                yield Input(
                    value=args_text,
                    placeholder="Arguments (space-separated, e.g., -y @package/name)",
                    id="mcp-args",
                )
                yield Input(
                    value=self.defaults.get("description", ""),
                    placeholder="Description (optional)",
                    id="mcp-description",
                )
                with Container(id="dialog-buttons"):
                    yield Button("Save", variant="success", id="save")
                    yield Button("Cancel", variant="error", id="cancel")

    def action_close(self) -> None:
        self.dismiss(None)

    def action_submit(self) -> None:
        self._submit()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save":
            self._submit()
        else:
            self.dismiss(None)

    def _submit(self) -> None:
        name = self.query_one("#mcp-name", Input).value.strip()
        command = self.query_one("#mcp-command", Input).value.strip()
        args_str = self.query_one("#mcp-args", Input).value.strip()
        description = self.query_one("#mcp-description", Input).value.strip()

        if not name or not command:
            self.dismiss(None)
            return

        # Parse args string into list
        args = args_str.split() if args_str else []

        self.dismiss(
            {
                "name": name,
                "command": command,
                "args": args,
                "description": description,
            }
        )


class HelpDialog(ModalScreen[None]):
    """Comprehensive keyboard shortcuts help dialog."""

    CSS = """
    HelpDialog {
        align: center middle;
    }

    HelpDialog #dialog {
        opacity: 1;
        width: 80%;
        max-height: 85%;
    }

    HelpDialog #help-scroll {
        height: auto;
        max-height: 50vh;
        border: solid $accent-darken-1;
        background: $surface;
        padding: 1;
    }

    HelpDialog #dialog-message {
        text-align: left;
        text-style: none;
        background: transparent;
    }
    """

    BINDINGS = [
        Binding("escape", "close", "Close"),
        Binding("enter", "close", "Close"),
        Binding("q", "close", "Close"),
    ]

    def __init__(self, current_view: str = "overview"):
        super().__init__()
        self.title = f"⌨️  Keyboard Shortcuts (Current: {current_view.title()})"
        self.current_view = current_view

    def compose(self) -> ComposeResult:
        help_text = self._generate_help_text()
        with Container(id="dialog"):
            with Vertical():
                yield Static(f"{Icons.CODE} [bold]{self.title}[/bold]", id="dialog-title")
                with VerticalScroll(id="help-scroll"):
                    yield Static(help_text, id="dialog-message")
                yield Button("Close (ESC/Q)", variant="primary", id="close")

    def _generate_help_text(self) -> str:
        """Generate formatted help text with all shortcuts."""
        global_shortcuts = """[bold cyan]━━━ GLOBAL SHORTCUTS ━━━[/bold cyan]

[bold]General:[/bold]
  [cyan]?[/cyan]      → Show this help
  [cyan]r[/cyan]      → Refresh current view
  [cyan]q[/cyan]      → Quit application
  [cyan]Ctrl+P[/cyan] → Command palette
  [cyan]Space[/cyan]  → Toggle selected item
  [cyan]W[/cyan]      → Configure CLAUDE.md wizard
  [cyan]h[/cyan]      → Manage hooks
  [cyan]b[/cyan]      → Backup manager

[bold]Navigation (Vi-style):[/bold]
  [cyan]j/k[/cyan]       → Cursor down/up
  [cyan]gg[/cyan]        → Jump to top
  [cyan]G[/cyan]         → Jump to bottom
  [cyan]Ctrl+U[/cyan]    → Half page up
  [cyan]Ctrl+D[/cyan]    → Half page down
  [cyan]Ctrl+B[/cyan]    → Page up
  [cyan]Ctrl+F[/cyan]    → Page down
  [cyan]↑/↓[/cyan]       → Cursor up/down

[bold]View Navigation:[/bold]
  [cyan]1[/cyan] Overview    [cyan]2[/cyan] Agents    [cyan]3[/cyan] Modes     [cyan]4[/cyan] Rules
  [cyan]p[/cyan] Principles  [cyan]5[/cyan] Skills   [cyan]6[/cyan] Workflows [cyan]C[/cyan] Worktrees [cyan]7[/cyan] MCP
  [cyan]8[/cyan] Profiles    [cyan]9[/cyan] Export   [cyan]0[/cyan] AI Asst   [cyan]A[/cyan] Assets
  [cyan]M[/cyan] Memory      [cyan]S[/cyan] Scenarios [cyan]o[/cyan] Orchestrate [cyan]Alt+g[/cyan] Galaxy
  [cyan]t[/cyan] Tasks
  [cyan]/[/cyan] Slash Cmds
"""

        view_shortcuts = {
            "overview": """
[bold]Metrics & monitoring[/bold]
""",
            "agents": """
[bold]Agent Management:[/bold]
  [cyan]Enter[/cyan] → View agent definition
  [cyan]Space[/cyan] → Toggle agent active/inactive
  [cyan]s[/cyan]     → Show agent details
  [cyan]v[/cyan]     → Validate agent
  [cyan]Ctrl+E[/cyan] → Edit agent file
""",
            "modes": """
[bold]Mode Management:[/bold]
  [cyan]Space[/cyan]  → Toggle mode active/inactive
  [cyan]Ctrl+E[/cyan] → Edit mode file
""",
            "rules": """
[bold]Rule Management:[/bold]
  [cyan]Space[/cyan]  → Toggle rule active/inactive
  [cyan]Ctrl+E[/cyan] → Edit rule file
""",
            "principles": """
[bold]Principles Management:[/bold]
  [cyan]Space[/cyan]  → Toggle snippet active/inactive
  [cyan]s[/cyan]      → View snippet details
  [cyan]c[/cyan]      → Rebuild PRINCIPLES.md
  [cyan]d[/cyan]      → Open PRINCIPLES.md
  [cyan]Ctrl+E[/cyan] → Edit snippet file
""",
            "skills": """
[bold]Skill Management:[/bold]
  [cyan]s[/cyan]      → Show skill details
  [cyan]v[/cyan]      → Validate skill
  [cyan]m[/cyan]      → Show skill metrics
  [cyan]d[/cyan]      → View skill docs
  [cyan]c[/cyan]      → Skill actions menu
  [cyan]Ctrl+E[/cyan] → Edit skill file
""",
            "workflows": """
[bold]Workflow Management:[/bold]
  [cyan]R[/cyan] → Run selected workflow
  [cyan]s[/cyan] → Show workflow details
""",
            "worktrees": """
[bold]Worktree Management:[/bold]
  [cyan]Ctrl+N[/cyan] → Add new worktree
  [cyan]Ctrl+O[/cyan] → Open selected worktree
  [cyan]Ctrl+W[/cyan] → Remove selected worktree
  [cyan]Ctrl+K[/cyan] → Prune stale worktrees
  [cyan]B[/cyan]      → Set base directory (use '-' to clear)
""",
            "scenarios": """
[bold]Scenario Management:[/bold]
  [cyan]P[/cyan] → Preview scenario
  [cyan]R[/cyan] → Run scenario
  [cyan]V[/cyan] → Validate scenario
  [cyan]H[/cyan] → Show scenario status/history
""",
            "mcp": """
[bold]MCP Server Management:[/bold]
  [cyan]B[/cyan]      → Browse & install from registry
  [cyan]Ctrl+A[/cyan] → Add new MCP server manually
  [cyan]E[/cyan]      → Edit selected server
  [cyan]X[/cyan]      → Remove selected server
  [cyan]s[/cyan]      → Show server details
  [cyan]d[/cyan]      → View server docs
  [cyan]v[/cyan]      → Validate server
  [cyan]Ctrl+T[/cyan] → Test selected server
  [cyan]D[/cyan]      → Diagnose all servers
""",
            "profiles": """
[bold]Profile Management:[/bold]
  [cyan]Enter[/cyan] → View/Edit profile
  [cyan]Space[/cyan] → Apply profile directly
  [cyan]n[/cyan]     → Save new profile
  [cyan]D[/cyan]     → Delete profile
""",
            "export": """
[bold]Export Management:[/bold]
  [cyan]Space[/cyan] → Toggle export category
  [cyan]f[/cyan]     → Cycle export format
  [cyan]e[/cyan]     → Execute export
  [cyan]x[/cyan]     → Copy to clipboard
""",
            "ai_assistant": """
[bold]AI Assistant:[/bold]
  [cyan]a[/cyan] → Auto-activate recommended agents
  [cyan]J[/cyan] → Consult Gemini
  [cyan]K[/cyan] → Assign LLM tasks
  [cyan]Y[/cyan] → Request review tasks
""",
            "tasks": """
[bold]Task Management:[/bold]
  [cyan]a[/cyan]      → Add new task
  [cyan]Space[/cyan]  → Toggle task status
  [cyan]Ctrl+E[/cyan] → Edit task
""",
            "assets": """
[bold]Asset Manager:[/bold]
  [cyan]i[/cyan]     → Install selected asset
  [cyan]u[/cyan]     → Uninstall selected asset
  [cyan]d[/cyan]     → View diff (installed vs source)
  [cyan]U[/cyan]     → Update all outdated assets
  [cyan]I[/cyan]     → Bulk install (by category)
  [cyan]T[/cyan]     → Change target directory
  [cyan]Enter[/cyan] → Show asset details
""",
            "memory": """
[bold]Memory Vault:[/bold]
  [cyan]Enter[/cyan] → View note content
  [cyan]N[/cyan]     → New note
  [cyan]O[/cyan]     → Open note in editor ($EDITOR)
  [cyan]D[/cyan]     → Delete note
""",
            "galaxy": """
[bold]Agent Galaxy View:[/bold]
  Visual dependency graph
""",
            "orchestrate": """
[bold]Orchestrate View:[/bold]
  Workstream management
""",
            "commands": """
[bold]Slash Commands:[/bold]
  [cyan]Enter[/cyan] → View command details
  [cyan]Ctrl+E[/cyan] → Edit command file
""",
        }

        current_view_help = view_shortcuts.get(self.current_view, "")

        if current_view_help:
            current_section = (
                f"[bold cyan]━━━ {self.current_view.upper()} VIEW ━━━[/bold cyan]\n"
                f"{current_view_help.strip()}\n"
            )
        else:
            current_section = ""

        footer = """
[bold cyan]━━━━━━━━━━━━━━━━━━━━━━[/bold cyan]

[dim]↑/↓ or j/k to scroll • ESC, Q, or Enter to close[/dim]
"""

        if current_section:
            return current_section + "\n" + global_shortcuts + footer
        return global_shortcuts + footer

    def action_close(self) -> None:
        self.dismiss()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss()
