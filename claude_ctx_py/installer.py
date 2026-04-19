"""Post-install helpers for CLI integrations, docs, and packaging."""

from __future__ import annotations

import json
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
from .core.asset_discovery import _SETTINGS_RELATIVE_PATHS

PACKAGE_NAME = "claude-cortex"
DOC_FILES = [
    "architecture-diagrams.md",
    "quick-reference.md",
    "DIAGRAMS_README.md",
    "VISUAL_SUMMARY.txt",
    "README.md",
]


def _find_cortex_root() -> Optional[Path]:
    """Find the cortex package root directory.

    Searches in order:
    1. Check if running from within the package directory (development)
    2. Check Claude's installed plugins registry (legacy)
    3. Check common installation locations
    """
    # 1. Check if running from within plugin (development or editable install)
    here = Path(__file__).resolve()
    for parent in [here.parent, *here.parents]:
        if (parent / ".claude-plugin" / "plugin.json").is_file():
            return parent
        # Also check for agent/skill directories as fallback
        if (
            (parent / "agents").is_dir()
            and (parent / "skills").is_dir()
            and (parent / "rules").is_dir()
        ):
            return parent

    # 2. Check Claude's installed plugins registry
    registry = Path.home() / ".claude" / "plugins" / "installed_plugins.json"
    if registry.exists():
        try:
            data = json.loads(registry.read_text(encoding="utf-8"))
            plugins = data.get("plugins", {})
            for key, entries in plugins.items():
                if "cortex" in key.lower():
                    for entry in entries if isinstance(entries, list) else [entries]:
                        if isinstance(entry, dict):
                            path_str = entry.get("installPath", "")
                            if path_str:
                                path = Path(path_str).expanduser()
                                if path.exists():
                                    return path
        except (json.JSONDecodeError, KeyError, TypeError):
            pass

    # 3. Check common locations
    candidates = [
        Path.home() / ".claude" / "plugins" / "claude-cortex",
    ]
    for candidate in candidates:
        if candidate.exists() and (candidate / "agents").is_dir():
            return candidate

    # 4. Fall back to bundled assets root
    return _resolve_cortex_root()


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
        if candidate.is_dir() and any(
            (candidate / name).exists() for name in DOC_FILES
        ):
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
            else home / ".cache" / "zsh" / "completions" / "_cortex"
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
            f"Completion file already exists at {target}. " "Use --force to overwrite."
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
            f"Would install manpages to: {target}\n" f"From: {source_dir}\n" f"{files}"
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
    """Install architecture docs to ~/.claude/docs (or target)."""
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


# Directories to copy from bundled assets to ~/.claude
BOOTSTRAP_DIRS = ["rules"]


def bootstrap(
    target_dir: Optional[Path] = None,
    force: bool = False,
    dry_run: bool = False,
    link_rules: bool = False,
) -> Tuple[int, str]:
    """Bootstrap ~/.claude with bundled assets and default configuration.

    Creates the .claude directory structure and copies rules and templates
    from the bundled cortex package assets.

    Args:
        target_dir: Target directory (default: ~/.claude)
        force: Overwrite existing directories
        dry_run: Show what would be done without writing files
        link_rules: Also create symlinks in ~/.claude/rules/cortex/
    """
    assets_root = _resolve_cortex_root()
    if assets_root is None:
        return 1, (
            "Bundled assets not found. This may indicate a broken installation.\n"
            "Try reinstalling: pipx install --force claude-cortex"
        )

    claude_home = target_dir or (Path.home() / ".claude")
    results: List[str] = []
    copied_dirs: List[str] = []

    if dry_run:
        lines = [
            f"Would bootstrap cortex home at: {claude_home}",
            f"Using assets from: {assets_root}",
            "",
            "Directories to copy:",
        ]
        for dir_name in BOOTSTRAP_DIRS:
            source = assets_root / dir_name
            if source.is_dir():
                lines.append(f"  - {dir_name}/ ({len(list(source.glob('*')))} files)")
        return 0, "\n".join(lines)

    # Create cortex home directory
    try:
        claude_home.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        return 1, f"Failed to create {claude_home}: {exc}"

    # Copy directories from assets
    for dir_name in BOOTSTRAP_DIRS:
        source = assets_root / dir_name
        target = claude_home / dir_name
        if not source.is_dir():
            continue
        if target.exists() and not force:
            results.append(f"  Skipped {dir_name}/ (exists, use --force to overwrite)")
            continue
        try:
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(source, target)
            copied_dirs.append(dir_name)
            results.append(f"  ✓ Copied {dir_name}/")
        except OSError as exc:
            results.append(f"  ✗ Failed to copy {dir_name}/: {exc}")

    # Link rules into ~/.claude/rules/cortex/ if requested
    link_results: List[str] = []
    if link_rules:
        from .core.rules import sync_rule_symlinks, DEFAULT_RULES_SUBDIR

        rules_root = claude_home
        active_rules = [p.stem for p in (claude_home / "rules").glob("*.md")]
        if dry_run:
            link_results.append(
                f"Would symlink {len(active_rules)} rules to {DEFAULT_RULES_SUBDIR}"
            )
        else:
            _, link_messages = sync_rule_symlinks(
                rules_root=rules_root,
                active_rules=active_rules,
                target_dir=DEFAULT_RULES_SUBDIR,
            )
            link_results.extend(link_messages)
            link_results.append(f"  ✓ Linked rules to {DEFAULT_RULES_SUBDIR}")

    summary = [
        f"✓ Bootstrapped cortex at: {claude_home}",
        f"  Assets from: {assets_root}",
        "",
        "Results:",
        *results,
    ]
    if link_results:
        summary.extend(["", "Rule symlinks:", *link_results])
    summary.extend(
        [
            "",
            "Next steps:",
            "  1. Run 'claude' directly - rules are auto-discovered",
            "  2. Run 'cortex agent list' to see available agents",
        ]
    )
    return 0, "\n".join(summary)


