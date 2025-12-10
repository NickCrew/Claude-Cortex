"""Tests for semantic intelligence module.

These tests verify the semantic matching functionality, including:
- Session-to-text conversion
- Embedding generation (if FastEmbed available)
- Similarity matching
- Graceful degradation when FastEmbed is unavailable
"""

import json
import tempfile
from pathlib import Path

import pytest

try:
    import numpy as np
    from claude_ctx_py.intelligence.semantic import SemanticMatcher
    SEMANTIC_AVAILABLE = True
except ImportError:
    SEMANTIC_AVAILABLE = False


@pytest.mark.skipif(not SEMANTIC_AVAILABLE, reason="FastEmbed not installed")
class TestSemanticMatcher:
    """Tests for SemanticMatcher class."""

    def test_initialization(self, tmp_path):
        """Test that SemanticMatcher initializes correctly."""
        matcher = SemanticMatcher(tmp_path)
        assert matcher.cache_dir == tmp_path
        assert matcher.embeddings == []
        assert matcher.embeddings_file == tmp_path / "session_embeddings.jsonl"

    def test_session_to_text_basic(self, tmp_path):
        """Test basic session-to-text conversion."""
        matcher = SemanticMatcher(tmp_path)

        session = {
            "files": ["auth.py", "login.ts", "oauth_handler.go"],
            "context": {
                "has_auth": True,
                "has_api": False,
                "has_tests": False,
            },
            "agents": ["security-auditor", "code-reviewer"],
        }

        text = matcher._session_to_text(session)

        # Should contain file names
        assert "auth.py" in text
        assert "login.ts" in text

        # Should contain auth keywords
        assert "authentication" in text or "authorization" in text

        # Should contain agent references
        assert "agent:security-auditor" in text
        assert "agent:code-reviewer" in text

    def test_session_to_text_with_multiple_signals(self, tmp_path):
        """Test session-to-text with multiple context signals."""
        matcher = SemanticMatcher(tmp_path)

        session = {
            "files": ["api/routes.ts", "db/migrations/001.sql"],
            "context": {
                "has_auth": False,
                "has_api": True,
                "has_tests": True,
                "has_database": True,
                "has_frontend": False,
                "has_backend": True,
            },
            "agents": ["api-documenter", "test-automator"],
        }

        text = matcher._session_to_text(session)

        # Should contain multiple domain keywords
        assert "api" in text.lower()
        assert "database" in text.lower() or "sql" in text.lower()
        assert "testing" in text.lower() or "test" in text.lower()

    def test_add_session(self, tmp_path):
        """Test adding a session creates an embedding."""
        matcher = SemanticMatcher(tmp_path)

        session = {
            "files": ["test.py"],
            "context": {"has_tests": True},
            "agents": ["test-automator"],
        }

        matcher.add_session(session)

        # Should have one embedding
        assert len(matcher.embeddings) == 1

        # Embedding should be a tuple of (session_data, embedding_vector)
        session_data, embedding = matcher.embeddings[0]
        assert session_data == session
        assert isinstance(embedding, np.ndarray)
        assert embedding.shape == (384,)  # bge-small-en-v1.5 dimension

    def test_embedding_persistence(self, tmp_path):
        """Test that embeddings are saved and loaded from disk."""
        session = {
            "files": ["test.py"],
            "context": {"has_tests": True},
            "agents": ["test-automator"],
        }

        # Create matcher and add session
        matcher1 = SemanticMatcher(tmp_path)
        matcher1.add_session(session)
        assert len(matcher1.embeddings) == 1

        # Create new matcher instance - should load from disk
        matcher2 = SemanticMatcher(tmp_path)
        assert len(matcher2.embeddings) == 1

        # Should be the same session
        loaded_session, loaded_embedding = matcher2.embeddings[0]
        assert loaded_session == session

    def test_find_similar_empty(self, tmp_path):
        """Test similarity search with no embeddings."""
        matcher = SemanticMatcher(tmp_path)

        context = {
            "files": ["auth.py"],
            "context": {"has_auth": True},
        }

        results = matcher.find_similar(context)
        assert results == []

    def test_find_similar_basic(self, tmp_path):
        """Test basic similarity matching."""
        matcher = SemanticMatcher(tmp_path)

        # Add similar sessions
        auth_session1 = {
            "files": ["auth.py", "login.py"],
            "context": {"has_auth": True},
            "agents": ["security-auditor"],
        }
        auth_session2 = {
            "files": ["oauth.py", "jwt.py"],
            "context": {"has_auth": True},
            "agents": ["security-auditor", "code-reviewer"],
        }
        test_session = {
            "files": ["test_api.py"],
            "context": {"has_tests": True},
            "agents": ["test-automator"],
        }

        matcher.add_session(auth_session1)
        matcher.add_session(auth_session2)
        matcher.add_session(test_session)

        # Search for auth-related context
        query = {
            "files": ["authentication.py"],
            "context": {"has_auth": True},
        }

        results = matcher.find_similar(query, top_k=2, min_similarity=0.3)

        # Should find the auth sessions
        assert len(results) >= 1

        # Results should be sorted by similarity
        for i in range(len(results) - 1):
            assert results[i][1] >= results[i + 1][1]

    def test_cosine_similarity(self):
        """Test cosine similarity calculation."""
        # Identical vectors
        a = np.array([1, 0, 0])
        b = np.array([1, 0, 0])
        assert SemanticMatcher._cosine_similarity(a, b) == pytest.approx(1.0)

        # Orthogonal vectors
        a = np.array([1, 0, 0])
        b = np.array([0, 1, 0])
        assert SemanticMatcher._cosine_similarity(a, b) == pytest.approx(0.0)

        # Opposite vectors
        a = np.array([1, 0, 0])
        b = np.array([-1, 0, 0])
        assert SemanticMatcher._cosine_similarity(a, b) == pytest.approx(-1.0)

        # Zero vectors
        a = np.array([0, 0, 0])
        b = np.array([1, 0, 0])
        assert SemanticMatcher._cosine_similarity(a, b) == 0.0

    def test_clear_cache(self, tmp_path):
        """Test clearing the embedding cache."""
        matcher = SemanticMatcher(tmp_path)

        session = {
            "files": ["test.py"],
            "context": {"has_tests": True},
            "agents": ["test-automator"],
        }

        matcher.add_session(session)
        assert len(matcher.embeddings) == 1
        assert matcher.embeddings_file.exists()

        matcher.clear_cache()
        assert len(matcher.embeddings) == 0
        assert not matcher.embeddings_file.exists()


