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

from .asset_discovery import Asset, AssetCategory
from .base import _update_with_backup, _extract_front_matter


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
) -> Tuple[int, str]:
    """Install an asset to a cortex directory.

    Args:
        asset: Asset to install
        target_dir: Target cortex directory
        activate: For agents/modes, whether to install as active

    Returns:
        Tuple of (exit_code, message)
    """
    try:
        if asset.category == AssetCategory.SKILLS:
            return _install_skill(asset, target_dir)
        elif asset.category == AssetCategory.HOOKS:
            return _install_hook(asset, target_dir)
        elif asset.category == AssetCategory.COMMANDS:
            return _install_command(asset, target_dir)
        elif asset.category == AssetCategory.AGENTS:
            return _install_agent(asset, target_dir, activate)
        elif asset.category == AssetCategory.MODES:
            return _install_mode(asset, target_dir, activate)
        elif asset.category == AssetCategory.WORKFLOWS:
            return _install_workflow(asset, target_dir)
        elif asset.category == AssetCategory.RULES:
            return _install_rule(asset, target_dir)
        elif asset.category == AssetCategory.FLAGS:
            return _install_flag(asset, target_dir)
        elif asset.category == AssetCategory.PROFILES:
            return _install_profile(asset, target_dir)
        elif asset.category == AssetCategory.SCENARIOS:
            return _install_scenario(asset, target_dir)
        elif asset.category == AssetCategory.TASKS:
            return _install_task(asset, target_dir)
        else:
            return _install_setting(asset, target_dir)
    except Exception as e:
        return 1, _color(f"Installation failed: {e}", RED)


def _install_skill(asset: Asset, target_dir: Path) -> Tuple[int, str]:
    """Install a skill (directory copy)."""
    skills_dir = target_dir / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)

    target_skill_dir = skills_dir / asset.name

    # Use atomic copy: temp dir then move
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir) / asset.name

        # Copy entire skill directory
        shutil.copytree(asset.source_path, temp_path)

        # Remove existing if present
        if target_skill_dir.exists():
            shutil.rmtree(target_skill_dir)

        # Move into place
        shutil.move(str(temp_path), str(target_skill_dir))

    # Add commented reference to SKILL.md for easy activation
    _add_commented_reference(target_dir, target_skill_dir / "SKILL.md")

    return 0, _color(f"Installed skill: {asset.name}", GREEN)


def _install_hook(asset: Asset, target_dir: Path) -> Tuple[int, str]:
    """Install a hook and optionally register in settings.json."""
    hooks_dir = target_dir / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)

    target_path = hooks_dir / asset.source_path.name

    # Copy file
    shutil.copy2(asset.source_path, target_path)

    # Make executable
    target_path.chmod(target_path.stat().st_mode | 0o111)

    _add_commented_reference(target_dir, target_path)

    return 0, _color(f"Installed hook: {asset.name}", GREEN)


def _install_command(asset: Asset, target_dir: Path) -> Tuple[int, str]:
    """Install a slash command."""
    commands_dir = target_dir / "commands"

    if asset.namespace:
        target_subdir = commands_dir / asset.namespace
        target_subdir.mkdir(parents=True, exist_ok=True)
        target_path = target_subdir / asset.source_path.name
    else:
        commands_dir.mkdir(parents=True, exist_ok=True)
        target_path = commands_dir / asset.source_path.name

    shutil.copy2(asset.source_path, target_path)

    _add_commented_reference(target_dir, target_path)

    return 0, _color(f"Installed command: {asset.display_name}", GREEN)


def _install_agent(asset: Asset, target_dir: Path, activate: bool) -> Tuple[int, str]:
    """Install an agent."""
    if activate:
        agents_dir = target_dir / "agents"
    else:
        agents_dir = target_dir / "inactive" / "agents"

    agents_dir.mkdir(parents=True, exist_ok=True)
    target_path = agents_dir / asset.source_path.name

    shutil.copy2(asset.source_path, target_path)

    _add_commented_reference(target_dir, target_path)

    status = "active" if activate else "inactive"
    return 0, _color(f"Installed agent ({status}): {asset.name}", GREEN)


