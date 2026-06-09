"""Unit tests for cost-segment visibility in the status line.

Cost is rendered only under metered, per-token billing (an API key or a
cloud backend). On a subscription/OAuth session the figure Claude Code
reports is notional, so the segment is suppressed unless ``show_cost`` is
forced on.
"""

from __future__ import annotations

import pytest

from claude_ctx_py import statusline
from claude_ctx_py.statusline import (
    DEFAULT_CONFIG,
    StatusData,
    _metered_billing,
    _should_show_cost,
    format_default,
    format_oneline,
)

pytestmark = pytest.mark.unit


_BILLING_ENV = (
    "ANTHROPIC_API_KEY",
    "ANTHROPIC_AUTH_TOKEN",
    "CLAUDE_CODE_USE_BEDROCK",
    "CLAUDE_CODE_USE_VERTEX",
)


@pytest.fixture(autouse=True)
def _clear_billing_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Start each test from a subscription-like environment (no billing vars)."""
    for name in _BILLING_ENV:
        monkeypatch.delenv(name, raising=False)


@pytest.fixture
def data() -> StatusData:
    return StatusData(cwd="/tmp/proj", cost_usd=1.23, lines_added=5, lines_removed=2)


@pytest.fixture
def config() -> dict:
    cfg = DEFAULT_CONFIG.copy()
    # Avoid invoking external probes (git/venv/...) during render-path tests.
    for key in ("show_git", "show_venv", "show_node"):
        cfg[key] = False
    return cfg


# --- billing detection ---------------------------------------------------


@pytest.mark.parametrize("var", _BILLING_ENV)
def test_metered_billing_true_for_each_env(
    monkeypatch: pytest.MonkeyPatch, var: str
) -> None:
    monkeypatch.setenv(var, "1")
    assert _metered_billing() is True


def test_metered_billing_false_without_env() -> None:
    assert _metered_billing() is False


def test_empty_env_value_is_not_metered(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "")
    assert _metered_billing() is False


# --- show_cost resolution ------------------------------------------------


def test_auto_defers_to_billing(monkeypatch: pytest.MonkeyPatch) -> None:
    cfg = {"show_cost": "auto"}
    assert _should_show_cost(cfg) is False
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
    assert _should_show_cost(cfg) is True


def test_default_config_is_auto() -> None:
    assert DEFAULT_CONFIG["show_cost"] == "auto"
    assert _should_show_cost({}) is False  # missing key behaves as auto


def test_explicit_true_forces_on() -> None:
    assert _should_show_cost({"show_cost": True}) is True


def test_explicit_false_forces_off(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
    assert _should_show_cost({"show_cost": False}) is False


# --- render integration --------------------------------------------------


def test_default_hides_cost_on_subscription(data: StatusData, config: dict) -> None:
    assert "$" not in format_default(data, config)


def test_default_shows_cost_with_api_key(
    monkeypatch: pytest.MonkeyPatch, data: StatusData, config: dict
) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
    assert "$1.23" in format_default(data, config)


def test_default_bedrock_multiplier_still_applies(
    monkeypatch: pytest.MonkeyPatch, data: StatusData, config: dict
) -> None:
    monkeypatch.setenv("CLAUDE_CODE_USE_BEDROCK", "1")
    out = format_default(data, config)
    assert "(b5k)" in out
    assert "$1.54" in out  # 1.23 * 1.25, two-decimal


def test_oneline_hides_cost_on_subscription(data: StatusData, config: dict) -> None:
    assert "$" not in format_oneline(data, config)


def test_oneline_shows_cost_with_api_key(
    monkeypatch: pytest.MonkeyPatch, data: StatusData, config: dict
) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
    assert "$1.23" in format_oneline(data, config)


def test_json_always_includes_cost(data: StatusData) -> None:
    # JSON output is for scripting; the raw number is kept regardless of plan.
    out = statusline.format_json(data, {})
    assert '"cost_usd": 1.23' in out
