from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional, TypedDict, Dict


@dataclass
class RuleNode:
    """Represents a rule in the system."""

    name: str
    status: str  # "active" or "inactive"
    category: str
    description: str
    path: Path


@dataclass
class AgentTask:
    """Represents an active agent task in the orchestration system."""

    agent_id: str
    agent_name: str
    workstream: str
    status: str
    progress: int
    category: str = "general"
    started: Optional[float] = None
    completed: Optional[float] = None
    description: str = ""
    raw_notes: str = ""
    source_path: Optional[str] = None


@dataclass
class WorkflowInfo:
    """Information about a workflow."""

    name: str
    description: str
    status: str
    progress: int
    started: Optional[float]
    steps: List[str]
    current_step: Optional[str]
    file_path: Path


@dataclass
class ModeInfo:
    """Represents a behavioral mode in the system."""

    name: str
    status: str  # "active" or "inactive"
    purpose: str
    description: str
    path: Path


@dataclass
class ScenarioInfo:
    """Represents a scenario definition and its runtime metadata."""

    name: str
    description: str
    priority: str
    scenario_type: str
    phase_names: List[str]
    agents: List[str]
    profiles: List[str]
    status: str
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    lock_holder: Optional[str]
    file_path: Path
    error: Optional[str] = None


class ScenarioRuntimeState(TypedDict):
    status: str
    started: Optional[datetime]
    completed: Optional[datetime]
