#!/usr/bin/env python3
"""
Documentation Claim Extractor

Parses markdown files and extracts verifiable claims:
- File path references (inline code matching path patterns)
- Shell commands (code blocks with shell indicators)
- Code references (function, class, method names in inline code)
- Import statements (from code blocks)
- Configuration references (env vars, config keys)
- URL references (external links)

Usage:
    python3 skills/doc-claim-validator/scripts/extract_claims.py [OPTIONS]

Options:
    --json          Output as JSON instead of markdown
    --root PATH     Project root directory (default: git root or cwd)
    --scope SCOPE   Which docs to scan: docs, manual, all (default: all)
    --verbose       Show extraction details per file
"""

import argparse
import json
import os
import re
import subprocess
import sys
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Optional


# --- Configuration ---

# Directories to scan per scope
SCOPE_DIRS = {
    "docs": ["docs"],
    "manual": ["manual"],
    "all": ["docs", "manual"],
}

# Always include README.md at project root
ALWAYS_INCLUDE = ["README.md", "CONTRIBUTING.md"]

# Skip directories
SKIP_DIRS = {"node_modules", ".git", "__pycache__", "archive"}

# --- Patterns ---

# Inline code: `something`
INLINE_CODE_RE = re.compile(r"(?<!`)`([^`\n]+?)`(?!`)")

# Fenced code blocks: ```lang\n...\n```
FENCED_BLOCK_RE = re.compile(
    r"^```(\w*)\s*\n(.*?)^```", re.MULTILINE | re.DOTALL
)

# Markdown links: [text](url)
MD_LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")

# File path patterns (inline code that looks like a file path)
FILE_PATH_RE = re.compile(
    r"^(?:\.{0,2}/)?(?:[\w@.-]+/)*[\w@.-]+\.\w+$"
)

# Shell command indicators
SHELL_LANGS = {"bash", "sh", "shell", "zsh", "console", "terminal", ""}
SHELL_PREFIX_RE = re.compile(r"^\s*\$\s+(.+)$", re.MULTILINE)
COMMAND_RE = re.compile(
    r"^(?:npm|npx|yarn|pnpm|pip|python3?|node|cargo|go|make|docker|"
    r"git|curl|wget|brew|apt|cortex|bd|claude)\s+.+"
)

# Code reference patterns (function calls, class names, methods)
FUNC_CALL_RE = re.compile(r"^[\w.]+\(.*\)$")
CLASS_REF_RE = re.compile(r"^[A-Z][\w]*(?:\.\w+)*$")
METHOD_REF_RE = re.compile(r"^[\w]+\.[\w]+(?:\(.*\))?$")

# Import/require patterns in code blocks
IMPORT_RE = re.compile(
    r"^(?:import\s+.*?from\s+['\"](.+?)['\"]|"
    r"(?:const|let|var)\s+.*?=\s*require\(['\"](.+?)['\"]\)|"
    r"from\s+([\w.]+)\s+import|"
    r"import\s+([\w.]+))",
    re.MULTILINE,
)

# Config/env var patterns
CONFIG_RE = re.compile(r"^[A-Z][A-Z0-9_]{2,}(?:=.+)?$")
ENV_VAR_RE = re.compile(r"\$\{?([A-Z][A-Z0-9_]{2,})\}?")

# No-verify marker
NO_VERIFY_RE = re.compile(r"<!--\s*no-verify\s*-->")

# Common false positives to skip
FALSE_POSITIVES = {
    "true", "false", "null", "undefined", "none", "nil",
    "string", "number", "boolean", "object", "array",
    "int", "float", "str", "bool", "dict", "list", "tuple",
    "void", "any", "never", "unknown",
    "GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS",
    "TODO", "FIXME", "NOTE", "WARNING", "HACK",
    "OK", "ERROR", "SUCCESS", "FAIL",
}


# --- Data Structures ---


@dataclass
class Claim:
    claim_type: str  # file_path, command, code_ref, import, config, url
    source_file: str  # markdown file containing the claim
    line_number: int  # line in the source file
    literal: str  # exact text of the claim
    context: str = ""  # surrounding text for disambiguation
    details: dict = field(default_factory=dict)


# --- Utilities ---


def get_project_root(root_override=None):
    """Determine project root from git or override."""
    if root_override:
        return Path(root_override).resolve()
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True,
        )
        return Path(result.stdout.strip())
    except (subprocess.CalledProcessError, FileNotFoundError):
        return Path.cwd()


def find_markdown_files(root, scope="all"):
    """Find markdown files based on scope."""
    files = []
    dirs = SCOPE_DIRS.get(scope, SCOPE_DIRS["all"])

    for d in dirs:
        search_root = root / d
        if search_root.exists():
            for md in search_root.rglob("*.md"):
                # Skip archive and other excluded dirs
                if any(part in SKIP_DIRS for part in md.relative_to(root).parts):
                    continue
                files.append(md)

    # Always include root-level files
    for name in ALWAYS_INCLUDE:
        f = root / name
        if f.exists():
            files.append(f)

    return sorted(set(files))


