"""Asset installer for plugin resources.

Handles installation, uninstallation, and updating of assets
in cortex directories.
"""

from __future__ import annotations

import difflib
import json
import shutil
import tempfile
from pathlib import Path
from typing import List, Optional, Tuple

import logging
from .asset_discovery import Asset, AssetCategory
from .base import _update_with_backup, _extract_front_matter
from .hooks import parse_hook_file

# Set up file logging for debugging
_log_path = Path.home() / ".cortex" / "logs" / "asset_copy.log"
_logger = logging.getLogger("asset_installer")
_logger.setLevel(logging.DEBUG)
if not _logger.handlers:
    _handler = logging.FileHandler(_log_path)
    _handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    _logger.addHandler(_handler)


# Color codes for output
BLUE = "\033[34m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
NC = "\033[0m"


def _color(text: str, color: str) -> str:
    """Wrap text in ANSI color codes."""
    return f"{color}{text}{NC}"


def _add_commented_reference(target_dir: Path, installed_path: Path) -> None:
    """Add a commented CLAUDE.md reference to an installed asset file.

    This helps users quickly enable the asset later by uncommenting the line.
    The update is best-effort and never raises.
    """

    claude_md = target_dir / "CLAUDE.md"

    # Only proceed when CLAUDE.md and the installed file exist
    if not claude_md.is_file() or not installed_path.exists():
        return

    try:
        rel_path = installed_path.relative_to(target_dir)
    except ValueError:
        rel_path = installed_path

    reference = rel_path.as_posix()
    comment_line = f"<!-- @{reference} -->"

    try:
        content = claude_md.read_text(encoding="utf-8")
    except OSError:
        return

    # Skip if already present (commented or active)
    if f"@{reference}" in content:
        return

    # Ensure trailing newline before appending
    if content and not content.endswith("\n"):
        content += "\n"

    content += f"{comment_line}\n"

    try:
        _update_with_backup(claude_md, lambda _: content)
    except Exception:
        # Reference addition is best-effort; ignore failures
        return


def install_asset(
    asset: Asset,
    target_dir: Path,
    activate: bool = True,
    *,
    add_claude_refs: bool = True,
    register_hooks: bool = True,
    use_copy: bool = False,
) -> Tuple[int, str]:
    """Install an asset to a target directory.

    Args:
        asset: Asset to install
        target_dir: Target directory
        activate: For agents/modes, whether to install as active
        add_claude_refs: When True, append commented reference to CLAUDE.md
        register_hooks: When True, register hooks in settings.json
        use_copy: When True, copy the file instead of symlinking (agents only)

    Returns:
        Tuple of (exit_code, message)
    """
    try:
        if asset.category == AssetCategory.SKILLS:
            return _install_skill(asset, target_dir, add_claude_refs=add_claude_refs)
        elif asset.category == AssetCategory.HOOKS:
            return _install_hook(asset, target_dir, add_claude_refs=add_claude_refs, register_hooks=register_hooks)
        elif asset.category == AssetCategory.COMMANDS:
            return _install_command(asset, target_dir, add_claude_refs=add_claude_refs)
        elif asset.category == AssetCategory.AGENTS:
            if use_copy:
                return _copy_agent(asset, target_dir, add_claude_refs=add_claude_refs)
            return _install_agent(asset, target_dir, activate, add_claude_refs=add_claude_refs)
        elif asset.category == AssetCategory.MODES:
            return _install_mode(asset, target_dir, activate, add_claude_refs=add_claude_refs)
        elif asset.category == AssetCategory.WORKFLOWS:
            return _install_workflow(asset, target_dir, add_claude_refs=add_claude_refs)
        elif asset.category == AssetCategory.RULES:
            return _install_rule(asset, target_dir, add_claude_refs=add_claude_refs)
        elif asset.category == AssetCategory.FLAGS:
            return _install_flag(asset, target_dir)
        elif asset.category == AssetCategory.PROFILES:
            return _install_profile(asset, target_dir, add_claude_refs=add_claude_refs)
        elif asset.category == AssetCategory.SCENARIOS:
            return _install_scenario(asset, target_dir, add_claude_refs=add_claude_refs)
        elif asset.category == AssetCategory.TASKS:
            return _install_task(asset, target_dir, add_claude_refs=add_claude_refs)
        else:
            return _install_setting(asset, target_dir)
    except Exception as e:
        return 1, _color(f"Copy failed: {e}", RED)


