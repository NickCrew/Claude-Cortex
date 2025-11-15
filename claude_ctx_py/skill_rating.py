"""Skill Rating & Feedback System.

Community-driven quality signals for skills through star ratings, reviews,
and success correlation tracking.
"""

from __future__ import annotations

import hashlib
import sqlite3
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
from collections import defaultdict

from .core.base import _resolve_claude_dir


@dataclass
class SkillRating:
    """User rating for a skill."""

    skill_name: str
    user_hash: str  # Anonymous user identifier
    stars: int  # 1-5
    timestamp: datetime
    project_type: str  # e.g., "python-fastapi"
    review: Optional[str]
    was_helpful: bool
    task_succeeded: bool  # Did the task using this skill succeed?

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data


@dataclass
class SkillQualityMetrics:
    """Automated quality metrics for a skill."""

    skill_name: str
    avg_rating: float  # Average star rating
    total_ratings: int
    helpful_percentage: float  # % of "helpful" votes
    success_correlation: float  # % tasks succeeded with this skill
    token_efficiency: Optional[float]  # Avg tokens saved (if tracked)
    usage_count: int  # Times activated
    last_updated: datetime

    # Rating distribution
    stars_5: int = 0
    stars_4: int = 0
    stars_3: int = 0
    stars_2: int = 0
    stars_1: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        data["last_updated"] = self.last_updated.isoformat()
        return data

    def star_display(self) -> str:
        """Return star rating as visual string (e.g., '⭐⭐⭐⭐⭐ 4.8/5.0')."""
        full_stars = int(self.avg_rating)
        half_star = (self.avg_rating - full_stars) >= 0.5
        stars = "⭐" * full_stars
        if half_star:
            stars += "½"
        return f"{stars} {self.avg_rating:.1f}/5.0"


