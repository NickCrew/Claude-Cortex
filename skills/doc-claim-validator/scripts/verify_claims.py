#!/usr/bin/env python3
"""
Documentation Claim Verifier

Takes claims extracted by extract_claims.py and verifies them against
the actual project state.

Verification methods per claim type:
- file_path:  os.path.exists()
- command:    shutil.which() + script existence check
- code_ref:   grep for symbol in codebase
- import:     check module in project or dependency manifests
- config:     grep for config key in source files
- url:        HTTP HEAD request (opt-in with --check-urls)

Usage:
    python3 skills/doc-claim-validator/scripts/verify_claims.py [OPTIONS]

Options:
    --json             Output as JSON instead of markdown
    --root PATH        Project root directory (default: git root or cwd)
    --claims-file PATH Read claims from JSON file (default: run extractor)
    --check-urls       Enable URL verification (slow, requires network)
    --scope SCOPE      Passed to extractor if no claims-file: docs, manual, all
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Dict, Optional, Tuple


# --- Configuration ---

# Source directories to search for code references
SOURCE_DIRS = [
    "src", "lib", "app", "bin", "scripts", "tools", "pkg", "cmd",
    "skills", "agents", "hooks", "codex", "catskills",
]

# File extensions to search for code references
CODE_EXTENSIONS = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".rs", ".rb",
    ".java", ".kt", ".swift", ".c", ".cpp", ".h", ".hpp",
    ".sh", ".bash", ".zsh", ".yaml", ".yml", ".toml", ".json",
}

# Dependency manifest files
DEP_MANIFESTS = [
    "package.json", "requirements.txt", "Pipfile", "pyproject.toml",
    "go.mod", "Cargo.toml", "Gemfile", "pom.xml", "build.gradle",
    "composer.json",
]

# Config file patterns
CONFIG_PATTERNS = [
    "*.env", "*.env.*", ".env*",
    "config.*", "*.config.*", "settings.*",
    "*.yaml", "*.yml", "*.toml", "*.ini", "*.cfg",
]

# Known system commands that don't need local verification
KNOWN_COMMANDS = {
    "npm", "npx", "yarn", "pnpm", "pip", "pip3", "python", "python3",
    "node", "cargo", "go", "make", "docker", "docker-compose",
    "git", "curl", "wget", "brew", "apt", "apt-get",
    "cat", "ls", "mkdir", "cp", "mv", "rm", "echo", "grep", "find",
    "sed", "awk", "sort", "uniq", "head", "tail", "wc",
}


# --- Data Structures ---


@dataclass
class VerificationResult:
    claim_type: str
    source_file: str
    line_number: int
    literal: str
    status: str  # pass, fail, skip, warn
    reason: str
    severity: str = ""  # P0-P4, set during classification
    category: str = ""  # missing_target, wrong_signature, etc.
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


def grep_codebase(pattern, root, file_extensions=None):
    """Search codebase for a pattern. Returns list of (file, line_num, line)."""
    cmd = ["grep", "-rn", "--include=*.py", "--include=*.js", "--include=*.ts",
           "--include=*.tsx", "--include=*.jsx", "--include=*.go", "--include=*.rs",
           "--include=*.sh", "--include=*.yaml", "--include=*.yml", "--include=*.toml",
           "--include=*.json", "--include=*.md",
           "-l", pattern]

    # Only search source directories that exist
    search_paths = []
    for d in SOURCE_DIRS:
        p = root / d
        if p.exists():
            search_paths.append(str(p))

    if not search_paths:
        # Fall back to root
        search_paths = [str(root)]

    cmd.extend(search_paths)

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=root,
            timeout=10,
        )
        if result.returncode == 0:
            return result.stdout.strip().splitlines()
        return []
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return []


# --- Git Staleness ---

# Cache for git timestamps to avoid repeated calls
_git_timestamp_cache: Dict[str, Optional[int]] = {}


def git_last_modified_ts(filepath, root):
    """Get Unix timestamp of last git modification. Cached."""
    key = str(filepath)
    if key in _git_timestamp_cache:
        return _git_timestamp_cache[key]

    try:
        rel = str(Path(filepath).relative_to(root))
    except ValueError:
        rel = str(filepath)

    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%ct", "--", rel],
            capture_output=True,
            text=True,
            cwd=root,
            timeout=5,
        )
        ts_str = result.stdout.strip()
        ts = int(ts_str) if ts_str else None
    except (subprocess.TimeoutExpired, FileNotFoundError, ValueError):
        ts = None

    _git_timestamp_cache[key] = ts
    return ts


def git_commit_count_since(filepath, since_ts, root):
    """Count commits touching filepath after a given timestamp."""
    try:
        rel = str(Path(filepath).relative_to(root))
    except ValueError:
        rel = str(filepath)

    try:
        result = subprocess.run(
            ["git", "log", "--oneline", f"--since={since_ts}", "--", rel],
            capture_output=True,
            text=True,
            cwd=root,
            timeout=5,
        )
        lines = [l for l in result.stdout.strip().splitlines() if l]
        return len(lines)
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return 0


def compute_staleness(claim, target_files, root):
    """Compute staleness score for a claim that passed existence checks.

    Returns (score, detail_dict) where:
      score = 0    -> no evidence of staleness
      score = 1-3  -> low drift (target changed 1-3 times since doc edit)
      score = 4-9  -> medium drift
      score = 10+  -> high drift (target changed heavily, doc didn't)

    The score is the total number of commits touching any target file
    after the doc file's last modification.
    """
    doc_ts = git_last_modified_ts(root / claim["source_file"], root)
    if doc_ts is None:
        return 0, {}

    total_commits = 0
    drift_details = {}

    for tf in target_files:
        target_ts = git_last_modified_ts(root / tf, root)
        if target_ts is None:
            continue

        # Only interesting if target was modified after the doc
        if target_ts > doc_ts:
            commits = git_commit_count_since(root / tf, doc_ts, root)
            if commits > 0:
                total_commits += commits
                days_ahead = (target_ts - doc_ts) // 86400
                drift_details[tf] = {
                    "commits_since_doc": commits,
                    "days_ahead": days_ahead,
                }

    return total_commits, drift_details


def staleness_label(score):
    """Convert numeric staleness score to human label."""
    if score == 0:
        return None
    if score <= 3:
        return "low"
    if score <= 9:
        return "medium"
    return "high"


def read_dep_manifests(root):
    """Read dependency manifest files and extract package names."""
    deps = set()

    # package.json
    pkg_json = root / "package.json"
    if pkg_json.exists():
        try:
            data = json.loads(pkg_json.read_text())
            for key in ("dependencies", "devDependencies", "peerDependencies"):
                if key in data:
                    deps.update(data[key].keys())
        except (json.JSONDecodeError, OSError):
            pass

    # requirements.txt
    req_txt = root / "requirements.txt"
    if req_txt.exists():
        try:
            for line in req_txt.read_text().splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    # Strip version specifiers
                    pkg = re.split(r"[>=<!\[;]", line)[0].strip()
                    if pkg:
                        deps.add(pkg.lower())
        except OSError:
            pass

    # pyproject.toml (basic parsing)
    pyproject = root / "pyproject.toml"
    if pyproject.exists():
        try:
            content = pyproject.read_text()
            # Look for dependencies list
            in_deps = False
            for line in content.splitlines():
                if "dependencies" in line and "=" in line:
                    in_deps = True
                    continue
                if in_deps:
                    if line.strip().startswith("]"):
                        in_deps = False
                    elif line.strip().startswith('"'):
                        pkg = re.split(r"[>=<!\[;]", line.strip().strip('",'))[0].strip()
                        if pkg:
                            deps.add(pkg.lower())
        except OSError:
            pass

    # go.mod
    go_mod = root / "go.mod"
    if go_mod.exists():
        try:
            for line in go_mod.read_text().splitlines():
                line = line.strip()
                if line and not line.startswith(("module ", "go ", "//")):
                    parts = line.split()
                    if parts:
                        deps.add(parts[0])
        except OSError:
            pass

    # Cargo.toml
    cargo = root / "Cargo.toml"
    if cargo.exists():
        try:
            in_deps = False
            for line in cargo.read_text().splitlines():
                if re.match(r"\[.*dependencies.*\]", line):
                    in_deps = True
                    continue
                if in_deps:
                    if line.startswith("["):
                        in_deps = False
                    elif "=" in line:
                        pkg = line.split("=")[0].strip()
                        if pkg:
                            deps.add(pkg)
        except OSError:
            pass

    return deps


# --- Verifiers ---


def verify_file_path(claim, root):
    """Verify that a referenced file path exists."""
    literal = claim["literal"]

    # Try as-is from project root
    target = root / literal
    if target.exists():
        return VerificationResult(
            claim_type=claim["claim_type"],
            source_file=claim["source_file"],
            line_number=claim["line_number"],
            literal=literal,
            status="pass",
            reason=f"File exists: {literal}",
        )

    # Try relative to the source file's directory
    source_dir = (root / claim["source_file"]).parent
    target = source_dir / literal
    if target.exists():
        return VerificationResult(
            claim_type=claim["claim_type"],
            source_file=claim["source_file"],
            line_number=claim["line_number"],
            literal=literal,
            status="pass",
            reason=f"File exists relative to doc: {literal}",
        )

    # Determine severity based on doc location
    is_user_facing = claim["source_file"].startswith("manual/")
    severity = "P0" if is_user_facing else "P1"

    return VerificationResult(
        claim_type=claim["claim_type"],
        source_file=claim["source_file"],
        line_number=claim["line_number"],
        literal=literal,
        status="fail",
        reason=f"File not found: {literal}",
        severity=severity,
        category="missing_target",
    )


def verify_command(claim, root):
    """Verify that a referenced command exists."""
    literal = claim["literal"]

    # Extract the base command (first word)
    base_cmd = literal.split()[0] if literal.split() else literal

    # Strip leading ./ or paths
    if "/" in base_cmd:
        # It's a script path — check if it exists
        script_path = root / base_cmd.lstrip("./")
        if script_path.exists():
            return VerificationResult(
                claim_type=claim["claim_type"],
                source_file=claim["source_file"],
                line_number=claim["line_number"],
                literal=literal,
                status="pass",
                reason=f"Script exists: {base_cmd}",
            )
        return VerificationResult(
            claim_type=claim["claim_type"],
            source_file=claim["source_file"],
            line_number=claim["line_number"],
            literal=literal,
            status="fail",
            reason=f"Script not found: {base_cmd}",
            severity="P1",
            category="missing_target",
        )

    # Known system commands
    if base_cmd in KNOWN_COMMANDS:
        return VerificationResult(
            claim_type=claim["claim_type"],
            source_file=claim["source_file"],
            line_number=claim["line_number"],
            literal=literal,
            status="pass",
            reason=f"Known system command: {base_cmd}",
        )

    # Check if command exists on PATH
    if shutil.which(base_cmd):
        return VerificationResult(
            claim_type=claim["claim_type"],
            source_file=claim["source_file"],
            line_number=claim["line_number"],
            literal=literal,
            status="pass",
            reason=f"Command found on PATH: {base_cmd}",
        )

    # Check if it's a project script (package.json scripts, Makefile targets, etc.)
    pkg_json = root / "package.json"
    if pkg_json.exists():
        try:
            data = json.loads(pkg_json.read_text())
            scripts = data.get("scripts", {})
            # Check for "npm run X" pattern
            if base_cmd == "npm" and len(literal.split()) >= 3:
                subcmd = literal.split()[1]
                script_name = literal.split()[2] if subcmd == "run" else subcmd
                if script_name in scripts:
                    return VerificationResult(
                        claim_type=claim["claim_type"],
                        source_file=claim["source_file"],
                        line_number=claim["line_number"],
                        literal=literal,
                        status="pass",
                        reason=f"npm script exists: {script_name}",
                    )
        except (json.JSONDecodeError, OSError):
            pass

    # Check bin/ directory
    bin_path = root / "bin" / base_cmd
    if bin_path.exists():
        return VerificationResult(
            claim_type=claim["claim_type"],
            source_file=claim["source_file"],
            line_number=claim["line_number"],
            literal=literal,
            status="pass",
            reason=f"Found in bin/: {base_cmd}",
        )

    return VerificationResult(
        claim_type=claim["claim_type"],
        source_file=claim["source_file"],
        line_number=claim["line_number"],
        literal=literal,
        status="warn",
        reason=f"Command not found locally: {base_cmd} (may be installed separately)",
        severity="P3",
        category="missing_target",
    )


def verify_code_ref(claim, root):
    """Verify that a referenced code symbol exists in the codebase."""
    literal = claim["literal"]

    # Search for the symbol
    matches = grep_codebase(re.escape(literal), root)

    if matches:
        return VerificationResult(
            claim_type=claim["claim_type"],
            source_file=claim["source_file"],
            line_number=claim["line_number"],
            literal=literal,
            status="pass",
            reason=f"Symbol found in {len(matches)} file(s)",
            details={"found_in": matches[:5]},
        )

    is_user_facing = claim["source_file"].startswith("manual/")
    severity = "P0" if is_user_facing else "P1"

    return VerificationResult(
        claim_type=claim["claim_type"],
        source_file=claim["source_file"],
        line_number=claim["line_number"],
        literal=literal,
        status="fail",
        reason=f"Symbol not found in codebase: {literal}",
        severity=severity,
        category="missing_target",
    )


def verify_import(claim, root, deps):
    """Verify that an imported module exists."""
    literal = claim["literal"]

    # Check if it's a relative import (project module)
    if literal.startswith(".") or literal.startswith("/"):
        # Resolve relative to project
        target = root / literal.lstrip("./")
        # Try with common extensions
        for ext in ["", ".py", ".js", ".ts", "/index.js", "/index.ts"]:
            if (root / (literal.lstrip("./") + ext)).exists():
                return VerificationResult(
                    claim_type=claim["claim_type"],
                    source_file=claim["source_file"],
                    line_number=claim["line_number"],
                    literal=literal,
                    status="pass",
                    reason=f"Local module found: {literal}",
                )

    # Check if it's a known dependency
    # Normalize: @scope/pkg -> @scope/pkg, lodash/fp -> lodash
    pkg_name = literal.split("/")[0]
    if literal.startswith("@") and "/" in literal:
        pkg_name = "/".join(literal.split("/")[:2])

    if pkg_name.lower() in {d.lower() for d in deps}:
        return VerificationResult(
            claim_type=claim["claim_type"],
            source_file=claim["source_file"],
            line_number=claim["line_number"],
            literal=literal,
            status="pass",
            reason=f"Package found in dependencies: {pkg_name}",
        )

    # Check Python stdlib (basic heuristic)
    python_stdlib = {
        "os", "sys", "re", "json", "pathlib", "subprocess", "argparse",
        "collections", "dataclasses", "typing", "functools", "itertools",
        "datetime", "time", "math", "random", "hashlib", "base64",
        "io", "logging", "unittest", "asyncio", "abc", "enum",
    }
    if literal.split(".")[0] in python_stdlib:
        return VerificationResult(
            claim_type=claim["claim_type"],
            source_file=claim["source_file"],
            line_number=claim["line_number"],
            literal=literal,
            status="pass",
            reason=f"Python stdlib module: {literal}",
        )

    return VerificationResult(
        claim_type=claim["claim_type"],
        source_file=claim["source_file"],
        line_number=claim["line_number"],
        literal=literal,
        status="warn",
        reason=f"Module not found in project deps: {literal}",
        severity="P3",
        category="dead_dependency",
    )


def verify_config(claim, root):
    """Verify that a config key exists in the project."""
    literal = claim["literal"]

    # Search for the config key in source files
    matches = grep_codebase(re.escape(literal), root)

    if matches:
        # Filter out matches that are only in docs (the claim itself)
        code_matches = [m for m in matches if not m.startswith(("docs/", "manual/"))]
        if code_matches:
            return VerificationResult(
                claim_type=claim["claim_type"],
                source_file=claim["source_file"],
                line_number=claim["line_number"],
                literal=literal,
                status="pass",
                reason=f"Config key found in {len(code_matches)} source file(s)",
                details={"found_in": code_matches[:5]},
            )

    return VerificationResult(
        claim_type=claim["claim_type"],
        source_file=claim["source_file"],
        line_number=claim["line_number"],
        literal=literal,
        status="warn",
        reason=f"Config key not found in source code: {literal}",
        severity="P3",
        category="phantom_config",
    )


def verify_url(claim):
    """Verify that a URL is reachable (opt-in)."""
    literal = claim["literal"]

    try:
        import urllib.request
        req = urllib.request.Request(literal, method="HEAD")
        req.add_header("User-Agent", "doc-claim-validator/1.0")
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status < 400:
                return VerificationResult(
                    claim_type=claim["claim_type"],
                    source_file=claim["source_file"],
                    line_number=claim["line_number"],
                    literal=literal,
                    status="pass",
                    reason=f"URL reachable (HTTP {resp.status})",
                )
            return VerificationResult(
                claim_type=claim["claim_type"],
                source_file=claim["source_file"],
                line_number=claim["line_number"],
                literal=literal,
                status="fail",
                reason=f"URL returned HTTP {resp.status}",
                severity="P2",
                category="dead_url",
            )
    except Exception as e:
        return VerificationResult(
            claim_type=claim["claim_type"],
            source_file=claim["source_file"],
            line_number=claim["line_number"],
            literal=literal,
            status="fail",
            reason=f"URL unreachable: {type(e).__name__}",
            severity="P2",
            category="dead_url",
        )


# --- Report Generation ---


def generate_markdown_report(results, root):
    """Generate a markdown-formatted verification report."""
    passed = [r for r in results if r.status == "pass"]
    failed = [r for r in results if r.status == "fail"]
    warned = [r for r in results if r.status == "warn"]
    skipped = [r for r in results if r.status == "skip"]

    lines = [
        "# Documentation Claim Verification Report",
        "",
        f"**Project root:** `{root}`",
        f"**Total claims verified:** {len(results)}",
        f"**Passed:** {len(passed)} | **Failed:** {len(failed)} | **Warnings:** {len(warned)} | **Skipped:** {len(skipped)}",
        "",
    ]

    if not failed and not warned:
        lines.append("All claims verified successfully.")
        return "\n".join(lines)

    # Failures by severity
    if failed:
        by_severity = defaultdict(list)
        for r in failed:
            by_severity[r.severity or "unclassified"].append(r)

        lines.append("## Failures")
        lines.append("")

        for sev in ["P0", "P1", "P2", "P3", "P4", "unclassified"]:
            if sev not in by_severity:
                continue
            lines.append(f"### {sev}")
            lines.append("")
            lines.append("| Source | Line | Type | Claim | Reason |")
            lines.append("|--------|------|------|-------|--------|")
            for r in by_severity[sev]:
                escaped = r.literal.replace("|", "\\|")[:60]
                reason = r.reason.replace("|", "\\|")
                lines.append(
                    f"| `{r.source_file}` | {r.line_number} | {r.claim_type} | `{escaped}` | {reason} |"
                )
            lines.append("")

    # Warnings
    if warned:
        lines.append("## Warnings")
        lines.append("")
        lines.append("| Source | Line | Type | Claim | Reason |")
        lines.append("|--------|------|------|-------|--------|")
        for r in warned:
            escaped = r.literal.replace("|", "\\|")[:60]
            reason = r.reason.replace("|", "\\|")
            lines.append(
                f"| `{r.source_file}` | {r.line_number} | {r.claim_type} | `{escaped}` | {reason} |"
            )
        lines.append("")

    return "\n".join(lines)


def generate_staleness_report(stale_results):
    """Generate a dedicated staleness section for the markdown report."""
    if not stale_results:
        return ""

    lines = [
        "",
        "## Likely Stale Claims (Git Drift Analysis)",
        "",
        "Claims that passed existence checks but whose targets changed significantly",
        "after the doc was last edited. Higher scores = more likely outdated.",
        "",
        "| Score | Drift | Source | Line | Type | Claim | Details |",
        "|-------|-------|--------|------|------|-------|---------|",
    ]

    for r in stale_results:
        score = r.details.get("staleness_score", 0)
        drift = r.details.get("drift", "?")
        targets = r.details.get("targets", {})
        # Build a compact details string
        detail_parts = []
        for tf, info in targets.items():
            detail_parts.append(
                f"{tf}: {info['commits_since_doc']} commits, {info['days_ahead']}d ahead"
            )
        detail_str = "; ".join(detail_parts[:2])
        if len(detail_parts) > 2:
            detail_str += f" (+{len(detail_parts) - 2} more)"

        escaped = r.literal.replace("|", "\\|")[:50]
        detail_str = detail_str.replace("|", "\\|")
        lines.append(
            f"| **{score}** | {drift} | `{r.source_file}` | {r.line_number} | {r.claim_type} | `{escaped}` | {detail_str} |"
        )

    lines.append("")
    return "\n".join(lines)


def generate_json_report(results, root):
    """Generate a JSON-formatted verification report."""
    report = {
        "project_root": str(root),
        "total_verified": len(results),
        "summary": {
            "passed": sum(1 for r in results if r.status == "pass"),
            "failed": sum(1 for r in results if r.status == "fail"),
            "warnings": sum(1 for r in results if r.status == "warn"),
            "skipped": sum(1 for r in results if r.status == "skip"),
        },
        "results": [asdict(r) for r in results if r.status != "pass"],
    }
    return json.dumps(report, indent=2)


# --- Main ---


def main():
    parser = argparse.ArgumentParser(description="Verify documentation claims")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--root", type=str, default=None, help="Project root path")
    parser.add_argument("--claims-file", type=str, default=None, help="JSON claims file from extractor")
    parser.add_argument("--check-urls", action="store_true", help="Enable URL verification")
    parser.add_argument("--check-staleness", action="store_true", help="Enable git-based staleness scoring")
    parser.add_argument(
        "--scope",
        choices=["docs", "manual", "all"],
        default="all",
        help="Passed to extractor if no claims-file",
    )
    args = parser.parse_args()

    root = get_project_root(args.root)

    # Load claims
    if args.claims_file:
        with open(args.claims_file) as f:
            data = json.load(f)
            claims = data["claims"]
    else:
        # Run extractor inline
        print("Running claim extractor...", file=sys.stderr)
        extractor_path = Path(__file__).parent / "extract_claims.py"
        result = subprocess.run(
            [sys.executable, str(extractor_path), "--json", "--root", str(root), "--scope", args.scope],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print(f"Extractor failed: {result.stderr}", file=sys.stderr)
            sys.exit(1)
        data = json.loads(result.stdout)
        claims = data["claims"]

    print(f"Verifying {len(claims)} claims...", file=sys.stderr)

    # Read dependency manifests once
    deps = read_dep_manifests(root)

    # Verify each claim
    results = []
    for claim in claims:
        ct = claim["claim_type"]

        if ct == "file_path":
            results.append(verify_file_path(claim, root))
        elif ct == "command":
            results.append(verify_command(claim, root))
        elif ct == "code_ref":
            results.append(verify_code_ref(claim, root))
        elif ct == "import":
            results.append(verify_import(claim, root, deps))
        elif ct == "config":
            results.append(verify_config(claim, root))
        elif ct == "url":
            if args.check_urls:
                results.append(verify_url(claim))
            else:
                results.append(VerificationResult(
                    claim_type=ct,
                    source_file=claim["source_file"],
                    line_number=claim["line_number"],
                    literal=claim["literal"],
                    status="skip",
                    reason="URL verification disabled (use --check-urls)",
                ))
        else:
            results.append(VerificationResult(
                claim_type=ct,
                source_file=claim["source_file"],
                line_number=claim["line_number"],
                literal=claim["literal"],
                status="skip",
                reason=f"No automated verifier for claim type: {ct}",
            ))

    # --- Staleness scoring pass ---
    stale_results = []
    if args.check_staleness:
        print("Running git staleness analysis...", file=sys.stderr)
        passed_results = [r for r in results if r.status == "pass"]
        # Build a map from (source_file, claim) -> target files for staleness
        claim_lookup = {
            (c["source_file"], c["line_number"], c["literal"]): c
            for c in claims
        }

        for r in passed_results:
            claim = claim_lookup.get((r.source_file, r.line_number, r.literal))
            if not claim:
                continue

            # Determine target files to check for drift
            target_files = []
            ct = r.claim_type

            if ct == "file_path":
                # The literal is the file path
                candidate = r.literal
                if (root / candidate).exists():
                    target_files.append(candidate)
                else:
                    # Try relative to source file
                    source_dir = Path(r.source_file).parent
                    rel = str(source_dir / candidate)
                    if (root / rel).exists():
                        target_files.append(rel)

            elif ct == "code_ref" and r.details.get("found_in"):
                # Use the files where the symbol was found
                for f in r.details["found_in"][:3]:
                    # grep -l output is relative paths
                    target_files.append(f)

            elif ct == "config" and r.details.get("found_in"):
                for f in r.details["found_in"][:3]:
                    target_files.append(f)

            elif ct == "command":
                # For script-path commands, check the script file
                literal = r.literal
                base_cmd = literal.split()[0]
                if "/" in base_cmd:
                    script = base_cmd.lstrip("./")
                    if (root / script).exists():
                        target_files.append(script)

            if not target_files:
                continue

            score, drift_details = compute_staleness(claim, target_files, root)
            label = staleness_label(score)

            if label:
                stale_results.append(VerificationResult(
                    claim_type=r.claim_type,
                    source_file=r.source_file,
                    line_number=r.line_number,
                    literal=r.literal,
                    status="stale",
                    reason=f"Target changed {score}x since doc was last edited (drift: {label})",
                    severity="P2" if label == "high" else "P3" if label == "medium" else "P4",
                    category="likely_stale",
                    details={"staleness_score": score, "drift": label, "targets": drift_details},
                ))

        if stale_results:
            # Sort stale results by score descending
            stale_results.sort(key=lambda r: -r.details.get("staleness_score", 0))
            print(f"  Found {len(stale_results)} likely stale claims.", file=sys.stderr)

    # Sort: failures first, then stale, then by severity
    severity_order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3, "P4": 4, "": 9}
    status_order = {"fail": 0, "warn": 1, "stale": 2, "skip": 3, "pass": 4}
    all_results = results + stale_results
    all_results.sort(key=lambda r: (
        status_order.get(r.status, 9),
        severity_order.get(r.severity, 9),
        r.source_file,
        r.line_number,
    ))

    # Output
    if args.json:
        print(generate_json_report(all_results, root))
    else:
        report = generate_markdown_report(all_results, root)
        if stale_results:
            report += generate_staleness_report(stale_results)
        print(report)

    # Summary to stderr
    failed = sum(1 for r in all_results if r.status == "fail")
    warned = sum(1 for r in all_results if r.status == "warn")
    passed = sum(1 for r in all_results if r.status == "pass")
    stale = sum(1 for r in all_results if r.status == "stale")
    parts = [f"{passed} passed", f"{failed} failed", f"{warned} warnings"]
    if stale:
        parts.append(f"{stale} likely stale")
    print(f"\nVerification complete: {', '.join(parts)}.", file=sys.stderr)

    # Exit code: non-zero if P0 or P1 failures
    has_critical = any(r.status == "fail" and r.severity in ("P0", "P1") for r in all_results)
    sys.exit(1 if has_critical else 0)


if __name__ == "__main__":
    main()
