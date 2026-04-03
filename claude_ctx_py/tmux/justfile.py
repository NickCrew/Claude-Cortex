"""Generate Justfile service targets wrapping ``cortex tmux``.

Detects project type, package manager, and long-running scripts,
then emits ready-to-paste Justfile recipes for tmux service management.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# package.json scripts that typically represent long-running services.
_SERVICE_SCRIPTS: Dict[str, str] = {
    "dev": "Dev server",
    "develop": "Dev server",
    "start": "App server",
    "serve": "App server",
    "server": "Backend server",
    "proxy": "Local proxy",
    "dev:server": "Backend server",
    "dev:api": "API server",
    "dev:client": "Frontend dev server",
    "dev:frontend": "Frontend dev server",
    "dev:proxy": "Local proxy",
    "storybook": "Storybook",
    "docs:dev": "Docs dev server",
    "watch": "File watcher",
    "build:watch": "Build watcher",
}


@dataclass
class Service:
    """A long-running service to run in a tmux window."""

    name: str  # tmux window name (e.g. "dev", "proxy")
    label: str  # Human-readable description
    command: str  # Shell command to execute


@dataclass
class ProjectInfo:
    """Detected project metadata."""

    name: str  # Directory-derived session name
    pkg_manager: str = "npm"
    framework: str = ""
    services: List[Service] = field(default_factory=list)


# ── Detection helpers ───────────────────────────────────────────────


def _detect_pkg_manager(directory: Path) -> str:
    """Detect the Node.js package manager from lock files."""
    if (directory / "pnpm-lock.yaml").exists():
        return "pnpm"
    if (directory / "yarn.lock").exists():
        return "yarn"
    if (directory / "bun.lockb").exists():
        return "bun"
    return "npm"


def _detect_framework(directory: Path) -> str:
    """Detect the frontend framework from config files."""
    checks: List[Tuple[List[str], str]] = [
        (["vite.config.ts", "vite.config.js", "vite.config.mjs"], "vite"),
        (["next.config.js", "next.config.mjs", "next.config.ts"], "next"),
        (["nuxt.config.ts", "nuxt.config.js"], "nuxt"),
        (["angular.json"], "angular"),
        (["svelte.config.js", "svelte.config.ts"], "svelte"),
        (["remix.config.js", "remix.config.ts"], "remix"),
        (["astro.config.mjs", "astro.config.ts"], "astro"),
    ]
    for filenames, fw in checks:
        if any((directory / f).exists() for f in filenames):
            return fw
    return ""


def _safe_window_name(name: str) -> str:
    """Convert a script/project name to a tmux-safe window name."""
    return name.replace(":", "-").replace(" ", "-").replace("_", "-")


def _run_cmd(pkg_manager: str, script: str) -> str:
    """Build the idiomatic run command for *pkg_manager*."""
    if pkg_manager in ("pnpm", "yarn"):
        return f"{pkg_manager} {script}"
    if pkg_manager == "bun":
        return f"bun run {script}"
    return f"npm run {script}"


def _detect_services_node(
    directory: Path, pkg_manager: str
) -> List[Service]:
    """Detect service-like scripts from ``package.json``."""
    pkg_json = directory / "package.json"
    if not pkg_json.exists():
        return []
    try:
        data = json.loads(pkg_json.read_text())
    except (json.JSONDecodeError, OSError):
        return []

    scripts = data.get("scripts", {})
    if not scripts:
        return []

    services: List[Service] = []
    for script_name, label in _SERVICE_SCRIPTS.items():
        if script_name in scripts:
            services.append(
                Service(
                    name=_safe_window_name(script_name),
                    label=label,
                    command=_run_cmd(pkg_manager, script_name),
                )
            )
    return services


def _detect_services_nx(
    directory: Path, pkg_manager: str  # noqa: ARG001 – reserved
) -> List[Service]:
    """Detect services from Nx workspace ``project.json`` files."""
    services: List[Service] = []
    seen: set[str] = set()

    for pattern in ("apps/*/project.json", "packages/*/project.json"):
        for pj_path in sorted(directory.glob(pattern)):
            try:
                pj = json.loads(pj_path.read_text())
            except (json.JSONDecodeError, OSError):
                continue
            proj_name = pj.get("name", pj_path.parent.name)
            targets = pj.get("targets", {})
            for target in ("serve", "dev"):
                if target in targets:
                    win = _safe_window_name(proj_name)
                    if win not in seen:
                        seen.add(win)
                        services.append(
                            Service(
                                name=win,
                                label=f"{proj_name} ({target})",
                                command=f"npx nx {target} {proj_name}",
                            )
                        )
                    break  # prefer serve over dev
    return services


def detect_project(directory: Optional[str] = None) -> ProjectInfo:
    """Detect project type, package manager, and available services."""
    path = Path(directory) if directory else Path.cwd()
    name = path.name.lower().replace(" ", "-")
    info = ProjectInfo(name=name)

    # Node.js
    if (path / "package.json").exists():
        info.pkg_manager = _detect_pkg_manager(path)
        info.framework = _detect_framework(path)

        # Nx workspace gets priority
        if (path / "nx.json").exists():
            info.services = _detect_services_nx(path, info.pkg_manager)

        # Fall back to package.json scripts
        if not info.services:
            info.services = _detect_services_node(path, info.pkg_manager)

    elif (path / "pyproject.toml").exists() or (path / "setup.py").exists():
        info.pkg_manager = "python"
    elif (path / "Cargo.toml").exists():
        info.pkg_manager = "cargo"
    elif (path / "go.mod").exists():
        info.pkg_manager = "go"

    # Fallback placeholder when nothing detected
    if not info.services:
        info.services = [
            Service(
                name="app",
                label="Application",
                command="echo 'TODO: replace with your dev command'",
            )
        ]

    return info


# ── Justfile generation ─────────────────────────────────────────────


def _jvar(var: str) -> str:
    """Return a Just ``{{ var }}`` interpolation expression."""
    return "{{ " + var + " }}"


def generate_justfile(project: ProjectInfo, prefix: str = "svc") -> str:
    """Generate Justfile service management targets."""
    lines: List[str] = []
    sess_var = f"_{prefix}_session"
    ctx_var = f"_{prefix}_cortex"
    init_recipe = f"_{prefix}-init"
    ctx = _jvar(ctx_var)
    sess = _jvar(sess_var)

    det = project.pkg_manager
    if project.framework:
        det += f" + {project.framework}"

    # Header
    lines.extend(
        [
            "# ─── Service Management ─────────────────────────────────────────────",
            "# Generated by: cortex tmux justfile",
            f"# Detected: {det}",
            "# ────────────────────────────────────────────────────────────────────",
            "",
            f'{sess_var} := env_var_or_default("TMUX_SESSION", "{project.name}")',
            f'{ctx_var}  := "cortex tmux"',
            "",
        ]
    )

    # _<prefix>-init (private)
    lines.extend(
        [
            "# Ensure the tmux session exists",
            f"{init_recipe}:",
            f'    @tmux has-session -t "{sess}" 2>/dev/null'
            f' || tmux new-session -d -s "{sess}"',
            "",
        ]
    )

    # svc-session
    lines.extend(
        [
            "# Print the tmux session name used by service recipes",
            f"{prefix}-session:",
            f'    @echo "{sess}"',
            "",
        ]
    )

    # Per-service start targets
    target_names: List[str] = []
    for svc in project.services:
        t = f"{prefix}-{svc.name}"
        target_names.append(t)
        lines.extend(
            [
                f"# Start {svc.label} in a dedicated window",
                f"{t}: {init_recipe}",
                f"    {ctx} new {svc.name} 2>/dev/null || true",
                f'    {ctx} send {svc.name} "{svc.command}"',
                "",
            ]
        )

    # svc-up
    lines.extend(
        [
            "# Start all service windows",
            f"{prefix}-up: {' '.join(target_names)}",
            "",
        ]
    )

    # svc-status
    lines.append("# Show status of service windows")
    lines.append(f"{prefix}-status:")
    for svc in project.services:
        lines.append(
            f'    @{ctx} status {svc.name} 2>/dev/null'
            f' || echo "{svc.name}: not running"'
        )
    lines.append("")

    # svc-stop
    lines.append("# Stop all service windows")
    lines.append(f"{prefix}-stop:")
    for svc in project.services:
        lines.append(f"    -{ctx} kill {svc.name}")
    lines.append("")

    # Per-service restart targets
    for svc in project.services:
        lines.extend(
            [
                f"# Restart {svc.label}",
                f"{prefix}-restart-{svc.name}:",
                f"    {ctx} interrupt {svc.name}",
                f"    -{ctx} wait {svc.name} 5",
                f'    {ctx} send {svc.name} "{svc.command}"',
                "",
            ]
        )

    # svc-restart (all)
    lines.extend(
        [
            "# Restart all services",
            f"{prefix}-restart: {prefix}-stop {prefix}-up",
            "",
        ]
    )

    # svc-shell
    lines.extend(
        [
            "# Attach to the service tmux session",
            f"{prefix}-shell:",
            f'    tmux attach-session -t "{sess}" 2>/dev/null'
            f' || tmux new-session -s "{sess}"',
            "",
        ]
    )

    # svc-reset
    lines.extend(
        [
            "# Reset the tmux session (kill and recreate)",
            f"{prefix}-reset:",
            f'    -tmux kill-session -t "{sess}"',
            f'    tmux new-session -d -s "{sess}"',
            "",
        ]
    )

    return "\n".join(lines)


def tmux_justfile(
    directory: Optional[str] = None,
    prefix: str = "svc",
) -> Tuple[int, str]:
    """Generate Justfile targets for tmux service management.

    Returns ``(exit_code, justfile_content)``.
    """
    project = detect_project(directory)
    content = generate_justfile(project, prefix=prefix)
    return 0, content
