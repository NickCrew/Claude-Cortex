"""Agent management functions."""

from __future__ import annotations


import builtins
import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess
import time
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Set, Tuple

try:  # pragma: no cover - dependency availability exercised in tests
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore[assignment]

# Import from base module
from .base import (
    BLUE,
    GREEN,
    YELLOW,
    RED,
    NC,
    FrontMatterToken,
    _color,
    _extract_front_matter,
    _extract_scalar_from_paths,
    _extract_values_from_paths,
    _is_disabled,
    _iter_all_files,
    _inactive_category_dir,
    _inactive_dir_candidates,
    _ensure_inactive_category_dir,
    _resolve_claude_dir,
    _tokenize_front_matter,
)


@dataclass
class AgentGraphNode:
    """Represents an agent in the dependency graph."""

    name: str
    slug: str
    path: Path
    category: str
    tier: str
    status: str  # "active" or "disabled"
    requires: List[str] = field(default_factory=list)
    recommends: List[str] = field(default_factory=list)
    required_by: List[str] = field(default_factory=list)
    recommended_by: List[str] = field(default_factory=list)


def _agent_basename(path: Path) -> str:
    name = path.name
    return name[:-3] if name.endswith(".md") else name


def _normalize_agent_filename(name: str) -> str:
    normalized = name.strip()
    if not normalized:
        raise ValueError("empty agent name")
    if not normalized.endswith(".md"):
        normalized = f"{normalized}.md"
    return normalized


def _find_disabled_agent_file(claude_dir: Path, filename: str) -> Optional[Path]:
    for directory in _inactive_dir_candidates(claude_dir, "agents"):
        candidate = directory / filename
        if candidate.is_file():
            return candidate
    return None


def _find_agent_file_any_state(claude_dir: Path, filename: str) -> Optional[Path]:
    """Find agent file in active or disabled directories."""
    agents_dir = claude_dir / "agents"
    active_path = agents_dir / filename
    if active_path.is_file():
        return active_path

    for directory in _inactive_dir_candidates(claude_dir, "agents"):
        candidate = directory / filename
        if candidate.is_file():
            return candidate

    return None


def _normalize_dependency_name(value: str) -> str:
    if not value:
        return value
    return _display_agent_name(value.strip())


def _parse_agent_dependencies(path: Path) -> Tuple[List[str], List[str]]:
    lines = _read_agent_front_matter_lines(path)
    return _parse_dependencies_from_front(lines)


def _read_agent_front_matter_lines(path: Path) -> Optional[List[str]]:
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None

    front = _extract_front_matter(text)
    if front is None:
        return None

    return front.splitlines()


def _parse_agent_metadata_name(lines: Optional[Iterable[str]]) -> Optional[str]:
    tokens = _tokenize_front_matter(lines)
    return _extract_scalar_from_paths(
        tokens,
        (
            ("metadata", "name"),
            ("name",),
        ),
    )


def _parse_dependencies_from_front(
    lines: Optional[Iterable[str]],
) -> Tuple[List[str], List[str]]:
    tokens = _tokenize_front_matter(lines)

    requires = _extract_values_from_paths(
        tokens,
        (
            ("metadata", "dependencies", "requires"),
            ("dependencies", "requires"),
        ),
    )

    recommends = _extract_values_from_paths(
        tokens,
        (
            ("metadata", "dependencies", "recommends"),
            ("dependencies", "recommends"),
        ),
    )

    return requires, recommends


def _display_agent_name(value: str) -> str:
    trimmed = value.strip()
    if trimmed.endswith(".md"):
        return trimmed[:-3]
    return trimmed


def _extract_agent_name(path: Path, lines: Optional[Iterable[str]] = None) -> str:
    """Extract agent name from YAML metadata, fallback to stem."""
    if lines is None:
        lines = _read_agent_front_matter_lines(path)
    metadata_name = _parse_agent_metadata_name(lines)
    if metadata_name:
        return metadata_name
    return path.stem


