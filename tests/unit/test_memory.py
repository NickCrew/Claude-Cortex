"""Tests for the memory capture system."""

from __future__ import annotations

import json
import pytest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from claude_ctx_py import memory
from claude_ctx_py.memory import templates, notes, config, capture, search


class TestSlugify:
    """Test the slugify function."""

    def test_simple_text(self):
        assert notes.slugify("Hello World") == "hello-world"

    def test_special_characters(self):
        assert notes.slugify("Test@123!") == "test123"

    def test_underscores(self):
        assert notes.slugify("hello_world_test") == "hello-world-test"

    def test_multiple_spaces(self):
        assert notes.slugify("hello   world") == "hello-world"

    def test_leading_trailing(self):
        assert notes.slugify("  hello world  ") == "hello-world"


class TestExtractTopicFromText:
    """Test topic extraction from text."""

    def test_is_pattern(self):
        assert notes.extract_topic_from_text("gateway is for connections") == "gateway"

    def test_quoted_text(self):
        assert notes.extract_topic_from_text('Check the "config file" here') == "config file"

    def test_for_pattern(self):
        assert notes.extract_topic_from_text("kubernetes for container orchestration") == "kubernetes"

    def test_fallback(self):
        # The "is" pattern matches, so it returns "this"
        topic = notes.extract_topic_from_text("simple example text here")
        # For text without special patterns, it falls back to first few words
        assert len(topic) > 0


class TestTemplates:
    """Test template rendering functions."""

    def test_render_knowledge_note(self):
        content = templates.render_knowledge_note(
            topic="Test Topic",
            summary="A test summary",
            details=["Fact 1", "Fact 2"],
            tags=["test"],
        )
        assert "# Test Topic" in content
        assert "## Summary" in content
        assert "A test summary" in content
        assert "- Fact 1" in content
        assert "- Fact 2" in content
        assert "#knowledge" in content
        assert "#test" in content

    def test_render_project_note(self):
        content = templates.render_project_note(
            name="test-project",
            purpose="A test project",
            path="/path/to/project",
            remote="git@github.com:test/project.git",
        )
        assert "# test-project" in content
        assert "## Purpose" in content
        assert "A test project" in content
        assert "/path/to/project" in content
        assert "#project" in content

    def test_render_session_note(self):
        content = templates.render_session_note(
            title="Test Session",
            summary="Worked on features",
            decisions=["Chose approach A"],
            implementations=["Built component X"],
            open_items=["Need to fix Y"],
        )
        assert "# Test Session" in content
        assert "## Decisions" in content
        assert "- Chose approach A" in content
        assert "## Implementations" in content
        assert "## Open Items" in content

    def test_render_fix_note(self):
        content = templates.render_fix_note(
            title="Bug Fix",
            problem="App crashed",
            cause="Null pointer",
            solution="Added null check",
            files_changed=[("src/app.py", "Added validation")],
        )
        assert "# Bug Fix" in content
        assert "## Problem" in content
        assert "## Cause" in content
        assert "## Solution" in content
        assert "## Files Changed" in content
        assert "`src/app.py`" in content


class TestConfig:
    """Test configuration management."""

    def test_memory_config_defaults(self):
        cfg = config.MemoryConfig()
        assert cfg.vault_path == "~/basic-memory"
        assert cfg.auto_capture.enabled is False
        assert cfg.auto_capture.min_session_length == 5

    def test_memory_config_to_dict(self):
        cfg = config.MemoryConfig()
        d = cfg.to_dict()
        assert "vault_path" in d
        assert "auto_capture" in d
        assert "defaults" in d

    def test_memory_config_from_dict(self):
        data = {
            "vault_path": "/custom/path",
            "auto_capture": {"enabled": True, "min_session_length": 10},
            "defaults": {"tags": ["default"]},
        }
        cfg = config.MemoryConfig.from_dict(data)
        assert cfg.vault_path == "/custom/path"
        assert cfg.auto_capture.enabled is True
        assert cfg.auto_capture.min_session_length == 10