def is_in_no_verify_block(content, line_num):
    """Check if a line is preceded by a no-verify comment."""
    lines = content.splitlines()
    # Look back up to 5 lines for a no-verify marker
    start = max(0, line_num - 6)
    preceding = "\n".join(lines[start:line_num - 1])
    return bool(NO_VERIFY_RE.search(preceding))


# --- Extractors ---


def extract_inline_code_claims(filepath, content, root):
    """Extract claims from inline code spans."""
    claims = []
    rel_path = str(filepath.relative_to(root))

    for i, line in enumerate(content.splitlines(), 1):
        if is_in_no_verify_block(content, i):
            continue

        for match in INLINE_CODE_RE.finditer(line):
            code = match.group(1).strip()

            # Skip false positives
            if code.lower() in {fp.lower() for fp in FALSE_POSITIVES}:
                continue
            if len(code) < 2:
                continue

            # Classify the inline code
            if FILE_PATH_RE.match(code) and "/" in code:
                claims.append(Claim(
                    claim_type="file_path",
                    source_file=rel_path,
                    line_number=i,
                    literal=code,
                    context=line.strip(),
                ))
            elif CONFIG_RE.match(code):
                claims.append(Claim(
                    claim_type="config",
                    source_file=rel_path,
                    line_number=i,
                    literal=code.split("=")[0],
                    context=line.strip(),
                ))
            elif FUNC_CALL_RE.match(code):
                # Strip parens for the function name
                func_name = code.split("(")[0]
                if func_name and not func_name[0].isdigit():
                    claims.append(Claim(
                        claim_type="code_ref",
                        source_file=rel_path,
                        line_number=i,
                        literal=func_name,
                        context=line.strip(),
                        details={"kind": "function_call", "full": code},
                    ))
            elif METHOD_REF_RE.match(code) and "." in code:
                claims.append(Claim(
                    claim_type="code_ref",
                    source_file=rel_path,
                    line_number=i,
                    literal=code.rstrip(")").split("(")[0],
                    context=line.strip(),
                    details={"kind": "method_ref", "full": code},
                ))
            elif COMMAND_RE.match(code):
                claims.append(Claim(
                    claim_type="command",
                    source_file=rel_path,
                    line_number=i,
                    literal=code,
                    context=line.strip(),
                ))

    return claims


def extract_code_block_claims(filepath, content, root):
    """Extract claims from fenced code blocks."""
    claims = []
    rel_path = str(filepath.relative_to(root))

    for match in FENCED_BLOCK_RE.finditer(content):
        lang = match.group(1).lower()
        block = match.group(2)
        block_start = content[:match.start()].count("\n") + 1

        # Check for no-verify
        if is_in_no_verify_block(content, block_start):
            continue

        # Shell commands
        if lang in SHELL_LANGS:
            for line_match in SHELL_PREFIX_RE.finditer(block):
                cmd = line_match.group(1).strip()
                line_in_block = block[:line_match.start()].count("\n")
                if cmd and not cmd.startswith("#"):
                    claims.append(Claim(
                        claim_type="command",
                        source_file=rel_path,
                        line_number=block_start + line_in_block + 1,
                        literal=cmd,
                        context=f"```{lang}``` block",
                        details={"block_lang": lang},
                    ))

            # Also catch commands without $ prefix
            for j, line in enumerate(block.splitlines()):
                stripped = line.strip()
                if stripped and COMMAND_RE.match(stripped) and not stripped.startswith("#"):
                    claims.append(Claim(
                        claim_type="command",
                        source_file=rel_path,
                        line_number=block_start + j + 1,
                        literal=stripped,
                        context=f"```{lang}``` block",
                        details={"block_lang": lang},
                    ))

        # Import statements in any code block
        for imp_match in IMPORT_RE.finditer(block):
            module = imp_match.group(1) or imp_match.group(2) or imp_match.group(3) or imp_match.group(4)
            if module:
                line_in_block = block[:imp_match.start()].count("\n")
                claims.append(Claim(
                    claim_type="import",
                    source_file=rel_path,
                    line_number=block_start + line_in_block + 1,
                    literal=module,
                    context=imp_match.group(0).strip(),
                    details={"block_lang": lang},
                ))

    return claims


