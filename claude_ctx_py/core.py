"""Core logic for the claude-ctx Python port."""

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
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, List, Optional, Sequence, Set, Tuple


BLUE = "\033[0;34m"
GREEN = "\033[0;32m"
YELLOW = "\033[0;33m"
RED = "\033[0;31m"
NC = "\033[0m"


def _color(text: str, color: str) -> str:
    return f"{color}{text}{NC}"


try:  # pragma: no cover - dependency availability exercised in tests
    import yaml  # type: ignore
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore[assignment]


def _resolve_claude_dir(home: Path | None = None) -> Path:
    """Resolve the working Claude directory.

    Preference order:

    1. Explicit override via ``CLAUDE_CTX_HOME``
    2. Plugin runtime via ``CLAUDE_PLUGIN_ROOT`` (set by Claude Code when
       commands execute inside a plugin sandbox)
    3. Caller-provided ``home`` argument
    4. ``$HOME/.claude`` fallback
    """

    override = os.environ.get("CLAUDE_CTX_HOME") or os.environ.get("CLAUDE_PLUGIN_ROOT")
    if override:
        path = Path(override).expanduser().resolve()
        if path.exists():
            return path

    if home is not None:
        base = Path(home)
    else:
        base = Path(os.environ.get("HOME", str(Path.home())))
    return base / ".claude"


def _resolve_init_dirs(claude_dir: Path) -> Tuple[Path, Path, Path]:
    """Ensure init directories exist and return (state, projects, cache)."""

    state_dir = claude_dir / ".init"
    projects_dir = state_dir / "projects"
    cache_dir = state_dir / "cache"

    for path in (state_dir, projects_dir, cache_dir):
        path.mkdir(parents=True, exist_ok=True)

    return state_dir, projects_dir, cache_dir


def _init_slug_for_path(path: Path) -> str:
    """Generate a stable slug for the given project path."""

    abs_path = str(path.resolve(strict=False))
    hash_part = hashlib.sha1(abs_path.encode("utf-8")).hexdigest()[:12]
    basename = path.name or "root"

    normalized = unicodedata.normalize("NFKD", basename)
    ascii_name = normalized.encode("ascii", "ignore").decode("ascii")
    safe = "".join(char.lower() if char.isalnum() else "-" for char in ascii_name)
    safe = safe.strip("-")
    if not safe:
        safe = "project"
    safe = safe[:40]

    return f"{safe}-{hash_part}"


_ANSI_RE = re.compile(r"\x1B\[[0-9;]*[A-Za-z]")


def _strip_ansi_codes(text: str) -> str:
    if not text:
        return ""
    return _ANSI_RE.sub("", text)


