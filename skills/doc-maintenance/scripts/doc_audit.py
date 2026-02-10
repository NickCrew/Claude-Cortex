#!/usr/bin/env python3
"""
Documentation Audit Script

Performs a deterministic scan of project documentation to identify:
- Broken internal links
- Orphan docs (not linked from anywhere)
- Missing required folder structure
- Stale files (unchanged while sibling code changed)
- Empty or stub files

Usage:
    python3 skills/doc-maintenance/scripts/doc_audit.py [--json] [--root PATH]

Options:
    --json    Output as JSON instead of markdown
    --root    Project root directory (default: current directory)
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from pathlib import Path


# --- Configuration ---

DOCS_ROOT = "docs"
MANUAL_ROOT = "manual"
README = "README.md"

REQUIRED_DOCS_FOLDERS = [
    "architecture",
    "development",
    "plans",
    "reviews",
    "testing",
    "reports",
    "security",
    "api",
    "reference",
    "ideas",
    "archive",
]

REQUIRED_MANUAL_FOLDERS = [
    "getting-started",
    "guides",
    "tutorials",
    "reference",
    "troubleshooting",
]

STALE_THRESHOLD_DAYS = 90
STUB_LINE_THRESHOLD = 3

# Regex for markdown links: [text](path) — ignores URLs and anchors
MD_LINK_PATTERN = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")


# --- Data Structures ---


@dataclass
class Finding:
    category: str  # broken_link, orphan, missing_structure, stale, stub
    severity: str  # P0, P1, P2, P3, P4
    file_path: str
    description: str
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


def find_markdown_files(root):
    """Find all markdown files under docs/, manual/, and README.md."""
    files = []
    for search_root in [root / DOCS_ROOT, root / MANUAL_ROOT]:
        if search_root.exists():
            files.extend(search_root.rglob("*.md"))
    readme = root / README
    if readme.exists():
        files.append(readme)
    return sorted(files)


def extract_md_links(filepath):
    """Extract markdown links from a file. Returns list of (line_num, text, target)."""
    links = []
    try:
        content = filepath.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return links

    for i, line in enumerate(content.splitlines(), 1):
        for match in MD_LINK_PATTERN.finditer(line):
            target = match.group(2)
            # Skip URLs, anchors, and mailto
            if target.startswith(("http://", "https://", "#", "mailto:")):
                continue
            # Strip anchor from local paths
            target = target.split("#")[0]
            if target:
                links.append((i, match.group(1), target))
    return links


def git_last_modified_days(filepath, root):
    """Get days since last git modification of a file."""
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%ct", "--", str(filepath.relative_to(root))],
            capture_output=True,
            text=True,
            cwd=root,
            check=True,
        )
        timestamp = result.stdout.strip()
        if not timestamp:
            return None
        days = (time.time() - int(timestamp)) / 86400
        return int(days)
    except (subprocess.CalledProcessError, FileNotFoundError, ValueError):
        return None


def file_line_count(filepath):
    """Count non-empty lines in a file."""
    try:
        content = filepath.read_text(encoding="utf-8", errors="replace")
        return sum(1 for line in content.splitlines() if line.strip())
    except OSError:
        return 0


# --- Checks ---


def check_broken_links(root, md_files):
    """Find markdown links pointing to nonexistent files."""
    findings = []
    for md_file in md_files:
        links = extract_md_links(md_file)
        for line_num, text, target in links:
            # Resolve relative to the file's directory
            resolved = (md_file.parent / target).resolve()
            if not resolved.exists():
                rel_path = str(md_file.relative_to(root))
                findings.append(
                    Finding(
                        category="broken_link",
                        severity="P1",
                        file_path=rel_path,
                        description=f"Link to '{target}' on line {line_num} points to missing file",
                        details={"line": line_num, "link_text": text, "target": target},
                    )
                )
    return findings


def check_orphan_docs(root, md_files):
    """Find docs not linked from any other doc."""
    # Build set of all link targets (resolved to absolute paths)
    linked_targets = set()
    for md_file in md_files:
        links = extract_md_links(md_file)
        for _, _, target in links:
            resolved = (md_file.parent / target).resolve()
            linked_targets.add(resolved)

    # Check which docs are never targeted
    findings = []
    for md_file in md_files:
        # Skip README.md — it's the root, not expected to be linked to
        if md_file == root / README:
            continue
        # Skip index files — they're navigation, not content targets
        if md_file.name.lower() in ("index.md", "readme.md"):
            continue
        if md_file.resolve() not in linked_targets:
            rel_path = str(md_file.relative_to(root))
            findings.append(
                Finding(
                    category="orphan",
                    severity="P3",
                    file_path=rel_path,
                    description="File is not linked from any other document",
                )
            )
    return findings


def check_missing_structure(root):
    """Check for missing required folders."""
    findings = []

    docs_dir = root / DOCS_ROOT
    manual_dir = root / MANUAL_ROOT

    # Check docs/ subfolders
    if docs_dir.exists():
        for folder in REQUIRED_DOCS_FOLDERS:
            if not (docs_dir / folder).exists():
                findings.append(
                    Finding(
                        category="missing_structure",
                        severity="P3",
                        file_path=f"docs/{folder}/",
                        description=f"Required folder docs/{folder}/ does not exist",
                    )
                )
    else:
        findings.append(
            Finding(
                category="missing_structure",
                severity="P2",
                file_path="docs/",
                description="docs/ directory does not exist",
            )
        )

    # Check manual/ subfolders
    if manual_dir.exists():
        for folder in REQUIRED_MANUAL_FOLDERS:
            if not (manual_dir / folder).exists():
                findings.append(
                    Finding(
                        category="missing_structure",
                        severity="P3",
                        file_path=f"manual/{folder}/",
                        description=f"Required folder manual/{folder}/ does not exist",
                    )
                )
    else:
        findings.append(
            Finding(
                category="missing_structure",
                severity="P2",
                file_path="manual/",
                description="manual/ directory does not exist",
            )
        )

    return findings


def check_stale_docs(root, md_files):
    """Find docs not modified in a long time."""
    findings = []
    for md_file in md_files:
        days = git_last_modified_days(md_file, root)
        if days is not None and days > STALE_THRESHOLD_DAYS:
            rel_path = str(md_file.relative_to(root))
            findings.append(
                Finding(
                    category="stale",
                    severity="P4",
                    file_path=rel_path,
                    description=f"File has not been modified in {days} days",
                    details={"days_since_modified": days},
                )
            )
    return findings


def check_stub_files(root, md_files):
    """Find files with very little content."""
    findings = []
    for md_file in md_files:
        line_count = file_line_count(md_file)
        if line_count <= STUB_LINE_THRESHOLD:
            rel_path = str(md_file.relative_to(root))
            findings.append(
                Finding(
                    category="stub",
                    severity="P3",
                    file_path=rel_path,
                    description=f"File has only {line_count} non-empty line(s) — likely a stub",
                    details={"line_count": line_count},
                )
            )
    return findings


# --- Report Generation ---


def generate_markdown_report(findings, root):
    """Generate a markdown-formatted audit report."""
    lines = [
        "# Documentation Audit Report",
        "",
        f"**Project root:** `{root}`",
        f"**Total findings:** {len(findings)}",
        "",
    ]

    if not findings:
        lines.append("No issues found. Documentation is in good shape.")
        return "\n".join(lines)

    # Summary by category
    by_category = defaultdict(list)
    for f in findings:
        by_category[f.category].append(f)

    lines.append("## Summary")
    lines.append("")
    lines.append("| Category | Count |")
    lines.append("|----------|-------|")
    for cat in ["broken_link", "orphan", "missing_structure", "stale", "stub"]:
        if cat in by_category:
            lines.append(f"| {cat} | {len(by_category[cat])} |")
    lines.append("")

    # Summary by severity
    by_severity = defaultdict(list)
    for f in findings:
        by_severity[f.severity].append(f)

    lines.append("## By Severity")
    lines.append("")
    for sev in ["P0", "P1", "P2", "P3", "P4"]:
        if sev not in by_severity:
            continue
        lines.append(f"### {sev}")
        lines.append("")
        lines.append("| File | Category | Description |")
        lines.append("|------|----------|-------------|")
        for f in by_severity[sev]:
            lines.append(f"| `{f.file_path}` | {f.category} | {f.description} |")
        lines.append("")

    return "\n".join(lines)


def generate_json_report(findings, root):
    """Generate a JSON-formatted audit report."""
    report = {
        "project_root": str(root),
        "total_findings": len(findings),
        "findings": [asdict(f) for f in findings],
    }
    return json.dumps(report, indent=2)


# --- Main ---


def main():
    parser = argparse.ArgumentParser(description="Documentation audit tool")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--root", type=str, default=None, help="Project root path")
    args = parser.parse_args()

    root = get_project_root(args.root)
    md_files = find_markdown_files(root)

    print(f"Scanning {len(md_files)} markdown files in {root}...", file=sys.stderr)

    # Run all checks
    findings = []
    findings.extend(check_broken_links(root, md_files))
    findings.extend(check_orphan_docs(root, md_files))
    findings.extend(check_missing_structure(root))
    findings.extend(check_stale_docs(root, md_files))
    findings.extend(check_stub_files(root, md_files))

    # Sort by severity then category
    severity_order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3, "P4": 4}
    findings.sort(key=lambda f: (severity_order.get(f.severity, 9), f.category, f.file_path))

    # Output
    if args.json:
        print(generate_json_report(findings, root))
    else:
        print(generate_markdown_report(findings, root))

    # Exit code: non-zero if P0 or P1 findings exist
    has_critical = any(f.severity in ("P0", "P1") for f in findings)
    sys.exit(1 if has_critical else 0)


if __name__ == "__main__":
    main()
