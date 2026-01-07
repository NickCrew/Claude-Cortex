"""MCP (Model Context Protocol) server management functionality.

This module provides utilities for discovering, validating, and managing
MCP servers configured in Claude Desktop. It handles:

- Discovering MCP servers from Claude Desktop config
- Parsing server capabilities and documentation
- Validating server configurations
- Generating config snippets for new servers

Cross-platform support for macOS, Linux, and Windows.
"""

from __future__ import annotations

import json
import os
import platform
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from ..exceptions import (
    ClaudeCtxError,
    FileOperationError,
    ValidationError,
    YAMLValidationError,
)
from .base import _resolve_claude_dir


# Platform-specific config paths
def _get_claude_config_path() -> Path:
    """Get the platform-specific Claude Desktop config path.

    Returns:
        Path to claude_desktop_config.json

    Platform paths:
        - macOS: ~/Library/Application Support/Claude/claude_desktop_config.json
        - Linux: ~/.config/Claude/claude_desktop_config.json
        - Windows: %APPDATA%/Claude/claude_desktop_config.json
    """
    system = platform.system()
    home = Path.home()

    if system == "Darwin":  # macOS
        return (
            home
            / "Library"
            / "Application Support"
            / "Claude"
            / "claude_desktop_config.json"
        )
    elif system == "Linux":
        return home / ".config" / "Claude" / "claude_desktop_config.json"
    elif system == "Windows":
        appdata = os.environ.get("APPDATA")
        if appdata:
            return Path(appdata) / "Claude" / "claude_desktop_config.json"
        # Fallback to home directory
        return home / "AppData" / "Roaming" / "Claude" / "claude_desktop_config.json"
    else:
        # Unknown platform - try Linux path as fallback
        return home / ".config" / "Claude" / "claude_desktop_config.json"


