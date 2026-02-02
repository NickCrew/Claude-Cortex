"""TUI dialogs package."""

from .asset_dialogs import (
    TargetSelectorDialog,
    AssetDetailDialog,
    DiffViewerDialog,
    BulkInstallDialog,
)

from .memory_dialogs import (
    MemoryNoteDialog,
    MemoryNoteCreateDialog,
)

from .mcp_install_dialogs import (
    MCPBrowseDialog,
    MCPInstallDialog,
)

from .hooks_manager import (
    HooksManagerDialog,
)

from .backup_manager import (
    BackupManagerDialog,
)

from .llm_provider_settings import (
    LLMProviderSettingsDialog,
)

__all__ = [
    "TargetSelectorDialog",
    "AssetDetailDialog",
    "DiffViewerDialog",
    "BulkInstallDialog",
    "MemoryNoteDialog",
    "MemoryNoteCreateDialog",
    "MCPBrowseDialog",
    "MCPInstallDialog",
    "HooksManagerDialog",
    "BackupManagerDialog",
    "LLMProviderSettingsDialog",
]