def test_semantic_availability_flag():
    """Test that SEMANTIC_AVAILABLE flag is set correctly."""
    from claude_ctx_py.intelligence import SEMANTIC_AVAILABLE as flag
    assert isinstance(flag, bool)


def test_graceful_degradation_without_fastembed():
    """Test that PatternLearner works without semantic matching."""
    from claude_ctx_py.intelligence import PatternLearner, SessionContext
    from datetime import datetime

    with tempfile.TemporaryDirectory() as tmpdir:
        history_file = Path(tmpdir) / "history.json"

        # Should initialize even without fastembed
        learner = PatternLearner(history_file, enable_semantic=False)
        assert learner.semantic_matcher is None

        # Should still be able to record sessions
        context = SessionContext(
            files_changed=["test.py"],
            file_types={".py"},
            directories={"tests"},
            has_tests=True,
            has_auth=False,
            has_api=False,
            has_frontend=False,
            has_backend=False,
            has_database=False,
            errors_count=0,
            test_failures=0,
            build_failures=0,
            session_start=datetime.now(),
            last_activity=datetime.now(),
            active_agents=[],
            active_modes=[],
            active_rules=[],
        )

        learner.record_success(context, ["test-automator"], 60, "success")

        # Should get recommendations (from heuristics only)
        recs = learner.predict_agents(context)
        assert isinstance(recs, list)
