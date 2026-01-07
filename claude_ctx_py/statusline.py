"""Claude Code status line utilities."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, Mapping, TextIO, cast

from .core.base import _resolve_claude_dir

try:
    import yaml

    HAS_YAML = True
except ImportError:  # pragma: no cover - optional dependency
    HAS_YAML = False


# =========================================================================
# Colors
# =========================================================================
class C:
    """ANSI color codes."""

    NC = "\033[0m"
    # Bright
    B_RED = "\033[1;31m"
    B_GRE = "\033[1;32m"
    B_YEL = "\033[1;33m"
    B_BLU = "\033[1;34m"
    B_MAG = "\033[1;35m"
    B_CYA = "\033[1;36m"
    B_WHI = "\033[1;37m"
    # Regular
    RED = "\033[0;31m"
    GRE = "\033[0;32m"
    YEL = "\033[0;33m"
    BLU = "\033[0;34m"
    MAG = "\033[0;35m"
    CYA = "\033[0;36m"
    WHI = "\033[0;37m"

    @classmethod
    def disable(cls) -> None:
        """Disable all colors."""
        for attr in dir(cls):
            if not attr.startswith("_") and attr != "disable":
                setattr(cls, attr, "")


# =========================================================================
# Config
# =========================================================================
CONFIG_PATH = _resolve_claude_dir() / "statusline.yaml"

ConfigDict = Dict[str, Any]
IconMap = Dict[str, str]

DEFAULT_CONFIG: ConfigDict = {
    "show_git": True,
    "show_kube": False,
    "show_aws": False,
    "show_docker": False,
    "show_venv": True,
    "show_node": False,
    # Git extras (worktree + last_commit always on)
    "git_show_conflicts": True,
    "git_show_state": True,  # merge/rebase/cherry-pick/bisect
    "git_show_tag": False,
    "git_show_assume_unchanged": False,
    "git_show_submodules": False,
    "separator": " | ",
    "icons": {
        "dir": "",
        "git": "",
        "tokens": "",
        "in_tokens": "󰜮",
        "out_tokens": "󰜷",
        "added": "",
        "removed": "",
        "model": "",
        "kube": "󰒋",
        "aws": "",
        "docker": "",
        "python": "",
        "node": "",
        "worktree": "⊕",
        "conflict": "✖",
        "state": "⚡",
        "tag": "",
        "time": "◷",
    },
}


def load_config() -> ConfigDict:
    """Load config from file, falling back to defaults."""
    config = DEFAULT_CONFIG.copy()
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH) as f:
                if HAS_YAML:
                    user_config = yaml.safe_load(f) or {}
                else:
                    user_config = json.load(f)
                if isinstance(user_config, dict):
                    config.update(user_config)
        except Exception:
            pass
    return config


def save_config(config: ConfigDict) -> None:
    """Save config to file."""
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        if HAS_YAML:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)
        else:
            json.dump(config, f, indent=2)


# =========================================================================
# Helpers
# =========================================================================
def ms_to_hhmmss(ms: int) -> str:
    """Convert milliseconds to HH:MM format."""
    ms = abs(ms or 0)
    total_seconds = ms // 1000
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    return f"{hours:02d}:{minutes:02d}"


def shorten_path(path: str, max_parts: int = 4) -> str:
    """Shorten path for display."""
    home = str(Path.home())
    if path.startswith(home):
        path = "~" + path[len(home) :]

    parts = path.split("/")
    if len(parts) <= max_parts:
        return path

    result = [parts[0]]
    for i, part in enumerate(parts[1:-1], start=1):
        if i == 1 or i == len(parts) - 2:
            result.append(part[:3])
        else:
            result.append(part[:1])
    result.append(parts[-1])
    return "/".join(result)


def run_cmd(cmd: list[str], cwd: str | None = None, timeout: int = 3) -> str:
    """Run command, return stdout or empty string on failure."""
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, cwd=cwd, timeout=timeout
        )
        return result.stdout.strip() if result.returncode == 0 else ""
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return ""


# =========================================================================
# Git
# =========================================================================
@dataclass
class GitStatus:
    branch: str = ""
    stashed: int = 0
    modified: int = 0
    staged: int = 0
    untracked: int = 0
    ahead: int = 0
    behind: int = 0
    conflicts: int = 0
    state: str = ""
    tag: str = ""
    worktree: bool = False
    assume_unchanged: int = 0
    dirty_submodules: int = 0
    last_commit_age: str = ""


def format_time_ago(timestamp: int) -> str:
    """Format unix timestamp as relative time (e.g., '3d', '2h', '15m')."""
    if not timestamp:
        return ""

    now = datetime.now(timezone.utc)
    commit_time = datetime.fromtimestamp(timestamp, timezone.utc)
    delta = now - commit_time

    seconds = int(delta.total_seconds())
    if seconds < 60:
        return f"{seconds}s"
    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes}m"
    hours = minutes // 60
    if hours < 24:
        return f"{hours}h"
    days = hours // 24
    if days < 30:
        return f"{days}d"
    months = days // 30
    if months < 12:
        return f"{months}mo"
    years = days // 365
    return f"{years}y"


def get_git_state(git_dir: str) -> str:
    """Detect merge/rebase/cherry-pick/bisect state."""
    git_path = Path(git_dir)

    if (git_path / "MERGE_HEAD").exists():
        return "MERGING"
    if (git_path / "rebase-merge").exists():
        return "REBASING"
    if (git_path / "rebase-apply").exists():
        return "REBASING"
    if (git_path / "CHERRY_PICK_HEAD").exists():
        return "CHERRY-PICKING"
    if (git_path / "BISECT_LOG").exists():
        return "BISECTING"
    if (git_path / "REVERT_HEAD").exists():
        return "REVERTING"
    return ""


def get_git_info(
    cwd: str,
    icons: Mapping[str, str],
    config: ConfigDict | None = None,
) -> str:
    """Get git branch and status."""
    if config is None:
        config = {}

    git_dir = run_cmd(["git", "-C", cwd, "rev-parse", "--git-dir"])
    if not git_dir:
        return ""

    if not git_dir.startswith("/"):
        git_dir = str(Path(cwd) / git_dir)

    branch = run_cmd(["git", "-C", cwd, "branch", "--show-current"])
    if not branch:
        branch = run_cmd(["git", "-C", cwd, "rev-parse", "--short", "HEAD"])[:7]
        if not branch:
            return ""

    status = GitStatus(branch=branch)

    porcelain = run_cmd(
        ["git", "-C", cwd, "status", "--porcelain", "--untracked-files=normal"]
    )
    for line in porcelain.splitlines():
        if line.startswith("?? "):
            status.untracked += 1
        elif len(line) >= 2:
            xy = line[:2]
            if xy in ("UU", "AA", "DD", "AU", "UA", "DU", "UD"):
                status.conflicts += 1
            else:
                if line[0] != " ":
                    status.staged += 1
                if line[1] != " ":
                    status.modified += 1

    stash = run_cmd(["git", "-C", cwd, "stash", "list"])
    status.stashed = len(stash.splitlines()) if stash else 0

    upstream = run_cmd(
        [
            "git",
            "-C",
            cwd,
            "rev-parse",
            "--abbrev-ref",
            "--symbolic-full-name",
            "@{u}",
        ]
    )
    if upstream:
        counts = run_cmd(
            ["git", "-C", cwd, "rev-list", "--left-right", "--count", "HEAD...@{u}"]
        )
        if counts and "\t" in counts:
            behind, ahead = counts.split("\t")
            status.ahead = int(ahead) if ahead.isdigit() else 0
            status.behind = int(behind) if behind.isdigit() else 0

    common_dir = run_cmd(["git", "-C", cwd, "rev-parse", "--git-common-dir"])
    if common_dir and common_dir != git_dir and common_dir != ".git":
        status.worktree = True

    timestamp = run_cmd(["git", "-C", cwd, "log", "-1", "--format=%ct"])
    if timestamp and timestamp.isdigit():
        status.last_commit_age = format_time_ago(int(timestamp))

    if config.get("git_show_state", True):
        status.state = get_git_state(git_dir)

    if config.get("git_show_tag", False):
        status.tag = run_cmd(
            ["git", "-C", cwd, "describe", "--tags", "--exact-match", "HEAD"]
        )

    if config.get("git_show_assume_unchanged", False):
        ls_files = run_cmd(["git", "-C", cwd, "ls-files", "-v"])
        status.assume_unchanged = sum(
            1 for line in ls_files.splitlines() if line.startswith("h ")
        )

    if config.get("git_show_submodules", False):
        submodule_status = run_cmd(["git", "-C", cwd, "submodule", "status"])
        status.dirty_submodules = sum(
            1 for line in submodule_status.splitlines() if line.startswith("+")
        )

    parts = [f"{C.B_BLU}{icons.get('git', '')} {branch}"]

    if status.state:
        parts.append(f"{C.B_RED}{icons.get('state', '⚡')}{status.state}{C.NC}")

    if status.conflicts and config.get("git_show_conflicts", True):
        parts.append(
            f"{C.B_RED}{icons.get('conflict', '✖')}{status.conflicts}{C.NC}"
        )

    if status.worktree:
        parts.append(f"{C.B_CYA}{icons.get('worktree', '⊕')}{C.NC}")

    if status.tag:
        parts.append(f"{C.B_YEL}{icons.get('tag', '')} {status.tag}{C.NC}")

    if status.stashed:
        parts.append(f"{C.B_MAG}*{status.stashed}")
    if status.modified:
        parts.append(f"{C.B_YEL}!{status.modified}")
    if status.staged:
        parts.append(f"{C.B_CYA}+{status.staged}")
    if status.untracked:
        parts.append(f"{C.B_BLU}?{status.untracked}")
    if status.ahead:
        parts.append(f"{C.B_GRE}⇡{status.ahead}")
    if status.behind:
        parts.append(f"{C.B_RED}⇣{status.behind}")

    if status.assume_unchanged:
        parts.append(f"{C.WHI}≡{status.assume_unchanged}")
    if status.dirty_submodules:
        parts.append(f"{C.B_YEL}◌{status.dirty_submodules}")

    if status.last_commit_age:
        parts.append(f"{C.WHI}{icons.get('time', '◷')}{status.last_commit_age}{C.NC}")

    return " ".join(parts) + C.NC


# =========================================================================
# Context Providers
# =========================================================================
def get_kube_context(icons: Mapping[str, str]) -> str:
    """Get current kubectl context."""
    ctx = run_cmd(["kubectx", "-c"]) or run_cmd(
        ["kubectl", "config", "current-context"]
    )
    return f"{C.MAG}{icons.get('kube', '')} {ctx}{C.NC}" if ctx else ""


def get_aws_info(icons: Mapping[str, str]) -> str:
    """Get AWS profile/region from environment."""
    profile = os.environ.get("AWS_PROFILE", "")
    region = os.environ.get("AWS_REGION", "")
    if not profile and not region:
        return ""
    info = " ".join(filter(None, [profile, region]))
    return f"{C.YEL}{icons.get('aws', '')} {info}{C.NC}"


def get_docker_context(icons: Mapping[str, str]) -> str:
    """Get current Docker context."""
    ctx = run_cmd(["docker", "context", "show"])
    if ctx and ctx != "default":
        return f"{C.B_BLU}{icons.get('docker', '')} {ctx}{C.NC}"
    return ""


def get_venv_info(icons: Mapping[str, str]) -> str:
    """Get Python virtual environment name."""
    venv = os.environ.get("VIRTUAL_ENV", "")
    if venv:
        name = Path(venv).name
        return f"{C.B_YEL}{icons.get('python', '')} {name}{C.NC}"
    return ""


def get_node_version(icons: Mapping[str, str]) -> str:
    """Get Node.js version if in a node project."""
    if Path("package.json").exists():
        version = run_cmd(["node", "--version"])
        if version:
            return f"{C.B_GRE}{icons.get('node', '')} {version}{C.NC}"
    return ""


def get_claude_version() -> str:
    """Get Claude CLI version."""
    output = run_cmd(["claude", "--version"])
    return f"v{output.split()[0]}" if output else ""


# =========================================================================
# Status Data
# =========================================================================
@dataclass
class StatusData:
    """Collected status information."""

    cwd: str = ""
    git: str = ""
    tokens_pct: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    lines_added: int = 0
    lines_removed: int = 0
    cost_usd: float = 0.0
    session_time: str = "00:00"
    model: str = ""
    version: str = ""
    kube: str = ""
    aws: str = ""
    docker: str = ""
    venv: str = ""
    node: str = ""


# =========================================================================
# Formatters
# =========================================================================
def _get_icons(config: ConfigDict) -> IconMap:
    icons = config.get("icons")
    if isinstance(icons, dict):
        return {str(k): str(v) for k, v in icons.items()}
    return {}


def format_default(data: StatusData, config: ConfigDict) -> str:
    """Default multi-line format."""
    sep = str(config.get("separator", " | "))
    icons = _get_icons(config)

    lines = []

    line1 = [f"{C.B_CYA}{icons.get('dir', '')} {shorten_path(data.cwd)}{C.NC}"]
    if data.git:
        line1.append(data.git)
    for ctx in [data.venv, data.kube, data.aws, data.docker, data.node]:
        if ctx:
            line1.append(ctx)
    lines.append(sep.join(line1))

    tokens = f"{C.B_MAG}{icons.get('tokens', '')} {data.tokens_pct}%{C.NC}"
    in_out = (
        f"{C.B_BLU}{icons.get('in_tokens', '󰜮')} {data.input_tokens} "
        f"{C.B_YEL}{icons.get('out_tokens', '󰜷')} {data.output_tokens}{C.NC}"
    )
    changes = (
        f"{C.B_GRE}{icons.get('added', '')} {data.lines_added} "
        f"{C.B_RED}{icons.get('removed', '')} {data.lines_removed}{C.NC}"
    )
    cost = f"{C.GRE}${data.cost_usd:.2f}{C.NC}"
    lines.append(sep.join([tokens, in_out, changes, cost]))

    model = f"{C.B_BLU}{icons.get('model', '')} {data.model}{C.NC}"
    lines.append(sep.join([model, data.version]))

    return "\n".join(lines)


def format_oneline(data: StatusData, config: ConfigDict) -> str:
    """Single line for tmux/i3bar."""
    sep = str(config.get("separator", " | "))
    parts = [
        shorten_path(data.cwd),
        f"{data.tokens_pct}%",
        f"↓{data.input_tokens} ↑{data.output_tokens}",
        f"+{data.lines_added}/-{data.lines_removed}",
        f"${data.cost_usd:.2f}",
    ]
    return sep.join(parts)


def format_json(data: StatusData, _config: ConfigDict) -> str:
    """JSON output for scripting."""
    return json.dumps(
        {
            "cwd": data.cwd,
            "tokens_pct": data.tokens_pct,
            "input_tokens": data.input_tokens,
            "output_tokens": data.output_tokens,
            "lines_added": data.lines_added,
            "lines_removed": data.lines_removed,
            "cost_usd": data.cost_usd,
            "session_time": data.session_time,
            "model": data.model,
            "version": data.version,
        },
        indent=2,
    )


FORMATTERS: Dict[str, Callable[[StatusData, ConfigDict], str]] = {
    "default": format_default,
    "oneline": format_oneline,
    "json": format_json,
}


# =========================================================================
# CLI helpers
# =========================================================================
def add_statusline_arguments(parser: argparse.ArgumentParser) -> None:
    """Add statusline arguments to an argparse parser."""
    parser.add_argument("-f", "--format", choices=FORMATTERS.keys(), default="default")
    parser.add_argument("--color", action="store_true", help="Force colors on")
    parser.add_argument("--no-color", action="store_true", help="Disable colors")

    for name in ["git", "kube", "aws", "docker", "venv", "node"]:
        parser.add_argument(
            f"--{name}", action="store_true", dest=f"show_{name}", default=None
        )
        parser.add_argument(
            f"--no-{name}", action="store_false", dest=f"show_{name}"
        )

    parser.add_argument(
        "--init-config", action="store_true", help=f"Create config at {CONFIG_PATH}"
    )


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Claude Code status line")
    add_statusline_arguments(parser)
    return parser.parse_args(list(argv) if argv is not None else None)


def _apply_cli_overrides(config: ConfigDict, args: argparse.Namespace) -> None:
    for key in [
        "show_git",
        "show_kube",
        "show_aws",
        "show_docker",
        "show_venv",
        "show_node",
    ]:
        if getattr(args, key, None) is not None:
            config[key] = getattr(args, key)


def _configure_colors(args: argparse.Namespace, stdout: TextIO) -> None:
    if getattr(args, "no_color", False):
        C.disable()
    elif not getattr(args, "color", False) and not stdout.isatty():
        C.disable()


def _read_claude_data(stdin: TextIO) -> Dict[str, Any]:
    try:
        data = json.load(stdin)
        if isinstance(data, dict):
            return cast(Dict[str, Any], data)
        return {}
    except json.JSONDecodeError:
        return {}


def _build_status_data(claude_data: Dict[str, Any], config: ConfigDict) -> StatusData:
    cwd = claude_data.get("workspace", {}).get("current_dir", os.getcwd())
    ctx = claude_data.get("context_window", {})
    context_size = ctx.get("context_window_size", 1)

    usage = ctx.get("current_usage")
    if usage:
        current = sum(
            [
                usage.get("input_tokens", 0),
                usage.get("cache_creation_input_tokens", 0),
                usage.get("cache_read_input_tokens", 0),
            ]
        )
        tokens_pct = (current * 100) // context_size if context_size else 0
    else:
        tokens_pct = 0

    cost = claude_data.get("cost", {})

    data = StatusData(
        cwd=cwd,
        tokens_pct=tokens_pct,
        input_tokens=ctx.get("total_input_tokens", 0),
        output_tokens=ctx.get("total_output_tokens", 0),
        lines_added=cost.get("total_lines_added", 0),
        lines_removed=cost.get("total_lines_removed", 0),
        cost_usd=cost.get("total_cost_usd", 0.0),
        session_time=ms_to_hhmmss(claude_data.get("session_duration_ms", 0)),
        model=claude_data.get("model", {}).get("display_name", ""),
        version=get_claude_version(),
    )

    icons = _get_icons(config)

    with ThreadPoolExecutor(max_workers=6) as ex:
        futures = {}
        if config.get("show_git"):
            futures["git"] = ex.submit(get_git_info, cwd, icons, config)
        if config.get("show_kube"):
            futures["kube"] = ex.submit(get_kube_context, icons)
        if config.get("show_aws"):
            futures["aws"] = ex.submit(get_aws_info, icons)
        if config.get("show_docker"):
            futures["docker"] = ex.submit(get_docker_context, icons)
        if config.get("show_venv"):
            futures["venv"] = ex.submit(get_venv_info, icons)
        if config.get("show_node"):
            futures["node"] = ex.submit(get_node_version, icons)

        for key, fut in futures.items():
            try:
                setattr(data, key, fut.result(timeout=3))
            except Exception:
                pass

    return data


def render_statusline(
    args: argparse.Namespace,
    stdin: TextIO | None = None,
    stdout: TextIO | None = None,
) -> int:
    """Render status line based on parsed args and stdin data."""
    stdin = stdin or sys.stdin
    stdout = stdout or sys.stdout
    config = load_config()

    if getattr(args, "init_config", False):
        save_config(DEFAULT_CONFIG)
        stdout.write(f"Created {CONFIG_PATH}\n")
        return 0

    _apply_cli_overrides(config, args)
    _configure_colors(args, stdout)

    claude_data = _read_claude_data(stdin)
    data = _build_status_data(claude_data, config)
    output = FORMATTERS[args.format](data, config)
    if not output.endswith("\n"):
        output += "\n"
    stdout.write(output)
    return 0


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    return render_statusline(args)


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
