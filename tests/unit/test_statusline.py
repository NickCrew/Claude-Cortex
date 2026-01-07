"""Tests for statusline module."""

import argparse
import io
import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone

from claude_ctx_py.statusline import (
    C,
    StatusData,
    GitStatus,
    load_config,
    save_config,
    ms_to_hhmmss,
    shorten_path,
    run_cmd,
    format_time_ago,
    get_git_state,
    get_venv_info,
    get_aws_info,
    format_default,
    format_oneline,
    format_json,
    parse_args,
    render_statusline,
    DEFAULT_CONFIG,
    FORMATTERS,
)


class TestColors:
    """Tests for color constants."""

    def test_colors_exist(self):
        """Test that color constants exist."""
        assert hasattr(C, "NC")
        assert hasattr(C, "B_RED")
        assert hasattr(C, "B_GRE")

    def test_disable_colors(self):
        """Test disabling colors."""
        # Save originals
        original_red = C.B_RED

        C.disable()

        assert C.B_RED == ""
        assert C.NC == ""

        # Restore for other tests
        C.B_RED = original_red
        C.NC = "\033[0m"


class TestMsToHhmmss:
    """Tests for ms_to_hhmmss function."""

    def test_zero_ms(self):
        """Test zero milliseconds."""
        assert ms_to_hhmmss(0) == "00:00"

    def test_minutes_only(self):
        """Test minutes only."""
        assert ms_to_hhmmss(5 * 60 * 1000) == "00:05"

    def test_hours_and_minutes(self):
        """Test hours and minutes."""
        assert ms_to_hhmmss(2 * 3600 * 1000 + 30 * 60 * 1000) == "02:30"

    def test_negative_ms(self):
        """Test negative milliseconds uses absolute value."""
        result = ms_to_hhmmss(-5 * 60 * 1000)
        assert result == "00:05"

    def test_none_ms(self):
        """Test None milliseconds."""
        assert ms_to_hhmmss(None) == "00:00"


class TestShortenPath:
    """Tests for shorten_path function."""

    def test_short_path_unchanged(self):
        """Test short paths are unchanged."""
        path = "/a/b/c"
        assert shorten_path(path) == "/a/b/c"

    def test_home_replacement(self):
        """Test home directory replacement."""
        home = str(Path.home())
        path = f"{home}/projects/myproject"
        result = shorten_path(path)
        assert result.startswith("~")

    def test_long_path_shortened(self):
        """Test long paths are shortened."""
        path = "/very/long/path/with/many/parts/here"
        result = shorten_path(path, max_parts=4)
        assert len(result) < len(path)


class TestRunCmd:
    """Tests for run_cmd function."""

    def test_successful_command(self):
        """Test successful command execution."""
        result = run_cmd(["echo", "hello"])
        assert result == "hello"

    def test_failed_command(self):
        """Test failed command returns empty string."""
        result = run_cmd(["false"])
        assert result == ""

    def test_nonexistent_command(self):
        """Test non-existent command returns empty string."""
        result = run_cmd(["nonexistent_command_12345"])
        assert result == ""

    def test_command_with_cwd(self, tmp_path: Path):
        """Test command with working directory."""
        result = run_cmd(["pwd"], cwd=str(tmp_path))
        assert str(tmp_path) in result


class TestFormatTimeAgo:
    """Tests for format_time_ago function."""

    def test_zero_timestamp(self):
        """Test zero timestamp returns empty."""
        assert format_time_ago(0) == ""

    def test_seconds_ago(self):
        """Test seconds ago formatting."""
        now = datetime.now(timezone.utc)
        timestamp = int(now.timestamp()) - 30
        result = format_time_ago(timestamp)
        assert result.endswith("s")

    def test_minutes_ago(self):
        """Test minutes ago formatting."""
        now = datetime.now(timezone.utc)
        timestamp = int(now.timestamp()) - 300  # 5 minutes
        result = format_time_ago(timestamp)
        assert result.endswith("m")

    def test_hours_ago(self):
        """Test hours ago formatting."""
        now = datetime.now(timezone.utc)
        timestamp = int(now.timestamp()) - 7200  # 2 hours
        result = format_time_ago(timestamp)
        assert result.endswith("h")

    def test_days_ago(self):
        """Test days ago formatting."""
        now = datetime.now(timezone.utc)
        timestamp = int(now.timestamp()) - 86400 * 3  # 3 days
        result = format_time_ago(timestamp)
        assert result.endswith("d")


