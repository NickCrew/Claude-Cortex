#!/usr/bin/env python3
"""Verify specialist review findings against the actual codebase.

Reads one or more specialist JSON output files, validates every finding's
file path, line range, and quoted code against the real files on disk,
and emits only verified findings.

Usage:
    verify_citations.py <specialist-output.json> [specialist-output2.json ...]
    verify_citations.py --repo-root /path/to/repo <files...>
    verify_citations.py --test  # self-test

Output (stdout): JSON object with verified and rejected findings:
    {
        "verified": [...findings...],
        "rejected": [...findings with "reject_reason"...],
        "stats": {"total": 10, "verified": 8, "rejected": 2}
    }

Exit codes:
    0 — at least one finding verified (or no findings at all)
    1 — all findings rejected or input error
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def _normalize_whitespace(text: str) -> str:
    """Collapse whitespace for fuzzy code matching."""
    return re.sub(r"\s+", " ", text.strip())


def _read_file_lines(path: Path) -> Optional[List[str]]:
    """Read file lines, returning None if unreadable."""
    try:
        return path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return None


def verify_finding(
    finding: Dict[str, Any],
    repo_root: Path,
) -> Tuple[bool, str]:
    """Verify a single finding against the codebase.

    Returns (is_valid, reason).
    """
    file_path = finding.get("file", "")
    if not file_path:
        return False, "Missing 'file' field"

    # Resolve relative to repo root
    full_path = repo_root / file_path
    if not full_path.exists():
        return False, f"File not found: {file_path}"

    if not full_path.is_file():
        return False, f"Not a file: {file_path}"

    line_start = finding.get("line_start")
    line_end = finding.get("line_end")

    if line_start is None or line_end is None:
        return False, "Missing 'line_start' or 'line_end'"

    if not isinstance(line_start, int) or not isinstance(line_end, int):
        return False, "line_start/line_end must be integers"

    if line_start < 1:
        return False, f"line_start must be >= 1, got {line_start}"

    if line_end < line_start:
        return False, f"line_end ({line_end}) < line_start ({line_start})"

    lines = _read_file_lines(full_path)
    if lines is None:
        return False, f"Could not read file: {file_path}"

    total_lines = len(lines)
    if line_start > total_lines:
        return False, (
            f"line_start ({line_start}) exceeds file length ({total_lines})"
        )

    # Allow line_end to exceed slightly (off-by-one tolerance)
    if line_end > total_lines + 1:
        return False, (
            f"line_end ({line_end}) exceeds file length ({total_lines})"
        )

    quoted_code = finding.get("quoted_code", "")
    if not quoted_code:
        return False, "Missing 'quoted_code'"

    # Check quoted code appears near the cited line range.
    # Use a ±5 line window to tolerate minor line number drift.
    window_start = max(0, line_start - 6)  # 0-indexed, 5-line buffer
    window_end = min(total_lines, line_end + 5)
    window_text = "\n".join(lines[window_start:window_end])

    quoted_norm = _normalize_whitespace(quoted_code)
    window_norm = _normalize_whitespace(window_text)

    if quoted_norm not in window_norm:
        # Try line-by-line substring match as fallback
        # (handles cases where the quote is a single expression)
        found = False
        for line in lines[window_start:window_end]:
            if quoted_norm in _normalize_whitespace(line):
                found = True
                break
        if not found:
            return False, (
                f"Quoted code not found near lines {line_start}-{line_end} "
                f"(searched {window_start + 1}-{window_end})"
            )

    # Validate required fields based on severity
    severity = finding.get("severity", "")
    if severity in ("P0", "P1"):
        if not finding.get("suggested_fix"):
            return False, f"{severity} finding missing 'suggested_fix'"
    elif severity in ("P2", "P3"):
        if not finding.get("recommendation"):
            return False, f"{severity} finding missing 'recommendation'"

    return True, "OK"


def verify_all(
    findings: List[Dict[str, Any]],
    repo_root: Path,
) -> Dict[str, Any]:
    """Verify all findings and return verified/rejected split."""
    verified: List[Dict[str, Any]] = []
    rejected: List[Dict[str, Any]] = []

    for finding in findings:
        is_valid, reason = verify_finding(finding, repo_root)
        if is_valid:
            verified.append(finding)
        else:
            rejected_finding = dict(finding)
            rejected_finding["reject_reason"] = reason
            rejected.append(rejected_finding)

    return {
        "verified": verified,
        "rejected": rejected,
        "stats": {
            "total": len(findings),
            "verified": len(verified),
            "rejected": len(rejected),
        },
    }


def load_specialist_output(path: Path) -> List[Dict[str, Any]]:
    """Load findings from a specialist JSON output file."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"Warning: Invalid JSON in {path}: {exc}", file=sys.stderr)
        return []
    except OSError as exc:
        print(f"Warning: Cannot read {path}: {exc}", file=sys.stderr)
        return []

    # Handle both direct findings array and wrapped object
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        findings = data.get("findings", [])
        if isinstance(findings, list):
            return findings
    print(f"Warning: Unexpected format in {path}", file=sys.stderr)
    return []


