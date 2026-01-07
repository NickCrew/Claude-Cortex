"""Post-install helpers for CLI integrations, docs, and packaging."""

from __future__ import annotations

import os
import shlex
import shutil
import subprocess
import sys
import sysconfig
from pathlib import Path
from typing import List, Optional, Tuple

from . import completions
from . import shell_integration
from .core.base import _resolve_cortex_root

PACKAGE_NAME = "claude-cortex"
DOC_FILES = [
    "architecture-diagrams.md",
    "quick-reference.md",
    "DIAGRAMS_README.md",
    "VISUAL_SUMMARY.txt",
    "README.md",
]


def _find_repo_root(start: Path) -> Optional[Path]:
    for parent in (start, *start.parents):
        if (parent / "pyproject.toml").is_file():
            return parent
    return None


def _find_docs_source() -> Optional[Path]:
    start = Path(__file__).resolve()
    repo_root = _find_repo_root(start)
    candidates: List[Path] = []
    if repo_root:
        candidates.append(repo_root / "docs" / "reference" / "architecture")
    data_docs = Path(sysconfig.get_path("data")) / "share" / PACKAGE_NAME / "docs"
    candidates.append(data_docs)

    for candidate in candidates:
        if candidate.is_dir() and any((candidate / name).exists() for name in DOC_FILES):
            return candidate
    return None


def _find_manpage_source() -> Optional[Path]:
    start = Path(__file__).resolve()
    repo_root = _find_repo_root(start)
    if repo_root:
        repo_docs = repo_root / "docs" / "reference"
        if repo_docs.is_dir() and any(repo_docs.glob("*.1")):
            return repo_docs
    data_man = Path(sysconfig.get_path("data")) / "share" / "man" / "man1"
    if data_man.is_dir() and any(data_man.glob("*.1")):
        return data_man
    return None


def _default_completion_path(shell: str, system: bool) -> Path:
    home = Path.home()
    if shell == "bash":
        return (
            Path("/etc/bash_completion.d/cortex")
            if system
            else home / ".bash_completion.d" / "cortex"
        )
    if shell == "zsh":
        return (
            Path("/usr/local/share/zsh/site-functions/_cortex")
            if system
            else home / ".zsh" / "completions" / "_cortex"
        )
    if shell == "fish":
        return (
            Path("/usr/local/share/fish/vendor_completions.d/cortex.fish")
            if system
            else home / ".config" / "fish" / "completions" / "cortex.fish"
        )
    raise ValueError(f"Unsupported shell: {shell}")


def _default_man_dir(system: bool) -> Path:
    if system:
        return Path("/usr/local/share/man/man1")
    data_home = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    return data_home / "man" / "man1"


def _build_completion_instructions(shell: str, target: Path) -> List[str]:
    if shell == "bash":
        return [
            "Add to ~/.bashrc:",
            f"  if [ -f {target} ]; then",
            f"    . {target}",
            "  fi",
            "Then reload: source ~/.bashrc",
        ]
    if shell == "zsh":
        return [
            "Add to ~/.zshrc (before compinit):",
            f"  fpath=({target.parent} $fpath)",
            "  autoload -Uz compinit && compinit",
            "Then reload: exec zsh",
        ]
    if shell == "fish":
        return [
            "Fish will load completions automatically on next shell start.",
            f"Reload now: source {target}",
        ]
    return ["Reload your shell to enable completions."]


def install_completions(
    shell: Optional[str] = None,
    target_path: Optional[Path] = None,
    system: bool = False,
    force: bool = False,
    dry_run: bool = False,
) -> Tuple[int, str]:
    """Install shell completion script for cortex."""
    try:
        if shell is None:
            shell, _ = shell_integration.detect_shell()
        shell = shell.lower()
    except RuntimeError as exc:
        return 1, str(exc)

    if shell not in ("bash", "zsh", "fish"):
        return 1, f"Unsupported shell: {shell}. Supported: bash, zsh, fish"

    target = target_path or _default_completion_path(shell, system)
    if target.exists() and not force:
        return 1, (
            f"Completion file already exists at {target}. "
            "Use --force to overwrite."
        )

    script = completions.get_completion_script(shell)
    if dry_run:
        message = [
            f"Would install {shell} completions to: {target}",
            "Run without --dry-run to write the file.",
        ]
        return 0, "\n".join(message)

    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(script)
    except Exception as exc:
        return 1, f"Failed to write completion file: {exc}"

    message = [
        f"✓ Installed {shell} completions to: {target}",
        "",
        *(_build_completion_instructions(shell, target)),
    ]
    return 0, "\n".join(message)