def install_post(
    shell: Optional[str] = None,
    completion_path: Optional[Path] = None,
    manpath: Optional[Path] = None,
    system: bool = False,
    force: bool = False,
    dry_run: bool = False,
) -> Tuple[int, str]:
    """Run post-install steps (completions and manpages)."""
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

    return exit_code, "\n\n".join(results)


# Directories to symlink into ~/.claude
LINK_DIRS = ["agents", "skills", "rules", "schemas"]


def _link_commands_from_skills(
    skills_dir: Path,
    commands_dir: Path,
    force: bool = False,
    dry_run: bool = False,
) -> List[str]:
    """Generate commands/ symlinks from skills/ directory.

    Creates symlinks like:
        commands/collaboration/pre-mortem.md -> skills/collaboration/pre_mortem/SKILL.md
        commands/ctx/canvas-design.md -> skills/canvas-design/SKILL.md

    Args:
        skills_dir: Source skills directory
        commands_dir: Target commands directory
        force: Remove existing commands_dir before linking
        dry_run: Show what would be done

    Returns:
        List of result messages
    """
    import re

    results: List[str] = []

    if not skills_dir.is_dir():
        return [f"  - commands/ (skills directory not found)"]

    # Collect all SKILL.md files
    skill_files = list(skills_dir.rglob("SKILL.md"))
    if not skill_files:
        return [f"  - commands/ (no skills found)"]

    if dry_run:
        return [f"  commands/ (would create {len(skill_files)} symlinks from skills)"]

    # Handle existing commands dir
    if commands_dir.exists() or commands_dir.is_symlink():
        if not force:
            return [f"  - commands/ (exists, use --force to replace)"]
        try:
            if commands_dir.is_symlink():
                commands_dir.unlink()
            else:
                shutil.rmtree(commands_dir)
        except OSError as exc:
            return [f"  ✗ commands/ (failed to remove: {exc})"]

    # Create commands directory
    try:
        commands_dir.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        return [f"  ✗ commands/ (failed to create: {exc})"]

    def slugify(text: str) -> str:
        slug = text.lower().replace("_", "-")
        slug = re.sub(r"[^a-z0-9-]", "", slug)
        slug = re.sub(r"-+", "-", slug)
        return slug.strip("-")

    created = 0
    for skill_path in skill_files:
        try:
            relative = skill_path.relative_to(skills_dir)
        except ValueError:
            continue

        parts = relative.parts[:-1]  # Exclude SKILL.md

        if len(parts) == 0:
            continue
        elif len(parts) == 1:
            # Flat skill: skills/foo/SKILL.md -> commands/ctx/foo.md
            namespace = "ctx"
            slug = slugify(parts[0])
        else:
            # Nested skill: skills/collaboration/pre_mortem/SKILL.md -> commands/collaboration/pre-mortem.md
            namespace = slugify(parts[0])
            slug = slugify(parts[-1])

        if not slug:
            continue

        # Create namespace dir
        namespace_dir = commands_dir / namespace
        namespace_dir.mkdir(parents=True, exist_ok=True)

        # Create symlink
        link_path = namespace_dir / f"{slug}.md"
        if link_path.exists() or link_path.is_symlink():
            if force:
                link_path.unlink()
            else:
                continue

        try:
            link_path.symlink_to(skill_path.resolve())
            created += 1
        except OSError:
            pass

    results.append(f"  ✓ commands/ ({created} symlinks from skills)")
    return results