def _install_skill(asset: Asset, target_dir: Path, *, add_claude_refs: bool = True) -> Tuple[int, str]:
    """Symlink a skill directory."""
    try:
        # Validate source exists before attempting symlink
        if not asset.source_path.exists():
            return 1, _color(f"Skill source not found: {asset.source_path}", RED)

        skills_dir = target_dir / "skills"
        skills_dir.mkdir(parents=True, exist_ok=True)

        target_skill_dir = skills_dir / asset.name

        # Remove existing file or symlink if present
        if target_skill_dir.exists() or target_skill_dir.is_symlink():
            if target_skill_dir.is_symlink():
                target_skill_dir.unlink()
            else:
                shutil.rmtree(target_skill_dir)

        # Create symlink to source skill directory
        target_skill_dir.symlink_to(asset.source_path)

        # Add commented reference to SKILL.md for easy activation
        if add_claude_refs:
            _add_commented_reference(target_dir, target_skill_dir / "SKILL.md")

        return 0, _color(f"Installed skill (symlink): {asset.name}", GREEN)
    except (OSError, PermissionError) as e:
        return 1, _color(f"Failed to create skill symlink: {e}", RED)


def _install_hook(asset: Asset, target_dir: Path, *, add_claude_refs: bool = True, register_hooks: bool = True) -> Tuple[int, str]:
    """Symlink a hook to ~/.claude/hooks/ and register in settings.json."""
    _logger.info(f"_install_hook called: asset.name={asset.name}, target_dir={target_dir}")

    try:
        if not asset.source_path.exists():
            _logger.error(f"Hook source file not found: {asset.source_path}")
            return 1, _color(f"Hook source file not found: {asset.source_path}", RED)

        hooks_dir = target_dir / "hooks"
        hooks_dir.mkdir(parents=True, exist_ok=True)

        target_path = hooks_dir / asset.source_path.name
        _logger.debug(f"target_path={target_path}")

        # Remove existing file or symlink if present
        if target_path.exists() or target_path.is_symlink():
            _logger.debug(f"Removing existing file/symlink at {target_path}")
            target_path.unlink()

        # Create symlink
        _logger.debug(f"Creating symlink from {target_path} to {asset.source_path}")
        target_path.symlink_to(asset.source_path)
        _logger.debug("Symlink created successfully")

        if add_claude_refs:
            _add_commented_reference(target_dir, target_path)

        if register_hooks:
            # Parse the hook file to get the event type
            hook_def = parse_hook_file(asset.source_path)
            _logger.debug(f"Parsed hook_def: {hook_def}")

            if hook_def:
                # Determine interpreter from file extension
                interpreter = "bash" if target_path.suffix == ".sh" else "python3"
                hook_command = f"{interpreter} {target_path}"
                _logger.debug(f"hook_command={hook_command}, event={hook_def.event}")

                # Register in settings.json
                settings_path = target_dir / "settings.json"
                _logger.info(f"Registering hook in settings: {settings_path}")
                exit_code, reg_msg = register_hook_in_settings(
                    asset.name, hook_command, hook_def.event, settings_path
                )
                _logger.info(f"register_hook_in_settings returned: exit_code={exit_code}, msg={reg_msg}")

                if exit_code != 0:
                    return 0, _color(f"Installed hook: {asset.name} (settings registration failed: {reg_msg})", YELLOW)
            else:
                _logger.warning("Could not parse hook file, skipping settings registration")

        _logger.info(f"Successfully installed hook: {asset.name}")
        return 0, _color(f"Installed hook: {asset.name}", GREEN)
    except Exception as e:
        _logger.exception(f"Exception in _install_hook: {e}")
        return 1, _color(f"Failed to install hook: {e}", RED)


def _install_command(asset: Asset, target_dir: Path, *, add_claude_refs: bool = True) -> Tuple[int, str]:
    """Copy a slash command."""
    commands_dir = target_dir / "commands"

    if asset.namespace:
        target_subdir = commands_dir / asset.namespace
        target_subdir.mkdir(parents=True, exist_ok=True)
        target_path = target_subdir / asset.source_path.name
    else:
        commands_dir.mkdir(parents=True, exist_ok=True)
        target_path = commands_dir / asset.source_path.name

    shutil.copy2(asset.source_path, target_path)

    if add_claude_refs:
        _add_commented_reference(target_dir, target_path)

    return 0, _color(f"Copied command: {asset.display_name}", GREEN)


