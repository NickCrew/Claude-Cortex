"""Base utility functions for cortex."""

from __future__ import annotations


import builtins
import datetime
from datetime import timezone
import hashlib
import json
import os
import re
import shutil
import subprocess
import sysconfig
import time
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Set, Tuple


BLUE = "\033[0;34m"
GREEN = "\033[0;32m"
YELLOW = "\033[0;33m"
RED = "\033[0;31m"
NC = "\033[0m"


def _color(text: str, color: str) -> str:
    return f"{color}{text}{NC}"


try:  # pragma: no cover - dependency availability exercised in tests
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore[assignment]


_CORTEX_SCOPE_ENV = "CORTEX_SCOPE"
_CORTEX_ROOT_ENV = "CORTEX_ROOT"
_CORTEX_ASSETS_ENV = "CORTEX_ASSETS_ROOT"


def _find_project_claude_dir(start: Path) -> Path | None:
    """Find the nearest .claude directory by walking up from start."""
    current = start.resolve()
    while True:
        candidate = current / ".claude"
        if candidate.is_dir():
            return candidate
        if current == current.parent:
            break
        current = current.parent
    return None


def _resolve_cortex_root(home: Path | None = None) -> Path:
    """Resolve the global Cortex root directory.

    Preference order:

    1. Explicit ``CORTEX_ROOT`` environment variable
    2. Caller-provided ``home`` argument
    3. ``$HOME/.cortex`` fallback
    """
    env_root = os.environ.get(_CORTEX_ROOT_ENV)
    if env_root:
        return Path(env_root).expanduser().resolve()

    base = Path(home) if home is not None else Path(os.environ.get("HOME", str(Path.home())))
    return base / ".cortex"


def _resolve_bundled_assets_root() -> Path | None:
    """Resolve the bundled assets root shipped with the Python package."""
    env_root = os.environ.get(_CORTEX_ASSETS_ENV)
    if env_root:
        path = Path(env_root).expanduser().resolve()
        if path.exists():
            return path

    module_root = Path(__file__).resolve().parents[1]
    candidate = module_root / "assets"
    if candidate.is_dir():
        return candidate

    data_root = Path(sysconfig.get_path("data")) / "share" / "claude-cortex" / "assets"
    if data_root.is_dir():
        return data_root

    return None


def _resolve_plugin_assets_root() -> Path:
    """Resolve the root directory containing bundled plugin assets."""
    env_root = os.environ.get("CLAUDE_PLUGIN_ROOT") or os.environ.get("CORTEX_PLUGIN_ROOT")
    if env_root:
        path = Path(env_root).expanduser().resolve()
        if path.exists():
            return path

    this_file = Path(__file__).resolve()
    repo_root = this_file.parent.parent.parent
    if (repo_root / "agents").is_dir() and (repo_root / "commands").is_dir():
        return repo_root

    bundled = _resolve_bundled_assets_root()
    if bundled is not None:
        return bundled

    return repo_root


def _resolve_claude_dir(
    home: Path | None = None,
    scope: str | None = None,
    cwd: Path | None = None,
) -> Path:
    """Resolve the working Cortex directory.

    Preference order:

    1. Explicit scope selection via ``CORTEX_SCOPE`` / ``scope`` argument
    2. Plugin runtime via ``CLAUDE_PLUGIN_ROOT`` (set by Claude Code when
       commands execute inside a plugin sandbox)
    3. Caller-provided ``home`` argument
    4. ``$CORTEX_ROOT`` / ``$HOME/.cortex`` fallback
    """

    scope_value = (scope or os.environ.get(_CORTEX_SCOPE_ENV) or "").strip().lower()
    if scope_value:
        if scope_value in ("project", "local"):
            base = cwd or Path.cwd()
            found = _find_project_claude_dir(base)
            return found if found is not None else base / ".claude"
        if scope_value in ("global", "home"):
            return _resolve_cortex_root(home)
        if scope_value in ("plugin", "plugin_root"):
            override = os.environ.get("CLAUDE_PLUGIN_ROOT")
            if override:
                path = Path(override).expanduser().resolve()
                if path.exists():
                    return path
            return _resolve_cortex_root(home)
        # Treat unknown scope as auto.

    if os.environ.get(_CORTEX_ROOT_ENV):
        return _resolve_cortex_root(home)

    override = os.environ.get("CLAUDE_PLUGIN_ROOT")
    if override:
        path = Path(override).expanduser().resolve()
        if path.exists():
            return path

    return _resolve_cortex_root(home)


def _resolve_init_dirs(claude_dir: Path) -> Tuple[Path, Path, Path]:
    """Ensure init directories exist and return (state, projects, cache)."""

    state_dir = claude_dir / ".init"
    projects_dir = state_dir / "projects"
    cache_dir = state_dir / "cache"

    for path in (state_dir, projects_dir, cache_dir):
        path.mkdir(parents=True, exist_ok=True)

    return state_dir, projects_dir, cache_dir


