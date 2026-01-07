"""Profile and initialization functions."""

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
import time
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, List, Optional, Sequence, Set, Tuple

# Import from base module
from .base import (
    BLUE,
    GREEN,
    YELLOW,
    RED,
    NC,
    _append_session_log,
    _color,
    _confirm,
    _ensure_claude_structure,
    _format_detection_summary,
    _format_header,
    _init_slug_for_path,
    _is_disabled,
    _iter_all_files,
    _iter_md_files,
    _list_available_agents,
    _list_available_modes,
    _load_detection_file,
    _parse_active_entries,
    _parse_selection,
    _prompt_user,
    _refresh_claude_md,
    _resolve_claude_dir,
    _resolve_init_dirs,
    _resolve_init_target,
    _run_analyze_project,
    _run_detect_project_type,
    _strip_ansi_codes,
)

# Import from other core modules
from .agents import (
    agent_activate,
    agent_deactivate,
    agent_status,
    _agent_basename,
    ESSENTIAL_AGENTS,
    FRONTEND_AGENTS,
    WEB_DEV_AGENTS,
    BACKEND_AGENTS,
    DEVOPS_AGENTS,
    DOCUMENTATION_AGENTS,
    DATA_AI_AGENTS,
    QUALITY_AGENTS,
    META_AGENTS,
    DX_AGENTS,
    PRODUCT_AGENTS,
    FULL_AGENTS,
    BUILT_IN_PROFILES,
)
from .modes import mode_activate, mode_deactivate, mode_status
from .rules import rules_activate


# Flag category mappings for profiles
PROFILE_FLAGS = {
    "minimal": [
        "mode-activation.md",
        "mcp-servers.md",
        "execution-control.md",
    ],
    "frontend": [
        "mode-activation.md",
        "mcp-servers.md",
        "execution-control.md",
        "visual-excellence.md",
        "testing-quality.md",
        "domain-presets.md",
        "debugging-trace.md",
    ],
    "web-dev": [
        "mode-activation.md",
        "mcp-servers.md",
        "analysis-depth.md",
        "execution-control.md",
        "visual-excellence.md",
        "output-optimization.md",
        "testing-quality.md",
        "domain-presets.md",
        "debugging-trace.md",
    ],
    "backend": [
        "mode-activation.md",
        "mcp-servers.md",
        "analysis-depth.md",
        "execution-control.md",
        "testing-quality.md",
        "debugging-trace.md",
        "refactoring-safety.md",
    ],
    "devops": [
        "mode-activation.md",
        "mcp-servers.md",
        "execution-control.md",
        "debugging-trace.md",
        "ci-cd.md",
    ],
    "documentation": [
        "mode-activation.md",
        "execution-control.md",
        "learning-education.md",
    ],
    "data-ai": [
        "mode-activation.md",
        "mcp-servers.md",
        "analysis-depth.md",
        "execution-control.md",
        "testing-quality.md",
    ],
    "quality": [
        "mode-activation.md",
        "mcp-servers.md",
        "analysis-depth.md",
        "execution-control.md",
        "testing-quality.md",
        "refactoring-safety.md",
        "debugging-trace.md",
    ],
    "meta": [
        "mode-activation.md",
        "mcp-servers.md",
        "analysis-depth.md",
        "execution-control.md",
        "refactoring-safety.md",
    ],
    "developer-experience": [
        "mode-activation.md",
        "mcp-servers.md",
        "execution-control.md",
        "interactive-control.md",
    ],
    "product": [
        "mode-activation.md",
        "execution-control.md",
        "learning-education.md",
    ],
    "full": [
        # All flags enabled for full profile
        "mode-activation.md",
        "mcp-servers.md",
        "thinking-budget.md",
        "analysis-depth.md",
        "auto-escalation.md",
        "execution-control.md",
        "visual-excellence.md",
        "output-optimization.md",
        "testing-quality.md",
        "learning-education.md",
        "cost-budget.md",
        "refactoring-safety.md",
        "domain-presets.md",
        "debugging-trace.md",
        "interactive-control.md",
        "ci-cd.md",
        "performance-optimization.md",
        "security-hardening.md",
        "documentation-generation.md",
        "git-workflow.md",
        "migration-upgrade.md",
        "database-operations.md",
    ],
}


