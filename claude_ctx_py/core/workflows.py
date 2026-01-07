"""Workflow management functions."""

from __future__ import annotations


import builtins
import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess
import time
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, List, Optional, Sequence, Set, Tuple

# Import from base module
from .base import BLUE, GREEN, YELLOW, RED, NC, _color, _resolve_claude_dir


def workflow_run(workflow: str, home: Path | None = None) -> Tuple[int, str]:
    """Run a predefined workflow."""
    claude_dir = _resolve_claude_dir(home)
    workflows_dir = claude_dir / "workflows"
    workflow_file = workflows_dir / f"{workflow}.yaml"

    if not workflow_file.is_file():
        available = workflow_list(home=home)
        missing_message_lines = [
            _color(f"Workflow {workflow!r} not found", RED),
            "Available workflows:",
            available,
        ]
        return 1, "\n".join(missing_message_lines)

    # Create task directory for this workflow
    tasks_dir = claude_dir / "tasks"
    current_dir = tasks_dir / "current"
    current_dir.mkdir(parents=True, exist_ok=True)

    # Save workflow state
    (current_dir / "active_workflow").write_text(workflow, encoding="utf-8")
    (current_dir / "workflow_status").write_text("pending", encoding="utf-8")
    (current_dir / "workflow_started").write_text(
        str(int(time.time())), encoding="utf-8"
    )

    lines: List[str] = [
        _color(f"Started workflow: {workflow}", GREEN),
        "",
        _color("Workflow steps will be executed by Claude Code", BLUE),
        f"To check progress: cortex workflow status",
        f"To resume if interrupted: cortex workflow resume",
        "",
        _color("Next: Open Claude Code and the workflow will guide you", YELLOW),
        "",
        _color(f"=== Workflow: {workflow} ===", BLUE),
    ]

    # Show workflow summary
    try:
        content = workflow_file.read_text(encoding="utf-8")
        for line in content.splitlines():
            if line.startswith("description:"):
                lines.append(line.replace("description:", "").strip())
                break
        lines.append("")
        lines.append(_color("Steps:", BLUE))
        for line in content.splitlines():
            if line.strip().startswith("- name:"):
                step_name = line.split("- name:", 1)[1].strip()
                lines.append(f"  → {step_name}")
    except OSError:
        pass

    return 0, "\n".join(lines)


def workflow_list(home: Path | None = None) -> str:
    """List available workflows."""
    claude_dir = _resolve_claude_dir(home)
    workflows_dir = claude_dir / "workflows"

    lines: List[str] = [_color("Available workflows:", BLUE)]

    if not workflows_dir.is_dir():
        return "\n".join(lines)

    for workflow_file in sorted(workflows_dir.glob("*.yaml")):
        if not workflow_file.is_file():
            continue
        workflow_name = workflow_file.stem
        if workflow_name == "README":
            continue

        lines.append(f"  {_color(workflow_name, GREEN)}")
        try:
            content = workflow_file.read_text(encoding="utf-8")
            for line in content.splitlines():
                if line.startswith("description:"):
                    desc = line.replace("description:", "").strip()
                    lines.append(f"    {desc}")
                    break
        except OSError:
            pass

    return "\n".join(lines)


def workflow_status(home: Path | None = None) -> Tuple[int, str]:
    """Show current workflow progress."""
    claude_dir = _resolve_claude_dir(home)
    tasks_dir = claude_dir / "tasks"
    current_dir = tasks_dir / "current"
    active_workflow_file = current_dir / "active_workflow"

    if not active_workflow_file.is_file():
        return 0, _color("No active workflow", YELLOW)

    workflow = active_workflow_file.read_text(encoding="utf-8").strip()
    status_file = current_dir / "workflow_status"
    started_file = current_dir / "workflow_started"

    status = "unknown"
    if status_file.is_file():
        status = status_file.read_text(encoding="utf-8").strip()

    started = 0
    if started_file.is_file():
        try:
            started = int(started_file.read_text(encoding="utf-8").strip())
        except ValueError:
            started = 0

    elapsed = int(time.time()) - started
    hours = elapsed // 3600
    minutes = (elapsed % 3600) // 60

    lines: List[str] = [
        _color("=== Active Workflow ===", BLUE),
        f"Workflow: {_color(workflow, GREEN)}",
        f"Status: {status}",
        f"Elapsed time: {hours}h {minutes}m",
    ]

    current_step_file = current_dir / "current_step"
    if current_step_file.is_file():
        step = current_step_file.read_text(encoding="utf-8").strip()
        lines.append(f"Current step: {_color(step, YELLOW)}")

    return 0, "\n".join(lines)


def workflow_resume(home: Path | None = None) -> Tuple[int, str]:
    """Resume interrupted workflow."""
    claude_dir = _resolve_claude_dir(home)
    tasks_dir = claude_dir / "tasks"
    current_dir = tasks_dir / "current"
    active_workflow_file = current_dir / "active_workflow"

    if not active_workflow_file.is_file():
        return 1, _color("No workflow to resume", YELLOW)

    workflow = active_workflow_file.read_text(encoding="utf-8").strip()
    lines: List[str] = [_color(f"Resuming workflow: {workflow}", GREEN)]

    current_step_file = current_dir / "current_step"
    if current_step_file.is_file():
        step = current_step_file.read_text(encoding="utf-8").strip()
        lines.append(f"Resuming from step: {_color(step, YELLOW)}")

    lines.append("")
    lines.append(
        _color("Continue in Claude Code - the workflow context has been restored", BLUE)
    )

    return 0, "\n".join(lines)


def workflow_stop(workflow: Optional[str] = None, home: Path | None = None) -> Tuple[int, str]:
    """Stop the active workflow by clearing its task state."""
    claude_dir = _resolve_claude_dir(home)
    tasks_dir = claude_dir / "tasks"
    current_dir = tasks_dir / "current"
    active_workflow_file = current_dir / "active_workflow"

    if not active_workflow_file.is_file():
        return 0, _color("No active workflow to stop", YELLOW)

    active_workflow = active_workflow_file.read_text(encoding="utf-8").strip()
    if workflow and workflow.strip() and workflow.strip() != active_workflow:
        return 1, _color(
            f"Active workflow '{active_workflow}' does not match '{workflow}'", YELLOW
        )

    for artifact in [
        "active_workflow",
        "workflow_status",
        "workflow_started",
        "current_step",
    ]:
        path = current_dir / artifact
        try:
            path.unlink()
        except FileNotFoundError:
            continue
        except OSError as exc:
            return 1, _color(f"Failed to remove {artifact}: {exc}", RED)

    return 0, _color(f"Stopped workflow '{active_workflow}'", GREEN)


# Scenario/Orchestrate functions