def _generate_dependency_map(claude_dir: Path) -> None:
    agents_dir = claude_dir / "agents"
    dep_entries: List[Tuple[str, List[str], List[str]]] = []

    def collect(directory: Path) -> None:
        if not directory.is_dir():
            return
        for path in sorted(directory.glob("*.md")):
            lines = _read_agent_front_matter_lines(path)
            agent_name = _extract_agent_name(path, lines)
            requires, recommends = _parse_dependencies_from_front(lines)
            dep_entries.append((agent_name, requires, recommends))

    collect(agents_dir)
    for directory in _inactive_dir_candidates(claude_dir, "agents"):
        collect(directory)

    dep_map_path = agents_dir / "dependencies.map"
    if not dep_entries:
        if dep_map_path.exists():
            dep_map_path.unlink()
        return

    lines = [
        "# Auto-generated by cortex",
        "# Format: agent:requires:recommends",
    ]
    for name, requires, recommends in dep_entries:
        req_str = ",".join(requires)
        rec_str = ",".join(recommends)
        lines.append(f"{name}:{req_str}:{rec_str}")

    dep_map_path.parent.mkdir(parents=True, exist_ok=True)
    dep_map_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _active_agent_files(claude_dir: Path) -> List[Path]:
    agents_dir = claude_dir / "agents"
    if not agents_dir.is_dir():
        return []
    return [
        path
        for path in sorted(agents_dir.glob("*.md"))
        if path.is_file() and not _is_disabled(path)
    ]


def _find_agent_dependents(claude_dir: Path, agent_name: str) -> List[str]:
    dependents: List[str] = []
    for path in _active_agent_files(claude_dir):
        requires, _ = _parse_agent_dependencies(path)
        required_names = {_display_agent_name(item) for item in requires}
        if agent_name in required_names:
            dependents.append(_agent_basename(path))
    return dependents


def build_agent_graph(home: Path | None = None) -> List[AgentGraphNode]:
    """Collect v2 agent metadata for graph rendering."""

    claude_dir = _resolve_claude_dir(home)
    agent_dirs = [(claude_dir / "agents", "active")]
    agent_dirs.extend(
        (directory, "disabled")
        for directory in _inactive_dir_candidates(claude_dir, "agents")
    )

    nodes_by_name: dict[str, AgentGraphNode] = {}

    for directory, status in agent_dirs:
        if not directory.is_dir():
            continue
        for path in sorted(directory.glob("*.md")):
            lines = _read_agent_front_matter_lines(path)
            if not lines:
                continue

            tokens = _tokenize_front_matter(lines)
            version = _extract_scalar_from_paths(
                tokens,
                (
                    ("metadata", "version"),
                    ("version",),
                ),
            )
            if str(version) != "2.0":
                continue

            name = _extract_agent_name(path, lines)
            category = (
                _extract_scalar_from_paths(
                    tokens,
                    (
                        ("metadata", "category"),
                        ("category",),
                    ),
                )
                or "unknown"
            )
            tier = (
                _extract_scalar_from_paths(
                    tokens,
                    (
                        ("metadata", "tier", "id"),
                        ("tier", "id"),
                    ),
                )
                or "unknown"
            )

            requires_raw, recommends_raw = _parse_dependencies_from_front(lines)
            requires = [
                _normalize_dependency_name(item)
                for item in requires_raw
                if item and _normalize_dependency_name(item)
            ]
            recommends = [
                _normalize_dependency_name(item)
                for item in recommends_raw
                if item and _normalize_dependency_name(item)
            ]

            node = AgentGraphNode(
                name=name,
                slug=path.stem,
                path=path,
                category=category,
                tier=tier,
                status=status,
                requires=requires,
                recommends=recommends,
            )

            existing = nodes_by_name.get(name)
            if existing is None or existing.status != "active":
                nodes_by_name[name] = node

    nodes = sorted(
        nodes_by_name.values(),
        key=lambda item: (item.category, item.name.lower()),
    )

    return nodes


def _format_dependency_entries(
    names: Sequence[str],
    status_lookup: dict[str, str],
) -> str:
    if not names:
        return "-"

    formatted: List[str] = []
    for name in names:
        status = status_lookup.get(name, "missing")
        formatted.append(f"{name} ({status})")
    return ", ".join(formatted)


