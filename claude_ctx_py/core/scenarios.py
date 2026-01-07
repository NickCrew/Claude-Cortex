"""Scenario management functions."""

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
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Set, Tuple

try:  # pragma: no cover - dependency availability exercised in tests
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore[assignment]

# Import from base module
from .base import (
    BLUE,
    GREEN,
    YELLOW,
    RED,
    NC,
    _color,
    _ensure_list,
    _flatten_mixed,
    _load_yaml,
    _load_yaml_dict,
    _now_iso,
    _resolve_claude_dir,
)
from .agents import (
    _find_agent_file_any_state,
    _generate_dependency_map,
    _normalize_agent_filename,
)


@dataclass
class ScenarioPhase:
    """Normalized representation of a scenario phase."""

    name: str
    description: str
    condition: str
    parallel: bool
    agents: List[str]
    profiles: List[str]
    success: List[str]


@dataclass
class ScenarioMetadata:
    name: str
    description: str
    priority: str
    scenario_type: str
    phases: List[ScenarioPhase]
    source_file: Path


def _scenario_dirs(claude_dir: Path) -> Tuple[Path, Path, Path]:
    scenarios_dir = claude_dir / "scenarios"
    state_dir = scenarios_dir / ".state"
    lock_dir = scenarios_dir / ".locks"
    return scenarios_dir, state_dir, lock_dir


def _ensure_scenarios_dir(claude_dir: Path) -> Tuple[Path, Path, Path]:
    """Ensure scenarios directory and subdirectories exist."""
    scenarios_dir, state_dir, lock_dir = _scenario_dirs(claude_dir)

    scenarios_dir.mkdir(parents=True, exist_ok=True)
    state_dir.mkdir(parents=True, exist_ok=True)
    lock_dir.mkdir(parents=True, exist_ok=True)

    return scenarios_dir, state_dir, lock_dir


def _scenario_schema_path(claude_dir: Path) -> Path:
    return claude_dir / "schema" / "scenario-schema-v1.yaml"


def _scenario_lock_basename(value: str) -> str:
    sanitized = value.replace("/", "_").replace("\\", "_").strip()
    return sanitized or "scenario"


