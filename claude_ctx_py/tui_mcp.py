"""TUI mixin for MCP server management view."""

from __future__ import annotations

from pathlib import Path
import subprocess
from typing import List, Dict, Any, Optional

from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.tree import Tree

from .core.mcp import (
    discover_servers,
    get_server_info,
    get_server_docs_path,
    validate_server_config,
    generate_config_snippet,
    MCPServerInfo,
)


class MCPViewMixin:
    """Mixin for MCP server management view functionality."""

    state: Any

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.mcp_servers: List[MCPServerInfo] = []
        self.mcp_filter: str = ""
        self.mcp_show_details: bool = False
        self.mcp_selected_server: Optional[MCPServerInfo] = None

    def load_mcp_servers(self) -> None:
        """Load MCP servers from Claude Desktop config."""
        try:
            success, servers, error = discover_servers()
            if success:
                self.mcp_servers = servers
                self.state.status_message = f"Loaded {len(servers)} MCP server(s)"
            else:
                self.mcp_servers = []
                self.state.status_message = f"Error loading MCP servers: {error}"
        except Exception as e:
            self.mcp_servers = []
            self.state.status_message = f"Failed to load MCP servers: {e}"

    def get_filtered_servers(self) -> List[MCPServerInfo]:
        """Get servers matching current filter."""
        if not self.mcp_filter:
            return self.mcp_servers

        filter_lower = self.mcp_filter.lower()
        return [
            server
            for server in self.mcp_servers
            if filter_lower in server.name.lower()
            or filter_lower in server.command.lower()
            or (server.description and filter_lower in server.description.lower())
        ]

    def render_mcp_view(self) -> Panel:
        """Render the MCP servers management view."""
        if self.mcp_show_details and self.mcp_selected_server:
            return self._render_mcp_details()
        else:
            return self._render_mcp_list()

    def _render_mcp_list(self) -> Panel:
        """Render the MCP servers list view."""
        servers = self.get_filtered_servers()

        # Create servers table
        table = Table(
            show_header=True,
            header_style="bold magenta",
            show_lines=False,
            expand=True,
        )

        table.add_column("", width=2, no_wrap=True)  # Selection indicator
        table.add_column("Status", width=6, no_wrap=True)
        table.add_column("Server Name", style="cyan", no_wrap=True)
        table.add_column("Command", width=30)
        table.add_column("Args", width=20)
        table.add_column("Docs", width=4, no_wrap=True)

        if not self.mcp_servers:
            table.add_row("", "", "No MCP servers configured", "", "", "")
        elif not servers:
            table.add_row(
                "", "", f"No servers matching '{self.mcp_filter}'", "", "", ""
            )
        else:
            for idx, server in enumerate(servers):
                is_selected = idx == self.state.selected_index
                indicator = ">" if is_selected else ""

                # Status indicator (for now, all show as configured)
                # In future, could check if server is actually running
                status = Text("●", style="green")

                # Truncate long args
                args_text = " ".join(server.args) if server.args else "-"
                if len(args_text) > 18:
                    args_text = args_text[:15] + "..."

                # Documentation indicator
                docs_text = (
                    Text("✓", style="green")
                    if server.docs_path
                    else Text("-", style="dim")
                )

                # Row style
                row_style = "reverse" if is_selected else None

                table.add_row(
                    indicator,
                    status,
                    server.name,
                    server.command,
                    args_text,
                    docs_text,
                    style=row_style,
                )

        # Add filter indicator
        subtitle = Text()
        if self.mcp_filter:
            subtitle.append(f"Filter: {self.mcp_filter}  ", style="cyan")

        # Add controls hint
        controls = Text()
        if subtitle.plain:
            controls.append("\n")
        controls.append("Controls: ", style="bold")
        controls.append("Enter", style="cyan")
        controls.append("=Details  ", style="dim")
        controls.append("t", style="cyan")
        controls.append("=Test  ", style="dim")
        controls.append("d", style="cyan")
        controls.append("=Docs  ", style="dim")
        controls.append("c", style="cyan")
        controls.append("=Copy Config  ", style="dim")
        controls.append("/", style="cyan")
        controls.append("=Filter  ", style="dim")
        controls.append("r", style="cyan")
        controls.append("=Reload", style="dim")

        subtitle.append_text(controls)

        return Panel(
            table,
            title="MCP Servers",
            subtitle=subtitle,
            border_style="cyan",
        )

    def _render_mcp_details(self) -> Panel:
        """Render detailed view of selected MCP server."""
        server = self.mcp_selected_server
        if not server:
            return Panel(
                Text("No server selected", style="dim"), title="Server Details"
            )

        content = Text()

        # Server name and status
        content.append(f"{server.name}\n", style="bold cyan")
        content.append("─" * 60 + "\n\n", style="dim")

        # Basic info
        content.append("Command:\n", style="bold")
        content.append(f"  {server.command}\n\n", style="white")

        if server.args:
            content.append("Arguments:\n", style="bold")
            for arg in server.args:
                content.append(f"  • {arg}\n", style="white")
            content.append("\n")

        # Environment variables
        if server.env:
            content.append("Environment Variables:\n", style="bold")
            for key, value in server.env.items():
                # Mask sensitive values
                display_value = value
                if any(
                    sensitive in key.lower()
                    for sensitive in ["key", "secret", "token", "password"]
                ):
                    display_value = "*" * 8
                content.append(f"  {key}=", style="yellow")
                content.append(f"{display_value}\n", style="dim")
            content.append("\n")

        # Documentation
        content.append("Documentation:\n", style="bold")
        if server.docs_path:
            content.append(f"  ✓ Available at: {server.docs_path}\n\n", style="green")
        else:
            content.append("  ✗ No documentation found\n\n", style="red")

        # Validation status
        content.append("Configuration Status:\n", style="bold")
        is_valid, errors = server.is_valid()
        if is_valid:
            content.append("  ✓ Valid configuration\n", style="green")
        else:
            content.append("  ✗ Configuration errors:\n", style="red")
            for error in errors:
                content.append(f"    • {error}\n", style="red")

        # Command line preview
        content.append("\nFull Command:\n", style="bold")
        full_cmd = server.command
        if server.args:
            full_cmd += " " + " ".join(server.args)
        content.append(f"  {full_cmd}\n", style="white")

        # Controls
        controls = Text()
        controls.append("\nControls: ", style="bold")
        controls.append("Esc", style="cyan")
        controls.append("=Back  ", style="dim")
        controls.append("d", style="cyan")
        controls.append("=View Docs  ", style="dim")
        controls.append("c", style="cyan")
        controls.append("=Copy Config  ", style="dim")
        controls.append("v", style="cyan")
        controls.append("=Validate", style="dim")

        content.append_text(controls)

        return Panel(
            content,
            title=f"Server Details: {server.name}",
            border_style="cyan",
        )

    def handle_mcp_keys(self, key: str) -> bool:
        """Handle keyboard input for MCP view.

        Args:
            key: The key that was pressed

        Returns:
            True if key was handled, False otherwise
        """
        servers = self.get_filtered_servers()

        # Navigation keys
        if key in ("j", "KEY_DOWN"):
            if servers:
                self.state.selected_index = min(
                    self.state.selected_index + 1, len(servers) - 1
                )
            return True

        elif key in ("k", "KEY_UP"):
            self.state.selected_index = max(0, self.state.selected_index - 1)
            return True

        # Show details
        elif key == "\n" or key == "KEY_ENTER":
            if servers and self.state.selected_index < len(servers):
                self.mcp_selected_server = servers[self.state.selected_index]
                self.mcp_show_details = True
                self.state.status_message = (
                    f"Viewing details for {self.mcp_selected_server.name}"
                )
            return True

        # Back from details
        elif key == "\x1b" or key == "KEY_ESCAPE":  # ESC
            if self.mcp_show_details:
                self.mcp_show_details = False
                self.mcp_selected_server = None
                self.state.status_message = "Back to server list"
                return True
            return False

        # Test server connection
        elif key == "t":
            if servers and self.state.selected_index < len(servers):
                server = servers[self.state.selected_index]
                self.test_mcp_server(server)
            return True

        # View documentation
        elif key == "d":
            if self.mcp_show_details and self.mcp_selected_server:
                self.view_mcp_docs(self.mcp_selected_server)
            elif servers and self.state.selected_index < len(servers):
                server = servers[self.state.selected_index]
                self.view_mcp_docs(server)
            return True

        # Copy config snippet
        elif key == "c":
            if self.mcp_show_details and self.mcp_selected_server:
                self.copy_mcp_config(self.mcp_selected_server)
            elif servers and self.state.selected_index < len(servers):
                server = servers[self.state.selected_index]
                self.copy_mcp_config(server)
            return True

        # Filter servers
        elif key == "/":
            self.state.status_message = "Filter: (enter text, ESC to clear)"
            # TODO: Implement inline filtering
            return True

        # Reload servers
        elif key == "r":
            self.load_mcp_servers()
            self.state.selected_index = 0
            return True

        # Validate configuration
        elif key == "v":
            if self.mcp_show_details and self.mcp_selected_server:
                self.validate_mcp_server(self.mcp_selected_server)
            elif servers and self.state.selected_index < len(servers):
                server = servers[self.state.selected_index]
                self.validate_mcp_server(server)
            return True

        return False

    def test_mcp_server(self, server: MCPServerInfo) -> None:
        """Test connection to MCP server.

        Args:
            server: Server to test

        Note:
            Full MCP protocol testing requires:
            1. Starting the server process
            2. Connecting via stdio
            3. Sending JSON-RPC initialization request
            4. Validating response and capabilities

            This is currently stubbed for future implementation.
        """
        import logging

        logger = logging.getLogger(__name__)
        logger.info(f"MCP Server Test requested: {server.name}")
        logger.debug(f"  Command: {server.command}")
        logger.debug(f"  Args: {server.args}")

        # Validate basic configuration first
        is_valid, errors = server.is_valid()
        if not is_valid:
            error_msg = errors[0] if errors else "Invalid configuration"
            self.state.status_message = f"✗ {server.name}: {error_msg}"
            return

        testing_msg = f"Testing {server.name}..."
        # Surface the testing cue so callers/tests can assert on it
        self.state.status_message = testing_msg

        # Placeholder until full MCP handshake is implemented
        self.state.status_message = (
            f"{testing_msg} ✓ {server.name} config valid (MCP connection test not yet implemented)"
        )

    def view_mcp_docs(self, server: MCPServerInfo) -> None:
        """View documentation for MCP server.

        Args:
            server: Server to view docs for
        """
        if server.docs_path and server.docs_path.exists():
            try:
                # Read first few lines as preview
                lines = server.docs_path.read_text(encoding="utf-8").split("\n")[:10]
                preview = "\n".join(lines)
                self.state.status_message = f"Docs preview: {preview[:100]}..."
            except Exception as e:
                self.state.status_message = f"Error reading docs: {e}"
        else:
            self.state.status_message = f"No documentation found for {server.name}"

    def copy_mcp_config(self, server: MCPServerInfo) -> None:
        """Copy server config snippet to clipboard.

        Args:
            server: Server to copy config for
        """
        try:
            snippet = generate_config_snippet(
                server.name,
                server.command,
                args=server.args if server.args else None,
                env=server.env if server.env else None,
            )
            try:
                subprocess.run(
                    ["pbcopy"],
                    input=snippet.encode("utf-8"),
                    check=True,
                    capture_output=True,
                )
                self.state.status_message = "Config snippet generated and copied to clipboard"
            except FileNotFoundError:
                self.state.status_message = "Error: 'pbcopy' command not found. Clipboard functionality requires macOS."
            except subprocess.CalledProcessError as e:
                self.state.status_message = f"Error copying to clipboard: {e.stderr.decode().strip()}"
            except Exception as e:
                self.state.status_message = f"An unexpected error occurred: {e}"
        except Exception as e:
            self.state.status_message = f"Error generating config: {e}"

    def validate_mcp_server(self, server: MCPServerInfo) -> None:
        """Validate MCP server configuration.

        Args:
            server: Server to validate
        """
        try:
            is_valid, errors, warnings = validate_server_config(server.name)
            if is_valid:
                msg = f"✓ {server.name} configuration is valid"
                if warnings:
                    msg += f" ({len(warnings)} warning(s))"
                self.state.status_message = msg
            else:
                error_summary = errors[0] if errors else "Unknown error"
                self.state.status_message = f"✗ Validation failed: {error_summary}"
        except Exception as e:
            self.state.status_message = f"Error validating server: {e}"
