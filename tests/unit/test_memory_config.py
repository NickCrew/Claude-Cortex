"""Unit tests for memory/config.py — scope-aware vault path resolution."""

from __future__ import annotations

from pathlib import Path

import pytest

from claude_ctx_py.memory.config import (
    MemoryConfig,
    _default_vault_path,
    get_vault_path,
)


@pytest.fixture(autouse=True)
def _clean_vault_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Strip ambient overrides so each test controls resolution explicitly."""
    monkeypatch.delenv("CORTEX_MEMORY_VAULT", raising=False)
    monkeypatch.delenv("CORTEX_SCOPE", raising=False)


# ── default resolution by scope ─────────────────────────────────────────────


@pytest.mark.unit
def test_default_vault_global_scope() -> None:
    assert _default_vault_path(scope="global") == Path.home() / ".cortex" / "vault"


@pytest.mark.unit
def test_default_vault_auto_scope_is_global() -> None:
    assert _default_vault_path(scope="auto") == Path.home() / ".cortex" / "vault"


@pytest.mark.unit
def test_default_vault_project_scope(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    project = tmp_path / "proj"
    (project / ".claude").mkdir(parents=True)
    monkeypatch.chdir(project)

    result = _default_vault_path(scope="project")

    assert result.resolve() == (project / ".cortex" / "vault").resolve()


@pytest.mark.unit
def test_default_vault_reads_scope_from_env(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    project = tmp_path / "proj"
    (project / ".claude").mkdir(parents=True)
    monkeypatch.chdir(project)
    monkeypatch.setenv("CORTEX_SCOPE", "project")

    result = _default_vault_path()

    assert result.resolve() == (project / ".cortex" / "vault").resolve()


# ── get_vault_path precedence ───────────────────────────────────────────────


@pytest.mark.unit
def test_env_override_beats_scope_default(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    custom = tmp_path / "custom-vault"
    monkeypatch.setenv("CORTEX_MEMORY_VAULT", str(custom))
    monkeypatch.setenv("CORTEX_SCOPE", "project")

    assert get_vault_path() == custom


@pytest.mark.unit
def test_explicit_config_beats_scope_default(tmp_path: Path) -> None:
    config = MemoryConfig(vault_path=str(tmp_path / "configured"))

    assert get_vault_path(config) == tmp_path / "configured"


@pytest.mark.unit
def test_unset_config_falls_back_to_scope_default() -> None:
    config = MemoryConfig()  # vault_path is None

    assert get_vault_path(config) == Path.home() / ".cortex" / "vault"


@pytest.mark.unit
def test_legacy_basic_memory_config_is_honoured() -> None:
    # Existing configs that persisted the old default keep their vault.
    config = MemoryConfig(vault_path="~/basic-memory")

    assert get_vault_path(config) == Path.home() / "basic-memory"
