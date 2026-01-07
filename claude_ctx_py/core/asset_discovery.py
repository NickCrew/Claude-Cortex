"""Asset discovery for plugin resources.

Discovers available assets from the plugin and installed assets
in cortex directories. Supports:
- Hooks
- Commands (slash commands)
- Agents
- Skills
- Modes
- Workflows
- Flags
- Rules
- Profiles
- Scenarios
- Tasks
- Settings
"""

from __future__ import annotations

import os
import re
import json
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any

from .base import _extract_front_matter, _resolve_claude_dir, _resolve_plugin_assets_root


_SETTINGS_RELATIVE_PATHS = [
    Path("agents/triggers.yaml"),
    Path("skills/activation.yaml"),
    Path("skills/composition.yaml"),
    Path("skills/versions.yaml"),
    Path("skills/analytics.schema.json"),
    Path("skills/metrics.schema.json"),
    Path("skills/community/registry.yaml"),
]


class AssetCategory(Enum):
    """Categories of installable assets."""

    HOOKS = "hooks"
    COMMANDS = "commands"
    AGENTS = "agents"
    SKILLS = "skills"
    MODES = "modes"
    WORKFLOWS = "workflows"
    FLAGS = "flags"
    RULES = "rules"
    PROFILES = "profiles"
    SCENARIOS = "scenarios"
    TASKS = "tasks"
    SETTINGS = "settings"


class InstallStatus(Enum):
    """Installation status of an asset."""

    NOT_INSTALLED = "not_installed"
    INSTALLED_SAME = "installed_same"
    INSTALLED_DIFFERENT = "installed_different"
    INSTALLED_NEWER = "installed_newer"
    INSTALLED_OLDER = "installed_older"


@dataclass
class Asset:
    """Represents a discoverable/installable asset."""

    name: str
    category: AssetCategory
    source_path: Path
    description: str
    version: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    # For commands, this is the namespace (e.g., "analyze", "dev")
    namespace: Optional[str] = None

    @property
    def display_name(self) -> str:
        """Get display name including namespace if applicable."""
        if self.namespace:
            return f"{self.namespace}:{self.name}"
        return self.name

    @property
    def install_target(self) -> str:
        """Get the relative install path within the cortex directory."""
        if self.category == AssetCategory.HOOKS:
            return f"hooks/{self.source_path.name}"
        elif self.category == AssetCategory.COMMANDS:
            if self.namespace:
                return f"commands/{self.namespace}/{self.source_path.name}"
            return f"commands/{self.source_path.name}"
        elif self.category == AssetCategory.AGENTS:
            return f"agents/{self.source_path.name}"
        elif self.category == AssetCategory.SKILLS:
            # Skills are directories
            return f"skills/{self.name}"
        elif self.category == AssetCategory.MODES:
            return f"modes/{self.source_path.name}"
        elif self.category == AssetCategory.WORKFLOWS:
            return f"workflows/{self.source_path.name}"
        elif self.category == AssetCategory.FLAGS:
            return f"flags/{self.source_path.name}"
        elif self.category == AssetCategory.RULES:
            return f"skills/{self.source_path.name}"
        elif self.category == AssetCategory.PROFILES:
            return f"profiles/{self.source_path.name}"
        elif self.category == AssetCategory.SCENARIOS:
            return f"scenarios/{self.source_path.name}"
        elif self.category == AssetCategory.TASKS:
            return f"tasks/{self.source_path.name}"
        else:
            return self.name


@dataclass
class ClaudeDir:
    """Represents a discovered cortex directory."""

    path: Path
    scope: str  # "project", "parent", "global"
    installed_assets: Dict[str, List[str]] = field(default_factory=dict)

    @property
    def display_name(self) -> str:
        """Get display name for the directory."""
        if self.scope == "global":
            return "~/.cortex (global)"
        elif self.scope == "legacy":
            return "~/.claude (legacy)"
        elif self.scope == "project":
            return f"./.claude (project)"
        else:
            # Show relative path for parent dirs
            try:
                rel = self.path.relative_to(Path.cwd())
                return f"{rel} ({self.scope})"
            except ValueError:
                return f"{self.path} ({self.scope})"