class SkillRatingCollector:
    """Collect and aggregate skill ratings."""

    def __init__(self, home: Path | None = None):
        """Initialize rating collector with optional home directory."""
        self.home = _resolve_claude_dir(home)
        self.db_path = self.home / "data" / "skill-ratings.db"
        self._init_database()

    def _init_database(self) -> None:
        """Initialize SQLite database for ratings."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS skill_ratings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    skill_name TEXT NOT NULL,
                    user_hash TEXT NOT NULL,
                    stars INTEGER NOT NULL CHECK(stars >= 1 AND stars <= 5),
                    timestamp TEXT NOT NULL,
                    project_type TEXT,
                    review TEXT,
                    was_helpful BOOLEAN NOT NULL,
                    task_succeeded BOOLEAN NOT NULL
                )
            """)

            # Index for fast lookups by skill
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_skill_ratings_skill
                ON skill_ratings(skill_name)
            """)

            # Index for user rating history
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_skill_ratings_user
                ON skill_ratings(user_hash, skill_name)
            """)

            # Aggregated metrics cache table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS skill_quality_metrics (
                    skill_name TEXT PRIMARY KEY,
                    avg_rating REAL NOT NULL,
                    total_ratings INTEGER NOT NULL,
                    helpful_percentage REAL NOT NULL,
                    success_correlation REAL NOT NULL,
                    token_efficiency REAL,
                    usage_count INTEGER NOT NULL DEFAULT 0,
                    last_updated TEXT NOT NULL,
                    stars_5 INTEGER NOT NULL DEFAULT 0,
                    stars_4 INTEGER NOT NULL DEFAULT 0,
                    stars_3 INTEGER NOT NULL DEFAULT 0,
                    stars_2 INTEGER NOT NULL DEFAULT 0,
                    stars_1 INTEGER NOT NULL DEFAULT 0
                )
            """)

            # Skill usage tracking (for success correlation)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS skill_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    skill_name TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    succeeded BOOLEAN NOT NULL,
                    duration_minutes REAL,
                    tokens_saved REAL
                )
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_skill_usage_skill
                ON skill_usage(skill_name)
            """)

            conn.commit()

    def _get_user_hash(self) -> str:
        """Generate anonymous user hash."""
        # Use machine ID + username for consistent anonymous ID
        import getpass
        import platform

        user_id = f"{platform.node()}-{getpass.getuser()}"
        return hashlib.sha256(user_id.encode()).hexdigest()[:16]

    def record_rating(
        self,
        skill: str,
        stars: int,
        helpful: bool,
        task_succeeded: bool,
        review: Optional[str] = None,
        project_type: Optional[str] = None,
    ) -> SkillRating:
        """
        Record user rating for a skill.

        Args:
            skill: Skill name
            stars: 1-5 star rating
            helpful: Was the skill helpful?
            task_succeeded: Did the task succeed?
            review: Optional written review
            project_type: Optional project type (e.g., "python-fastapi")

        Returns:
            SkillRating object
        """
        if not 1 <= stars <= 5:
            raise ValueError(f"Stars must be 1-5, got {stars}")

        user_hash = self._get_user_hash()
        timestamp = datetime.now(timezone.utc)

        rating = SkillRating(
            skill_name=skill,
            user_hash=user_hash,
            stars=stars,
            timestamp=timestamp,
            project_type=project_type or "unknown",
            review=review,
            was_helpful=helpful,
            task_succeeded=task_succeeded,
        )

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO skill_ratings
                (skill_name, user_hash, stars, timestamp, project_type,
                 review, was_helpful, task_succeeded)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    rating.skill_name,
                    rating.user_hash,
                    rating.stars,
                    rating.timestamp.isoformat(),
                    rating.project_type,
                    rating.review,
                    rating.was_helpful,
                    rating.task_succeeded,
                ),
            )
            conn.commit()

        # Update aggregated metrics
        self._update_metrics(skill)

        return rating

    def record_usage(
        self,
        skill: str,
        succeeded: bool,
        duration_minutes: Optional[float] = None,
        tokens_saved: Optional[float] = None,
    ) -> None:
        """
        Record skill usage for success correlation tracking.

        Args:
            skill: Skill name
            succeeded: Did the task succeed?
            duration_minutes: Optional task duration
            tokens_saved: Optional tokens saved by using skill
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO skill_usage
                (skill_name, timestamp, succeeded, duration_minutes, tokens_saved)
                VALUES (?, ?, ?, ?, ?)
            """,
                (
                    skill,
                    datetime.now(timezone.utc).isoformat(),
                    succeeded,
                    duration_minutes,
                    tokens_saved,
                ),
            )
            conn.commit()

        # Update metrics to reflect new usage
        self._update_metrics(skill)

    def get_skill_score(self, skill: str) -> Optional[SkillQualityMetrics]:
        """
        Get aggregated quality metrics for a skill.

        Returns None if skill has no ratings.
        """
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                """
                SELECT avg_rating, total_ratings, helpful_percentage,
                       success_correlation, token_efficiency, usage_count,
                       last_updated, stars_5, stars_4, stars_3, stars_2, stars_1
                FROM skill_quality_metrics
                WHERE skill_name = ?
            """,
                (skill,),
            ).fetchone()

            if not row:
                return None

            return SkillQualityMetrics(
                skill_name=skill,
                avg_rating=row[0],
                total_ratings=row[1],
                helpful_percentage=row[2],
                success_correlation=row[3],
                token_efficiency=row[4],
                usage_count=row[5],
                last_updated=datetime.fromisoformat(row[6]),
                stars_5=row[7],
                stars_4=row[8],
                stars_3=row[9],
                stars_2=row[10],
                stars_1=row[11],
            )

    def get_top_rated(
        self, category: Optional[str] = None, limit: int = 10
    ) -> List[Tuple[str, SkillQualityMetrics]]:
        """
        Get top-rated skills.

        Args:
            category: Optional category filter (not implemented yet)
            limit: Maximum number of results

        Returns:
            List of (skill_name, metrics) tuples sorted by rating
        """
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                """
                SELECT skill_name, avg_rating, total_ratings, helpful_percentage,
                       success_correlation, token_efficiency, usage_count,
                       last_updated, stars_5, stars_4, stars_3, stars_2, stars_1
                FROM skill_quality_metrics
                WHERE total_ratings >= 3
                ORDER BY avg_rating DESC, total_ratings DESC
                LIMIT ?
            """,
                (limit,),
            ).fetchall()

            results = []
            for row in rows:
                metrics = SkillQualityMetrics(
                    skill_name=row[0],
                    avg_rating=row[1],
                    total_ratings=row[2],
                    helpful_percentage=row[3],
                    success_correlation=row[4],
                    token_efficiency=row[5],
                    usage_count=row[6],
                    last_updated=datetime.fromisoformat(row[7]),
                    stars_5=row[8],
                    stars_4=row[9],
                    stars_3=row[10],
                    stars_2=row[11],
                    stars_1=row[12],
                )
                results.append((row[0], metrics))

            return results

    def get_recent_reviews(
        self, skill: str, limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get recent reviews for a skill.

        Returns:
            List of review dictionaries with stars, review text, and timestamp
        """
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                """
                SELECT stars, review, timestamp, was_helpful
                FROM skill_ratings
                WHERE skill_name = ? AND review IS NOT NULL
                ORDER BY timestamp DESC
                LIMIT ?
            """,
                (skill, limit),
            ).fetchall()

            reviews = []
            for row in rows:
                # Calculate relative time
                ts = datetime.fromisoformat(row[2])
                now = datetime.now(timezone.utc)
                delta = now - ts
                if delta.days > 0:
                    time_ago = f"{delta.days} day{'s' if delta.days > 1 else ''} ago"
                elif delta.seconds >= 3600:
                    hours = delta.seconds // 3600
                    time_ago = f"{hours} hour{'s' if hours > 1 else ''} ago"
                else:
                    minutes = delta.seconds // 60
                    time_ago = f"{minutes} minute{'s' if minutes > 1 else ''} ago"

                reviews.append(
                    {
                        "stars": row[0],
                        "review": row[1],
                        "timestamp": ts.isoformat(),
                        "time_ago": time_ago,
                        "was_helpful": row[3],
                    }
                )

            return reviews

    def _update_metrics(self, skill: str) -> None:
        """Update aggregated metrics for a skill."""
        with sqlite3.connect(self.db_path) as conn:
            # Calculate rating stats
            rating_stats = conn.execute(
                """
                SELECT
                    COUNT(*) as total,
                    AVG(stars) as avg_stars,
                    SUM(CASE WHEN was_helpful = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as helpful_pct,
                    SUM(CASE WHEN stars = 5 THEN 1 ELSE 0 END) as stars_5,
                    SUM(CASE WHEN stars = 4 THEN 1 ELSE 0 END) as stars_4,
                    SUM(CASE WHEN stars = 3 THEN 1 ELSE 0 END) as stars_3,
                    SUM(CASE WHEN stars = 2 THEN 1 ELSE 0 END) as stars_2,
                    SUM(CASE WHEN stars = 1 THEN 1 ELSE 0 END) as stars_1
                FROM skill_ratings
                WHERE skill_name = ?
            """,
                (skill,),
            ).fetchone()

            # Calculate usage stats
            usage_stats = conn.execute(
                """
                SELECT
                    COUNT(*) as total_usage,
                    SUM(CASE WHEN succeeded = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as success_pct,
                    AVG(tokens_saved) as avg_tokens_saved
                FROM skill_usage
                WHERE skill_name = ?
            """,
                (skill,),
            ).fetchone()

            total_ratings = rating_stats[0]
            if total_ratings == 0:
                return  # No ratings yet

            avg_rating = rating_stats[1] or 0.0
            helpful_pct = rating_stats[2] or 0.0
            usage_count = usage_stats[0] or 0
            success_pct = usage_stats[1] or 0.0
            token_efficiency = usage_stats[2]

            # Upsert metrics
            conn.execute(
                """
                INSERT OR REPLACE INTO skill_quality_metrics
                (skill_name, avg_rating, total_ratings, helpful_percentage,
                 success_correlation, token_efficiency, usage_count, last_updated,
                 stars_5, stars_4, stars_3, stars_2, stars_1)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    skill,
                    avg_rating,
                    total_ratings,
                    helpful_pct,
                    success_pct,
                    token_efficiency,
                    usage_count,
                    datetime.now(timezone.utc).isoformat(),
                    rating_stats[3],
                    rating_stats[4],
                    rating_stats[5],
                    rating_stats[6],
                    rating_stats[7],
                ),
            )
            conn.commit()

    def has_user_rated(self, skill: str) -> bool:
        """Check if current user has already rated this skill."""
        user_hash = self._get_user_hash()
        with sqlite3.connect(self.db_path) as conn:
            result = conn.execute(
                """
                SELECT COUNT(*) FROM skill_ratings
                WHERE skill_name = ? AND user_hash = ?
            """,
                (skill, user_hash),
            ).fetchone()
            count: int = result[0] if result else 0
            return count > 0

    def get_user_rating(self, skill: str) -> Optional[SkillRating]:
        """Get current user's rating for a skill, if exists."""
        user_hash = self._get_user_hash()
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                """
                SELECT skill_name, user_hash, stars, timestamp, project_type,
                       review, was_helpful, task_succeeded
                FROM skill_ratings
                WHERE skill_name = ? AND user_hash = ?
                ORDER BY timestamp DESC
                LIMIT 1
            """,
                (skill, user_hash),
            ).fetchone()

            if not row:
                return None

            return SkillRating(
                skill_name=row[0],
                user_hash=row[1],
                stars=row[2],
                timestamp=datetime.fromisoformat(row[3]),
                project_type=row[4],
                review=row[5],
                was_helpful=row[6],
                task_succeeded=row[7],
            )

    def export_ratings(self, skill: Optional[str] = None) -> Dict[str, Any]:
        """
        Export ratings data for analysis or sharing.

        Args:
            skill: Optional skill name to filter by

        Returns:
            Dictionary with ratings and metrics
        """
        with sqlite3.connect(self.db_path) as conn:
            if skill:
                ratings = conn.execute(
                    """
                    SELECT skill_name, stars, timestamp, project_type,
                           review, was_helpful, task_succeeded
                    FROM skill_ratings
                    WHERE skill_name = ?
                    ORDER BY timestamp DESC
                """,
                    (skill,),
                ).fetchall()
            else:
                ratings = conn.execute(
                    """
                    SELECT skill_name, stars, timestamp, project_type,
                           review, was_helpful, task_succeeded
                    FROM skill_ratings
                    ORDER BY timestamp DESC
                """
                ).fetchall()

            rating_data = []
            for row in ratings:
                rating_data.append(
                    {
                        "skill_name": row[0],
                        "stars": row[1],
                        "timestamp": row[2],
                        "project_type": row[3],
                        "review": row[4],
                        "was_helpful": row[5],
                        "task_succeeded": row[6],
                    }
                )

            # Get all metrics
            if skill:
                metrics_rows = conn.execute(
                    """
                    SELECT skill_name, avg_rating, total_ratings, helpful_percentage,
                           success_correlation, token_efficiency, usage_count, last_updated
                    FROM skill_quality_metrics
                    WHERE skill_name = ?
                """,
                    (skill,),
                ).fetchall()
            else:
                metrics_rows = conn.execute(
                    """
                    SELECT skill_name, avg_rating, total_ratings, helpful_percentage,
                           success_correlation, token_efficiency, usage_count, last_updated
                    FROM skill_quality_metrics
                    ORDER BY avg_rating DESC
                """
                ).fetchall()

            metrics_data = []
            for row in metrics_rows:
                metrics_data.append(
                    {
                        "skill_name": row[0],
                        "avg_rating": row[1],
                        "total_ratings": row[2],
                        "helpful_percentage": row[3],
                        "success_correlation": row[4],
                        "token_efficiency": row[5],
                        "usage_count": row[6],
                        "last_updated": row[7],
                    }
                )

            return {
                "export_date": datetime.now(timezone.utc).isoformat(),
                "ratings": rating_data,
                "metrics": metrics_data,
                "total_ratings": len(rating_data),
                "total_skills": len(set(r["skill_name"] for r in rating_data)),
            }