class TestGetGitState:
    """Tests for get_git_state function."""

    def test_normal_state(self, tmp_path: Path):
        """Test normal state (no special files)."""
        state = get_git_state(str(tmp_path))
        assert state == ""

    def test_merging_state(self, tmp_path: Path):
        """Test merging state detection."""
        merge_head = tmp_path / "MERGE_HEAD"
        merge_head.touch()

        state = get_git_state(str(tmp_path))
        assert state == "MERGING"

    def test_rebasing_state_merge(self, tmp_path: Path):
        """Test rebase-merge detection."""
        rebase_dir = tmp_path / "rebase-merge"
        rebase_dir.mkdir()

        state = get_git_state(str(tmp_path))
        assert state == "REBASING"

    def test_rebasing_state_apply(self, tmp_path: Path):
        """Test rebase-apply detection."""
        rebase_dir = tmp_path / "rebase-apply"
        rebase_dir.mkdir()

        state = get_git_state(str(tmp_path))
        assert state == "REBASING"

    def test_cherry_picking_state(self, tmp_path: Path):
        """Test cherry-pick detection."""
        cherry_head = tmp_path / "CHERRY_PICK_HEAD"
        cherry_head.touch()

        state = get_git_state(str(tmp_path))
        assert state == "CHERRY-PICKING"

    def test_bisecting_state(self, tmp_path: Path):
        """Test bisect detection."""
        bisect_log = tmp_path / "BISECT_LOG"
        bisect_log.touch()

        state = get_git_state(str(tmp_path))
        assert state == "BISECTING"


class TestGetVenvInfo:
    """Tests for get_venv_info function."""

    def test_no_venv(self):
        """Test when no virtualenv is active."""
        with patch.dict("os.environ", {}, clear=True):
            result = get_venv_info({})
        assert result == ""

    def test_with_venv(self):
        """Test when virtualenv is active."""
        with patch.dict("os.environ", {"VIRTUAL_ENV": "/path/to/myenv"}):
            result = get_venv_info({"python": ""})
        assert "myenv" in result


class TestGetAwsInfo:
    """Tests for get_aws_info function."""

    def test_no_aws(self):
        """Test when no AWS environment vars."""
        with patch.dict("os.environ", {}, clear=True):
            result = get_aws_info({})
        assert result == ""

    def test_with_profile(self):
        """Test when AWS_PROFILE is set."""
        with patch.dict("os.environ", {"AWS_PROFILE": "production"}):
            result = get_aws_info({"aws": ""})
        assert "production" in result

    def test_with_region(self):
        """Test when AWS_REGION is set."""
        with patch.dict("os.environ", {"AWS_REGION": "us-west-2"}):
            result = get_aws_info({"aws": ""})
        assert "us-west-2" in result


class TestStatusData:
    """Tests for StatusData dataclass."""

    def test_create_status_data(self):
        """Test creating StatusData instance."""
        data = StatusData(
            cwd="/home/user/project",
            tokens_pct=50,
            input_tokens=1000,
            output_tokens=500,
        )
        assert data.cwd == "/home/user/project"
        assert data.tokens_pct == 50

    def test_default_values(self):
        """Test StatusData default values."""
        data = StatusData()
        assert data.cwd == ""
        assert data.tokens_pct == 0
        assert data.cost_usd == 0.0
        assert data.session_time == "00:00"


class TestGitStatus:
    """Tests for GitStatus dataclass."""

    def test_create_git_status(self):
        """Test creating GitStatus instance."""
        status = GitStatus(
            branch="main",
            modified=5,
            staged=2,
        )
        assert status.branch == "main"
        assert status.modified == 5

    def test_default_values(self):
        """Test GitStatus default values."""
        status = GitStatus()
        assert status.branch == ""
        assert status.stashed == 0
        assert status.worktree is False


