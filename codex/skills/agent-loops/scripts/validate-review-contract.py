#!/usr/bin/env python3
"""Validate agent-loops review and audit artifact contracts."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


def _require(pattern: str, text: str, message: str) -> None:
    if not re.search(pattern, text, flags=re.MULTILINE):
        raise SystemExit(message)


def validate_code_review(text: str) -> None:
    _require(r"^## Code Review:", text, "Missing '## Code Review:' heading")
    _require(r"^\*\*Files reviewed:\*\*", text, "Missing '**Files reviewed:**' line")
    _require(r"^\*\*Iteration:\*\*", text, "Missing '**Iteration:**' line")
    _require(r"^### Findings$", text, "Missing '### Findings' section")
    _require(r"^### Summary$", text, "Missing '### Summary' section")
    _require(r"^- P0: \d+ findings \(MUST fix\)$", text, "Missing P0 summary line")
    _require(r"^- P1: \d+ findings \(MUST fix\)$", text, "Missing P1 summary line")
    _require(r"^- P2: \d+ findings \(file issues\)$", text, "Missing P2 summary line")
    _require(r"^- P3: \d+ findings \(file issues\)$", text, "Missing P3 summary line")
    _require(
        r"^- \*\*Verdict:\*\* (BLOCKED|PASS WITH ISSUES|CLEAN)$",
        text,
        "Missing or invalid verdict line",
    )


def validate_test_audit(text: str) -> None:
    _require(r"^## Test Gap Report:", text, "Missing '## Test Gap Report:' heading")
    _require(r"^\*\*Module:\*\*", text, "Missing '**Module:**' line")
    _require(r"^\*\*Tests:\*\*", text, "Missing '**Tests:**' line")
    _require(r"^\*\*Mode:\*\*", text, "Missing '**Mode:**' line")
    _require(r"^### Behavior Inventory$", text, "Missing '### Behavior Inventory' section")
    _require(r"^### Prioritized Gaps$", text, "Missing '### Prioritized Gaps' section")
    _require(r"^### Summary$", text, "Missing '### Summary' section")
    _require(r"^\| Behavior \| Coverage \| Evidence \|$", text, "Missing behavior table header")
    _require(r"^- Covered: \d+$", text, "Missing covered summary line")
    _require(r"^- Shallow: \d+$", text, "Missing shallow summary line")
    _require(r"^- Missing: \d+$", text, "Missing missing summary line")
    _require(r"^- P0: \d+$", text, "Missing P0 summary line")
    _require(r"^- P1: \d+$", text, "Missing P1 summary line")
    _require(r"^- P2: \d+$", text, "Missing P2 summary line")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate review or audit contract")
    parser.add_argument("mode", choices=("code-review", "test-audit"))
    parser.add_argument("artifact")
    args = parser.parse_args()

    text = Path(args.artifact).read_text(encoding="utf-8")
    if args.mode == "code-review":
        validate_code_review(text)
    else:
        validate_test_audit(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
