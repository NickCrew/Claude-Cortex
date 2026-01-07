"""Unit tests for skill_recommender module."""

import json
import sqlite3
from pathlib import Path
from unittest import mock
import pytest
from datetime import datetime

from claude_ctx_py.skill_recommender import SkillRecommender, SkillRecommendation, recommend_skills, get_stats, provide_feedback
from claude_ctx_py.intelligence import SessionContext

# --------------------------------------------------------------------------- fixtures

@pytest.fixture
def mock_home(tmp_path):
    """Create a temporary home directory with necessary structure."""
    home = tmp_path / ".cortex"
    home.mkdir()
    (home / "data").mkdir()
    (home / "skills").mkdir()
    return home

@pytest.fixture
def recommender(mock_home):
    """Create a SkillRecommender instance."""
    with mock.patch("claude_ctx_py.skill_recommender._resolve_claude_dir", return_value=mock_home):
        return SkillRecommender(home=mock_home)

@pytest.fixture
def session_context():
    """Create a sample session context."""
    return SessionContext(
        files_changed=["auth/login.py", "tests/test_login.py"],
        file_types={".py"},
        directories={"auth", "tests"},
        has_tests=True,
        has_auth=True,
        has_api=False,
        has_frontend=False,
        has_backend=True,
        has_database=False,
        errors_count=0,
        test_failures=0,
        build_failures=0,
        session_start=datetime.now(),
        last_activity=datetime.now(),
        active_agents=["security-auditor"],
        active_modes=[],
        active_rules=[],
    )

# --------------------------------------------------------------------------- Initialization & DB

def test_init_creates_database(mock_home):
    """Test that initialization creates the database tables."""
    with mock.patch("claude_ctx_py.skill_recommender._resolve_claude_dir", return_value=mock_home):
        SkillRecommender(home=mock_home)
    
    db_path = mock_home / "data" / "skill-recommendations.db"
    assert db_path.exists()
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        # Check tables exist
        tables = [
            "recommendations_history",
            "recommendation_feedback",
            "context_patterns"
        ]
        for table in tables:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            assert cursor.fetchone() is not None

def test_load_rules_defaults(recommender, mock_home):
    """Test loading default rules when file doesn't exist."""
    assert len(recommender.rules) > 0
    # Should have created the file
    rules_path = mock_home / "skills" / "recommendation-rules.json"
    assert rules_path.exists()
    
    content = json.loads(rules_path.read_text())
    assert "rules" in content
    assert len(content["rules"]) == len(recommender.rules)

def test_load_rules_existing(mock_home):
    """Test loading rules from existing file."""
    rules_path = mock_home / "skills" / "recommendation-rules.json"
    custom_rules = {
        "rules": [
            {
                "trigger": {"file_patterns": ["*.custom"]},
                "recommend": [{"skill": "custom-skill", "confidence": 0.9, "reason": "Custom rule"}]
            }
        ]
    }
    mock_home.mkdir(parents=True, exist_ok=True)
    (mock_home / "skills").mkdir(exist_ok=True)
    rules_path.write_text(json.dumps(custom_rules))
    
    with mock.patch("claude_ctx_py.skill_recommender._resolve_claude_dir", return_value=mock_home):
        rec = SkillRecommender(home=mock_home)
    
    assert len(rec.rules) == 1
    assert rec.rules[0]["recommend"][0]["skill"] == "custom-skill"

# --------------------------------------------------------------------------- Recommendations

def test_recommend_for_context_rule_based(recommender, session_context):
    """Test generating recommendations based on rules (files changed)."""
    # Context has auth/login.py -> should trigger auth/security rules
    recs = recommender.recommend_for_context(session_context)
    
    security_recs = [r for r in recs if r.skill_name in ["owasp-top-10", "secure-coding-practices"]]
    assert len(security_recs) > 0
    assert security_recs[0].confidence >= 0.85

def test_recommend_for_context_agent_based(recommender, session_context):
    """Test generating recommendations based on active agents."""
    # Context has 'security-auditor' active
    recs = recommender.recommend_for_context(session_context)
    
    # AGENT_SKILL_MAP for security-auditor includes 'threat-modeling-techniques'
    threat_rec = next((r for r in recs if r.skill_name == "threat-modeling-techniques"), None)
    assert threat_rec is not None
    assert threat_rec.confidence >= 0.9
    assert "security-auditor" in threat_rec.related_agents

def test_recommend_for_context_pattern_based(recommender, session_context):
    """Test generating recommendations based on historical patterns."""
    # Seed DB with multiple successful patterns to boost confidence
    # Logic requires score/10 >= 0.6, so score >= 6.
    # We insert 7 records with 0.9 success rate = 6.3 score
    # context_hash must be unique
    base_hash = recommender._compute_context_hash(session_context)
    
    with sqlite3.connect(recommender.db_path) as conn:
        for i in range(7):
            unique_hash = f"{base_hash}-{i}"
            conn.execute("""
                INSERT INTO context_patterns (context_hash, successful_skills, success_rate, last_updated)
                VALUES (?, ?, ?, ?)
            """, (unique_hash, json.dumps(["historical-skill"]), 0.9, f"2025-01-0{i+1}"))
    
    recs = recommender.recommend_for_context(session_context)
    historical_rec = next((r for r in recs if r.skill_name == "historical-skill"), None)
    
    assert historical_rec is not None
    assert historical_rec.reason == "Successful in similar projects"

def test_recommend_deduplication_and_boost(recommender, session_context):
    """Test that same skill from multiple sources gets a confidence boost."""
    # 'owasp-top-10' comes from rule (auth files) AND agent (security-auditor)
    recs = recommender.recommend_for_context(session_context)
    
    owasp = next(r for r in recs if r.skill_name == "owasp-top-10")
    # Base confidence is 0.9 (rule) or 0.95 (agent). Boost adds 0.05.
    # Should be close to max but capped at 0.99
    assert owasp.confidence > 0.9 