class TestFormatters:
    """Tests for output formatters."""

    def test_format_default(self):
        """Test default formatter output."""
        data = StatusData(
            cwd="/home/user/project",
            tokens_pct=50,
            input_tokens=1000,
            output_tokens=500,
            model="claude-3",
        )
        config = DEFAULT_CONFIG.copy()

        result = format_default(data, config)

        assert "project" in result
        assert "50%" in result

    def test_format_oneline(self):
        """Test oneline formatter output."""
        data = StatusData(
            cwd="/home/user/project",
            tokens_pct=50,
            input_tokens=1000,
            output_tokens=500,
        )
        config = DEFAULT_CONFIG.copy()

        result = format_oneline(data, config)

        assert "\n" not in result
        assert "50%" in result

    def test_format_json(self):
        """Test JSON formatter output."""
        data = StatusData(
            cwd="/home/user/project",
            tokens_pct=50,
            input_tokens=1000,
        )
        config = DEFAULT_CONFIG.copy()

        result = format_json(data, config)
        parsed = json.loads(result)

        assert parsed["cwd"] == "/home/user/project"
        assert parsed["tokens_pct"] == 50


class TestParseArgs:
    """Tests for argument parsing."""

    def test_default_args(self):
        """Test default argument values."""
        args = parse_args([])
        assert args.format == "default"

    def test_format_option(self):
        """Test format option."""
        args = parse_args(["-f", "json"])
        assert args.format == "json"

    def test_color_options(self):
        """Test color options."""
        args = parse_args(["--no-color"])
        assert args.no_color is True

        args = parse_args(["--color"])
        assert args.color is True

    def test_show_options(self):
        """Test show/no-show options."""
        args = parse_args(["--git"])
        assert args.show_git is True

        args = parse_args(["--no-git"])
        assert args.show_git is False


class TestConfig:
    """Tests for config loading and saving."""

    def test_load_default_config(self, tmp_path: Path):
        """Test loading default config when file doesn't exist."""
        with patch("claude_ctx_py.statusline.CONFIG_PATH", tmp_path / "missing.yaml"):
            config = load_config()

        assert "show_git" in config
        assert config["show_git"] is True

    def test_save_and_load_config(self, tmp_path: Path):
        """Test saving and loading config."""
        config_path = tmp_path / "statusline.yaml"

        with patch("claude_ctx_py.statusline.CONFIG_PATH", config_path):
            save_config({"show_git": False, "separator": " - "})
            config = load_config()

        assert config["show_git"] is False
        assert config["separator"] == " - "


class TestRenderStatusline:
    """Tests for render_statusline function."""

    def test_init_config(self, tmp_path: Path):
        """Test init-config option."""
        config_path = tmp_path / "statusline.yaml"
        stdout = io.StringIO()
        stdin = io.StringIO("{}")

        args = argparse.Namespace(
            format="default",
            color=False,
            no_color=True,
            init_config=True,
            show_git=None,
            show_kube=None,
            show_aws=None,
            show_docker=None,
            show_venv=None,
            show_node=None,
        )

        with patch("claude_ctx_py.statusline.CONFIG_PATH", config_path):
            result = render_statusline(args, stdin=stdin, stdout=stdout)

        assert result == 0
        assert config_path.exists()

    def test_render_with_json_format(self):
        """Test rendering with JSON format."""
        stdout = io.StringIO()
        stdin = io.StringIO(json.dumps({
            "workspace": {"current_dir": "/home/user"},
            "context_window": {"total_input_tokens": 100},
        }))

        args = argparse.Namespace(
            format="json",
            color=False,
            no_color=True,
            init_config=False,
            show_git=False,
            show_kube=False,
            show_aws=False,
            show_docker=False,
            show_venv=False,
            show_node=False,
        )

        with patch("claude_ctx_py.statusline.load_config", return_value=DEFAULT_CONFIG.copy()):
            result = render_statusline(args, stdin=stdin, stdout=stdout)

        assert result == 0
        output = stdout.getvalue()
        parsed = json.loads(output)
        assert "cwd" in parsed


class TestFormatterRegistry:
    """Tests for FORMATTERS registry."""

    def test_all_formatters_exist(self):
        """Test all expected formatters are registered."""
        assert "default" in FORMATTERS
        assert "oneline" in FORMATTERS
        assert "json" in FORMATTERS

    def test_formatters_are_callable(self):
        """Test all formatters are callable."""
        for name, formatter in FORMATTERS.items():
            assert callable(formatter), f"Formatter {name} is not callable"
