"""Tests for reasoning system features and Phase 2 enhancements."""

import pytest
from pathlib import Path
import json


class TestReasoningCommand:
    """Tests for /reasoning:adjust command structure."""

    def test_reasoning_command_exists(self):
        """Test that reasoning/adjust.md command file exists."""
        command_path = Path(__file__).parent.parent.parent / "commands" / "reasoning" / "adjust.md"
        assert command_path.exists(), f"Command file not found at {command_path}"

    def test_reasoning_command_has_required_frontmatter(self):
        """Test that reasoning command has proper frontmatter."""
        # Read the actual command file
        command_path = Path(__file__).parent.parent.parent / "commands" / "reasoning" / "adjust.md"

        if not command_path.exists():
            pytest.skip("Command file not found in expected location")

        content = command_path.read_text()

        # Check for required frontmatter fields
        assert "name: adjust" in content
        assert "description:" in content
        assert "category:" in content
        assert "complexity:" in content

    def test_reasoning_levels_documented(self):
        """Test that all reasoning levels are documented."""
        command_path = Path(__file__).parent.parent.parent / "commands" / "reasoning" / "adjust.md"

        if not command_path.exists():
            pytest.skip("Command file not found in expected location")

        content = command_path.read_text()

        # Check for all depth levels
        assert "low" in content.lower()
        assert "medium" in content.lower()
        assert "high" in content.lower()
        assert "ultra" in content.lower()

        # Check for token budgets
        assert "2K" in content or "2,000" in content
        assert "4K" in content or "4,000" in content
        assert "10K" in content or "10,000" in content
        assert "32K" in content or "32,000" in content

    def test_scope_control_documented(self):
        """Test that scope control is documented."""
        command_path = Path(__file__).parent.parent.parent / "commands" / "reasoning" / "adjust.md"

        if not command_path.exists():
            pytest.skip("Command file not found in expected location")

        content = command_path.read_text()

        # Check for scope options
        assert "--scope current" in content or "scope current" in content
        assert "--scope remaining" in content or "scope remaining" in content


class TestReasoningProfiles:
    """Tests for reasoning profiles in analyze:code command."""

    def test_analyze_code_has_reasoning_profiles(self):
        """Test that analyze:code command documents reasoning profiles."""
        command_path = Path(__file__).parent.parent.parent / "commands" / "analyze" / "code.md"

        if not command_path.exists():
            pytest.skip("Command file not found in expected location")

        content = command_path.read_text()

        # Check for reasoning profile parameter
        assert "--reasoning-profile" in content

        # Check for profile types
        assert "default" in content.lower()
        assert "security" in content.lower()
        assert "performance" in content.lower()

    def test_security_profile_documented(self):
        """Test that security profile is properly documented."""
        command_path = Path(__file__).parent.parent.parent / "commands" / "analyze" / "code.md"

        if not command_path.exists():
            pytest.skip("Command file not found in expected location")

        content = command_path.read_text()

        # Check for security-specific features
        assert "threat modeling" in content.lower() or "owasp" in content.lower()
        assert "cve" in content.lower() or "vulnerability" in content.lower()

    def test_performance_profile_documented(self):
        """Test that performance profile is properly documented."""
        command_path = Path(__file__).parent.parent.parent / "commands" / "analyze" / "code.md"

        if not command_path.exists():
            pytest.skip("Command file not found in expected location")

        content = command_path.read_text()

        # Check for performance-specific features
        assert "algorithmic" in content.lower() or "big-o" in content.lower()
        assert "bottleneck" in content.lower() or "profiling" in content.lower()


class TestUltrathinkEnhancements:
    """Tests for ultrathink flag enhancements."""

    def test_ultrathink_has_summary_options(self):
        """Test that ultrathink documents summary options."""
        flags_path = Path(__file__).parent.parent.parent / "flags" / "analysis-depth.md"

        if not flags_path.exists():
            pytest.skip("analysis-depth.md not found in expected location")

        content = flags_path.read_text()

        # Check for summary options
        assert "--summary" in content
        assert "brief" in content.lower()
        assert "detailed" in content.lower()
        assert "comprehensive" in content.lower()

    def test_ultrathink_auto_enables_introspect(self):
        """Test that ultrathink auto-enables introspect."""
        flags_path = Path(__file__).parent.parent.parent / "flags" / "analysis-depth.md"

        if not flags_path.exists():
            pytest.skip("analysis-depth.md not found in expected location")

        content = flags_path.read_text()

        # Find ultrathink section
        ultrathink_start = content.find("**--ultrathink**")
        if ultrathink_start == -1:
            pytest.fail("--ultrathink flag not found in analysis-depth.md")

        # Check next 500 characters for introspect reference
        ultrathink_section = content[ultrathink_start:ultrathink_start + 500]
        assert "introspect" in ultrathink_section.lower()
        assert "auto-enable" in ultrathink_section.lower() or "auto-enables" in ultrathink_section.lower()

    def test_introspect_documents_transparency_markers(self):
        """Test that introspect flag documents transparency markers."""
        flags_path = Path(__file__).parent.parent.parent / "flags" / "mode-activation.md"

        if not flags_path.exists():
            pytest.skip("mode-activation.md not found in expected location")

        content = flags_path.read_text()

        # Find introspect section
        introspect_start = content.find("**--introspect**")
        if introspect_start == -1:
            pytest.fail("--introspect flag not found in mode-activation.md")

        # Check for transparency markers (emoji or descriptions)
        introspect_section = content[introspect_start:introspect_start + 400]
        marker_count = sum([
            "thinking" in introspect_section.lower(),
            "focus" in introspect_section.lower(),
            "insight" in introspect_section.lower(),
            "data" in introspect_section.lower(),
            "decision" in introspect_section.lower()
        ])

        # Should have at least 3 of the 5 markers documented
        assert marker_count >= 3