def _scenario_init_state(state_file: Path, metadata: ScenarioMetadata) -> None:
    payload = {
        "scenario": metadata.name,
        "description": metadata.description,
        "source": str(metadata.source_file),
        "started": _now_iso(),
        "status": "running",
        "phases": [],
    }
    state_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _scenario_update_phase_state(
    state_file: Path,
    *,
    index: int,
    phase_name: str,
    status: str,
    note: Optional[str] = None,
) -> None:
    try:
        data = json.loads(state_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        data = {}

    phases = data.setdefault("phases", [])
    while len(phases) <= index:
        phases.append({})

    entry = phases[index] or {}
    entry.update(
        {
            "name": phase_name,
            "status": status,
            "updated": _now_iso(),
        }
    )
    if note:
        entry["note"] = note
    else:
        entry.pop("note", None)
    phases[index] = entry

    state_file.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _scenario_finalize_state(state_file: Path, final_status: str) -> None:
    try:
        data = json.loads(state_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        data = {}
    data["status"] = final_status
    data["completed"] = _now_iso()
    state_file.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _collect_scenario_targets(
    names: Sequence[str],
    scenarios_dir: Path,
    messages: List[str],
) -> List[Path]:
    normalized = [name for name in names if name]
    use_all = not normalized or any(name == "--all" for name in normalized)
    if use_all:
        return sorted(scenarios_dir.glob("*.yaml"))

    targets: List[Path] = []
    for raw in normalized:
        if raw == "--all":
            continue
        candidate = scenarios_dir / (raw if raw.endswith(".yaml") else f"{raw}.yaml")
        if candidate.is_file():
            targets.append(candidate)
        else:
            messages.append(_color(f"Scenario file not found: {raw}", RED))
    return targets


def _parse_scenario_metadata(
    scenario_path: Path,
) -> Tuple[int, Optional[ScenarioMetadata], str]:
    if not scenario_path.is_file():
        return 1, None, f"Scenario file not found: {scenario_path.name}"

    success, data, error = _load_yaml_dict(scenario_path)
    if not success:
        return 1, None, error

    name = str(data.get("name") or scenario_path.stem)
    description = str(data.get("description") or "")
    priority = str(data.get("priority") or "normal")
    scenario_type = str(data.get("type") or "operational")

    phases_raw = data.get("phases") or []
    if not isinstance(phases_raw, list):
        return 1, None, "invalid phases"

    phases: List[ScenarioPhase] = []
    for idx, raw in enumerate(phases_raw):
        if not isinstance(raw, dict):
            return 1, None, f"phase_{idx}_not_object"
        phase_name = str(raw.get("name") or f"phase_{idx + 1}")
        phase_desc = str(raw.get("description") or "")
        condition = str(raw.get("condition") or "manual")
        parallel = bool(raw.get("parallel", False))
        agents = _flatten_mixed(raw.get("agents") or [])
        profiles = _flatten_mixed(raw.get("profiles") or [])
        success_criteria = _flatten_mixed(raw.get("success_criteria") or [])
        phases.append(
            ScenarioPhase(
                name=phase_name,
                description=phase_desc,
                condition=condition,
                parallel=parallel,
                agents=agents,
                profiles=profiles,
                success=success_criteria,
            )
        )

    metadata = ScenarioMetadata(
        name=name,
        description=description,
        priority=priority,
        scenario_type=scenario_type,
        phases=phases,
        source_file=scenario_path,
    )
    return 0, metadata, ""


def scenario_list(home: Path | None = None) -> str:
    """List all available scenarios."""
    claude_dir = _resolve_claude_dir(home)
    scenarios_dir, _, _ = _ensure_scenarios_dir(claude_dir)

    if yaml is None:
        return _color("PyYAML is required to manage scenarios.", RED)  # type: ignore[unreachable]

    entries: List[Tuple[str, str, str]] = []
    for scenario_file in sorted(scenarios_dir.glob("*.yaml")):
        code, metadata, error_msg = _parse_scenario_metadata(scenario_file)
        if code != 0 or metadata is None:
            entries.append((scenario_file.stem, "invalid YAML", "error"))
            continue
        description = metadata.description or "No description provided"
        entries.append((metadata.name, description, metadata.priority))

    if not entries:
        return "No scenarios defined. Add YAML files under ~/.cortex/scenarios/."

    lines: List[str] = ["Available scenarios:\n"]
    for name, desc, priority in entries:
        lines.append(f"- {name} [priority: {priority}]")
        lines.append(f"  {desc}")
    return "\n".join(lines)


def scenario_validate(
    *scenario_names: str,
    home: Path | None = None,
) -> Tuple[int, str]:
    claude_dir = _resolve_claude_dir(home)
    scenarios_dir, _, _ = _ensure_scenarios_dir(claude_dir)

    if yaml is None:
        return 1, _color("PyYAML is required to validate scenarios.", RED)  # type: ignore[unreachable]

    messages: List[str] = []
    targets = _collect_scenario_targets(scenario_names, scenarios_dir, messages)

    schema: Dict[str, Any] = {}
    schema_path = _scenario_schema_path(claude_dir)
    if schema_path.is_file():
        ok, raw_schema, error = _load_yaml(schema_path)
        if not ok:
            return 1, _color(f"Failed to parse schema: {error}", RED)
        if isinstance(raw_schema, dict):
            schema = raw_schema

    required_fields = schema.get("required", [])
    fields = schema.get("fields", {})
    allowed_types = set(fields.get("type", {}).get("enum", []))
    allowed_priorities = set(fields.get("priority", {}).get("enum", []))
    allowed_conditions = set(fields.get("condition", {}).get("enum", []))

    if not targets:
        messages.append(_color("No scenario files found for validation", YELLOW))
        return 0, "\n".join(messages)

    exit_code = 0
    for scenario_file in targets:
        success, data, error = _load_yaml_dict(scenario_file)
        if not success:
            messages.append(f"[ERROR] {scenario_file.name}: {error}")
            exit_code = 1
            continue

        errors: List[str] = []
        warnings: List[str] = []

        for key in required_fields:
            if not data.get(key):
                errors.append(f"missing required field '{key}'")

        scenario_type = str(data.get("type", "operational"))
        if allowed_types and scenario_type not in allowed_types:
            warnings.append(
                f"[WARN] {scenario_file.name}: unknown type '{scenario_type}' "
                f"(allowed: {sorted(allowed_types)})"
            )

        priority = str(data.get("priority", "normal"))
        if allowed_priorities and priority not in allowed_priorities:
            warnings.append(
                f"[WARN] {scenario_file.name}: unknown priority '{priority}' "
                f"(allowed: {sorted(allowed_priorities)})"
            )

        phases = data.get("phases")
        if not isinstance(phases, list) or not phases:
            errors.append("'phases' must be a non-empty list")
            phases = []

        for idx, phase in enumerate(phases):
            if not isinstance(phase, dict):
                errors.append(f"phase {idx}: must be an object")
                continue
            if not phase.get("name"):
                errors.append(f"phase {idx}: missing 'name'")
            condition = str(phase.get("condition", "manual"))
            if allowed_conditions and condition not in allowed_conditions:
                warnings.append(
                    f"[WARN] {scenario_file.name}: phase {idx} unknown condition '{condition}' "
                    f"(allowed: {sorted(allowed_conditions)})"
                )
            _ensure_list(phase.get("agents"), f"phases[{idx}].agents", errors)
            _ensure_list(phase.get("profiles"), f"phases[{idx}].profiles", errors)
            if "agents" not in phase and "profiles" not in phase:
                warnings.append(
                    f"[WARN] {scenario_file.name}: phase {idx} has no agents or profiles defined"
                )

        if errors:
            messages.append(f"[ERROR] {scenario_file.name}: {'; '.join(errors)}")
            exit_code = 1
            continue

        messages.extend(warnings)
        messages.append(f"[OK] {scenario_file.name}: valid scenario definition")

    return exit_code, "\n".join(messages)


def scenario_status(home: Path | None = None) -> str:
    claude_dir = _resolve_claude_dir(home)
    _, state_dir, lock_dir = _ensure_scenarios_dir(claude_dir)

    lines: List[str] = []

    locks: List[Tuple[str, str]] = []
    for lock_file in sorted(lock_dir.glob("*.lock")):
        try:
            exec_id = lock_file.read_text(encoding="utf-8").strip()
        except OSError:
            exec_id = ""
        locks.append((lock_file.stem, exec_id))

    if locks:
        lines.append("Active locks:")
        for scenario, exec_id in locks:
            suffix = f": execution {exec_id}" if exec_id else ""
            lines.append(f"- {scenario}{suffix}")
        lines.append("")

    entries: List[Tuple[str, str, str, str]] = []
    for state_file in sorted(state_dir.glob("*.json"), reverse=True):
        try:
            data = json.loads(state_file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        entries.append(
            (
                str(data.get("scenario", "unknown")),
                str(data.get("status", "unknown")),
                str(data.get("started", "unknown")),
                str(data.get("completed", "")),
            )
        )

    if entries:
        lines.append("Recent scenario executions:\n")
        for scenario, status, started, completed in entries[:10]:
            lines.append(f"- {scenario} ({status})")
            lines.append(f"  started: {started}")
            if completed:
                lines.append(f"  completed: {completed}")
    else:
        lines.append("No scenario executions logged yet.")

    return "\n".join(lines)


def scenario_stop(scenario_name: str, home: Path | None = None) -> Tuple[int, str]:
    """Stop a running scenario by clearing its lock."""
    claude_dir = _resolve_claude_dir(home)
    _, _, lock_dir = _ensure_scenarios_dir(claude_dir)

    if not scenario_name:
        return 1, _color("Provide a scenario name to stop", RED)

    lock_file = lock_dir / f"{_scenario_lock_basename(scenario_name)}.lock"
    if not lock_file.is_file():
        return 0, _color(f"No active lock for scenario '{scenario_name}'", YELLOW)

    try:
        lock_file.unlink()
    except OSError as exc:
        return 1, _color(f"Failed to clear lock: {exc}", RED)

    return 0, _color(f"Cleared lock for scenario '{scenario_name}'", GREEN)


def scenario_run(
    scenario_name: str,
    *options: str,
    home: Path | None = None,
    input_fn: Optional[Callable[[str], str]] = None,
) -> Tuple[int, str]:
    """Run a scenario, supporting interactive, automatic, and plan modes."""
    claude_dir = _resolve_claude_dir(home)
    scenarios_dir, state_dir, lock_dir = _ensure_scenarios_dir(claude_dir)

    if not scenario_name:
        message = _color("Specify a scenario name", RED)
        return 1, f"{message}\n{scenario_list(home=home)}"

    run_mode = "interactive"
    warnings: List[str] = []
    for option in options:
        if not option:
            continue
        normalized = option.lower()
        if normalized in ("--auto", "--automatic", "automatic"):
            run_mode = "automatic"
        elif normalized in ("--interactive", "interactive"):
            run_mode = "interactive"
        elif normalized in (
            "--plan",
            "--preview",
            "--validate",
            "plan",
            "preview",
            "validate",
        ):
            run_mode = "plan"
        else:
            warnings.append(_color(f"Ignoring unknown option '{option}'", YELLOW))

    scenario_filename = (
        scenario_name if scenario_name.endswith(".yaml") else f"{scenario_name}.yaml"
    )
    scenario_file = scenarios_dir / scenario_filename
    if not scenario_file.is_file():
        message = _color(f"Scenario file not found: {scenario_name}", RED)
        return 1, f"{message}\n{scenario_list(home=home)}"

    if yaml is None:
        return 1, _color("PyYAML is required to run scenarios.", RED)  # type: ignore[unreachable]

    code, metadata, error_msg = _parse_scenario_metadata(scenario_file)
    if code != 0 or metadata is None:
        return 1, _color(f"Error: {error_msg}", RED)

    if run_mode == "plan":
        preview_lines: List[str] = [
            *warnings,
            _color(f"Scenario preview: {metadata.name}", BLUE),
            f"Description: {metadata.description}",
            f"Priority: {metadata.priority}",
            f"Type: {metadata.scenario_type}",
            f"Phases: {len(metadata.phases)}",
        ]

        for idx, phase in enumerate(metadata.phases, 1):
            preview_lines.append("")
            preview_lines.append(f"- Phase {idx}: {phase.name}")
            if phase.description:
                preview_lines.append(f"  {phase.description}")
            preview_lines.append(f"  condition: {phase.condition}")
            preview_lines.append(f"  parallel: {'true' if phase.parallel else 'false'}")
            if phase.profiles:
                preview_lines.append(f"  profiles: {','.join(phase.profiles)}")
            if phase.agents:
                preview_lines.append(f"  agents: {','.join(phase.agents)}")
            if phase.success:
                preview_lines.append(f"  success checks: {','.join(phase.success)}")

        return 0, "\n".join(preview_lines)

    input_cb = input_fn or input
    lock_name = _scenario_lock_basename(metadata.name)
    lock_file = lock_dir / f"{lock_name}.lock"
    if lock_file.exists():
        return 1, _color(
            f"Scenario '{metadata.name}' already running (lock present). Use 'cortex orchestrate stop {metadata.name}' if the previous run is stuck.",
            RED,
        )

    exec_id = str(int(time.time()))
    lock_file.write_text(exec_id, encoding="utf-8")
    state_file = state_dir / f"{lock_name}-{exec_id}.json"
    _scenario_init_state(state_file, metadata)

    lines: List[str] = warnings.copy()
    lines.append(_color(f"=== Executing scenario: {metadata.name} ===", BLUE))
    lines.append(f"Description: {metadata.description}")
    lines.append(f"Priority: {metadata.priority}")
    lines.append(f"Type: {metadata.scenario_type}")
    lines.append(f"Run mode: {run_mode}")
    lines.append(f"Execution id: {exec_id}")
    lines.append("")

    exit_code = 0
    try:
        for idx, phase in enumerate(metadata.phases):
            lines.append(_color(f"Phase {idx + 1}: {phase.name}", YELLOW))
            if phase.description:
                lines.append(f"  {phase.description}")
            lines.append(f"  condition: {phase.condition}")
            lines.append(f"  parallel: {'true' if phase.parallel else 'false'}")
            if phase.profiles:
                lines.append(f"  profiles: {','.join(phase.profiles)}")
            if phase.agents:
                lines.append(f"  agents: {','.join(phase.agents)}")
            if phase.success:
                lines.append(f"  success checks: {','.join(phase.success)}")

            if run_mode == "interactive" and phase.condition != "manual":
                response = input_cb("Execute this phase now? [y/N] ")
                if not response or response.strip().lower()[0] != "y":
                    lines.append("  Skipping phase on user request")
                    _scenario_update_phase_state(
                        state_file,
                        index=idx,
                        phase_name=phase.name,
                        status="skipped",
                        note="user skipped",
                    )
                    lines.append("")
                    continue

            _scenario_update_phase_state(
                state_file,
                index=idx,
                phase_name=phase.name,
                status="running",
            )

            for profile in phase.profiles:
                lines.append(f"  -> Loading profile: {profile}")

            for agent in phase.agents:
                lines.append(f"  -> Activating agent: {agent}")
                try:
                    filename = _normalize_agent_filename(agent)
                except ValueError:
                    filename = f"{agent}.md"
                if _find_agent_file_any_state(claude_dir, filename) is None:
                    lines.append(
                        "    "
                        + _color(f"Warning: could not activate '{agent}'", YELLOW)
                    )

            _generate_dependency_map(claude_dir)
            _scenario_update_phase_state(
                state_file,
                index=idx,
                phase_name=phase.name,
                status="completed",
            )
            lines.append("")

        _scenario_finalize_state(state_file, "completed")
        lines.append(_color(f"Scenario '{metadata.name}' completed", GREEN))
    except Exception as exc:  # pragma: no cover - defensive fallback
        _scenario_finalize_state(state_file, "failed")
        lines.append(_color(f"Scenario '{metadata.name}' failed: {exc}", RED))
        exit_code = 1
    finally:
        try:
            lock_file.unlink()
        except OSError:
            pass

    return exit_code, "\n".join(lines)


def scenario_preview(scenario_name: str, home: Path | None = None) -> Tuple[int, str]:
    """Preview a scenario without executing it."""
    return scenario_run(scenario_name, "plan", home=home)