def _run_detection_command(command: Sequence[str], cwd: Path) -> str:
    try:
        result = subprocess.run(
            command,
            cwd=str(cwd),
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        return ""
    except OSError:
        return ""
    if result.returncode != 0:
        return result.stdout or ""
    return result.stdout or ""


def _run_detect_project_type(project_path: Path) -> str:
    return _run_detection_command(["detect_project_type"], project_path).strip()


def _run_analyze_project(project_path: Path) -> str:
    return _run_detection_command(["analyze_project"], project_path)


def _is_disabled(path: Path) -> bool:
    text = str(path)
    return "/disabled/" in text or "/inactive/" in text


def _iter_md_files(directory: Path) -> List[Path]:
    if not directory.is_dir():
        return []
    return sorted(p for p in directory.glob("*.md") if p.is_file())


def _iter_all_files(directory: Path) -> List[Path]:
    if not directory.is_dir():
        return []
    return sorted(p for p in directory.iterdir() if p.is_file())


def _agent_basename(path: Path) -> str:
    name = path.name
    return name[:-3] if name.endswith(".md") else name


def _parse_active_entries(path: Path) -> List[str]:
    """Return non-empty, stripped entries from an ``.active-*`` file."""
    if not path.is_file():
        return []

    entries: List[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        value = raw.strip()
        if value:
            entries.append(value)
    return entries


def _update_with_backup(path: Path, transform: Callable[[str], str]) -> None:
    """Apply ``transform`` to a file while preserving a ``.bak`` backup."""

    if not path.is_file():
        return

    original = path.read_text(encoding="utf-8")
    backup_path = path.with_name(f"{path.name}.bak")
    backup_path.write_text(original, encoding="utf-8")

    updated = transform(original)
    path.write_text(updated, encoding="utf-8")


def _uncomment_rule_line(content: str, rule: str) -> str:
    prefix = f"# @rules/{rule}.md"
    marker = "    # Uncomment to activate"
    replacement = f"@rules/{rule}.md"
    lines = []
    for line in content.splitlines(keepends=True):
        if line.startswith(prefix):
            remainder = line[len(prefix):]
            if remainder.startswith(marker):
                remainder = remainder[len(marker):]
            lines.append(f"{replacement}{remainder}")
        else:
            lines.append(line)
    return "".join(lines)


def _comment_rule_line(content: str, rule: str) -> str:
    prefix = f"@rules/{rule}.md"
    replacement = f"# @rules/{rule}.md    # Uncomment to activate"
    lines = []
    for line in content.splitlines(keepends=True):
        if line.startswith(prefix):
            remainder = line[len(prefix):]
            lines.append(f"{replacement}{remainder}")
        else:
            lines.append(line)
    return "".join(lines)


def _remove_exact_entries(content: str, value: str) -> str:
    """Remove lines that exactly match ``value`` from newline-delimited content."""

    result: List[str] = []
    for line in content.splitlines(keepends=True):
        if line.rstrip("\n") == value:
            continue
        result.append(line)
    return "".join(result)


def _normalize_agent_filename(name: str) -> str:
    normalized = name.strip()
    if not normalized:
        raise ValueError("empty agent name")
    if not normalized.endswith(".md"):
        normalized = f"{normalized}.md"
    return normalized


def _find_disabled_agent_file(claude_dir: Path, filename: str) -> Optional[Path]:
    preferred = claude_dir / "agents-disabled" / filename
    if preferred.is_file():
        return preferred
    legacy = claude_dir / "agents" / "disabled" / filename
    if legacy.is_file():
        return legacy
    return None


def _find_agent_file_any_state(claude_dir: Path, filename: str) -> Optional[Path]:
    """Find agent file in active or disabled directories."""
    agents_dir = claude_dir / "agents"
    active_path = agents_dir / filename
    if active_path.is_file():
        return active_path

    disabled_external = claude_dir / "agents-disabled" / filename
    if disabled_external.is_file():
        return disabled_external

    disabled_legacy = agents_dir / "disabled" / filename
    if disabled_legacy.is_file():
        return disabled_legacy

    return None


def _extract_front_matter(text: str) -> Optional[str]:
    stripped = text.lstrip()
    if not stripped.startswith("---"):
        return None
    parts = stripped.split("---", 2)
    if len(parts) < 3:
        return None
    return parts[1]


FrontMatterToken = Tuple[int, str]


def _tokenize_front_matter(lines: Optional[Iterable[str]]) -> List[FrontMatterToken]:
    tokens: List[FrontMatterToken] = []
    if not lines:
        return tokens
    for raw_line in lines:
        line = raw_line.rstrip("\n")
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(line) - len(line.lstrip(" "))
        tokens.append((indent, stripped))
    return tokens


def _strip_inline_comment(value: str) -> str:
    if not value:
        return value
    if " #" in value:
        value = value.split(" #", 1)[0]
    return value.strip()


def _clean_scalar(value: str) -> str:
    value = _strip_inline_comment(value)
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        value = value[1:-1]
    return value.strip()


def _parse_inline_list(value: str) -> List[str]:
    inner = value[1:-1].strip()
    if not inner:
        return []

    items: List[str] = []
    current: List[str] = []
    in_quote = False
    quote_char = ""

    for char in inner:
        if in_quote:
            current.append(char)
            if char == quote_char:
                in_quote = False
            continue

        if char in {'"', "'"}:
            in_quote = True
            quote_char = char
            current.append(char)
            continue

        if char == ',':
            item = "".join(current).strip()
            if item:
                items.append(item)
            current = []
            continue

        current.append(char)

    tail = "".join(current).strip()
    if tail:
        items.append(tail)

    return [_clean_scalar(item) for item in items if _clean_scalar(item)]


def _find_key(
    tokens: Sequence[FrontMatterToken],
    start_index: int,
    key: str,
    parent_indent: int,
) -> Optional[Tuple[int, int, str]]:
    prefix = f"{key}:"
    for index in range(start_index, len(tokens)):
        indent, stripped = tokens[index]
        if indent <= parent_indent:
            return None
        if stripped.startswith(prefix):
            remainder = stripped[len(prefix):].strip()
            return index, indent, remainder
    return None


def _locate_path(
    tokens: Sequence[FrontMatterToken], path: Sequence[str]
) -> Optional[Tuple[int, int, str]]:
    index = -1
    parent_indent = -1
    remainder = ""
    for key in path:
        found = _find_key(tokens, index + 1, key, parent_indent)
        if found is None:
            return None
        index, parent_indent, remainder = found
    return index, parent_indent, remainder


def _collect_list_items(
    tokens: Sequence[FrontMatterToken],
    start_index: int,
    section_indent: int,
) -> List[str]:
    values: List[str] = []
    for index in range(start_index, len(tokens)):
        indent, stripped = tokens[index]
        if indent <= section_indent:
            break
        if stripped.startswith("- "):
            values.append(_clean_scalar(stripped[2:]))
    return [value for value in values if value]


def _extract_values_for_path(
    tokens: Sequence[FrontMatterToken], path: Sequence[str]
) -> Optional[List[str]]:
    located = _locate_path(tokens, path)
    if located is None:
        return None

    index, indent, remainder = located
    remainder = _strip_inline_comment(remainder)

    if remainder:
        if remainder.startswith("[") and remainder.endswith("]"):
            return _parse_inline_list(remainder)
        cleaned = _clean_scalar(remainder)
        return [cleaned] if cleaned else []

    return _collect_list_items(tokens, index + 1, indent)


def _extract_values_from_paths(
    tokens: Sequence[FrontMatterToken], paths: Sequence[Sequence[str]]
) -> List[str]:
    for path in paths:
        values = _extract_values_for_path(tokens, path)
        if values is not None:
            return values
    return []


def _extract_scalar_from_paths(
    tokens: Sequence[FrontMatterToken], paths: Sequence[Sequence[str]]
) -> Optional[str]:
    for path in paths:
        located = _locate_path(tokens, path)
        if located is None:
            continue
        _, _, remainder = located
        cleaned = _clean_scalar(remainder)
        if cleaned:
            return cleaned
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
    collect(claude_dir / "agents-disabled")
    collect(agents_dir / "disabled")

    dep_map_path = agents_dir / "dependencies.map"
    if not dep_entries:
        if dep_map_path.exists():
            dep_map_path.unlink()
        return

    lines = [
        "# Auto-generated by claude-ctx",
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


@dataclass
class AgentGraphNode:
    name: str
    slug: str
    category: str
    tier: str
    status: str
    requires: List[str]
    recommends: List[str]


def build_agent_graph(home: Path | None = None) -> List[AgentGraphNode]:
    """Collect v2 agent metadata for graph rendering."""

    claude_dir = _resolve_claude_dir(home)
    agent_dirs = [
        (claude_dir / "agents", "active"),
        (claude_dir / "agents-disabled", "disabled"),
        (claude_dir / "agents" / "disabled", "disabled"),
    ]

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
            category = _extract_scalar_from_paths(
                tokens,
                (
                    ("metadata", "category"),
                    ("category",),
                ),
            ) or "unknown"
            tier = _extract_scalar_from_paths(
                tokens,
                (
                    ("metadata", "tier", "id"),
                    ("tier", "id"),
                ),
            ) or "unknown"

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
        "# Auto-generated by claude-ctx agent graph",
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


def rules_status(home: Path | None = None) -> str:
    claude_dir = _resolve_claude_dir(home)
    active_file = claude_dir / ".active-rules"

    lines: List[str] = [_color("Active rule modules:", BLUE)]

    if active_file.is_file():
        entries = [line.strip() for line in active_file.read_text(encoding="utf-8").splitlines() if line.strip()]
    else:
        entries = []

    if entries:
        for rule in entries:
            lines.append(f"  {_color(rule, GREEN)}")
    else:
        lines.append("  None")

    return "\n".join(lines)


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

    for directory in (
        claude_dir / "agents",
        claude_dir / "agents-disabled",
        claude_dir / "agents" / "disabled",
    ):
        path = directory / normalized
        if path.is_file() and path.name != "TRIGGERS.md":
            return path

    return None


def _load_agent_schema(claude_dir: Path) -> Tuple[int, Optional[dict], str]:
    schema_path = claude_dir / "schema" / "agent-schema-v2.yaml"
    if not schema_path.is_file():
        message = f"[ERROR] Schema file missing: {schema_path}"
        return 1, None, message

    try:
        import yaml
    except ImportError:
        message = (
            f"{_color('[ERROR]', RED)} PyYAML is not installed. Install it to use 'agent validate'."
        )
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
    allowed_strategies = set(
        tier_fields.get("activation_strategy", {}).get("enum", [])
    )

    include_all = bool(include_all) or not agent_names

    agent_paths: List[Path] = []
    if include_all:
        agent_paths.extend(
            _iter_agent_paths(claude_dir, claude_dir / "agents")
        )
        agent_paths.extend(
            _iter_agent_paths(claude_dir, claude_dir / "agents-disabled")
        )

    seen_paths: set[Path] = set(agent_paths)

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

    def dotted_get(data, dotted_key: str):
        current = data
        for part in dotted_key.split('.'):
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
        if not stripped.startswith('---'):
            errors.append(f"[ERROR] {path}: missing YAML front matter")
            continue

        parts = stripped.split('---', 2)
        if len(parts) < 3:
            errors.append(f"[ERROR] {path}: malformed front matter delimiter")
            continue

        header = parts[1]
        try:
            import yaml  # type: ignore
        except ImportError:
            errors.append(
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
            joined = '; '.join(local_errors)
            errors.append(f"[ERROR] {path}: {joined}")
            continue

        validated += 1

    output_lines: List[str] = []
    output_lines.extend(warnings)

    if errors:
        output_lines.extend(errors)
        if validated:
            output_lines.append(
                f"Validated {validated} agent(s) before failures."
            )
        output_lines.append(
            _color("Agent metadata validation failed", RED)
        )
        return 1, "\n".join(output_lines)

    output_lines.append(
        f"Validated {validated} agent(s) against schema v2.0."
    )
    output_lines.append(
        _color("Agent metadata conforms to schema v2.0", GREEN)
    )

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
        messages.append("Checked: agents-disabled/ and agents/disabled/")
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
    exit_code = _agent_activate_recursive(_display_agent_name(agent), claude_dir, stack, messages)
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
            _color(
                f"Cannot deactivate '{agent_name}' while required by:", RED
            )
            + f" {' '.join(dependents)}",
            f"Use 'claude-ctx agent deps {agent_name}' to inspect relationships or '--force' to override.",
        ]
        return 1, "\n".join(message)

    disabled_dir = claude_dir / "agents-disabled"
    if disabled_dir.is_dir():
        destination_dir = disabled_dir
    else:
        destination_dir = agents_dir / "disabled"
        destination_dir.mkdir(parents=True, exist_ok=True)

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


def rules_activate(rule: str, home: Path | None = None) -> str:
    """Activate a rule module, mirroring the Bash implementation."""

    claude_dir = _resolve_claude_dir(home)
    claude_dir.mkdir(parents=True, exist_ok=True)

    active_rules = claude_dir / ".active-rules"
    with active_rules.open("a", encoding="utf-8") as handle:
        handle.write(f"{rule}\n")

    claude_md = claude_dir / "CLAUDE.md"
    _update_with_backup(claude_md, lambda content: _uncomment_rule_line(content, rule))

    return _color(f"Activated rule module: {rule}", GREEN)


def rules_deactivate(rule: str, home: Path | None = None) -> str:
    """Deactivate a rule module, restoring comment markers and state."""

    claude_dir = _resolve_claude_dir(home)
    claude_dir.mkdir(parents=True, exist_ok=True)

    active_rules = claude_dir / ".active-rules"
    if active_rules.is_file():
        _update_with_backup(
            active_rules, lambda content: _remove_exact_entries(content, rule)
        )

    claude_md = claude_dir / "CLAUDE.md"
    _update_with_backup(claude_md, lambda content: _comment_rule_line(content, rule))

    return _color(f"Deactivated rule module: {rule}", YELLOW)


def _backup_config(claude_dir: Path) -> None:
    claude_md = claude_dir / "CLAUDE.md"
    if not claude_md.is_file():
        return
    timestamp = int(time.time())
    backup_path = claude_dir / f"CLAUDE.md.backup.{timestamp}"
    backup_path.write_text(claude_md.read_text(encoding="utf-8"), encoding="utf-8")


def _render_section(lines: Iterable[str]) -> str:
    return "\n".join(lines) + "\n"


def _refresh_claude_md(claude_dir: Path) -> None:
    claude_dir.mkdir(parents=True, exist_ok=True)

    rules_dir = claude_dir / "rules"
    modes_dir = claude_dir / "modes"
    inactive_modes_dir = modes_dir / "inactive"

    active_rules = set(_parse_active_entries(claude_dir / ".active-rules"))
    available_rules = (
        sorted(p.stem for p in rules_dir.glob("*.md")) if rules_dir.is_dir() else []
    )
    active_modes = _parse_active_entries(claude_dir / ".active-modes")
    inactive_modes = (
        sorted(p.stem for p in inactive_modes_dir.glob("*.md"))
        if inactive_modes_dir.is_dir()
        else []
    )

    claude_md = claude_dir / "CLAUDE.md"
    _backup_config(claude_dir)

    sections: List[str] = []
    sections.append(
        _render_section(
            [
                "# Claude Framework Entry Point",
                "",
                "# Core Framework",
                "@FLAGS.md",
                "@PRINCIPLES.md",
                "@RULES.md",
                "",
                "# Workflow Rules (load for all development tasks)",
                "@rules/workflow-rules.md",
                "",
                "# Conditional Rules (load as needed)",
            ]
        )
    )

    rule_lines: List[str] = []
    for rule in available_rules:
        if rule == "workflow-rules":
            continue
        if rule in active_rules:
            rule_lines.append(f"@rules/{rule}.md")
        else:
            rule_lines.append(f"# @rules/{rule}.md    # Uncomment to activate")
    rule_lines.append("")
    sections.append(_render_section(rule_lines))

    mode_lines: List[str] = ["# Active Behavioral Modes"]
    mode_lines.extend(f"@modes/{mode}.md" for mode in active_modes)
    mode_lines.append("")
    mode_lines.append("# Inactive Modes (move to active/ as needed)")
    mode_lines.extend(f"# @modes/inactive/{mode}.md" for mode in inactive_modes)
    mode_lines.append("")
    sections.append(_render_section(mode_lines))

    sections.append(
        _render_section(
            [
                "# MCP Documentation",
                "@mcp/docs/Context7.md",
                "@mcp/docs/Sequential.md",
                "@mcp/docs/Serena.md",
            ]
        )
    )

    claude_md.write_text("".join(sections), encoding="utf-8")


def _mode_active_file(claude_dir: Path) -> Path:
    return claude_dir / ".active-modes"


def _mode_inactive_dir(claude_dir: Path) -> Path:
    return claude_dir / "modes" / "inactive"


def mode_activate(mode: str, home: Path | None = None) -> tuple[int, str]:
    claude_dir = _resolve_claude_dir(home)
    modes_dir = claude_dir / "modes"
    inactive_dir = _mode_inactive_dir(claude_dir)
    inactive_path = inactive_dir / f"{mode}.md"
    active_path = modes_dir / f"{mode}.md"

    if not inactive_path.is_file():
        return 1, _color(f"Mode '{mode}' not found in inactive modes", RED)

    modes_dir.mkdir(parents=True, exist_ok=True)
    inactive_dir.mkdir(parents=True, exist_ok=True)
    active_path.parent.mkdir(parents=True, exist_ok=True)

    if active_path.exists():
        active_path.unlink()
    inactive_path.replace(active_path)

    active_modes = _mode_active_file(claude_dir)
    with active_modes.open("a", encoding="utf-8") as handle:
        handle.write(f"{mode}\n")

    _refresh_claude_md(claude_dir)
    return 0, _color(f"Activated mode: {mode}", GREEN)


def mode_deactivate(mode: str, home: Path | None = None) -> tuple[int, str]:
    claude_dir = _resolve_claude_dir(home)
    modes_dir = claude_dir / "modes"
    active_path = modes_dir / f"{mode}.md"
    inactive_dir = _mode_inactive_dir(claude_dir)
    inactive_path = inactive_dir / f"{mode}.md"

    if not active_path.is_file():
        return 1, _color(f"Mode '{mode}' is not currently active", RED)

    inactive_dir.mkdir(parents=True, exist_ok=True)
    if inactive_path.exists():
        inactive_path.unlink()
    active_path.replace(inactive_path)

    active_modes = _mode_active_file(claude_dir)
    if active_modes.is_file():
        _update_with_backup(
            active_modes, lambda content: _remove_exact_entries(content, mode)
        )
    else:
        active_modes.touch(exist_ok=True)

    _refresh_claude_md(claude_dir)

    return 0, _color(f"Deactivated mode: {mode}", YELLOW)


def list_modes(home: Path | None = None) -> str:
    claude_dir = _resolve_claude_dir(home)
    modes_dir = claude_dir / "modes"

    lines: List[str] = [_color("Available modes:", BLUE)]

    inactive_dir = modes_dir / "inactive"
    for path in _iter_md_files(inactive_dir):
        lines.append(f"  {path.stem} (inactive)")

    disabled_dir = modes_dir / "disabled"
    for path in _iter_md_files(disabled_dir):
        lines.append(f"  {path.stem} (disabled)")

    for path in _iter_md_files(modes_dir):
        if _is_disabled(path):
            continue
        lines.append(f"  {_color(f'{path.stem} (active)', GREEN)}")

    return "\n".join(lines)


def mode_status(home: Path | None = None) -> str:
    claude_dir = _resolve_claude_dir(home)
    active_file = claude_dir / ".active-modes"

    lines: List[str] = [_color("Active modes:", BLUE)]
    if active_file.is_file():
        for raw in active_file.read_text(encoding="utf-8").splitlines():
            lines.append(f"  {_color(raw, GREEN)}")
    else:
        lines.append("  None")
    return "\n".join(lines)


def list_agents(home: Path | None = None) -> str:
    claude_dir = _resolve_claude_dir(home)
    agents_dir = claude_dir / "agents"
    disabled_external_dir = claude_dir / "agents-disabled"

    lines: List[str] = [_color("Available agents:", BLUE)]

    disabled_dir = agents_dir / "disabled"
    for path in _iter_all_files(disabled_dir):
        if not path.name.endswith(".md"):
            continue
        lines.append(f"  {_agent_basename(path)} (disabled - in agents/disabled/)")

    for path in _iter_all_files(disabled_external_dir):
        if not path.name.endswith(".md"):
            continue
        lines.append(f"  {_agent_basename(path)} (disabled - in agents-disabled/)")

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


def list_rules(home: Path | None = None) -> str:
    claude_dir = _resolve_claude_dir(home)
    rules_dir = claude_dir / "rules"
    active_rules_file = claude_dir / ".active-rules"

    active_rules = set(_parse_active_entries(active_rules_file))

    lines: List[str] = [_color("Available rule modules:", BLUE)]
    for path in _iter_md_files(rules_dir):
        if _is_disabled(path):
            continue
        rule_name = path.stem
        if rule_name in active_rules:
            lines.append(f"  {_color(f'{rule_name} (active)', GREEN)}")
        else:
            lines.append(f"  {rule_name} (inactive)")

    return "\n".join(lines)


def show_status(home: Path | None = None) -> str:
    claude_dir = _resolve_claude_dir(home)
    home_arg = claude_dir.parent

    sections: List[str] = [_color("=== Claude Context Status ===", BLUE)]
    sections.append("")
    sections.append(agent_status(home=home_arg))
    sections.append("")
    sections.append(mode_status(home=home_arg))
    sections.append("")

    lines: List[str] = [_color("Active rule modules:", BLUE)]
    active_rules_file = claude_dir / ".active-rules"
    active_rules = _parse_active_entries(active_rules_file)
    if active_rules:
        for raw in active_rules:
            lines.append(f"  {_color(raw, GREEN)}")
    else:
        lines.append("  None")

    sections.append("\n".join(lines))
    return "\n".join(sections)


def list_skills(home: Path | None = None) -> str:
    """List all available skills."""
    claude_dir = _resolve_claude_dir(home)
    skills_dir = claude_dir / "skills"

    if not skills_dir.is_dir():
        return "No skills directory found."

    skills: List[Tuple[str, str]] = []

    for skill_path in sorted(skills_dir.iterdir()):
        if not skill_path.is_dir():
            continue

        skill_file = skill_path / "SKILL.md"
        if not skill_file.is_file():
            continue

        skill_name = skill_path.name

        # Extract description from frontmatter
        try:
            content = skill_file.read_text(encoding="utf-8")
            front_matter = _extract_front_matter(content)
            if front_matter:
                lines = front_matter.strip().splitlines()
                tokens = _tokenize_front_matter(lines)
                description = _extract_scalar_from_paths(
                    tokens, (("description",),)
                ) or "No description"
            else:
                description = "No description"
        except Exception:
            description = "Error reading skill"

        skills.append((skill_name, description))

    if not skills:
        return "No skills found."

    lines: List[str] = [_color("Available skills:", BLUE)]

    # Find max skill name length for alignment
    max_name_len = max(len(name) for name, _ in skills) if skills else 0

    for skill_name, description in skills:
        # Truncate description if too long
        max_desc_len = 80
        if len(description) > max_desc_len:
            description = description[:max_desc_len-3] + "..."

        lines.append(f"  {_color(skill_name.ljust(max_name_len), GREEN)}  {description}")

    return "\n".join(lines)


def skill_info(skill: str, home: Path | None = None) -> Tuple[int, str]:
    """Show detailed information about a skill."""
    claude_dir = _resolve_claude_dir(home)
    skills_dir = claude_dir / "skills"

    if not skill:
        return 1, _color("Usage:", RED) + " claude-ctx skills info <skill_name>"

    skill_path = skills_dir / skill / "SKILL.md"

    if not skill_path.is_file():
        return 1, _color(f"Skill '{skill}' not found", RED)

    try:
        content = skill_path.read_text(encoding="utf-8")
    except Exception as exc:
        return 1, _color(f"Error reading skill: {exc}", RED)

    # Extract frontmatter
    front_matter = _extract_front_matter(content)
    if not front_matter:
        return 1, _color(f"Skill '{skill}' has no valid frontmatter", RED)

    lines = front_matter.strip().splitlines()
    tokens = _tokenize_front_matter(lines)

    skill_name = _extract_scalar_from_paths(
        tokens, (("name",),)
    ) or skill
    description = _extract_scalar_from_paths(
        tokens, (("description",),)
    ) or "No description"

    # Count tokens (rough estimate: words * 1.3)
    word_count = len(content.split())
    token_estimate = int(word_count * 1.3)

    output_lines: List[str] = [
        _color(f"=== Skill: {skill_name} ===", BLUE),
        "",
        _color("Description:", BLUE),
        f"  {description}",
        "",
        _color("Size:", BLUE),
        f"  ~{token_estimate} tokens (estimated)",
        "",
        _color("Location:", BLUE),
        f"  {skill_path}",
    ]

    return 0, "\n".join(output_lines)


def skill_validate(*skills: str, home: Path | None = None) -> Tuple[int, str]:
    """Validate skill metadata against required schema."""
    claude_dir = _resolve_claude_dir(home)
    skills_dir = claude_dir / "skills"

    if not skills_dir.is_dir():
        return 1, _color("No skills directory found", RED)

    validate_all = skills and skills[0] == "--all"

    if validate_all:
        skill_targets = [
            p.name for p in sorted(skills_dir.iterdir())
            if p.is_dir() and (p / "SKILL.md").is_file()
        ]
    elif skills:
        skill_targets = list(skills)
    else:
        skill_targets = [
            p.name for p in sorted(skills_dir.iterdir())
            if p.is_dir() and (p / "SKILL.md").is_file()
        ]

    if not skill_targets:
        return 1, _color("No skills to validate", YELLOW)

    results: List[str] = []
    errors: List[str] = []

    for skill_name in skill_targets:
        skill_path = skills_dir / skill_name / "SKILL.md"

        if not skill_path.is_file():
            errors.append(f"  {_color('✗', RED)} {skill_name}: SKILL.md not found")
            continue

        try:
            content = skill_path.read_text(encoding="utf-8")
            front_matter = _extract_front_matter(content)

            if not front_matter:
                errors.append(f"  {_color('✗', RED)} {skill_name}: Missing frontmatter")
                continue

            lines = front_matter.strip().splitlines()
            tokens = _tokenize_front_matter(lines)

            # Validate required fields
            name = _extract_scalar_from_paths(tokens, (("name",),))
            description = _extract_scalar_from_paths(tokens, (("description",),))

            if not name:
                errors.append(f"  {_color('✗', RED)} {skill_name}: Missing 'name' field")
                continue

            if not description:
                errors.append(f"  {_color('✗', RED)} {skill_name}: Missing 'description' field")
                continue

            if len(description) > 1024:
                errors.append(f"  {_color('⚠', YELLOW)} {skill_name}: Description too long ({len(description)} > 1024 chars)")

            if "Use when" not in description:
                errors.append(f"  {_color('⚠', YELLOW)} {skill_name}: Description missing 'Use when' trigger")

            results.append(f"  {_color('✓', GREEN)} {skill_name}: Valid")

        except Exception as exc:
            errors.append(f"  {_color('✗', RED)} {skill_name}: Error reading file: {exc}")

    output_lines: List[str] = [_color("=== Skill Validation ===", BLUE), ""]

    if results:
        output_lines.extend(results)

    if errors:
        if results:
            output_lines.append("")
        output_lines.extend(errors)

    output_lines.append("")
    output_lines.append(
        f"Validated: {len(results)} passed, {len(errors)} issues"
    )

    exit_code = 0 if not errors else 1
    return exit_code, "\n".join(output_lines)


def agent_deps(agent: str, home: Path | None = None) -> Tuple[int, str]:
    """Show dependency information for an agent."""
    claude_dir = _resolve_claude_dir(home)

    if not agent:
        return 1, _color("Usage:", RED) + " claude-ctx agent deps <agent_name>"

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
    lines: List[str] = [
        f"{_color('Agent:', BLUE)} {agent_name} ({status_label})"
    ]

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

BACKEND_AGENTS = [
    "python-pro",
    "database-optimizer",
    "security-auditor",
    "api-documenter",
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


def _profile_reset(home: Path | None = None) -> Tuple[int, str]:
    """Reset to minimal configuration while surfacing any operation failures."""

    claude_dir = _resolve_claude_dir(home)
    agents_dir = claude_dir / "agents"

    # Deactivate non-essential agents currently active
    for agent_file in _iter_md_files(agents_dir):
        if _is_disabled(agent_file):
            continue
        agent_name = _agent_basename(agent_file)
        if agent_name in ESSENTIAL_AGENTS:
            continue
        exit_code, message = agent_deactivate(
            agent_name,
            force=True,
            home=home,
        )
        if exit_code != 0:
            return exit_code, message or _color(
                f"Failed to deactivate agent: {agent_name}", RED
            )

    # Ensure essential agents are active
    for agent_name in ESSENTIAL_AGENTS:
        exit_code, message = agent_activate(agent_name, home=home)
        if exit_code != 0:
            return exit_code, message or _color(
                f"Failed to activate essential agent: {agent_name}", RED
            )

    # Move all modes except Task_Management to inactive
    modes_dir = claude_dir / "modes"
    for mode_file in _iter_md_files(modes_dir):
        if _is_disabled(mode_file):
            continue
        mode_name = mode_file.stem
        if mode_name == "Task_Management":
            continue
        exit_code, message = mode_deactivate(mode_name, home=home)
        if exit_code != 0:
            return exit_code, message or _color(
                f"Failed to deactivate mode: {mode_name}", RED
            )

    # Clear active rules file entirely
    active_rules = claude_dir / ".active-rules"
    try:
        if active_rules.exists():
            active_rules.unlink()
    except OSError as exc:  # pragma: no cover - extremely unlikely
        return 1, _color(f"Failed to clear active rules: {exc}", RED)

    _refresh_claude_md(claude_dir)

    return 0, _color("Reset to minimal configuration", GREEN)


def profile_list(home: Path | None = None) -> str:
    """List all built-in and saved profiles."""
    claude_dir = _resolve_claude_dir(home)

    lines: List[str] = [_color("Available profiles:", BLUE)]

    # Built-in profiles
    for profile in BUILT_IN_PROFILES:
        lines.append(f"  {profile} (built-in)")

    # Saved profiles
    profiles_dir = claude_dir / "profiles"
    if profiles_dir.is_dir():
        for profile_file in sorted(profiles_dir.glob("*.profile")):
            profile_name = profile_file.stem
            lines.append(f"  {_color(f'{profile_name} (saved)', GREEN)}")

    return "\n".join(lines)


def profile_save(name: str, home: Path | None = None) -> Tuple[int, str]:
    """Save current configuration state to a named profile."""
    claude_dir = _resolve_claude_dir(home)
    profiles_dir = claude_dir / "profiles"
    profiles_dir.mkdir(parents=True, exist_ok=True)

    # Collect active agents
    agents_dir = claude_dir / "agents"
    active_agents: List[str] = []
    for agent_file in _iter_all_files(agents_dir):
        if agent_file.name.endswith(".md") and not _is_disabled(agent_file):
            active_agents.append(agent_file.name)

    # Collect active modes
    active_modes = _parse_active_entries(claude_dir / ".active-modes")

    # Collect active rules
    active_rules = _parse_active_entries(claude_dir / ".active-rules")

    # Write profile file
    profile_file = profiles_dir / f"{name}.profile"
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

    content_lines = [
        f"# Profile: {name}",
        f"# Generated: {timestamp}",
        "",
        "# Active agents",
        f"AGENTS=\"{' '.join(active_agents)}\"",
        "",
        "# Active modes",
        f"MODES=\"{' '.join(active_modes)}\"",
        "",
        "# Active rules",
        f"RULES=\"{' '.join(active_rules)}\"",
    ]

    profile_file.write_text("\n".join(content_lines) + "\n", encoding="utf-8")

    return 0, _color(f"Saved profile: {name}", GREEN)


def profile_minimal(home: Path | None = None) -> Tuple[int, str]:
    """Load the minimal profile, failing loudly if prerequisites are missing."""

    exit_code, reset_message = _profile_reset(home=home)
    if exit_code != 0:
        return exit_code, reset_message

    messages = [reset_message, _color("Loaded profile: minimal", GREEN)]
    return 0, "\n".join(messages)


def profile_backend(home: Path | None = None) -> Tuple[int, str]:
    """Load backend profile: minimal + backend-specific agents, Task_Management mode, quality-rules."""
    claude_dir = _resolve_claude_dir(home)

    exit_code, reset_message = _profile_reset(home=home)
    messages: List[str] = []
    if reset_message:
        messages.append(reset_message)
    if exit_code != 0:
        return exit_code, "\n".join(messages)

    for agent_name in BACKEND_AGENTS:
        exit_code, message = agent_activate(agent_name, home=home)
        if exit_code != 0:
            if message:
                messages.append(message)
            else:
                messages.append(
                    _color(f"Failed to activate backend agent: {agent_name}", RED)
                )
            return exit_code, "\n".join(messages)
        if message:
            messages.append(message)

    exit_code, mode_message = mode_activate("Task_Management", home=home)
    if exit_code != 0:
        if mode_message:
            messages.append(mode_message)
        else:
            messages.append(
                _color("Failed to activate Task_Management mode", RED)
            )
        return exit_code, "\n".join(messages)
    if mode_message:
        messages.append(mode_message)

    rule_message = rules_activate("quality-rules", home=home)
    if rule_message:
        messages.append(rule_message)

    _refresh_claude_md(claude_dir)

    messages.append(_color("Loaded profile: backend", GREEN))
    return 0, "\n".join(messages)


def workflow_run(workflow: str, home: Path | None = None) -> Tuple[int, str]:
    """Run a predefined workflow."""
    claude_dir = _resolve_claude_dir(home)
    workflows_dir = claude_dir / "workflows"
    workflow_file = workflows_dir / f"{workflow}.yaml"

    if not workflow_file.is_file():
        available = workflow_list(home=home)
        lines = [
            _color(f"Workflow {workflow!r} not found", RED),
            "Available workflows:",
            available,
        ]
        return 1, "\n".join(lines)

    # Create task directory for this workflow
    tasks_dir = claude_dir / "tasks"
    current_dir = tasks_dir / "current"
    current_dir.mkdir(parents=True, exist_ok=True)

    # Save workflow state
    (current_dir / "active_workflow").write_text(workflow, encoding="utf-8")
    (current_dir / "workflow_status").write_text("pending", encoding="utf-8")
    (current_dir / "workflow_started").write_text(str(int(time.time())), encoding="utf-8")

    lines: List[str] = [
        _color(f"Started workflow: {workflow}", GREEN),
        "",
        _color("Workflow steps will be executed by Claude Code", BLUE),
        f"To check progress: claude-ctx workflow status",
        f"To resume if interrupted: claude-ctx workflow resume",
        "",
        _color("Next: Open Claude Code and the workflow will guide you", YELLOW),
        "",
        _color(f"=== Workflow: {workflow} ===", BLUE),
    ]

    # Show workflow summary
    try:
        content = workflow_file.read_text(encoding="utf-8")
        for line in content.splitlines():
            if line.startswith("description:"):
                lines.append(line.replace("description:", "").strip())
                break
        lines.append("")
        lines.append(_color("Steps:", BLUE))
        for line in content.splitlines():
            if line.strip().startswith("- name:"):
                step_name = line.split("- name:", 1)[1].strip()
                lines.append(f"  → {step_name}")
    except OSError:
        pass

    return 0, "\n".join(lines)


def workflow_list(home: Path | None = None) -> str:
    """List available workflows."""
    claude_dir = _resolve_claude_dir(home)
    workflows_dir = claude_dir / "workflows"

    lines: List[str] = [_color("Available workflows:", BLUE)]

    if not workflows_dir.is_dir():
        return "\n".join(lines)

    for workflow_file in sorted(workflows_dir.glob("*.yaml")):
        if not workflow_file.is_file():
            continue
        workflow_name = workflow_file.stem
        if workflow_name == "README":
            continue

        lines.append(f"  {_color(workflow_name, GREEN)}")
        try:
            content = workflow_file.read_text(encoding="utf-8")
            for line in content.splitlines():
                if line.startswith("description:"):
                    desc = line.replace("description:", "").strip()
                    lines.append(f"    {desc}")
                    break
        except OSError:
            pass

    return "\n".join(lines)


def workflow_status(home: Path | None = None) -> Tuple[int, str]:
    """Show current workflow progress."""
    claude_dir = _resolve_claude_dir(home)
    tasks_dir = claude_dir / "tasks"
    current_dir = tasks_dir / "current"
    active_workflow_file = current_dir / "active_workflow"

    if not active_workflow_file.is_file():
        return 0, _color("No active workflow", YELLOW)

    workflow = active_workflow_file.read_text(encoding="utf-8").strip()
    status_file = current_dir / "workflow_status"
    started_file = current_dir / "workflow_started"

    status = "unknown"
    if status_file.is_file():
        status = status_file.read_text(encoding="utf-8").strip()

    started = 0
    if started_file.is_file():
        try:
            started = int(started_file.read_text(encoding="utf-8").strip())
        except ValueError:
            started = 0

    elapsed = int(time.time()) - started
    hours = elapsed // 3600
    minutes = (elapsed % 3600) // 60

    lines: List[str] = [
        _color("=== Active Workflow ===", BLUE),
        f"Workflow: {_color(workflow, GREEN)}",
        f"Status: {status}",
        f"Elapsed time: {hours}h {minutes}m",
    ]

    current_step_file = current_dir / "current_step"
    if current_step_file.is_file():
        step = current_step_file.read_text(encoding="utf-8").strip()
        lines.append(f"Current step: {_color(step, YELLOW)}")

    return 0, "\n".join(lines)


def workflow_resume(home: Path | None = None) -> Tuple[int, str]:
    """Resume interrupted workflow."""
    claude_dir = _resolve_claude_dir(home)
    tasks_dir = claude_dir / "tasks"
    current_dir = tasks_dir / "current"
    active_workflow_file = current_dir / "active_workflow"

    if not active_workflow_file.is_file():
        return 1, _color("No workflow to resume", YELLOW)

    workflow = active_workflow_file.read_text(encoding="utf-8").strip()
    lines: List[str] = [_color(f"Resuming workflow: {workflow}", GREEN)]

    current_step_file = current_dir / "current_step"
    if current_step_file.is_file():
        step = current_step_file.read_text(encoding="utf-8").strip()
        lines.append(f"Resuming from step: {_color(step, YELLOW)}")

    lines.append("")
    lines.append(_color("Continue in Claude Code - the workflow context has been restored", BLUE))

    return 0, "\n".join(lines)


# Scenario/Orchestrate functions


@dataclass
class ScenarioPhase:
    name: str
    description: str
    condition: str
    parallel: bool
    agents: List[str]
    profiles: List[str]
    success: List[str]


@dataclass
class ScenarioMetadata:
    name: str
    description: str
    priority: str
    scenario_type: str
    phases: List[ScenarioPhase]
    source_file: Path


def _scenario_dirs(claude_dir: Path) -> Tuple[Path, Path, Path]:
    scenarios_dir = claude_dir / "scenarios"
    state_dir = scenarios_dir / ".state"
    lock_dir = scenarios_dir / ".locks"
    return scenarios_dir, state_dir, lock_dir


def _ensure_scenarios_dir(claude_dir: Path) -> Tuple[Path, Path, Path]:
    """Ensure scenarios directory and subdirectories exist."""
    scenarios_dir, state_dir, lock_dir = _scenario_dirs(claude_dir)

    scenarios_dir.mkdir(parents=True, exist_ok=True)
    state_dir.mkdir(parents=True, exist_ok=True)
    lock_dir.mkdir(parents=True, exist_ok=True)

    return scenarios_dir, state_dir, lock_dir


def _scenario_schema_path(claude_dir: Path) -> Path:
    return claude_dir / "schema" / "scenario-schema-v1.yaml"


def _now_iso() -> str:
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def _scenario_lock_basename(value: str) -> str:
    sanitized = value.replace("/", "_").replace("\\", "_").strip()
    return sanitized or "scenario"


def _load_yaml(path: Path) -> Tuple[bool, Any, str]:
    if yaml is None:
        return False, None, "PyYAML is not installed."
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return False, None, f"Failed to read {path}: {exc}"
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        return False, None, f"YAML parse error - {exc}"
    return True, data, ""


def _load_yaml_dict(path: Path) -> Tuple[bool, Dict[str, Any], str]:
    ok, data, error = _load_yaml(path)
    if not ok:
        return False, {}, error
    if data is None:
        return True, {}, ""
    if not isinstance(data, dict):
        return False, {}, "Scenario definition must be a mapping"
    return True, data, ""


def _flatten_mixed(items: Any) -> List[str]:
    if items is None:
        return []
    if isinstance(items, str):
        trimmed = items.strip()
        return [trimmed] if trimmed else []
    if not isinstance(items, list):
        return [str(items)]
    result: List[str] = []
    for item in items:
        if isinstance(item, str):
            trimmed = item.strip()
            if trimmed:
                result.append(trimmed)
        elif isinstance(item, dict):
            for key, value in item.items():
                key_str = str(key).strip()
                if isinstance(value, str):
                    value_str = value.strip()
                    if value_str:
                        result.append(f"{key_str}:{value_str}")
                    elif key_str:
                        result.append(key_str)
                elif key_str:
                    result.append(key_str)
        elif item is not None:
            result.append(str(item))
    return result


def _scenario_init_state(state_file: Path, metadata: ScenarioMetadata) -> None:
    payload = {
        "scenario": metadata.name,
        "description": metadata.description,
        "source": str(metadata.source_file),
        "started": _now_iso(),
        "status": "running",
        "phases": [],
    }
    state_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _scenario_update_phase_state(
    state_file: Path,
    *,
    index: int,
    phase_name: str,
    status: str,
    note: Optional[str] = None,
) -> None:
    try:
        data = json.loads(state_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        data = {}

    phases = data.setdefault("phases", [])
    while len(phases) <= index:
        phases.append({})

    entry = phases[index] or {}
    entry.update({
        "name": phase_name,
        "status": status,
        "updated": _now_iso(),
    })
    if note:
        entry["note"] = note
    else:
        entry.pop("note", None)
    phases[index] = entry

    state_file.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _scenario_finalize_state(state_file: Path, final_status: str) -> None:
    try:
        data = json.loads(state_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        data = {}
    data["status"] = final_status
    data["completed"] = _now_iso()
    state_file.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _collect_scenario_targets(
    names: Sequence[str],
    scenarios_dir: Path,
    messages: List[str],
) -> List[Path]:
    normalized = [name for name in names if name]
    use_all = not normalized or any(name == "--all" for name in normalized)
    if use_all:
        return sorted(scenarios_dir.glob("*.yaml"))

    targets: List[Path] = []
    for raw in normalized:
        if raw == "--all":
            continue
        candidate = scenarios_dir / (raw if raw.endswith(".yaml") else f"{raw}.yaml")
        if candidate.is_file():
            targets.append(candidate)
        else:
            messages.append(_color(f"Scenario file not found: {raw}", RED))
    return targets


def _ensure_list(value: Any, label: str, messages: List[str]) -> List[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    messages.append(f"'{label}' must be a list")
    return []


def _parse_scenario_metadata(
    scenario_path: Path,
) -> Tuple[int, Optional[ScenarioMetadata], str]:
    if not scenario_path.is_file():
        return 1, None, f"Scenario file not found: {scenario_path.name}"

    success, data, error = _load_yaml_dict(scenario_path)
    if not success:
        return 1, None, error

    name = str(data.get("name") or scenario_path.stem)
    description = str(data.get("description") or "")
    priority = str(data.get("priority") or "normal")
    scenario_type = str(data.get("type") or "operational")

    phases_raw = data.get("phases") or []
    if not isinstance(phases_raw, list):
        return 1, None, "invalid phases"

    phases: List[ScenarioPhase] = []
    for idx, raw in enumerate(phases_raw):
        if not isinstance(raw, dict):
            return 1, None, f"phase_{idx}_not_object"
        phase_name = str(raw.get("name") or f"phase_{idx + 1}")
        phase_desc = str(raw.get("description") or "")
        condition = str(raw.get("condition") or "manual")
        parallel = bool(raw.get("parallel", False))
        agents = _flatten_mixed(raw.get("agents") or [])
        profiles = _flatten_mixed(raw.get("profiles") or [])
        success = _flatten_mixed(raw.get("success_criteria") or [])
        phases.append(
            ScenarioPhase(
                name=phase_name,
                description=phase_desc,
                condition=condition,
                parallel=parallel,
                agents=agents,
                profiles=profiles,
                success=success,
            )
        )

    metadata = ScenarioMetadata(
        name=name,
        description=description,
        priority=priority,
        scenario_type=scenario_type,
        phases=phases,
        source_file=scenario_path,
    )
    return 0, metadata, ""


def scenario_list(home: Path | None = None) -> str:
    """List all available scenarios."""
    claude_dir = _resolve_claude_dir(home)
    scenarios_dir, _, _ = _ensure_scenarios_dir(claude_dir)

    if yaml is None:
        return _color("PyYAML is required to manage scenarios.", RED)

    entries: List[Tuple[str, str, str]] = []
    for scenario_file in sorted(scenarios_dir.glob("*.yaml")):
        code, metadata, error_msg = _parse_scenario_metadata(scenario_file)
        if code != 0 or metadata is None:
            entries.append((scenario_file.stem, "invalid YAML", "error"))
            continue
        description = metadata.description or "No description provided"
        entries.append((metadata.name, description, metadata.priority))

    if not entries:
        return "No scenarios defined. Add YAML files under ~/.claude/scenarios/."

    lines: List[str] = ["Available scenarios:\n"]
    for name, desc, priority in entries:
        lines.append(f"- {name} [priority: {priority}]")
        lines.append(f"  {desc}")
    return "\n".join(lines)


def scenario_validate(
    *scenario_names: str,
    home: Path | None = None,
) -> Tuple[int, str]:
    claude_dir = _resolve_claude_dir(home)
    scenarios_dir, _, _ = _ensure_scenarios_dir(claude_dir)

    if yaml is None:
        return 1, _color("PyYAML is required to validate scenarios.", RED)

    messages: List[str] = []
    targets = _collect_scenario_targets(scenario_names, scenarios_dir, messages)

    schema: Dict[str, Any] = {}
    schema_path = _scenario_schema_path(claude_dir)
    if schema_path.is_file():
        ok, raw_schema, error = _load_yaml(schema_path)
        if not ok:
            return 1, _color(f"Failed to parse schema: {error}", RED)
        if isinstance(raw_schema, dict):
            schema = raw_schema

    required_fields = schema.get("required", [])
    fields = schema.get("fields", {})
    allowed_types = set(fields.get("type", {}).get("enum", []))
    allowed_priorities = set(fields.get("priority", {}).get("enum", []))
    allowed_conditions = set(fields.get("condition", {}).get("enum", []))

    if not targets:
        messages.append(_color("No scenario files found for validation", YELLOW))
        return 0, "\n".join(messages)

    exit_code = 0
    for scenario_file in targets:
        success, data, error = _load_yaml_dict(scenario_file)
        if not success:
            messages.append(f"[ERROR] {scenario_file.name}: {error}")
            exit_code = 1
            continue

        errors: List[str] = []
        warnings: List[str] = []

        for key in required_fields:
            if not data.get(key):
                errors.append(f"missing required field '{key}'")

        scenario_type = str(data.get("type", "operational"))
        if allowed_types and scenario_type not in allowed_types:
            warnings.append(
                f"[WARN] {scenario_file.name}: unknown type '{scenario_type}' "
                f"(allowed: {sorted(allowed_types)})"
            )

        priority = str(data.get("priority", "normal"))
        if allowed_priorities and priority not in allowed_priorities:
            warnings.append(
                f"[WARN] {scenario_file.name}: unknown priority '{priority}' "
                f"(allowed: {sorted(allowed_priorities)})"
            )

        phases = data.get("phases")
        if not isinstance(phases, list) or not phases:
            errors.append("'phases' must be a non-empty list")
            phases = []

        for idx, phase in enumerate(phases):
            if not isinstance(phase, dict):
                errors.append(f"phase {idx}: must be an object")
                continue
            if not phase.get("name"):
                errors.append(f"phase {idx}: missing 'name'")
            condition = str(phase.get("condition", "manual"))
            if allowed_conditions and condition not in allowed_conditions:
                warnings.append(
                    f"[WARN] {scenario_file.name}: phase {idx} unknown condition '{condition}' "
                    f"(allowed: {sorted(allowed_conditions)})"
                )
            _ensure_list(phase.get("agents"), f"phases[{idx}].agents", errors)
            _ensure_list(phase.get("profiles"), f"phases[{idx}].profiles", errors)
            if "agents" not in phase and "profiles" not in phase:
                warnings.append(
                    f"[WARN] {scenario_file.name}: phase {idx} has no agents or profiles defined"
                )

        if errors:
            messages.append(f"[ERROR] {scenario_file.name}: {'; '.join(errors)}")
            exit_code = 1
            continue

        messages.extend(warnings)
        messages.append(f"[OK] {scenario_file.name}: valid scenario definition")

    return exit_code, "\n".join(messages)


def scenario_status(home: Path | None = None) -> str:
    claude_dir = _resolve_claude_dir(home)
    _, state_dir, lock_dir = _ensure_scenarios_dir(claude_dir)

    lines: List[str] = []

    locks: List[Tuple[str, str]] = []
    for lock_file in sorted(lock_dir.glob("*.lock")):
        try:
            exec_id = lock_file.read_text(encoding="utf-8").strip()
        except OSError:
            exec_id = ""
        locks.append((lock_file.stem, exec_id))

    if locks:
        lines.append("Active locks:")
        for scenario, exec_id in locks:
            suffix = f": execution {exec_id}" if exec_id else ""
            lines.append(f"- {scenario}{suffix}")
        lines.append("")

    entries: List[Tuple[str, str, str, str]] = []
    for state_file in sorted(state_dir.glob("*.json"), reverse=True):
        try:
            data = json.loads(state_file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        entries.append(
            (
                str(data.get("scenario", "unknown")),
                str(data.get("status", "unknown")),
                str(data.get("started", "unknown")),
                str(data.get("completed", "")),
            )
        )

    if entries:
        lines.append("Recent scenario executions:\n")
        for scenario, status, started, completed in entries[:10]:
            lines.append(f"- {scenario} ({status})")
            lines.append(f"  started: {started}")
            if completed:
                lines.append(f"  completed: {completed}")
    else:
        lines.append("No scenario executions logged yet.")

    return "\n".join(lines)


def scenario_stop(scenario_name: str, home: Path | None = None) -> Tuple[int, str]:
    """Stop a running scenario by clearing its lock."""
    claude_dir = _resolve_claude_dir(home)
    _, _, lock_dir = _ensure_scenarios_dir(claude_dir)

    if not scenario_name:
        return 1, _color("Provide a scenario name to stop", RED)

    lock_file = lock_dir / f"{_scenario_lock_basename(scenario_name)}.lock"
    if not lock_file.is_file():
        return 0, _color(f"No active lock for scenario '{scenario_name}'", YELLOW)

    try:
        lock_file.unlink()
    except OSError as exc:
        return 1, _color(f"Failed to clear lock: {exc}", RED)

    return 0, _color(f"Cleared lock for scenario '{scenario_name}'", GREEN)


def scenario_run(
    scenario_name: str,
    *options: str,
    home: Path | None = None,
    input_fn: Optional[Callable[[str], str]] = None,
) -> Tuple[int, str]:
    """Run a scenario, supporting interactive, automatic, and plan modes."""
    claude_dir = _resolve_claude_dir(home)
    scenarios_dir, state_dir, lock_dir = _ensure_scenarios_dir(claude_dir)

    if not scenario_name:
        message = _color("Specify a scenario name", RED)
        return 1, f"{message}\n{scenario_list(home=home)}"

    run_mode = "interactive"
    warnings: List[str] = []
    for option in options:
        if not option:
            continue
        normalized = option.lower()
        if normalized in ("--auto", "--automatic", "automatic"):
            run_mode = "automatic"
        elif normalized in ("--interactive", "interactive"):
            run_mode = "interactive"
        elif normalized in ("--plan", "--preview", "--validate", "plan", "preview", "validate"):
            run_mode = "plan"
        else:
            warnings.append(_color(f"Ignoring unknown option '{option}'", YELLOW))

    scenario_filename = scenario_name if scenario_name.endswith(".yaml") else f"{scenario_name}.yaml"
    scenario_file = scenarios_dir / scenario_filename
    if not scenario_file.is_file():
        message = _color(f"Scenario file not found: {scenario_name}", RED)
        return 1, f"{message}\n{scenario_list(home=home)}"

    if yaml is None:
        return 1, _color("PyYAML is required to run scenarios.", RED)

    code, metadata, error_msg = _parse_scenario_metadata(scenario_file)
    if code != 0 or metadata is None:
        return 1, _color(f"Error: {error_msg}", RED)

    if run_mode == "plan":
        lines: List[str] = [
            *warnings,
            _color(f"Scenario preview: {metadata.name}", BLUE),
            f"Description: {metadata.description}",
            f"Priority: {metadata.priority}",
            f"Type: {metadata.scenario_type}",
            f"Phases: {len(metadata.phases)}",
        ]

        for idx, phase in enumerate(metadata.phases, 1):
            lines.append("")
            lines.append(f"- Phase {idx}: {phase.name}")
            if phase.description:
                lines.append(f"  {phase.description}")
            lines.append(f"  condition: {phase.condition}")
            lines.append(f"  parallel: {'true' if phase.parallel else 'false'}")
            if phase.profiles:
                lines.append(f"  profiles: {','.join(phase.profiles)}")
            if phase.agents:
                lines.append(f"  agents: {','.join(phase.agents)}")
            if phase.success:
                lines.append(f"  success checks: {','.join(phase.success)}")

        return 0, "\n".join(lines)

    input_cb = input_fn or input
    lock_name = _scenario_lock_basename(metadata.name)
    lock_file = lock_dir / f"{lock_name}.lock"
    if lock_file.exists():
        return 1, _color(
            f"Scenario '{metadata.name}' already running (lock present). Use 'claude-ctx orchestrate stop {metadata.name}' if the previous run is stuck.",
            RED,
        )

    exec_id = str(int(time.time()))
    lock_file.write_text(exec_id, encoding="utf-8")
    state_file = state_dir / f"{lock_name}-{exec_id}.json"
    _scenario_init_state(state_file, metadata)

    lines: List[str] = warnings.copy()
    lines.append(_color(f"=== Executing scenario: {metadata.name} ===", BLUE))
    lines.append(f"Description: {metadata.description}")
    lines.append(f"Priority: {metadata.priority}")
    lines.append(f"Type: {metadata.scenario_type}")
    lines.append(f"Run mode: {run_mode}")
    lines.append(f"Execution id: {exec_id}")
    lines.append("")

    exit_code = 0
    try:
        for idx, phase in enumerate(metadata.phases):
            lines.append(_color(f"Phase {idx + 1}: {phase.name}", YELLOW))
            if phase.description:
                lines.append(f"  {phase.description}")
            lines.append(f"  condition: {phase.condition}")
            lines.append(f"  parallel: {'true' if phase.parallel else 'false'}")
            if phase.profiles:
                lines.append(f"  profiles: {','.join(phase.profiles)}")
            if phase.agents:
                lines.append(f"  agents: {','.join(phase.agents)}")
            if phase.success:
                lines.append(f"  success checks: {','.join(phase.success)}")

            if run_mode == "interactive" and phase.condition != "manual":
                response = input_cb("Execute this phase now? [y/N] ")
                if not response or response.strip().lower()[0] != "y":
                    lines.append("  Skipping phase on user request")
                    _scenario_update_phase_state(
                        state_file,
                        index=idx,
                        phase_name=phase.name,
                        status="skipped",
                        note="user skipped",
                    )
                    lines.append("")
                    continue

            _scenario_update_phase_state(
                state_file,
                index=idx,
                phase_name=phase.name,
                status="running",
            )

            for profile in phase.profiles:
                lines.append(f"  -> Loading profile: {profile}")

            for agent in phase.agents:
                lines.append(f"  -> Activating agent: {agent}")
                try:
                    filename = _normalize_agent_filename(agent)
                except ValueError:
                    filename = f"{agent}.md"
                if _find_agent_file_any_state(claude_dir, filename) is None:
                    lines.append("    " + _color(f"Warning: could not activate '{agent}'", YELLOW))

            _generate_dependency_map(claude_dir)
            _scenario_update_phase_state(
                state_file,
                index=idx,
                phase_name=phase.name,
                status="completed",
            )
            lines.append("")

        _scenario_finalize_state(state_file, "completed")
        lines.append(_color(f"Scenario '{metadata.name}' completed", GREEN))
    except Exception as exc:  # pragma: no cover - defensive fallback
        _scenario_finalize_state(state_file, "failed")
        lines.append(_color(f"Scenario '{metadata.name}' failed: {exc}", RED))
        exit_code = 1
    finally:
        try:
            lock_file.unlink()
        except OSError:
            pass

    return exit_code, "\n".join(lines)


def scenario_preview(scenario_name: str, home: Path | None = None) -> Tuple[int, str]:
    """Preview a scenario without executing it."""
    return scenario_run(scenario_name, "plan", home=home)


def init_detect(
    target: str | None = None,
    *,
    home: Path | None = None,
    cwd: Path | None = None,
) -> Tuple[int, str]:
    """Detect project context and write init artifacts."""

    claude_dir = _resolve_claude_dir(home)
    _, projects_dir, cache_dir = _resolve_init_dirs(claude_dir)

    base_dir = Path(cwd or Path.cwd())

    if target:
        candidate = Path(target)
        if not candidate.is_absolute():
            candidate = base_dir / candidate
    else:
        candidate = base_dir

    if not candidate.is_dir():
        display_target = target if target else str(candidate)
        message = _color(
            f"init_detect: directory not found: {display_target}",
            RED,
        )
        return 1, message

    try:
        resolved_path = candidate.resolve(strict=True)
    except OSError:
        display_target = target if target else str(candidate)
        message = _color(
            f"init_detect: unable to resolve path: {display_target}",
            RED,
        )
        return 1, message

    slug = _init_slug_for_path(resolved_path)

    project_state_dir = projects_dir / slug
    cache_project_dir = cache_dir / slug
    project_state_dir.mkdir(parents=True, exist_ok=True)
    cache_project_dir.mkdir(parents=True, exist_ok=True)

    detection_json_cache = cache_project_dir / "detection.json"
    detection_json_state = project_state_dir / "detection.json"
    session_log_cache = cache_project_dir / "session-log.md"
    session_log_state = project_state_dir / "session-log.md"

    iso_now = datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

    detection_raw = _run_detect_project_type(resolved_path)
    detection_language = detection_framework = detection_infra = ""
    detection_types_raw = ""
    if detection_raw:
        parts = [part.strip() for part in detection_raw.split("|")]
        while len(parts) < 4:
            parts.append("")
        detection_language, detection_framework, detection_infra, detection_types_raw = parts[:4]

    types_list = [item for item in detection_types_raw.split() if item]

    analysis_raw = _run_analyze_project(resolved_path)
    analysis_plain = _strip_ansi_codes(analysis_raw).strip()

    payload: dict[str, object] = {
        "path": str(resolved_path),
        "slug": slug,
        "timestamp": iso_now,
        "language": detection_language or None,
        "framework": detection_framework or None,
        "infrastructure": detection_infra or None,
        "types": types_list,
    }

    if analysis_plain:
        payload["analysis_output"] = analysis_plain

    payload_text = json.dumps(payload, indent=2, ensure_ascii=False)

    detection_json_cache.write_text(payload_text + "\n", encoding="utf-8")
    detection_json_state.write_text(payload_text + "\n", encoding="utf-8")

    session_lines = [
        "# Init Detection Session",
        f"- Timestamp: {iso_now}",
        f"- Path: {resolved_path}",
        f"- Slug: {slug}",
        "",
        "## Detection Summary",
    ]

    if detection_language:
        session_lines.append(f"- Language: {detection_language}")
    if detection_framework:
        session_lines.append(f"- Framework: {detection_framework}")
    if detection_infra:
        session_lines.append(f"- Infrastructure: {detection_infra}")
    if detection_types_raw:
        session_lines.append(f"- Types: {detection_types_raw}")

    if analysis_plain:
        session_lines.append("")
        session_lines.append("## analyze_project Output")
        session_lines.extend(analysis_plain.splitlines())

    session_log_state.write_text("\n".join(session_lines) + "\n", encoding="utf-8")
    shutil.copyfile(session_log_state, session_log_cache)

    lines = [
        _color("init_detect complete", GREEN),
        f"  Project path: {_color(str(resolved_path), BLUE)}",
        f"  Project slug: {_color(slug, BLUE)}",
        f"  Detection JSON: {_color(str(detection_json_cache), BLUE)}",
        f"  Session log: {_color(str(session_log_state), BLUE)}",
    ]

    return 0, "\n".join(lines)


def init_minimal(home: Path | None = None) -> Tuple[int, str]:
    """Apply minimal defaults via the init system."""

    claude_dir = _resolve_claude_dir(home)
    _resolve_init_dirs(claude_dir)

    exit_code, message = _profile_reset(home=home)
    if exit_code != 0:
        return exit_code, message

    lines = []
    if message:
        lines.append(message)
    lines.append(_color("Initialized minimal claude-ctx configuration", GREEN))

    return 0, "\n".join(lines)


def init_profile(
    profile_name: str | None,
    *,
    home: Path | None = None,
) -> Tuple[int, str]:
    """Load a profile within the init workflow."""

    claude_dir = _resolve_claude_dir(home)
    _resolve_init_dirs(claude_dir)

    if not profile_name:
        message = _color("init_profile requires a profile name", RED)
        hint = "Use 'claude-ctx profile list' to view available presets."
        return 1, f"{message}\n{hint}"

    loaders = {
        "minimal": profile_minimal,
        "backend": profile_backend,
    }

    loader = loaders.get(profile_name)
    if loader is None:
        return 1, _color(f"Failed to load profile '{profile_name}'", RED)

    exit_code, profile_message = loader(home=home)
    if exit_code != 0:
        return exit_code, profile_message

    lines = []
    if profile_message:
        lines.append(profile_message)
    lines.append(
        _color(
            f"Initialized claude-ctx with profile '{profile_name}'",
            GREEN,
        )
    )
    return 0, "\n".join(lines)


def _load_detection_file(path: Path) -> Tuple[Optional[dict], Optional[str], Optional[str]]:
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None, "missing", None
    except OSError as exc:
        return None, f"error reading file: {exc}", None

    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        return None, f"invalid JSON: {exc}", text

    return data, None, text


def _resolve_init_target(
    command: str,
    target: str | None,
    *,
    cwd: Path | None = None,
) -> Tuple[Optional[str], Optional[Path], Optional[str]]:
    """Resolve an init command target into a slug and optional resolved path."""

    base_dir = Path(cwd or Path.cwd())
    resolved_path: Optional[Path] = None
    slug: Optional[str] = None

    if target:
        candidate = Path(target)
        if not candidate.is_absolute():
            candidate = base_dir / candidate
        if candidate.is_dir():
            try:
                resolved_path = candidate.resolve(strict=True)
            except OSError:
                message = _color(
                    f"{command}: unable to resolve path: {target}",
                    RED,
                )
                return None, None, message
            slug = _init_slug_for_path(resolved_path)
        else:
            slug = target.strip()
    else:
        try:
            resolved_path = base_dir.resolve(strict=True)
        except OSError:
            message = _color(
                f"{command}: unable to determine project path",
                RED,
            )
            return None, None, message
        slug = _init_slug_for_path(resolved_path)

    if not slug:
        message = _color(
            f"{command}: unable to determine project slug",
            RED,
        )
        return None, resolved_path, message

    if any(sep in slug for sep in ("/", "\\")) or slug in {".", ".."}:
        message = _color(
            f"{command}: invalid project slug '{slug}'",
            RED,
        )
        return None, resolved_path, message

    return slug, resolved_path, None


def _prompt_user(prompt: str, default: str = "") -> str:
    """Prompt the user for input with an optional default."""

    if default:
        display = f"{prompt} [{default}]: "
    else:
        display = f"{prompt}: "

    try:
        response = builtins.input(display)  # type: ignore[attr-defined]
    except (EOFError, KeyboardInterrupt):
        return default

    response = response.strip()
    return response if response else default


def _confirm(prompt: str, default: bool = True) -> bool:
    """Prompt the user to confirm an action."""

    default_display = "Y/n" if default else "y/N"
    response = _prompt_user(f"{prompt} [{default_display}]", "")

    if not response:
        return default

    return response.lower() in {"y", "yes"}


def _format_detection_summary(data: dict[str, object]) -> List[str]:
    lines: List[str] = []
    lines.append(f"  Language: {data.get('language') or 'unknown'}")
    lines.append(f"  Framework: {data.get('framework') or 'unknown'}")
    lines.append(f"  Infrastructure: {data.get('infrastructure') or 'unknown'}")

    types_val = data.get("types")
    if isinstance(types_val, list) and types_val:
        types_str = ", ".join(str(item) for item in types_val)
        lines.append(f"  Types: {types_str}")

    return lines


def _format_header(title: str) -> str:
    separator = "━" * 60
    return f"{_color(separator, BLUE)}\n{_color(title, BLUE)}\n{_color(separator, BLUE)}"


def _list_available_agents(claude_dir: Path) -> List[str]:
    agents: Set[str] = set()
    for directory in [
        claude_dir / "agents",
        claude_dir / "agents-disabled",
        claude_dir / "agents" / "disabled",
    ]:
        if directory.is_dir():
            for path in directory.glob("*.md"):
                agents.add(path.stem)
    return sorted(agents)


def _list_available_modes(claude_dir: Path) -> List[str]:
    modes: Set[str] = set()
    for directory in [
        claude_dir / "modes",
        claude_dir / "modes" / "inactive",
    ]:
        if directory.is_dir():
            for path in directory.glob("*.md"):
                if path.stem == "Task_Management":
                    continue
                modes.add(path.stem)
    return sorted(modes)


def _parse_selection(
    raw: str,
    available: Sequence[str],
    *,
    label: str,
) -> Tuple[bool, List[str], Optional[str]]:
    """Parse a comma-separated selection string against available values."""

    if not raw.strip():
        return True, [], None

    selections = [item.strip() for item in raw.split(",") if item.strip()]
    if not selections:
        return True, [], None

    lower_map = {item.lower(): item for item in available}

    resolved: List[str] = []
    for selection in selections:
        match = lower_map.get(selection.lower())
        if not match:
            return False, [], _color(
                f"Unknown {label}: {selection}",
                RED,
            )
        resolved.append(match)

    return True, resolved, None


def _append_session_log(project_dir: Path, lines: Sequence[str]) -> None:
    log_path = project_dir / "session-log.md"
    try:
        with log_path.open("a", encoding="utf-8") as handle:
            handle.write("\n".join(lines) + "\n")
    except OSError:
        pass


def init_status(
    target: str | None = None,
    *,
    json_output: bool = False,
    home: Path | None = None,
    cwd: Path | None = None,
) -> Tuple[int, str, str]:
    """Show stored init state for a project."""

    claude_dir = _resolve_claude_dir(home)
    _, projects_dir, cache_dir = _resolve_init_dirs(claude_dir)

    slug, resolved_path, resolve_error = _resolve_init_target(
        "init_status",
        target,
        cwd=cwd,
    )

    if slug is None:
        message = resolve_error or _color(
            "init_status: unable to determine project slug.",
            RED,
        )
        return 1, "", message

    project_file = projects_dir / slug / "detection.json"
    cache_file = cache_dir / slug / "detection.json"

    proj_data, proj_error, proj_text = _load_detection_file(project_file)
    cache_data, cache_error, cache_text = _load_detection_file(cache_file)

    if proj_data is not None and cache_data is not None:
        match_status = "identical" if proj_data == cache_data else "mismatch"
    else:
        match_status = "unverified"

    base_data = proj_data or cache_data or {}

    summary_path = base_data.get("path") if isinstance(base_data, dict) else None
    if not summary_path and resolved_path is not None:
        summary_path = str(resolved_path)
    summary_slug = base_data.get("slug") if isinstance(base_data, dict) else None
    summary_timestamp = base_data.get("timestamp") if isinstance(base_data, dict) else None
    summary_language = base_data.get("language") if isinstance(base_data, dict) else None
    summary_framework = base_data.get("framework") if isinstance(base_data, dict) else None
    summary_infra = base_data.get("infrastructure") if isinstance(base_data, dict) else None
    types_val = base_data.get("types") if isinstance(base_data, dict) else None
    summary_types_list = types_val if isinstance(types_val, list) else []
    summary_types = ", ".join(str(item) for item in summary_types_list) if summary_types_list else "none"
    analysis_present = (
        "yes"
        if isinstance(base_data, dict) and base_data.get("analysis_output")
        else "no"
    )

    def colorize(text: str, color: str) -> str:
        return _color(text, color)

    def status_label(error: Optional[str]) -> str:
        if error is None:
            return colorize("ok", GREEN)
        if error == "missing":
            return colorize("missing", YELLOW)
        return colorize(error, RED)

    if match_status == "identical":
        consistency_msg = colorize(
            "OK - cache and project artifacts match",
            GREEN,
        )
    elif match_status == "mismatch":
        consistency_msg = colorize(
            "MISMATCH - cache and project artifacts differ",
            RED,
        )
    else:
        reasons: List[str] = []
        if proj_error:
            reasons.append(f"project {proj_error}")
        if cache_error:
            reasons.append(f"cache {cache_error}")
        if not reasons:
            reasons.append("insufficient data")
        consistency_msg = colorize(
            "Unable to verify - " + "; ".join(reasons),
            YELLOW,
        )

    summary_lines = [
        _color("Init Status", BLUE),
        f"  Project slug: {summary_slug or slug}",
        f"  Project path: {summary_path or '(unknown)'}",
        f"  Project file: {project_file}",
        f"    Status: {status_label(proj_error)}",
        f"  Cache file: {cache_file}",
        f"    Status: {status_label(cache_error)}",
        f"  Cache consistency: {consistency_msg}",
        "",
        "  Detected attributes:",
        f"    Timestamp: {summary_timestamp or 'unknown'}",
        f"    Language: {summary_language or 'unknown'}",
        f"    Framework: {summary_framework or 'unknown'}",
        f"    Infrastructure: {summary_infra or 'unknown'}",
        f"    Types: {summary_types}",
    ]

    if analysis_present == "yes":
        summary_lines.append(
            "    analyze_project output stored in detection.json"
        )

    exit_code = 0
    if proj_error is not None or cache_error is not None or match_status == "mismatch":
        exit_code = 1

    summary_text = "\n".join(summary_lines)

    warnings: List[str] = []
    if proj_error:
        warnings.append(
            colorize(f"Project detection.json {proj_error}", RED)
        )
    if cache_error:
        warnings.append(
            colorize(f"Cache detection.json {cache_error}", RED)
        )
    if match_status == "mismatch":
        warnings.append(
            colorize("Cache and project detection artifacts differ", RED)
        )
    elif match_status == "unverified" and not (proj_error or cache_error):
        warnings.append(
            colorize("Unable to verify cache consistency", YELLOW)
        )

    warnings_text = "\n".join(warnings)

    if not json_output:
        return exit_code, summary_text, ""

    output_text: Optional[str]
    if proj_data is not None and proj_text is not None:
        output_text = proj_text
    elif cache_data is not None and cache_text is not None:
        output_text = cache_text
    else:
        error_text = colorize(
            f"No detection artifacts found for slug '{slug}'.",
            RED,
        )
        warnings_text = "\n".join([
            warning for warning in [warnings_text, error_text] if warning
        ])
        return 1, "", warnings_text

    return exit_code, output_text, warnings_text


def init_reset(
    target: str | None = None,
    *,
    home: Path | None = None,
    cwd: Path | None = None,
) -> Tuple[int, str]:
    """Remove cached/project detection artifacts for a given slug/path.

    Args:
        target: Optional project path or slug. Defaults to current working directory.
        home: Optional home directory override.
        cwd: Optional current working directory override.

    Returns:
        Tuple of (exit_code, message).
    """
    claude_dir = _resolve_claude_dir(home)
    _, projects_dir, cache_dir = _resolve_init_dirs(claude_dir)

    slug, resolved_path, resolve_error = _resolve_init_target(
        "init_reset",
        target,
        cwd=cwd,
    )

    if slug is None:
        message = resolve_error or _color(
            "init_reset: unable to determine project slug",
            RED,
        )
        return 1, message

    project_dir = projects_dir / slug
    cache_project_dir = cache_dir / slug

    project_removed = False
    cache_removed = False
    errors: List[str] = []

    if project_dir.exists():
        try:
            if project_dir.is_dir():
                shutil.rmtree(project_dir)
            else:
                project_dir.unlink()
            project_removed = True
        except OSError as exc:
            errors.append(f"project artifacts: {exc}")

    if cache_project_dir.exists():
        try:
            if cache_project_dir.is_dir():
                shutil.rmtree(cache_project_dir)
            else:
                cache_project_dir.unlink()
            cache_removed = True
        except OSError as exc:
            errors.append(f"cache artifacts: {exc}")

    if errors:
        details = "; ".join(errors)
        return 1, _color(
            f"init_reset: failed to remove artifacts ({details})",
            RED,
        )

    lines = [
        _color("Init Reset", BLUE),
        f"  Project slug: {_color(slug, BLUE)}",
    ]

    if resolved_path is not None:
        lines.append(f"  Project path: {_color(str(resolved_path), BLUE)}")

    if project_removed:
        lines.append(
            _color(f"  Removed project state: {project_dir}", GREEN)
        )
    if cache_removed:
        lines.append(
            _color(f"  Removed cache state: {cache_project_dir}", GREEN)
        )

    if not (project_removed or cache_removed):
        lines.append(
            _color(
                "  No init detection artifacts found for this project",
                YELLOW,
            )
        )

    lines.append(
        f"{_color('TODO:', YELLOW)} Additional reset behaviors coming soon."
    )

    return 0, "\n".join(lines)


def init_resume(
    target: str | None = None,
    *,
    home: Path | None = None,
    cwd: Path | None = None,
) -> Tuple[int, str]:
    """Emit message summarizing last detection info or warn if none.

    Args:
        target: Optional project path or slug. Defaults to current working directory.
        home: Optional home directory override.
        cwd: Optional current working directory override.

    Returns:
        Tuple of (exit_code, message).
    """
    claude_dir = _resolve_claude_dir(home)
    _, projects_dir, cache_dir = _resolve_init_dirs(claude_dir)

    slug, resolved_path, resolve_error = _resolve_init_target(
        "init_resume",
        target,
        cwd=cwd,
    )

    if slug is None:
        message = resolve_error or _color(
            "init_resume: unable to determine project slug",
            RED,
        )
        return 1, message

    project_file = projects_dir / slug / "detection.json"
    cache_file = cache_dir / slug / "detection.json"

    proj_data, proj_error, _ = _load_detection_file(project_file)
    cache_data, cache_error, _ = _load_detection_file(cache_file)

    detection_data = proj_data or cache_data
    detection_source = (
        "project" if proj_data is not None else "cache" if cache_data is not None else None
    )

    warnings: List[str] = []
    if proj_error and proj_error != "missing":
        warnings.append(f"project detection.json {proj_error}")
    if cache_error and cache_error != "missing":
        warnings.append(f"cache detection.json {cache_error}")

    if detection_data is None:
        warning_lines = []
        if warnings:
            warning_lines.extend(warnings)
        warning_lines.append(
            f"no previous init detection found for slug '{slug}'"
        )
        message = _color(
            "init_resume: " + "; ".join(warning_lines),
            YELLOW,
        )
        return 1, message

    timestamp = (
        detection_data.get("timestamp")
        if isinstance(detection_data, dict)
        else None
    )
    detected_path = (
        detection_data.get("path")
        if isinstance(detection_data, dict)
        else None
    )
    language = (
        detection_data.get("language")
        if isinstance(detection_data, dict)
        else None
    )
    framework = (
        detection_data.get("framework")
        if isinstance(detection_data, dict)
        else None
    )
    infrastructure = (
        detection_data.get("infrastructure")
        if isinstance(detection_data, dict)
        else None
    )
    types_val = (
        detection_data.get("types")
        if isinstance(detection_data, dict)
        else None
    )
    types_label = (
        ", ".join(str(item) for item in types_val)
        if isinstance(types_val, list) and types_val
        else "none"
    )

    summary_path = detected_path or (str(resolved_path) if resolved_path else "(unknown)")

    lines = [
        _color("Init Resume", BLUE),
        f"  Project slug: {_color(slug, BLUE)}",
        f"  Project path: {_color(summary_path, BLUE)}",
        f"  Detection source: {detection_source or 'unknown'}",
        f"  Timestamp: {timestamp or 'unknown'}",
        f"  Language: {language or 'unknown'}",
        f"  Framework: {framework or 'unknown'}",
        f"  Infrastructure: {infrastructure or 'unknown'}",
        f"  Types: {types_label}",
    ]

    for warning in warnings:
        lines.append(_color(f"  Warning: {warning}", YELLOW))

    lines.append(
        f"{_color('TODO:', YELLOW)} Resume interactive configuration steps coming soon."
    )

    return 0, "\n".join(lines)


def init_wizard(
    target: str | None = None,
    *,
    home: Path | None = None,
    cwd: Path | None = None,
) -> Tuple[int, str]:
    """Interactive wizard guiding project initialization."""

    claude_dir = _resolve_claude_dir(home)
    _, projects_dir, cache_dir = _resolve_init_dirs(claude_dir)

    base_dir = Path(cwd or Path.cwd())

    if target:
        candidate = Path(target)
        if not candidate.is_absolute():
            candidate = base_dir / candidate
    else:
        candidate = base_dir

    if not candidate.is_dir():
        display_target = target if target else str(candidate)
        message = _color(
            f"init_wizard: directory not found: {display_target}",
            RED,
        )
        return 1, message

    try:
        resolved_path = candidate.resolve(strict=True)
    except OSError:
        display_target = target if target else str(candidate)
        message = _color(
            f"init_wizard: unable to resolve path: {display_target}",
            RED,
        )
        return 1, message

    slug = _init_slug_for_path(resolved_path)

    project_file = projects_dir / slug / "detection.json"
    cache_file = cache_dir / slug / "detection.json"

    wizard_lines: List[str] = []
    wizard_lines.append(_format_header("Init Wizard"))
    wizard_lines.append(f"Project path: {_color(str(resolved_path), BLUE)}")
    wizard_lines.append(f"Project slug: {_color(slug, BLUE)}")
    wizard_lines.append("")

    # Ensure detection artifacts exist
    detect_message = ""
    ran_detection = False

    if not project_file.is_file() and not cache_file.is_file():
        detect_code, detect_output = init_detect(
            None,
            home=home,
            cwd=resolved_path,
        )
        if detect_code != 0:
            message = detect_output or _color(
                f"init_wizard: failed to detect project '{slug}'",
                RED,
            )
            return detect_code, message
        detect_message = detect_output
        ran_detection = True

    proj_data, proj_error, _ = _load_detection_file(project_file)
    cache_data, cache_error, _ = _load_detection_file(cache_file)

    detection_data = proj_data or cache_data

    if detection_data is None:
        message = _color(
            f"init_wizard: unable to locate detection artifacts for slug '{slug}'",
            RED,
        )
        return 1, message

    wizard_lines.append(_color("Detection summary", BLUE))
    wizard_lines.extend(_format_detection_summary(detection_data))
    wizard_lines.append("")

    if proj_error and proj_error != "missing":
        wizard_lines.append(
            _color(f"Warning: project detection.json {proj_error}", YELLOW)
        )
    if cache_error and cache_error != "missing":
        wizard_lines.append(
            _color(f"Warning: cache detection.json {cache_error}", YELLOW)
        )
    if proj_error or cache_error:
        wizard_lines.append("")

    if not ran_detection:
        if _confirm("Re-run project detection now?", default=False):
            detect_code, detect_output = init_detect(
                None,
                home=home,
                cwd=resolved_path,
            )
            if detect_code != 0:
                message = detect_output or _color(
                    f"init_wizard: failed to re-run detection for '{slug}'",
                    RED,
                )
                return detect_code, message
            detect_message = detect_output
            proj_data, proj_error, _ = _load_detection_file(project_file)
            cache_data, cache_error, _ = _load_detection_file(cache_file)
            detection_data = proj_data or cache_data
            wizard_lines.append(_color("Detection refreshed", GREEN))
            wizard_lines.append("")

    detection_data = detection_data or {}

    # Profile selection
    profile_options = [
        ("1", "minimal", "Essential agents only"),
        ("2", "backend", "Backend development toolkit"),
        ("3", "custom", "Manual agent and mode selection"),
        ("4", "skip", "Skip profile configuration"),
    ]

    for code, name, description in profile_options:
        builtins.print(
            f"  {code}. {name.ljust(8)} - {description}",
        )
    profile_choice = ""
    while True:
        profile_choice = _prompt_user("Select profile", "1")
        profile_choice = profile_choice.strip() or "1"
        mapping = {code: name for code, name, _ in profile_options}
        if profile_choice in mapping:
            profile_choice = mapping[profile_choice]
        if profile_choice in {"minimal", "backend", "custom", "skip"}:
            break
        builtins.print(_color(f"Invalid profile selection: {profile_choice}", RED))

    wizard_lines.append(f"Selected profile: {profile_choice}")

    additional_agents: List[str] = []
    additional_modes: List[str] = []

    available_agents = _list_available_agents(claude_dir)
    available_modes = _list_available_modes(claude_dir)

    if profile_choice != "skip":
        if available_agents:
            builtins.print("Available agents:")
            builtins.print("  " + ", ".join(sorted(available_agents)))
        while True:
            agent_input = _prompt_user(
                "Additional agents (comma separated, Enter to skip)",
                "",
            )
            valid, parsed, error = _parse_selection(
                agent_input,
                available_agents,
                label="agent",
            )
            if valid:
                additional_agents = parsed
                break
            if error:
                builtins.print(error)

        if available_modes:
            builtins.print("Available modes:")
            builtins.print("  " + ", ".join(sorted(available_modes)))
        while True:
            mode_input = _prompt_user(
                "Additional modes (comma separated, Enter to skip)",
                "",
            )
            valid, parsed, error = _parse_selection(
                mode_input,
                available_modes,
                label="mode",
            )
            if valid:
                additional_modes = parsed
                break
            if error:
                builtins.print(error)

    wizard_lines.append(
        f"Additional agents: {', '.join(additional_agents) if additional_agents else 'none'}"
    )
    wizard_lines.append(
        f"Additional modes: {', '.join(additional_modes) if additional_modes else 'none'}"
    )

    if detect_message:
        wizard_lines.append("")
        wizard_lines.append(detect_message)

    wizard_lines.append("")
    wizard_lines.append(_color("Summary", BLUE))
    wizard_lines.extend(_format_detection_summary(detection_data))
    wizard_lines.append(
        f"  Profile: {profile_choice}"
    )
    wizard_lines.append(
        f"  Agents to activate: {', '.join(additional_agents) if additional_agents else 'none'}"
    )
    wizard_lines.append(
        f"  Modes to activate: {', '.join(additional_modes) if additional_modes else 'none'}"
    )

    wizard_lines.append("")

    if not _confirm("Apply this configuration?", default=True):
        wizard_lines.append(_color("Wizard cancelled. No changes applied.", YELLOW))
        return 1, "\n".join(wizard_lines)

    applied_lines: List[str] = []

    if profile_choice == "minimal":
        exit_code, message = profile_minimal(home=home)
        if exit_code != 0:
            return exit_code, message
        applied_lines.append(message)
    elif profile_choice == "backend":
        exit_code, message = profile_backend(home=home)
        if exit_code != 0:
            return exit_code, message
        applied_lines.append(message)

    if additional_agents:
        for agent in additional_agents:
            exit_code, message = agent_activate(agent, home=home)
            applied_lines.append(message)
            if exit_code != 0:
                return exit_code, "\n".join(wizard_lines + applied_lines)

    if additional_modes:
        for mode in additional_modes:
            exit_code, message = mode_activate(mode, home=home)
            applied_lines.append(message)
            if exit_code != 0:
                return exit_code, "\n".join(wizard_lines + applied_lines)

    session_lines = [
        "# Init Wizard Session",
        f"- Timestamp: {datetime.datetime.utcnow().isoformat()}Z",
        f"- Path: {resolved_path}",
        f"- Slug: {slug}",
        f"- Profile: {profile_choice}",
        f"- Additional agents: {', '.join(additional_agents) if additional_agents else 'none'}",
        f"- Additional modes: {', '.join(additional_modes) if additional_modes else 'none'}",
    ]

    project_state_dir = projects_dir / slug
    project_state_dir.mkdir(parents=True, exist_ok=True)
    _append_session_log(project_state_dir, session_lines)

    wizard_lines.append("")
    wizard_lines.append(_color("Configuration applied successfully", GREEN))
    wizard_lines.extend(applied_lines)

    return 0, "\n".join(wizard_lines)


__all__ = [
    "list_modes",
    "mode_status",
    "list_agents",
    "agent_status",
    "agent_deps",
    "agent_validate",
    "build_agent_graph",
    "render_agent_graph",
    "export_agent_graph",
    "agent_graph",
    "list_rules",
    "rules_status",
    "show_status",
    "rules_activate",
    "rules_deactivate",
    "profile_list",
    "profile_save",
    "profile_minimal",
    "profile_backend",
    "workflow_run",
    "workflow_list",
    "workflow_status",
    "workflow_resume",
    "scenario_list",
    "scenario_validate",
    "scenario_status",
    "scenario_stop",
    "scenario_run",
    "scenario_preview",
    "init_detect",
    "init_minimal",
    "init_profile",
    "init_status",
    "init_reset",
    "init_resume",
    "init_wizard",
]
