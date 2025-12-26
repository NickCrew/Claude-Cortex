"""MCP Server Installer - Install and configure MCP servers."""

from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .mcp import add_mcp_server, _get_claude_config_path
from .mcp_registry import (
    MCPServerDefinition,
    PackageManager,
    get_server,
)


@dataclass
class InstallResult:
    """Result of an installation attempt."""
    success: bool
    message: str
    server_name: Optional[str] = None
    warnings: List[str] = field(default_factory=list)


def check_package_manager(pm: PackageManager) -> Tuple[bool, str]:
    """Check if a package manager is available.

    Returns:
        Tuple of (available, path_or_error_message)
    """
    cmd_map = {
        PackageManager.NPX: "npx",
        PackageManager.NPM: "npm",
        PackageManager.PIP: "pip",
        PackageManager.PIPX: "pipx",
        PackageManager.BREW: "brew",
        PackageManager.CARGO: "cargo",
    }

    cmd = cmd_map.get(pm)
    if not cmd:
        return False, f"Unknown package manager: {pm}"

    path = shutil.which(cmd)
    if path:
        return True, path
    return False, f"{cmd} not found in PATH"


def get_available_package_managers() -> Dict[PackageManager, str]:
    """Get all available package managers and their paths."""
    available = {}
    for pm in PackageManager:
        if pm in (PackageManager.BINARY, PackageManager.MANUAL):
            continue
        is_available, path = check_package_manager(pm)
        if is_available:
            available[pm] = path
    return available


def install_package(server: MCPServerDefinition) -> InstallResult:
    """Install the package for an MCP server.

    Returns:
        InstallResult with success status and message
    """
    # Check if package manager is available
    available, path_or_error = check_package_manager(server.package_manager)
    if not available:
        return InstallResult(
            success=False,
            message=f"Package manager not available: {path_or_error}",
        )

    # NPX doesn't need pre-installation
    if server.package_manager == PackageManager.NPX:
        return InstallResult(
            success=True,
            message="NPX packages don't require pre-installation",
            server_name=server.name,
        )

    # Get install command
    install_cmd = server.get_install_command()
    if not install_cmd:
        return InstallResult(
            success=False,
            message=f"No install command for {server.package_manager.value}",
        )

    try:
        # Run installation
        result = subprocess.run(
            install_cmd,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
        )

        if result.returncode == 0:
            return InstallResult(
                success=True,
                message=f"Successfully installed {server.package}",
                server_name=server.name,
            )
        else:
            return InstallResult(
                success=False,
                message=f"Installation failed: {result.stderr or result.stdout}",
            )

    except subprocess.TimeoutExpired:
        return InstallResult(
            success=False,
            message="Installation timed out after 5 minutes",
        )
    except Exception as e:
        return InstallResult(
            success=False,
            message=f"Installation error: {str(e)}",
        )


def configure_server(
    server: MCPServerDefinition,
    env_values: Optional[Dict[str, str]] = None,
    extra_args: Optional[List[str]] = None,
) -> InstallResult:
    """Configure an MCP server in Claude's config.

    Args:
        server: The server definition from the registry
        env_values: Values for required environment variables
        extra_args: Additional arguments to append

    Returns:
        InstallResult with success status and message
    """
    env_values = env_values or {}
    extra_args = extra_args or []

    # Build the configuration
    command = server.get_command()
    args = server.get_default_args() + extra_args

    # Build env dict from provided values
    env = {}
    warnings = []

    for env_var in server.env_vars:
        if env_var.name in env_values:
            env[env_var.name] = env_values[env_var.name]
        elif env_var.default:
            env[env_var.name] = env_var.default
        elif env_var.required:
            warnings.append(f"Missing required env var: {env_var.name}")

    # Add to Claude config
    try:
        success, _ = add_mcp_server(
            name=server.name,
            command=command,
            args=args,
            env=env if env else None,
            description=server.description,
        )

        if success:
            return InstallResult(
                success=True,
                message=f"Successfully configured {server.name}",
                server_name=server.name,
                warnings=warnings,
            )
        else:
            return InstallResult(
                success=False,
                message=f"Failed to add {server.name} to config",
                warnings=warnings,
            )

    except Exception as e:
        return InstallResult(
            success=False,
            message=f"Configuration error: {str(e)}",
            warnings=warnings,
        )


def install_and_configure(
    server: MCPServerDefinition,
    env_values: Optional[Dict[str, str]] = None,
    extra_args: Optional[List[str]] = None,
    skip_install: bool = False,
) -> InstallResult:
    """Install and configure an MCP server.

    This is the main entry point for installing a server from the registry.

    Args:
        server: The server definition from the registry
        env_values: Values for required environment variables
        extra_args: Additional arguments to append
        skip_install: Skip package installation (for NPX or already installed)

    Returns:
        InstallResult with success status and message
    """
    warnings = []

    # Step 1: Install package (if needed)
    if not skip_install and server.package_manager != PackageManager.NPX:
        install_result = install_package(server)
        if not install_result.success:
            return install_result
        warnings.extend(install_result.warnings)

    # Step 2: Configure in Claude
    config_result = configure_server(server, env_values, extra_args)
    config_result.warnings = warnings + config_result.warnings

    return config_result


def install_from_registry(
    server_name: str,
    env_values: Optional[Dict[str, str]] = None,
    extra_args: Optional[List[str]] = None,
) -> InstallResult:
    """Install a server by name from the registry.

    Args:
        server_name: Name of the server in the registry
        env_values: Values for required environment variables
        extra_args: Additional arguments to append

    Returns:
        InstallResult with success status and message
    """
    server = get_server(server_name)
    if not server:
        return InstallResult(
            success=False,
            message=f"Server '{server_name}' not found in registry",
        )

    return install_and_configure(server, env_values, extra_args)


def check_server_installed(server: MCPServerDefinition) -> Tuple[bool, str]:
    """Check if a server is already configured.

    Returns:
        Tuple of (is_configured, status_message)
    """
    config_path = _get_claude_config_path()
    if not config_path or not config_path.exists():
        return False, "Claude config not found"

    try:
        with open(config_path) as f:
            config = json.load(f)

        servers = config.get("mcpServers", {})
        if server.name in servers:
            return True, "Already configured"
        return False, "Not configured"

    except Exception as e:
        return False, f"Error reading config: {e}"


def get_server_requirements(server: MCPServerDefinition) -> Dict[str, Any]:
    """Get the requirements for installing a server.

    Returns dict with:
        - package_manager: Required package manager
        - pm_available: Whether it's installed
        - env_vars: List of required env vars
        - install_notes: Any special instructions
    """
    pm_available, pm_status = check_package_manager(server.package_manager)

    return {
        "package_manager": server.package_manager.value,
        "pm_available": pm_available,
        "pm_status": pm_status,
        "env_vars": [
            {
                "name": ev.name,
                "description": ev.description,
                "required": ev.required,
                "secret": ev.secret,
                "default": ev.default,
            }
            for ev in server.env_vars
        ],
        "install_notes": server.install_notes,
        "post_install_notes": server.post_install_notes,
    }