def _install_mode(asset: Asset, target_dir: Path, activate: bool) -> Tuple[int, str]:
    """Install a mode."""
    if activate:
        modes_dir = target_dir / "modes"
    else:
        modes_dir = target_dir / "inactive" / "modes"

    modes_dir.mkdir(parents=True, exist_ok=True)
    target_path = modes_dir / asset.source_path.name

    shutil.copy2(asset.source_path, target_path)

    _add_commented_reference(target_dir, target_path)

    status = "active" if activate else "inactive"
    return 0, _color(f"Installed mode ({status}): {asset.name}", GREEN)


def _install_workflow(asset: Asset, target_dir: Path) -> Tuple[int, str]:
    """Install a workflow."""
    workflows_dir = target_dir / "workflows"
    workflows_dir.mkdir(parents=True, exist_ok=True)

    target_path = workflows_dir / asset.source_path.name
    shutil.copy2(asset.source_path, target_path)

    _add_commented_reference(target_dir, target_path)

    return 0, _color(f"Installed workflow: {asset.name}", GREEN)


def _install_rule(asset: Asset, target_dir: Path) -> Tuple[int, str]:
    """Install a recommendation/config rules file under skills/."""
    skills_dir = target_dir / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)

    target_path = skills_dir / asset.source_path.name
    shutil.copy2(asset.source_path, target_path)

    _add_commented_reference(target_dir, target_path)

    return 0, _color(f"Installed rules: {asset.name}", GREEN)


def _install_flag(asset: Asset, target_dir: Path) -> Tuple[int, str]:
    """Install a flag file into flags/ (does not auto-enable)."""
    flags_dir = target_dir / "flags"
    flags_dir.mkdir(parents=True, exist_ok=True)

    target_path = flags_dir / asset.source_path.name
    shutil.copy2(asset.source_path, target_path)

    return 0, _color(f"Installed flag: {asset.name}", GREEN)


def _install_profile(asset: Asset, target_dir: Path) -> Tuple[int, str]:
    """Install a profile markdown file."""
    profiles_dir = target_dir / "profiles"
    profiles_dir.mkdir(parents=True, exist_ok=True)

    target_path = profiles_dir / asset.source_path.name
    shutil.copy2(asset.source_path, target_path)

    _add_commented_reference(target_dir, target_path)

    return 0, _color(f"Installed profile: {asset.name}", GREEN)


def _install_scenario(asset: Asset, target_dir: Path) -> Tuple[int, str]:
    """Install a scenario markdown file."""
    scenarios_dir = target_dir / "scenarios"
    scenarios_dir.mkdir(parents=True, exist_ok=True)

    target_path = scenarios_dir / asset.source_path.name
    shutil.copy2(asset.source_path, target_path)

    _add_commented_reference(target_dir, target_path)

    return 0, _color(f"Installed scenario: {asset.name}", GREEN)


def _install_task(asset: Asset, target_dir: Path) -> Tuple[int, str]:
    """Install a task template markdown file."""
    tasks_dir = target_dir / "tasks"
    tasks_dir.mkdir(parents=True, exist_ok=True)

    target_path = tasks_dir / asset.source_path.name
    shutil.copy2(asset.source_path, target_path)

    _add_commented_reference(target_dir, target_path)

    return 0, _color(f"Installed task: {asset.name}", GREEN)


def _install_setting(asset: Asset, target_dir: Path) -> Tuple[int, str]:
    """Install a shared settings/config file."""
    target_path = target_dir / asset.install_target
    target_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(asset.source_path, target_path)
    return 0, _color(f"Installed settings: {asset.name}", GREEN)


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
    """Uninstall a skill."""
    skill_dir = target_dir / "skills" / name
    if not skill_dir.exists():
        return 1, _color(f"Skill not installed: {name}", YELLOW)

    shutil.rmtree(skill_dir)
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
    """Uninstall an agent (from active or inactive)."""
    for agent_dir in [target_dir / "agents", target_dir / "inactive" / "agents"]:
        agent_path = agent_dir / f"{name}.md"
        if agent_path.exists():
            agent_path.unlink()
            return 0, _color(f"Uninstalled agent: {name}", GREEN)

    return 1, _color(f"Agent not installed: {name}", YELLOW)