def get_plugin_root() -> Path:
    """Get the root directory of the plugin installation.

    Returns:
        Path to the plugin root directory
    """
    return _resolve_plugin_assets_root()


def discover_plugin_assets() -> Dict[str, List[Asset]]:
    """Discover all available assets from the plugin.

    Returns:
        Dict mapping category names to lists of Asset objects
    """
    plugin_root = get_plugin_root()

    assets: Dict[str, List[Asset]] = {
        "hooks": [],
        "commands": [],
        "agents": [],
        "skills": [],
        "modes": [],
        "workflows": [],
        "flags": [],
        "rules": [],
        "profiles": [],
        "scenarios": [],
        "tasks": [],
        "settings": [],
    }

    # Discover each category
    assets["hooks"] = _discover_hooks(plugin_root)
    assets["commands"] = _discover_commands(plugin_root)
    assets["agents"] = _discover_agents(plugin_root)
    assets["skills"] = _discover_skills(plugin_root)
    assets["modes"] = _discover_modes(plugin_root)
    assets["workflows"] = _discover_workflows(plugin_root)
    assets["flags"] = _discover_flags(plugin_root)
    assets["rules"] = _discover_rules(plugin_root)
    assets["profiles"] = _discover_profiles(plugin_root)
    assets["scenarios"] = _discover_scenarios(plugin_root)
    assets["tasks"] = _discover_tasks(plugin_root)
    assets["settings"] = _discover_settings(plugin_root)

    return assets


def _discover_hooks(plugin_root: Path) -> List[Asset]:
    """Discover available hooks."""
    hooks: List[Asset] = []
    hooks_dir = plugin_root / "hooks" / "examples"

    if not hooks_dir.exists():
        return hooks

    for path in hooks_dir.iterdir():
        if path.is_file() and path.suffix in (".py", ".sh"):
            # Extract description from file
            description = _extract_hook_description(path)

            hooks.append(Asset(
                name=path.stem,
                category=AssetCategory.HOOKS,
                source_path=path,
                description=description,
                metadata={"type": path.suffix},
            ))

    return sorted(hooks, key=lambda a: a.name)


def _extract_hook_description(path: Path) -> str:
    """Extract description from hook file."""
    try:
        content = path.read_text(encoding="utf-8")

        # Look for docstring (Python) or comment block (shell)
        if path.suffix == ".py":
            # Python docstring
            match = re.search(r'"""(.+?)"""', content, re.DOTALL)
            if match:
                # Get first line of docstring
                return match.group(1).strip().split("\n")[0]
        elif path.suffix == ".sh":
            # Shell comment block
            lines = content.split("\n")
            for line in lines:
                if line.startswith("# ") and not line.startswith("#!"):
                    return line[2:].strip()

        return "No description available"
    except OSError:
        return "Could not read file"


def _discover_commands(plugin_root: Path) -> List[Asset]:
    """Discover available slash commands."""
    commands: List[Asset] = []
    commands_dir = plugin_root / "commands"

    if not commands_dir.exists():
        return commands

    for item in commands_dir.iterdir():
        if item.is_dir() and not item.name.startswith("."):
            # Namespace directory (e.g., analyze/, dev/)
            namespace = item.name
            for cmd_file in item.glob("*.md"):
                if cmd_file.name == "README.md":
                    continue
                asset = _parse_command_file(cmd_file, namespace)
                if asset:
                    commands.append(asset)
        elif item.is_file() and item.suffix == ".md":
            # Root-level command
            if item.name == "README.md":
                continue
            asset = _parse_command_file(item, None)
            if asset:
                commands.append(asset)

    return sorted(commands, key=lambda a: a.display_name)


def _parse_command_front_matter(content: str) -> Dict[str, Any]:
    """Parse command front matter into a dict (best-effort)."""
    front_matter_str = _extract_front_matter(content)
    if not front_matter_str:
        return {}
    try:
        import yaml
        return yaml.safe_load(front_matter_str) or {}
    except Exception:
        return {}


