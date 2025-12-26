"""Configuration management for LLM intelligence features.

Handles:
- Model selection preferences
- Cost budget settings
- Prompt caching configuration
- LLM feature toggles
"""

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, Literal, Optional

from ..core.base import _resolve_claude_dir


CONFIG_FILE_NAME = "intelligence-config.json"

ModelName = Literal["claude-opus-4-20250514", "claude-sonnet-4-20250514", "claude-haiku-4-20250514"]


@dataclass
class ModelSelectionConfig:
    """Model selection preferences."""

    # Auto-select model based on complexity (recommended)
    auto_select: bool = True

    # Default model when not auto-selecting
    default_model: ModelName = "claude-sonnet-4-20250514"

    # Complexity threshold for Haiku (0.0-1.0)
    # Lower = more aggressive use of Haiku (more savings)
    haiku_threshold: float = 0.4

    # Complexity threshold for Opus (0.0-1.0)
    # Higher = less aggressive use of Opus (more savings)
    opus_threshold: float = 0.75

    # Override: Always use specific model (ignores auto_select)
    force_model: Optional[ModelName] = None


@dataclass
class CostBudgetConfig:
    """Cost budget and spending controls."""

    # Enable budget tracking
    enabled: bool = False

    # Daily spending limit in USD (0 = unlimited)
    daily_limit: float = 1.0

    # Warning threshold (percentage of daily limit)
    warning_threshold: float = 0.8

    # Require confirmation for requests over this cost
    confirmation_threshold: float = 0.01


@dataclass
class CachingConfig:
    """Prompt caching configuration."""

    # Enable prompt caching (reduces costs by ~90%)
    enabled: bool = True

    # Cache time-to-live in seconds (default: 5 minutes)
    # Note: Claude manages TTL automatically (~5 min)
    ttl: int = 300


@dataclass
class IntelligenceConfig:
    """LLM intelligence feature configuration."""

    # Enable LLM-powered recommendations (requires anthropic package)
    llm_enabled: bool = False

    # Model selection preferences
    model_selection: ModelSelectionConfig = field(default_factory=ModelSelectionConfig)

    # Cost budget settings
    budget: CostBudgetConfig = field(default_factory=CostBudgetConfig)

    # Caching configuration
    caching: CachingConfig = field(default_factory=CachingConfig)

    # Minimum confidence score for semantic matching fallback
    semantic_fallback_threshold: float = 0.5

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "llm_enabled": self.llm_enabled,
            "model_selection": asdict(self.model_selection),
            "budget": asdict(self.budget),
            "caching": asdict(self.caching),
            "semantic_fallback_threshold": self.semantic_fallback_threshold,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "IntelligenceConfig":
        """Create from dictionary."""
        model_selection_data = data.get("model_selection", {})
        budget_data = data.get("budget", {})
        caching_data = data.get("caching", {})

        return cls(
            llm_enabled=data.get("llm_enabled", False),
            model_selection=ModelSelectionConfig(
                auto_select=model_selection_data.get("auto_select", True),
                default_model=model_selection_data.get(
                    "default_model", "claude-sonnet-4-20250514"
                ),
                haiku_threshold=model_selection_data.get("haiku_threshold", 0.4),
                opus_threshold=model_selection_data.get("opus_threshold", 0.75),
                force_model=model_selection_data.get("force_model"),
            ),
            budget=CostBudgetConfig(
                enabled=budget_data.get("enabled", False),
                daily_limit=budget_data.get("daily_limit", 1.0),
                warning_threshold=budget_data.get("warning_threshold", 0.8),
                confirmation_threshold=budget_data.get("confirmation_threshold", 0.01),
            ),
            caching=CachingConfig(
                enabled=caching_data.get("enabled", True),
                ttl=caching_data.get("ttl", 300),
            ),
            semantic_fallback_threshold=data.get("semantic_fallback_threshold", 0.5),
        )


def _get_claude_dir() -> Path:
    """Get the Claude configuration directory."""
    return _resolve_claude_dir()


def _get_config_path() -> Path:
    """Get the path to the intelligence config file."""
    return _get_claude_dir() / CONFIG_FILE_NAME