def _migrate_dir_symlink(dst: Path, src: Path, category: str) -> List[str]:
    """Migrate a directory-level symlink to per-file symlinks.

    If ``dst`` is a symlink pointing to ``src`` (or any directory), replace it
    with a real directory containing per-file symlinks for each asset inside.

    Returns a list of human-readable result messages (empty when no migration).
    """
    if not dst.is_symlink():
        return []

    results: List[str] = []

    # Collect assets from the resolved source before removing the link
    resolved = dst.resolve()
    assets: List[Path] = []
    if category == "skills":
        # Skills: each subdirectory containing SKILL.md
        if resolved.is_dir():
            assets = [p.parent for p in resolved.rglob("SKILL.md")]
    else:
        # agents / rules: each *.md file (flat + subdirs for rules)
        if resolved.is_dir():
            assets = list(resolved.rglob("*.md"))

    # Remove the directory symlink and create a real directory
    try:
        dst.unlink()
        dst.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        return [f"  ✗ {category}/ migration failed: {exc}"]

    # Create per-file/dir symlinks
    for asset in assets:
        try:
            relative = asset.relative_to(resolved)
        except ValueError:
            continue

        link_path = dst / relative
        if category == "skills":
            # Symlink each skill subdirectory
            link_path.parent.mkdir(parents=True, exist_ok=True)
            if not link_path.exists() and not link_path.is_symlink():
                link_path.symlink_to(asset)
        else:
            # Symlink each .md file, preserving subdirectory structure
            link_path.parent.mkdir(parents=True, exist_ok=True)
            if not link_path.exists() and not link_path.is_symlink():
                link_path.symlink_to(asset)

    results.append(
        f"  ✓ {category}/ migrated from dir symlink → {len(assets)} per-file symlinks"
    )
    return results


def _link_files_into_dir(
    src: Path, dst: Path, category: str, force: bool = False
) -> List[str]:
    """Create per-file symlinks from ``src/`` into ``dst/``.

    - ``agents`` and ``rules``: iterate ``*.md`` files (and subdirs for rules)
    - ``skills``: iterate subdirectories containing ``SKILL.md``
    """
    results: List[str] = []
    created = 0
    skipped = 0

    if category == "skills":
        for skill_dir in sorted(src.iterdir()):
            if not skill_dir.is_dir():
                continue
            if not (skill_dir / "SKILL.md").exists():
                continue
            link_path = dst / skill_dir.name
            if link_path.is_symlink():
                if link_path.resolve() == skill_dir.resolve():
                    skipped += 1
                    continue
                if force:
                    link_path.unlink()
                else:
                    skipped += 1
                    continue
            elif link_path.exists():
                if not force:
                    skipped += 1
                    continue
                shutil.rmtree(link_path)
            try:
                link_path.symlink_to(skill_dir)
                created += 1
            except OSError:
                pass
    elif category == "schemas":
        # Flat directory of schema files. Symlink each so that updates to the
        # repo copies propagate automatically — schemas are shipped artifacts,
        # not user-customized settings.
        for schema_file in sorted(src.iterdir()):
            if not schema_file.is_file():
                continue
            if schema_file.suffix.lower() not in {".json", ".yaml", ".yml"}:
                continue
            link_path = dst / schema_file.name
            if link_path.is_symlink():
                if link_path.resolve() == schema_file.resolve():
                    skipped += 1
                    continue
                if force:
                    link_path.unlink()
                else:
                    skipped += 1
                    continue
            elif link_path.exists():
                # Plain copy (legacy install) — replace with symlink on --force,
                # otherwise skip so we don't clobber a user's local override.
                if not force:
                    skipped += 1
                    continue
                link_path.unlink()
            link_path.parent.mkdir(parents=True, exist_ok=True)
            try:
                link_path.symlink_to(schema_file)
                created += 1
            except OSError:
                pass
    else:
        # agents / rules: *.md files, recursing into subdirectories for rules
        for md_file in sorted(src.rglob("*.md")):
            try:
                relative = md_file.relative_to(src)
            except ValueError:
                continue
            link_path = dst / relative
            if link_path.is_symlink():
                if link_path.resolve() == md_file.resolve():
                    skipped += 1
                    continue
                if force:
                    link_path.unlink()
                else:
                    skipped += 1
                    continue
            elif link_path.exists():
                if not force:
                    skipped += 1
                    continue
                link_path.unlink()
            link_path.parent.mkdir(parents=True, exist_ok=True)
            try:
                link_path.symlink_to(md_file)
                created += 1
            except OSError:
                pass

    status = f"{created} linked"
    if skipped:
        status += f", {skipped} unchanged"
    results.append(f"  ✓ {category}/ ({status})")
    return results


