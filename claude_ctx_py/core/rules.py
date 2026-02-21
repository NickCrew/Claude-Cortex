"""Rule management functions (file-based activation)."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Optional, Tuple

from .base import _resolve_cortex_root, _resolve_claude_dir
from .components import (
    component_activate,
    component_deactivate,
    list_components,
    component_status,
    add_component_to_claude_md,
    get_all_available_components,
)

COMPONENT_TYPE = "rules"
DEFAULT_RULES_SUBDIR = Path.home() / ".claude" / "rules" / "cortex"


def _ensure_symlink(source: Path, target: Path) -> Optional[str]:
    """Create a symlink, returning a warning if it fails."""
    if target.exists() or target.is_symlink():
        if target.is_symlink() and target.resolve() == source.resolve():
            return None
        if target.is_symlink():
            target.unlink()
        else:
            return f"Skipping non-symlink rule file: {target}"
    target.symlink_to(source)
    return None


def _ensure_rules_gitignore(claude_home: Path) -> Optional[str]:
    """Add rules/cortex/ to .claude/.gitignore if not present."""
    gitignore_path = claude_home / ".gitignore"
    entry = "rules/cortex/"
    try:
        if gitignore_path.exists():
            content = gitignore_path.read_text(encoding="utf-8").splitlines()
            if entry in content:
                return None
            content.append(entry)
            gitignore_path.write_text("\n".join(content).rstrip() + "\n", encoding="utf-8")
        else:
            gitignore_path.write_text(entry + "\n", encoding="utf-8")
    except OSError as exc:
        return f"Failed to update {gitignore_path}: {exc}"
    return None


def sync_rule_symlinks(
    rules_root: Path,
    active_rules: Iterable[str],
    target_dir: Path = DEFAULT_RULES_SUBDIR,
    fallback_root: Optional[Path] = None,
) -> Tuple[int, List[str]]:
    """Sync active rule symlinks into ~/.claude/rules/cortex/.

    Args:
        rules_root: Directory containing rules/ subdirectory
        active_rules: List of rule names (without .md extension)
        target_dir: Target symlink directory
        fallback_root: Fallback directory to search for rules

    Returns:
        Tuple of (exit_code, list of messages)
    """
    messages: List[str] = []
    target_dir.mkdir(parents=True, exist_ok=True)
    active_set = {rule.strip() for rule in active_rules if rule.strip()}
    expected = {f"{rule}.md" for rule in active_set}

    existing = {path.name: path for path in target_dir.glob("*.md")}
    # Remove stale symlinks only
    for name, path in existing.items():
        if name in expected:
            continue
        if path.is_symlink():
            path.unlink()
            messages.append(f"Removed rule link: {name}")

    # Ensure active symlinks exist
    for rule in sorted(active_set):
        source = rules_root / "rules" / f"{rule}.md"
        if not source.is_file() and fallback_root is not None:
            fallback = fallback_root / "rules" / f"{rule}.md"
            if fallback.is_file():
                source = fallback
        if not source.is_file():
            messages.append(f"Missing rule file: {source}")
            continue
        target = target_dir / source.name
        warn = _ensure_symlink(source, target)
        if warn:
            messages.append(warn)

    gitignore_warning = _ensure_rules_gitignore(target_dir.parent.parent)
    if gitignore_warning:
        messages.append(gitignore_warning)
    return 0, messages


def _get_all_available_rules(claude_dir: Path) -> List[str]:
    """Get all rule files from the rules directory."""
    return get_all_available_components(claude_dir, COMPONENT_TYPE)


def rules_activate(rule: str, home: Path | None = None) -> str:
    """Activate a rule by moving it into the active rules directory.

    For CORTEX_ROOT editable installs, moves from CORTEX_ROOT/inactive/rules.
    Otherwise, moves from claude_dir/inactive/rules.
    """
    # First try to activate from CORTEX_ROOT/inactive (editable install)
    cortex_root = _resolve_cortex_root()
    inactive_file = cortex_root / "inactive" / "rules" / f"{rule}.md"

    if inactive_file.exists():
        # Activate from CORTEX_ROOT/inactive
        active_dir = cortex_root / "rules"
        active_dir.mkdir(parents=True, exist_ok=True)
        rule_file = active_dir / f"{rule}.md"
        try:
            inactive_file.rename(rule_file)
            return f"✓ Activated rule: {rule}"
        except OSError as e:
            return f"✗ Failed to activate rule: {e}"

    # Fall back to activating from claude_dir (default behavior)
    exit_code, message = component_activate(COMPONENT_TYPE, rule, home)
    return message


def rules_deactivate(rule: str, home: Path | None = None) -> str:
    """Deactivate a rule by moving it into the inactive rules directory.

    For CORTEX_ROOT editable installs, moves from CORTEX_ROOT/rules.
    Otherwise, moves from claude_dir/rules.
    """
    # First try to deactivate from CORTEX_ROOT (editable install)
    cortex_root = _resolve_cortex_root()
    rule_file = cortex_root / "rules" / f"{rule}.md"

    if rule_file.exists():
        # Deactivate from CORTEX_ROOT
        inactive_dir = cortex_root / "inactive" / "rules"
        inactive_dir.mkdir(parents=True, exist_ok=True)
        inactive_file = inactive_dir / f"{rule}.md"
        try:
            rule_file.rename(inactive_file)
            return f"✓ Deactivated rule: {rule}"
        except OSError as e:
            return f"✗ Failed to deactivate rule: {e}"

    # Fall back to deactivating from claude_dir (default behavior)
    exit_code, message = component_deactivate(COMPONENT_TYPE, rule, home)
    return message


def list_rules(home: Path | None = None) -> str:
    """List all rules with their status from filesystem state."""
    return list_components(COMPONENT_TYPE, home)


def rules_status(home: Path | None = None) -> str:
    """Show currently active rules from filesystem state."""
    return component_status(COMPONENT_TYPE, home)


def rule_add_to_claude_md(
    rule: str,
    active: bool = False,
    home: Path | None = None
) -> Tuple[int, str]:
    """Legacy helper; validates rule exists on disk."""
    return add_component_to_claude_md(COMPONENT_TYPE, rule, "", active, home)
