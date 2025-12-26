"""MCP Server Installation Dialogs."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, ListItem, ListView, Static

from ...core.mcp_registry import (
    MCPServerDefinition,
    ServerCategory,
    get_all_servers,
    get_categories,
    get_server,
    get_servers_by_category,
    search_servers,
)
from ...core.mcp_installer import (
    check_package_manager,
    check_server_installed,
    get_server_requirements,
)


class MCPBrowseDialog(ModalScreen[Optional[str]]):
    """Dialog for browsing and selecting MCP servers to install."""

    CSS = """
    MCPBrowseDialog {
        align: center middle;
    }

    MCPBrowseDialog #dialog {
        width: 85%;
        max-width: 100;
        height: 80%;
        background: $surface-lighten-1;
        border: thick $accent;
        padding: 1 2;
        opacity: 1;
    }

    MCPBrowseDialog #dialog-title {
        text-align: center;
        color: $accent;
        text-style: bold;
        margin-bottom: 1;
    }

    MCPBrowseDialog #search-container {
        height: auto;
        margin-bottom: 1;
    }

    MCPBrowseDialog #search-input {
        width: 100%;
    }

    MCPBrowseDialog #content-container {
        height: 1fr;
    }

    MCPBrowseDialog #category-list {
        width: 25;
        height: 100%;
        border: solid $primary-darken-2;
        background: $surface;
    }

    MCPBrowseDialog #server-list {
        width: 1fr;
        height: 100%;
        border: solid $primary-darken-2;
        background: $surface;
        margin-left: 1;
    }

    MCPBrowseDialog .category-item {
        padding: 0 1;
    }

    MCPBrowseDialog .category-item.selected {
        background: $accent;
        color: $text;
    }

    MCPBrowseDialog .server-item {
        padding: 0 1;
        height: auto;
    }

    MCPBrowseDialog .server-name {
        text-style: bold;
    }

    MCPBrowseDialog .server-desc {
        color: $text-muted;
    }

    MCPBrowseDialog .server-status {
        color: $success;
    }

    MCPBrowseDialog #dialog-hint {
        text-align: center;
        color: $text-muted;
        margin-top: 1;
    }

    MCPBrowseDialog #dialog-buttons {
        align: center middle;
        height: auto;
        margin-top: 1;
    }
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("enter", "select", "Select"),
        Binding("/", "focus_search", "Search"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.selected_category: Optional[ServerCategory] = None
        self.selected_server: Optional[str] = None
        self.servers: List[MCPServerDefinition] = []

    def compose(self) -> ComposeResult:
        with Container(id="dialog", classes="visible"):
            yield Static("🔌 Browse MCP Servers", id="dialog-title")

            with Container(id="search-container"):
                yield Input(placeholder="Search servers...", id="search-input")

            with Horizontal(id="content-container"):
                yield ListView(id="category-list")
                yield ListView(id="server-list")

            yield Static(
                "[dim]↑/↓ Navigate • Enter Select • / Search • Esc Cancel[/dim]",
                id="dialog-hint",
            )

            with Container(id="dialog-buttons"):
                yield Button("Install Selected", variant="success", id="install")
                yield Button("Cancel", variant="default", id="cancel")

    def on_mount(self) -> None:
        """Populate categories on mount."""
        category_list = self.query_one("#category-list", ListView)

        # Add "All" option
        all_item = ListItem(Static("📋 All Servers"), id="cat-all")
        category_list.append(all_item)

        # Add categories
        category_icons = {
            ServerCategory.DOCUMENTATION: "📚",
            ServerCategory.CODE_INTELLIGENCE: "🧠",
            ServerCategory.REASONING: "💭",
            ServerCategory.DATABASE: "🗄️",
            ServerCategory.WEB: "🌐",
            ServerCategory.FILE_SYSTEM: "📁",
            ServerCategory.PRODUCTIVITY: "⚡",
            ServerCategory.AI_TOOLS: "🤖",
            ServerCategory.DEVELOPMENT: "🛠️",
            ServerCategory.OTHER: "📦",
        }

        for category in get_categories():
            icon = category_icons.get(category, "📦")
            item = ListItem(
                Static(f"{icon} {category.value}"),
                id=f"cat-{category.name.lower()}",
            )
            category_list.append(item)

        # Select "All" by default and load servers
        category_list.index = 0
        self._load_all_servers()

    def _load_all_servers(self) -> None:
        """Load all servers."""
        self.servers = get_all_servers()
        self._update_server_list()

    def _load_category_servers(self, category: ServerCategory) -> None:
        """Load servers for a specific category."""
        self.servers = get_servers_by_category(category)
        self._update_server_list()

    def _update_server_list(self) -> None:
        """Update the server list display."""
        server_list = self.query_one("#server-list", ListView)
        server_list.clear()

        for server in self.servers:
            # Check if already installed
            is_installed, _ = check_server_installed(server)
            status = " ✓" if is_installed else ""

            # Check package manager availability
            pm_available, _ = check_package_manager(server.package_manager)
            pm_indicator = "" if pm_available else " ⚠️"

            content = Text()
            content.append(f"{server.name}{status}{pm_indicator}\n", style="bold")
            content.append(server.description[:60], style="dim")
            if len(server.description) > 60:
                content.append("...", style="dim")

            item = ListItem(Static(content), id=f"srv-{server.name}")
            server_list.append(item)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle list selection."""
        item_id = event.item.id or ""

        if item_id.startswith("cat-"):
            # Category selected
            cat_name = item_id[4:]
            if cat_name == "all":
                self._load_all_servers()
            else:
                for cat in ServerCategory:
                    if cat.name.lower() == cat_name:
                        self._load_category_servers(cat)
                        break
        elif item_id.startswith("srv-"):
            # Server selected
            self.selected_server = item_id[4:]

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle search input."""
        if event.input.id == "search-input":
            query = event.value.strip()
            if query:
                self.servers = search_servers(query)
            else:
                self._load_all_servers()
            self._update_server_list()

    def action_focus_search(self) -> None:
        """Focus the search input."""
        self.query_one("#search-input", Input).focus()

    def action_cancel(self) -> None:
        """Cancel and close dialog."""
        self.dismiss(None)

    def action_select(self) -> None:
        """Select current server."""
        server_list = self.query_one("#server-list", ListView)
        if server_list.highlighted_child:
            item_id = server_list.highlighted_child.id or ""
            if item_id.startswith("srv-"):
                self.dismiss(item_id[4:])

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button.id == "install":
            self.action_select()
        elif event.button.id == "cancel":
            self.dismiss(None)


class MCPInstallDialog(ModalScreen[Optional[Dict[str, Any]]]):
    """Dialog for configuring and installing an MCP server."""

    CSS = """
    MCPInstallDialog {
        align: center middle;
    }

    MCPInstallDialog #dialog {
        width: 70%;
        max-width: 80;
        height: auto;
        max-height: 85%;
        background: $surface-lighten-1;
        border: thick $accent;
        padding: 1 2;
        opacity: 1;
    }

    MCPInstallDialog #dialog-title {
        text-align: center;
        color: $accent;
        text-style: bold;
        margin-bottom: 1;
    }

    MCPInstallDialog #server-info {
        background: $surface;
        border: solid $primary-darken-2;
        padding: 1;
        margin-bottom: 1;
    }

    MCPInstallDialog #requirements {
        background: $surface;
        border: solid $warning-darken-1;
        padding: 1;
        margin-bottom: 1;
    }

    MCPInstallDialog .section-title {
        text-style: bold;
        margin-bottom: 1;
    }

    MCPInstallDialog .env-field {
        margin-bottom: 1;
    }

    MCPInstallDialog .env-label {
        margin-bottom: 0;
    }

    MCPInstallDialog .env-desc {
        color: $text-muted;
        margin-bottom: 0;
    }

    MCPInstallDialog .required {
        color: $error;
    }

    MCPInstallDialog #env-vars-container {
        height: auto;
        max-height: 30vh;
        background: $surface;
        border: solid $primary-darken-2;
        padding: 1;
        margin-bottom: 1;
    }

    MCPInstallDialog #dialog-buttons {
        align: center middle;
        height: auto;
        margin-top: 1;
    }

    MCPInstallDialog #dialog-hint {
        text-align: center;
        color: $text-muted;
        margin-top: 1;
    }
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("ctrl+s", "install", "Install"),
    ]

    def __init__(self, server_name: str) -> None:
        super().__init__()
        self.server_name = server_name
        self.server = get_server(server_name)
        self.requirements = get_server_requirements(self.server) if self.server else {}

    def compose(self) -> ComposeResult:
        if not self.server:
            with Container(id="dialog", classes="visible"):
                yield Static("❌ Server not found", id="dialog-title")
                yield Button("Close", variant="default", id="cancel")
            return

        with Container(id="dialog", classes="visible"):
            yield Static(f"🔧 Install {self.server.name}", id="dialog-title")

            # Server info
            with Vertical(id="server-info"):
                yield Static("[bold]Server Information[/bold]", classes="section-title")
                yield Static(f"[cyan]Name:[/cyan] {self.server.name}")
                yield Static(f"[cyan]Package:[/cyan] {self.server.package}")
                yield Static(f"[cyan]Category:[/cyan] {self.server.category.value}")
                yield Static(f"\n{self.server.description}")

            # Requirements
            with Vertical(id="requirements"):
                yield Static("[bold]Requirements[/bold]", classes="section-title")

                pm_status = "✓" if self.requirements["pm_available"] else "✗"
                pm_color = "green" if self.requirements["pm_available"] else "red"
                yield Static(
                    f"[cyan]Package Manager:[/cyan] {self.requirements['package_manager']} "
                    f"[{pm_color}]{pm_status}[/{pm_color}]"
                )

                if self.server.install_notes:
                    yield Static(f"[yellow]Note:[/yellow] {self.server.install_notes}")

            # Environment variables
            if self.requirements["env_vars"]:
                with VerticalScroll(id="env-vars-container"):
                    yield Static(
                        "[bold]Environment Variables[/bold]",
                        classes="section-title",
                    )

                    for env_var in self.requirements["env_vars"]:
                        required_marker = " [red]*[/red]" if env_var["required"] else ""
                        yield Label(
                            f"{env_var['name']}{required_marker}",
                            classes="env-label",
                        )
                        yield Static(
                            f"[dim]{env_var['description']}[/dim]",
                            classes="env-desc",
                        )
                        yield Input(
                            placeholder=env_var.get("default", ""),
                            password=env_var.get("secret", False),
                            id=f"env-{env_var['name']}",
                            classes="env-field",
                        )

            yield Static(
                "[dim]Ctrl+S Install • Esc Cancel[/dim]",
                id="dialog-hint",
            )

            with Container(id="dialog-buttons"):
                can_install = self.requirements.get("pm_available", False)
                yield Button(
                    "Install & Configure",
                    variant="success" if can_install else "default",
                    id="install",
                    disabled=not can_install,
                )
                yield Button("Cancel", variant="default", id="cancel")

    def action_cancel(self) -> None:
        """Cancel installation."""
        self.dismiss(None)

    def action_install(self) -> None:
        """Proceed with installation."""
        if not self.server or not self.requirements.get("pm_available"):
            return

        # Collect environment variable values
        env_values = {}
        for env_var in self.requirements.get("env_vars", []):
            try:
                input_widget = self.query_one(f"#env-{env_var['name']}", Input)
                value = input_widget.value.strip()
                if value:
                    env_values[env_var["name"]] = value
                elif env_var.get("default"):
                    env_values[env_var["name"]] = env_var["default"]
            except Exception:
                pass

        self.dismiss({
            "server_name": self.server_name,
            "env_values": env_values,
        })

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button.id == "install":
            self.action_install()
        elif event.button.id == "cancel":
            self.dismiss(None)