def get_config() -> IntelligenceConfig:
    """Load intelligence configuration from file.

    Returns:
        IntelligenceConfig instance (defaults if file doesn't exist)
    """
    config_path = _get_config_path()

    if not config_path.exists():
        return IntelligenceConfig()

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return IntelligenceConfig.from_dict(data)
    except (json.JSONDecodeError, OSError):
        return IntelligenceConfig()


def save_config(config: IntelligenceConfig) -> None:
    """Save intelligence configuration to file.

    Args:
        config: IntelligenceConfig instance to save
    """
    config_path = _get_config_path()

    # Ensure directory exists
    config_path.parent.mkdir(parents=True, exist_ok=True)

    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config.to_dict(), f, indent=2)


def is_llm_enabled(config: Optional[IntelligenceConfig] = None) -> bool:
    """Check if LLM intelligence is enabled.

    Args:
        config: Optional config to use (loads if not provided)

    Returns:
        True if LLM intelligence is enabled
    """
    if config is None:
        config = get_config()

    return config.llm_enabled


def enable_llm(enabled: bool = True) -> IntelligenceConfig:
    """Enable or disable LLM intelligence.

    Args:
        enabled: Whether to enable LLM intelligence

    Returns:
        Updated IntelligenceConfig
    """
    config = get_config()
    config.llm_enabled = enabled
    save_config(config)
    return config


def get_model_preference(
    config: Optional[IntelligenceConfig] = None,
) -> tuple[bool, Optional[str]]:
    """Get model selection preferences.

    Args:
        config: Optional config to use (loads if not provided)

    Returns:
        Tuple of (auto_select, forced_model)
    """
    if config is None:
        config = get_config()

    return config.model_selection.auto_select, config.model_selection.force_model


def set_model_preference(
    auto_select: Optional[bool] = None,
    force_model: Optional[ModelName] = None,
    default_model: Optional[ModelName] = None,
) -> IntelligenceConfig:
    """Set model selection preferences.

    Args:
        auto_select: Enable auto model selection
        force_model: Always use specific model (overrides auto_select)
        default_model: Default model when not auto-selecting

    Returns:
        Updated IntelligenceConfig
    """
    config = get_config()

    if auto_select is not None:
        config.model_selection.auto_select = auto_select

    if force_model is not None:
        config.model_selection.force_model = force_model

    if default_model is not None:
        config.model_selection.default_model = default_model

    save_config(config)
    return config


def get_budget_config(
    config: Optional[IntelligenceConfig] = None,
) -> CostBudgetConfig:
    """Get cost budget configuration.

    Args:
        config: Optional config to use (loads if not provided)

    Returns:
        CostBudgetConfig instance
    """
    if config is None:
        config = get_config()

    return config.budget


def set_budget(
    enabled: Optional[bool] = None,
    daily_limit: Optional[float] = None,
    warning_threshold: Optional[float] = None,
) -> IntelligenceConfig:
    """Set cost budget parameters.

    Args:
        enabled: Enable budget tracking
        daily_limit: Daily spending limit in USD
        warning_threshold: Warning threshold (0.0-1.0)

    Returns:
        Updated IntelligenceConfig
    """
    config = get_config()

    if enabled is not None:
        config.budget.enabled = enabled

    if daily_limit is not None:
        config.budget.daily_limit = daily_limit

    if warning_threshold is not None:
        config.budget.warning_threshold = warning_threshold

    save_config(config)
    return config


def is_caching_enabled(config: Optional[IntelligenceConfig] = None) -> bool:
    """Check if prompt caching is enabled.

    Args:
        config: Optional config to use (loads if not provided)

    Returns:
        True if caching is enabled
    """
    if config is None:
        config = get_config()

    return config.caching.enabled


def set_caching_enabled(enabled: bool = True) -> IntelligenceConfig:
    """Enable or disable prompt caching.

    Args:
        enabled: Whether to enable prompt caching

    Returns:
        Updated IntelligenceConfig
    """
    config = get_config()
    config.caching.enabled = enabled
    save_config(config)
    return config
