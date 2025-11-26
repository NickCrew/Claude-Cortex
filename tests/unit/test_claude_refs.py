"""Tests for CLAUDE.md reference parsing helpers."""

from pathlib import Path

from claude_ctx_py.core.base import _parse_claude_md_refs


def test_parse_claude_md_refs_recognizes_active_entries(tmp_path: Path) -> None:
    """Ensure active rule and mode references are detected while comments are ignored."""
    claude_md = tmp_path / "CLAUDE.md"
    claude_md.write_text(
        """
# Core
@rules/workflow-rules.md
# @rules/quality-rules.md
   @rules/Quality/Advanced.md    # optional

# Modes
@modes/Parallel_Orchestration.md
#    @inactive/modes/Deep_Analysis.md
@modes/supersaiyan/Super_Mode.md
""",
        encoding="utf-8",
    )

    rule_refs = _parse_claude_md_refs(tmp_path, "rules")
    mode_refs = _parse_claude_md_refs(tmp_path, "modes")

    assert rule_refs == {"workflow-rules", "quality/advanced"}
    assert mode_refs == {"parallel_orchestration", "supersaiyan/super_mode"}
