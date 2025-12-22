"""AI-Powered Skill Recommendation System.

Intelligent skill recommendations based on context analysis, historical patterns,
and agent activation triggers.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Set, Tuple, Any
from collections import Counter, defaultdict

from .intelligence import SessionContext, PatternLearner
from .core.base import _resolve_claude_dir


@dataclass
class SkillRecommendation:
    """Intelligent skill recommendation."""

    skill_name: str
    confidence: float  # 0.0-1.0
    reason: str
    triggers: List[str]
    related_agents: List[str]
    estimated_value: str  # "high", "medium", "low"
    auto_activate: bool  # Activate if confidence >= 0.8

    def should_notify(self) -> bool:
        """Determine if this recommendation should notify the user."""
        return self.confidence >= 0.7

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)


# Agent → Skills mapping (based on domain expertise)
AGENT_SKILL_MAP: Dict[str, List[Tuple[str, float]]] = {
    "security-auditor": [
        ("owasp-top-10", 0.95),
        ("threat-modeling-techniques", 0.9),
        ("secure-coding-practices", 0.85),
        ("security-testing-patterns", 0.8),
    ],
    "kubernetes-architect": [
        ("kubernetes-deployment-patterns", 0.95),
        ("helm-chart-patterns", 0.9),
        ("kubernetes-security-policies", 0.85),
        ("gitops-workflows", 0.8),
    ],
    "python-pro": [
        ("python-testing-patterns", 0.9),
        ("async-python-patterns", 0.85),
        ("python-performance-optimization", 0.8),
    ],
    "typescript-pro": [
        ("typescript-advanced-patterns", 0.9),
        ("react-performance-optimization", 0.85),
    ],
    "terraform-specialist": [
        ("terraform-best-practices", 0.95),
        ("cloud-architect-patterns", 0.8),
    ],
    "cloud-architect": [
        ("cloud-design-patterns", 0.9),
        ("terraform-best-practices", 0.85),
        ("kubernetes-deployment-patterns", 0.8),
    ],
    "code-reviewer": [
        ("code-quality-patterns", 0.85),
        ("testing-anti-patterns", 0.8),
    ],
    "debugger": [
        ("systematic-debugging", 0.9),
        ("root-cause-tracing", 0.85),
    ],
}


class SkillRecommender:
    """AI-powered skill recommendation engine."""

    def __init__(self, home: Path | None = None):
        """Initialize recommender with optional home directory."""
        self.home = _resolve_claude_dir(home)
        self.db_path = self.home / "data" / "skill-recommendations.db"
        self.rules_path = self.home / "skills" / "recommendation-rules.json"
        self._init_database()
        self._load_rules()

    def _init_database(self) -> None:
        """Initialize SQLite database for recommendations and feedback."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS recommendations_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    skill_name TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    context_hash TEXT NOT NULL,
                    was_activated BOOLEAN DEFAULT 0,
                    was_helpful BOOLEAN NULL,
                    reason TEXT
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS recommendation_feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    recommendation_id INTEGER,
                    timestamp TEXT NOT NULL,
                    helpful BOOLEAN NOT NULL,
                    comment TEXT,
                    FOREIGN KEY (recommendation_id) REFERENCES recommendations_history(id)
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS context_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    context_hash TEXT UNIQUE NOT NULL,
                    file_patterns TEXT,  -- JSON array
                    active_agents TEXT,  -- JSON array
                    successful_skills TEXT,  -- JSON array
                    success_rate REAL,
                    last_updated TEXT
                )
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_recommendations_skill
                ON recommendations_history(skill_name)
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_recommendations_context
                ON recommendations_history(context_hash)
            """)

            conn.commit()

    def _load_rules(self) -> None:
        """Load recommendation rules from configuration file."""
        self.rules: List[Dict[str, Any]] = []

        if self.rules_path.exists():
            try:
                rules_data = json.loads(self.rules_path.read_text(encoding="utf-8"))
                self.rules = rules_data.get("rules", [])
            except (json.JSONDecodeError, Exception):
                # If rules file doesn't exist or is invalid, use defaults
                self.rules = self._get_default_rules()
                self._save_rules()
        else:
            self.rules = self._get_default_rules()
            self._save_rules()

    def _get_default_rules(self) -> List[Dict[str, Any]]:
        """Get default recommendation rules."""
        return [
            {
                "trigger": {
                    "file_patterns": ["**/auth/**/*.py", "**/security/**"]
                },
                "recommend": [
                    {
                        "skill": "owasp-top-10",
                        "confidence": 0.9,
                        "reason": "Auth code detected, security review recommended"
                    },
                    {
                        "skill": "secure-coding-practices",
                        "confidence": 0.85,
                        "reason": "Security-critical files modified"
                    }
                ]
            },
            {
                "trigger": {
                    "file_patterns": ["**/*.test.py", "**/*.spec.ts", "**/tests/**"]
                },
                "recommend": [
                    {
                        "skill": "testing-anti-patterns",
                        "confidence": 0.85,
                        "reason": "Test files detected, avoid common pitfalls"
                    },
                    {
                        "skill": "test-driven-development",
                        "confidence": 0.8,
                        "reason": "Testing activity detected"
                    }
                ]
            },
            {
                "trigger": {
                    "file_patterns": ["**/*.tf", "**/terraform/**"]
                },
                "recommend": [
                    {
                        "skill": "terraform-best-practices",
                        "confidence": 0.95,
                        "reason": "Terraform files detected"
                    }
                ]
            },
            {
                "trigger": {
                    "file_patterns": ["**/k8s/**", "**/kubernetes/**", "**/*.yaml"]
                },
                "recommend": [
                    {
                        "skill": "kubernetes-deployment-patterns",
                        "confidence": 0.9,
                        "reason": "Kubernetes configuration detected"
                    },
                    {
                        "skill": "kubernetes-security-policies",
                        "confidence": 0.85,
                        "reason": "K8s security review recommended"
                    }
                ]
            }
        ]

    def _save_rules(self) -> None:
        """Save recommendation rules to configuration file."""
        self.rules_path.parent.mkdir(parents=True, exist_ok=True)
        rules_data = {"rules": self.rules}
        self.rules_path.write_text(json.dumps(rules_data, indent=2), encoding="utf-8")

    def recommend_for_context(
        self,
        context: SessionContext
    ) -> List[SkillRecommendation]:
        """
        Generate skill recommendations based on current context.

        Uses multiple strategies:
        1. Rule-based (file patterns → skills)
        2. Pattern-based (historical success)
        3. Agent-based (active agents → skills)
        4. Collaborative (similar projects)

        Args:
            context: Current session context

        Returns:
            List of skill recommendations, sorted by confidence (high to low)
        """
        recommendations: Dict[str, SkillRecommendation] = {}

        # Strategy 1: Rule-based recommendations
        rule_recs = self._rule_based_recommendations(context)
        for rec in rule_recs:
            recommendations[rec.skill_name] = rec

        # Strategy 2: Agent-based recommendations
        agent_recs = self._agent_based_recommendations(context)
        for rec in agent_recs:
            if rec.skill_name in recommendations:
                # Boost confidence if multiple strategies recommend same skill
                existing = recommendations[rec.skill_name]
                existing.confidence = min(0.99, existing.confidence + 0.05)
                existing.related_agents.extend(rec.related_agents)
                existing.triggers.extend(rec.triggers)
            else:
                recommendations[rec.skill_name] = rec

        # Strategy 3: Pattern-based recommendations (from history)
        pattern_recs = self._pattern_based_recommendations(context)
        for rec in pattern_recs:
            if rec.skill_name in recommendations:
                existing = recommendations[rec.skill_name]
                existing.confidence = min(0.99, existing.confidence + 0.03)
            else:
                recommendations[rec.skill_name] = rec

        # Sort by confidence (highest first)
        sorted_recs = sorted(
            recommendations.values(),
            key=lambda r: r.confidence,
            reverse=True
        )

        # Record recommendations to history
        self._record_recommendations(sorted_recs, context)

        return sorted_recs

    def _rule_based_recommendations(
        self,
        context: SessionContext
    ) -> List[SkillRecommendation]:
        """Generate recommendations based on predefined rules."""
        recommendations: List[SkillRecommendation] = []

        for rule in self.rules:
            trigger = rule.get("trigger", {})

            # Check file pattern triggers
            file_patterns = trigger.get("file_patterns", [])
            if file_patterns:
                # Match file patterns against changed files
                matched = any(
                    self._match_pattern(pattern, file_path)
                    for pattern in file_patterns
                    for file_path in context.files_changed
                )

                if matched:
                    for rec_data in rule.get("recommend", []):
                        rec = SkillRecommendation(
                            skill_name=rec_data["skill"],
                            confidence=rec_data["confidence"],
                            reason=rec_data["reason"],
                            triggers=file_patterns,
                            related_agents=[],
                            estimated_value=self._estimate_value(rec_data["confidence"]),
                            auto_activate=rec_data["confidence"] >= 0.8
                        )
                        recommendations.append(rec)

        return recommendations

    def _agent_based_recommendations(
        self,
        context: SessionContext
    ) -> List[SkillRecommendation]:
        """Generate recommendations based on active agents."""
        recommendations: List[SkillRecommendation] = []

        for agent_name in context.active_agents:
            if agent_name in AGENT_SKILL_MAP:
                for skill_name, confidence in AGENT_SKILL_MAP[agent_name]:
                    rec = SkillRecommendation(
                        skill_name=skill_name,
                        confidence=confidence,
                        reason=f"Recommended for {agent_name}",
                        triggers=[f"agent:{agent_name}"],
                        related_agents=[agent_name],
                        estimated_value=self._estimate_value(confidence),
                        auto_activate=confidence >= 0.8
                    )
                    recommendations.append(rec)

        return recommendations

    def _pattern_based_recommendations(
        self,
        context: SessionContext
    ) -> List[SkillRecommendation]:
        """Generate recommendations based on historical success patterns."""
        recommendations: List[SkillRecommendation] = []

        # Compute context hash for similarity matching
        context_hash = self._compute_context_hash(context)

        # Find similar contexts from history
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT successful_skills, success_rate
                FROM context_patterns
                WHERE success_rate > 0.7
                ORDER BY last_updated DESC
                LIMIT 10
            """)

            skill_scores: Counter[str] = Counter()
            for row in cursor.fetchall():
                try:
                    skills = json.loads(row[0])
                    success_rate = row[1]
                    for skill in skills:
                        skill_scores[skill] += success_rate
                except (json.JSONDecodeError, Exception):
                    continue

        # Create recommendations from top scoring skills
        for skill_name, score in skill_scores.most_common(5):
            confidence = min(0.8, score / 10)  # Normalize to 0-0.8 range
            if confidence >= 0.6:  # Only recommend if reasonably confident
                rec = SkillRecommendation(
                    skill_name=skill_name,
                    confidence=confidence,
                    reason="Successful in similar projects",
                    triggers=["historical_pattern"],
                    related_agents=[],
                    estimated_value=self._estimate_value(confidence),
                    auto_activate=False  # Never auto-activate pattern-based
                )
                recommendations.append(rec)

        return recommendations

    def _match_pattern(self, pattern: str, file_path: str) -> bool:
        """Match a glob pattern against a file path."""
        from fnmatch import fnmatch
        return fnmatch(file_path, pattern)

    def _estimate_value(self, confidence: float) -> str:
        """Estimate value based on confidence score."""
        if confidence >= 0.85:
            return "high"
        elif confidence >= 0.70:
            return "medium"
        else:
            return "low"

    def _compute_context_hash(self, context: SessionContext) -> str:
        """Compute hash of context for similarity matching."""
        # Create a stable representation of context
        context_str = json.dumps({
            "file_types": sorted(context.file_types),
            "has_auth": context.has_auth,
            "has_api": context.has_api,
            "has_frontend": context.has_frontend,
            "has_backend": context.has_backend,
            "active_agents": sorted(context.active_agents),
        }, sort_keys=True)

        return hashlib.md5(context_str.encode()).hexdigest()

    def _record_recommendations(
        self,
        recommendations: List[SkillRecommendation],
        context: SessionContext
    ) -> None:
        """Record recommendations to history database."""
        context_hash = self._compute_context_hash(context)
        timestamp = datetime.now().isoformat()

        with sqlite3.connect(self.db_path) as conn:
            for rec in recommendations:
                conn.execute("""
                    INSERT INTO recommendations_history
                    (timestamp, skill_name, confidence, context_hash, reason)
                    VALUES (?, ?, ?, ?, ?)
                """, (timestamp, rec.skill_name, rec.confidence, context_hash, rec.reason))

            conn.commit()

    def record_activation(self, skill_name: str, context_hash: str) -> None:
        """Record that a recommended skill was activated."""
        with sqlite3.connect(self.db_path) as conn:
            # Find the most recent recommendation ID
            cursor = conn.execute("""
                SELECT id FROM recommendations_history
                WHERE skill_name = ? AND context_hash = ?
                ORDER BY timestamp DESC
                LIMIT 1
            """, (skill_name, context_hash))
            
            row = cursor.fetchone()
            if row:
                rec_id = row[0]
                conn.execute("""
                    UPDATE recommendations_history
                    SET was_activated = 1
                    WHERE id = ?
                """, (rec_id,))
                conn.commit()

    def learn_from_feedback(
        self,
        skill: str,
        was_helpful: bool,
        context_hash: str,
        comment: Optional[str] = None
    ) -> None:
        """Update recommendation model based on user feedback."""
        timestamp = datetime.now().isoformat()

        with sqlite3.connect(self.db_path) as conn:
            # Find the recommendation to update
            cursor = conn.execute("""
                SELECT id FROM recommendations_history
                WHERE skill_name = ? AND context_hash = ?
                ORDER BY timestamp DESC
                LIMIT 1
            """, (skill, context_hash))

            row = cursor.fetchone()
            if row:
                rec_id = row[0]

                # Update recommendation
                conn.execute("""
                    UPDATE recommendations_history
                    SET was_helpful = ?
                    WHERE id = ?
                """, (was_helpful, rec_id))

                # Insert feedback
                conn.execute("""
                    INSERT INTO recommendation_feedback
                    (recommendation_id, timestamp, helpful, comment)
                    VALUES (?, ?, ?, ?)
                """, (rec_id, timestamp, was_helpful, comment))

                conn.commit()

    def get_recommendation_stats(
        self,
        skill_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get statistics about recommendations and their effectiveness."""
        with sqlite3.connect(self.db_path) as conn:
            if skill_name:
                # Stats for specific skill
                cursor = conn.execute("""
                    SELECT
                        COUNT(*) as total_recommendations,
                        COALESCE(SUM(CASE WHEN was_activated THEN 1 ELSE 0 END), 0) as activations,
                        COALESCE(SUM(CASE WHEN was_helpful THEN 1 ELSE 0 END), 0) as helpful,
                        AVG(confidence) as avg_confidence
                    FROM recommendations_history
                    WHERE skill_name = ?
                """, (skill_name,))

                row = cursor.fetchone()
                # Row values will be 0 instead of None due to COALESCE or count behavior
                total = row[0]
                activations = row[1]
                helpful = row[2]
                
                stats = {
                    "skill_name": skill_name,
                    "total_recommendations": total,
                    "activations": activations,
                    "helpful_count": helpful,
                    "avg_confidence": round(row[3], 2) if row[3] else 0,
                    "activation_rate": round((activations / total) * 100, 1) if total > 0 else 0,
                    "helpful_rate": round((helpful / activations) * 100, 1) if activations > 0 else 0
                }
            else:
                # Overall stats
                cursor = conn.execute("""
                    SELECT
                        COUNT(*) as total,
                        COALESCE(SUM(CASE WHEN was_activated THEN 1 ELSE 0 END), 0) as activated,
                        COALESCE(SUM(CASE WHEN was_helpful THEN 1 ELSE 0 END), 0) as helpful
                    FROM recommendations_history
                """)

                row = cursor.fetchone()
                total = row[0]
                activated = row[1]
                helpful = row[2]
                
                stats = {
                    "total_recommendations": total,
                    "total_activations": activated,
                    "total_helpful": helpful,
                    "activation_rate": round((activated / total) * 100, 1) if total > 0 else 0,
                    "helpful_rate": round((helpful / activated) * 100, 1) if activated > 0 else 0
                }

        return stats

    def record_feedback(
        self,
        skill_name: str,
        helpful: bool,
        comment: str = ""
    ) -> None:
        """Record user feedback on a skill (standalone, without context hash).

        For CLI usage where we don't have access to the full context hash.

        Args:
            skill_name: Name of the skill
            helpful: Whether the skill was helpful
            comment: Optional user comment
        """
        timestamp = datetime.now().isoformat()

        with sqlite3.connect(self.db_path) as conn:
            # Record feedback directly in feedback table
            conn.execute("""
                INSERT INTO recommendation_feedback (recommendation_id, timestamp, helpful, comment)
                VALUES (NULL, ?, ?, ?)
            """, (timestamp, helpful, comment))

            # Update pattern learning for this skill
            # Use a generic context hash for CLI feedback
            context_hash = hashlib.md5(f"cli-feedback-{skill_name}".encode()).hexdigest()

            # Check if we have a recent recommendation for this skill
            cursor = conn.execute("""
                SELECT id FROM recommendations_history
                WHERE skill_name = ?
                ORDER BY timestamp DESC
                LIMIT 1
            """, (skill_name,))

            row = cursor.fetchone()
            if row:
                # Update existing recommendation
                conn.execute("""
                    UPDATE recommendations_history
                    SET was_helpful = ?
                    WHERE id = ?
                """, (helpful, row[0]))
            else:
                # Create a new entry for this feedback
                conn.execute("""
                    INSERT INTO recommendations_history
                    (timestamp, skill_name, confidence, context_hash, was_activated, was_helpful, reason)
                    VALUES (?, ?, 0.0, ?, 0, ?, ?)
                """, (timestamp, skill_name, context_hash, helpful, comment))

            conn.commit()


# Helper functions for CLI integration

def recommend_skills(context: SessionContext, home: Path | None = None) -> List[SkillRecommendation]:
    """Generate skill recommendations for current context."""
    recommender = SkillRecommender(home)
    return recommender.recommend_for_context(context)


def provide_feedback(
    skill: str,
    helpful: bool,
    context_hash: str,
    comment: Optional[str] = None,
    home: Path | None = None
) -> None:
    """Provide feedback on a skill recommendation."""
    recommender = SkillRecommender(home)
    recommender.learn_from_feedback(skill, helpful, context_hash, comment)


def get_stats(skill_name: Optional[str] = None, home: Path | None = None) -> Dict[str, Any]:
    """Get recommendation statistics."""
    recommender = SkillRecommender(home)
    return recommender.get_recommendation_stats(skill_name)