def render_agent_graph(
    nodes: Sequence[AgentGraphNode],
    *,
    use_color: bool = False,
) -> str:
    """Render agent graph table output."""

    if not nodes:
        return "No v2 agents found."

    status_lookup: dict[str, str] = {}
    for node in nodes:
        aliases = {node.name, node.slug}
        for alias in aliases:
            if not alias:
                continue
            if node.status == "active":
                status_lookup[alias] = node.status
            else:
                status_lookup.setdefault(alias, node.status)

    name_width = max(len("Agent"), max(len(node.name) for node in nodes))
    category_width = max(len("Category"), max(len(node.category) for node in nodes))
    tier_width = max(len("Tier"), max(len(node.tier) for node in nodes))
    status_width = max(len("Status"), max(len(node.status) for node in nodes))

    header = (
        f"{'Agent'.ljust(name_width)}  "
        f"{'Category'.ljust(category_width)}  "
        f"{'Tier'.ljust(tier_width)}  "
        f"{'Status'.ljust(status_width)}  "
        "Requires   Recommends"
    )

    lines: List[str] = [header, "-" * len(header)]

    for node in nodes:
        requires = _format_dependency_entries(node.requires, status_lookup)
        recommends = _format_dependency_entries(node.recommends, status_lookup)
        status_text = node.status
        if use_color:
            if node.status == "active":
                status_text = _color(status_text, GREEN)
            elif node.status == "disabled":
                status_text = _color(status_text, YELLOW)
            else:
                status_text = _color(status_text, RED)

        line = (
            f"{node.name.ljust(name_width)}  "
            f"{node.category.ljust(category_width)}  "
            f"{node.tier.ljust(tier_width)}  "
            f"{status_text.ljust(status_width)}  "
            f"{requires}  {recommends}"
        )
        lines.append(line)

    return "\n".join(lines)


def export_agent_graph(nodes: Sequence[AgentGraphNode], destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Auto-generated by cortex agent graph",
        "# Format: agent:requires:recommends",
    ]
    for node in nodes:
        requires = ",".join(node.requires)
        recommends = ",".join(node.recommends)
        lines.append(f"{node.name}:{requires}:{recommends}")
    destination.write_text("\n".join(lines) + "\n", encoding="utf-8")


def agent_graph(
    export_path: str | Path | None = None,
    *,
    home: Path | None = None,
    use_color: bool = False,
) -> Tuple[int, str]:
    nodes = build_agent_graph(home=home)
    output = render_agent_graph(nodes, use_color=use_color)

    if export_path is None:
        return 0, output

    destination = Path(os.path.expanduser(str(export_path)))
    try:
        export_agent_graph(nodes, destination)
    except OSError as exc:  # PermissionError and similar
        return 1, f"{output}\nError exporting dependency map: {exc}"

    try:
        resolved_path = destination.resolve()
    except OSError:
        resolved_path = destination

    export_message = f"Exported dependency map to {resolved_path}"
    return 0, f"{output}\n{export_message}"


def _iter_agent_paths(claude_dir: Path, directory: Path) -> List[Path]:
    if not directory.is_dir():
        return []
    return [
        path
        for path in sorted(directory.glob("*.md"))
        if path.is_file() and path.name != "TRIGGERS.md"
    ]


def _resolve_agent_validation_target(claude_dir: Path, target: str) -> Optional[Path]:
    candidate = Path(target).expanduser()
    if candidate.is_file():
        return candidate

    try:
        normalized = _normalize_agent_filename(target)
    except ValueError:
        return None

    directories = [claude_dir / "agents"]
    directories.extend(_inactive_dir_candidates(claude_dir, "agents"))
    for directory in directories:
        path = directory / normalized
        if path.is_file() and path.name != "TRIGGERS.md":
            return path

    return None