def _install_agent(asset: Asset, target_dir: Path, activate: bool, *, add_claude_refs: bool = True) -> Tuple[int, str]:
    """Symlink an agent file to active agents directory.

    Note: The activate parameter is deprecated and ignored. Symlink presence
    determines activation state. Symlinks are always created in agents/.
    """
    try:
        # Validate source exists before attempting symlink
        if not asset.source_path.exists():
            return 1, _color(f"Agent source not found: {asset.source_path}", RED)

        agents_dir = target_dir / "agents"
        agents_dir.mkdir(parents=True, exist_ok=True)
        target_path = agents_dir / asset.source_path.name

        # Remove existing file or symlink if present
        if target_path.exists() or target_path.is_symlink():
            if target_path.is_symlink():
                target_path.unlink()
            else:
                target_path.unlink()

        # Create symlink to source agent file
        target_path.symlink_to(asset.source_path)

        if add_claude_refs:
            _add_commented_reference(target_dir, target_path)

        return 0, _color(f"Installed agent (symlink): {asset.name}", GREEN)
    except (OSError, PermissionError) as e:
        return 1, _color(f"Failed to create agent symlink: {e}", RED)


def _copy_agent(asset: Asset, target_dir: Path, *, add_claude_refs: bool = True) -> Tuple[int, str]:
    """Copy an agent file to the agents directory.

    Unlike _install_agent which creates a symlink, this creates an independent
    copy that won't change when the source is modified.
    """
    try:
        if not asset.source_path.exists():
            return 1, _color(f"Agent source not found: {asset.source_path}", RED)

        agents_dir = target_dir / "agents"
        agents_dir.mkdir(parents=True, exist_ok=True)
        target_path = agents_dir / asset.source_path.name

        # Remove existing file or symlink if present
        if target_path.exists() or target_path.is_symlink():
            target_path.unlink()

        shutil.copy2(asset.source_path, target_path)

        if add_claude_refs:
            _add_commented_reference(target_dir, target_path)

        return 0, _color(f"Installed agent (copy): {asset.name}", GREEN)
    except (OSError, PermissionError) as e:
        return 1, _color(f"Failed to copy agent: {e}", RED)


def _install_mode(asset: Asset, target_dir: Path, activate: bool, *, add_claude_refs: bool = True) -> Tuple[int, str]:
    """Symlink a mode file to modes directory.

    Note: The activate parameter is deprecated and ignored. Symlink presence
    determines activation state. Symlinks are always created in modes/.
    """
    try:
        # Validate source exists before attempting symlink
        if not asset.source_path.exists():
            return 1, _color(f"Mode source not found: {asset.source_path}", RED)

        modes_dir = target_dir / "modes"
        modes_dir.mkdir(parents=True, exist_ok=True)
        target_path = modes_dir / asset.source_path.name

        # Remove existing file or symlink if present
        if target_path.exists() or target_path.is_symlink():
            if target_path.is_symlink():
                target_path.unlink()
            else:
                target_path.unlink()

        # Create symlink to source mode file
        target_path.symlink_to(asset.source_path)

        if add_claude_refs:
            _add_commented_reference(target_dir, target_path)

        return 0, _color(f"Installed mode (symlink): {asset.name}", GREEN)
    except (OSError, PermissionError) as e:
        return 1, _color(f"Failed to create mode symlink: {e}", RED)


def _install_workflow(asset: Asset, target_dir: Path, *, add_claude_refs: bool = True) -> Tuple[int, str]:
    """Copy a workflow."""
    workflows_dir = target_dir / "workflows"
    workflows_dir.mkdir(parents=True, exist_ok=True)

    target_path = workflows_dir / asset.source_path.name
    shutil.copy2(asset.source_path, target_path)

    if add_claude_refs:
        _add_commented_reference(target_dir, target_path)

    return 0, _color(f"Copied workflow: {asset.name}", GREEN)