def _apply_profile_flags(profile_name: str, claude_dir: Path) -> None:
    """Apply flag configuration for a given profile by modifying FLAGS.md."""
    flags_md_path = claude_dir / "FLAGS.md"

    if not flags_md_path.exists():
        return

    profile_flags = PROFILE_FLAGS.get(profile_name, [])
    profile_flag_set = set(profile_flags)

    try:
        lines = flags_md_path.read_text(encoding="utf-8").splitlines(keepends=True)
    except OSError:
        return

    modified_lines: List[str] = []
    active_flags_present: Set[str] = set()

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("@flags/"):
            filename = stripped.replace("@flags/", "").strip()
            if filename in profile_flag_set:
                modified_lines.append(f"@flags/{filename}\n")
                active_flags_present.add(filename)
            continue
        if stripped.startswith("<!-- @flags/") and stripped.endswith("-->"):
            # Drop legacy commented references.
            continue
        modified_lines.append(line)

    missing_flags = [name for name in profile_flags if name not in active_flags_present]
    if missing_flags:
        if modified_lines and not modified_lines[-1].endswith("\n"):
            modified_lines[-1] = f"{modified_lines[-1]}\n"
        for filename in missing_flags:
            modified_lines.append(f"@flags/{filename}\n")

    try:
        flags_md_path.write_text("".join(modified_lines), encoding="utf-8")
    except OSError:
        return


def _profile_reset(home: Path | None = None) -> Tuple[int, str]:
    """Reset to minimal configuration while surfacing any operation failures."""

    claude_dir = _resolve_claude_dir(home)

    # Ensure directory structure exists
    _ensure_claude_structure(claude_dir)

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

    # Apply minimal profile flags
    _apply_profile_flags("minimal", claude_dir)

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