class TestNotes:
    """Test note CRUD operations."""

    def test_get_note_path(self, tmp_path):
        path = notes.get_note_path(
            templates.NoteType.KNOWLEDGE,
            "Test Topic",
            vault_path=tmp_path,
        )
        assert path == tmp_path / "knowledge" / "test-topic.md"

    def test_get_session_note_path_unique(self, tmp_path):
        # Create first note
        sessions_dir = tmp_path / "sessions"
        sessions_dir.mkdir(parents=True)

        path1 = notes.get_session_note_path("Test", vault_path=tmp_path)
        path1.parent.mkdir(parents=True, exist_ok=True)
        path1.write_text("test", encoding="utf-8")

        # Second note should have sequence number
        path2 = notes.get_session_note_path("Test", vault_path=tmp_path)
        assert path2 != path1
        assert "-2" in path2.name

    def test_create_note(self, tmp_path):
        content = "# Test\n\nContent here"
        path, created = notes.create_note(
            templates.NoteType.KNOWLEDGE,
            "test-note",
            content,
            vault_path=tmp_path,
        )
        assert created is True
        assert path.exists()
        assert path.read_text() == content

    def test_read_note(self, tmp_path):
        # Create note first
        content = "# Test\n\nContent"
        notes.create_note(
            templates.NoteType.KNOWLEDGE,
            "test-note",
            content,
            vault_path=tmp_path,
        )

        # Read it back
        result = notes.read_note(
            templates.NoteType.KNOWLEDGE,
            "test-note",
            vault_path=tmp_path,
        )
        assert result == content

    def test_read_note_not_found(self, tmp_path):
        result = notes.read_note(
            templates.NoteType.KNOWLEDGE,
            "nonexistent",
            vault_path=tmp_path,
        )
        assert result is None

    def test_note_exists(self, tmp_path):
        # Create a note
        notes.create_note(
            templates.NoteType.KNOWLEDGE,
            "exists-note",
            "content",
            vault_path=tmp_path,
        )

        assert notes.note_exists(templates.NoteType.KNOWLEDGE, "exists-note", tmp_path)
        assert not notes.note_exists(templates.NoteType.KNOWLEDGE, "no-note", tmp_path)

    def test_list_notes(self, tmp_path):
        # Create some notes
        notes.create_note(
            templates.NoteType.KNOWLEDGE,
            "note1",
            "# Note 1\n\n---\ntags: #test\n",
            vault_path=tmp_path,
        )
        notes.create_note(
            templates.NoteType.PROJECT,
            "project1",
            "# Project 1\n\n---\ntags: #project\n",
            vault_path=tmp_path,
        )

        # List all
        all_notes = notes.list_notes(vault_path=tmp_path)
        assert len(all_notes) == 2

        # List by type
        knowledge_notes = notes.list_notes(
            note_type=templates.NoteType.KNOWLEDGE,
            vault_path=tmp_path,
        )
        assert len(knowledge_notes) == 1
        assert knowledge_notes[0]["type"] == "knowledge"


class TestSearch:
    """Test search functionality."""

    def test_search_notes(self, tmp_path):
        # Create notes with searchable content
        notes.create_note(
            templates.NoteType.KNOWLEDGE,
            "python-testing",
            "# Python Testing\n\n## Summary\nHow to test Python code\n\n## Details\n- Use pytest\n\n---\ntags: #knowledge\n",
            vault_path=tmp_path,
        )
        notes.create_note(
            templates.NoteType.KNOWLEDGE,
            "javascript",
            "# JavaScript\n\n## Summary\nJS stuff\n\n---\ntags: #knowledge\n",
            vault_path=tmp_path,
        )

        # Search for python
        results = search.search_notes("python", vault_path=tmp_path)
        assert len(results) == 1
        assert "python" in results[0]["title"].lower()

    def test_search_notes_no_results(self, tmp_path):
        notes.create_note(
            templates.NoteType.KNOWLEDGE,
            "test",
            "# Test\n\n---\ntags: #test\n",
            vault_path=tmp_path,
        )

        results = search.search_notes("nonexistent", vault_path=tmp_path)
        assert len(results) == 0

    def test_get_all_tags(self, tmp_path):
        notes.create_note(
            templates.NoteType.KNOWLEDGE,
            "note1",
            "# Note\n\n---\ntags: #python #testing\n",
            vault_path=tmp_path,
        )
        notes.create_note(
            templates.NoteType.KNOWLEDGE,
            "note2",
            "# Note 2\n\n---\ntags: #python #dev\n",
            vault_path=tmp_path,
        )

        tags = search.get_all_tags(vault_path=tmp_path)
        assert tags.get("python") == 2
        assert tags.get("testing") == 1
        assert tags.get("dev") == 1


