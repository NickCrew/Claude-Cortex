#!/usr/bin/env python3
"""Deterministic perspective triage for multi-specialist code review.

Selects 3-5 review perspectives based on file extensions and content
signals in a diff.  Zero API cost — pure heuristics from the perspective
catalog selection rules.

Usage:
    triage_perspectives.py <diff-file>
    triage_perspectives.py -            # read from stdin
    triage_perspectives.py --test       # self-test with sample diffs

Output (stdout): JSON object with selected perspectives and metadata:
    {
        "perspectives": ["correctness", "security", "maintainability"],
        "signals": {"security": ["auth", "password"]},
        "file_types": [".py", ".sql"]
    }
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Set, Tuple


# ── Perspective definitions ────────────────────────────────────────

@dataclass
class Perspective:
    """A review perspective with its trigger rules."""

    name: str
    display_name: str
    focus: str
    file_extensions: Set[str] = field(default_factory=set)
    file_patterns: List[str] = field(default_factory=list)
    content_signals: List[str] = field(default_factory=list)
    always_include: bool = False


PERSPECTIVES: List[Perspective] = [
    Perspective(
        name="correctness",
        display_name="Correctness",
        focus=(
            "Logic errors, off-by-one, null/undefined handling, edge cases, "
            "race conditions, contract violations, type mismatches, "
            "incomplete error propagation."
        ),
        always_include=True,
    ),
    Perspective(
        name="maintainability",
        display_name="Maintainability",
        focus=(
            "Naming clarity, single responsibility, DRY violations, "
            "cognitive complexity, dead code, unclear intent, "
            "over-abstraction, under-abstraction."
        ),
        always_include=True,
    ),
    Perspective(
        name="security",
        display_name="Security",
        focus=(
            "Injection, auth bypass, data exposure, input validation, "
            "secrets handling, crypto, HTTP headers, CORS, cookie handling."
        ),
        content_signals=[
            r"\bauth\b", r"\blogin\b", r"\bpassword\b", r"\btoken\b",
            r"\bsecret\b", r"\bapi.?key\b", r"\bcredential\b",
            r"\bcookie\b", r"\bsession\b", r"\bcors\b", r"\bcrypt\b",
            r"\bhash\b", r"\bsalt\b", r"\bjwt\b", r"\boauth\b",
            r"\bsanitiz", r"\bescape\b", r"\bxss\b", r"\bcsrf\b",
            r"\bsql\b", r"\binjection\b", r"\bpermission\b",
            r"\brole\b", r"\baccess.?control\b",
            r"\bexecute\b.*\bquery\b", r"\beval\b", r"\bexec\b",
        ],
    ),
    Perspective(
        name="performance",
        display_name="Performance",
        focus=(
            "N+1 queries, unnecessary allocations, algorithmic complexity, "
            "caching, batch operations, rendering paths, memory leaks."
        ),
        file_extensions={".py", ".rs", ".go", ".java", ".tsx", ".jsx"},
        content_signals=[
            r"\bfor\b.*\bin\b.*\bquery\b", r"\bSELECT\b",
            r"\bINSERT\b", r"\bUPDATE\b", r"\bDELETE\b",
            r"\bcache\b", r"\bmemoiz", r"\bO\(n",
            r"\balloc", r"\bbuffer\b", r"\bpool\b",
            r"\basync\b.*\bfor\b", r"\bawait\b.*\bloop\b",
            r"\bsetInterval\b", r"\bsetTimeout\b",
            r"\buseEffect\b", r"\buseMemo\b", r"\buseCallback\b",
            r"\brender\b", r"\bre-?render\b",
        ],
    ),
    Perspective(
        name="testing",
        display_name="Testing",
        focus=(
            "Test coverage gaps, assertion quality, edge case coverage, "
            "test isolation, mock appropriateness, flaky tests."
        ),
        file_patterns=[r"test[_.]", r"spec[_.]", r"__tests__"],
        content_signals=[
            r"\btest_\w+", r"\bdescribe\b", r"\bit\b\(",
            r"\bexpect\b", r"\bassert\b", r"\bmock\b",
            r"\bpatch\b", r"\bfixture\b", r"\bpytest\b",
            r"\bjest\b", r"\bvitest\b",
        ],
    ),
    Perspective(
        name="architecture",
        display_name="Architecture",
        focus=(
            "Layer violations, coupling direction, dependency inversion, "
            "interface segregation, domain boundaries, circular deps."
        ),
        content_signals=[
            r"\bimport\b.*\bfrom\b", r"\brequire\b",
            r"\binterface\b", r"\bprotocol\b", r"\babstract\b",
            r"\bfactory\b", r"\brepository\b", r"\bservice\b",
            r"\bcontroller\b", r"\bmiddleware\b", r"\bprovider\b",
            r"\bdependency\b", r"\binject\b",
        ],
    ),
    Perspective(
        name="infrastructure",
        display_name="Infrastructure",
        focus=(
            "Resource misconfiguration, missing limits/quotas, "
            "insecure defaults, state management, drift potential."
        ),
        file_extensions={".tf", ".hcl", ".yaml", ".yml"},
        file_patterns=[
            r"Dockerfile", r"docker-compose",
            r"\.github/workflows/", r"\.gitlab-ci",
            r"Jenkinsfile", r"k8s/", r"kubernetes/",
            r"helm/", r"charts/",
        ],
    ),
    Perspective(
        name="api-contract",
        display_name="API Contract",
        focus=(
            "Breaking changes, backwards compatibility, error response "
            "consistency, pagination, auth headers, rate limiting."
        ),
        content_signals=[
            r"\bendpoint\b", r"\broute\b", r"\bapi\b",
            r"\bstatus.?code\b", r"\b[45]\d{2}\b",
            r"\bschema\b", r"\bserializ", r"\bdeserializ",
            r"\bswagger\b", r"\bopenapi\b",
            r"\bGraphQL\b", r"\bquery\b.*\bmutation\b",
            r"\bpaginat", r"\bcursor\b", r"\boffset\b",
            r"\bContent-Type\b", r"\bAccept\b",
        ],
    ),
    Perspective(
        name="accessibility",
        display_name="Accessibility",
        focus=(
            "WCAG 2.2 AA, keyboard navigation, screen reader "
            "compatibility, color contrast, semantic HTML, focus management."
        ),
        file_extensions={".tsx", ".jsx", ".html", ".vue", ".svelte"},
        content_signals=[
            r"\baria-", r"\brole=", r"\btabindex\b",
            r"\balt=", r"\bsr-only\b", r"\bscreen.?reader\b",
            r"\bfocus\b", r"\bkeyboard\b", r"\ba11y\b",
            r"\baccessib", r"\bwcag\b",
        ],
    ),
    Perspective(
        name="ux-design",
        display_name="UX / Design",
        focus=(
            "User flow, error messaging, loading/empty states, "
            "progressive disclosure, interaction feedback, visual consistency."
        ),
        file_extensions={".tsx", ".jsx", ".vue", ".svelte", ".css", ".scss"},
        content_signals=[
            r"\bloading\b", r"\bspinner\b", r"\bskeleton\b",
            r"\bempty.?state\b", r"\berror.?message\b",
            r"\btoast\b", r"\bnotif", r"\bmodal\b",
            r"\bdialog\b", r"\bform\b", r"\binput\b",
            r"\bbutton\b", r"\bsubmit\b",
        ],
    ),
]

_PERSPECTIVE_MAP: Dict[str, Perspective] = {p.name: p for p in PERSPECTIVES}

MAX_PERSPECTIVES = 5


# ── Diff parsing ───────────────────────────────────────────────────

_DIFF_FILE_RE = re.compile(r"^(?:diff --git a/.+ b/|[+]{3} b/)(.+)$", re.MULTILINE)


def _extract_changed_files(diff_text: str) -> List[str]:
    """Extract file paths from a unified diff."""
    return _DIFF_FILE_RE.findall(diff_text)


def _extract_extensions(files: List[str]) -> Set[str]:
    """Extract unique file extensions from paths."""
    exts: Set[str] = set()
    for f in files:
        ext = Path(f).suffix.lower()
        if ext:
            exts.add(ext)
    return exts


# ── Triage logic ───────────────────────────────────────────────────


def _score_perspective(
    perspective: Perspective,
    diff_text: str,
    changed_files: List[str],
    file_extensions: Set[str],
) -> Tuple[float, List[str]]:
    """Score a perspective's relevance.  Returns (score, matched_signals)."""
    if perspective.always_include:
        return (100.0, [])

    score = 0.0
    matched: List[str] = []

    # File extension matches
    if perspective.file_extensions:
        overlap = perspective.file_extensions & file_extensions
        if overlap:
            score += 20.0 * len(overlap)
            matched.extend(f"ext:{e}" for e in sorted(overlap))

    # File pattern matches
    for pattern in perspective.file_patterns:
        for f in changed_files:
            if re.search(pattern, f, re.IGNORECASE):
                score += 15.0
                matched.append(f"file:{pattern}")
                break

    # Content signal matches (sample first 50k chars to bound cost)
    sample = diff_text[:50000]
    for signal in perspective.content_signals:
        hits = len(re.findall(signal, sample, re.IGNORECASE))
        if hits > 0:
            # Diminishing returns: first hit is worth most
            score += min(10.0, 5.0 + hits * 2.0)
            matched.append(signal.replace(r"\b", "").replace("\\", ""))

    return (score, matched)