def install_manpages(
    target_dir: Optional[Path] = None,
    system: bool = False,
    dry_run: bool = False,
) -> Tuple[int, str]:
    """Install manpages to the specified man1 directory."""
    source_dir = _find_manpage_source()
    if source_dir is None:
        return 1, "Manpage sources not found."

    manpages = sorted(source_dir.glob("*.1"))
    if not manpages:
        return 1, f"No manpages found in {source_dir}"

    target = target_dir or _default_man_dir(system)
    if dry_run:
        files = "\n".join(f"  - {page.name}" for page in manpages)
        return 0, (
            f"Would install manpages to: {target}\n"
            f"From: {source_dir}\n"
            f"{files}"
        )

    try:
        target.mkdir(parents=True, exist_ok=True)
        for page in manpages:
            destination = target / page.name
            if destination.resolve() == page.resolve():
                continue
            shutil.copy2(page, destination)
    except Exception as exc:
        return 1, f"Failed to install manpages: {exc}"

    man_root = target.parent
    message = [
        f"✓ Installed {len(manpages)} manpage(s) to: {target}",
        "Try: man cortex",
        f"Ensure MANPATH includes: {man_root}",
    ]
    return 0, "\n".join(message)


def install_docs(
    target_dir: Optional[Path] = None, dry_run: bool = False
) -> Tuple[int, str]:
    """Install architecture docs to ~/.cortex/docs (or target)."""
    source_dir = _find_docs_source()
    if source_dir is None:
        return 1, "Architecture docs source not found."

    target = target_dir or (_resolve_cortex_root() / "docs")
    available_files = [name for name in DOC_FILES if (source_dir / name).exists()]
    if not available_files:
        return 1, f"No architecture docs found in {source_dir}"

    if dry_run:
        files = "\n".join(f"  - {name}" for name in available_files)
        return 0, (
            f"Would install architecture docs to: {target}\n"
            f"From: {source_dir}\n"
            f"{files}"
        )

    try:
        target.mkdir(parents=True, exist_ok=True)
        for name in available_files:
            source_file = source_dir / name
            destination = target / name
            if destination.resolve() == source_file.resolve():
                continue
            shutil.copy2(source_file, destination)
    except Exception as exc:
        return 1, f"Failed to install docs: {exc}"

    message = [
        f"✓ Installed architecture docs to: {target}",
        "Quick view:",
        f"  cat {target / 'VISUAL_SUMMARY.txt'}",
    ]
    return 0, "\n".join(message)


def install_post(
    shell: Optional[str] = None,
    completion_path: Optional[Path] = None,
    manpath: Optional[Path] = None,
    docs_target: Optional[Path] = None,
    system: bool = False,
    force: bool = False,
    dry_run: bool = False,
) -> Tuple[int, str]:
    """Run all post-install steps (completions, manpages, docs)."""
    results = []
    exit_code = 0

    code, message = install_completions(
        shell=shell,
        target_path=completion_path,
        system=system,
        force=force,
        dry_run=dry_run,
    )
    results.append(message)
    exit_code = max(exit_code, code)

    code, message = install_manpages(
        target_dir=manpath,
        system=system,
        dry_run=dry_run,
    )
    results.append(message)
    exit_code = max(exit_code, code)

    code, message = install_docs(
        target_dir=docs_target,
        dry_run=dry_run,
    )
    results.append(message)
    exit_code = max(exit_code, code)

    return exit_code, "\n\n".join(results)


def install_package(
    manager: str,
    path: Optional[Path],
    name: str,
    editable: bool,
    dev: bool,
    upgrade: bool,
    dry_run: bool,
) -> Tuple[int, str]:
    """Install the package using pip/uv/pipx."""
    manager = manager.lower()
    if manager not in ("pip", "uv", "pipx"):
        return 1, f"Unsupported package manager: {manager}"

    if path is not None and not path.exists():
        return 1, f"Install path not found: {path}"

    package_spec = str(path or name)
    if dev:
        package_spec = f"{package_spec}[dev]"

    cmd: List[str]
    if manager == "pip":
        cmd = [sys.executable, "-m", "pip", "install"]
        if upgrade:
            cmd.append("--upgrade")
        if editable:
            cmd.append("-e")
        cmd.append(package_spec)
    elif manager == "uv":
        if shutil.which("uv") is None:
            return 1, "uv is not installed. Install uv first or use --manager pip."
        cmd = ["uv", "pip", "install"]
        if upgrade:
            cmd.append("--upgrade")
        if editable:
            cmd.append("-e")
        cmd.append(package_spec)
    else:
        if shutil.which("pipx") is None:
            return 1, "pipx is not installed. Install pipx first or use --manager pip."
        cmd = ["pipx", "install"]
        if upgrade:
            cmd.append("--force")
        if editable:
            cmd.append("--editable")
        cmd.append(package_spec)

    if dry_run:
        return 0, f"Would run: {shlex.join(cmd)}"

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        combined = (result.stdout + "\n" + result.stderr).strip()
        return result.returncode, combined or "Package installation failed."

    return 0, f"✓ Installed via {manager}: {shlex.join(cmd)}"
