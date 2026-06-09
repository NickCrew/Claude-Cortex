"""`.cortex/manifest.yaml` — project-scope skill declarations.

The manifest is the source of truth for which skills a project wants.
``reconcile()`` is the idempotent sync operation that materialises the
declared set on disk (copy → .agents, relative symlink → .claude).

Schema (extensible):

  skills:
    enabled: [systematic-debugging, atomic-commits]
  # future: agents:, rules:, mcp:
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any, Dict, List

_MANIFEST_PATH = ".cortex/manifest.yaml"


class ReconcileReport:
    """Summary of what reconcile() changed."""

    def __init__(self) -> None:
        self.added: List[str] = []
        self.removed: List[str] = []
        self.refreshed: List[str] = []
        self.unchanged: List[str] = []
        self.errors: List[str] = []

    def __repr__(self) -> str:
        return (
            f"ReconcileReport(added={self.added}, removed={self.removed}, "
            f"refreshed={self.refreshed}, unchanged={self.unchanged}, "
            f"errors={self.errors})"
        )


def load_manifest(project_root: Path) -> Dict[str, Any]:
    """Load ``.cortex/manifest.yaml`` from *project_root*.

    Returns ``{}`` on missing or malformed file — same degradation pattern as
    ``load_skills_registry`` in skills.py.
    """
    from .base import _load_yaml_dict

    manifest_path = project_root / _MANIFEST_PATH
    if not manifest_path.exists():
        return {}
    ok, data, _err = _load_yaml_dict(manifest_path)
    if not ok:
        return {}
    return data


def write_manifest(project_root: Path, data: Dict[str, Any]) -> None:
    """Write *data* to ``.cortex/manifest.yaml`` under *project_root*.

    Creates the ``.cortex/`` directory if absent.
    """
    try:
        import yaml
    except ImportError as exc:
        raise RuntimeError("PyYAML is required to write manifests") from exc

    manifest_dir = project_root / ".cortex"
    manifest_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = manifest_dir / "manifest.yaml"
    manifest_path.write_text(yaml.safe_dump(data, sort_keys=True), encoding="utf-8")


def reconcile(
    project_root: Path,
    *,
    refresh_drift: bool = True,
    cortex_root: Path | None = None,
) -> ReconcileReport:
    """Sync the filesystem to the manifest declaration.

    For each skill listed in ``manifest.skills.enabled``:
    - Ensure a ``.agents/skills/<name>`` copy exists.
    - Ensure a relative ``.claude/skills/<name>`` symlink exists.
    - If ``refresh_drift`` is True and the copy is stale vs the bundle,
      refresh it.

    Skills present in ``.agents/skills/`` but *not* in the manifest are
    removed (both the agents copy and the .claude symlink).

    Args:
        project_root: Root of the project (parent of ``.claude`` and ``.agents``).
        refresh_drift: When True, stale .agents copies are refreshed from the
            bundle. When False, staleness is recorded but not fixed.
        cortex_root: Override for the bundle root (resolves automatically if None).

    Returns:
        ReconcileReport describing what changed.
    """
    from .base import _resolve_cortex_root
    from .skill_link import DriftStatus, link_skill, skill_drift_status, unlink_skill

    if cortex_root is None:
        cortex_root = _resolve_cortex_root()

    report = ReconcileReport()
    manifest = load_manifest(project_root)
    enabled: List[str] = []
    skills_section = manifest.get("skills", {})
    if isinstance(skills_section, dict):
        raw = skills_section.get("enabled", [])
        if isinstance(raw, list):
            enabled = [str(s) for s in raw if s]

    claude_dir = project_root / ".claude"
    claude_dir.mkdir(parents=True, exist_ok=True)

    # ── ensure declared skills are installed ──────────────────────────────
    for name in enabled:
        bundle = cortex_root / "skills" / name
        if not bundle.exists():
            report.errors.append(f"{name}: bundle not found at {bundle}")
            continue

        drift = skill_drift_status(project_root, name, cortex_root)

        if drift == DriftStatus.NOT_INSTALLED:
            code, msg = link_skill(bundle, claude_dir, scope="project")
            if code == 0:
                report.added.append(name)
            else:
                report.errors.append(f"{name}: {msg}")
        elif drift == DriftStatus.STALE and refresh_drift:
            code, msg = link_skill(bundle, claude_dir, scope="project")
            if code == 0:
                report.refreshed.append(name)
            else:
                report.errors.append(f"{name}: {msg}")
        else:
            report.unchanged.append(name)

    # ── remove skills present but not declared ────────────────────────────
    agents_skills_dir = project_root / ".agents" / "skills"
    if agents_skills_dir.is_dir():
        enabled_set = set(enabled)
        for installed in sorted(agents_skills_dir.iterdir()):
            if not installed.is_dir():
                continue
            if installed.name not in enabled_set:
                code, msg = unlink_skill(claude_dir, installed.name, scope="project")
                if code == 0:
                    report.removed.append(installed.name)
                else:
                    report.errors.append(f"{installed.name}: {msg}")

    return report
