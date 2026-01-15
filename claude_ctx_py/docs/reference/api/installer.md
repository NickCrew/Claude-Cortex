# Installer Module API Reference

**Module:** `claude_ctx_py.installer`

The installer module provides post-install helpers for CLI integrations, documentation, and packaging. It handles installation of shell completions, manpages, and architecture documentation.

## Overview

The installer supports three main installation targets:
- **Shell Completions**: Bash, Zsh, and Fish completion scripts
- **Manpages**: Unix manual pages for CLI commands
- **Documentation**: Architecture diagrams and reference docs

## Functions

### install_completions

```python
def install_completions(
    shell: Optional[str] = None,
    target_path: Optional[Path] = None,
    system: bool = False,
    force: bool = False,
    dry_run: bool = False,
) -> Tuple[int, str]
```

Install shell completion script for cortex.

**Parameters:**
- `shell` (str, optional): Shell type ("bash", "zsh", "fish"). Auto-detected if None.
- `target_path` (Path, optional): Custom installation path
- `system` (bool): Install to system location (requires elevated privileges)
- `force` (bool): Overwrite existing completion file
- `dry_run` (bool): Preview without making changes

**Returns:**
- `Tuple[int, str]`: (exit_code, message)

**Default Paths:**

| Shell | User Path | System Path |
|-------|-----------|-------------|
| Bash | `~/.bash_completion.d/cortex` | `/etc/bash_completion.d/cortex` |
| Zsh | `~/.zsh/completions/_cortex` | `/usr/local/share/zsh/site-functions/_cortex` |
| Fish | `~/.config/fish/completions/cortex.fish` | `/usr/local/share/fish/vendor_completions.d/cortex.fish` |

**Example:**
```python
# Install for current shell
code, msg = install_completions()

# Install for specific shell with dry run
code, msg = install_completions(shell="zsh", dry_run=True)

# Force reinstall
code, msg = install_completions(force=True)
```

---

### install_manpages

```python
def install_manpages(
    target_dir: Optional[Path] = None,
    system: bool = False,
    dry_run: bool = False,
) -> Tuple[int, str]
```

Install manpages to the specified man1 directory.

**Parameters:**
- `target_dir` (Path, optional): Custom man1 directory
- `system` (bool): Install to system location (`/usr/local/share/man/man1`)
- `dry_run` (bool): Preview without making changes

**Returns:**
- `Tuple[int, str]`: (exit_code, message)

**Default Paths:**
- User: `~/.local/share/man/man1`
- System: `/usr/local/share/man/man1`

**Example:**
```python
# Install to default user location
code, msg = install_manpages()

# Preview system installation
code, msg = install_manpages(system=True, dry_run=True)
```

---

### install_docs

```python
def install_docs(
    target_dir: Optional[Path] = None,
    dry_run: bool = False
) -> Tuple[int, str]
```

Install architecture docs to `~/.cortex/docs` (or custom target).

**Parameters:**
- `target_dir` (Path, optional): Custom installation directory
- `dry_run` (bool): Preview without making changes

**Returns:**
- `Tuple[int, str]`: (exit_code, message)

**Installed Files:**
- `architecture-diagrams.md`
- `quick-reference.md`
- `DIAGRAMS_README.md`
- `VISUAL_SUMMARY.txt`
- `README.md`

**Example:**
```python
# Install to default location (~/.cortex/docs)
code, msg = install_docs()

# Install to custom location
code, msg = install_docs(target_dir=Path("~/my-docs"))
```

---

### install_post

```python
def install_post(
    shell: Optional[str] = None,
    completion_path: Optional[Path] = None,
    manpath: Optional[Path] = None,
    docs_target: Optional[Path] = None,
    system: bool = False,
    force: bool = False,
    dry_run: bool = False,
) -> Tuple[int, str]
```

Run all post-install steps (completions, manpages, docs).

**Parameters:**
- `shell` (str, optional): Shell type for completions
- `completion_path` (Path, optional): Custom completion path
- `manpath` (Path, optional): Custom manpage directory
- `docs_target` (Path, optional): Custom docs directory
- `system` (bool): Install to system locations
- `force` (bool): Overwrite existing files
- `dry_run` (bool): Preview without making changes

**Returns:**
- `Tuple[int, str]`: (max_exit_code, combined_messages)

**Example:**
```python
# Full post-install
code, msg = install_post()

# Preview all installations
code, msg = install_post(dry_run=True)

# System-wide installation
code, msg = install_post(system=True)
```

---

### install_package

```python
def install_package(
    manager: str,
    path: Optional[Path],
    name: str,
    editable: bool,
    dev: bool,
    upgrade: bool,
    dry_run: bool,
) -> Tuple[int, str]
```

Install the package using pip, uv, or pipx.

**Parameters:**
- `manager` (str): Package manager ("pip", "uv", "pipx")
- `path` (Path, optional): Local path for installation
- `name` (str): Package name (used if path is None)
- `editable` (bool): Install in editable/development mode
- `dev` (bool): Include development dependencies
- `upgrade` (bool): Upgrade if already installed
- `dry_run` (bool): Preview without installing

**Returns:**
- `Tuple[int, str]`: (exit_code, message)

**Example:**
```python
# Install from local path
code, msg = install_package(
    manager="pip",
    path=Path("./cortex-plugin"),
    name="claude-cortex",
    editable=True,
    dev=True,
    upgrade=False,
    dry_run=False
)

# Install from PyPI
code, msg = install_package(
    manager="pipx",
    path=None,
    name="claude-cortex",
    editable=False,
    dev=False,
    upgrade=True,
    dry_run=False
)
```

## Helper Functions

### _find_repo_root

```python
def _find_repo_root(start: Path) -> Optional[Path]
```

Find the repository root by looking for `pyproject.toml`.

### _find_docs_source

```python
def _find_docs_source() -> Optional[Path]
```

Find the source directory for architecture documentation.

### _find_manpage_source

```python
def _find_manpage_source() -> Optional[Path]
```

Find the source directory for manpage files.

## CLI Integration

```bash
# Install shell completions
cortex install completions --shell zsh

# Install manpages
cortex install manpages

# Install documentation
cortex install docs

# Run all post-install steps
cortex install post

# Install package
cortex install package --manager pip --editable

# Dry run to preview
cortex install post --dry-run
```

## Constants

```python
PACKAGE_NAME = "claude-cortex"

DOC_FILES = [
    "architecture-diagrams.md",
    "quick-reference.md",
    "DIAGRAMS_README.md",
    "VISUAL_SUMMARY.txt",
    "README.md",
]
```

## Dependencies

The installer module uses:
- `claude_ctx_py.completions` - Shell completion script generation
- `claude_ctx_py.shell_integration` - Shell detection utilities

## See Also

- [Shell Integration Module](/reference/api/shell-integration/) - Shell detection and alias management
- [Completions Module](/reference/api/completions/) - Completion script generation