def _install_rule(asset: Asset, target_dir: Path, *, add_claude_refs: bool = True) -> Tuple[int, str]:
    """Symlink a rule file to the rules/ directory."""
    try:
        # Validate source exists before attempting symlink
        if not asset.source_path.exists():
            return 1, _color(f"Rule source not found: {asset.source_path}", RED)

        rules_dir = target_dir / "rules"
        rules_dir.mkdir(parents=True, exist_ok=True)

        target_path = rules_dir / asset.source_path.name

        # Remove existing file or symlink if present
        if target_path.exists() or target_path.is_symlink():
            if target_path.is_symlink():
                target_path.unlink()
            else:
                target_path.unlink()

        # Create symlink to source rule file
        target_path.symlink_to(asset.source_path)

        if add_claude_refs:
            _add_commented_reference(target_dir, target_path)

        return 0, _color(f"Installed rules (symlink): {asset.name}", GREEN)
    except (OSError, PermissionError) as e:
        return 1, _color(f"Failed to create rule symlink: {e}", RED)


def _install_flag(asset: Asset, target_dir: Path) -> Tuple[int, str]:
    """Copy a flag file into flags/ (does not auto-enable)."""
    flags_dir = target_dir / "flags"
    flags_dir.mkdir(parents=True, exist_ok=True)

    target_path = flags_dir / asset.source_path.name
    shutil.copy2(asset.source_path, target_path)

    return 0, _color(f"Copied flag: {asset.name}", GREEN)


def _install_profile(asset: Asset, target_dir: Path, *, add_claude_refs: bool = True) -> Tuple[int, str]:
    """Copy a profile markdown file."""
    profiles_dir = target_dir / "profiles"
    profiles_dir.mkdir(parents=True, exist_ok=True)

    target_path = profiles_dir / asset.source_path.name
    shutil.copy2(asset.source_path, target_path)

    if add_claude_refs:
        _add_commented_reference(target_dir, target_path)

    return 0, _color(f"Copied profile: {asset.name}", GREEN)


def _install_scenario(asset: Asset, target_dir: Path, *, add_claude_refs: bool = True) -> Tuple[int, str]:
    """Copy a scenario markdown file."""
    scenarios_dir = target_dir / "scenarios"
    scenarios_dir.mkdir(parents=True, exist_ok=True)

    target_path = scenarios_dir / asset.source_path.name
    shutil.copy2(asset.source_path, target_path)

    if add_claude_refs:
        _add_commented_reference(target_dir, target_path)

    return 0, _color(f"Copied scenario: {asset.name}", GREEN)


def _install_task(asset: Asset, target_dir: Path, *, add_claude_refs: bool = True) -> Tuple[int, str]:
    """Copy a task template markdown file."""
    tasks_dir = target_dir / "tasks"
    tasks_dir.mkdir(parents=True, exist_ok=True)

    target_path = tasks_dir / asset.source_path.name
    shutil.copy2(asset.source_path, target_path)

    if add_claude_refs:
        _add_commented_reference(target_dir, target_path)

    return 0, _color(f"Copied task: {asset.name}", GREEN)


def _install_setting(asset: Asset, target_dir: Path) -> Tuple[int, str]:
    """Copy a shared settings/config file."""
    target_path = target_dir / asset.install_target
    target_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(asset.source_path, target_path)
    return 0, _color(f"Copied settings: {asset.name}", GREEN)


def uninstall_asset(
    category: str,
    name: str,
    target_dir: Path,
) -> Tuple[int, str]:
    """Uninstall an asset from a cortex directory.

    Args:
        category: Asset category (hooks, commands, agents, skills, modes, workflows)
        name: Asset name (for commands, use namespace:name format)
        target_dir: Target cortex directory

    Returns:
        Tuple of (exit_code, message)
    """
    try:
        if category == "skills":
            return _uninstall_skill(name, target_dir)
        elif category == "hooks":
            return _uninstall_hook(name, target_dir)
        elif category == "commands":
            return _uninstall_command(name, target_dir)
        elif category == "agents":
            return _uninstall_agent(name, target_dir)
        elif category == "modes":
            return _uninstall_mode(name, target_dir)
        elif category == "workflows":
            return _uninstall_workflow(name, target_dir)
        elif category == "rules":
            return _uninstall_rule(name, target_dir)
        elif category == "flags":
            return _uninstall_flag(name, target_dir)
        elif category == "profiles":
            return _uninstall_profile(name, target_dir)
        elif category == "scenarios":
            return _uninstall_scenario(name, target_dir)
        elif category == "tasks":
            return _uninstall_task(name, target_dir)
        elif category == "settings":
            return _uninstall_setting(name, target_dir)
        else:
            return 1, _color(f"Unknown category: {category}", RED)
    except Exception as e:
        return 1, _color(f"Uninstall failed: {e}", RED)