def _load_agent_schema(claude_dir: Path) -> Tuple[int, Optional[Dict[str, Any]], str]:
    schema_path = claude_dir / "schema" / "agent-schema-v2.yaml"
    if not schema_path.is_file():
        message = f"[ERROR] Schema file missing: {schema_path}"
        return 1, None, message

    if yaml is None:
        message = f"{_color('[ERROR]', RED)} PyYAML is not installed. Install it to use 'agent validate'."  # type: ignore[unreachable]
        return 1, None, message

    try:
        schema = yaml.safe_load(schema_path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        message = f"[ERROR] Failed to parse schema: {exc}"
        return 1, None, message

    return 0, schema, ""


def agent_validate(
    *agent_names: str,
    home: Path | None = None,
    include_all: bool | None = None,
) -> Tuple[int, str]:
    claude_dir = _resolve_claude_dir(home)

    code, schema, schema_message = _load_agent_schema(claude_dir)
    if code != 0 or schema is None:
        return code, schema_message

    required_keys = schema.get("required", [])
    fields = schema.get("fields", {})

    allowed_categories = set(fields.get("category", {}).get("enum", []))
    tier_fields = fields.get("tier", {}).get("properties", {})
    allowed_tiers = set(tier_fields.get("id", {}).get("enum", []))
    allowed_strategies = set(tier_fields.get("activation_strategy", {}).get("enum", []))

    include_all = bool(include_all) or not agent_names

    agent_paths: List[Path] = []
    if include_all:
        agent_paths.extend(_iter_agent_paths(claude_dir, claude_dir / "agents"))
        for directory in _inactive_dir_candidates(claude_dir, "agents"):
            agent_paths.extend(_iter_agent_paths(claude_dir, directory))

    seen_paths: Set[Path] = set(agent_paths)

    for name in agent_names:
        resolved = _resolve_agent_validation_target(claude_dir, name)
        if resolved is None:
            return 1, _color(f"Agent file not found: {name}", RED)
        if resolved.name == "TRIGGERS.md":
            continue
        if resolved not in seen_paths:
            seen_paths.add(resolved)
            agent_paths.append(resolved)

    if not agent_paths:
        return 0, _color("No agent files found for validation", YELLOW)

    def dotted_get(data: Dict[str, Any], dotted_key: str) -> Optional[Any]:
        current: Any = data
        for part in dotted_key.split("."):
            if not isinstance(current, dict) or part not in current:
                return None
            current = current[part]
        return current

    warnings: List[str] = []
    errors: List[str] = []
    validated = 0

    for path in agent_paths:
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            errors.append(f"[ERROR] {path}: unable to read file - {exc}")
            continue

        stripped = text.lstrip()
        if not stripped.startswith("---"):
            errors.append(f"[ERROR] {path}: missing YAML front matter")
            continue

        parts = stripped.split("---", 2)
        if len(parts) < 3:
            errors.append(f"[ERROR] {path}: malformed front matter delimiter")
            continue

        header = parts[1]
        if yaml is None:
            errors.append(  # type: ignore[unreachable]
                f"[ERROR] {path}: PyYAML is not installed. Install it to validate agents."
            )
            continue

        try:
            metadata = yaml.safe_load(header) or {}
        except yaml.YAMLError as exc:
            errors.append(f"[ERROR] {path}: YAML parse failure - {exc}")
            continue

        version = metadata.get("version")
        if str(version) != "2.0":
            warnings.append(
                f"[WARN] {path}: version {version or 'missing'} - skipping schema v2 validation"
            )
            continue

        local_errors: List[str] = []

        for key in required_keys:
            value = dotted_get(metadata, key)
            if value in (None, ""):
                local_errors.append(f"missing required field '{key}'")

        category = metadata.get("category")
        if category and allowed_categories and category not in allowed_categories:
            local_errors.append(
                f"invalid category '{category}' (allowed: {sorted(allowed_categories)})"
            )

        tier = metadata.get("tier")
        if isinstance(tier, dict):
            tier_id = tier.get("id")
            if allowed_tiers and tier_id not in allowed_tiers:
                local_errors.append(
                    f"invalid tier.id '{tier_id}' (allowed: {sorted(allowed_tiers)})"
                )
            strategy = tier.get("activation_strategy")
            if strategy and allowed_strategies and strategy not in allowed_strategies:
                local_errors.append(
                    f"invalid tier.activation_strategy '{strategy}' (allowed: {sorted(allowed_strategies)})"
                )
        else:
            local_errors.append("'tier' must be an object")

        tools = metadata.get("tools", {})
        catalog = tools.get("catalog") if isinstance(tools, dict) else None
        if not isinstance(catalog, list) or not catalog:
            local_errors.append("'tools.catalog' must be a non-empty list")

        dependencies = metadata.get("dependencies")
        if dependencies and not isinstance(dependencies, dict):
            local_errors.append("'dependencies' must be an object when provided")

        if local_errors:
            joined = "; ".join(local_errors)
            errors.append(f"[ERROR] {path}: {joined}")
            continue

        validated += 1

    output_lines: List[str] = []
    output_lines.extend(warnings)

    if errors:
        output_lines.extend(errors)
        if validated:
            output_lines.append(f"Validated {validated} agent(s) before failures.")
        output_lines.append(_color("Agent metadata validation failed", RED))
        return 1, "\n".join(output_lines)

    output_lines.append(f"Validated {validated} agent(s) against schema v2.0.")
    output_lines.append(_color("Agent metadata conforms to schema v2.0", GREEN))

    return 0, "\n".join(output_lines)


def _agent_activate_recursive(
    agent_name: str,
    claude_dir: Path,
    stack: List[str],
    messages: List[str],
) -> int:
    try:
        filename = _normalize_agent_filename(agent_name)
    except ValueError:
        messages.append(_color("Please specify an agent to activate", RED))
        return 1

    agents_dir = claude_dir / "agents"
    active_path = agents_dir / filename
    if active_path.is_file():
        messages.append(_color(f"Agent '{agent_name}' is already active", YELLOW))
        return 0

    disabled_path = _find_disabled_agent_file(claude_dir, filename)
    if disabled_path is None:
        messages.append(
            _color(f"Agent '{agent_name}' not found in disabled agents", RED)
        )
        messages.append("Checked: inactive/agents/, agents-disabled/, and agents/disabled/")
        return 1

    if agent_name in stack:
        messages.append(
            _color(
                f"Dependency cycle detected while activating '{agent_name}'",
                RED,
            )
        )
        return 1

    requires_raw, recommends_raw = _parse_agent_dependencies(disabled_path)
    recommends = [_display_agent_name(item) for item in recommends_raw if item]
    recommend_set = set(recommends)
    requires = [
        _display_agent_name(item)
        for item in requires_raw
        if item and _display_agent_name(item) not in recommend_set
    ]

    stack.append(agent_name)
    for dep in requires:
        if dep == agent_name:
            continue
        exit_code = _agent_activate_recursive(dep, claude_dir, stack, messages)
        if exit_code != 0:
            stack.pop()
            return exit_code
    stack.pop()

    agents_dir.mkdir(parents=True, exist_ok=True)
    destination = agents_dir / filename
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        destination.unlink()
    disabled_path.replace(destination)

    messages.append(_color(f"Activated agent: {agent_name}", GREEN))
    if recommends:
        display = " ".join(recommends)
        messages.append(f"{YELLOW}Consider activating:{NC} {display}")

    _generate_dependency_map(claude_dir)
    return 0


def agent_activate(agent: str, home: Path | None = None) -> Tuple[int, str]:
    claude_dir = _resolve_claude_dir(home)
    messages: List[str] = []
    stack: List[str] = []
    exit_code = _agent_activate_recursive(
        _display_agent_name(agent), claude_dir, stack, messages
    )
    return exit_code, "\n".join(messages)


def agent_deactivate(
    agent: str, *, force: bool = False, home: Path | None = None
) -> Tuple[int, str]:
    claude_dir = _resolve_claude_dir(home)
    try:
        filename = _normalize_agent_filename(agent)
    except ValueError:
        return 1, _color("Please specify an agent to deactivate", RED)

    agent_name = _display_agent_name(filename)
    agents_dir = claude_dir / "agents"
    active_path = agents_dir / filename
    if not active_path.is_file():
        return 1, _color(f"Agent '{agent_name}' is not currently active", RED)

    dependents = _find_agent_dependents(claude_dir, agent_name)
    if dependents and not force:
        message = [
            _color(f"Cannot deactivate '{agent_name}' while required by:", RED)
            + f" {' '.join(dependents)}",
            f"Use 'cortex agent deps {agent_name}' to inspect relationships or '--force' to override.",
        ]
        return 1, "\n".join(message)

    destination_dir = _ensure_inactive_category_dir(claude_dir, "agents")

    destination = destination_dir / filename
    if destination.exists():
        destination.unlink()
    active_path.replace(destination)

    messages = [_color(f"Deactivated agent: {agent_name}", YELLOW)]
    if dependents and force:
        messages.append(
            f"{YELLOW}Warning:{NC} left dependents without required agent: {' '.join(dependents)}"
        )

    _generate_dependency_map(claude_dir)
    return 0, "\n".join(messages)


def list_agents(home: Path | None = None) -> str:
    claude_dir = _resolve_claude_dir(home)
    agents_dir = claude_dir / "agents"

    lines: List[str] = [_color("Available agents:", BLUE)]

    for directory in _inactive_dir_candidates(claude_dir, "agents"):
        rel_prefix = "inactive/agents" if directory == _inactive_category_dir(claude_dir, "agents") else directory.relative_to(claude_dir)
        for path in _iter_all_files(directory):
            if not path.name.endswith(".md"):
                continue
            lines.append(
                f"  {_agent_basename(path)} (disabled - in {rel_prefix}/)"
            )

    for path in _iter_all_files(agents_dir):
        if path.name.endswith(".md") and not _is_disabled(path):
            lines.append(f"  {_color(f'{_agent_basename(path)} (active)', GREEN)}")

    return "\n".join(lines)


def agent_status(home: Path | None = None) -> str:
    claude_dir = _resolve_claude_dir(home)
    agents_dir = claude_dir / "agents"

    lines: List[str] = [_color("Active agents:", BLUE)]
    count = 0
    for path in _iter_all_files(agents_dir):
        if path.name.endswith(".md") and not _is_disabled(path):
            lines.append(f"  {_color(_agent_basename(path), GREEN)}")
            count += 1
    lines.append(_color(f"Total active agents: {count}", BLUE))
    return "\n".join(lines)


def agent_deps(agent: str, home: Path | None = None) -> Tuple[int, str]:
    """Show dependency information for an agent."""
    claude_dir = _resolve_claude_dir(home)

    if not agent:
        return 1, _color("Usage:", RED) + " cortex agent deps <agent_name>"

    try:
        filename = _normalize_agent_filename(agent)
    except ValueError:
        return 1, _color(f"Unable to normalize agent name '{agent}'", RED)

    agent_path = _find_agent_file_any_state(claude_dir, filename)
    if agent_path is None:
        agent_name = _display_agent_name(filename)
        return 1, _color(
            f"Agent '{agent_name}' not found in active or disabled directories", RED
        )

    agent_name = _display_agent_name(filename)
    requires_raw, recommends_raw = _parse_agent_dependencies(agent_path)

    # Determine agent status
    agents_dir = claude_dir / "agents"
    status_label = "disabled"
    if agent_path == agents_dir / filename:
        status_label = "active"

    # Build output lines
    lines: List[str] = [f"{_color('Agent:', BLUE)} {agent_name} ({status_label})"]

    def _format_dependency_line(label: str, values: List[str]) -> None:
        formatted: List[str] = []
        for value in values:
            if not value:
                continue
            try:
                dep_filename = _normalize_agent_filename(value)
            except ValueError:
                continue

            dep_base = _display_agent_name(dep_filename)
            dep_status = "missing"

            if (agents_dir / dep_filename).is_file():
                dep_status = "active"
            else:
                if _find_disabled_agent_file(claude_dir, dep_filename) is not None:
                    dep_status = "disabled"

            formatted.append(f"{dep_base} ({dep_status})")

        if not formatted:
            rendered = "(none)"
        else:
            rendered = ", ".join(formatted)

        lines.append(f"{_color(label, BLUE)} {rendered}")

    _format_dependency_line("Requires:", requires_raw)
    _format_dependency_line("Recommends:", recommends_raw)

    return 0, "\n".join(lines)


# Profile management functions


ESSENTIAL_AGENTS = [
    "code-reviewer",
    "debugger",
    "typescript-pro",
    "python-pro",
    "security-auditor",
]

FRONTEND_AGENTS = [
    "typescript-pro",
    "code-reviewer",
]

WEB_DEV_AGENTS = [
    "typescript-pro",
    "python-pro",
    "code-reviewer",
]

BACKEND_AGENTS = [
    "python-pro",
    "security-auditor",
]

DEVOPS_AGENTS = [
    "cloud-architect",
    "deployment-engineer",
    "kubernetes-architect",
    "terraform-specialist",
]

DOCUMENTATION_AGENTS = [
    "code-reviewer",
]

DATA_AI_AGENTS = [
    "python-pro",
]

QUALITY_AGENTS = [
    "code-reviewer",
    "security-auditor",
    "debugger",
]

META_AGENTS = [
    "code-reviewer",
]

DX_AGENTS = [
    "code-reviewer",
    "debugger",
]

PRODUCT_AGENTS = [
    "code-reviewer",
]

FULL_AGENTS = [
    "code-reviewer",
    "debugger",
    "typescript-pro",
    "python-pro",
    "security-auditor",
    "cloud-architect",
    "deployment-engineer",
    "kubernetes-architect",
    "terraform-specialist",
]

BUILT_IN_PROFILES = [
    "minimal",
    "frontend",
    "web-dev",
    "backend",
    "devops",
    "documentation",
    "data-ai",
    "quality",
    "meta",
    "developer-experience",
    "product",
    "full",
]
