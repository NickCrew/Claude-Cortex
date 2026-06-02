#!/usr/bin/env python3
"""Synthesize two agent-loops review artifacts into one contract artifact."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def section(text: str, start: str, end: str) -> str:
    match = re.search(
        rf"^{re.escape(start)}\s*\n(?P<body>.*?)(?=^{re.escape(end)}\s*$)",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    if not match:
        return "_No section content found._"
    body = match.group("body").strip()
    return body or "_No findings._"


def first_line(text: str, label: str, fallback: str) -> str:
    match = re.search(
        rf"^{re.escape(label)}\s*(?P<value>.+)$", text, flags=re.MULTILINE
    )
    return match.group("value").strip() if match else fallback


def code_count(text: str, severity: str) -> int:
    match = re.search(
        rf"^- {severity}: (?P<count>\d+) findings", text, flags=re.MULTILINE
    )
    return int(match.group("count")) if match else 0


def audit_count(text: str, label: str) -> int:
    match = re.search(
        rf"^- {re.escape(label)}: (?P<count>\d+)\s*$", text, flags=re.MULTILINE
    )
    return int(match.group("count")) if match else 0


def behavior_rows(text: str, provider: str) -> list[str]:
    body = section(text, "### Behavior Inventory", "### Prioritized Gaps")
    rows: list[str] = []
    for line in body.splitlines():
        stripped = line.strip()
        content = stripped.strip("|").strip()
        if not stripped.startswith("|") or not content:
            continue
        if re.match(r"(?i)^behavior\s*\|\s*coverage", content):
            continue
        if re.fullmatch(r"\|[\s\-:|]+", stripped):
            continue
        row_content = stripped[:-1].rstrip() if stripped.endswith("|") else stripped
        rows.append(f"{row_content} ({provider}) |")
    return rows


def code_verdict(text: str) -> str:
    match = re.search(
        r"^- \*\*Verdict:\*\* (?P<verdict>BLOCKED|PASS WITH ISSUES|CLEAN)\s*$",
        text,
        flags=re.MULTILINE,
    )
    return match.group("verdict") if match else "PASS WITH ISSUES"


def synthesize_code_review(args: argparse.Namespace) -> str:
    primary = read_text(args.primary)
    secondary = read_text(args.secondary)
    counts = {
        severity: code_count(primary, severity) + code_count(secondary, severity)
        for severity in ("P0", "P1", "P2", "P3")
    }

    verdicts = {code_verdict(primary), code_verdict(secondary)}
    if counts["P0"] or counts["P1"] or "BLOCKED" in verdicts:
        verdict = "BLOCKED"
    elif counts["P2"] or counts["P3"] or "PASS WITH ISSUES" in verdicts:
        verdict = "PASS WITH ISSUES"
    else:
        verdict = "CLEAN"

    files = first_line(primary, "**Files reviewed:**", args.files_reviewed)
    iteration = first_line(primary, "**Iteration:**", "1 of 3")
    primary_findings = section(primary, "### Findings", "### Summary")
    secondary_findings = section(secondary, "### Findings", "### Summary")

    return f"""## Code Review: dual reviewer synthesis

**Files reviewed:** {files}
**Iteration:** {iteration}
**Review mode:** primary={args.primary_provider}, secondary={args.secondary_provider}
**Primary artifact:** `{args.primary}`
**Secondary artifact:** `{args.secondary}`

### Findings

#### Primary Review ({args.primary_provider})
{primary_findings}

#### Secondary Review ({args.secondary_provider})
{secondary_findings}

### Summary
- P0: {counts["P0"]} findings (MUST fix)
- P1: {counts["P1"]} findings (MUST fix)
- P2: {counts["P2"]} findings (file issues)
- P3: {counts["P3"]} findings (file issues)
- **Verdict:** {verdict}
"""


def synthesize_test_audit(args: argparse.Namespace) -> str:
    primary = read_text(args.primary)
    secondary = read_text(args.secondary)
    counts = {
        label: audit_count(primary, label) + audit_count(secondary, label)
        for label in ("Covered", "Shallow", "Missing", "P0", "P1", "P2")
    }
    rows = behavior_rows(primary, args.primary_provider) + behavior_rows(
        secondary, args.secondary_provider
    )
    if not rows:
        rows = [
            f"| Primary audit artifact | Covered | `{args.primary}` ({args.primary_provider}) |",
            f"| Secondary audit artifact | Covered | `{args.secondary}` ({args.secondary_provider}) |",
        ]
    behavior_table = "\n".join(rows)
    module = first_line(primary, "**Module:**", args.module or "(see primary artifact)")
    tests = first_line(primary, "**Tests:**", args.tests or "(see primary artifact)")
    mode = first_line(primary, "**Mode:**", args.audit_mode or "full")
    primary_gaps = section(primary, "### Prioritized Gaps", "### Summary")
    secondary_gaps = section(secondary, "### Prioritized Gaps", "### Summary")

    return f"""## Test Gap Report: dual reviewer synthesis

**Module:** {module}
**Tests:** {tests}
**Mode:** {mode}
**Review mode:** primary={args.primary_provider}, secondary={args.secondary_provider}
**Primary artifact:** `{args.primary}`
**Secondary artifact:** `{args.secondary}`

### Behavior Inventory

| Behavior | Coverage | Evidence |
|----------|----------|----------|
{behavior_table}

### Prioritized Gaps

#### Primary Audit ({args.primary_provider})
{primary_gaps}

#### Secondary Audit ({args.secondary_provider})
{secondary_gaps}

### Summary
- Covered: {counts["Covered"]}
- Shallow: {counts["Shallow"]}
- Missing: {counts["Missing"]}
- P0: {counts["P0"]}
- P1: {counts["P1"]}
- P2: {counts["P2"]}
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("code-review", "test-audit"))
    parser.add_argument("--primary", type=Path, required=True)
    parser.add_argument("--secondary", type=Path, required=True)
    parser.add_argument("--primary-provider", required=True)
    parser.add_argument("--secondary-provider", required=True)
    parser.add_argument("--files-reviewed", default="(see primary artifact)")
    parser.add_argument("--module", default="(see primary artifact)")
    parser.add_argument("--tests", default="(see primary artifact)")
    parser.add_argument("--audit-mode", default="full")
    args = parser.parse_args()

    if args.mode == "code-review":
        print(synthesize_code_review(args), end="")
    else:
        print(synthesize_test_audit(args), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