def _copy_settings_files(
    source: Path,
    target: Path,
    force: bool = False,
    dry_run: bool = False,
) -> List[str]:
    """Copy bundled settings/config files from cortex_root to target.

    Copies (not symlinks) so that the originals in cortex_root are preserved
    for restoration via --force.

    Args:
        source: Cortex root containing bundled assets
        target: Target directory (e.g. ~/.claude)
        force: Overwrite existing files
        dry_run: Show what would be done
    """
    results: List[str] = []
    found = [rp for rp in _SETTINGS_RELATIVE_PATHS if (source / rp).exists()]

    if not found:
        return []

    if dry_run:
        return [f"  settings ({len(found)} config files)"]

    copied = 0
    skipped = 0
    for rel_path in found:
        src_file = source / rel_path
        dst_file = target / rel_path
        if dst_file.exists() and not force:
            skipped += 1
            continue
        try:
            dst_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_file, dst_file)
            copied += 1
        except OSError:
            pass

    status = f"{copied} copied"
    if skipped:
        status += f", {skipped} unchanged"
    results.append(f"  ✓ settings ({status})")
    return results


def link_content(
    source_dir: Optional[Path] = None,
    target_dir: Optional[Path] = None,
    force: bool = False,
    dry_run: bool = False,
) -> Tuple[int, str]:
    """Symlink bundled content (agents, skills, rules) into ~/.claude.

    Creates per-file symlinks for each asset rather than directory-level
    symlinks, allowing individual assets to be toggled on/off.  Also copies
    bundled settings/config files (YAML schemas, activation maps, etc.) so
    that runtime code can read them from claude_dir.  Originals are preserved
    in cortex_root for restoration via --force.

    Args:
        source_dir: Source directory with content (default: auto-detect plugin root)
        target_dir: Target directory (default: ~/.claude)
        force: Remove existing symlinks/directories before linking
        dry_run: Show what would be done without making changes
    """
    # Find source
    source = source_dir or _find_cortex_root()
    if source is None:
        return 1, (
            "Could not find cortex content directory.\n"
            "Set CLAUDE_PLUGIN_ROOT or run from within the cortex repo."
        )

    # Verify source has content
    found_dirs = [d for d in LINK_DIRS if (source / d).is_dir()]
    if not found_dirs:
        return 1, f"No content directories found in {source}"

    # Target is always ~/.claude (global scope) for install link
    target = target_dir or (Path.home() / ".claude")

    if dry_run:
        lines = [
            f"Would link content from: {source}",
            f"To: {target}",
            "",
            "Directories to link (per-file symlinks):",
        ]
        for dir_name in found_dirs:
            src = source / dir_name
            count = len(list(src.glob("*")))
            lines.append(f"  {dir_name}/ ({count} items)")
        settings_dry = _copy_settings_files(source, target, force=force, dry_run=True)
        if settings_dry:
            lines.append("")
            lines.append("Config files to copy:")
            lines.extend(settings_dry)
        return 0, "\n".join(lines)

    # Create target if needed
    try:
        target.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        return 1, f"Failed to create {target}: {exc}"

    results: List[str] = []
    for dir_name in found_dirs:
        src = source / dir_name
        dst = target / dir_name

        # Migrate directory-level symlinks to per-file symlinks
        migration_msgs = _migrate_dir_symlink(dst, src, dir_name)
        if migration_msgs:
            results.extend(migration_msgs)

        # Ensure dst is a real directory
        if not dst.exists():
            try:
                dst.mkdir(parents=True, exist_ok=True)
            except OSError as exc:
                results.append(f"  ✗ {dir_name}/ (failed to create: {exc})")
                continue

        # Create per-file symlinks
        link_results = _link_files_into_dir(src, dst, dir_name, force=force)
        results.extend(link_results)

    # Copy bundled settings/config files
    settings_results = _copy_settings_files(source, target, force=force)
    if settings_results:
        results.extend(settings_results)

    # Generate commands/ from skills/
    skills_dir = target / "skills"
    commands_dir = target / "commands"
    cmd_results = _link_commands_from_skills(
        skills_dir, commands_dir, force=force, dry_run=dry_run
    )
    results.extend(cmd_results)

    summary = [
        f"Linked content to: {target}",
        f"Source: {source}",
        "",
        *results,
    ]
    return 0, "\n".join(summary)


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