def _uninstall_skill(name: str, target_dir: Path) -> Tuple[int, str]:
    """Uninstall a skill (remove symlink)."""
    skill_dir = target_dir / "skills" / name

    if not skill_dir.exists() and not skill_dir.is_symlink():
        return 1, _color(f"Skill not installed: {name}", YELLOW)

    # Unlink symlink or remove directory if still a copy
    if skill_dir.is_symlink():
        skill_dir.unlink()
    elif skill_dir.is_dir():
        shutil.rmtree(skill_dir)
    else:
        return 1, _color(f"Skill not installed: {name}", YELLOW)

    return 0, _color(f"Uninstalled skill: {name}", GREEN)


def _uninstall_hook(name: str, target_dir: Path) -> Tuple[int, str]:
    """Uninstall a hook."""
    hooks_dir = target_dir / "hooks"

    # Try common extensions
    for ext in [".py", ".sh", ""]:
        hook_path = hooks_dir / f"{name}{ext}"
        if hook_path.exists():
            hook_path.unlink()
            return 0, _color(f"Uninstalled hook: {name}", GREEN)

    return 1, _color(f"Hook not installed: {name}", YELLOW)


def _uninstall_command(name: str, target_dir: Path) -> Tuple[int, str]:
    """Uninstall a command."""
    commands_dir = target_dir / "commands"

    cmd_path = _resolve_command_path(commands_dir, name)
    if cmd_path is None or not cmd_path.exists():
        return 1, _color(f"Command not installed: {name}", YELLOW)

    cmd_path.unlink()
    return 0, _color(f"Uninstalled command: {name}", GREEN)


def _extract_command_name(path: Path) -> Optional[str]:
    try:
        content = path.read_text(encoding="utf-8")
    except OSError:
        return None

    front_matter = _extract_front_matter(content)
    if not front_matter:
        return None

    for line in front_matter.splitlines():
        if not line.strip().startswith("name:"):
            continue
        value = line.split(":", 1)[1].strip()
        if not value:
            return None
        if value[0] in ("'", '"') and value[-1:] == value[0]:
            value = value[1:-1]
        return value
    return None


def _resolve_command_path(commands_dir: Path, name: str) -> Optional[Path]:
    """Resolve command path by name across legacy and flattened layouts."""
    if ":" in name:
        namespace, cmd_name = name.split(":", 1)
        legacy = commands_dir / namespace / f"{cmd_name}.md"
        if legacy.exists():
            return legacy
        normalized = commands_dir / f"{name.replace(':', '-')}.md"
        if normalized.exists():
            return normalized

    direct = commands_dir / f"{name}.md"
    if direct.exists():
        return direct

    for cmd_file in commands_dir.rglob("*.md"):
        if cmd_file.name == "README.md":
            continue
        declared = _extract_command_name(cmd_file)
        if declared == name:
            return cmd_file
    return None


def _uninstall_agent(name: str, target_dir: Path) -> Tuple[int, str]:
    """Uninstall an agent (remove symlink or file)."""
    agent_path = target_dir / "agents" / f"{name}.md"

    if not agent_path.exists() and not agent_path.is_symlink():
        return 1, _color(f"Agent not installed: {name}", YELLOW)

    # Unlink symlink or remove file
    agent_path.unlink()
    return 0, _color(f"Uninstalled agent: {name}", GREEN)


def _uninstall_mode(name: str, target_dir: Path) -> Tuple[int, str]:
    """Uninstall a mode (remove symlink or file)."""
    mode_path = target_dir / "modes" / f"{name}.md"

    if not mode_path.exists() and not mode_path.is_symlink():
        return 1, _color(f"Mode not installed: {name}", YELLOW)

    # Unlink symlink or remove file
    mode_path.unlink()
    return 0, _color(f"Uninstalled mode: {name}", GREEN)


def _uninstall_workflow(name: str, target_dir: Path) -> Tuple[int, str]:
    """Uninstall a workflow."""
    workflow_path = target_dir / "workflows" / f"{name}.yaml"
    if not workflow_path.exists():
        return 1, _color(f"Workflow not installed: {name}", YELLOW)

    workflow_path.unlink()
    return 0, _color(f"Uninstalled workflow: {name}", GREEN)


def _uninstall_rule(name: str, target_dir: Path) -> Tuple[int, str]:
    """Uninstall a rule file (remove symlink or file)."""
    rule_path = target_dir / "rules" / f"{name}.md"

    if not rule_path.exists() and not rule_path.is_symlink():
        return 1, _color(f"Rule not installed: {name}", YELLOW)

    # Unlink symlink or remove file
    rule_path.unlink()
    return 0, _color(f"Uninstalled rule: {name}", GREEN)