def _resolve_command_name(
    path: Path,
    namespace: Optional[str],
    front_matter: Dict[str, Any],
) -> tuple[str, Optional[str]]:
    """Resolve command name + namespace, honoring front matter when present."""
    name = path.stem
    resolved_namespace = namespace
    raw_name = front_matter.get("name")
    if isinstance(raw_name, str):
        cleaned = raw_name.strip()
        if cleaned:
            if ":" in cleaned:
                return cleaned, None
            name = cleaned
    return name, resolved_namespace


def _parse_command_file(path: Path, namespace: Optional[str]) -> Optional[Asset]:
    """Parse a command markdown file."""
    try:
        content = path.read_text(encoding="utf-8")
        front_matter = _parse_command_front_matter(content)
        name, resolved_namespace = _resolve_command_name(path, namespace, front_matter)

        description = front_matter.get("description", "")
        if not description:
            # Try to extract from content
            lines = content.split("\n")
            for line in lines:
                if line.startswith("# "):
                    continue
                if line.strip():
                    description = line.strip()
                    break

        return Asset(
            name=name,
            category=AssetCategory.COMMANDS,
            source_path=path,
            description=description[:100] + "..." if len(description) > 100 else description,
            namespace=resolved_namespace,
            metadata=front_matter,
        )
    except OSError:
        return None


def _discover_agents(plugin_root: Path) -> List[Asset]:
    """Discover available agents."""
    agents: List[Asset] = []
    agents_dir = plugin_root / "agents"

    if not agents_dir.exists():
        return agents

    for path in agents_dir.glob("*.md"):
        if path.name in ("README.md", "dependencies.map"):
            continue

        try:
            content = path.read_text(encoding="utf-8")
            front_matter_str = _extract_front_matter(content)

            # Parse YAML front matter
            front_matter: Dict[str, Any] = {}
            if front_matter_str:
                try:
                    import yaml
                    front_matter = yaml.safe_load(front_matter_str) or {}
                except Exception:
                    pass

            description = front_matter.get("summary", front_matter.get("description", ""))
            if not description:
                description = f"Agent: {path.stem}"

            agents.append(Asset(
                name=path.stem,
                category=AssetCategory.AGENTS,
                source_path=path,
                description=description[:100] + "..." if len(description) > 100 else description,
                version=front_matter.get("version"),
                metadata=front_matter,
            ))
        except OSError:
            continue

    return sorted(agents, key=lambda a: a.name)


def _discover_skills(plugin_root: Path) -> List[Asset]:
    """Discover available skills."""
    skills: List[Asset] = []
    skills_dir = plugin_root / "skills"

    if not skills_dir.exists():
        return skills

    for item in skills_dir.iterdir():
        if not item.is_dir():
            continue
        if item.name.startswith(".") or item.name in ("community", "__pycache__"):
            continue

        # Look for SKILL.md
        skill_file = item / "SKILL.md"
        if not skill_file.exists():
            continue

        try:
            content = skill_file.read_text(encoding="utf-8")
            front_matter_str = _extract_front_matter(content)

            # Parse YAML front matter
            front_matter: Dict[str, Any] = {}
            if front_matter_str:
                try:
                    import yaml
                    front_matter = yaml.safe_load(front_matter_str) or {}
                except Exception:
                    pass

            description = front_matter.get("description", "")
            if not description:
                # Try to get from first paragraph
                lines = content.split("\n")
                for line in lines:
                    if line.startswith("#"):
                        continue
                    if line.strip() and not line.startswith("---"):
                        description = line.strip()
                        break

            skills.append(Asset(
                name=item.name,
                category=AssetCategory.SKILLS,
                source_path=item,
                description=description[:100] + "..." if len(description) > 100 else description,
                version=front_matter.get("version"),
                metadata=front_matter,
            ))
        except OSError:
            continue

    return sorted(skills, key=lambda a: a.name)


