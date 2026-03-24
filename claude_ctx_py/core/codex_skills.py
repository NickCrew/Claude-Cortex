"""LLM provider skills symlinking management.

Supports multiple providers (codex, gemini, etc.) by symlinking
bundled cortex skills into provider-specific skill directories
(e.g., ~/.codex/skills, ~/.gemini/skills).
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Literal, Optional, Tuple

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]

from .base import _resolve_cortex_root

# ---------------------------------------------------------------------------
# Supported providers
# ---------------------------------------------------------------------------

SkillProvider = Literal["codex", "gemini"]

SKILL_PROVIDERS: List[SkillProvider] = ["codex", "gemini"]

PROVIDER_LABELS: Dict[SkillProvider, str] = {
    "codex": "Codex",
    "gemini": "Gemini",
}

PROVIDER_ICONS: Dict[SkillProvider, str] = {
    "codex": "🤖",
    "gemini": "✦",
}


# ---------------------------------------------------------------------------
# Path resolution — provider-parameterized
# ---------------------------------------------------------------------------


def _resolve_provider_skills_dir(provider: SkillProvider = "codex") -> Path:
    """Resolve ~/.<provider>/skills directory, create if needed."""
    skills_dir = Path.home() / f".{provider}" / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)
    return skills_dir


def _resolve_cortex_skills_root() -> Path:
    """Resolve bundled cortex skills directory."""
    return _resolve_cortex_root() / "skills"


def _resolve_provider_native_skills_dir(
    provider: SkillProvider = "codex",
) -> Path:
    """Resolve bundled provider-native skills directory (<provider>/skills/)."""
    return _resolve_cortex_root() / provider / "skills"


# ---------------------------------------------------------------------------
# Backward-compatible aliases
# ---------------------------------------------------------------------------


def _resolve_codex_skills_dir() -> Path:
    """Resolve ~/.codex/skills directory, create if needed."""
    return _resolve_provider_skills_dir("codex")


def _resolve_codex_native_skills_dir() -> Path:
    """Resolve bundled codex-native skills directory (codex/skills/)."""
    return _resolve_provider_native_skills_dir("codex")


# ---------------------------------------------------------------------------
# Symlink helper
# ---------------------------------------------------------------------------


def _ensure_skill_symlink(source: Path, target: Path) -> Optional[str]:
    """Create a skill symlink, returning warning if it fails.

    Pattern adapted from rules.py::_ensure_symlink.
    """
    if target.exists() or target.is_symlink():
        if target.is_symlink() and target.resolve() == source.resolve():
            return None  # Already correct
        if target.is_symlink():
            target.unlink()  # Remove stale symlink
        else:
            return f"Skipping non-symlink file: {target}"
    target.symlink_to(source)
    return None


# ---------------------------------------------------------------------------
# Scanning
# ---------------------------------------------------------------------------


def scan_provider_native_skills(
    provider: SkillProvider = "codex",
) -> List[Dict[str, str | bool]]:
    """Scan <provider>/skills/ for provider-native skills.

    Returns:
        List of dicts with keys: name, path, is_linked
    """
    native_dir = _resolve_provider_native_skills_dir(provider)
    provider_skills_dir = _resolve_provider_skills_dir(provider)
    results: List[Dict[str, str | bool]] = []

    if not native_dir.exists():
        return results

    for skill_dir in sorted(native_dir.iterdir()):
        if not skill_dir.is_dir() or not (skill_dir / "SKILL.md").exists():
            continue

        target = provider_skills_dir / skill_dir.name
        is_linked = (
            target.is_symlink()
            and target.resolve() == skill_dir.resolve()
        )
        results.append({
            "name": skill_dir.name,
            "path": str(skill_dir),
            "is_linked": is_linked,
        })

    return results


def scan_provider_skill_status(
    provider: SkillProvider = "codex",
) -> Dict[str, bool]:
    """Scan ~/.<provider>/skills and return linked status.

    Returns:
        Dict mapping skill_name -> is_linked (bool)
    """
    provider_skills_dir = _resolve_provider_skills_dir(provider)
    cortex_skills_root = _resolve_cortex_skills_root()

    status: Dict[str, bool] = {}
    if not cortex_skills_root.exists():
        return status

    # Check each skill in cortex/skills
    for skill_dir in cortex_skills_root.iterdir():
        if not skill_dir.is_dir() or not (skill_dir / "SKILL.md").exists():
            continue

        skill_name = skill_dir.name
        target = provider_skills_dir / skill_name

        # Check if symlink exists and points to cortex
        is_linked = (
            target.is_symlink()
            and target.resolve() == skill_dir.resolve()
        )
        status[skill_name] = is_linked

    return status


# ---------------------------------------------------------------------------
# Link / unlink — single skill
# ---------------------------------------------------------------------------


def link_provider_skill(
    skill_name: str,
    provider: SkillProvider = "codex",
    source_dir: Optional[Path] = None,
) -> Tuple[int, str]:
    """Create symlink for a single skill into ~/.<provider>/skills/.

    Args:
        skill_name: Name of the skill directory.
        provider: Target provider.
        source_dir: Optional override for the skills source directory.
                    Defaults to the bundled cortex skills root.
    """
    skills_root = source_dir or _resolve_cortex_skills_root()
    provider_skills_dir = _resolve_provider_skills_dir(provider)

    source = skills_root / skill_name
    target = provider_skills_dir / skill_name

    if not source.exists():
        return 1, f"Skill not found: {skill_name}"

    warning = _ensure_skill_symlink(source, target)
    if warning:
        return 1, warning

    return 0, f"Linked: {skill_name}"


def unlink_provider_skill(
    skill_name: str,
    provider: SkillProvider = "codex",
) -> Tuple[int, str]:
    """Remove symlink for a single skill from ~/.<provider>/skills/."""
    provider_skills_dir = _resolve_provider_skills_dir(provider)
    target = provider_skills_dir / skill_name

    if not target.exists() and not target.is_symlink():
        return 1, f"Not linked: {skill_name}"

    if not target.is_symlink():
        return 1, f"Cannot unlink non-symlink: {skill_name}"

    target.unlink()
    return 0, f"Unlinked: {skill_name}"


# ---------------------------------------------------------------------------
# Link / unlink — by category
# ---------------------------------------------------------------------------


def link_provider_skills_by_category(
    category: str,
    registry: dict,
    provider: SkillProvider = "codex",
) -> Tuple[int, List[str]]:
    """Link all skills in a category for a provider."""
    messages: List[str] = []
    success_count = 0

    skills_data = registry.get("skills", {})
    for skill_name, skill_info in skills_data.items():
        categories = skill_info.get("categories", [])
        if category in categories:
            exit_code, msg = link_provider_skill(skill_name, provider)
            messages.append(msg)
            if exit_code == 0:
                success_count += 1

    return success_count, messages


def unlink_provider_skills_by_category(
    category: str,
    registry: dict,
    provider: SkillProvider = "codex",
) -> Tuple[int, List[str]]:
    """Unlink all skills in a category for a provider."""
    messages: List[str] = []
    success_count = 0

    skills_data = registry.get("skills", {})
    for skill_name, skill_info in skills_data.items():
        categories = skill_info.get("categories", [])
        if category in categories:
            exit_code, msg = unlink_provider_skill(skill_name, provider)
            messages.append(msg)
            if exit_code == 0:
                success_count += 1

    return success_count, messages


# ---------------------------------------------------------------------------
# Link / unlink — all
# ---------------------------------------------------------------------------


def link_all_provider_skills(
    registry: dict,
    provider: SkillProvider = "codex",
) -> Tuple[int, List[str]]:
    """Link all available skills for a provider."""
    messages: List[str] = []
    success_count = 0

    skills_data = registry.get("skills", {})
    for skill_name in skills_data.keys():
        exit_code, msg = link_provider_skill(skill_name, provider)
        messages.append(msg)
        if exit_code == 0:
            success_count += 1

    return success_count, messages


def unlink_all_provider_skills(
    provider: SkillProvider = "codex",
) -> Tuple[int, List[str]]:
    """Unlink all skills for a provider."""
    messages: List[str] = []
    success_count = 0

    provider_skills_dir = _resolve_provider_skills_dir(provider)
    if not provider_skills_dir.exists():
        return 0, []

    for item in provider_skills_dir.iterdir():
        if item.is_symlink():
            try:
                item.unlink()
                messages.append(f"Unlinked: {item.name}")
                success_count += 1
            except OSError as e:
                messages.append(f"Failed to unlink {item.name}: {e}")

    return success_count, messages


# ---------------------------------------------------------------------------
# Backward-compatible wrappers (delegate to provider-parameterized versions)
# ---------------------------------------------------------------------------


def scan_codex_native_skills() -> List[Dict[str, str | bool]]:
    """Scan codex/skills/ for codex-native skills."""
    return scan_provider_native_skills("codex")


def scan_codex_skill_status() -> Dict[str, bool]:
    """Scan ~/.codex/skills and return linked status."""
    return scan_provider_skill_status("codex")


def link_codex_skill(
    skill_name: str, source_dir: Optional[Path] = None
) -> Tuple[int, str]:
    """Create symlink for a single skill into ~/.codex/skills/."""
    return link_provider_skill(skill_name, "codex", source_dir)


def unlink_codex_skill(skill_name: str) -> Tuple[int, str]:
    """Remove symlink for a single skill from ~/.codex/skills/."""
    return unlink_provider_skill(skill_name, "codex")


def link_codex_skills_by_category(
    category: str, registry: dict
) -> Tuple[int, List[str]]:
    """Link all skills in a category for Codex."""
    return link_provider_skills_by_category(category, registry, "codex")


def unlink_codex_skills_by_category(
    category: str, registry: dict
) -> Tuple[int, List[str]]:
    """Unlink all skills in a category for Codex."""
    return unlink_provider_skills_by_category(category, registry, "codex")


def link_all_codex_skills(registry: dict) -> Tuple[int, List[str]]:
    """Link all available skills for Codex."""
    return link_all_provider_skills(registry, "codex")


def unlink_all_codex_skills() -> Tuple[int, List[str]]:
    """Unlink all Codex skills."""
    return unlink_all_provider_skills("codex")