class TestDocumentationConsistency:
    """Tests for documentation consistency across files."""

    def test_command_count_matches_actual(self):
        """Test that documented command count matches actual files."""
        commands_dir = Path(__file__).parent.parent.parent / "commands"

        if not commands_dir.exists():
            pytest.skip("Commands directory not found")

        # Count actual command files
        command_files = list(commands_dir.rglob("*.md"))
        # Exclude README.md files
        command_files = [f for f in command_files if f.name != "README.md"]
        actual_count = len(command_files)

        # Read index.md
        index_path = Path(__file__).parent.parent.parent / "docs" / "index.md"
        if index_path.exists():
            content = index_path.read_text()
            # Should mention actual command count
            assert f"{actual_count} commands" in content or "commands across" in content

    def test_reasoning_category_in_project_structure(self):
        """Test that reasoning category is listed in project structure."""
        index_path = Path(__file__).parent.parent.parent / "docs" / "index.md"

        if not index_path.exists():
            pytest.skip("docs/index.md not found")

        content = index_path.read_text()

        # Check for reasoning category
        assert "reasoning/" in content.lower()
        assert "11 categories" in content or "reasoning depth control" in content.lower()

    def test_reasoning_adjust_in_command_reference(self):
        """Test that /reasoning:adjust is in command reference docs."""
        commands_doc = Path(__file__).parent.parent.parent / "docs" / "commands.md"

        if not commands_doc.exists():
            pytest.skip("docs/commands.md not found")

        content = commands_doc.read_text()

        # Check for reasoning:adjust command
        assert "/reasoning:adjust" in content
        assert "Dynamic reasoning depth" in content or "reasoning depth during task" in content.lower()


class TestThinkingBudget:
    """Tests for /reasoning:budget command and --thinking-budget flag."""

    def test_budget_command_exists(self):
        """Test that reasoning/budget.md command file exists."""
        command_path = Path(__file__).parent.parent.parent / "commands" / "reasoning" / "budget.md"

        if not command_path.exists():
            pytest.skip("Command file not found")

        content = command_path.read_text()
        assert "name: budget" in content
        assert "description:" in content

    def test_budget_levels_documented(self):
        """Test that all budget levels are documented."""
        command_path = Path(__file__).parent.parent.parent / "commands" / "reasoning" / "budget.md"

        if not command_path.exists():
            pytest.skip("Command file not found")

        content = command_path.read_text()

        # Check for all budget levels
        assert "4000" in content or "4,000" in content
        assert "10000" in content or "10,000" in content
        assert "32000" in content or "32,000" in content
        assert "128000" in content or "128,000" in content

        # Check for extended thinking mode
        assert "Extended" in content or "extended" in content

    def test_budget_flag_in_flags_md(self):
        """Test that --thinking-budget flag is documented."""
        flags_path = Path(__file__).parent.parent.parent / "flags" / "thinking-budget.md"

        if not flags_path.exists():
            pytest.skip("thinking-budget.md not found")

        content = flags_path.read_text()

        assert "--thinking-budget" in content
        assert "128000" in content or "128K" in content

    def test_cost_information_included(self):
        """Test that budget command includes cost information."""
        command_path = Path(__file__).parent.parent.parent / "commands" / "reasoning" / "budget.md"

        if not command_path.exists():
            pytest.skip("Command file not found")

        content = command_path.read_text()

        # Should have cost examples
        assert "$" in content
        assert "cost" in content.lower() or "pricing" in content.lower()