def _ensure_claude_structure(claude_dir: Path) -> List[str]:
    """Ensure all required directories and files exist for cortex.

    Creates the standard directory structure and activation tracking files.
    Returns a list of created paths for logging.
    """
    created: List[str] = []

    # Ensure main claude directory exists
    claude_dir.mkdir(parents=True, exist_ok=True)

    # Standard directories
    dirs = [
        "rules",
        "modes",
        "mcp/docs",
        "inactive/rules",
        "agents",
        "skills",
        "commands",
        "workflows",
        "flags",
        "principles",
    ]

    for dir_name in dirs:
        dir_path = claude_dir / dir_name
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            created.append(str(dir_path))

    # Activation tracking files
    active_files = [".active-modes", ".active-mcp", ".active-rules", ".active-principles"]
    for active_file in active_files:
        file_path = claude_dir / active_file
        if not file_path.exists():
            file_path.touch()
            created.append(str(file_path))

    return created


def _get_builtin_templates_dir() -> Path:
    """Get the bundled templates directory shipped with the plugin."""
    return _resolve_plugin_assets_root() / "templates"


def _list_template_files(template_dir: Path) -> List[Path]:
    """Return all template files under the given directory."""
    if not template_dir.is_dir():
        return []
    return sorted(path for path in template_dir.rglob("*") if path.is_file())


def _find_missing_template_files(target_root: Path) -> List[Path]:
    """Find template files missing from the target root's templates/ directory."""
    source_dir = _get_builtin_templates_dir()
    if not source_dir.is_dir():
        return []

    target_dir = target_root / "templates"
    missing: List[Path] = []
    for src in _list_template_files(source_dir):
        rel_path = src.relative_to(source_dir)
        if not (target_dir / rel_path).exists():
            missing.append(rel_path)
    return missing


def _ensure_template_files(target_root: Path) -> List[str]:
    """Copy any missing template files into target_root/templates."""
    source_dir = _get_builtin_templates_dir()
    if not source_dir.is_dir():
        return []

    created: List[str] = []
    target_dir = target_root / "templates"
    for src in _list_template_files(source_dir):
        rel_path = src.relative_to(source_dir)
        dest = target_dir / rel_path
        if dest.exists():
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        created.append(str(dest))
    return created


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
_CLAUDE_MD_PATTERNS: Dict[str, Tuple[re.Pattern[str], ...]] = {
    "rules": (
        re.compile(r"^@rules/([A-Za-z0-9_\-/]+)\.md\b", re.IGNORECASE),
    ),
    "modes": (
        re.compile(r"^@modes/([A-Za-z0-9_\-/]+)\.md\b", re.IGNORECASE),
        re.compile(r"^@inactive/modes/([A-Za-z0-9_\-/]+)\.md\b", re.IGNORECASE),
    ),
}
_INACTIVE_ALIAS_MAP: Dict[str, Tuple[str, ...]] = {
    "agents": ("agents-disabled", "agents/disabled"),
    "modes": ("modes-inactive", "modes/inactive"),
    "rules": ("rules-inactive", "rules-disabled", "rules/disabled"),
}


def _normalize_context_slug(category: str, slug: str) -> str:
    """Normalize CLAUDE.md slugs for comparisons."""
    category = category.lower()
    slug = slug.strip().lstrip("./")

    # Strip explicit category prefixes (e.g., modes/foo -> foo)
    prefix = f"{category}/"
    if slug.startswith(prefix):
        slug = slug[len(prefix) :]

    # Strip inactive/<category>/ prefixes
    inactive_prefix = f"inactive/{category}/"
    if slug.startswith(inactive_prefix):
        slug = slug[len(inactive_prefix) :]
    elif slug.startswith("inactive/"):
        slug = slug[len("inactive/") :]

    return slug


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


def _write_active_entries(path: Path, entries: Iterable[str]) -> None:
    """Write normalized entries to an ``.active-*`` file."""

    normalized: List[str] = []
    for value in entries:
        text = str(value).strip()
        if text:
            normalized.append(text)

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(sorted(set(normalized))) + "\n", encoding="utf-8")


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
            remainder = line[len(prefix) :]
            if remainder.startswith(marker):
                remainder = remainder[len(marker) :]
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
            remainder = line[len(prefix) :]
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


def _parse_claude_md_refs(claude_dir: Path, category: str) -> Set[str]:
    """Extract active context references from CLAUDE.md for a given category.

    Args:
        claude_dir: Path to the CLAUDE home directory
        category: Supported category name ("rules" or "modes")

    Returns:
        Set of normalized slug strings (lowercase, POSIX separators, no ".md")
    """
    claude_md = claude_dir / "CLAUDE.md"
    if not claude_md.is_file():
        return set()

    category_key = category.lower()
    patterns = _CLAUDE_MD_PATTERNS.get(category_key)
    if patterns is None:
        return set()

    refs: Set[str] = set()
    try:
        for raw_line in claude_md.read_text(encoding="utf-8").splitlines():
            stripped = raw_line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            for pattern in patterns:
                matcher = pattern.match(stripped)
                if not matcher:
                    continue
                slug = matcher.group(1).strip().replace("\\", "/").lower()
                slug = _normalize_context_slug(category_key, slug)
                if slug:
                    refs.add(slug)
                break
    except OSError:
        return set()

    return refs


