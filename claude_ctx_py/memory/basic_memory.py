"""Basic Memory integration for ``cortex notes``.

``cortex notes`` stores Markdown in a scope-aware vault (``.cortex/vault`` for
project scope, ``~/.cortex/vault`` globally — see :mod:`config`). This module
wires that vault into the Basic Memory CLI/MCP:

- ``init``            register the vault as a Basic Memory project
                      (``basic-memory project add <name> <vault>``)
- ``remove``          unregister it (``basic-memory project remove <name>``)
- ``mcp``             run the project's MCP server
                      (``basic-memory mcp --project <name>``)
- ``mcp --configure`` record that server in the local Claude Code MCP config
                      (``~/.claude.json`` under the project key)

Runtime resolution prefers ``uvx basic-memory`` (no global install needed),
falls back to a directly-installed ``basic-memory`` (e.g. Homebrew), and
otherwise tells the user to install uv.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from ..core.base import _resolve_claude_dir
from .config import ensure_vault_structure, get_vault_path
from .notes import slugify

# A subprocess runner — injected in tests; defaults to subprocess.run. Typed as
# Callable[..., Any] to sidestep subprocess.run's overloaded return type under
# --strict; only ``.returncode`` is read from the result.
Runner = Callable[..., Any]
Which = Callable[[str], Optional[str]]


class BasicMemoryUnavailable(RuntimeError):
    """Raised when neither uv (uvx) nor basic-memory is installed."""


_INSTALL_HINT = (
    "Basic Memory is unavailable.\n"
    "Install uv (recommended — cortex notes then runs `uvx basic-memory` with "
    "no further setup):\n"
    "  brew install uv\n"
    "  # or: curl -LsSf https://astral.sh/uv/install.sh | sh\n"
    "Alternatively install basic-memory directly: brew install basic-memory"
)


@dataclass(frozen=True)
class Runtime:
    """How to invoke the Basic Memory CLI on this machine.

    ``command`` is the executable; ``prefix`` are the leading args before the
    basic-memory subcommand. For uvx: ``command="uvx"``, ``prefix=("basic-memory",)``.
    For a direct install: ``command="basic-memory"``, ``prefix=()``.
    """

    command: str
    prefix: Tuple[str, ...]

    def argv(self, *args: str) -> List[str]:
        """Full argv for a basic-memory invocation, e.g. ``argv("mcp")``."""
        return [self.command, *self.prefix, *args]


def resolve_runtime(which: Which = shutil.which) -> Runtime:
    """Resolve how to invoke Basic Memory, preferring uvx.

    Order: uvx (uv installed) → ``basic-memory`` on PATH (e.g. Homebrew) →
    raise :class:`BasicMemoryUnavailable` with an install hint.
    """
    if which("uvx"):
        return Runtime("uvx", ("basic-memory",))
    if which("basic-memory"):
        return Runtime("basic-memory", ())
    raise BasicMemoryUnavailable(_INSTALL_HINT)


def _project_root() -> Path:
    """Project root for the active scope — parent of the resolved ``.claude``."""
    return _resolve_claude_dir().parent


def default_project_name() -> str:
    """Default Basic Memory project name: ``<project-dir>-notes`` (slugified).

    Reads the active ``CORTEX_SCOPE``: project scope yields ``<repo>-notes``,
    global scope yields ``<home-dir>-notes``.
    """
    base = slugify(_project_root().name) or "cortex"
    return f"{base}-notes"


def mcp_server_entry(runtime: Runtime, name: str) -> Dict[str, Any]:
    """Build the ``~/.claude.json`` mcpServers entry for the notes MCP server."""
    argv = runtime.argv("mcp", "--project", name)
    return {"command": argv[0], "args": argv[1:]}


# ── project registration ────────────────────────────────────────────────────


def init(name: Optional[str] = None, *, runner: Runner = subprocess.run) -> Tuple[int, str]:
    """Register the vault as a Basic Memory project."""
    try:
        runtime = resolve_runtime()
    except BasicMemoryUnavailable as exc:
        return 1, str(exc)

    project_name = name or default_project_name()
    vault = ensure_vault_structure(get_vault_path())
    vault_abs = str(vault.resolve())

    result = runner(runtime.argv("project", "add", project_name, vault_abs))
    if result.returncode != 0:
        return result.returncode, (
            f"`basic-memory project add` failed (exit {result.returncode})"
        )
    return 0, (
        f"Registered Basic Memory project '{project_name}'\n"
        f"  vault: {vault_abs}\n"
        f"Next: cortex notes mcp --configure   (register the MCP server)"
    )


def remove(
    name: Optional[str] = None,
    *,
    delete_notes: bool = False,
    runner: Runner = subprocess.run,
    config_path: Optional[Path] = None,
    project_root: Optional[Path] = None,
) -> Tuple[int, str]:
    """Unregister the Basic Memory project and drop its MCP config entry.

    The vault files are kept unless ``delete_notes`` is set. Removing the MCP
    config entry is best-effort so a stale entry doesn't outlive the project.
    """
    try:
        runtime = resolve_runtime()
    except BasicMemoryUnavailable as exc:
        return 1, str(exc)

    project_name = name or default_project_name()
    args = ["project", "remove", project_name]
    if delete_notes:
        args.append("--delete-notes")

    result = runner(runtime.argv(*args))
    if result.returncode != 0:
        return result.returncode, (
            f"`basic-memory project remove` failed (exit {result.returncode})"
        )

    unconfigured = _unconfigure_mcp(
        project_name, config_path=config_path, project_root=project_root
    )
    files_note = "vault files deleted" if delete_notes else "vault files kept"
    mcp_note = "; MCP config entry removed" if unconfigured else ""
    return 0, f"Removed Basic Memory project '{project_name}' ({files_note}){mcp_note}"


# ── MCP server ──────────────────────────────────────────────────────────────


def serve_mcp(name: Optional[str] = None, *, runner: Runner = subprocess.run) -> Tuple[int, str]:
    """Run the project's Basic Memory MCP server (stdio, inherits this process).

    Used for manual launches; the configured ``~/.claude.json`` entry invokes
    basic-memory directly, so this wrapper's extra process layer never affects
    Claude Code.
    """
    try:
        runtime = resolve_runtime()
    except BasicMemoryUnavailable as exc:
        return 1, str(exc)

    project_name = name or default_project_name()
    result = runner(runtime.argv("mcp", "--project", project_name))
    return int(result.returncode), ""


def configure_mcp(
    name: Optional[str] = None,
    *,
    config_path: Optional[Path] = None,
    project_root: Optional[Path] = None,
    runtime: Optional[Runtime] = None,
) -> Tuple[int, str]:
    """Register the notes MCP server in ``~/.claude.json`` (local, project-keyed).

    Merges into the existing project entry; other servers (e.g. backlog) and
    every other key are preserved.
    """
    if runtime is None:
        try:
            runtime = resolve_runtime()
        except BasicMemoryUnavailable as exc:
            return 1, str(exc)

    project_name = name or default_project_name()
    config_path = config_path or (Path.home() / ".claude.json")
    key = str((project_root or _project_root()).resolve())

    data, err = _load_claude_json(config_path)
    if err:
        return 1, err

    projects = data.setdefault("projects", {})
    if not isinstance(projects, dict):
        return 1, f"Unexpected 'projects' shape in {config_path}"
    project_entry = projects.setdefault(key, {})
    servers = project_entry.setdefault("mcpServers", {})
    servers[project_name] = mcp_server_entry(runtime, project_name)

    config_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return 0, (
        f"Configured MCP server '{project_name}' for {key}\n"
        f"  in {config_path}\n"
        f"Restart Claude Code in this project to load it."
    )


def _unconfigure_mcp(
    name: str,
    *,
    config_path: Optional[Path] = None,
    project_root: Optional[Path] = None,
) -> bool:
    """Remove the named MCP server entry. Returns True if one was removed."""
    config_path = config_path or (Path.home() / ".claude.json")
    if not config_path.exists():
        return False
    data, err = _load_claude_json(config_path)
    if err:
        return False

    key = str((project_root or _project_root()).resolve())
    servers = data.get("projects", {}).get(key, {}).get("mcpServers", {})
    if not isinstance(servers, dict) or name not in servers:
        return False

    del servers[name]
    config_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return True


def _load_claude_json(config_path: Path) -> Tuple[Dict[str, Any], Optional[str]]:
    """Load ``~/.claude.json`` (``{}`` if absent). Returns (data, error)."""
    if not config_path.exists():
        return {}, None
    try:
        loaded = json.loads(config_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        return {}, f"Could not parse {config_path} ({exc}); leaving it untouched"
    if not isinstance(loaded, dict):
        return {}, f"{config_path} is not a JSON object; leaving it untouched"
    return loaded, None