def _uninstall_mode(name: str, target_dir: Path) -> Tuple[int, str]:
    """Uninstall a mode (from active or inactive)."""
    for modes_dir in [target_dir / "modes", target_dir / "inactive" / "modes"]:
        mode_path = modes_dir / f"{name}.md"
        if mode_path.exists():
            mode_path.unlink()
            return 0, _color(f"Uninstalled mode: {name}", GREEN)

    return 1, _color(f"Mode not installed: {name}", YELLOW)


def _uninstall_workflow(name: str, target_dir: Path) -> Tuple[int, str]:
    """Uninstall a workflow."""
    workflow_path = target_dir / "workflows" / f"{name}.yaml"
    if not workflow_path.exists():
        return 1, _color(f"Workflow not installed: {name}", YELLOW)

    workflow_path.unlink()
    return 0, _color(f"Uninstalled workflow: {name}", GREEN)


def _uninstall_rule(name: str, target_dir: Path) -> Tuple[int, str]:
    """Uninstall a rules file (skill/recommendation rules)."""
    rules_dir = target_dir / "skills"
    rule_path = rules_dir / f"{name}.json"
    if not rule_path.exists():
        return 1, _color(f"Rules not installed: {name}", YELLOW)

    rule_path.unlink()
    return 0, _color(f"Uninstalled rules: {name}", GREEN)


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
        if not installed_path.exists():
            installed_path = target_dir / "inactive" / "agents" / asset.source_path.name
        source_path = asset.source_path
    elif asset.category == AssetCategory.MODES:
        installed_path = target_dir / "modes" / asset.source_path.name
        if not installed_path.exists():
            installed_path = target_dir / "inactive" / "modes" / asset.source_path.name
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

    if not installed_path.exists():
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
) -> List[Tuple[Asset, int, str]]:
    """Install multiple assets.

    Args:
        assets: List of assets to install
        target_dir: Target cortex directory
        activate: For agents/modes, whether to install as active

    Returns:
        List of (asset, exit_code, message) tuples
    """
    results = []

    for asset in assets:
        exit_code, message = install_asset(asset, target_dir, activate)
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

    Args:
        asset: Asset to find
        target_dir: Target cortex directory

    Returns:
        Path to installed asset or None if not installed
    """
    if asset.category == AssetCategory.SKILLS:
        path = target_dir / "skills" / asset.name
        return path if path.exists() else None
    elif asset.category == AssetCategory.AGENTS:
        path = target_dir / "agents" / asset.source_path.name
        if path.exists():
            return path
        path = target_dir / "inactive" / "agents" / asset.source_path.name
        return path if path.exists() else None
    elif asset.category == AssetCategory.MODES:
        path = target_dir / "modes" / asset.source_path.name
        if path.exists():
            return path
        path = target_dir / "inactive" / "modes" / asset.source_path.name
        return path if path.exists() else None
    elif asset.category == AssetCategory.COMMANDS:
        if asset.namespace:
            path = target_dir / "commands" / asset.namespace / asset.source_path.name
        else:
            path = target_dir / "commands" / asset.source_path.name
        return path if path.exists() else None
    elif asset.category == AssetCategory.HOOKS:
        path = target_dir / "hooks" / asset.source_path.name
        return path if path.exists() else None
    elif asset.category == AssetCategory.WORKFLOWS:
        path = target_dir / "workflows" / asset.source_path.name
        return path if path.exists() else None
    elif asset.category == AssetCategory.SETTINGS:
        path = target_dir / asset.install_target
        return path if path.exists() else None

    return None