def _discover_modes(plugin_root: Path) -> List[Asset]:
    """Discover available modes."""
    modes: List[Asset] = []
    modes_dir = plugin_root / "modes"

    if not modes_dir.exists():
        return modes

    for path in modes_dir.glob("*.md"):
        if path.name == "README.md":
            continue

        try:
            content = path.read_text(encoding="utf-8")

            # Extract description from Purpose section
            description = ""
            lines = content.split("\n")
            in_purpose = False
            for line in lines:
                if "**Purpose**:" in line:
                    description = line.split("**Purpose**:")[-1].strip()
                    break
                if line.strip().lower() == "## purpose":
                    in_purpose = True
                    continue
                if in_purpose and line.strip():
                    description = line.strip()
                    break

            if not description:
                description = f"Mode: {path.stem}"

            modes.append(Asset(
                name=path.stem,
                category=AssetCategory.MODES,
                source_path=path,
                description=description[:100] + "..." if len(description) > 100 else description,
            ))
        except OSError:
            continue

    return sorted(modes, key=lambda a: a.name)


def _discover_workflows(plugin_root: Path) -> List[Asset]:
    """Discover available workflows."""
    workflows: List[Asset] = []
    workflows_dir = plugin_root / "workflows"

    if not workflows_dir.exists():
        return workflows

    for path in workflows_dir.glob("*.yaml"):
        try:
            import yaml
            content = path.read_text(encoding="utf-8")
            data = yaml.safe_load(content)

            if not isinstance(data, dict):
                continue

            workflows.append(Asset(
                name=path.stem,
                category=AssetCategory.WORKFLOWS,
                source_path=path,
                description=data.get("description", f"Workflow: {path.stem}"),
                version=data.get("version"),
                metadata=data,
            ))
        except (OSError, Exception):
            continue

    return sorted(workflows, key=lambda a: a.name)


def _discover_flags(plugin_root: Path) -> List[Asset]:
    """Discover available flags."""
    flags: List[Asset] = []
    flags_dir = plugin_root / "flags"

    if not flags_dir.exists():
        return flags

    for path in flags_dir.glob("*.md"):
        if path.name == "README.md":
            continue

        try:
            content = path.read_text(encoding="utf-8")

            # Extract description from first non-empty line after title
            description = ""
            lines = content.split("\n")
            found_title = False
            for line in lines:
                if line.startswith("# "):
                    found_title = True
                    continue
                if found_title and line.strip() and not line.startswith("**Estimated"):
                    description = line.strip()
                    break

            if not description:
                description = f"Flag: {path.stem}"

            # Extract estimated tokens if present
            tokens = None
            for line in lines:
                if "**Estimated tokens:" in line:
                    import re
                    match = re.search(r"~?(\d+)", line)
                    if match:
                        tokens = int(match.group(1))
                    break

            flags.append(Asset(
                name=path.stem,
                category=AssetCategory.FLAGS,
                source_path=path,
                description=description[:100] + "..." if len(description) > 100 else description,
                metadata={"estimated_tokens": tokens} if tokens else {},
            ))
        except OSError:
            continue

    return sorted(flags, key=lambda a: a.name)


def _discover_rules(plugin_root: Path) -> List[Asset]:
    """Discover recommendation/config rule files."""
    rules: List[Asset] = []
    candidates = [
        plugin_root / "skills" / "skill-rules.json",
        plugin_root / "skills" / "recommendation-rules.json",
    ]

    for path in candidates:
        if not path.exists():
            continue
        try:
            import json

            data = json.loads(path.read_text(encoding="utf-8"))
            version = data.get("version")
            description = (
                data.get("description")
                or f"Ruleset for {path.stem.replace('-', ' ')}"
            )
            rules.append(
                Asset(
                    name=path.stem,
                    category=AssetCategory.RULES,
                    source_path=path,
                    description=description[:100] + "..." if len(description) > 100 else description,
                    version=version,
                    metadata=data,
                )
            )
        except (OSError, Exception):
            continue

    return sorted(rules, key=lambda a: a.name)


def _describe_settings_file(path: Path) -> str:
    """Best-effort description for a settings file."""
    try:
        if path.suffix == ".json":
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                desc = data.get("description") or data.get("title")
                if desc:
                    return str(desc)
    except Exception:
        pass

    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith("#"):
                return stripped.lstrip("#").strip()
            if stripped.startswith("//"):
                return stripped.lstrip("/").strip()
            return stripped
    except OSError:
        pass

    return f"Settings: {path.name}"