def _inactive_root(claude_dir: Path) -> Path:
    return claude_dir / "inactive"


def _expand_relative_path(base: Path, specification: str) -> Path:
    path = base
    for part in specification.split("/"):
        if part:
            path = path / part
    return path


def _inactive_category_dir(claude_dir: Path, category: str) -> Path:
    path = _inactive_root(claude_dir) / category
    return path


def _ensure_inactive_category_dir(claude_dir: Path, category: str) -> Path:
    path = _inactive_category_dir(claude_dir, category)
    path.mkdir(parents=True, exist_ok=True)
    return path


def _inactive_dir_candidates(claude_dir: Path, category: str) -> List[Path]:
    canonical = _inactive_category_dir(claude_dir, category)
    candidates = [canonical]
    for alias in _INACTIVE_ALIAS_MAP.get(category, ()):  # legacy locations
        candidates.append(_expand_relative_path(claude_dir, alias))
    return candidates


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

        if char == ",":
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
            remainder = stripped[len(prefix) :].strip()
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

    active_rules: List[str] = []
    if rules_dir.is_dir():
        active_rules = sorted(p.stem for p in rules_dir.glob("*.md"))

    # Modes use reference-based activation - only .active-modes determines what's active
    active_modes = set(_parse_active_entries(claude_dir / ".active-modes"))

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
            ]
        )
    )

    rule_lines: List[str] = ["# Rules"]
    for rule in active_rules:
        rule_lines.append(f"@rules/{rule}.md")
    rule_lines.append("")
    sections.append(_render_section(rule_lines))

    mode_lines: List[str] = ["# Behavioral Modes"]
    for mode in sorted(active_modes):
        mode_lines.append(f"@modes/{mode}.md")
    mode_lines.append("")
    sections.append(_render_section(mode_lines))

    # MCP docs use reference-based activation - only .active-mcp determines what's active
    active_mcp = set(_parse_active_entries(claude_dir / ".active-mcp"))
    mcp_lines: List[str] = ["# MCP Documentation"]
    for doc in sorted(active_mcp):
        mcp_lines.append(f"@mcp/docs/{doc}.md")
    mcp_lines.append("")
    sections.append(_render_section(mcp_lines))

    # Prompts use reference-based activation - only .active-prompts determines what's active
    active_prompts = set(_parse_active_entries(claude_dir / ".active-prompts"))
    if active_prompts:
        prompt_lines: List[str] = ["# Prompt Library"]
        for prompt_slug in sorted(active_prompts):
            prompt_lines.append(f"@prompts/{prompt_slug}.md")
        prompt_lines.append("")
        sections.append(_render_section(prompt_lines))

    claude_md.write_text("".join(sections), encoding="utf-8")


def _load_yaml(path: Path) -> Tuple[bool, Any, str]:
    if yaml is None:
        return False, None, "PyYAML is not installed."  # type: ignore[unreachable]
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


def _ensure_list(value: Any, label: str, messages: List[str]) -> List[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    messages.append(f"'{label}' must be a list")
    return []


def _now_iso() -> str:
    return datetime.datetime.now(timezone.utc).replace(microsecond=0).isoformat() + "Z"


def _load_detection_file(
    path: Path,
) -> Tuple[Optional[Dict[str, Any]], Optional[str], Optional[str]]:
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

    if not isinstance(data, dict):
        return None, "invalid JSON structure", text

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
        response = builtins.input(display)
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
    return (
        f"{_color(separator, BLUE)}\n{_color(title, BLUE)}\n{_color(separator, BLUE)}"
    )


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
            return (
                False,
                [],
                _color(
                    f"Unknown {label}: {selection}",
                    RED,
                ),
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


def _list_available_agents(claude_dir: Path) -> List[str]:
    agents: Set[str] = set()
    for directory in [claude_dir / "agents", *_inactive_dir_candidates(claude_dir, "agents")]:
        if directory.is_dir():
            for path in directory.glob("*.md"):
                agents.add(path.stem)
    return sorted(agents)


def _list_available_modes(claude_dir: Path) -> List[str]:
    modes: Set[str] = set()
    for directory in [claude_dir / "modes", *_inactive_dir_candidates(claude_dir, "modes")]:
        if directory.is_dir():
            for path in directory.glob("*.md"):
                if path.stem == "Task_Management":
                    continue
                modes.add(path.stem)
    return sorted(modes)
