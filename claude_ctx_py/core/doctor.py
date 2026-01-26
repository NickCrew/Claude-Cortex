"""Doctor module for diagnosing and fixing context issues."""

from __future__ import annotations

import hashlib
import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple, Set, Dict

from .base import (
    _resolve_claude_dir,
    _resolve_cortex_root,
    _resolve_bundled_assets_root,
    _parse_active_entries,
    _iter_md_files,
    _color,
    RED,
    YELLOW,
    GREEN,
    BLUE,
    NC,
)

# Expected directories in CORTEX_ROOT
EXPECTED_DIRECTORIES = [
    "agents",
    "commands",
    "flags",
    "modes",
    "principles",
    "rules",
    "skills",
    "workflows",
]

# Directories that should contain .md files (not just exist)
CONTENT_REQUIRED_DIRECTORIES = [
    "modes",
    "rules",
    "flags",
]

# Template directories that can populate empty directories
TEMPLATE_DIRECTORIES = [
    "principles",
    "modes",
    "rules",
    "flags",
]

@dataclass
class Diagnosis:
    category: str
    level: str
    message: str
    resource: Optional[str] = None
    suggestion: Optional[str] = None

def doctor_run(fix: bool = False, home: Path | None = None) -> Tuple[int, str]:
    """Run system diagnostics."""
    cortex_root = _resolve_cortex_root(home)
    claude_dir = _resolve_claude_dir(home)
    report_lines = []
    error_count = 0
    warning_count = 0
    fixed_count = 0

    # 0. CORTEX_ROOT Structure
    structure_issues = check_structure(cortex_root)
    if not structure_issues:
        report_lines.append(f"{_color('[PASS]', GREEN)} Structure check")
    else:
        has_errors = any(d.level == "ERROR" for d in structure_issues)
        if has_errors:
            report_lines.append(f"{_color('[FAIL]', RED)} Structure check")
        else:
            report_lines.append(f"{_color('[WARN]', YELLOW)} Structure check")
        for d in structure_issues:
            report_lines.append(f"  - {d.message}")
            if d.resource:
                report_lines.append(f"    Path: {d.resource}")
            if d.suggestion:
                report_lines.append(f"    Suggestion: {d.suggestion}")
            if d.level == "ERROR":
                error_count += 1
            else:
                warning_count += 1
            # Auto-fix for missing/empty directories with templates
            if fix and d.category == "Structure" and "empty" in d.message.lower():
                fix_result = _try_fix_empty_directory(cortex_root, d)
                if fix_result:
                    report_lines.append(f"    {_color('[FIXED]', GREEN)} {fix_result}")
                    fixed_count += 1

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

    # 5. Principles
    principles_issues = check_principles(cortex_root)
    if not principles_issues:
        report_lines.append(f"{_color('[PASS]', GREEN)} Principles check")
    else:
        has_errors = any(d.level == "ERROR" for d in principles_issues)
        if has_errors:
            report_lines.append(f"{_color('[FAIL]', RED)} Principles check")
        else:
            report_lines.append(f"{_color('[WARN]', YELLOW)} Principles check")
        for d in principles_issues:
            report_lines.append(f"  - {d.message}")
            if d.suggestion:
                report_lines.append(f"    Suggestion: {d.suggestion}")
            if d.level == "ERROR":
                error_count += 1
            else:
                warning_count += 1

    # Summary
    if fix and fixed_count > 0:
        report_lines.append(f"\n{_color(f'Auto-fixed {fixed_count} issue(s).', GREEN)}")
    elif fix and error_count > 0:
        report_lines.append(_color("\nSome issues could not be auto-fixed.", YELLOW))

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


def check_structure(cortex_root: Path) -> List[Diagnosis]:
    """Check that expected directories exist and have content."""
    diagnoses = []

    for dir_name in EXPECTED_DIRECTORIES:
        dir_path = cortex_root / dir_name
        if not dir_path.exists():
            diagnoses.append(Diagnosis(
                category="Structure",
                level="WARNING",
                message=f"Missing directory: {dir_name}",
                resource=str(dir_path),
                suggestion=f"Run 'cortex install bootstrap' to create missing directories"
            ))
        elif dir_name in CONTENT_REQUIRED_DIRECTORIES:
            # Check if directory has any .md files
            md_files = list(_iter_md_files(dir_path))
            if not md_files:
                diagnoses.append(Diagnosis(
                    category="Structure",
                    level="WARNING",
                    message=f"Directory is empty: {dir_name}",
                    resource=str(dir_path),
                    suggestion=f"Add content or run 'cortex install bootstrap' to populate"
                ))

    return diagnoses


def check_principles(cortex_root: Path) -> List[Diagnosis]:
    """Check principles directory configuration."""
    diagnoses = []

    principles_dir = cortex_root / "principles"
    if not principles_dir.exists():
        diagnoses.append(Diagnosis(
            category="Principles",
            level="WARNING",
            message="Principles directory not found",
            resource=str(principles_dir),
            suggestion="Run 'cortex install bootstrap' to create principles directory"
        ))
        return diagnoses

    # Check for any .md files in principles
    md_files = list(_iter_md_files(principles_dir))
    if not md_files:
        diagnoses.append(Diagnosis(
            category="Principles",
            level="WARNING",
            message="No principle files found",
            resource=str(principles_dir),
            suggestion="Add principle files or run 'cortex install bootstrap'"
        ))

    return diagnoses


def _try_fix_empty_directory(cortex_root: Path, diagnosis: Diagnosis) -> Optional[str]:
    """Attempt to fix an empty directory by copying from bundled assets."""
    if not diagnosis.resource:
        return None

    dir_path = Path(diagnosis.resource)
    dir_name = dir_path.name

    # Only fix directories that have templates
    if dir_name not in TEMPLATE_DIRECTORIES:
        return None

    # Try to get bundled assets
    bundled_root = _resolve_bundled_assets_root()
    if not bundled_root:
        return None

    bundled_dir = bundled_root / dir_name
    if not bundled_dir.exists():
        return None

    # Copy files from bundled assets
    copied_count = 0
    for src_file in bundled_dir.iterdir():
        if src_file.is_file() and src_file.suffix == ".md":
            dst_file = dir_path / src_file.name
            if not dst_file.exists():
                shutil.copy2(src_file, dst_file)
                copied_count += 1

    if copied_count > 0:
        return f"Copied {copied_count} file(s) from bundled assets"

    return None
