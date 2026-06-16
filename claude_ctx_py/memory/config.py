"""Configuration management for memory capture system.

Handles:
- Vault path resolution
- Auto-capture state
- Default settings
"""

import json
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..core.base import _CORTEX_SCOPE_ENV, _resolve_claude_dir


CONFIG_FILE_NAME = "memory-config.json"


@dataclass
class AutoCaptureConfig:
    """Auto-capture settings."""

    enabled: bool = False
    min_session_length: int = 5
    exclude_patterns: List[str] = field(
        default_factory=lambda: ["explain", "what is", "how do"]
    )
    last_capture: Optional[str] = None


@dataclass
class MemoryDefaults:
    """Default values for memory operations."""

    tags: List[str] = field(default_factory=list)
    project: Optional[str] = None


@dataclass
class MemoryConfig:
    """Memory capture configuration."""

    # None means "not explicitly configured" — get_vault_path() then falls
    # back to the scope-aware default. A persisted non-null value (including
    # the legacy "~/basic-memory") is always honoured, so existing configs
    # keep their vault.
    vault_path: Optional[str] = None
    auto_capture: AutoCaptureConfig = field(default_factory=AutoCaptureConfig)
    defaults: MemoryDefaults = field(default_factory=MemoryDefaults)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "vault_path": self.vault_path,
            "auto_capture": asdict(self.auto_capture),
            "defaults": asdict(self.defaults),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryConfig":
        """Create from dictionary."""
        auto_capture_data = data.get("auto_capture", {})
        defaults_data = data.get("defaults", {})

        return cls(
            vault_path=data.get("vault_path"),
            auto_capture=AutoCaptureConfig(
                enabled=auto_capture_data.get("enabled", False),
                min_session_length=auto_capture_data.get("min_session_length", 5),
                exclude_patterns=auto_capture_data.get(
                    "exclude_patterns", ["explain", "what is", "how do"]
                ),
                last_capture=auto_capture_data.get("last_capture"),
            ),
            defaults=MemoryDefaults(
                tags=defaults_data.get("tags", []),
                project=defaults_data.get("project"),
            ),
        )


def _get_claude_dir() -> Path:
    """Get the Claude configuration directory."""
    return _resolve_claude_dir()


def _get_config_path() -> Path:
    """Get the path to the memory config file."""
    return _get_claude_dir() / CONFIG_FILE_NAME


def get_config() -> MemoryConfig:
    """Load memory configuration from file.

    Returns:
        MemoryConfig instance (defaults if file doesn't exist)
    """
    config_path = _get_config_path()

    if not config_path.exists():
        return MemoryConfig()

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return MemoryConfig.from_dict(data)
    except (json.JSONDecodeError, OSError):
        return MemoryConfig()


def save_config(config: MemoryConfig) -> None:
    """Save memory configuration to file.

    Args:
        config: MemoryConfig instance to save
    """
    config_path = _get_config_path()

    # Ensure directory exists
    config_path.parent.mkdir(parents=True, exist_ok=True)

    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config.to_dict(), f, indent=2)


def _default_vault_path(scope: Optional[str] = None) -> Path:
    """Resolve the default vault location from the active cortex scope.

    - ``project`` / ``local``: ``<project-root>/.cortex/vault``
    - ``global`` / ``home`` / ``auto`` (default): ``~/.cortex/vault``

    The project root is located the same way the rest of cortex resolves
    project scope — by walking up to the nearest ``.claude`` — so the vault
    lands beside the project's other cortex state (``.cortex/manifest.yaml``)
    rather than at an unrelated cwd.

    Args:
        scope: Explicit scope override; falls back to ``CORTEX_SCOPE``.

    Returns:
        Resolved Path to the default vault directory.
    """
    scope_value = (scope or os.environ.get(_CORTEX_SCOPE_ENV) or "auto").strip().lower()
    if scope_value in ("project", "local"):
        project_root = _resolve_claude_dir(scope="project").parent
        return project_root / ".cortex" / "vault"
    return Path.home() / ".cortex" / "vault"


def get_vault_path(config: Optional[MemoryConfig] = None) -> Path:
    """Get the resolved vault path.

    Checks, in order:
    1. ``CORTEX_MEMORY_VAULT`` environment variable
    2. Explicit ``vault_path`` set in the config file
    3. Scope-aware default (``.cortex/vault`` — see :func:`_default_vault_path`)

    Args:
        config: Optional config to use (loads if not provided)

    Returns:
        Resolved Path to vault directory
    """
    # Environment override
    if "CORTEX_MEMORY_VAULT" in os.environ:
        return Path(os.environ["CORTEX_MEMORY_VAULT"]).expanduser()

    # Explicit config setting
    if config is None:
        config = get_config()
    if config.vault_path:
        return Path(config.vault_path).expanduser()

    # Scope-aware default
    return _default_vault_path()


def ensure_vault_structure(vault_path: Optional[Path] = None) -> Path:
    """Ensure the vault directory structure exists.

    Creates:
        vault/
        ├── knowledge/
        ├── projects/
        ├── sessions/
        └── fixes/

    Args:
        vault_path: Optional explicit vault path

    Returns:
        Path to vault directory
    """
    if vault_path is None:
        vault_path = get_vault_path()

    subdirs = ["knowledge", "projects", "sessions", "fixes"]

    for subdir in subdirs:
        (vault_path / subdir).mkdir(parents=True, exist_ok=True)

    return vault_path


def is_auto_capture_enabled(config: Optional[MemoryConfig] = None) -> bool:
    """Check if auto-capture is enabled.

    Args:
        config: Optional config to use (loads if not provided)

    Returns:
        True if auto-capture is enabled
    """
    if config is None:
        config = get_config()

    return config.auto_capture.enabled


def set_auto_capture_enabled(enabled: bool) -> MemoryConfig:
    """Enable or disable auto-capture.

    Args:
        enabled: Whether to enable auto-capture

    Returns:
        Updated MemoryConfig
    """
    config = get_config()
    config.auto_capture.enabled = enabled

    if enabled:
        config.auto_capture.last_capture = None

    save_config(config)
    return config


def update_last_capture(timestamp: Optional[datetime] = None) -> None:
    """Update the last capture timestamp.

    Args:
        timestamp: Capture timestamp (defaults to now)
    """
    if timestamp is None:
        timestamp = datetime.now()

    config = get_config()
    config.auto_capture.last_capture = timestamp.isoformat()
    save_config(config)


def get_last_capture() -> Optional[datetime]:
    """Get the last capture timestamp.

    Returns:
        Last capture datetime or None if never captured
    """
    config = get_config()

    if config.auto_capture.last_capture is None:
        return None

    try:
        return datetime.fromisoformat(config.auto_capture.last_capture)
    except ValueError:
        return None
