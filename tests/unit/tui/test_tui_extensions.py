"""Unit tests for TUI extension mixins."""

import pytest
from unittest.mock import MagicMock, patch, PropertyMock
from pathlib import Path
from typing import Any, Dict, List, Set, Optional

from claude_ctx_py.tui_extensions import ProfileViewMixin, ExportViewMixin, WizardViewMixin
from claude_ctx_py.core.asset_discovery import Asset, AssetCategory

class MockState:
    """Mock state object for TUI mixins."""
    def __init__(self):
        self.selected_index = 0
        self.current_view = "overview"
        self.status_message = ""

class MockApp(ProfileViewMixin, ExportViewMixin, WizardViewMixin):
    """Mock application class that uses the mixins."""
    def __init__(self):
        # Initialize mixins
        super().__init__()
        self.state = MockState()
        self.selected_index = 0 # Also on main app
        self.wizard_active = False
        self.wizard_step = 0
        self.wizard_selections = {}
        self.available_assets = {}
        self.flag_categories = ["all"]
        self.flag_categories_enabled = {}
        self.current_flag_category = "all"
        
        # Mixin requirements
        self.load_agents = MagicMock()
        self.update_view = MagicMock()
        self.notify = MagicMock()

    def _load_profiles_data(self):
        pass

@pytest.fixture
def mock_app():
    return MockApp()

class TestProfileViewMixin:
    """Tests for ProfileViewMixin."""

    @patch("claude_ctx_py.tui_extensions._resolve_claude_dir")
    @patch("claude_ctx_py.tui_extensions._get_current_active_state")
    def test_load_profiles(self, mock_active_state, mock_resolve_dir, mock_app):
        mock_resolve_dir.return_value = Path("/tmp/.cortex")
        mock_active_state.return_value = (set(), set(), set())
        
        profiles = mock_app.load_profiles()
        
        assert len(profiles) > 0
        assert profiles[0]["type"] == "built-in"
        assert any(p["name"] == "minimal" for p in profiles)

    def test_get_profile_state_from_name_built_in(self, mock_app):
        agents, modes, rules = mock_app._get_profile_state_from_name("minimal", Path("/tmp"), True)
        assert "debugger" in agents # Essential agent
        assert len(modes) == 0
        assert len(rules) == 0
        
        # Test a few others for coverage
        agents, modes, rules = mock_app._get_profile_state_from_name("backend", Path("/tmp"), True)
        assert "python-pro" in agents
        assert "Task_Management" in modes
        
        agents, modes, rules = mock_app._get_profile_state_from_name("frontend", Path("/tmp"), True)
        assert "typescript-pro" in agents
        
        agents, modes, rules = mock_app._get_profile_state_from_name("full", Path("/tmp"), True)
        assert "Super_Saiyan" in modes

    @patch("claude_ctx_py.tui_extensions.profile_minimal")
    def test_apply_profile_success(self, mock_minimal, mock_app):
        mock_minimal.return_value = (0, "Success")
        mock_app.load_profiles = MagicMock(return_value=[{"name": "minimal", "type": "built-in"}])
        mock_app.state.selected_index = 0
        
        mock_app.apply_profile()
        
        mock_minimal.assert_called_once()
        assert "Success" in mock_app.state.status_message
        mock_app.load_agents.assert_called_once()

    def test_apply_profile_not_implemented(self, mock_app):
        mock_app.load_profiles = MagicMock(return_value=[{"name": "unknown", "type": "built-in"}])
        mock_app.state.selected_index = 0
        mock_app.apply_profile()
        assert "not implemented" in mock_app.state.status_message

    def test_delete_profile_built_in(self, mock_app):
        mock_app.load_profiles = MagicMock(return_value=[{"name": "minimal", "type": "built-in"}])
        mock_app.state.selected_index = 0
        mock_app.delete_profile()
        assert "Cannot delete built-in" in mock_app.state.status_message

    def test_delete_profile_not_selected(self, mock_app):
        mock_app.load_profiles = MagicMock(return_value=[])
        mock_app.delete_profile()
        assert "No profile selected" in mock_app.state.status_message

    @patch("claude_ctx_py.tui_extensions._get_profile_state")
    def test_get_profile_state_saved(self, mock_get_state, mock_app):
        mock_get_state.return_value = ({"agent1"}, {"mode1"}, {"rule1"})
        with patch("pathlib.Path.is_file", return_value=True):
            agents, modes, rules = mock_app._get_profile_state_from_name("custom", Path("/tmp"), False)
            assert "agent1" in agents

    def test_render_profile_view(self, mock_app):
        mock_app.load_profiles = MagicMock(return_value=[
            {"name": "minimal", "type": "built-in", "description": "desc", "active": True}
        ])
        panel = mock_app.render_profile_view()
        assert panel.title == "Profile Management"