@dataclass
class MCPServerInfo:
    """Information about an MCP server configuration.

    Attributes:
        name: Server identifier
        command: Executable command
        args: Command line arguments
        env: Environment variables
        description: Optional server description
        tools: Available tools/capabilities (if known)
        docs_path: Path to local documentation (if available)
    """

    name: str
    command: str
    args: List[str] = field(default_factory=list)
    env: Dict[str, str] = field(default_factory=dict)
    description: str = ""
    tools: List[str] = field(default_factory=list)
    docs_path: Optional[Path] = None
    doc_only: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "command": self.command,
            "args": self.args,
            "env": self.env,
            "description": self.description,
            "tools": self.tools,
            "docs_path": str(self.docs_path) if self.docs_path else None,
            "doc_only": self.doc_only,
        }

    def is_valid(self) -> Tuple[bool, List[str]]:
        """Validate server configuration.

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors: List[str] = []

        if not self.name:
            errors.append("Server name is required")

        if not self.command:
            errors.append("Server command is required")

        # Check if command exists (basic validation)
        if self.command:
            # Handle both absolute paths and command names
            if os.path.isabs(self.command):
                if not Path(self.command).exists():
                    errors.append(f"Command not found: {self.command}")

        return len(errors) == 0, errors


@dataclass
class MCPServerCapabilities:
    """MCP server capabilities and metadata.

    Attributes:
        tools: List of available tool names
        resources: List of available resources
        prompts: List of available prompts
        version: Server/protocol version
        metadata: Additional metadata
    """

    tools: List[str] = field(default_factory=list)
    resources: List[str] = field(default_factory=list)
    prompts: List[str] = field(default_factory=list)
    version: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


# Core MCP management functions


def discover_servers(
    config_path: Optional[Path] = None,
) -> Tuple[bool, List[MCPServerInfo], str]:
    """Discover MCP servers from Claude Desktop config.

    Args:
        config_path: Optional path to config file (uses platform default if None)

    Returns:
        Tuple of (success, servers, error_message)

    Examples:
        >>> success, servers, error = discover_servers()
        >>> if success:
        ...     for server in servers:
        ...         print(f"Found: {server.name}")
    """
    if config_path is None:
        config_path = _get_claude_config_path()

    # Check if config exists
    if not config_path.exists():
        return False, [], f"Config file not found: {config_path}"

    # Read and parse config
    try:
        text = config_path.read_text(encoding="utf-8")
    except OSError as exc:
        return False, [], f"Failed to read config: {exc}"

    try:
        config = json.loads(text)
    except json.JSONDecodeError as exc:
        return False, [], f"Invalid JSON in config: {exc}"

    # Extract MCP servers
    if not isinstance(config, dict):
        return False, [], "Config must be a JSON object"

    mcp_servers = config.get("mcpServers", {})
    if not isinstance(mcp_servers, dict):
        return False, [], "'mcpServers' must be an object"

    servers: List[MCPServerInfo] = []
    for name, server_config in mcp_servers.items():
        if not isinstance(server_config, dict):
            continue

        # Parse server configuration
        command = server_config.get("command", "")
        args = server_config.get("args", [])
        env = server_config.get("env", {})
        description = server_config.get("description", "")

        if not isinstance(args, list):
            args = []
        if not isinstance(env, dict):
            env = {}

        # Try to find documentation
        docs_path = get_server_docs_path(name)

        server = MCPServerInfo(
            name=name,
            command=command,
            args=args,
            env=env,
            description=description,
            docs_path=docs_path,
        )

        servers.append(server)

    return True, servers, ""


def list_doc_only_servers(
    configured_names: Iterable[str],
    claude_dir: Optional[Path] = None,
) -> List[MCPServerInfo]:
    """Return MCP servers that have docs installed but are missing config entries."""

    if claude_dir is None:
        claude_dir = _resolve_claude_dir()

    docs_dir = claude_dir / "mcp" / "docs"
    if not docs_dir.is_dir():
        return []

    configured = {name.lower() for name in configured_names}
    doc_servers: List[MCPServerInfo] = []

    for doc_path in sorted(docs_dir.glob("*.md")):
        name = doc_path.stem
        if name.lower() in configured:
            continue
        doc_servers.append(
            MCPServerInfo(
                name=name,
                command="",
                description="Documentation installed – server not configured",
                docs_path=doc_path,
                doc_only=True,
            )
        )

    return doc_servers


def get_server_info(
    name: str,
    config_path: Optional[Path] = None,
) -> Tuple[bool, Optional[MCPServerInfo], str]:
    """Get details about a specific MCP server.

    Args:
        name: Server name to lookup
        config_path: Optional path to config file

    Returns:
        Tuple of (success, server_info, error_message)

    Examples:
        >>> success, server, error = get_server_info("context7")
        >>> if success and server:
        ...     print(f"Command: {server.command}")
        ...     print(f"Args: {server.args}")
    """
    success, servers, error = discover_servers(config_path)
    if not success:
        return False, None, error

    # Find matching server (case-insensitive)
    name_lower = name.lower()
    for server in servers:
        if server.name.lower() == name_lower:
            return True, server, ""

    available = ", ".join(s.name for s in servers) if servers else "none"
    return False, None, f"Server '{name}' not found. Available: {available}"


def list_server_tools(
    name: str,
    config_path: Optional[Path] = None,
) -> Tuple[bool, List[str], str]:
    """List tools/capabilities provided by an MCP server.

    Note: This requires the server to be running or have cached capabilities.
    For now, this is a placeholder that returns empty list.

    Args:
        name: Server name
        config_path: Optional path to config file

    Returns:
        Tuple of (success, tool_names, error_message)

    Examples:
        >>> success, tools, error = list_server_tools("context7")
        >>> if success:
        ...     for tool in tools:
        ...         print(f"Tool: {tool}")
    """
    success, server, error = get_server_info(name, config_path)
    if not success:
        return False, [], error

    # TODO: Implement actual capability discovery
    # This would require:
    # 1. Starting the MCP server
    # 2. Sending initialization request
    # 3. Querying available tools
    # 4. Caching results for future queries

    # For now, return placeholder
    return True, [], "Tool discovery not yet implemented"


def get_server_docs_path(
    name: str,
    claude_dir: Optional[Path] = None,
) -> Optional[Path]:
    """Find documentation for an MCP server.

    Looks for documentation in ~/.cortex/mcp/docs/{name}.md

    Args:
        name: Server name
        claude_dir: Optional Cortex directory (uses ~/.cortex if None)

    Returns:
        Path to documentation if found, None otherwise

    Examples:
        >>> docs_path = get_server_docs_path("context7")
        >>> if docs_path:
        ...     content = docs_path.read_text()
    """
    if claude_dir is None:
        claude_dir = _resolve_claude_dir()

    # Check mcp/docs directory
    docs_dir = claude_dir / "mcp" / "docs"
    if not docs_dir.is_dir():
        return None

    # Try exact match first
    exact_path = docs_dir / f"{name}.md"
    if exact_path.is_file():
        return exact_path

    # Try case-insensitive match
    name_lower = name.lower()
    for doc_file in docs_dir.glob("*.md"):
        if doc_file.stem.lower() == name_lower:
            return doc_file

    return None


def validate_server_config(
    name: str,
    config_path: Optional[Path] = None,
) -> Tuple[bool, List[str], List[str]]:
    """Validate an MCP server configuration.

    Checks:
    - Server exists in config
    - Command is specified
    - Command is executable (if absolute path)
    - Environment variables are valid

    Args:
        name: Server name to validate
        config_path: Optional path to config file

    Returns:
        Tuple of (is_valid, errors, warnings)

    Examples:
        >>> valid, errors, warnings = validate_server_config("context7")
        >>> if not valid:
        ...     for error in errors:
        ...         print(f"Error: {error}")
    """
    success, server, error = get_server_info(name, config_path)
    if not success:
        return False, [error], []

    if server is None:
        return False, [f"Server '{name}' not found"], []

    # When a config file path is provided, prefer documentation inside the
    # surrounding Claude directory instead of the user's global ~/.cortex. This
    # keeps validation deterministic in tests and for portable configs.
    if config_path is not None:
        override_docs = get_server_docs_path(name, config_path.parent)
        server.docs_path = override_docs

    # Use server's built-in validation
    is_valid, errors = server.is_valid()
    warnings: List[str] = []

    # Additional validation checks
    if server.docs_path is None:
        warnings.append(f"No documentation found for '{name}'")

    # Check environment variables
    if server.env:
        for key, value in server.env.items():
            if not key:
                errors.append("Environment variable name cannot be empty")
            if value == "" or value is None:
                warnings.append(f"Environment variable '{key}' has empty value")

    return len(errors) == 0, errors, warnings


def generate_config_snippet(
    name: str,
    command: str,
    args: Optional[List[str]] = None,
    env: Optional[Dict[str, str]] = None,
    indent: int = 2,
) -> str:
    """Generate a JSON config snippet for an MCP server.

    Args:
        name: Server name
        command: Executable command
        args: Optional command line arguments
        env: Optional environment variables
        indent: JSON indentation level (default: 2)

    Returns:
        JSON string ready to add to mcpServers section

    Examples:
        >>> snippet = generate_config_snippet(
        ...     "myserver",
        ...     "npx",
        ...     args=["-y", "@myorg/mcp-server"],
        ...     env={"API_KEY": "your-key-here"}
        ... )
        >>> print(snippet)
    """
    config: Dict[str, Any] = {
        "command": command,
    }

    if args:
        config["args"] = args

    if env:
        config["env"] = env

    # Create full mcpServers object
    full_config = {"mcpServers": {name: config}}

    # Generate formatted JSON
    json_str = json.dumps(full_config, indent=indent)

    # Add helpful comment
    comment = f"// Add this to your Claude Desktop config under 'mcpServers':"
    return f"{comment}\n{json_str}"


def list_available_servers(
    config_path: Optional[Path] = None,
) -> List[str]:
    """Get list of all available MCP server names.

    Args:
        config_path: Optional path to config file

    Returns:
        List of server names

    Examples:
        >>> servers = list_available_servers()
        >>> print("Available servers:", ", ".join(servers))
    """
    success, servers, error = discover_servers(config_path)
    if not success:
        return []

    return [s.name for s in servers]


def get_server_command_line(
    name: str,
    config_path: Optional[Path] = None,
) -> Tuple[bool, str, str]:
    """Get the full command line for an MCP server.

    Args:
        name: Server name
        config_path: Optional path to config file

    Returns:
        Tuple of (success, command_line, error_message)

    Examples:
        >>> success, cmd, error = get_server_command_line("context7")
        >>> if success:
        ...     print(f"Run with: {cmd}")
    """
    success, server, error = get_server_info(name, config_path)
    if not success or server is None:
        return False, "", error

    # Build command line
    parts = [server.command]
    parts.extend(server.args)

    command_line = " ".join(parts)
    return True, command_line, ""


def export_servers_list(
    config_path: Optional[Path] = None,
    format_type: str = "text",
) -> Tuple[bool, str, str]:
    """Export list of MCP servers in various formats.

    Args:
        config_path: Optional path to config file
        format_type: Output format ("text", "json", "markdown")

    Returns:
        Tuple of (success, output, error_message)

    Examples:
        >>> success, output, error = export_servers_list(format_type="markdown")
        >>> if success:
        ...     print(output)
    """
    success, servers, error = discover_servers(config_path)
    if not success:
        return False, "", error

    if not servers:
        return True, "No MCP servers configured", ""

    if format_type == "json":
        # JSON format
        data = [s.to_dict() for s in servers]
        output = json.dumps(data, indent=2)
        return True, output, ""

    elif format_type == "markdown":
        # Markdown table format
        lines = ["# MCP Servers", ""]
        lines.append("| Name | Command | Args | Docs |")
        lines.append("|------|---------|------|------|")

        for server in servers:
            args_str = " ".join(server.args) if server.args else "-"
            docs_str = "✓" if server.docs_path else "-"
            lines.append(
                f"| {server.name} | `{server.command}` | `{args_str}` | {docs_str} |"
            )

        return True, "\n".join(lines), ""

    else:  # text format (default)
        lines = []
        for server in servers:
            lines.append(f"Server: {server.name}")
            lines.append(f"  Command: {server.command}")
            if server.args:
                lines.append(f"  Args: {' '.join(server.args)}")
            if server.env:
                lines.append(f"  Env vars: {len(server.env)}")
            if server.docs_path:
                lines.append(f"  Docs: {server.docs_path}")
            lines.append("")

        return True, "\n".join(lines), ""


# Convenience exception classes for MCP-specific errors


class MCPConfigError(ClaudeCtxError):
    """Raised when MCP configuration is invalid or missing."""

    def __init__(self, message: str, config_path: Optional[Path] = None):
        recovery_hint = "Check Claude Desktop configuration"
        if config_path:
            recovery_hint = f"Check configuration at: {config_path}"
        super().__init__(message, recovery_hint)
        self.config_path = config_path


class MCPServerNotFoundError(ClaudeCtxError):
    """Raised when requested MCP server is not configured."""

    def __init__(self, server_name: str, available_servers: List[str]):
        available_str = ", ".join(available_servers) if available_servers else "none"
        message = f"MCP server '{server_name}' not found"
        recovery_hint = f"Available servers: {available_str}"
        super().__init__(message, recovery_hint)
        self.server_name = server_name
        self.available_servers = available_servers


# CLI-facing functions


def mcp_list(config_path: Optional[Path] = None) -> Tuple[int, str]:
    """List all MCP servers with status.

    Args:
        config_path: Optional path to config file

    Returns:
        Tuple of (exit_code, message)
    """
    success, servers, error = discover_servers(config_path)
    if not success:
        return 1, f"Error: {error}"

    if not servers:
        return 0, "No MCP servers configured"

    lines = ["MCP Servers:"]
    lines.append("")

    for server in servers:
        # Validate server
        is_valid, errors, warnings = validate_server_config(server.name, config_path)

        status = "✓" if is_valid else "✗"
        lines.append(f"{status} {server.name}")
        lines.append(f"  Command: {server.command}")

        if server.args:
            lines.append(f"  Args: {' '.join(server.args)}")

        if server.env:
            env_keys = ", ".join(server.env.keys())
            lines.append(f"  Env: {env_keys}")

        if server.docs_path:
            lines.append(f"  Docs: {server.docs_path}")

        if not is_valid:
            for err in errors:
                lines.append(f"  Error: {err}")

        if warnings:
            for warn in warnings:
                lines.append(f"  Warning: {warn}")

        lines.append("")

    return 0, "\n".join(lines)


def mcp_show(server_name: str, config_path: Optional[Path] = None) -> Tuple[int, str]:
    """Show detailed server info.

    Args:
        server_name: Server name
        config_path: Optional path to config file

    Returns:
        Tuple of (exit_code, message)
    """
    success, server, error = get_server_info(server_name, config_path)
    if not success or server is None:
        return 1, f"Error: {error}"

    lines = [f"MCP Server: {server.name}"]
    lines.append("")
    lines.append(f"Command: {server.command}")

    if server.args:
        lines.append("Arguments:")
        for arg in server.args:
            lines.append(f"  - {arg}")

    if server.env:
        lines.append("Environment Variables:")
        for key, value in server.env.items():
            lines.append(f"  {key}={value}")

    if server.docs_path:
        lines.append(f"\nDocumentation: {server.docs_path}")

    # Validation status
    is_valid, errors, warnings = validate_server_config(server_name, config_path)
    lines.append("")
    lines.append(f"Status: {'Valid' if is_valid else 'Invalid'}")

    if errors:
        lines.append("\nErrors:")
        for err in errors:
            lines.append(f"  - {err}")

    if warnings:
        lines.append("\nWarnings:")
        for warn in warnings:
            lines.append(f"  - {warn}")

    return 0, "\n".join(lines)


def mcp_docs(server_name: str, config_path: Optional[Path] = None) -> Tuple[int, str]:
    """Display server documentation.

    Args:
        server_name: Server name
        config_path: Optional path to config file

    Returns:
        Tuple of (exit_code, message)
    """
    success, server, error = get_server_info(server_name, config_path)
    if not success or server is None:
        return 1, f"Error: {error}"

    if server.docs_path is None:
        return 1, f"No documentation found for '{server_name}'"

    if not server.docs_path.exists():
        return 1, f"Documentation file not found: {server.docs_path}"

    try:
        content = server.docs_path.read_text(encoding="utf-8")
        return 0, content
    except OSError as exc:
        return 1, f"Failed to read documentation: {exc}"


def mcp_test(server_name: str, config_path: Optional[Path] = None) -> Tuple[int, str]:
    """Test server configuration.

    Args:
        server_name: Server name
        config_path: Optional path to config file

    Returns:
        Tuple of (exit_code, message)
    """
    success, server, error = get_server_info(server_name, config_path)
    if not success or server is None:
        return 1, f"Error: {error}"

    lines = [f"Testing MCP Server: {server.name}"]
    lines.append("")

    # Validation
    is_valid, errors, warnings = validate_server_config(server_name, config_path)

    if is_valid:
        lines.append("✓ Configuration is valid")
    else:
        lines.append("✗ Configuration has errors:")
        for err in errors:
            lines.append(f"  - {err}")

    if warnings:
        lines.append("\nWarnings:")
        for warn in warnings:
            lines.append(f"  - {warn}")

    # Command check
    lines.append("")
    lines.append("Command:")
    success, cmd_line, error = get_server_command_line(server_name, config_path)
    if success:
        lines.append(f"  {cmd_line}")
    else:
        lines.append(f"  Error: {error}")

    # Documentation check
    lines.append("")
    if server.docs_path:
        lines.append(f"✓ Documentation found: {server.docs_path}")
    else:
        lines.append("⚠ No documentation found")

    return 0 if is_valid else 1, "\n".join(lines)


def mcp_diagnose(config_path: Optional[Path] = None) -> Tuple[int, str]:
    """Diagnose all server issues.

    Args:
        config_path: Optional path to config file

    Returns:
        Tuple of (exit_code, message)
    """
    success, servers, error = discover_servers(config_path)
    if not success:
        return 1, f"Error: {error}"

    if not servers:
        return 0, "No MCP servers configured"

    lines = ["MCP Server Diagnostics"]
    lines.append("=" * 60)
    lines.append("")

    all_valid = True
    for server in servers:
        is_valid, errors, warnings = validate_server_config(server.name, config_path)

        if not is_valid:
            all_valid = False

        status = "✓ PASS" if is_valid else "✗ FAIL"
        lines.append(f"{status} {server.name}")

        if errors:
            for err in errors:
                lines.append(f"  Error: {err}")

        if warnings:
            for warn in warnings:
                lines.append(f"  Warning: {warn}")

        if is_valid and not warnings:
            lines.append("  No issues found")

        lines.append("")

    lines.append("=" * 60)
    if all_valid:
        lines.append("All servers are valid ✓")
    else:
        lines.append("Some servers have errors ✗")

    return 0 if all_valid else 1, "\n".join(lines)


def mcp_snippet(
    server_name: str,
    config_path: Optional[Path] = None,
) -> Tuple[int, str]:
    """Generate config snippet.

    Args:
        server_name: Server name
        config_path: Optional path to config file

    Returns:
        Tuple of (exit_code, message)
    """
    success, server, error = get_server_info(server_name, config_path)
    if not success or server is None:
        return 1, f"Error: {error}"

    snippet = generate_config_snippet(
        server.name,
        server.command,
        args=server.args if server.args else None,
        env=server.env if server.env else None,
    )

    return 0, snippet


# Configuration modification functions


def add_mcp_server(
    name: str,
    command: str,
    args: Optional[List[str]] = None,
    env: Optional[Dict[str, str]] = None,
    description: str = "",
    config_path: Optional[Path] = None,
) -> Tuple[bool, str]:
    """Add a new MCP server to the configuration.

    Args:
        name: Server name/identifier
        command: Executable command
        args: Optional command line arguments
        env: Optional environment variables
        description: Optional server description
        config_path: Optional path to config file (uses platform default if None)

    Returns:
        Tuple of (success, message)

    Examples:
        >>> success, msg = add_mcp_server("my-server", "npx", ["-y", "@my/package"])
        >>> if success:
        ...     print("Server added successfully")
    """
    if config_path is None:
        config_path = _get_claude_config_path()

    # Validate inputs
    if not name:
        return False, "Server name is required"
    if not command:
        return False, "Server command is required"

    # Read existing config
    try:
        if config_path.exists():
            text = config_path.read_text(encoding="utf-8")
            config = json.loads(text)
        else:
            config = {}
    except (OSError, json.JSONDecodeError) as exc:
        return False, f"Failed to read config: {exc}"

    # Ensure mcpServers section exists
    if "mcpServers" not in config:
        config["mcpServers"] = {}

    # Check if server already exists
    if name in config["mcpServers"]:
        return False, f"Server '{name}' already exists. Use update to modify it."

    # Create server config
    server_config: Dict[str, Any] = {
        "command": command,
    }
    if args:
        server_config["args"] = args
    if env:
        server_config["env"] = env
    if description:
        server_config["description"] = description

    # Add server to config
    config["mcpServers"][name] = server_config

    # Write config back
    try:
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
        return True, f"Added server '{name}'"
    except OSError as exc:
        return False, f"Failed to write config: {exc}"


def remove_mcp_server(
    name: str,
    config_path: Optional[Path] = None,
) -> Tuple[bool, str]:
    """Remove an MCP server from the configuration.

    Args:
        name: Server name to remove
        config_path: Optional path to config file (uses platform default if None)

    Returns:
        Tuple of (success, message)

    Examples:
        >>> success, msg = remove_mcp_server("my-server")
        >>> if success:
        ...     print("Server removed successfully")
    """
    if config_path is None:
        config_path = _get_claude_config_path()

    if not config_path.exists():
        return False, f"Config file not found: {config_path}"

    # Read config
    try:
        text = config_path.read_text(encoding="utf-8")
        config = json.loads(text)
    except (OSError, json.JSONDecodeError) as exc:
        return False, f"Failed to read config: {exc}"

    # Check if mcpServers section exists
    if "mcpServers" not in config or not isinstance(config["mcpServers"], dict):
        return False, "No MCP servers configured"

    # Check if server exists
    if name not in config["mcpServers"]:
        return False, f"Server '{name}' not found"

    # Remove server
    del config["mcpServers"][name]

    # Write config back
    try:
        config_path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
        return True, f"Removed server '{name}'"
    except OSError as exc:
        return False, f"Failed to write config: {exc}"


def update_mcp_server(
    name: str,
    command: Optional[str] = None,
    args: Optional[List[str]] = None,
    env: Optional[Dict[str, str]] = None,
    description: Optional[str] = None,
    config_path: Optional[Path] = None,
) -> Tuple[bool, str]:
    """Update an existing MCP server configuration.

    Args:
        name: Server name to update
        command: Optional new command
        args: Optional new arguments (None to keep existing)
        env: Optional new environment (None to keep existing)
        description: Optional new description (None to keep existing)
        config_path: Optional path to config file (uses platform default if None)

    Returns:
        Tuple of (success, message)

    Examples:
        >>> success, msg = update_mcp_server("my-server", description="Updated desc")
        >>> if success:
        ...     print("Server updated successfully")
    """
    if config_path is None:
        config_path = _get_claude_config_path()

    if not config_path.exists():
        return False, f"Config file not found: {config_path}"

    # Read config
    try:
        text = config_path.read_text(encoding="utf-8")
        config = json.loads(text)
    except (OSError, json.JSONDecodeError) as exc:
        return False, f"Failed to read config: {exc}"

    # Check if mcpServers section exists
    if "mcpServers" not in config or not isinstance(config["mcpServers"], dict):
        return False, "No MCP servers configured"

    # Check if server exists
    if name not in config["mcpServers"]:
        return False, f"Server '{name}' not found"

    # Update server config
    server_config = config["mcpServers"][name]
    if command is not None:
        server_config["command"] = command
    if args is not None:
        server_config["args"] = args
    if env is not None:
        server_config["env"] = env
    if description is not None:
        server_config["description"] = description

    # Write config back
    try:
        config_path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
        return True, f"Updated server '{name}'"
    except OSError as exc:
        return False, f"Failed to write config: {exc}"


# ---------------------------------------------------------------------------
# MCP Docs Activation (reference-based, controls CLAUDE.md inclusion)
# ---------------------------------------------------------------------------

from .components import ref_activate, ref_deactivate, ref_list, ref_status

MCP_COMPONENT_TYPE = "mcp"
MCP_BASE_PATH = "mcp/docs"


def mcp_activate(name: str, home: Path | None = None) -> Tuple[int, str]:
    """Activate an MCP doc by adding it to .active-mcp.

    This controls which MCP documentation is included in CLAUDE.md.
    """
    return ref_activate(MCP_COMPONENT_TYPE, name, MCP_BASE_PATH, home)


def mcp_deactivate(name: str, home: Path | None = None) -> Tuple[int, str]:
    """Deactivate an MCP doc by removing it from .active-mcp."""
    return ref_deactivate(MCP_COMPONENT_TYPE, name, home)


def mcp_list_docs(home: Path | None = None) -> str:
    """List all MCP docs with their activation status."""
    return ref_list(MCP_COMPONENT_TYPE, MCP_BASE_PATH, home)


def mcp_docs_status(home: Path | None = None) -> str:
    """Show currently active MCP docs."""
    return ref_status(MCP_COMPONENT_TYPE, home)