def _uninstall_flag(name: str, target_dir: Path) -> Tuple[int, str]:
    """Uninstall a flag file and remove any FLAGS.md reference."""
    flag_path = target_dir / "flags" / f"{name}.md"
    if not flag_path.exists():
        return 1, _color(f"Flag not installed: {name}", YELLOW)

    flag_path.unlink()

    flags_md = target_dir / "FLAGS.md"
    if flags_md.exists():
        try:
            content = flags_md.read_text(encoding="utf-8")
        except OSError:
            return 0, _color(f"Uninstalled flag: {name}", GREEN)

        lines = [
            line for line in content.splitlines()
            if line.strip() != f"@flags/{name}.md"
        ]
        updated = "\n".join(lines)
        if updated and not updated.endswith("\n"):
            updated += "\n"
        try:
            _update_with_backup(flags_md, lambda _: updated)
        except Exception:
            pass

    return 0, _color(f"Uninstalled flag: {name}", GREEN)


def _uninstall_profile(name: str, target_dir: Path) -> Tuple[int, str]:
    """Uninstall a profile."""
    profile_path = target_dir / "profiles" / f"{name}.md"
    if not profile_path.exists():
        return 1, _color(f"Profile not installed: {name}", YELLOW)

    profile_path.unlink()
    return 0, _color(f"Uninstalled profile: {name}", GREEN)


def _uninstall_scenario(name: str, target_dir: Path) -> Tuple[int, str]:
    """Uninstall a scenario."""
    scenario_path = target_dir / "scenarios" / f"{name}.md"
    if not scenario_path.exists():
        return 1, _color(f"Scenario not installed: {name}", YELLOW)

    scenario_path.unlink()
    return 0, _color(f"Uninstalled scenario: {name}", GREEN)


def _uninstall_task(name: str, target_dir: Path) -> Tuple[int, str]:
    """Uninstall a task template."""
    task_path = target_dir / "tasks" / f"{name}.md"
    if not task_path.exists():
        return 1, _color(f"Task not installed: {name}", YELLOW)

    task_path.unlink()
    return 0, _color(f"Uninstalled task: {name}", GREEN)


def _uninstall_setting(name: str, target_dir: Path) -> Tuple[int, str]:
    """Uninstall a settings file."""
    setting_path = target_dir / name
    if not setting_path.exists():
        return 1, _color(f"Settings not installed: {name}", YELLOW)

    setting_path.unlink()
    return 0, _color(f"Uninstalled settings: {name}", GREEN)


def get_asset_diff(
    asset: Asset,
    target_dir: Path,
) -> Optional[str]:
    """Get unified diff between source and installed asset.

    For symlinked assets, compares the target of the symlink with the source.

    Args:
        asset: Asset to compare
        target_dir: Target cortex directory

    Returns:
        Diff string or None if not installed/identical
    """
    # Determine installed path
    if asset.category == AssetCategory.SKILLS:
        installed_path = target_dir / "skills" / asset.name / "SKILL.md"
        source_path = asset.source_path / "SKILL.md"
    elif asset.category == AssetCategory.AGENTS:
        installed_path = target_dir / "agents" / asset.source_path.name
        if not installed_path.exists() and not installed_path.is_symlink():
            return None
        source_path = asset.source_path
    elif asset.category == AssetCategory.MODES:
        installed_path = target_dir / "modes" / asset.source_path.name
        if not installed_path.exists() and not installed_path.is_symlink():
            return None
        source_path = asset.source_path
    elif asset.category == AssetCategory.COMMANDS:
        if asset.namespace:
            installed_path = target_dir / "commands" / asset.namespace / asset.source_path.name
        else:
            installed_path = target_dir / "commands" / asset.source_path.name
        source_path = asset.source_path
    else:
        installed_path = target_dir / asset.install_target
        source_path = asset.source_path

    if not installed_path.exists() and not installed_path.is_symlink():
        return None

    try:
        installed_lines = installed_path.read_text(encoding="utf-8").splitlines(keepends=True)
        source_lines = source_path.read_text(encoding="utf-8").splitlines(keepends=True)

        diff = list(difflib.unified_diff(
            installed_lines,
            source_lines,
            fromfile=f"installed/{asset.name}",
            tofile=f"source/{asset.name}",
        ))

        if not diff:
            return None

        return "".join(diff)
    except OSError:
        return None


