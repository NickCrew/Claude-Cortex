#!/usr/bin/env python3
"""Skill Quality Audit Tool.

Audits skills for quality, completeness, and adherence to standards.
Generates reports with scores and actionable recommendations.

Usage:
    python scripts/audit_skill.py <skill-name>
    python scripts/audit_skill.py <skill-name> --quick
    python scripts/audit_skill.py <skill-name> --full --output report.md
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]


# Quality dimension weights (must sum to 100)
DIMENSION_WEIGHTS = {
    "clarity": 25,
    "completeness": 25,
    "accuracy": 30,
    "usefulness": 20,
}

# Required sections in a skill
REQUIRED_SECTIONS = [
    "when to use",
    "core principles",
]

RECOMMENDED_SECTIONS = [
    "implementation patterns",
    "best practices",
    "anti-patterns",
    "troubleshooting",
]

# Required frontmatter fields
REQUIRED_METADATA = ["name", "description"]
RECOMMENDED_METADATA = ["author", "version", "tags", "triggers"]


@dataclass
class Issue:
    """An issue found during audit."""

    severity: str  # critical, major, minor, suggestion
    description: str
    location: str = ""
    recommendation: str = ""

    def to_dict(self) -> dict[str, str]:
        """Convert to dictionary."""
        return {
            "severity": self.severity,
            "description": self.description,
            "location": self.location,
            "recommendation": self.recommendation,
        }


@dataclass
class DimensionScore:
    """Score for a quality dimension."""

    name: str
    score: float
    weight: int
    notes: str = ""
    criteria_met: list[str] = field(default_factory=list)
    criteria_missed: list[str] = field(default_factory=list)

    @property
    def weighted_score(self) -> float:
        """Calculate weighted contribution."""
        return self.score * (self.weight / 100)


@dataclass
class AuditResult:
    """Complete audit result."""

    skill_name: str
    skill_path: Path
    timestamp: datetime
    status: str  # pass, fail, needs_review
    scores: dict[str, DimensionScore]
    issues: list[Issue]
    recommendations: list[str]
    checklist_results: dict[str, dict[str, bool]]

    @property
    def weighted_average(self) -> float:
        """Calculate overall weighted score."""
        return sum(s.weighted_score for s in self.scores.values())

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "skill_name": self.skill_name,
            "skill_path": str(self.skill_path),
            "timestamp": self.timestamp.isoformat(),
            "status": self.status,
            "weighted_average": round(self.weighted_average, 2),
            "scores": {
                name: {
                    "score": s.score,
                    "weight": s.weight,
                    "weighted": round(s.weighted_score, 2),
                    "notes": s.notes,
                }
                for name, s in self.scores.items()
            },
            "issues": [i.to_dict() for i in self.issues],
            "recommendations": self.recommendations,
            "checklist": self.checklist_results,
        }

    def to_markdown(self) -> str:
        """Generate markdown report."""
        lines = [
            f"# Audit Report: {self.skill_name}",
            "",
            f"**Date**: {self.timestamp.strftime('%Y-%m-%d %H:%M')}",
            f"**Path**: `{self.skill_path}`",
            f"**Status**: **{self.status.upper()}**",
            "",
            "## Scores",
            "",
            "| Dimension | Score | Weight | Weighted |",
            "|-----------|-------|--------|----------|",
        ]

        for name, score in self.scores.items():
            lines.append(
                f"| {name.title()} | {score.score:.1f}/5 | {score.weight}% | {score.weighted_score:.2f} |"
            )

        lines.extend([
            f"| **Total** | | | **{self.weighted_average:.2f}/5** |",
            "",
        ])

        if self.issues:
            lines.extend(["## Issues Found", ""])
            for issue in sorted(self.issues, key=lambda i: ["critical", "major", "minor", "suggestion"].index(i.severity)):
                icon = {"critical": "🔴", "major": "🟠", "minor": "🟡", "suggestion": "💡"}.get(issue.severity, "•")
                lines.append(f"- {icon} **[{issue.severity.upper()}]** {issue.description}")
                if issue.location:
                    lines.append(f"  - Location: `{issue.location}`")
                if issue.recommendation:
                    lines.append(f"  - Fix: {issue.recommendation}")
            lines.append("")

        if self.recommendations:
            lines.extend(["## Recommendations", ""])
            for i, rec in enumerate(self.recommendations, 1):
                lines.append(f"{i}. {rec}")
            lines.append("")

        # Checklist results
        lines.extend(["## Checklist Results", ""])
        for category, checks in self.checklist_results.items():
            lines.append(f"### {category.title()}")
            for check, passed in checks.items():
                icon = "✅" if passed else "❌"
                lines.append(f"- {icon} {check}")
            lines.append("")

        return "\n".join(lines)


class SkillAuditor:
    """Audits skills for quality and standards compliance."""

    def __init__(self, skills_dir: Path | None = None):
        """Initialize auditor.

        Args:
            skills_dir: Path to skills directory (auto-detected if None)
        """
        if skills_dir is None:
            # Try to find skills directory
            cwd = Path.cwd()
            if (cwd / "skills").is_dir():
                skills_dir = cwd / "skills"
            elif (cwd.parent / "skills").is_dir():
                skills_dir = cwd.parent / "skills"
            else:
                skills_dir = cwd

        self.skills_dir = skills_dir
        self.issues: list[Issue] = []

    def find_skill(self, skill_name: str) -> Path | None:
        """Find skill directory by name."""
        skill_path = self.skills_dir / skill_name
        if skill_path.is_dir() and (skill_path / "SKILL.md").exists():
            return skill_path

        # Try finding by partial match
        for path in self.skills_dir.iterdir():
            if path.is_dir() and skill_name.lower() in path.name.lower():
                if (path / "SKILL.md").exists():
                    return path

        return None

    def parse_frontmatter(self, content: str) -> tuple[dict[str, Any], str]:
        """Parse YAML frontmatter from markdown content."""
        if not content.strip().startswith("---"):
            return {}, content

        lines = content.split("\n")
        end_idx = None
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                end_idx = i
                break

        if end_idx is None:
            return {}, content

        yaml_content = "\n".join(lines[1:end_idx])
        remaining = "\n".join(lines[end_idx + 1:])

        if yaml is None:
            return {}, content

        try:
            metadata = yaml.safe_load(yaml_content)
            return metadata if isinstance(metadata, dict) else {}, remaining
        except yaml.YAMLError:
            self.issues.append(Issue(
                severity="major",
                description="Invalid YAML frontmatter",
                location="SKILL.md:1",
                recommendation="Fix YAML syntax errors in frontmatter"
            ))
            return {}, content

    def check_structure(self, skill_path: Path, content: str, metadata: dict) -> dict[str, bool]:
        """Check skill structure against requirements."""
        results = {}

        # Check SKILL.md exists
        results["SKILL.md exists"] = (skill_path / "SKILL.md").exists()

        # Check frontmatter
        results["Has YAML frontmatter"] = bool(metadata)

        # Check required metadata
        for field in REQUIRED_METADATA:
            key = f"Has '{field}' metadata"
            results[key] = field in metadata
            if not results[key]:
                self.issues.append(Issue(
                    severity="major",
                    description=f"Missing required metadata: {field}",
                    location="SKILL.md frontmatter",
                    recommendation=f"Add '{field}' to frontmatter"
                ))

        # Check recommended metadata
        for field in RECOMMENDED_METADATA:
            key = f"Has '{field}' metadata"
            results[key] = field in metadata
            if not results[key]:
                self.issues.append(Issue(
                    severity="suggestion",
                    description=f"Missing recommended metadata: {field}",
                    location="SKILL.md frontmatter",
                    recommendation=f"Consider adding '{field}' to frontmatter"
                ))

        # Check for examples directory
        results["Has examples/ directory"] = (skill_path / "examples").is_dir()

        # Check for validation rubric
        results["Has validation/rubric.yaml"] = (skill_path / "validation" / "rubric.yaml").exists()

        return results

    def check_content(self, content: str) -> dict[str, bool]:
        """Check content for required sections and quality markers."""
        results = {}
        content_lower = content.lower()

        # Check required sections
        for section in REQUIRED_SECTIONS:
            key = f"Has '{section}' section"
            # Look for markdown headers
            pattern = rf"#+\s*{re.escape(section)}"
            results[key] = bool(re.search(pattern, content_lower))
            if not results[key]:
                self.issues.append(Issue(
                    severity="major",
                    description=f"Missing required section: {section}",
                    location="SKILL.md",
                    recommendation=f"Add a '## {section.title()}' section"
                ))

        # Check recommended sections
        for section in RECOMMENDED_SECTIONS:
            key = f"Has '{section}' section"
            pattern = rf"#+\s*{re.escape(section)}"
            results[key] = bool(re.search(pattern, content_lower))
            if not results[key]:
                self.issues.append(Issue(
                    severity="minor",
                    description=f"Missing recommended section: {section}",
                    location="SKILL.md",
                    recommendation=f"Consider adding a '## {section.title()}' section"
                ))

        # Check for code examples
        code_blocks = re.findall(r"```(\w+)?", content)
        results["Has code examples"] = len(code_blocks) > 0
        if not results["Has code examples"]:
            self.issues.append(Issue(
                severity="major",
                description="No code examples found",
                location="SKILL.md",
                recommendation="Add code examples with language-tagged code blocks"
            ))

        # Check code blocks have language tags
        untagged = sum(1 for lang in code_blocks if not lang)
        results["Code blocks have language tags"] = untagged == 0
        if untagged > 0:
            self.issues.append(Issue(
                severity="minor",
                description=f"{untagged} code block(s) missing language tags",
                location="SKILL.md",
                recommendation="Add language tags to all code blocks (e.g., ```python)"
            ))

        # Check for TODO/FIXME markers
        todos = len(re.findall(r"\b(TODO|FIXME|XXX|HACK)\b", content))
        results["No TODO/FIXME markers"] = todos == 0
        if todos > 0:
            self.issues.append(Issue(
                severity="minor",
                description=f"Found {todos} TODO/FIXME marker(s)",
                location="SKILL.md",
                recommendation="Complete or remove TODO items before finalizing"
            ))

        return results

    def score_clarity(self, content: str, metadata: dict) -> DimensionScore:
        """Score the clarity dimension."""
        score = 3.0  # Start at acceptable
        criteria_met = []
        criteria_missed = []

        # Check structure
        headers = re.findall(r"^#+\s+.+$", content, re.MULTILINE)
        if len(headers) >= 5:
            score += 0.5
            criteria_met.append("Well-organized with multiple sections")
        else:
            criteria_missed.append("Could use more section organization")

        # Check for progressive disclosure
        if "tier" in content.lower() or "level" in content.lower() or "basic" in content.lower():
            score += 0.3
            criteria_met.append("Shows progressive disclosure pattern")

        # Check description length
        desc = metadata.get("description", "")
        if 50 < len(desc) < 300:
            score += 0.3
            criteria_met.append("Description is appropriately sized")
        elif len(desc) < 50:
            score -= 0.3
            criteria_missed.append("Description too brief")

        # Check for tables (good for clarity)
        if "|" in content and "---" in content:
            score += 0.2
            criteria_met.append("Uses tables for structured information")

        return DimensionScore(
            name="clarity",
            score=min(5.0, max(1.0, score)),
            weight=DIMENSION_WEIGHTS["clarity"],
            criteria_met=criteria_met,
            criteria_missed=criteria_missed,
        )

    def score_completeness(self, content: str, skill_path: Path) -> DimensionScore:
        """Score the completeness dimension."""
        score = 3.0
        criteria_met = []
        criteria_missed = []

        content_lower = content.lower()

        # Check for anti-patterns section
        if "anti-pattern" in content_lower or "don't" in content_lower:
            score += 0.5
            criteria_met.append("Includes anti-patterns or don'ts")
        else:
            criteria_missed.append("Missing anti-patterns guidance")

        # Check for examples
        if (skill_path / "examples").is_dir():
            score += 0.5
            criteria_met.append("Has examples directory")

        # Check for troubleshooting
        if "troubleshoot" in content_lower or "common issues" in content_lower:
            score += 0.3
            criteria_met.append("Has troubleshooting section")

        # Check code block count
        code_blocks = len(re.findall(r"```", content))
        if code_blocks >= 6:
            score += 0.4
            criteria_met.append("Rich with code examples")
        elif code_blocks < 2:
            score -= 0.5
            criteria_missed.append("Needs more code examples")

        # Check content length
        word_count = len(content.split())
        if word_count > 500:
            score += 0.3
            criteria_met.append("Comprehensive content length")
        elif word_count < 200:
            score -= 0.5
            criteria_missed.append("Content too brief")

        return DimensionScore(
            name="completeness",
            score=min(5.0, max(1.0, score)),
            weight=DIMENSION_WEIGHTS["completeness"],
            criteria_met=criteria_met,
            criteria_missed=criteria_missed,
        )

    def score_accuracy(self, content: str, metadata: dict) -> DimensionScore:
        """Score the accuracy dimension."""
        score = 3.5  # Assume mostly accurate unless red flags
        criteria_met = []
        criteria_missed = []

        # Check for version info (indicates maintained)
        if metadata.get("version"):
            score += 0.3
            criteria_met.append("Has version information")

        # Check for updated date
        if metadata.get("updated"):
            score += 0.2
            criteria_met.append("Has last updated date")

        # Check for deprecated patterns (negative)
        deprecated_patterns = ["var ", "callback(", "require("]  # Examples
        deprecated_found = sum(1 for p in deprecated_patterns if p in content)
        if deprecated_found == 0:
            score += 0.3
            criteria_met.append("No obviously deprecated patterns")
        else:
            score -= 0.3 * deprecated_found
            criteria_missed.append(f"May contain deprecated patterns")

        # Check for security mentions in relevant contexts
        if "security" in content.lower() or "auth" in content.lower():
            if "vulnerab" in content.lower() or "protect" in content.lower() or "secure" in content.lower():
                score += 0.2
                criteria_met.append("Addresses security considerations")

        return DimensionScore(
            name="accuracy",
            score=min(5.0, max(1.0, score)),
            weight=DIMENSION_WEIGHTS["accuracy"],
            criteria_met=criteria_met,
            criteria_missed=criteria_missed,
        )

    def score_usefulness(self, content: str, skill_path: Path) -> DimensionScore:
        """Score the usefulness dimension."""
        score = 3.0
        criteria_met = []
        criteria_missed = []

        content_lower = content.lower()

        # Check for real-world examples
        if "example" in content_lower or "real" in content_lower or "production" in content_lower:
            score += 0.4
            criteria_met.append("References real-world usage")

        # Check for practical patterns
        if "pattern" in content_lower:
            score += 0.3
            criteria_met.append("Includes implementation patterns")

        # Check for CLI/tool integration
        if "```bash" in content or "```shell" in content or "cortex" in content:
            score += 0.3
            criteria_met.append("Includes CLI examples")

        # Check for testing guidance
        if "test" in content_lower:
            score += 0.3
            criteria_met.append("Includes testing guidance")

        # Check for immediate applicability
        if "when to use" in content_lower:
            score += 0.2
            criteria_met.append("Clear activation criteria")

        # Check dependencies are documented
        if (skill_path / "SKILL.md").exists():
            skill_content = (skill_path / "SKILL.md").read_text()
            if "dependencies:" in skill_content:
                score += 0.2
                criteria_met.append("Dependencies documented")

        return DimensionScore(
            name="usefulness",
            score=min(5.0, max(1.0, score)),
            weight=DIMENSION_WEIGHTS["usefulness"],
            criteria_met=criteria_met,
            criteria_missed=criteria_missed,
        )

    def determine_status(self, scores: dict[str, DimensionScore]) -> str:
        """Determine overall pass/fail status."""
        weighted_avg = sum(s.weighted_score for s in scores.values())

        # Check for blocking issues
        critical_issues = [i for i in self.issues if i.severity == "critical"]
        if critical_issues:
            return "fail"

        # Check accuracy threshold
        if scores["accuracy"].score < 3.0:
            return "fail"

        # Check overall score
        if weighted_avg >= 3.0:
            if weighted_avg >= 4.0:
                return "pass"
            else:
                return "needs_review"
        else:
            return "fail"

    def generate_recommendations(self, result: AuditResult) -> list[str]:
        """Generate actionable recommendations based on audit results."""
        recommendations = []

        # Based on lowest scores
        lowest = min(result.scores.values(), key=lambda s: s.score)
        if lowest.score < 3.5:
            recommendations.append(f"Focus on improving {lowest.name}: {', '.join(lowest.criteria_missed[:2])}")

        # Based on issues
        critical = [i for i in result.issues if i.severity == "critical"]
        major = [i for i in result.issues if i.severity == "major"]

        if critical:
            recommendations.append(f"Fix {len(critical)} critical issue(s) immediately")
        if major:
            recommendations.append(f"Address {len(major)} major issue(s) before finalizing")

        # Based on checklist
        for category, checks in result.checklist_results.items():
            failed = [k for k, v in checks.items() if not v and "recommended" not in k.lower()]
            if failed:
                recommendations.append(f"Complete missing {category} items: {failed[0]}")

        # General recommendations based on score ranges
        if result.weighted_average < 4.0:
            recommendations.append("Add more code examples to improve completeness")
        if result.weighted_average >= 4.0:
            recommendations.append("Consider adding a validation/rubric.yaml for self-auditing")

        return recommendations[:5]  # Top 5 recommendations

    def audit(self, skill_name: str, quick: bool = False) -> AuditResult | None:
        """Perform audit on a skill.

        Args:
            skill_name: Name of skill to audit
            quick: If True, only do structural checks

        Returns:
            AuditResult or None if skill not found
        """
        self.issues = []  # Reset issues

        skill_path = self.find_skill(skill_name)
        if skill_path is None:
            print(f"Error: Skill '{skill_name}' not found in {self.skills_dir}", file=sys.stderr)
            return None

        skill_file = skill_path / "SKILL.md"
        content = skill_file.read_text(encoding="utf-8")
        metadata, body = self.parse_frontmatter(content)

        # Run checks
        structure_results = self.check_structure(skill_path, content, metadata)
        content_results = self.check_content(body)

        if quick:
            # Quick audit - just structural checks
            scores = {
                dim: DimensionScore(name=dim, score=3.0, weight=w)
                for dim, w in DIMENSION_WEIGHTS.items()
            }
        else:
            # Full audit - score all dimensions
            scores = {
                "clarity": self.score_clarity(body, metadata),
                "completeness": self.score_completeness(body, skill_path),
                "accuracy": self.score_accuracy(body, metadata),
                "usefulness": self.score_usefulness(body, skill_path),
            }

        result = AuditResult(
            skill_name=skill_name,
            skill_path=skill_path,
            timestamp=datetime.now(),
            status="pending",
            scores=scores,
            issues=self.issues,
            recommendations=[],
            checklist_results={
                "structure": structure_results,
                "content": content_results,
            },
        )

        result.status = self.determine_status(scores)
        result.recommendations = self.generate_recommendations(result)

        return result


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Audit skill quality and standards compliance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python scripts/audit_skill.py api-design-patterns
    python scripts/audit_skill.py quality-audit --quick
    python scripts/audit_skill.py my-skill --output report.md
    python scripts/audit_skill.py my-skill --format json
        """,
    )
    parser.add_argument("skill", help="Skill name to audit")
    parser.add_argument("--quick", action="store_true", help="Quick structural check only")
    parser.add_argument("--output", "-o", help="Output file for report")
    parser.add_argument(
        "--format", "-f",
        choices=["markdown", "json", "yaml"],
        default="markdown",
        help="Output format (default: markdown)"
    )
    parser.add_argument(
        "--fail-under",
        type=float,
        default=0,
        help="Exit with error if score is below threshold"
    )
    parser.add_argument(
        "--skills-dir",
        type=Path,
        help="Path to skills directory"
    )

    args = parser.parse_args()

    auditor = SkillAuditor(skills_dir=args.skills_dir)
    result = auditor.audit(args.skill, quick=args.quick)

    if result is None:
        sys.exit(1)

    # Generate output
    if args.format == "markdown":
        output = result.to_markdown()
    elif args.format == "json":
        output = json.dumps(result.to_dict(), indent=2)
    elif args.format == "yaml":
        if yaml is None:
            print("Error: PyYAML not installed for YAML output", file=sys.stderr)
            sys.exit(1)
        output = yaml.dump(result.to_dict(), default_flow_style=False)
    else:
        output = result.to_markdown()

    # Write or print output
    if args.output:
        Path(args.output).write_text(output)
        print(f"Report written to {args.output}")
    else:
        print(output)

    # Print summary
    print(f"\n{'='*50}")
    print(f"Skill: {result.skill_name}")
    print(f"Score: {result.weighted_average:.2f}/5")
    print(f"Status: {result.status.upper()}")
    print(f"Issues: {len(result.issues)} ({len([i for i in result.issues if i.severity == 'critical'])} critical)")
    print(f"{'='*50}")

    # Check fail-under threshold
    if args.fail_under > 0 and result.weighted_average < args.fail_under:
        print(f"\nFailed: Score {result.weighted_average:.2f} is below threshold {args.fail_under}")
        sys.exit(1)

    # Exit code based on status
    if result.status == "fail":
        sys.exit(1)
    elif result.status == "needs_review":
        sys.exit(2)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