def _get_active_agents_list(claude_dir: Path) -> List[str]:
    """Get list of currently active agent names."""
    active_file = claude_dir / ".active-agents"
    if not active_file.is_file():
        return []

    return [
        line.strip()
        for line in active_file.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _get_active_rules_list(claude_dir: Path) -> List[str]:
    """Get list of currently active rule names."""
    active_file = claude_dir / ".active-rules"
    if not active_file.is_file():
        return []

    return [
        line.strip()
        for line in active_file.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]



def _get_current_active_state(claude_dir: Path) -> Tuple[Set[str], Set[str], Set[str]]:
    """Get the current active agents, modes, and rules as sets."""
    active_agents = set(_get_active_agents_list(claude_dir))
    # _get_active_modes is in claude_ctx_py/core/modes.py
    from .modes import _get_active_modes
    active_modes = set(_get_active_modes(claude_dir))
    active_rules = set(_get_active_rules_list(claude_dir))
    return active_agents, active_modes, active_rules


def _get_profile_state(profile_path: Path) -> Tuple[Set[str], Set[str], Set[str]]:
    """Parse a .profile file and return the agents, modes, and rules as sets."""
    content = profile_path.read_text(encoding="utf-8")
    profile_agents: Set[str] = set()
    profile_modes: Set[str] = set()
    profile_rules: Set[str] = set()

    for line in content.splitlines():
        if line.startswith("AGENTS=\""):
            profile_agents = set(line.strip().split("=\"", 1)[1][:-1].split())
        elif line.startswith("MODES=\""):
            profile_modes = set(line.strip().split("=\"", 1)[1][:-1].split())
        elif line.startswith("RULES=\""):
            profile_rules = set(line.strip().split("=\"", 1)[1][:-1].split())

    return profile_agents, profile_modes, profile_rules


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
            messages.append(_color("Failed to activate Task_Management mode", RED))
        return exit_code, "\n".join(messages)
    if mode_message:
        messages.append(mode_message)

    rule_message = rules_activate("quality-rules", home=home)
    if rule_message:
        messages.append(rule_message)

    # Apply backend profile flags
    _apply_profile_flags("backend", claude_dir)

    _refresh_claude_md(claude_dir)

    messages.append(_color("Loaded profile: backend", GREEN))
    return 0, "\n".join(messages)


def _load_profile_with_agents(
    profile_name: str,
    agent_list: List[str],
    *,
    home: Path | None = None,
    activate_task_management: bool = False,
    activate_quality_rules: bool = False,
) -> Tuple[int, str]:
    """Generic profile loader that resets and activates specified agents."""
    claude_dir = _resolve_claude_dir(home)

    exit_code, reset_message = _profile_reset(home=home)
    messages: List[str] = []
    if reset_message:
        messages.append(reset_message)
    if exit_code != 0:
        return exit_code, "\n".join(messages)

    for agent_name in agent_list:
        exit_code, message = agent_activate(agent_name, home=home)
        if exit_code != 0:
            if message:
                messages.append(message)
            else:
                messages.append(_color(f"Failed to activate agent: {agent_name}", RED))
            return exit_code, "\n".join(messages)
        if message:
            messages.append(message)

    if activate_task_management:
        exit_code, mode_message = mode_activate("Task_Management", home=home)
        # Task_Management might already be active from _profile_reset, which is ok
        if exit_code != 0 and "not found in inactive modes" not in mode_message:
            if mode_message:
                messages.append(mode_message)
            else:
                messages.append(_color("Failed to activate Task_Management mode", RED))
            return exit_code, "\n".join(messages)
        if mode_message and exit_code == 0:
            messages.append(mode_message)

    if activate_quality_rules:
        rule_message = rules_activate("quality-rules", home=home)
        if rule_message:
            messages.append(rule_message)

    # Apply profile-specific flags
    _apply_profile_flags(profile_name, claude_dir)

    _refresh_claude_md(claude_dir)

    messages.append(_color(f"Loaded profile: {profile_name}", GREEN))
    return 0, "\n".join(messages)


def profile_frontend(home: Path | None = None) -> Tuple[int, str]:
    """Load frontend profile: minimal + TypeScript, code review."""
    return _load_profile_with_agents(
        "frontend",
        FRONTEND_AGENTS,
        home=home,
        activate_task_management=True,
    )


def profile_web_dev(home: Path | None = None) -> Tuple[int, str]:
    """Load web-dev profile: minimal + full-stack web development tools."""
    return _load_profile_with_agents(
        "web-dev",
        WEB_DEV_AGENTS,
        home=home,
        activate_task_management=True,
        activate_quality_rules=True,
    )


def profile_devops(home: Path | None = None) -> Tuple[int, str]:
    """Load devops profile: infrastructure and deployment focused."""
    return _load_profile_with_agents(
        "devops",
        DEVOPS_AGENTS,
        home=home,
        activate_task_management=True,
    )


def profile_documentation(home: Path | None = None) -> Tuple[int, str]:
    """Load documentation profile: documentation and writing focused."""
    return _load_profile_with_agents(
        "documentation",
        DOCUMENTATION_AGENTS,
        home=home,
        activate_task_management=True,
    )


def profile_data_ai(home: Path | None = None) -> Tuple[int, str]:
    """Load data-ai profile: data science and AI development."""
    return _load_profile_with_agents(
        "data-ai",
        DATA_AI_AGENTS,
        home=home,
        activate_task_management=True,
    )


def profile_quality(home: Path | None = None) -> Tuple[int, str]:
    """Load quality profile: code quality and security focused."""
    return _load_profile_with_agents(
        "quality",
        QUALITY_AGENTS,
        home=home,
        activate_task_management=True,
        activate_quality_rules=True,
    )


def profile_meta(home: Path | None = None) -> Tuple[int, str]:
    """Load meta profile: meta-programming and tooling."""
    return _load_profile_with_agents(
        "meta",
        META_AGENTS,
        home=home,
        activate_task_management=True,
    )


def profile_developer_experience(home: Path | None = None) -> Tuple[int, str]:
    """Load developer-experience profile: DX and tooling optimization."""
    return _load_profile_with_agents(
        "developer-experience",
        DX_AGENTS,
        home=home,
        activate_task_management=True,
    )


def profile_product(home: Path | None = None) -> Tuple[int, str]:
    """Load product profile: product development and management."""
    return _load_profile_with_agents(
        "product",
        PRODUCT_AGENTS,
        home=home,
        activate_task_management=True,
    )


def profile_full(home: Path | None = None) -> Tuple[int, str]:
    """Load full profile: all available agents enabled."""
    return _load_profile_with_agents(
        "full",
        FULL_AGENTS,
        home=home,
        activate_task_management=True,
        activate_quality_rules=True,
    )


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

    iso_now = datetime.datetime.now(timezone.utc).replace(microsecond=0).isoformat() + "Z"

    detection_raw = _run_detect_project_type(resolved_path)
    detection_language = detection_framework = detection_infra = ""
    detection_types_raw = ""
    if detection_raw:
        parts = [part.strip() for part in detection_raw.split("|")]
        while len(parts) < 4:
            parts.append("")
        (
            detection_language,
            detection_framework,
            detection_infra,
            detection_types_raw,
        ) = parts[:4]

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

    # Ensure all required directories and files exist
    created = _ensure_claude_structure(claude_dir)

    exit_code, message = _profile_reset(home=home)
    if exit_code != 0:
        return exit_code, message

    lines = []
    if created:
        lines.append(_color(f"Created {len(created)} directories/files", GREEN))
    if message:
        lines.append(message)
    lines.append(_color("Initialized minimal cortex configuration", GREEN))

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
        hint = "Use 'cortex profile list' to view available presets."
        return 1, f"{message}\n{hint}"

    loaders = {
        "minimal": profile_minimal,
        "frontend": profile_frontend,
        "web-dev": profile_web_dev,
        "backend": profile_backend,
        "devops": profile_devops,
        "documentation": profile_documentation,
        "data-ai": profile_data_ai,
        "quality": profile_quality,
        "meta": profile_meta,
        "developer-experience": profile_developer_experience,
        "product": profile_product,
        "full": profile_full,
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
            f"Initialized cortex with profile '{profile_name}'",
            GREEN,
        )
    )
    return 0, "\n".join(lines)


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
    summary_timestamp = (
        base_data.get("timestamp") if isinstance(base_data, dict) else None
    )
    summary_language = (
        base_data.get("language") if isinstance(base_data, dict) else None
    )
    summary_framework = (
        base_data.get("framework") if isinstance(base_data, dict) else None
    )
    summary_infra = (
        base_data.get("infrastructure") if isinstance(base_data, dict) else None
    )
    types_val = base_data.get("types") if isinstance(base_data, dict) else None
    summary_types_list = types_val if isinstance(types_val, list) else []
    summary_types = (
        ", ".join(str(item) for item in summary_types_list)
        if summary_types_list
        else "none"
    )
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
        summary_lines.append("    analyze_project output stored in detection.json")

    exit_code = 0
    if proj_error is not None or cache_error is not None or match_status == "mismatch":
        exit_code = 1

    summary_text = "\n".join(summary_lines)

    warnings: List[str] = []
    if proj_error:
        warnings.append(colorize(f"Project detection.json {proj_error}", RED))
    if cache_error:
        warnings.append(colorize(f"Cache detection.json {cache_error}", RED))
    if match_status == "mismatch":
        warnings.append(colorize("Cache and project detection artifacts differ", RED))
    elif match_status == "unverified" and not (proj_error or cache_error):
        warnings.append(colorize("Unable to verify cache consistency", YELLOW))

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
        warnings_text = "\n".join(
            [warning for warning in [warnings_text, error_text] if warning]
        )
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
        lines.append(_color(f"  Removed project state: {project_dir}", GREEN))
    if cache_removed:
        lines.append(_color(f"  Removed cache state: {cache_project_dir}", GREEN))

    if not (project_removed or cache_removed):
        lines.append(
            _color(
                "  No init detection artifacts found for this project",
                YELLOW,
            )
        )

    lines.append(f"{_color('TODO:', YELLOW)} Additional reset behaviors coming soon.")

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
        "project"
        if proj_data is not None
        else "cache" if cache_data is not None else None
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
        warning_lines.append(f"no previous init detection found for slug '{slug}'")
        message = _color(
            "init_resume: " + "; ".join(warning_lines),
            YELLOW,
        )
        return 1, message

    timestamp = (
        detection_data.get("timestamp") if isinstance(detection_data, dict) else None
    )
    detected_path = (
        detection_data.get("path") if isinstance(detection_data, dict) else None
    )
    language = (
        detection_data.get("language") if isinstance(detection_data, dict) else None
    )
    framework = (
        detection_data.get("framework") if isinstance(detection_data, dict) else None
    )
    infrastructure = (
        detection_data.get("infrastructure")
        if isinstance(detection_data, dict)
        else None
    )
    types_val = (
        detection_data.get("types") if isinstance(detection_data, dict) else None
    )
    types_label = (
        ", ".join(str(item) for item in types_val)
        if isinstance(types_val, list) and types_val
        else "none"
    )

    summary_path = detected_path or (
        str(resolved_path) if resolved_path else "(unknown)"
    )

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

    # Ensure all required directories and files exist
    _ensure_claude_structure(claude_dir)

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
    wizard_lines.append(f"  Profile: {profile_choice}")
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
        f"- Timestamp: {datetime.datetime.now(timezone.utc).isoformat()}Z",
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
    "BUILT_IN_PROFILES",
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


def show_status(home: Path | None = None) -> str:
    claude_dir = _resolve_claude_dir(home)
    home_arg = claude_dir.parent

    sections: List[str] = [_color("=== Cortex Status ===", BLUE)]
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