def _discover_settings(plugin_root: Path) -> List[Asset]:
    """Discover shared settings/config files for agents and skills."""
    settings: List[Asset] = []

    for rel_path in _SETTINGS_RELATIVE_PATHS:
        path = plugin_root / rel_path
        if not path.exists():
            continue

        description = _describe_settings_file(path)
        settings.append(
            Asset(
                name=rel_path.as_posix(),
                category=AssetCategory.SETTINGS,
                source_path=path,
                description=description[:100] + "..." if len(description) > 100 else description,
                metadata={},
            )
        )

    return sorted(settings, key=lambda a: a.name)


def _discover_profiles(plugin_root: Path) -> List[Asset]:
    """Discover reusable profiles."""
    profiles: List[Asset] = []
    profiles_dir = plugin_root / "profiles"
    if not profiles_dir.exists():
        return profiles

    for path in profiles_dir.glob("*.md"):
        if path.name == "README.md":
            continue
        try:
            content = path.read_text(encoding="utf-8")
            description = content.strip().split("\n")[0]
            profiles.append(
                Asset(
                    name=path.stem,
                    category=AssetCategory.PROFILES,
                    source_path=path,
                    description=description[:100] + "..." if len(description) > 100 else description,
                    metadata={},
                )
            )
        except OSError:
            continue

    return sorted(profiles, key=lambda a: a.name)


def _discover_scenarios(plugin_root: Path) -> List[Asset]:
    """Discover scenario templates."""
    scenarios: List[Asset] = []
    scenarios_dir = plugin_root / "scenarios"
    if not scenarios_dir.exists():
        return scenarios

    for path in scenarios_dir.glob("*.md"):
        if path.name == "README.md":
            continue
        try:
            content = path.read_text(encoding="utf-8")
            description = content.strip().split("\n")[0]
            scenarios.append(
                Asset(
                    name=path.stem,
                    category=AssetCategory.SCENARIOS,
                    source_path=path,
                    description=description[:100] + "..." if len(description) > 100 else description,
                    metadata={},
                )
            )
        except OSError:
            continue

    return sorted(scenarios, key=lambda a: a.name)


def _discover_tasks(plugin_root: Path) -> List[Asset]:
    """Discover task templates."""
    tasks: List[Asset] = []
    tasks_dir = plugin_root / "tasks"
    if not tasks_dir.exists():
        return tasks

    for path in tasks_dir.glob("*.md"):
        if path.name == "README.md":
            continue
        try:
            content = path.read_text(encoding="utf-8")
            description = content.strip().split("\n")[0]
            tasks.append(
                Asset(
                    name=path.stem,
                    category=AssetCategory.TASKS,
                    source_path=path,
                    description=description[:100] + "..." if len(description) > 100 else description,
                    metadata={},
                )
            )
        except OSError:
            continue

    return sorted(tasks, key=lambda a: a.name)


def find_claude_directories(start_path: Optional[Path] = None) -> List[ClaudeDir]:
    """Find all cortex directories from start_path up to root and home.

    Args:
        start_path: Starting directory (defaults to cwd)

    Returns:
        List of ClaudeDir objects, ordered by specificity (project first)
    """
    if start_path is None:
        start_path = Path.cwd()

    claude_dirs: List[ClaudeDir] = []
    seen_paths: set[str] = set()

    # Walk up from start_path
    current = start_path.resolve()
    home = Path.home().resolve()
    depth = 0

    while current != current.parent:  # Stop at root
        claude_path = current / ".claude"
        if claude_path.exists() and claude_path.is_dir():
            if str(claude_path) not in seen_paths:
                seen_paths.add(str(claude_path))

                if depth == 0:
                    scope = "project"
                elif claude_path.parent == home:
                    scope = "global"
                else:
                    scope = "parent"

                installed = get_installed_assets(claude_path)
                claude_dirs.append(ClaudeDir(
                    path=claude_path,
                    scope=scope,
                    installed_assets=installed,
                ))

        current = current.parent
        depth += 1

    # Always include ~/.cortex (or CORTEX_ROOT) as global target
    global_root = _resolve_claude_dir(home, scope="global")
    if str(global_root) not in seen_paths:
        installed = get_installed_assets(global_root)
        claude_dirs.append(ClaudeDir(
            path=global_root,
            scope="global",
            installed_assets=installed,
        ))
        seen_paths.add(str(global_root))

    # If a legacy ~/.claude exists, surface it as a secondary option
    legacy_root = home / ".claude"
    if legacy_root.exists() and str(legacy_root) not in seen_paths:
        installed = get_installed_assets(legacy_root)
        claude_dirs.append(ClaudeDir(
            path=legacy_root,
            scope="legacy",
            installed_assets=installed,
        ))
        seen_paths.add(str(legacy_root))

    return claude_dirs


