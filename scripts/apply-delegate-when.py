#!/usr/bin/env python3
"""First-pass: tag select agents with ``delegate_when:`` values.

The mapping below encodes a conservative taxonomy — only agents where
delegation is clearly a good mode are tagged. Everything else stays empty
(consultation-only), which is the safer default.

Idempotent — running twice leaves existing ``delegate_when:`` values intact
and never duplicates the block.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Dict, List

REPO_ROOT = Path(__file__).resolve().parent.parent
AGENTS_ROOT = REPO_ROOT / "agents"

# Mapping: agent name -> list of delegate_when values.
# Valid values: isolation, independence, parallel, large_scope
DELEGATE_WHEN: Dict[str, List[str]] = {
    # Review/audit agents — fresh eyes are the point.
    "code-reviewer": ["independence"],
    "security-auditor": ["independence", "isolation"],
    "performance-monitor": ["independence", "isolation"],
    "frontend-optimizer": ["independence"],
    "database-optimizer": ["independence"],
    "test-automator": ["independence"],
    # Reads many files, produces synthesis.
    "docs-architect": ["isolation", "large_scope"],
    # Parallelization is its whole purpose.
    "orchestrator": ["parallel"],
}


def apply(agent_md: Path, values: List[str]) -> bool:
    text = agent_md.read_text(encoding="utf-8")
    stripped = text.lstrip()
    if not stripped.startswith("---"):
        return False
    after_first = stripped[3:]
    end_match = re.search(r"\n---", after_first)
    if not end_match:
        return False
    leading_len = len(text) - len(stripped)
    leading = text[:leading_len]
    fm_text = after_first[: end_match.start()]
    closing_onwards = after_first[end_match.start():]

    if re.search(r"^delegate_when:", fm_text, re.MULTILINE):
        return False  # already has it; don't duplicate

    # Append the delegate_when block to the front matter.
    block_lines = ["delegate_when:"]
    for v in values:
        block_lines.append(f"  - {v}")
    block = "\n".join(block_lines)
    new_fm = fm_text.rstrip() + "\n" + block + "\n"
    new_text = f"{leading}---{new_fm}{closing_onwards}"
    agent_md.write_text(new_text, encoding="utf-8")
    return True


def main() -> int:
    missing: List[str] = []
    written = 0
    for name, values in DELEGATE_WHEN.items():
        agent_md = AGENTS_ROOT / f"{name}.md"
        if not agent_md.exists():
            missing.append(name)
            continue
        if apply(agent_md, values):
            written += 1

    if missing:
        print(f"WARNING: {len(missing)} agents missing:")
        for n in missing:
            print(f"  - {n}")

    print(f"Tagged {written} agent(s) with delegate_when.")
    print(f"Total consultation-only (untouched): {28 - len(DELEGATE_WHEN)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
