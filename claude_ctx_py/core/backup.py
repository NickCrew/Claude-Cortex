"""Backup and restore functionality for ~/.cortex directory."""

from __future__ import annotations

import shutil
import tarfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

from .base import _resolve_claude_dir, _color, GREEN, YELLOW, RED, BLUE


@dataclass
class BackupInfo:
    """Information about a backup."""

    path: Path
    name: str
    created: datetime
    size_bytes: int
    size_human: str


def get_backup_dir() -> Path:
    """Get the backup directory."""
    claude_dir = _resolve_claude_dir()
    backup_dir = claude_dir / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    return backup_dir


def format_size(size_bytes: int) -> str:
    """Format byte size to human readable."""
    size = float(size_bytes)
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


def create_backup(
    name: Optional[str] = None,
    include_backups: bool = False,
) -> Tuple[bool, str, Optional[BackupInfo]]:
    """Create a backup of ~/.cortex.

    Args:
        name: Optional custom name for the backup
        include_backups: If True, include the backups directory itself

    Returns:
        Tuple of (success, message, backup_info)
    """
    claude_dir = _resolve_claude_dir()
    backup_dir = get_backup_dir()

    # Generate backup name
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if name:
        backup_name = f"{name}_{timestamp}.tar.gz"
    else:
        backup_name = f"claude_backup_{timestamp}.tar.gz"

    backup_path = backup_dir / backup_name

    try:
        with tarfile.open(backup_path, "w:gz") as tar:
            for item in claude_dir.iterdir():
                # Skip backups directory unless requested
                if item.name == "backups" and not include_backups:
                    continue
                # Skip temporary files
                if item.name.startswith(".") and item.name.endswith(".tmp"):
                    continue
                # Add to archive
                tar.add(item, arcname=item.name)

        # Get backup info
        size_bytes = backup_path.stat().st_size
        backup_info = BackupInfo(
            path=backup_path,
            name=backup_name,
            created=datetime.now(),
            size_bytes=size_bytes,
            size_human=format_size(size_bytes),
        )

        return True, _color(f"Created backup: {backup_name} ({backup_info.size_human})", GREEN), backup_info

    except Exception as e:
        return False, _color(f"Failed to create backup: {e}", RED), None


def list_backups() -> List[BackupInfo]:
    """List all available backups.

    Returns:
        List of BackupInfo objects, sorted by creation time (newest first)
    """
    backup_dir = get_backup_dir()
    backups: List[BackupInfo] = []

    for backup_file in backup_dir.glob("*.tar.gz"):
        try:
            stat = backup_file.stat()
            created = datetime.fromtimestamp(stat.st_mtime)
            size_bytes = stat.st_size

            backups.append(
                BackupInfo(
                    path=backup_file,
                    name=backup_file.name,
                    created=created,
                    size_bytes=size_bytes,
                    size_human=format_size(size_bytes),
                )
            )
        except OSError:
            continue

    # Sort by creation time (newest first)
    backups.sort(key=lambda b: b.created, reverse=True)
    return backups


def restore_backup(
    backup: BackupInfo,
    overwrite: bool = False,
) -> Tuple[bool, str]:
    """Restore from a backup.

    Args:
        backup: BackupInfo of the backup to restore
        overwrite: If True, overwrite existing files without confirmation

    Returns:
        Tuple of (success, message)
    """
    claude_dir = _resolve_claude_dir()
    backup_dir = get_backup_dir()

    if not backup.path.exists():
        return False, _color(f"Backup not found: {backup.name}", RED)

    try:
        # Create a pre-restore backup first
        pre_restore_name = f"pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        success, msg, _ = create_backup(name=pre_restore_name)
        if not success:
            return False, _color(f"Failed to create pre-restore backup: {msg}", RED)

        # Extract backup
        with tarfile.open(backup.path, "r:gz") as tar:
            # Check for unsafe paths
            for member in tar.getmembers():
                if member.name.startswith("/") or ".." in member.name:
                    return False, _color(f"Unsafe path in backup: {member.name}", RED)

            # Extract to temp directory first
            temp_dir = claude_dir / ".restore_temp"
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
            temp_dir.mkdir()

            tar.extractall(temp_dir)

            # Move files from temp to claude_dir
            for item in temp_dir.iterdir():
                target = claude_dir / item.name
                # Skip backups directory
                if item.name == "backups":
                    continue

                if target.exists():
                    if target.is_dir():
                        shutil.rmtree(target)
                    else:
                        target.unlink()

                shutil.move(str(item), str(target))

            # Cleanup temp directory
            shutil.rmtree(temp_dir)

        return True, _color(f"Restored from backup: {backup.name}", GREEN)

    except Exception as e:
        return False, _color(f"Failed to restore backup: {e}", RED)


def delete_backup(backup: BackupInfo) -> Tuple[bool, str]:
    """Delete a backup.

    Args:
        backup: BackupInfo of the backup to delete

    Returns:
        Tuple of (success, message)
    """
    try:
        backup.path.unlink()
        return True, _color(f"Deleted backup: {backup.name}", GREEN)
    except Exception as e:
        return False, _color(f"Failed to delete backup: {e}", RED)


def get_backup_summary() -> str:
    """Get a summary of available backups.

    Returns:
        Formatted summary string
    """
    backups = list_backups()

    if not backups:
        return _color("No backups available", YELLOW)

    lines = [_color(f"Found {len(backups)} backup(s):", BLUE)]
    total_size = 0

    for backup in backups[:10]:  # Show latest 10
        created_str = backup.created.strftime("%Y-%m-%d %H:%M")
        lines.append(f"  {backup.name} ({backup.size_human}) - {created_str}")
        total_size += backup.size_bytes

    if len(backups) > 10:
        lines.append(f"  ... and {len(backups) - 10} more")

    lines.append(f"\nTotal size: {format_size(total_size)}")
    return "\n".join(lines)


def auto_cleanup_backups(max_count: int = 10, max_age_days: int = 30) -> Tuple[int, str]:
    """Automatically clean up old backups.

    Args:
        max_count: Maximum number of backups to keep
        max_age_days: Maximum age in days to keep backups

    Returns:
        Tuple of (deleted_count, message)
    """
    backups = list_backups()
    deleted = 0
    cutoff_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    cutoff_date = cutoff_date.replace(day=cutoff_date.day - max_age_days)

    # Keep at least max_count backups, but delete old ones beyond that
    for i, backup in enumerate(backups):
        if i >= max_count or backup.created < cutoff_date:
            success, _ = delete_backup(backup)
            if success:
                deleted += 1

    if deleted > 0:
        return deleted, _color(f"Cleaned up {deleted} old backup(s)", GREEN)
    return 0, _color("No backups needed cleanup", YELLOW)