class TestExportViewMixin:
    """Tests for ExportViewMixin."""

    def test_init_export_options(self, mock_app):
        # The mixin __init__ is called by MockApp.__init__
        assert mock_app.export_options["core"] is True
        assert mock_app.export_format == "json"

    def test_toggle_export_option(self, mock_app):
        mock_app.state.selected_index = 0 # "core"
        initial_val = mock_app.export_options["core"]
        
        mock_app.toggle_export_option()
        assert mock_app.export_options["core"] is not initial_val
        
        mock_app.toggle_export_option()
        assert mock_app.export_options["core"] is initial_val

    def test_cycle_export_format(self, mock_app):
        assert mock_app.export_format == "json"
        mock_app.cycle_export_format()
        assert mock_app.export_format == "xml"
        mock_app.cycle_export_format()
        assert mock_app.export_format == "markdown"
        mock_app.cycle_export_format()
        assert mock_app.export_format == "json"

    def test_render_export_view(self, mock_app):
        panel = mock_app.render_export_view()
        assert panel.title == "Context Export"

    @patch("claude_ctx_py.tui_extensions.collect_context_components")
    @patch("claude_ctx_py.tui_extensions._resolve_claude_dir")
    def test_generate_export_preview_json(self, mock_resolve, mock_collect, mock_app):
        mock_resolve.return_value = Path("/tmp")
        mock_collect.return_value = {"core": {"file1": "content"}}
        mock_app.export_format = "json"
        
        preview = mock_app.generate_export_preview()
        assert '"core":' in preview
        assert '"file1"' in preview
        
        mock_app.export_format = "xml"
        assert "xml" in mock_app.generate_export_preview()
        
        mock_app.export_format = "markdown"
        assert "Cortex Context Export" in mock_app.generate_export_preview()

    @patch("claude_ctx_py.tui_extensions.export_context")
    def test_execute_export(self, mock_export, mock_app):
        mock_export.return_value = (0, "Success")
        mock_app.execute_export()
        assert "Success" in mock_app.state.status_message

    @patch("subprocess.run")
    def test_copy_to_clipboard(self, mock_run, mock_app):
        mock_app.copy_to_clipboard()
        mock_run.assert_called_once()
        assert "copied to clipboard" in mock_app.state.status_message

