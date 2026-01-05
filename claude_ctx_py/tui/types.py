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
class PrincipleSnippet:
    """Represents a principles snippet in the system."""

    name: str
    status: str  # "active" or "inactive"
    title: str
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
class MCPDocInfo:
    """Represents an MCP documentation file."""

    name: str
    status: str  # "active" or "inactive"
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


@dataclass
class AssetInfo:
    """Represents an asset available for installation."""

    name: str
    category: str  # hooks, commands, agents, skills, modes, workflows
    source_path: str
    description: str
    status: str  # "installed", "available", "differs"
    version: Optional[str] = None
    namespace: Optional[str] = None  # For namespaced commands


@dataclass
class MemoryNote:
    """Represents a note in the memory vault."""

    title: str
    note_type: str  # knowledge, projects, sessions, fixes
    path: str
    modified: datetime
    tags: List[str]
    snippet: str


@dataclass
class WatchModeState:
    """Represents watch mode runtime state."""

    running: bool
    directory: Path
    auto_activate: bool
    threshold: float
    interval: float
    checks_performed: int
    recommendations_made: int
    auto_activations: int
    started_at: Optional[datetime]
    last_notification: Optional[str]


@dataclass
class PromptInfo:
    """Represents a prompt in the prompt library."""

    name: str
    slug: str  # category/name format (e.g., "guidelines/code-review")
    status: str  # "active" or "inactive"
    category: str
    description: str
    tokens: int
    path: Path