def extract_url_claims(filepath, content, root):
    """Extract external URL claims from markdown links."""
    claims = []
    rel_path = str(filepath.relative_to(root))

    for i, line in enumerate(content.splitlines(), 1):
        if is_in_no_verify_block(content, i):
            continue

        for match in MD_LINK_RE.finditer(line):
            url = match.group(2)
            if url.startswith(("http://", "https://")):
                claims.append(Claim(
                    claim_type="url",
                    source_file=rel_path,
                    line_number=i,
                    literal=url,
                    context=match.group(0),
                    details={"link_text": match.group(1)},
                ))

    return claims


def extract_env_var_claims(filepath, content, root):
    """Extract environment variable references."""
    claims = []
    rel_path = str(filepath.relative_to(root))

    for i, line in enumerate(content.splitlines(), 1):
        if is_in_no_verify_block(content, i):
            continue

        for match in ENV_VAR_RE.finditer(line):
            var_name = match.group(1)
            if var_name not in FALSE_POSITIVES and len(var_name) > 3:
                claims.append(Claim(
                    claim_type="config",
                    source_file=rel_path,
                    line_number=i,
                    literal=var_name,
                    context=line.strip(),
                    details={"kind": "env_var"},
                ))

    return claims


# --- Deduplication ---


def deduplicate_claims(claims):
    """Remove duplicate claims (same type + literal + source file)."""
    seen = set()
    unique = []
    for c in claims:
        key = (c.claim_type, c.literal, c.source_file)
        if key not in seen:
            seen.add(key)
            unique.append(c)
    return unique


# --- Report Generation ---


def generate_markdown_report(claims, root):
    """Generate a markdown-formatted extraction report."""
    lines = [
        "# Documentation Claim Extraction Report",
        "",
        f"**Project root:** `{root}`",
        f"**Total claims extracted:** {len(claims)}",
        "",
    ]

    if not claims:
        lines.append("No verifiable claims found in documentation.")
        return "\n".join(lines)

    # Summary by type
    by_type = defaultdict(list)
    for c in claims:
        by_type[c.claim_type].append(c)

    lines.append("## Summary by Type")
    lines.append("")
    lines.append("| Type | Count |")
    lines.append("|------|-------|")
    for ct in ["file_path", "command", "code_ref", "import", "config", "url"]:
        if ct in by_type:
            lines.append(f"| {ct} | {len(by_type[ct])} |")
    lines.append("")

    # Claims by type
    for ct in ["file_path", "command", "code_ref", "import", "config", "url"]:
        if ct not in by_type:
            continue
        lines.append(f"## {ct} ({len(by_type[ct])})")
        lines.append("")
        lines.append("| File | Line | Claim |")
        lines.append("|------|------|-------|")
        for c in by_type[ct]:
            escaped = c.literal.replace("|", "\\|")
            lines.append(f"| `{c.source_file}` | {c.line_number} | `{escaped}` |")
        lines.append("")

    return "\n".join(lines)


def generate_json_report(claims, root):
    """Generate a JSON-formatted extraction report."""
    report = {
        "project_root": str(root),
        "total_claims": len(claims),
        "claims": [asdict(c) for c in claims],
    }
    return json.dumps(report, indent=2)


# --- Main ---


def main():
    parser = argparse.ArgumentParser(description="Extract verifiable claims from docs")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--root", type=str, default=None, help="Project root path")
    parser.add_argument(
        "--scope",
        choices=["docs", "manual", "all"],
        default="all",
        help="Which docs to scan (default: all)",
    )
    parser.add_argument("--verbose", action="store_true", help="Show per-file details")
    args = parser.parse_args()

    root = get_project_root(args.root)
    md_files = find_markdown_files(root, args.scope)

    print(f"Scanning {len(md_files)} markdown files in {root}...", file=sys.stderr)

    all_claims = []

    for md_file in md_files:
        try:
            content = md_file.read_text(encoding="utf-8", errors="replace")
        except OSError as e:
            print(f"Warning: Could not read {md_file}: {e}", file=sys.stderr)
            continue

        file_claims = []
        file_claims.extend(extract_inline_code_claims(md_file, content, root))
        file_claims.extend(extract_code_block_claims(md_file, content, root))
        file_claims.extend(extract_url_claims(md_file, content, root))
        file_claims.extend(extract_env_var_claims(md_file, content, root))

        if args.verbose and file_claims:
            rel = str(md_file.relative_to(root))
            print(f"  {rel}: {len(file_claims)} claims", file=sys.stderr)

        all_claims.extend(file_claims)

    # Deduplicate
    all_claims = deduplicate_claims(all_claims)

    # Sort by source file, then line number
    all_claims.sort(key=lambda c: (c.source_file, c.line_number))

    # Output
    if args.json:
        print(generate_json_report(all_claims, root))
    else:
        print(generate_markdown_report(all_claims, root))

    print(f"\nExtracted {len(all_claims)} unique claims.", file=sys.stderr)


if __name__ == "__main__":
    main()