class TestWizardViewMixin:
    """Tests for WizardViewMixin."""

    def test_start_wizard(self, mock_app):
        mock_app.start_wizard()
        assert mock_app.wizard_active is True
        assert mock_app.wizard_step == 0
        assert mock_app.state.selected_index == 0

    def test_wizard_navigation(self, mock_app):
        mock_app.start_wizard()
        mock_app.wizard_next_step()
        assert mock_app.wizard_step == 1
        mock_app.wizard_prev_step()
        assert mock_app.wizard_step == 0
        
        mock_app.action_wizard_prev()
        assert mock_app.wizard_step == 0 # Clamped

    def test_action_wizard_next_confirmation(self, mock_app):
        mock_app.wizard_active = True
        mock_app.wizard_step = 4
        with patch.object(mock_app, "_apply_wizard_configuration") as mock_apply:
            mock_app.action_wizard_next()
            mock_apply.assert_called_once()
            assert mock_app.wizard_step == 5

    def test_action_wizard_toggle_no_active(self, mock_app):
        mock_app.wizard_active = False
        mock_app.action_wizard_toggle() # Should do nothing

    @patch("claude_ctx_py.tui_extensions.discover_plugin_assets")
    def test_action_wizard_toggle_agent(self, mock_discover, mock_app):
        mock_app.start_wizard()
        mock_app.state.selected_index = 1 # Backend API
        
        mock_app.action_wizard_next()
        
        assert mock_app.wizard_selections["project_type"] == "Backend API"
        assert mock_app.wizard_step == 1

    @patch("claude_ctx_py.tui_extensions.discover_plugin_assets")
    def test_action_wizard_toggle_agent(self, mock_discover, mock_app):
        mock_app.wizard_active = True
        mock_app.wizard_step = 1 # Agents
        mock_app.state.selected_index = 0
        
        mock_asset = MagicMock(spec=Asset)
        mock_asset.name = "test-agent"
        mock_discover.return_value = {"agents": [mock_asset]}
        
        # Toggle on
        mock_app.action_wizard_toggle()
        assert "test-agent" in mock_app.wizard_selections["agents"]
        
        # Toggle off
        mock_app.action_wizard_toggle()
        assert "test-agent" not in mock_app.wizard_selections["agents"]

    @patch("claude_ctx_py.tui_extensions.discover_plugin_assets")
    def test_action_wizard_toggle_mode(self, mock_discover, mock_app):
        mock_app.wizard_active = True
        mock_app.wizard_step = 2 # Modes
        mock_app.state.selected_index = 0
        
        mock_asset = MagicMock()
        mock_asset.name = "Turbo"
        mock_discover.return_value = {"modes": [mock_asset]}
        
        mock_app.action_wizard_toggle()
        assert "Turbo" in mock_app.wizard_selections["modes"]

    @patch("claude_ctx_py.tui_extensions.discover_plugin_assets")
    def test_action_wizard_toggle_rule(self, mock_discover, mock_app):
        mock_app.wizard_active = True
        mock_app.wizard_step = 3 # Rules
        mock_app.state.selected_index = 0
        
        mock_asset = MagicMock()
        mock_asset.name = "strict"
        mock_discover.return_value = {"rules": [mock_asset]}
        
        mock_app.action_wizard_toggle()
        assert "strict" in mock_app.wizard_selections["rules"]

    @patch("claude_ctx_py.tui_extensions.profile_backend")
    @patch("claude_ctx_py.tui_extensions.agent_activate")
    def test_apply_wizard_configuration(self, mock_agent_act, mock_profile_backend, mock_app):
        mock_app.wizard_selections = {
            "project_type": "Backend API",
            "agents": {"special-agent"},
            "modes": {"Turbo"},
            "rules": {"strict-rules"}
        }
        
        with patch("claude_ctx_py.tui_extensions.mode_activate") as mock_mode_act:
            with patch("claude_ctx_py.tui_extensions.rules_activate") as mock_rule_act:
                mock_app._apply_wizard_configuration()
                
                mock_profile_backend.assert_called_once()
                mock_agent_act.assert_called_with("special-agent")
                mock_mode_act.assert_called_with("Turbo")
                mock_rule_act.assert_called_with("strict-rules")

    @patch("claude_ctx_py.tui_extensions.profile_web_dev")
    def test_apply_wizard_configuration_web(self, mock_profile_web, mock_app):
        mock_app.wizard_selections = {"project_type": "Web Development (Frontend/Backend)"}
        with patch("claude_ctx_py.tui_extensions.agent_activate"):
            with patch("claude_ctx_py.tui_extensions.mode_activate"):
                with patch("claude_ctx_py.tui_extensions.rules_activate"):
                    mock_app._apply_wizard_configuration()
                    mock_profile_web.assert_called_once()

    @patch("claude_ctx_py.tui_extensions.profile_devops")
    def test_apply_wizard_configuration_devops(self, mock_profile, mock_app):
        mock_app.wizard_selections = {"project_type": "DevOps/Infrastructure"}
        with patch("claude_ctx_py.tui_extensions.agent_activate"), \
             patch("claude_ctx_py.tui_extensions.mode_activate"), \
             patch("claude_ctx_py.tui_extensions.rules_activate"):
            mock_app._apply_wizard_configuration()
            mock_profile.assert_called_once()

    @patch("claude_ctx_py.tui_extensions.profile_data_ai")
    def test_apply_wizard_configuration_data(self, mock_profile, mock_app):
        mock_app.wizard_selections = {"project_type": "Data Science/AI"}
        with patch("claude_ctx_py.tui_extensions.agent_activate"), \
             patch("claude_ctx_py.tui_extensions.mode_activate"), \
             patch("claude_ctx_py.tui_extensions.rules_activate"):
            mock_app._apply_wizard_configuration()
            mock_profile.assert_called_once()

    @patch("claude_ctx_py.tui_extensions.profile_documentation")
    def test_apply_wizard_configuration_docs(self, mock_profile, mock_app):
        mock_app.wizard_selections = {"project_type": "Documentation"}
        with patch("claude_ctx_py.tui_extensions.agent_activate"), \
             patch("claude_ctx_py.tui_extensions.mode_activate"), \
             patch("claude_ctx_py.tui_extensions.rules_activate"):
            mock_app._apply_wizard_configuration()
            mock_profile.assert_called_once()

    def test_render_wizard_view_steps(self, mock_app):
        mock_app.wizard_active = True
        
        # Step 0: Start
        mock_app.wizard_step = 0
        panel = mock_app.render_wizard_view()
        assert "Step 1/5" in panel.renderable.plain # type: ignore
        
        # Step 1: Agents
        mock_app.wizard_step = 1
        with patch("claude_ctx_py.tui_extensions.discover_plugin_assets") as mock_disc:
            mock_disc.return_value = {"agents": []}
            
            # Test pre-selection for DevOps
            mock_app.wizard_selections = {"project_type": "DevOps/Infrastructure"}
            panel = mock_app.render_wizard_view()
            assert "Step 2/5" in panel.renderable.plain # type: ignore
            assert "deployment-engineer" in mock_app.wizard_selections["agents"]
            
            # Test pre-selection for Data
            mock_app.wizard_selections = {"project_type": "Data Science/AI"}
            mock_app.wizard_selections.pop("agents", None) # Force re-detect
            panel = mock_app.render_wizard_view()
            assert "python-pro" in mock_app.wizard_selections["agents"]

        # Step 2: Modes
        mock_app.wizard_step = 2
        with patch("claude_ctx_py.tui_extensions.discover_plugin_assets") as mock_disc:
            mock_disc.return_value = {"modes": []}
            panel = mock_app.render_wizard_view()
            assert "Step 3/5" in panel.renderable.plain # type: ignore

        # Step 3: Rules
        mock_app.wizard_step = 3
        with patch("claude_ctx_py.tui_extensions.discover_plugin_assets") as mock_disc:
            mock_disc.return_value = {"rules": []}
            panel = mock_app.render_wizard_view()
            assert "Step 4/5" in panel.renderable.plain # type: ignore
            
        # Step 4: Confirm
        mock_app.wizard_step = 4
        panel = mock_app.render_wizard_view()
        assert "Step 5/5" in panel.renderable.plain # type: ignore