def get_installed_assets(claude_dir: Path) -> Dict[str, List[str]]:
    """Get list of installed assets in a cortex directory.

    Args:
        claude_dir: Path to cortex directory

    Returns:
        Dict mapping category names to lists of asset names
    """
    installed: Dict[str, List[str]] = {
        "hooks": [],
        "commands": [],
        "agents": [],
        "skills": [],
        "modes": [],
        "workflows": [],
        "flags": [],
        "rules": [],
        "profiles": [],
        "scenarios": [],
        "tasks": [],
        "settings": [],
    }

    # Hooks
    hooks_dir = claude_dir / "hooks"
    if hooks_dir.exists():
        for f in hooks_dir.iterdir():
            if f.is_file() and f.suffix in (".py", ".sh"):
                installed["hooks"].append(f.stem)

    # Commands
    commands_dir = claude_dir / "commands"
    if commands_dir.exists():
        for item in commands_dir.iterdir():
            if item.is_dir():
                # Namespaced commands
                ns = item.name
                for cmd in item.glob("*.md"):
                    if cmd.name != "README.md":
                        try:
                            content = cmd.read_text(encoding="utf-8")
                        except OSError:
                            installed["commands"].append(f"{ns}:{cmd.stem}")
                            continue
                        front_matter = _parse_command_front_matter(content)
                        name, resolved_ns = _resolve_command_name(cmd, ns, front_matter)
                        if resolved_ns:
                            installed["commands"].append(f"{resolved_ns}:{name}")
                        else:
                            installed["commands"].append(name)
            elif item.is_file() and item.suffix == ".md":
                if item.name != "README.md":
                    try:
                        content = item.read_text(encoding="utf-8")
                    except OSError:
                        installed["commands"].append(item.stem)
                        continue
                    front_matter = _parse_command_front_matter(content)
                    name, resolved_ns = _resolve_command_name(item, None, front_matter)
                    if resolved_ns:
                        installed["commands"].append(f"{resolved_ns}:{name}")
                    else:
                        installed["commands"].append(name)

    # Agents (both active and inactive)
    for agent_dir in [claude_dir / "agents", claude_dir / "inactive" / "agents"]:
        if agent_dir.exists():
            for f in agent_dir.glob("*.md"):
                if f.name not in ("README.md", "dependencies.map"):
                    if f.stem not in installed["agents"]:
                        installed["agents"].append(f.stem)

    # Skills
    skills_dir = claude_dir / "skills"
    if skills_dir.exists():
        for item in skills_dir.iterdir():
            if item.is_dir() and (item / "SKILL.md").exists():
                installed["skills"].append(item.name)

    # Modes (both active and inactive)
    for modes_dir in [claude_dir / "modes", claude_dir / "inactive" / "modes"]:
        if modes_dir.exists():
            for f in modes_dir.glob("*.md"):
                if f.name != "README.md":
                    if f.stem not in installed["modes"]:
                        installed["modes"].append(f.stem)

    # Workflows
    workflows_dir = claude_dir / "workflows"
    if workflows_dir.exists():
        for f in workflows_dir.glob("*.yaml"):
            installed["workflows"].append(f.stem)

    # Flags
    flags_dir = claude_dir / "flags"
    if flags_dir.exists():
        for f in flags_dir.glob("*.md"):
            if f.name != "README.md":
                installed["flags"].append(f.stem)

    # Rules (JSON in skills/)
    rules_dir = claude_dir / "skills"
    for rule_name in ("skill-rules.json", "recommendation-rules.json"):
        rule_path = rules_dir / rule_name
        if rule_path.exists():
            installed["rules"].append(rule_path.stem)

    # Profiles
    profiles_dir = claude_dir / "profiles"
    if profiles_dir.exists():
        for f in profiles_dir.glob("*.md"):
            if f.name != "README.md":
                installed["profiles"].append(f.stem)

    # Scenarios
    scenarios_dir = claude_dir / "scenarios"
    if scenarios_dir.exists():
        for f in scenarios_dir.glob("*.md"):
            if f.name != "README.md":
                installed["scenarios"].append(f.stem)

    # Tasks
    tasks_dir = claude_dir / "tasks"
    if tasks_dir.exists():
        for f in tasks_dir.glob("*.md"):
            if f.name != "README.md":
                installed["tasks"].append(f.stem)

    # Settings
    for rel_path in _SETTINGS_RELATIVE_PATHS:
        setting_path = claude_dir / rel_path
        if setting_path.exists():
            installed["settings"].append(rel_path.as_posix())

    return installed