def triage(diff_text: str) -> Dict[str, object]:
    """Select perspectives for a diff.

    Returns a dict with:
      - perspectives: list of perspective names (3-5)
      - signals: dict of perspective → matched signals
      - file_types: list of detected extensions
      - changed_files: list of changed file paths
    """
    changed_files = _extract_changed_files(diff_text)
    file_extensions = _extract_extensions(changed_files)

    # Score all perspectives
    scored: List[Tuple[float, Perspective, List[str]]] = []
    for p in PERSPECTIVES:
        score, signals = _score_perspective(
            p, diff_text, changed_files, file_extensions
        )
        scored.append((score, p, signals))

    # Sort by score descending
    scored.sort(key=lambda x: x[0], reverse=True)

    # Always-include perspectives first, then top conditional ones
    selected: List[Perspective] = []
    signals_map: Dict[str, List[str]] = {}

    for score, p, signals in scored:
        if p.always_include:
            selected.append(p)
            if signals:
                signals_map[p.name] = signals

    for score, p, signals in scored:
        if p.always_include:
            continue
        if score <= 0:
            continue
        if len(selected) >= MAX_PERSPECTIVES:
            break
        selected.append(p)
        if signals:
            signals_map[p.name] = signals

    # Ensure at least 3 perspectives by adding top conditional ones
    if len(selected) < 3:
        for score, p, signals in scored:
            if p not in selected:
                selected.append(p)
                if signals:
                    signals_map[p.name] = signals
                if len(selected) >= 3:
                    break

    return {
        "perspectives": [p.name for p in selected],
        "display_names": {p.name: p.display_name for p in selected},
        "focus_areas": {p.name: p.focus for p in selected},
        "signals": signals_map,
        "file_types": sorted(file_extensions),
        "changed_files": changed_files,
    }


