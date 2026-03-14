"""Parse specialist review outcomes and feed into SkillRecommender learning.

Extracts which review perspectives found actionable issues, maps them to skills
via the perspective catalog, and records successes so future recommendations
improve automatically. Best-effort only — failures never block the review pipeline.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class ReviewFinding:
    """A single finding from a specialist review."""

    perspective: str
    finding_id: str
    severity: str
    file_path: str
    title: str


@dataclass
class ParsedReview:
    """Structured representation of a parsed specialist review."""

    perspectives_selected: List[str]
    findings: List[ReviewFinding]
    findings_by_perspective: Dict[str, List[ReviewFinding]]
    verdict: str
    file_paths: List[str]


# Maps perspective names (lowercase) to skill lists.
# Derived from skills/agent-loops/references/perspective-catalog.md
PERSPECTIVE_SKILL_MAP: Dict[str, List[str]] = {
    "correctness": [],
    "security": [
        "owasp-top-10",
        "secure-coding-practices",
        "threat-modeling-techniques",
        "security-testing-patterns",
    ],
    "performance": [
        "python-performance-optimization",
        "react-performance-optimization",
        "workflow-performance",
        "database-design-patterns",
    ],
    "maintainability": [
        "code-quality-workflow",
    ],
    "testing": [
        "python-testing-patterns",
        "test-generation",
        "test-driven-development",
        "testing-anti-patterns",
    ],
    "architecture": [
        "system-design",
        "api-design-patterns",
        "microservices-patterns",
        "event-driven-architecture",
    ],
    "infrastructure": [
        "terraform-best-practices",
        "kubernetes-deployment-patterns",
        "kubernetes-security-policies",
        "helm-chart-patterns",
        "gitops-workflows",
    ],
    "api contract": [
        "api-design-patterns",
        "api-gateway-patterns",
    ],
    "accessibility": [
        "accessibility-audit",
    ],
    "ux / design": [
        "ux-review",
        "ui-design-aesthetics",
    ],
    # Alternate names that appear in review headers
    "configuration consistency": [],
}


def _extract_perspectives(content: str) -> List[str]:
    """Extract selected perspective names from review content.

    Handles two formats:
    - Numbered bold: ``1. **Correctness** — description``
    - Specialists line: ``**Specialists**: Security, Architecture, Config``
    """
    perspectives: List[str] = []

    # Format 1: numbered bold perspectives in triage section
    # e.g. "1. **Correctness** —" or "2. **Security** —"
    for m in re.finditer(r"^\d+\.\s+\*\*([^*]+)\*\*\s*[—–-]", content, re.MULTILINE):
        perspectives.append(m.group(1).strip().lower())

    # Format 2: specialists line
    # e.g. "**Specialists**: Security, Architecture, Configuration Consistency"
    m = re.search(r"\*\*Specialists?\*\*\s*:\s*(.+)", content)
    if m:
        for name in m.group(1).split(","):
            name = name.strip().lower()
            if name:
                perspectives.append(name)

    # Deduplicate while preserving order
    seen: set[str] = set()
    unique: List[str] = []
    for p in perspectives:
        if p not in seen:
            seen.add(p)
            unique.append(p)

    return unique


def _extract_findings(content: str) -> List[ReviewFinding]:
    """Extract findings from review content.

    Handles both ID schemes:
    - Letter prefix: ``C-1``, ``S-1``, ``M-1``, ``A-1``
    - Priority prefix: ``P0-1``, ``P1-1``, ``P2-1``
    """
    findings: List[ReviewFinding] = []

    # Map letter prefixes to perspective names
    prefix_map = {
        "C": "correctness",
        "S": "security",
        "P": "performance",
        "M": "maintainability",
        "T": "testing",
        "A": "architecture",
        "I": "infrastructure",
        "AC": "accessibility",
        "U": "ux / design",
    }

    # Pattern for letter-prefix findings: ### C-1: Title
    for m in re.finditer(
        r"^###\s+([A-Z]{1,2})-(\d+)\s*:\s*(.+)",
        content,
        re.MULTILINE,
    ):
        prefix = m.group(1)
        finding_id = f"{prefix}-{m.group(2)}"
        title = m.group(3).strip()
        perspective = prefix_map.get(prefix, prefix.lower())

        # Look for severity on a nearby line
        severity = _find_severity_near(content, m.end())

        # Look for file path on a nearby line
        file_path = _find_file_near(content, m.end())

        findings.append(ReviewFinding(
            perspective=perspective,
            finding_id=finding_id,
            severity=severity,
            file_path=file_path,
            title=title,
        ))

    # Pattern for priority-prefix findings: #### P0-1: Title
    for m in re.finditer(
        r"^#{3,4}\s+P(\d)-(\d+)\s*:\s*(.+)",
        content,
        re.MULTILINE,
    ):
        priority = m.group(1)
        finding_id = f"P{priority}-{m.group(2)}"
        title = m.group(3).strip()
        # P-prefix reviews don't consistently map to a single perspective
        perspective = f"p{priority}"

        severity = _find_severity_near(content, m.end())
        file_path = _find_file_near(content, m.end())

        findings.append(ReviewFinding(
            perspective=perspective,
            finding_id=finding_id,
            severity=severity,
            file_path=file_path,
            title=title,
        ))

    return findings


def _find_severity_near(content: str, pos: int) -> str:
    """Find severity annotation near a position in the content."""
    # Look within the next 300 chars for a severity line
    snippet = content[pos:pos + 300]
    m = re.search(r"\*\*Severity:?\*\*\s*(\w+)", snippet)
    if m:
        return m.group(1).upper()
    return "UNKNOWN"


def _find_file_near(content: str, pos: int) -> str:
    """Find file path annotation near a position in the content."""
    snippet = content[pos:pos + 300]
    # **File:** `path` or **File**: `path`
    m = re.search(r"\*\*Files?:?\*\*\s*:?\s*`([^`]+)`", snippet)
    if m:
        # Strip line number suffix (e.g. :59-67)
        path = re.sub(r":\d+.*$", "", m.group(1))
        return path
    return ""


def _extract_verdict(content: str) -> str:
    """Extract the review verdict.

    Returns one of: APPROVE, APPROVE WITH CHANGES, REQUEST CHANGES, UNKNOWN
    """
    # Look for explicit verdict line, e.g. "**APPROVE WITH CHANGES**"
    m = re.search(
        r"\*\*(APPROVE WITH CHANGES|REQUEST CHANGES|APPROVE)\*\*",
        content,
        re.IGNORECASE,
    )
    if m:
        return m.group(1).upper()

    # Fallback: look for verdict in a "Verdict" section header
    m = re.search(
        r"(?:^|\n)#+\s*Verdict\s*\n+\s*\*?\*?(APPROVE WITH CHANGES|REQUEST CHANGES|APPROVE)\*?\*?",
        content,
        re.IGNORECASE,
    )
    if m:
        return m.group(1).upper()

    return "UNKNOWN"


def _extract_file_paths(content: str) -> List[str]:
    """Extract file paths from ``**File:** `path` `` annotations."""
    paths: List[str] = []
    for m in re.finditer(r"\*\*Files?:?\*\*\s*:?\s*`([^`]+)`", content):
        raw = m.group(1)
        # Strip line numbers (e.g. :59-67, :130-150)
        path = re.sub(r":\d+.*$", "", raw)
        if path and path not in paths:
            paths.append(path)
    return paths


def parse_review(content: str) -> ParsedReview:
    """Parse a specialist review markdown into structured data."""
    perspectives = _extract_perspectives(content)
    findings = _extract_findings(content)
    verdict = _extract_verdict(content)
    file_paths = _extract_file_paths(content)

    # Group findings by perspective
    by_perspective: Dict[str, List[ReviewFinding]] = {}
    for f in findings:
        by_perspective.setdefault(f.perspective, []).append(f)

    return ParsedReview(
        perspectives_selected=perspectives,
        findings=findings,
        findings_by_perspective=by_perspective,
        verdict=verdict,
        file_paths=file_paths,
    )


def ingest_review(
    review_path: Path,
    home: Optional[Path] = None,
) -> Dict[str, object]:
    """Ingest a specialist review and feed outcomes into skill learning.

    Args:
        review_path: Path to review markdown file
        home: Optional home directory for SkillRecommender

    Returns:
        Summary dict with keys: verdict, perspectives_found, skills_recorded
    """
    content = review_path.read_text(encoding="utf-8")
    parsed = parse_review(content)

    # Identify productive perspectives (those with findings)
    productive_perspectives = [
        p for p in parsed.perspectives_selected
        if p in parsed.findings_by_perspective
    ]

    # Map productive perspectives to skills
    skills: List[str] = []
    for perspective in productive_perspectives:
        mapped = PERSPECTIVE_SKILL_MAP.get(perspective, [])
        for skill in mapped:
            if skill not in skills:
                skills.append(skill)

    # Also map findings from P-prefix format by checking section headers
    # that mention a perspective name (e.g. "## Security Review")
    for perspective_name in parsed.findings_by_perspective:
        if perspective_name in PERSPECTIVE_SKILL_MAP:
            for skill in PERSPECTIVE_SKILL_MAP[perspective_name]:
                if skill not in skills:
                    skills.append(skill)

    summary: Dict[str, object] = {
        "verdict": parsed.verdict,
        "perspectives_found": len(productive_perspectives),
        "productive_perspectives": productive_perspectives,
        "skills_recorded": skills,
        "total_findings": len(parsed.findings),
        "file_paths": parsed.file_paths,
    }

    # Only record skills for reviews that found actionable issues
    if parsed.verdict in ("APPROVE WITH CHANGES", "REQUEST CHANGES") and skills:
        try:
            from .intelligence import ContextDetector
            from .skill_recommender import SkillRecommender

            # Build context from extracted file paths
            file_path_objects = [Path(p) for p in parsed.file_paths if p]
            context = ContextDetector.detect_from_files(file_path_objects)

            recommender = SkillRecommender(home=home, enable_semantic=False)
            recommender.record_skill_success(context, skills)
        except Exception:
            pass  # Best-effort — never block the review pipeline

    return summary


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 -m claude_ctx_py.review_parser <review-file>", file=sys.stderr)
        sys.exit(1)

    review_file = Path(sys.argv[1])
    if not review_file.exists():
        print(f"Error: File not found: {review_file}", file=sys.stderr)
        sys.exit(1)

    result = ingest_review(review_file)
    print(f"Review ingested ({result['verdict']})", file=sys.stderr)
    print(f"  Productive perspectives: {result['perspectives_found']}", file=sys.stderr)
    print(f"  Skills recorded: {result['skills_recorded']}", file=sys.stderr)
    print(f"  Total findings: {result['total_findings']}", file=sys.stderr)