def check_installation_status(
    asset: Asset,
    claude_dir: Path,
) -> InstallStatus:
    """Check the installation status of an asset.

    Args:
        asset: Asset to check
        claude_dir: Target cortex directory

    Returns:
        InstallStatus enum value
    """
    target_path = claude_dir / asset.install_target

    # For skills, check the directory
    if asset.category == AssetCategory.SKILLS:
        skill_dir = claude_dir / "skills" / asset.name
        if not skill_dir.exists():
            return InstallStatus.NOT_INSTALLED

        # Check SKILL.md for changes
        installed_skill = skill_dir / "SKILL.md"
        source_skill = asset.source_path / "SKILL.md"

        if installed_skill.exists() and source_skill.exists():
            try:
                installed_content = installed_skill.read_text(encoding="utf-8")
                source_content = source_skill.read_text(encoding="utf-8")
                if installed_content == source_content:
                    return InstallStatus.INSTALLED_SAME
                return InstallStatus.INSTALLED_DIFFERENT
            except OSError:
                return InstallStatus.INSTALLED_DIFFERENT

        return InstallStatus.INSTALLED_SAME
    # For rules (single JSON files under skills/)
    if asset.category == AssetCategory.RULES:
        if not target_path.exists():
            return InstallStatus.NOT_INSTALLED
        try:
            installed_content = target_path.read_text(encoding="utf-8")
            source_content = asset.source_path.read_text(encoding="utf-8")
            if installed_content == source_content:
                return InstallStatus.INSTALLED_SAME
            return InstallStatus.INSTALLED_DIFFERENT
        except OSError:
            return InstallStatus.INSTALLED_DIFFERENT

    # For other assets, check the file
    if not target_path.exists():
        # Check inactive locations for agents and modes
        if asset.category == AssetCategory.AGENTS:
            inactive_path = claude_dir / "inactive" / "agents" / asset.source_path.name
            if inactive_path.exists():
                target_path = inactive_path
            else:
                return InstallStatus.NOT_INSTALLED
        elif asset.category == AssetCategory.MODES:
            inactive_path = claude_dir / "inactive" / "modes" / asset.source_path.name
            if inactive_path.exists():
                target_path = inactive_path
            else:
                return InstallStatus.NOT_INSTALLED
        else:
            return InstallStatus.NOT_INSTALLED

    # Compare contents
    try:
        installed_content = target_path.read_text(encoding="utf-8")
        source_content = asset.source_path.read_text(encoding="utf-8")

        if installed_content == source_content:
            return InstallStatus.INSTALLED_SAME
        return InstallStatus.INSTALLED_DIFFERENT
    except OSError:
        return InstallStatus.INSTALLED_DIFFERENT


def get_all_assets_flat(
    assets: Optional[Dict[str, List[Asset]]] = None
) -> List[Asset]:
    """Get all assets as a flat list.

    Args:
        assets: Asset dict (will discover if not provided)

    Returns:
        Flat list of all assets sorted by category then name
    """
    if assets is None:
        assets = discover_plugin_assets()

    result = []
    for category in [
        "hooks",
        "commands",
        "agents",
        "skills",
        "modes",
        "workflows",
        "flags",
        "rules",
        "profiles",
        "scenarios",
        "tasks",
        "settings",
    ]:
        result.extend(assets.get(category, []))

    return result
