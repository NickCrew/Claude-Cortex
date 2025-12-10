"""Intelligence subsystem for claude-ctx framework.

This package provides AI-powered features including:
- Pattern learning from session history
- Semantic similarity matching using embeddings
- Optional LLM-powered analysis (user opt-in)
- Hybrid recommendation system

The intelligence system learns from successful sessions and makes
recommendations about which agents to activate based on context.
"""

from __future__ import annotations

# Core intelligence classes (always available)
from claude_ctx_py.intelligence.base import (
    AgentRecommendation,
    ContextDetector,
    IntelligentAgent,
    PatternLearner,
    SessionContext,
    WorkflowPrediction,
)

__all__ = [
    "AgentRecommendation",
    "ContextDetector",
    "IntelligentAgent",
    "PatternLearner",
    "SessionContext",
    "WorkflowPrediction",
]

# Optional semantic intelligence (requires fastembed)
try:
    from claude_ctx_py.intelligence.semantic import SemanticMatcher

    __all__.append("SemanticMatcher")
    SEMANTIC_AVAILABLE = True
except ImportError:
    SEMANTIC_AVAILABLE = False

# Optional LLM intelligence (requires anthropic)
try:
    from claude_ctx_py.intelligence.semantic import LLMIntelligence

    __all__.append("LLMIntelligence")
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