def bulk_install(
    assets: List[Asset],
    target_dir: Path,
    activate: bool = True,
    *,
    add_claude_refs: bool = True,
    register_hooks: bool = True,
) -> List[Tuple[Asset, int, str]]:
    """Copy multiple assets.

    Args:
        assets: List of assets to copy
        target_dir: Target directory
        activate: For agents/modes, whether to install as active
        add_claude_refs: When True, append commented reference to CLAUDE.md
        register_hooks: When True, register hooks in settings.json

    Returns:
        List of (asset, exit_code, message) tuples
    """
    results = []

    for asset in assets:
        exit_code, message = install_asset(
            asset, target_dir, activate,
            add_claude_refs=add_claude_refs,
            register_hooks=register_hooks,
        )
        results.append((asset, exit_code, message))

    return results


def register_hook_in_settings(
    hook_name: str,
    hook_command: str,
    hook_type: str,
    settings_path: Path,
) -> Tuple[int, str]:
    """Register a hook in settings.json.

    Args:
        hook_name: Name of the hook (for display)
        hook_command: Full command to execute
        hook_type: Hook type (e.g., "UserPromptSubmit", "Stop")
        settings_path: Path to settings.json

    Returns:
        Tuple of (exit_code, message)
    """
    try:
        # Load existing settings
        if settings_path.exists():
            with open(settings_path, "r", encoding="utf-8") as f:
                settings = json.load(f)
        else:
            settings = {}

        # Ensure hooks structure exists
        if "hooks" not in settings:
            settings["hooks"] = {}

        if hook_type not in settings["hooks"]:
            settings["hooks"][hook_type] = []

        # Check if hook already registered
        hooks_list = settings["hooks"][hook_type]
        for hook_entry in hooks_list:
            if isinstance(hook_entry, dict):
                existing_hooks = hook_entry.get("hooks", [])
                for h in existing_hooks:
                    if h.get("command") == hook_command:
                        return 0, _color(f"Hook already registered: {hook_name}", YELLOW)

        # Add new hook
        new_hook = {
            "matcher": "",
            "hooks": [
                {
                    "type": "command",
                    "command": hook_command,
                }
            ]
        }
        hooks_list.append(new_hook)

        # Backup and write
        if settings_path.exists():
            backup_path = settings_path.with_suffix(".json.bak")
            shutil.copy2(settings_path, backup_path)

        with open(settings_path, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2)

        return 0, _color(f"Registered hook: {hook_name}", GREEN)
    except Exception as e:
        return 1, _color(f"Failed to register hook: {e}", RED)


def get_installed_path(
    asset: Asset,
    target_dir: Path,
) -> Optional[Path]:
    """Get the installed path of an asset if it exists.

    For symlinked assets, returns the symlink path (not the target).

    Args:
        asset: Asset to find
        target_dir: Target cortex directory

    Returns:
        Path to installed asset or None if not installed
    """
    if asset.category == AssetCategory.SKILLS:
        path = target_dir / "skills" / asset.name
        return path if (path.exists() or path.is_symlink()) else None
    elif asset.category == AssetCategory.AGENTS:
        path = target_dir / "agents" / asset.source_path.name
        return path if (path.exists() or path.is_symlink()) else None
    elif asset.category == AssetCategory.MODES:
        path = target_dir / "modes" / asset.source_path.name
        return path if (path.exists() or path.is_symlink()) else None
    elif asset.category == AssetCategory.COMMANDS:
        if asset.namespace:
            path = target_dir / "commands" / asset.namespace / asset.source_path.name
        else:
            path = target_dir / "commands" / asset.source_path.name
        return path if path.exists() else None
    elif asset.category == AssetCategory.HOOKS:
        path = target_dir / "hooks" / asset.source_path.name
        return path if (path.exists() or path.is_symlink()) else None
    elif asset.category == AssetCategory.WORKFLOWS:
        path = target_dir / "workflows" / asset.source_path.name
        return path if path.exists() else None
    elif asset.category == AssetCategory.RULES:
        path = target_dir / "rules" / asset.source_path.name
        return path if (path.exists() or path.is_symlink()) else None
    elif asset.category == AssetCategory.SETTINGS:
        path = target_dir / asset.install_target
        return path if path.exists() else None

    return None
