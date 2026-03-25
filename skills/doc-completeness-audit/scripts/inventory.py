#!/usr/bin/env python3
"""Extract documentable surface area from a codebase.

Scans source files for signals that indicate something a user or developer
might need documentation for: environment variables, CLI commands, config
keys, public exports, HTTP endpoints, and error types.

Output is a JSON inventory that can be diffed against existing documentation
to find coverage gaps.

Usage:
    python3 inventory.py [--root PATH] [--json] [--detectors LIST]

Detectors:
    env_vars        Environment variable references
    cli_commands    CLI framework commands and flags
    config_keys     Configuration file key access
    http_endpoints  HTTP route definitions
    public_exports  Public module/package exports
    error_types     Custom error/exception definitions

    Default: all detectors enabled.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class InventoryItem:
    """A single documentable item found in the codebase."""
    topic: str
    category: str  # env_var, cli_command, cli_flag, config_key, endpoint, export, error_type
    source_file: str
    source_line: int
    detail: str = ""  # extra context (default value, type, HTTP method, etc.)
    audience: str = "user"  # user, developer, operator


@dataclass
class Inventory:
    """Complete inventory of documentable surface area."""
    root: str
    items: List[InventoryItem] = field(default_factory=list)
    detectors_run: List[str] = field(default_factory=list)
    files_scanned: int = 0

    def add(self, item: InventoryItem) -> None:
        self.items.append(item)

    def summary(self) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for item in self.items:
            counts[item.category] = counts.get(item.category, 0) + 1
        return counts


# ---------------------------------------------------------------------------
# File discovery
# ---------------------------------------------------------------------------

# Extensions to scan per language family
SOURCE_EXTENSIONS: Dict[str, List[str]] = {
    "python": [".py"],
    "javascript": [".js", ".mjs", ".cjs"],
    "typescript": [".ts", ".tsx"],
    "rust": [".rs"],
    "go": [".go"],
    "ruby": [".rb"],
    "java": [".java", ".kt"],
    "shell": [".sh", ".bash", ".zsh"],
}

# Directories to skip
SKIP_DIRS: Set[str] = {
    "node_modules", ".git", "__pycache__", ".tox", ".venv", "venv",
    "dist", "build", ".eggs", "*.egg-info", "target", "vendor",
    ".mypy_cache", ".pytest_cache", ".ruff_cache", "htmlcov",
    "_site", ".jekyll-cache", ".next", ".nuxt",
}

ALL_EXTENSIONS: Set[str] = set()
for exts in SOURCE_EXTENSIONS.values():
    ALL_EXTENSIONS.update(exts)


def discover_files(root: Path) -> List[Path]:
    """Find source files, skipping common non-source directories."""
    files: List[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        # Prune skipped directories in-place
        dirnames[:] = [
            d for d in dirnames
            if d not in SKIP_DIRS and not d.endswith(".egg-info")
        ]
        for fname in filenames:
            if any(fname.endswith(ext) for ext in ALL_EXTENSIONS):
                files.append(Path(dirpath) / fname)
    return sorted(files)


def read_file_lines(path: Path) -> List[str]:
    """Read file lines, returning empty list on decode errors."""
    try:
        return path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return []


# ---------------------------------------------------------------------------
# Detectors
# ---------------------------------------------------------------------------

# -- Environment variables --------------------------------------------------

ENV_PATTERNS = [
    # Python
    (re.compile(r'''os\.environ\.get\(\s*["']([A-Z_][A-Z0-9_]+)["']'''), None),
    (re.compile(r'''os\.environ\[["']([A-Z_][A-Z0-9_]+)["']\]'''), None),
    (re.compile(r'''os\.getenv\(\s*["']([A-Z_][A-Z0-9_]+)["']'''), None),
    # JavaScript / TypeScript
    (re.compile(r'''process\.env\.([A-Z_][A-Z0-9_]+)'''), None),
    (re.compile(r'''process\.env\[["']([A-Z_][A-Z0-9_]+)["']\]'''), None),
    # Rust
    (re.compile(r'''env::var\(\s*["']([A-Z_][A-Z0-9_]+)["']'''), None),
    (re.compile(r'''env::var_os\(\s*["']([A-Z_][A-Z0-9_]+)["']'''), None),
    # Go
    (re.compile(r'''os\.Getenv\(\s*["']([A-Z_][A-Z0-9_]+)["']'''), None),
    (re.compile(r'''os\.LookupEnv\(\s*["']([A-Z_][A-Z0-9_]+)["']'''), None),
    # Ruby
    (re.compile(r'''ENV\[["']([A-Z_][A-Z0-9_]+)["']\]'''), None),
    # Shell
    (re.compile(r'''\$\{([A-Z_][A-Z0-9_]+)(?::[-=+?])'''), None),
    (re.compile(r'''\$([A-Z_][A-Z0-9_]+)'''), None),
]

# Common env vars that don't need documentation
IGNORE_ENV_VARS: Set[str] = {
    "HOME", "PATH", "USER", "SHELL", "TERM", "LANG", "LC_ALL",
    "PWD", "OLDPWD", "TMPDIR", "TMP", "TEMP", "EDITOR", "VISUAL",
    "HTTP_PROXY", "HTTPS_PROXY", "NO_PROXY", "CI", "DEBUG",
    "NODE_ENV", "PYTHONPATH", "PYTHONDONTWRITEBYTECODE",
    "VIRTUAL_ENV", "CONDA_DEFAULT_ENV",
}


def detect_env_vars(files: List[Path], root: Path, inv: Inventory) -> None:
    """Detect environment variable references."""
    seen: Dict[str, InventoryItem] = {}
    for fpath in files:
        lines = read_file_lines(fpath)
        for lineno, line in enumerate(lines, 1):
            for pattern, _ in ENV_PATTERNS:
                for match in pattern.finditer(line):
                    name = match.group(1)
                    if name in IGNORE_ENV_VARS:
                        continue
                    if name not in seen:
                        # Try to extract default value
                        default = _extract_default(line, name)
                        item = InventoryItem(
                            topic=name,
                            category="env_var",
                            source_file=str(fpath.relative_to(root)),
                            source_line=lineno,
                            detail=f"default: {default}" if default else "",
                            audience="operator",
                        )
                        seen[name] = item
                        inv.add(item)


def _extract_default(line: str, var_name: str) -> Optional[str]:
    """Try to extract a default value from env var access."""
    # Python: os.environ.get("X", "default") or os.getenv("X", "default")
    m = re.search(
        rf'''(?:os\.environ\.get|os\.getenv)\(\s*["']{var_name}["']\s*,\s*(.+?)\)''',
        line,
    )
    if m:
        return m.group(1).strip().strip("\"'")
    # Shell: ${VAR:-default}
    m = re.search(rf'''\$\{{{var_name}:-([^}}]*)\}}''', line)
    if m:
        return m.group(1)
    return None


# -- CLI commands -----------------------------------------------------------

CLI_FRAMEWORK_PATTERNS = {
    # Python argparse
    "argparse": [
        (re.compile(r'''add_parser\(\s*["']([a-z][\w-]*)["']'''), "subcommand"),
        (re.compile(r'''add_argument\(\s*["'](--[\w-]+)["']'''), "flag"),
        (re.compile(r'''add_argument\(\s*["'](-\w)["']'''), "short_flag"),
    ],
    # Python click
    "click": [
        (re.compile(r'''@(?:click\.)?command\(\s*(?:["'](\w[\w-]*)["'])?'''), "command"),
        (re.compile(r'''@(?:click\.)?group\(\s*(?:["'](\w[\w-]*)["'])?'''), "group"),
        (re.compile(r'''@(?:click\.)?option\(\s*["'](--[\w-]+)["']'''), "flag"),
        (re.compile(r'''@(?:click\.)?argument\(\s*["'](\w+)["']'''), "argument"),
    ],
    # Rust clap
    "clap": [
        (re.compile(r'''\.subcommand\(\s*Command::new\(\s*["'](\w[\w-]*)["']'''), "subcommand"),
        (re.compile(r'''Arg::new\(\s*["'](\w[\w-]*)["']'''), "argument"),
        (re.compile(r'''\.long\(\s*["']([\w-]+)["']'''), "flag"),
    ],
    # Go cobra
    "cobra": [
        (re.compile(r'''&cobra\.Command\{[^}]*Use:\s*["'](\w[\w-]*)''', re.DOTALL), "command"),
    ],
    # Node commander
    "commander": [
        (re.compile(r'''\.command\(\s*["'](\w[\w-]*)'''), "command"),
        (re.compile(r'''\.option\(\s*["'](--[\w-]+)'''), "flag"),
    ],
}


def detect_cli_commands(files: List[Path], root: Path, inv: Inventory) -> None:
    """Detect CLI framework commands and flags."""
    seen_commands: Set[str] = set()
    seen_flags: Set[str] = set()

    for fpath in files:
        lines = read_file_lines(fpath)
        content = "\n".join(lines)
        relpath = str(fpath.relative_to(root))

        for framework, patterns in CLI_FRAMEWORK_PATTERNS.items():
            for pattern, kind in patterns:
                for match in pattern.finditer(content):
                    name = match.group(1)
                    if not name:
                        continue

                    # Find the line number
                    pos = match.start()
                    lineno = content[:pos].count("\n") + 1

                    if kind in ("command", "subcommand", "group"):
                        if name not in seen_commands:
                            seen_commands.add(name)
                            # Try to extract help text
                            help_text = _extract_help(content, pos)
                            inv.add(InventoryItem(
                                topic=name,
                                category="cli_command",
                                source_file=relpath,
                                source_line=lineno,
                                detail=help_text or f"framework: {framework}",
                                audience="user",
                            ))
                    elif kind in ("flag", "short_flag"):
                        if name not in seen_flags:
                            seen_flags.add(name)
                            help_text = _extract_help(content, pos)
                            inv.add(InventoryItem(
                                topic=name,
                                category="cli_flag",
                                source_file=relpath,
                                source_line=lineno,
                                detail=help_text or f"framework: {framework}",
                                audience="user",
                            ))
                    elif kind == "argument":
                        inv.add(InventoryItem(
                            topic=name,
                            category="cli_argument",
                            source_file=relpath,
                            source_line=lineno,
                            detail=f"framework: {framework}",
                            audience="user",
                        ))


def _extract_help(content: str, match_pos: int) -> Optional[str]:
    """Try to extract a help string near a CLI definition."""
    # Look for help="..." within 200 chars after match
    window = content[match_pos:match_pos + 300]
    m = re.search(r'''help\s*=\s*["']([^"']+)["']''', window)
    if m:
        return m.group(1)
    # Rust/Go: doc comment before
    before = content[max(0, match_pos - 200):match_pos]
    m = re.search(r'''///\s*(.+)$''', before, re.MULTILINE)
    if m:
        return m.group(1).strip()
    return None


# -- Config keys ------------------------------------------------------------

CONFIG_PATTERNS = [
    # Python dict .get() with string key
    (re.compile(r'''\.get\(\s*["']([a-z][\w._-]*)["']'''), "dict_get"),
    # Python dict["key"] access
    (re.compile(r'''\[["']([a-z][\w._-]*)["']\]'''), "dict_access"),
    # TOML/INI section headers
    (re.compile(r'''^\[([a-z][\w._-]*)\]\s*$''', re.MULTILINE), "section"),
    # YAML top-level keys (simplified)
    (re.compile(r'''^([a-z][\w_-]*):\s''', re.MULTILINE), "yaml_key"),
    # JS/TS config access: config.key or config["key"]
    (re.compile(r'''config\.([a-z][\w_]*)'''), "js_config"),
]

# Strings too generic to be config keys
IGNORE_CONFIG_KEYS: Set[str] = {
    "name", "type", "value", "key", "data", "id", "get", "set",
    "items", "keys", "values", "pop", "update", "default", "format",
    "path", "file", "line", "text", "string", "result", "output",
    "input", "error", "message", "status", "code", "index", "count",
    "size", "length", "start", "end", "true", "false", "none", "null",
}

# Only scan files that look like config loaders
CONFIG_FILE_PATTERNS = [
    re.compile(r"config", re.IGNORECASE),
    re.compile(r"settings", re.IGNORECASE),
    re.compile(r"options", re.IGNORECASE),
    re.compile(r"preferences", re.IGNORECASE),
]


def detect_config_keys(files: List[Path], root: Path, inv: Inventory) -> None:
    """Detect configuration key access patterns in config-related files."""
    seen: Set[str] = set()

    # Only scan files whose name suggests config handling
    config_files = [
        f for f in files
        if any(p.search(f.name) for p in CONFIG_FILE_PATTERNS)
    ]

    for fpath in config_files:
        lines = read_file_lines(fpath)
        relpath = str(fpath.relative_to(root))

        for lineno, line in enumerate(lines, 1):
            for pattern, kind in CONFIG_PATTERNS:
                for match in pattern.finditer(line):
                    key = match.group(1)
                    if key in IGNORE_CONFIG_KEYS or len(key) < 3:
                        continue
                    if key not in seen:
                        seen.add(key)
                        inv.add(InventoryItem(
                            topic=key,
                            category="config_key",
                            source_file=relpath,
                            source_line=lineno,
                            detail=f"pattern: {kind}",
                            audience="operator",
                        ))


# -- HTTP endpoints ---------------------------------------------------------

ENDPOINT_PATTERNS = [
    # Python Flask/FastAPI decorators
    (re.compile(r'''@\w+\.(get|post|put|patch|delete|route)\(\s*["']([^"']+)["']''', re.IGNORECASE), "decorator"),
    # Express.js
    (re.compile(r'''(?:app|router)\.(get|post|put|patch|delete)\(\s*["']([^"']+)["']'''), "express"),
    # Rust actix/axum
    (re.compile(r'''#\[(get|post|put|patch|delete)\(\s*"([^"]+)"'''), "rust_macro"),
    (re.compile(r'''\.route\(\s*["']([^"']+)["']\s*,\s*(?:get|post|put|patch|delete)'''), "axum"),
    # Go net/http
    (re.compile(r'''(?:Handle|HandleFunc)\(\s*["']([^"']+)["']'''), "go_http"),
]


def detect_http_endpoints(files: List[Path], root: Path, inv: Inventory) -> None:
    """Detect HTTP route/endpoint definitions."""
    seen: Set[str] = set()

    for fpath in files:
        lines = read_file_lines(fpath)
        relpath = str(fpath.relative_to(root))

        for lineno, line in enumerate(lines, 1):
            for pattern, kind in ENDPOINT_PATTERNS:
                for match in pattern.finditer(line):
                    groups = match.groups()
                    if kind == "decorator" or kind == "express" or kind == "rust_macro":
                        method, path = groups[0].upper(), groups[1]
                    elif kind == "go_http":
                        method, path = "ANY", groups[0]
                    elif kind == "axum":
                        path, method = groups[0], "ANY"
                    else:
                        continue

                    endpoint = f"{method} {path}"
                    if endpoint not in seen:
                        seen.add(endpoint)
                        inv.add(InventoryItem(
                            topic=endpoint,
                            category="http_endpoint",
                            source_file=relpath,
                            source_line=lineno,
                            detail=f"framework: {kind}",
                            audience="developer",
                        ))


# -- Public exports ---------------------------------------------------------

EXPORT_PATTERNS = [
    # Python __init__.py imports
    (re.compile(r'''from\s+\.\w+\s+import\s+(\w+)'''), "python_reexport"),
    # Python __all__
    (re.compile(r'''__all__\s*=\s*\[([^\]]+)\]'''), "python_all"),
    # JS/TS named exports
    (re.compile(r'''export\s+(?:const|let|var|function|class|interface|type|enum)\s+(\w+)'''), "js_export"),
    # JS/TS re-exports
    (re.compile(r'''export\s+\{([^}]+)\}'''), "js_reexport"),
    # Rust pub items
    (re.compile(r'''pub\s+(?:fn|struct|enum|trait|type|const|static|mod)\s+(\w+)'''), "rust_pub"),
    # Go exported (capitalized) functions
    (re.compile(r'''func\s+(?:\(\w+\s+\*?\w+\)\s+)?([A-Z]\w+)\('''), "go_export"),
]


def detect_public_exports(files: List[Path], root: Path, inv: Inventory) -> None:
    """Detect public module exports and API surface."""
    seen: Set[str] = set()

    # For Python, focus on __init__.py and public modules
    # For JS/TS, focus on index files and files with 'export'
    # For Rust, focus on lib.rs and mod.rs
    export_files = [
        f for f in files
        if f.name in ("__init__.py", "index.ts", "index.js", "lib.rs", "mod.rs")
        or "export" in (read_file_lines(f)[:5] and " ".join(read_file_lines(f)[:5]) or "")
    ]

    # Also include all Rust/Go files for pub/exported detection
    for f in files:
        if f.suffix in (".rs", ".go") and f not in export_files:
            export_files.append(f)

    for fpath in export_files:
        lines = read_file_lines(fpath)
        relpath = str(fpath.relative_to(root))
        content = "\n".join(lines)

        for pattern, kind in EXPORT_PATTERNS:
            for match in pattern.finditer(content):
                raw = match.group(1)

                # Handle multi-name exports (__all__, export { a, b })
                if kind in ("python_all", "js_reexport"):
                    names = [
                        n.strip().strip("\"'")
                        for n in raw.split(",")
                        if n.strip().strip("\"'")
                    ]
                else:
                    names = [raw]

                pos = match.start()
                lineno = content[:pos].count("\n") + 1

                for name in names:
                    if name.startswith("_") or name in seen:
                        continue
                    seen.add(name)
                    inv.add(InventoryItem(
                        topic=name,
                        category="public_export",
                        source_file=relpath,
                        source_line=lineno,
                        detail=f"kind: {kind}",
                        audience="developer",
                    ))


# -- Error types ------------------------------------------------------------

ERROR_PATTERNS = [
    # Python exception classes
    (re.compile(r'''class\s+(\w*(?:Error|Exception|Failure|Fault)\w*)\s*\('''), "python"),
    # JS/TS error classes
    (re.compile(r'''class\s+(\w*(?:Error|Exception)\w*)\s+extends'''), "js"),
    # Rust error enums/structs
    (re.compile(r'''(?:pub\s+)?(?:enum|struct)\s+(\w*(?:Error|Err)\w*)'''), "rust"),
    # Go error types
    (re.compile(r'''type\s+(\w*(?:Error|Err)\w*)\s+struct'''), "go"),
    # HTTP error status codes in route handlers
    (re.compile(r'''(?:status|code)\s*[=:]\s*(4\d{2}|5\d{2})'''), "http_status"),
]


def detect_error_types(files: List[Path], root: Path, inv: Inventory) -> None:
    """Detect custom error/exception type definitions."""
    seen: Set[str] = set()

    for fpath in files:
        lines = read_file_lines(fpath)
        relpath = str(fpath.relative_to(root))

        for lineno, line in enumerate(lines, 1):
            for pattern, kind in ERROR_PATTERNS:
                for match in pattern.finditer(line):
                    name = match.group(1)
                    if name not in seen:
                        seen.add(name)
                        category = "error_type"
                        if kind == "http_status":
                            category = "http_error_status"
                        inv.add(InventoryItem(
                            topic=name,
                            category=category,
                            source_file=relpath,
                            source_line=lineno,
                            detail=f"language: {kind}",
                            audience="developer",
                        ))


# ---------------------------------------------------------------------------
# Detector registry
# ---------------------------------------------------------------------------

DETECTORS = {
    "env_vars": detect_env_vars,
    "cli_commands": detect_cli_commands,
    "config_keys": detect_config_keys,
    "http_endpoints": detect_http_endpoints,
    "public_exports": detect_public_exports,
    "error_types": detect_error_types,
}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run_inventory(
    root: Path,
    detectors: Optional[List[str]] = None,
) -> Inventory:
    """Run the inventory extraction pipeline."""
    inv = Inventory(root=str(root))

    # Discover source files
    files = discover_files(root)
    inv.files_scanned = len(files)

    # Run selected detectors
    detector_names = detectors or list(DETECTORS.keys())
    for name in detector_names:
        if name in DETECTORS:
            DETECTORS[name](files, root, inv)
            inv.detectors_run.append(name)

    return inv


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract documentable surface area from a codebase.",
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Project root directory (default: current directory)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON (default: human-readable table)",
    )
    parser.add_argument(
        "--detectors",
        default=None,
        help="Comma-separated list of detectors to run (default: all)",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"Error: {root} is not a directory", file=sys.stderr)
        sys.exit(1)

    detector_list = args.detectors.split(",") if args.detectors else None
    inv = run_inventory(root, detector_list)

    if args.json:
        output = {
            "root": inv.root,
            "files_scanned": inv.files_scanned,
            "detectors_run": inv.detectors_run,
            "summary": inv.summary(),
            "items": [asdict(item) for item in inv.items],
        }
        json.dump(output, sys.stdout, indent=2)
        print()
    else:
        print(f"Inventory: {root}")
        print(f"Files scanned: {inv.files_scanned}")
        print(f"Detectors: {', '.join(inv.detectors_run)}")
        print(f"Items found: {len(inv.items)}")
        print()

        summary = inv.summary()
        for category, count in sorted(summary.items()):
            print(f"  {category}: {count}")
        print()

        # Group by category
        by_category: Dict[str, List[InventoryItem]] = {}
        for item in inv.items:
            by_category.setdefault(item.category, []).append(item)

        for category in sorted(by_category.keys()):
            items = by_category[category]
            print(f"## {category} ({len(items)})")
            print()
            for item in sorted(items, key=lambda i: i.topic):
                loc = f"{item.source_file}:{item.source_line}"
                detail = f" ({item.detail})" if item.detail else ""
                print(f"  {item.topic}{detail}")
                print(f"    {loc}")
            print()


if __name__ == "__main__":
    main()
