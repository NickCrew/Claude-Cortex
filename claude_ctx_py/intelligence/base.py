"""Intelligent automation system for claude-ctx framework.

This module provides AI-powered features that learn from usage patterns,
predict needs, and auto-manage the framework without manual intervention.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Set, Tuple, Any
from collections import defaultdict, Counter


@dataclass
class SessionContext:
    """Represents the current session context for intelligent decision-making."""

    # File context
    files_changed: List[str]
    file_types: Set[str]
    directories: Set[str]

    # Code context
    has_tests: bool
    has_auth: bool
    has_api: bool
    has_frontend: bool
    has_backend: bool
    has_database: bool

    # Activity context
    errors_count: int
    test_failures: int
    build_failures: int

    # Time context
    session_start: datetime
    last_activity: datetime

    # Current state
    active_agents: List[str]
    active_modes: List[str]
    active_rules: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "files_changed": self.files_changed,
            "file_types": list(self.file_types),
            "directories": list(self.directories),
            "has_tests": self.has_tests,
            "has_auth": self.has_auth,
            "has_api": self.has_api,
            "has_frontend": self.has_frontend,
            "has_backend": self.has_backend,
            "has_database": self.has_database,
            "errors_count": self.errors_count,
            "test_failures": self.test_failures,
            "build_failures": self.build_failures,
            "session_start": self.session_start.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "active_agents": self.active_agents,
            "active_modes": self.active_modes,
            "active_rules": self.active_rules,
        }


@dataclass
class AgentRecommendation:
    """Represents an intelligent agent recommendation."""

    agent_name: str
    confidence: float  # 0.0 to 1.0
    reason: str
    urgency: str  # low, medium, high, critical
    auto_activate: bool
    context_triggers: List[str]

    def should_notify(self) -> bool:
        """Determine if this should notify the user."""
        return self.confidence >= 0.7 or self.urgency in ("high", "critical")


@dataclass
class AgentDeactivationRecommendation:
    """Represents a recommendation to deactivate an active agent."""

    agent_name: str
    confidence: float  # 0.0 to 1.0
    reason: str
    urgency: str  # low, medium, high
    auto_deactivate: bool
    inactive_duration: int  # seconds since last relevant activity
    resource_impact: str  # low, medium, high

    def should_notify(self) -> bool:
        """Determine if this should notify the user."""
        return self.confidence >= 0.6 or self.urgency in ("medium", "high")


@dataclass
class WorkflowPrediction:
    """Predicted workflow based on context."""

    workflow_name: str
    agents_sequence: List[str]
    confidence: float
    estimated_duration: int  # seconds
    success_probability: float
    based_on_pattern: str


class PatternLearner:
    """Learns patterns from successful sessions to make predictions.

    Combines:
    - Frequency-based pattern matching (fast, always available)
    - Semantic similarity matching (optional, requires fastembed)
    - Rule-based heuristics (reliable fallback)
    """

    def __init__(self, history_file: Path, enable_semantic: bool = True):
        """Initialize pattern learner.

        Args:
            history_file: Path to session history JSON file
            enable_semantic: Enable semantic matching (requires fastembed)
        """
        self.history_file = history_file
        self.patterns: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.agent_sequences: List[List[str]] = []
        self.success_contexts: List[Dict[str, Any]] = []

        # Optional semantic matcher
        self.semantic_matcher = None
        if enable_semantic:
            try:
                from claude_ctx_py.intelligence.semantic import SemanticMatcher
                cache_dir = history_file.parent / "semantic_cache"
                self.semantic_matcher = SemanticMatcher(cache_dir)
            except ImportError:
                pass  # Semantic matching will be disabled

        self._load_history()

    def _load_history(self) -> None:
        """Load session history from disk."""
        if not self.history_file.exists():
            return

        try:
            with open(self.history_file, "r") as f:
                data = json.load(f)
                self.patterns = data.get("patterns", {})
                self.agent_sequences = data.get("agent_sequences", [])
                self.success_contexts = data.get("success_contexts", [])
        except Exception:
            pass

    def record_success(
        self,
        context: SessionContext,
        agents_used: List[str],
        duration: int,
        outcome: str,
    ) -> None:
        """Record a successful session for learning.

        Args:
            context: Session context
            agents_used: List of agents that were active
            duration: Session duration in seconds
            outcome: Outcome description
        """
        session_data = {
            "timestamp": datetime.now().isoformat(),
            "context": context.to_dict(),
            "agents": agents_used,
            "duration": duration,
            "outcome": outcome,
            "files": context.files_changed,
        }

        # Store by primary context
        context_key = self._generate_context_key(context)
        self.patterns[context_key].append(session_data)

        # Store agent sequence
        self.agent_sequences.append(agents_used)

        # Store full context for similarity matching
        self.success_contexts.append(session_data)

        # Add to semantic matcher if available
        if self.semantic_matcher:
            self.semantic_matcher.add_session(session_data)

        # Persist to disk
        self._save_history()

    def _generate_context_key(self, context: SessionContext) -> str:
        """Generate a key representing the context type.

        Args:
            context: Session context

        Returns:
            Context key string
        """
        components = []

        if context.has_frontend:
            components.append("frontend")
        if context.has_backend:
            components.append("backend")
        if context.has_database:
            components.append("database")
        if context.has_tests:
            components.append("tests")
        if context.has_auth:
            components.append("auth")
        if context.has_api:
            components.append("api")

        return "_".join(sorted(components)) or "general"

    def predict_agents(self, context: SessionContext) -> List[AgentRecommendation]:
        """Predict which agents should be activated based on context.

        Uses a hybrid approach:
        1. Semantic similarity matching (if available) - finds similar sessions
        2. Frequency-based pattern matching - looks for exact context matches
        3. Rule-based heuristics - applies domain knowledge

        Args:
            context: Current session context

        Returns:
            List of agent recommendations sorted by confidence
        """
        recommendations = []
        context_key = self._generate_context_key(context)

        # Try semantic matching first (highest quality)
        semantic_recs = self._semantic_recommendations(context)
        if semantic_recs:
            recommendations.extend(semantic_recs)

        # Add frequency-based pattern matching
        pattern_recs = self._pattern_recommendations(context, context_key)
        recommendations.extend(pattern_recs)

        # Add rule-based recommendations (always run - good fallback)
        recommendations.extend(self._rule_based_recommendations(context))

        # Deduplicate by agent name, keeping highest confidence
        seen: Dict[str, AgentRecommendation] = {}
        for rec in recommendations:
            if rec.agent_name not in seen or rec.confidence > seen[rec.agent_name].confidence:
                seen[rec.agent_name] = rec

        # Sort by confidence
        final_recs = sorted(seen.values(), key=lambda r: r.confidence, reverse=True)

        return final_recs

    def _semantic_recommendations(
        self, context: SessionContext
    ) -> List[AgentRecommendation]:
        """Generate recommendations using semantic similarity.

        Args:
            context: Current session context

        Returns:
            List of recommendations from semantically similar sessions
        """
        if not self.semantic_matcher:
            return []

        # Prepare context for semantic matching
        context_dict = {
            "files": context.files_changed,
            "context": context.to_dict(),
        }

        # Find similar sessions
        similar = self.semantic_matcher.find_similar(
            context_dict, top_k=10, min_similarity=0.6
        )

        if not similar:
            return []

        # Aggregate agent recommendations from similar sessions
        agent_scores: Dict[str, float] = {}
        for session_data, similarity in similar:
            agents = session_data.get("agents", [])
            for agent in agents:
                # Weight by similarity score
                agent_scores[agent] = agent_scores.get(agent, 0) + similarity

        # Convert to recommendations
        recommendations = []
        for agent, score in sorted(
            agent_scores.items(), key=lambda x: x[1], reverse=True
        )[:10]:
            # Normalize score to 0-1 range (max 5 similar sessions at 1.0 similarity)
            confidence = min(score / 5.0, 1.0)

            if confidence >= 0.3:  # Only recommend if reasonably confident
                recommendations.append(
                    AgentRecommendation(
                        agent_name=agent,
                        confidence=confidence,
                        reason=f"Used in semantically similar sessions (match: {confidence:.0%})",
                        urgency="medium" if confidence > 0.7 else "low",
                        auto_activate=confidence > 0.85,
                        context_triggers=["semantic_match"],
                    )
                )

        return recommendations

    def _pattern_recommendations(
        self, context: SessionContext, context_key: str
    ) -> List[AgentRecommendation]:
        """Generate recommendations using frequency-based pattern matching.

        Args:
            context: Session context
            context_key: Generated context key

        Returns:
            List of recommendations from exact pattern matches
        """
        recommendations = []
        similar_sessions = self.patterns.get(context_key, [])

        if similar_sessions:
            # Count agent frequency in similar contexts
            agent_counts: Counter[str] = Counter()
            for session in similar_sessions:
                agent_counts.update(session["agents"])

            total_sessions = len(similar_sessions)

            # Generate recommendations based on frequency
            for agent, count in agent_counts.most_common(10):
                confidence = count / total_sessions

                # Only recommend if used in >30% of similar sessions
                if confidence >= 0.3:
                    recommendation = AgentRecommendation(
                        agent_name=agent,
                        confidence=confidence,
                        reason=f"Used in {count}/{total_sessions} {context_key} sessions",
                        urgency="medium" if confidence >= 0.7 else "low",
                        auto_activate=confidence >= 0.8,
                        context_triggers=[context_key],
                    )
                    recommendations.append(recommendation)

        return recommendations

    def _rule_based_recommendations(
        self, context: SessionContext
    ) -> List[AgentRecommendation]:
        """Generate rule-based recommendations based on context signals.

        Args:
            context: Session context

        Returns:
            List of recommendations
        """
        recommendations = []

        # Security recommendations
        if context.has_auth or any("auth" in f.lower() for f in context.files_changed):
            recommendations.append(
                AgentRecommendation(
                    agent_name="security-auditor",
                    confidence=0.9,
                    reason="Auth code detected - security review recommended",
                    urgency="high",
                    auto_activate=True,
                    context_triggers=["auth_code"],
                )
            )

        # Test recommendations
        if context.test_failures > 0:
            recommendations.append(
                AgentRecommendation(
                    agent_name="test-automator",
                    confidence=0.95,
                    reason=f"{context.test_failures} test failures detected",
                    urgency="critical",
                    auto_activate=True,
                    context_triggers=["test_failures"],
                )
            )

        # Code review recommendations
        if len(context.files_changed) >= 5:
            recommendations.append(
                AgentRecommendation(
                    agent_name="code-reviewer",
                    confidence=0.85,
                    reason=f"{len(context.files_changed)} files changed - review recommended",
                    urgency="medium",
                    auto_activate=False,
                    context_triggers=["large_changeset"],
                )
            )

        # Performance recommendations
        if context.has_database or context.has_api:
            recommendations.append(
                AgentRecommendation(
                    agent_name="performance-engineer",
                    confidence=0.7,
                    reason="Database/API changes - performance check recommended",
                    urgency="low",
                    auto_activate=False,
                    context_triggers=["database", "api"],
                )
            )

        # Documentation recommendations
        if context.has_api and len(context.files_changed) >= 3:
            recommendations.append(
                AgentRecommendation(
                    agent_name="api-documenter",
                    confidence=0.75,
                    reason="API changes detected - documentation update needed",
                    urgency="medium",
                    auto_activate=False,
                    context_triggers=["api_changes"],
                )
            )

        return recommendations

    def predict_deactivations(
        self, context: SessionContext, active_agents: List[str]
    ) -> List[AgentDeactivationRecommendation]:
        """Predict which active agents should be deactivated based on context.

        Identifies agents that are:
        - Not relevant to current context
        - Unused in similar past sessions
        - Active but not providing value
        - Consuming resources unnecessarily

        Args:
            context: Current session context
            active_agents: List of currently active agent names

        Returns:
            List of deactivation recommendations sorted by confidence
        """
        if not active_agents:
            return []

        recommendations = []
        context_key = self._generate_context_key(context)

        # Get agents that SHOULD be active for this context
        should_be_active = set()
        activation_recs = self.predict_agents(context)
        for rec in activation_recs:
            if rec.confidence >= 0.5:  # Reasonably confident they should be active
                should_be_active.add(rec.agent_name)

        # Check each active agent
        for agent_name in active_agents:
            # Skip if agent should definitely be active
            if agent_name in should_be_active:
                continue

            # Check historical usage in similar contexts
            usage_score = self._calculate_agent_usage(agent_name, context_key)

            # Determine if agent should be deactivated
            if usage_score < 0.3:  # Low usage in similar contexts
                confidence = 1.0 - usage_score  # Higher confidence if rarely used

                # Determine urgency and resource impact
                urgency = "low"
                resource_impact = "low"

                # High-resource agents get higher urgency
                if agent_name in {
                    "performance-engineer",
                    "security-auditor",
                    "code-reviewer",
                }:
                    resource_impact = "high"
                    urgency = "medium" if confidence > 0.7 else "low"

                # Very low usage gets higher urgency
                if usage_score < 0.1:
                    urgency = "medium"

                recommendations.append(
                    AgentDeactivationRecommendation(
                        agent_name=agent_name,
                        confidence=confidence,
                        reason=f"Low relevance to {context_key} context (used in {usage_score:.0%} of similar sessions)",
                        urgency=urgency,
                        auto_deactivate=confidence > 0.8 and resource_impact == "high",
                        inactive_duration=0,  # Could be enhanced with activity tracking
                        resource_impact=resource_impact,
                    )
                )

        # Sort by confidence (descending)
        recommendations.sort(key=lambda r: r.confidence, reverse=True)

        return recommendations

    def _calculate_agent_usage(self, agent_name: str, context_key: str) -> float:
        """Calculate how often an agent is used in similar contexts.

        Args:
            agent_name: Name of the agent
            context_key: Context key to check

        Returns:
            Usage score (0.0 to 1.0)
        """
        similar_sessions = self.patterns.get(context_key, [])

        if not similar_sessions:
            # No history - assume low usage but don't be too confident
            return 0.3

        # Count how often this agent was used
        usage_count = sum(
            1 for session in similar_sessions if agent_name in session.get("agents", [])
        )

        return usage_count / len(similar_sessions)

    def predict_workflow(self, context: SessionContext) -> Optional[WorkflowPrediction]:
        """Predict optimal workflow based on context.

        Args:
            context: Session context

        Returns:
            Workflow prediction or None
        """
        context_key = self._generate_context_key(context)
        similar_sessions = self.patterns.get(context_key, [])

        if len(similar_sessions) < 3:
            return None

        # Find most common agent sequence
        sequence_counts: Counter[Tuple[str, ...]] = Counter()
        for session in similar_sessions:
            seq_key = tuple(session["agents"])
            sequence_counts[seq_key] = sequence_counts.get(seq_key, 0) + 1

        if not sequence_counts:
            return None

        most_common_seq, count = sequence_counts.most_common(1)[0]
        confidence = count / len(similar_sessions)

        # Calculate average duration for this sequence
        durations = [
            s["duration"]
            for s in similar_sessions
            if tuple(s["agents"]) == most_common_seq
        ]
        avg_duration = int(sum(durations) / len(durations)) if durations else 600

        return WorkflowPrediction(
            workflow_name=f"auto_{context_key}",
            agents_sequence=list(most_common_seq),
            confidence=confidence,
            estimated_duration=avg_duration,
            success_probability=confidence,
            based_on_pattern=context_key,
        )

    def _save_history(self) -> None:
        """Save patterns to disk."""
        self.history_file.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "patterns": dict(self.patterns),
            "agent_sequences": self.agent_sequences,
            "success_contexts": self.success_contexts,
            "last_updated": datetime.now().isoformat(),
        }

        with open(self.history_file, "w") as f:
            json.dump(data, f, indent=2)


class ContextDetector:
    """Detects context from file system and code analysis."""

    @staticmethod
    def detect_from_files(files: List[Path]) -> SessionContext:
        """Detect context from a list of files.

        Args:
            files: List of file paths

        Returns:
            Session context
        """
        file_types = set()
        directories = set()
        files_changed = []

        # Analyze files
        for file_path in files:
            files_changed.append(str(file_path))
            file_types.add(file_path.suffix.lower())
            directories.add(str(file_path.parent))

        # Detect context signals
        has_tests = any("test" in str(f).lower() for f in files)
        has_auth = any("auth" in str(f).lower() for f in files)
        has_api = any(
            "api" in str(f).lower() or "routes" in str(f).lower() for f in files
        )
        has_frontend = any(
            ext in file_types
            for ext in {".tsx", ".jsx", ".vue", ".svelte", ".html", ".css"}
        )
        has_backend = any(
            ext in file_types for ext in {".py", ".go", ".java", ".rs", ".rb"}
        )
        has_database = any(
            "db" in str(f).lower()
            or "migration" in str(f).lower()
            or "schema" in str(f).lower()
            for f in files
        )

        return SessionContext(
            files_changed=files_changed,
            file_types=file_types,
            directories=directories,
            has_tests=has_tests,
            has_auth=has_auth,
            has_api=has_api,
            has_frontend=has_frontend,
            has_backend=has_backend,
            has_database=has_database,
            errors_count=0,
            test_failures=0,
            build_failures=0,
            session_start=datetime.now(),
            last_activity=datetime.now(),
            active_agents=[],
            active_modes=[],
            active_rules=[],
        )

    @staticmethod
    def detect_from_git() -> List[Path]:
        """Detect changed files from git.

        Returns:
            List of changed files
        """
        import subprocess

        try:
            # Get modified files from git
            result = subprocess.run(
                ["git", "diff", "--name-only", "HEAD"],
                capture_output=True,
                text=True,
                check=True,
            )

            files = [
                Path(line.strip()) for line in result.stdout.split("\n") if line.strip()
            ]

            return files
        except Exception:
            return []


class IntelligentAgent:
    """Main intelligent automation agent that orchestrates everything."""

    def __init__(self, data_dir: Path):
        """Initialize intelligent agent.

        Args:
            data_dir: Directory for storing learning data
        """
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)

        history_file = data_dir / "session_history.json"
        self.learner = PatternLearner(history_file)
        self.context_detector = ContextDetector()

        self.current_context: Optional[SessionContext] = None
        self.recommendations: List[AgentRecommendation] = []
        self.auto_activated: Set[str] = set()

    def analyze_context(self, files: Optional[List[Path]] = None) -> SessionContext:
        """Analyze current context.

        Args:
            files: Optional list of files (auto-detect from git if None)

        Returns:
            Session context
        """
        if files is None:
            files = self.context_detector.detect_from_git()

        self.current_context = self.context_detector.detect_from_files(files)
        return self.current_context

    def get_recommendations(self) -> List[AgentRecommendation]:
        """Get intelligent recommendations for current context.

        Returns:
            List of recommendations
        """
        if self.current_context is None:
            self.analyze_context()

        assert self.current_context is not None
        self.recommendations = self.learner.predict_agents(self.current_context)
        return self.recommendations

    def get_auto_activations(self) -> List[str]:
        """Get list of agents that should be auto-activated.

        Returns:
            List of agent names to activate
        """
        recommendations = self.get_recommendations()
        return [
            rec.agent_name
            for rec in recommendations
            if rec.auto_activate and rec.agent_name not in self.auto_activated
        ]

    def mark_auto_activated(self, agent_name: str) -> None:
        """Mark an agent as auto-activated.

        Args:
            agent_name: Agent that was activated
        """
        self.auto_activated.add(agent_name)

    def get_deactivation_recommendations(
        self, active_agents: Optional[List[str]] = None
    ) -> List[AgentDeactivationRecommendation]:
        """Get recommendations for agents that should be deactivated.

        Args:
            active_agents: List of currently active agents (uses current context if None)

        Returns:
            List of deactivation recommendations
        """
        if self.current_context is None:
            self.analyze_context()

        assert self.current_context is not None

        # Use active agents from context if not provided
        if active_agents is None:
            active_agents = self.current_context.active_agents

        return self.learner.predict_deactivations(self.current_context, active_agents)

    def predict_workflow(self) -> Optional[WorkflowPrediction]:
        """Predict optimal workflow for current context.

        Returns:
            Workflow prediction or None
        """
        if self.current_context is None:
            self.analyze_context()

        assert self.current_context is not None
        return self.learner.predict_workflow(self.current_context)

    def record_session_success(
        self, agents_used: List[str], duration: int, outcome: str = "success"
    ) -> None:
        """Record a successful session for learning.

        Args:
            agents_used: Agents that were used
            duration: Session duration in seconds
            outcome: Outcome description
        """
        if self.current_context is not None:
            self.learner.record_success(
                self.current_context,
                agents_used,
                duration,
                outcome,
            )

    def get_smart_suggestions(self) -> Dict[str, Any]:
        """Get comprehensive smart suggestions.

        Returns:
            Dictionary with all suggestions
        """
        recommendations = self.get_recommendations()
        workflow = self.predict_workflow()

        return {
            "agent_recommendations": [
                {
                    "agent": rec.agent_name,
                    "confidence": f"{rec.confidence * 100:.0f}%",
                    "reason": rec.reason,
                    "urgency": rec.urgency,
                    "auto_activate": rec.auto_activate,
                }
                for rec in recommendations
            ],
            "workflow_prediction": (
                {
                    "name": workflow.workflow_name,
                    "agents": workflow.agents_sequence,
                    "confidence": f"{workflow.confidence * 100:.0f}%",
                    "estimated_time": f"{workflow.estimated_duration // 60}m {workflow.estimated_duration % 60}s",
                }
                if workflow
                else None
            ),
            "context": {
                "files_changed": (
                    len(self.current_context.files_changed)
                    if self.current_context
                    else 0
                ),
                "has_tests": (
                    self.current_context.has_tests if self.current_context else False
                ),
                "has_auth": (
                    self.current_context.has_auth if self.current_context else False
                ),
                "has_api": (
                    self.current_context.has_api if self.current_context else False
                ),
            },
        }