class TestCapture:
    """Test capture CLI functions."""

    def test_memory_remember(self, tmp_path, monkeypatch):
        monkeypatch.setenv("CORTEX_MEMORY_VAULT", str(tmp_path))

        exit_code, message = capture.memory_remember(
            text="Python is great for scripting",
            topic="python",
        )

        assert exit_code == 0
        assert "Created" in message or "Updated" in message
        assert (tmp_path / "knowledge" / "python.md").exists()

    def test_memory_project(self, tmp_path, monkeypatch):
        monkeypatch.setenv("CORTEX_MEMORY_VAULT", str(tmp_path))

        exit_code, message = capture.memory_project(
            name="test-project",
            purpose="A test project",
            path="/path/to/project",
        )

        assert exit_code == 0
        assert "Created" in message or "Updated" in message
        assert (tmp_path / "projects" / "test-project.md").exists()

    def test_memory_capture(self, tmp_path, monkeypatch):
        monkeypatch.setenv("CORTEX_MEMORY_VAULT", str(tmp_path))

        exit_code, message = capture.memory_capture(
            title="Test Session",
            summary="Tested the memory system",
            decisions=["Chose pytest"],
        )

        assert exit_code == 0
        assert "Created" in message

        # Check session file was created
        sessions = list((tmp_path / "sessions").glob("*.md"))
        assert len(sessions) == 1

    def test_memory_fix(self, tmp_path, monkeypatch):
        monkeypatch.setenv("CORTEX_MEMORY_VAULT", str(tmp_path))

        exit_code, message = capture.memory_fix(
            title="Fixed null pointer",
            problem="App crashed on null",
            cause="Missing validation",
            solution="Added null check",
        )

        assert exit_code == 0
        assert "Created" in message
        assert (tmp_path / "fixes" / "fixed-null-pointer.md").exists()

    def test_memory_auto(self, tmp_path, monkeypatch):
        monkeypatch.setenv("CLAUDE_PLUGIN_ROOT", str(tmp_path))

        # Check status
        exit_code, message = capture.memory_auto("status")
        assert exit_code == 0
        assert "disabled" in message

        # Enable
        exit_code, message = capture.memory_auto("on")
        assert exit_code == 0
        assert "enabled" in message

        # Disable
        exit_code, message = capture.memory_auto("off")
        assert exit_code == 0
        assert "disabled" in message

    def test_memory_list(self, tmp_path, monkeypatch):
        monkeypatch.setenv("CORTEX_MEMORY_VAULT", str(tmp_path))

        # Create some notes
        capture.memory_remember(text="Test fact", topic="test")

        # List
        exit_code, message = capture.memory_list()
        assert exit_code == 0
        # May be "No notes" or list output

    def test_memory_search(self, tmp_path, monkeypatch):
        monkeypatch.setenv("CORTEX_MEMORY_VAULT", str(tmp_path))

        # Create a note
        capture.memory_remember(text="Python is great", topic="python")

        # Search
        exit_code, message = capture.memory_search("python")
        assert exit_code == 0

    def test_get_vault_stats(self, tmp_path, monkeypatch):
        monkeypatch.setenv("CORTEX_MEMORY_VAULT", str(tmp_path))

        # Create some notes
        capture.memory_remember(text="Fact 1", topic="topic1")
        capture.memory_project(name="proj1", purpose="Test")

        stats = capture.get_vault_stats()
        assert stats["total"] >= 2
        assert stats["types"]["knowledge"] >= 1
        assert stats["types"]["projects"] >= 1