# ── CLI ────────────────────────────────────────────────────────────


def _self_test() -> int:
    """Run built-in smoke tests."""
    cases = [
        (
            "Python auth change",
            "diff --git a/src/auth.py b/src/auth.py\n"
            "+++ b/src/auth.py\n"
            "+def verify_token(jwt_token: str) -> bool:\n"
            "+    password = get_secret('db_password')\n",
            {"correctness", "maintainability", "security"},
        ),
        (
            "React component",
            "diff --git a/src/Button.tsx b/src/Button.tsx\n"
            "+++ b/src/Button.tsx\n"
            "+export function Button({ onClick }: Props) {\n"
            "+  return <button role='button' aria-label='Submit'>{children}</button>\n",
            {"correctness", "maintainability", "accessibility"},
        ),
        (
            "Terraform change",
            "diff --git a/infra/main.tf b/infra/main.tf\n"
            "+++ b/infra/main.tf\n"
            "+resource \"aws_s3_bucket\" \"data\" {\n",
            {"correctness", "maintainability", "infrastructure"},
        ),
        (
            "Test file",
            "diff --git a/tests/test_parser.py b/tests/test_parser.py\n"
            "+++ b/tests/test_parser.py\n"
            "+def test_parse_empty():\n"
            "+    assert parse('') == []\n",
            {"correctness", "maintainability", "testing"},
        ),
    ]

    passed = 0
    for label, diff, expected_subset in cases:
        result = triage(diff)
        selected = set(result["perspectives"])
        if expected_subset <= selected:
            print(f"  PASS: {label} → {result['perspectives']}")
            passed += 1
        else:
            missing = expected_subset - selected
            print(f"  FAIL: {label} → {result['perspectives']}  (missing: {missing})")

    print(f"\n{passed}/{len(cases)} tests passed.")
    return 0 if passed == len(cases) else 1


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__, file=sys.stderr)
        return 1

    if sys.argv[1] == "--test":
        return _self_test()

    if sys.argv[1] == "-":
        diff_text = sys.stdin.read()
    else:
        path = Path(sys.argv[1])
        if not path.exists():
            print(f"Error: File not found: {path}", file=sys.stderr)
            return 1
        diff_text = path.read_text(encoding="utf-8", errors="replace")

    if not diff_text.strip():
        print("Error: Empty diff.", file=sys.stderr)
        return 1

    result = triage(diff_text)
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
