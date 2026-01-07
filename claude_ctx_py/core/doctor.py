"""Doctor module for diagnosing and fixing context issues."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple, Set, Dict

from .base import (
    _resolve_claude_dir,
    _parse_active_entries,
    _iter_md_files,
    _color,
    RED,
    YELLOW,
    GREEN,
    BLUE,
    NC,
)

@dataclass
class Diagnosis:
    category: str
    level: str
    message: str
    resource: Optional[str] = None
    suggestion: Optional[str] = None

def doctor_run(fix: bool = False, home: Path | None = None) -> Tuple[int, str]:
    """Run system diagnostics."""
    claude_dir = _resolve_claude_dir(home)
    report_lines = []
    error_count = 0

    # 1. Consistency
    consistency_issues = check_consistency(claude_dir)
    if not consistency_issues:
        report_lines.append(f"{_color('[PASS]', GREEN)} Consistency check")
    else:
        report_lines.append(f"{_color('[FAIL]', RED)} Consistency check")
        for d in consistency_issues:
            report_lines.append(f"  - {d.message} ({d.resource or ''})")
            if d.suggestion:
                report_lines.append(f"    Suggestion: {d.suggestion}")
            if d.level == "ERROR":
                error_count += 1

    # 2. Duplicates
    duplicate_issues = check_duplicates(claude_dir)
    if not duplicate_issues:
        report_lines.append(f"{_color('[PASS]', GREEN)} Duplicate check")
    else:
        report_lines.append(f"{_color('[WARN]', YELLOW)} Duplicate check")
        for d in duplicate_issues:
            report_lines.append(f"  - {d.message}")
            if d.suggestion:
                report_lines.append(f"    Suggestion: {d.suggestion}")

    # 3. Redundancy
    redundancy_issues = check_redundancy(claude_dir)
    if not redundancy_issues:
        report_lines.append(f"{_color('[PASS]', GREEN)} Redundancy check")
    else:
        report_lines.append(f"{_color('[WARN]', YELLOW)} Redundancy check")
        for d in redundancy_issues:
            report_lines.append(f"  - {d.message}")

    # 4. Optimization
    optimization_issues = check_optimizations(claude_dir)
    if not optimization_issues:
        report_lines.append(f"{_color('[PASS]', GREEN)} Optimization check")
    else:
        report_lines.append(f"{_color('[WARN]', YELLOW)} Optimization check")
        for d in optimization_issues:
            report_lines.append(f"  - {d.message}")
            if d.suggestion:
                report_lines.append(f"    Suggestion: {d.suggestion}")

    if fix and error_count > 0:
        report_lines.append(_color("\nAuto-fix not fully implemented yet.", YELLOW))

    return (1 if error_count > 0 else 0), "\n".join(report_lines)

def check_consistency(claude_dir: Path) -> List[Diagnosis]:
    """Check consistency between active state and file system."""
    diagnoses = []
    
    # Active Modes
    active_modes_file = claude_dir / ".active-modes"
    if active_modes_file.exists():
        modes = _parse_active_entries(active_modes_file)
        for mode in modes:
            mode_path = claude_dir / "modes" / f"{mode}.md"
            if not mode_path.is_file():
                diagnoses.append(Diagnosis(
                    category="Consistency",
                    level="ERROR",
                    message=f"Active mode '{mode}' references missing file",
                    resource=str(mode_path),
                    suggestion=f"Run 'cortex mode deactivate {mode}'"
                ))

    # Active Rules
    active_rules_file = claude_dir / ".active-rules"
    if active_rules_file.exists():
        rules = _parse_active_entries(active_rules_file)
        for rule in rules:
            rule_path = claude_dir / "rules" / f"{rule}.md"
            if not rule_path.is_file():
                diagnoses.append(Diagnosis(
                    category="Consistency",
                    level="ERROR",
                    message=f"Active rule '{rule}' references missing file",
                    resource=str(rule_path),
                    suggestion=f"Run 'cortex rules deactivate {rule}'"
                ))

    return diagnoses

def check_duplicates(claude_dir: Path) -> List[Diagnosis]:
    """Check for duplicate definitions."""
    diagnoses = []
    # Check hash of all agents to find content duplicates
    hashes: Dict[str, List[str]] = {}
    
    agents_dir = claude_dir / "agents"
    if agents_dir.exists():
        for agent_file in _iter_md_files(agents_dir):
            try:
                content = agent_file.read_bytes()
                file_hash = hashlib.md5(content).hexdigest()
                if file_hash not in hashes:
                    hashes[file_hash] = []
                hashes[file_hash].append(agent_file.name)
            except Exception:
                continue
        
    for file_hash, files in hashes.items():
        if len(files) > 1:
            diagnoses.append(Diagnosis(
                category="Duplicate",
                level="WARNING",
                message=f"Identical content found in agents: {', '.join(files)}",
                suggestion="Delete duplicate files."
            ))
    return diagnoses

def check_redundancy(claude_dir: Path) -> List[Diagnosis]:
    """Check for unused resources."""
    diagnoses: List[Diagnosis] = []
    # Placeholder for future implementation
    return diagnoses

def check_optimizations(claude_dir: Path) -> List[Diagnosis]:
    """Check for optimization opportunities."""
    diagnoses = []
    
    # Check for large agent files
    agents_dir = claude_dir / "agents"
    if agents_dir.exists():
        for agent_file in _iter_md_files(agents_dir):
            try:
                size = agent_file.stat().st_size
                if size > 10 * 1024: # 10KB
                    diagnoses.append(Diagnosis(
                        category="Optimization",
                        level="WARNING",
                        message=f"Agent definition is large ({size/1024:.1f}KB)",
                        resource=agent_file.name,
                        suggestion="Consider splitting this agent or removing verbose examples."
                    ))
            except Exception:
                continue
    
    return diagnoses