def _detect_repo_root() -> Path:
    """Find the git repo root from CWD."""
    cwd = Path.cwd()
    for parent in [cwd, *cwd.parents]:
        if (parent / ".git").exists():
            return parent
    return cwd


# ── Self-test ──────────────────────────────────────────────────────


def _self_test() -> int:
    """Run built-in smoke tests using this file as the test subject."""
    this_file = Path(__file__)
    repo_root = _detect_repo_root()
    rel_path = this_file.relative_to(repo_root)

    lines = this_file.read_text().splitlines()
    # Pick a line we know exists
    sample_line = lines[0]  # "#!/usr/bin/env python3"

    tests = [
        (
            "valid finding",
            {
                "severity": "P2",
                "id": "P2-001",
                "title": "Test finding",
                "file": str(rel_path),
                "line_start": 1,
                "line_end": 1,
                "quoted_code": sample_line,
                "issue": "test",
                "impact": "test",
                "recommendation": "test",
            },
            True,
        ),
        (
            "nonexistent file",
            {
                "severity": "P1",
                "id": "P1-001",
                "title": "Ghost file",
                "file": "nonexistent/file.py",
                "line_start": 1,
                "line_end": 1,
                "quoted_code": "x = 1",
                "issue": "test",
                "impact": "test",
                "suggested_fix": "test",
            },
            False,
        ),
        (
            "wrong quoted code",
            {
                "severity": "P2",
                "id": "P2-001",
                "title": "Wrong quote",
                "file": str(rel_path),
                "line_start": 1,
                "line_end": 1,
                "quoted_code": "this code does not exist anywhere in the file xyz123",
                "issue": "test",
                "impact": "test",
                "recommendation": "test",
            },
            False,
        ),
        (
            "line out of range",
            {
                "severity": "P2",
                "id": "P2-001",
                "title": "Bad line",
                "file": str(rel_path),
                "line_start": 99999,
                "line_end": 99999,
                "quoted_code": sample_line,
                "issue": "test",
                "impact": "test",
                "recommendation": "test",
            },
            False,
        ),
        (
            "P0 missing suggested_fix",
            {
                "severity": "P0",
                "id": "P0-001",
                "title": "No fix",
                "file": str(rel_path),
                "line_start": 1,
                "line_end": 1,
                "quoted_code": sample_line,
                "issue": "test",
                "impact": "test",
            },
            False,
        ),
    ]

    passed = 0
    for label, finding, expected_valid in tests:
        is_valid, reason = verify_finding(finding, repo_root)
        if is_valid == expected_valid:
            status = "PASS"
            passed += 1
        else:
            status = "FAIL"
        detail = "OK" if is_valid else reason
        print(f"  {status}: {label} → valid={is_valid} ({detail})")

    print(f"\n{passed}/{len(tests)} tests passed.")
    return 0 if passed == len(tests) else 1


# ── CLI ────────────────────────────────────────────────────────────


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__, file=sys.stderr)
        return 1

    if sys.argv[1] == "--test":
        return _self_test()

    # Parse --repo-root if provided
    args = sys.argv[1:]
    repo_root = _detect_repo_root()
    if args[0] == "--repo-root":
        if len(args) < 3:
            print("Error: --repo-root requires a path and at least one file",
                  file=sys.stderr)
            return 1
        repo_root = Path(args[1])
        args = args[2:]

    # Load all specialist outputs
    all_findings: List[Dict[str, Any]] = []
    for arg in args:
        path = Path(arg)
        findings = load_specialist_output(path)
        all_findings.extend(findings)
        if findings:
            perspective = findings[0].get("perspective", "unknown")
            print(
                f"Loaded {len(findings)} findings from {path.name} "
                f"({perspective})",
                file=sys.stderr,
            )

    if not all_findings:
        # No findings is valid (clean review)
        result = {"verified": [], "rejected": [], "stats": {
            "total": 0, "verified": 0, "rejected": 0,
        }}
        json.dump(result, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0

    result = verify_all(all_findings, repo_root)

    stats = result["stats"]
    print(
        f"Verification: {stats['verified']}/{stats['total']} findings verified, "
        f"{stats['rejected']} rejected",
        file=sys.stderr,
    )
    for r in result["rejected"]:
        print(
            f"  REJECTED: {r.get('id', '?')} in {r.get('file', '?')} — "
            f"{r.get('reject_reason', '?')}",
            file=sys.stderr,
        )

    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")

    # Exit 1 only if ALL findings were rejected (indicates hallucination)
    if stats["verified"] == 0 and stats["total"] > 0:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