class TestReasoningProfiles:
    """Tests for expanded reasoning profiles."""

    def test_architecture_profile_exists(self):
        """Test that architecture profile is documented."""
        command_path = Path(__file__).parent.parent.parent / "commands" / "analyze" / "code.md"

        if not command_path.exists():
            pytest.skip("Command file not found")

        content = command_path.read_text()

        assert "architecture" in content.lower()
        assert "microservices" in content.lower() or "api design" in content.lower()

    def test_data_profile_exists(self):
        """Test that data profile is documented."""
        command_path = Path(__file__).parent.parent.parent / "commands" / "analyze" / "code.md"

        if not command_path.exists():
            pytest.skip("Command file not found")

        content = command_path.read_text()

        assert "### data" in content.lower()
        assert "database" in content.lower() or "cqrs" in content.lower()

    def test_testing_profile_exists(self):
        """Test that testing profile is documented."""
        command_path = Path(__file__).parent.parent.parent / "commands" / "analyze" / "code.md"

        if not command_path.exists():
            pytest.skip("Command file not found")

        content = command_path.read_text()

        assert "### testing" in content.lower()
        assert "test coverage" in content.lower() or "property-based" in content.lower()

    def test_skill_mappings_documented(self):
        """Test that profiles document skill activations."""
        command_path = Path(__file__).parent.parent.parent / "commands" / "analyze" / "code.md"

        if not command_path.exists():
            pytest.skip("Command file not found")

        content = command_path.read_text()

        # Check for skill references
        assert "api-design-patterns" in content or "database-design-patterns" in content
        assert "Enables:" in content or "enables:" in content


class TestIntrospectLevels:
    """Tests for --introspect-level enhancement."""

    def test_introspect_levels_documented(self):
        """Test that introspect levels are documented in mode-activation flags."""
        flags_path = Path(__file__).parent.parent.parent / "flags" / "mode-activation.md"

        if not flags_path.exists():
            pytest.skip("mode-activation.md not found")

        content = flags_path.read_text()

        assert "--introspect-level" in content or "introspect-level" in content
        assert "markers" in content.lower()
        assert "steps" in content.lower()
        assert "full" in content.lower()

    def test_transparency_markers_documented(self):
        """Test that transparency markers are documented in mode-activation flags."""
        flags_path = Path(__file__).parent.parent.parent / "flags" / "mode-activation.md"

        if not flags_path.exists():
            pytest.skip("mode-activation.md not found")

        content = flags_path.read_text()

        # Check for emoji or descriptions
        marker_keywords = ["thinking", "focus", "insight", "data", "decision"]
        found_markers = sum(1 for keyword in marker_keywords if keyword in content.lower())

        assert found_markers >= 3


class TestReasoningMetrics:
    """Tests for /reasoning:metrics command."""

    def test_metrics_command_exists(self):
        """Test that reasoning/metrics.md exists."""
        command_path = Path(__file__).parent.parent.parent / "commands" / "reasoning" / "metrics.md"

        if not command_path.exists():
            pytest.skip("Command file not found")

        content = command_path.read_text()
        assert "name: metrics" in content

    def test_metrics_dashboard_documented(self):
        """Test that metrics dashboard format is documented."""
        command_path = Path(__file__).parent.parent.parent / "commands" / "reasoning" / "metrics.md"

        if not command_path.exists():
            pytest.skip("Command file not found")

        content = command_path.read_text()

        # Should document dashboard sections
        assert "dashboard" in content.lower() or "metrics" in content.lower()
        assert "export" in content.lower()

    def test_export_formats_documented(self):
        """Test that export formats are documented."""
        command_path = Path(__file__).parent.parent.parent / "commands" / "reasoning" / "metrics.md"

        if not command_path.exists():
            pytest.skip("Command file not found")

        content = content = command_path.read_text()

        # Check for export formats
        assert "json" in content.lower()
        assert "csv" in content.lower() or "markdown" in content.lower()


class TestAutoEscalation:
    """Tests for --auto-escalate flag."""

    def test_auto_escalate_documented(self):
        """Test that --auto-escalate is documented in auto-escalation flags."""
        flags_path = Path(__file__).parent.parent.parent / "flags" / "auto-escalation.md"

        if not flags_path.exists():
            pytest.skip("auto-escalation.md not found")

        content = flags_path.read_text()

        assert "--auto-escalate" in content

    def test_escalation_triggers_documented(self):
        """Test that escalation triggers are documented."""
        flags_path = Path(__file__).parent.parent.parent / "flags" / "auto-escalation.md"

        if not flags_path.exists():
            pytest.skip("auto-escalation.md not found")

        content = flags_path.read_text()

        # Check for trigger types
        assert "confidence" in content.lower()
        assert "errors" in content.lower()
        assert "complexity" in content.lower()
        assert "adaptive" in content.lower()

    def test_escalation_modes_documented(self):
        """Test that all escalation modes are documented."""
        flags_path = Path(__file__).parent.parent.parent / "flags" / "auto-escalation.md"

        if not flags_path.exists():
            pytest.skip("auto-escalation.md not found")

        content = flags_path.read_text()

        # Should describe what each mode does
        auto_escalate_section = content[content.find("--auto-escalate"):][:2000]

        assert "confidence" in auto_escalate_section.lower()
        assert "0.6" in auto_escalate_section or "threshold" in auto_escalate_section.lower()