# --------------------------------------------------------------------------- Recording & Feedback

def test_record_recommendations(recommender, session_context):
    """Test that recommendations are recorded to DB."""
    recs = [
        SkillRecommendation(
            skill_name="test-skill",
            confidence=0.8,
            reason="Test",
            triggers=[],
            related_agents=[],
            estimated_value="high",
            auto_activate=False
        )
    ]
    recommender._record_recommendations(recs, session_context)
    
    with sqlite3.connect(recommender.db_path) as conn:
        cursor = conn.execute("SELECT skill_name, confidence FROM recommendations_history")
        row = cursor.fetchone()
        assert row is not None
        assert row[0] == "test-skill"
        assert row[1] == 0.8

def test_record_activation(recommender, session_context):
    """Test recording skill activation."""
    context_hash = "test-hash"
    # Seed recommendation
    with sqlite3.connect(recommender.db_path) as conn:
        conn.execute("""
            INSERT INTO recommendations_history (timestamp, skill_name, confidence, context_hash, was_activated)
            VALUES (?, ?, ?, ?, ?)
        """, ("2025-01-01", "test-skill", 0.8, context_hash, 0))
    
    recommender.record_activation("test-skill", context_hash)
    
    with sqlite3.connect(recommender.db_path) as conn:
        cursor = conn.execute("SELECT was_activated FROM recommendations_history WHERE skill_name='test-skill'")
        assert cursor.fetchone()[0] == 1

def test_learn_from_feedback(recommender):
    """Test updating feedback for a recommendation."""
    context_hash = "ctx-hash"
    skill = "test-skill"
    
    # Seed recommendation
    with sqlite3.connect(recommender.db_path) as conn:
        conn.execute("""
            INSERT INTO recommendations_history (timestamp, skill_name, confidence, context_hash, was_activated)
            VALUES (?, ?, ?, ?, ?)
        """, (datetime.now().isoformat(), skill, 0.8, context_hash, 1))
        rec_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    
    recommender.learn_from_feedback(skill, True, context_hash, "Great skill!")
    
    with sqlite3.connect(recommender.db_path) as conn:
        # Check history update
        cursor = conn.execute("SELECT was_helpful FROM recommendations_history WHERE id=?", (rec_id,))
        assert cursor.fetchone()[0] == 1
        
        # Check feedback table
        cursor = conn.execute("SELECT comment FROM recommendation_feedback WHERE recommendation_id=?", (rec_id,))
        assert cursor.fetchone()[0] == "Great skill!"

def test_record_feedback_cli(recommender):
    """Test recording standalone feedback from CLI."""
    skill = "cli-skill"
    recommender.record_feedback(skill, False, "Not useful")
    
    with sqlite3.connect(recommender.db_path) as conn:
        # Should create a new history entry if none existed
        cursor = conn.execute("SELECT was_helpful, reason FROM recommendations_history WHERE skill_name=?", (skill,))
        row = cursor.fetchone()
        assert row[0] == 0
        assert row[1] == "Not useful"
        
        # Should add to feedback table (with NULL rec_id if direct insert logic used in code)
        # Wait, code does: INSERT INTO recommendation_feedback (recommendation_id, ... VALUES (NULL, ...)
        cursor = conn.execute("SELECT comment, helpful FROM recommendation_feedback WHERE comment='Not useful'")
        row = cursor.fetchone()
        assert row[0] == "Not useful"
        assert row[1] == 0

# --------------------------------------------------------------------------- Stats

def test_get_recommendation_stats(recommender):
    """Test retrieving stats."""
    with sqlite3.connect(recommender.db_path) as conn:
        conn.execute("""
            INSERT INTO recommendations_history (timestamp, skill_name, confidence, context_hash, was_activated, was_helpful)
            VALUES (?, ?, ?, ?, ?, ?)
        """, ("2025-01-01", "skill-a", 0.9, "h1", 1, 1))
        conn.execute("""
            INSERT INTO recommendations_history (timestamp, skill_name, confidence, context_hash, was_activated, was_helpful)
            VALUES (?, ?, ?, ?, ?, ?)
        """, ("2025-01-02", "skill-a", 0.8, "h2", 0, 0))
    
    # Specific skill stats
    stats_a = recommender.get_recommendation_stats("skill-a")
    assert stats_a["total_recommendations"] == 2
    assert stats_a["activations"] == 1
    assert stats_a["helpful_count"] == 1
    assert stats_a["activation_rate"] == 50.0
    
    # Global stats
    global_stats = recommender.get_recommendation_stats()
    assert global_stats["total_recommendations"] == 2
    assert global_stats["total_activations"] == 1

# --------------------------------------------------------------------------- Helper functions

def test_helper_recommend_skills(mock_home, session_context):
    """Test helper wrapper function."""
    with mock.patch("claude_ctx_py.skill_recommender._resolve_claude_dir", return_value=mock_home):
        recs = recommend_skills(session_context, home=mock_home)
        assert isinstance(recs, list)

def test_helper_provide_feedback(mock_home):
    """Test helper wrapper function for feedback."""
    with mock.patch("claude_ctx_py.skill_recommender._resolve_claude_dir", return_value=mock_home):
        # Just ensure it runs without error
        provide_feedback("skill", True, "hash", home=mock_home)

def test_helper_get_stats(mock_home):
    """Test helper wrapper function for stats."""
    with mock.patch("claude_ctx_py.skill_recommender._resolve_claude_dir", return_value=mock_home):
        stats = get_stats(home=mock_home)
        assert isinstance(stats, dict)
