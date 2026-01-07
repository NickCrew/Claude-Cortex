"""Launcher utilities for starting Claude Code with Cortex context."""

from __future__ import annotations

import json
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple


from .core.base import _resolve_bundled_assets_root, _resolve_cortex_root


DEFAULT_CONFIG_PATH = _resolve_cortex_root() / "cortex-config.json"
DEFAULT_RULES_SUBDIR = Path.home() / ".claude" / "rules" / "cortex"
DEFAULT_PLUGIN_ID_CANDIDATES = ("cortex", "cortex", "cortex-plugin")


@dataclass
class LauncherConfig:
    """Resolved configuration for launching Claude."""

    plugin_root: Path
    settings_path: Optional[Path]
    rules: List[str]
    flags: List[str]
    modes: List[str]
    principles: List[str]


def _read_json(path: Path) -> Tuple[Dict[str, object], List[str]]:
    warnings: List[str] = []
    if not path.exists():
        return {}, warnings
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        warnings.append(f"Invalid JSON in {path}: {exc}")
        return {}, warnings
    if not isinstance(data, dict):
        warnings.append(f"Config {path} must be a JSON object.")
        return {}, warnings
    return data, warnings


def _write_json(path: Path, data: Dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _repo_root_from_module() -> Optional[Path]:
    here = Path(__file__).resolve()
    for parent in [here.parent, *here.parents]:
        if (parent / ".claude-plugin" / "plugin.json").is_file():
            return parent
        if (parent / "commands").is_dir() and (parent / "agents").is_dir() and (parent / "skills").is_dir():
            return parent
    return None


def _load_installed_plugins(path: Path) -> Dict[str, object]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(data, dict):
        return {}
    return data


def _select_plugin_entry(entries: Iterable[Dict[str, object]]) -> Optional[Dict[str, object]]:
    candidates = [entry for entry in entries if isinstance(entry, dict)]
    if not candidates:
        return None

    def score(entry: Dict[str, object]) -> str:
        return str(entry.get("lastUpdated") or entry.get("installedAt") or "")

    return max(candidates, key=score)


def _resolve_plugin_root_from_registry(plugin_id: Optional[str]) -> Optional[Path]:
    registry_path = Path.home() / ".claude" / "plugins" / "installed_plugins.json"
    if not registry_path.exists():
        return None
    data = _load_installed_plugins(registry_path)
    plugins = data.get("plugins")
    if not isinstance(plugins, dict):
        return None

    ids_to_try: List[str] = []
    if plugin_id:
        ids_to_try.append(plugin_id)
    else:
        for candidate in plugins.keys():
            if any(token in candidate.lower() for token in DEFAULT_PLUGIN_ID_CANDIDATES):
                ids_to_try.append(candidate)
        for candidate in DEFAULT_PLUGIN_ID_CANDIDATES:
            if candidate in plugins:
                ids_to_try.append(candidate)

    for plugin_key in ids_to_try:
        entries = plugins.get(plugin_key)
        if not isinstance(entries, list):
            continue
        selected = _select_plugin_entry(entries)
        if not selected:
            continue
        install_path = selected.get("installPath")
        if isinstance(install_path, str):
            path = Path(install_path).expanduser()
            if path.exists():
                return path
    return None


def _resolve_plugin_root(
    explicit: Optional[Path],
    config: Dict[str, object],
) -> Optional[Path]:
    if explicit:
        return explicit.expanduser()

    env_root = os.environ.get("CLAUDE_PLUGIN_ROOT") or os.environ.get("CORTEX_PLUGIN_ROOT")
    if env_root:
        path = Path(env_root).expanduser()
        if path.exists():
            return path

    plugin_dir = config.get("plugin_dir")
    if isinstance(plugin_dir, str):
        path = Path(plugin_dir).expanduser()
        if path.exists():
            return path

    repo_root = _repo_root_from_module()
    if repo_root is not None:
        return repo_root

    bundled_root = _resolve_bundled_assets_root()
    if bundled_root is not None and bundled_root.exists():
        return bundled_root

    plugin_id = config.get("plugin_id")
    plugin_id_str = plugin_id if isinstance(plugin_id, str) else None
    return _resolve_plugin_root_from_registry(plugin_id_str)


def _list_dir_stems(directory: Path) -> List[str]:
    if not directory.is_dir():
        return []
    return sorted(p.stem for p in directory.glob("*.md") if p.is_file())


def _resolve_principles_dir(content_root: Path, plugin_root: Optional[Path] = None) -> Optional[Path]:
    direct = content_root / "principles"
    if direct.is_dir():
        return direct
    templates = content_root / "templates" / "principles"
    if templates.is_dir():
        return templates
    if plugin_root is not None:
        direct = plugin_root / "principles"
        if direct.is_dir():
            return direct
        templates = plugin_root / "templates" / "principles"
        if templates.is_dir():
            return templates
    return None


def _resolve_flags_md(
    content_root: Path,
    plugin_root: Optional[Path] = None,
    config_home: Optional[Path] = None,
) -> Optional[Path]:
    if config_home is not None:
        candidate = config_home / "FLAGS.md"
        if candidate.is_file():
            return candidate
    direct = content_root / "FLAGS.md"
    if direct.is_file():
        return direct
    template = content_root / "templates" / "FLAGS.md"
    if template.is_file():
        return template
    if plugin_root is not None:
        direct = plugin_root / "FLAGS.md"
        if direct.is_file():
            return direct
        template = plugin_root / "templates" / "FLAGS.md"
        if template.is_file():
            return template
    return None


def _ensure_default_config(
    config_path: Path,
    config: Dict[str, object],
    plugin_root: Path,
    content_root: Optional[Path] = None,
) -> Tuple[Dict[str, object], List[str]]:
    updated = False
    warnings: List[str] = []

    source_root = content_root or plugin_root
    rules_dir = source_root / "rules"
    fallback_rules_dir = plugin_root / "rules" if plugin_root is not None else None
    principles_dir = _resolve_principles_dir(source_root, plugin_root)
    flags_md = _resolve_flags_md(source_root, plugin_root, config_path.parent)

    if "rules" not in config:
        rules = _list_dir_stems(rules_dir)
        if not rules and fallback_rules_dir is not None:
            rules = _list_dir_stems(fallback_rules_dir)
        config["rules"] = rules
        updated = True
    if "flags" not in config:
        config["flags"] = _parse_flags_md(flags_md) if flags_md else []
        updated = True
    if "modes" not in config:
        config["modes"] = []
        updated = True
    if "principles" not in config:
        if principles_dir is None:
            config["principles"] = []
        else:
            config["principles"] = _list_dir_stems(principles_dir)
        updated = True

    if "settings_path" not in config:
        settings_path = source_root / "templates" / "settings.json"
        if not settings_path.exists() and plugin_root is not None:
            fallback = plugin_root / "templates" / "settings.json"
            settings_path = fallback
        config["settings_path"] = str(settings_path) if settings_path.exists() else None
        updated = True

    if updated:
        try:
            _write_json(config_path, config)
            warnings.append(f"Initialized config: {config_path}")
        except OSError as exc:
            warnings.append(f"Failed to write {config_path}: {exc}")

    return config, warnings


def _normalize_name_list(values: Iterable[str]) -> List[str]:
    items: List[str] = []
    for value in values:
        if not isinstance(value, str):
            continue
        for part in value.split(","):
            cleaned = part.strip()
            if cleaned:
                items.append(cleaned)
    return items


def _ensure_symlink(source: Path, target: Path) -> Optional[str]:
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
    """Sync active rule symlinks into ~/.claude/rules/cortex/."""
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


def _read_markdown(path: Path) -> Optional[str]:
    try:
        text = path.read_text(encoding="utf-8").strip()
    except OSError:
        return None
    return text or None


def _resolve_relative_md(root: Path, name: str) -> Path:
    if name.endswith(".md"):
        rel = name
    else:
        rel = f"{name}.md"
    return root / rel


def _parse_flags_md(path: Optional[Path]) -> List[str]:
    if path is None or not path.exists():
        return []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []
    active: List[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped.startswith("@flags/"):
            continue
        name = stripped.replace("@flags/", "", 1).strip()
        if name:
            active.append(name)
    return active


def build_system_prompt(
    content_root: Path,
    modes: Iterable[str],
    principles: Iterable[str],
    flags: Iterable[str],
    plugin_root: Optional[Path] = None,
) -> str:
    sections: List[str] = []

    principles_dir = _resolve_principles_dir(content_root, plugin_root)
    if principles_dir is not None:
        active_principles = _normalize_name_list(principles)
        if not active_principles:
            active_principles = _list_dir_stems(principles_dir)
        for name in active_principles:
            snippet_path = _resolve_relative_md(principles_dir, name)
            text = _read_markdown(snippet_path)
            if text:
                sections.append(text)

    flags_dir = content_root / "flags"
    if not flags_dir.is_dir() and plugin_root is not None:
        flags_dir = plugin_root / "flags"
    if flags_dir.is_dir():
        active_flags = _normalize_name_list(flags)
        for name in active_flags:
            flag_path = _resolve_relative_md(flags_dir, name)
            text = _read_markdown(flag_path)
            if text:
                sections.append(text)

    modes_dir = content_root / "modes"
    if not modes_dir.is_dir() and plugin_root is not None:
        modes_dir = plugin_root / "modes"
    if modes_dir.is_dir():
        active_modes = _normalize_name_list(modes)
        for name in active_modes:
            mode_path = _resolve_relative_md(modes_dir, name)
            text = _read_markdown(mode_path)
            if text:
                sections.append(text)

    return "\n\n".join(sections).strip()


def load_launcher_config(
    *,
    config_path: Path,
    plugin_root: Path,
    content_root: Optional[Path] = None,
    modes_override: Optional[str] = None,
    flags_override: Optional[str] = None,
) -> Tuple[LauncherConfig, List[str]]:
    config, warnings = _read_json(config_path)
    config, update_warnings = _ensure_default_config(
        config_path, config, plugin_root, content_root=content_root
    )
    warnings.extend(update_warnings)

    rules = _normalize_name_list(config.get("rules", [])) if isinstance(config.get("rules"), list) else []
    flags_md = _resolve_flags_md(content_root or plugin_root, plugin_root, config_path.parent)
    if flags_override:
        flags = _normalize_name_list(flags_override.split(","))
    elif flags_md is not None:
        flags = _parse_flags_md(flags_md)
    elif isinstance(config.get("flags"), list):
        flags = _normalize_name_list(config.get("flags", []))
    else:
        flags = []
    modes = _normalize_name_list(modes_override.split(",")) if modes_override else (
        _normalize_name_list(config.get("modes", [])) if isinstance(config.get("modes"), list) else []
    )
    principles = _normalize_name_list(config.get("principles", [])) if isinstance(config.get("principles"), list) else []

    settings_path = None
    settings_raw = config.get("settings_path")
    if isinstance(settings_raw, str) and settings_raw.strip():
        settings_path = Path(settings_raw).expanduser()

    return (
        LauncherConfig(
            plugin_root=plugin_root,
            settings_path=settings_path,
            rules=rules,
            flags=flags,
            modes=modes,
            principles=principles,
        ),
        warnings,
    )


def start_claude(
    *,
    config_path: Path = DEFAULT_CONFIG_PATH,
    plugin_dir: Optional[Path] = None,
    claude_bin: str = "claude",
    settings_path: Optional[Path] = None,
    modes_override: Optional[str] = None,
    flags_override: Optional[str] = None,
    extra_args: Optional[List[str]] = None,
) -> int:
    config_raw, config_warnings = _read_json(config_path)
    plugin_root = _resolve_plugin_root(plugin_dir, config_raw)
    if plugin_root is None or not plugin_root.exists():
        raise RuntimeError(
            "Unable to resolve plugin root. Provide --plugin-dir or set "
            "`plugin_dir` in ~/.cortex/cortex-config.json."
        )

    content_root = config_path.parent if config_path is not None else _resolve_cortex_root()
    config, warnings = load_launcher_config(
        config_path=config_path,
        plugin_root=plugin_root,
        content_root=content_root,
        modes_override=modes_override,
        flags_override=flags_override,
    )
    warnings = config_warnings + warnings

    sync_code, sync_messages = sync_rule_symlinks(
        content_root, config.rules, fallback_root=plugin_root
    )
    for message in warnings + sync_messages:
        print(message)

    prompt = build_system_prompt(
        content_root=content_root,
        modes=config.modes,
        principles=config.principles,
        flags=config.flags,
        plugin_root=plugin_root,
    )

    cmd: List[str] = [claude_bin]
    cmd.extend(["--plugin-dir", str(plugin_root)])

    effective_settings = settings_path or config.settings_path
    if effective_settings is not None:
        if effective_settings.exists():
            cmd.extend(["--settings", str(effective_settings)])
        else:
            print(f"Settings file not found: {effective_settings}")

    if prompt:
        cmd.extend(["--append-system-prompt", prompt])

    if extra_args:
        cmd.extend(extra_args)

    env = os.environ.copy()
    env["CLAUDE_PLUGIN_ROOT"] = str(plugin_root)
    env["CORTEX_ROOT"] = str(content_root)

    return subprocess.call(cmd, env=env)
