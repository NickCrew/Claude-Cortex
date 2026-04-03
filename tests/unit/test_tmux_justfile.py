"""Unit tests for claude_ctx_py.tmux.justfile (Justfile generation)."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from claude_ctx_py.cli import build_parser
from claude_ctx_py.cmd_tmux import handle_tmux_command
from claude_ctx_py.tmux.justfile import (
    ProjectInfo,
    Service,
    _detect_framework,
    _detect_pkg_manager,
    _detect_services_node,
    _detect_services_nx,
    _run_cmd,
    _safe_window_name,
    detect_project,
    generate_justfile,
    tmux_justfile,
)

_TMUX = "claude_ctx_py.tmux"


def _parse(args: list[str]):
    return build_parser().parse_args(args)


# ── Helper unit tests ───────────────────────────────────────────────


@pytest.mark.unit
class TestSafeWindowName:
    def test_colons(self):
        assert _safe_window_name("dev:server") == "dev-server"

    def test_spaces(self):
        assert _safe_window_name("my app") == "my-app"

    def test_underscores(self):
        assert _safe_window_name("build_watch") == "build-watch"

    def test_passthrough(self):
        assert _safe_window_name("dev") == "dev"


@pytest.mark.unit
class TestRunCmd:
    def test_pnpm(self):
        assert _run_cmd("pnpm", "dev") == "pnpm dev"

    def test_yarn(self):
        assert _run_cmd("yarn", "serve") == "yarn serve"

    def test_npm(self):
        assert _run_cmd("npm", "dev") == "npm run dev"

    def test_bun(self):
        assert _run_cmd("bun", "dev") == "bun run dev"


# ── Detection tests ─────────────────────────────────────────────────


@pytest.mark.unit
class TestDetectPkgManager:
    def test_pnpm(self, tmp_path: Path):
        (tmp_path / "pnpm-lock.yaml").touch()
        assert _detect_pkg_manager(tmp_path) == "pnpm"

    def test_yarn(self, tmp_path: Path):
        (tmp_path / "yarn.lock").touch()
        assert _detect_pkg_manager(tmp_path) == "yarn"

    def test_bun(self, tmp_path: Path):
        (tmp_path / "bun.lockb").touch()
        assert _detect_pkg_manager(tmp_path) == "bun"

    def test_npm_default(self, tmp_path: Path):
        assert _detect_pkg_manager(tmp_path) == "npm"

    def test_pnpm_priority(self, tmp_path: Path):
        """pnpm wins when multiple lock files exist."""
        (tmp_path / "pnpm-lock.yaml").touch()
        (tmp_path / "yarn.lock").touch()
        assert _detect_pkg_manager(tmp_path) == "pnpm"


@pytest.mark.unit
class TestDetectFramework:
    def test_vite_ts(self, tmp_path: Path):
        (tmp_path / "vite.config.ts").touch()
        assert _detect_framework(tmp_path) == "vite"

    def test_vite_js(self, tmp_path: Path):
        (tmp_path / "vite.config.js").touch()
        assert _detect_framework(tmp_path) == "vite"

    def test_next(self, tmp_path: Path):
        (tmp_path / "next.config.mjs").touch()
        assert _detect_framework(tmp_path) == "next"

    def test_angular(self, tmp_path: Path):
        (tmp_path / "angular.json").touch()
        assert _detect_framework(tmp_path) == "angular"

    def test_none(self, tmp_path: Path):
        assert _detect_framework(tmp_path) == ""


@pytest.mark.unit
class TestDetectServicesNode:
    def test_dev_script(self, tmp_path: Path):
        pkg = {"scripts": {"dev": "vite", "build": "vite build"}}
        (tmp_path / "package.json").write_text(json.dumps(pkg))
        services = _detect_services_node(tmp_path, "pnpm")
        assert len(services) == 1
        assert services[0].name == "dev"
        assert services[0].command == "pnpm dev"

    def test_multiple_scripts(self, tmp_path: Path):
        pkg = {"scripts": {"dev": "vite", "proxy": "node proxy.js"}}
        (tmp_path / "package.json").write_text(json.dumps(pkg))
        services = _detect_services_node(tmp_path, "npm")
        names = {s.name for s in services}
        assert "dev" in names
        assert "proxy" in names

    def test_no_service_scripts(self, tmp_path: Path):
        pkg = {"scripts": {"build": "tsc", "lint": "eslint ."}}
        (tmp_path / "package.json").write_text(json.dumps(pkg))
        services = _detect_services_node(tmp_path, "pnpm")
        assert services == []

    def test_colon_scripts(self, tmp_path: Path):
        pkg = {"scripts": {"dev:server": "node server.js"}}
        (tmp_path / "package.json").write_text(json.dumps(pkg))
        services = _detect_services_node(tmp_path, "yarn")
        assert services[0].name == "dev-server"
        assert services[0].command == "yarn dev:server"

    def test_no_package_json(self, tmp_path: Path):
        assert _detect_services_node(tmp_path, "npm") == []

    def test_invalid_json(self, tmp_path: Path):
        (tmp_path / "package.json").write_text("{broken")
        assert _detect_services_node(tmp_path, "npm") == []


@pytest.mark.unit
class TestDetectServicesNx:
    def test_serve_target(self, tmp_path: Path):
        app_dir = tmp_path / "apps" / "web"
        app_dir.mkdir(parents=True)
        pj = {"name": "web", "targets": {"serve": {"executor": "@nx/vite:dev-server"}}}
        (app_dir / "project.json").write_text(json.dumps(pj))
        services = _detect_services_nx(tmp_path, "pnpm")
        assert len(services) == 1
        assert services[0].name == "web"
        assert "nx serve web" in services[0].command

    def test_dev_target(self, tmp_path: Path):
        app_dir = tmp_path / "apps" / "api"
        app_dir.mkdir(parents=True)
        pj = {"name": "api", "targets": {"dev": {"executor": "nx:run-commands"}}}
        (app_dir / "project.json").write_text(json.dumps(pj))
        services = _detect_services_nx(tmp_path, "npm")
        assert services[0].command == "npx nx dev api"

    def test_serve_preferred_over_dev(self, tmp_path: Path):
        """When a project has both serve and dev, only serve is used."""
        app_dir = tmp_path / "apps" / "ui"
        app_dir.mkdir(parents=True)
        pj = {
            "name": "ui",
            "targets": {
                "serve": {"executor": "exec"},
                "dev": {"executor": "exec"},
            },
        }
        (app_dir / "project.json").write_text(json.dumps(pj))
        services = _detect_services_nx(tmp_path, "pnpm")
        assert len(services) == 1
        assert "serve" in services[0].command

    def test_deduplication(self, tmp_path: Path):
        """Same project name from apps/ and packages/ is not duplicated."""
        for parent in ("apps", "packages"):
            d = tmp_path / parent / "shared"
            d.mkdir(parents=True)
            pj = {"name": "shared", "targets": {"serve": {}}}
            (d / "project.json").write_text(json.dumps(pj))
        services = _detect_services_nx(tmp_path, "npm")
        assert len(services) == 1

    def test_no_project_files(self, tmp_path: Path):
        assert _detect_services_nx(tmp_path, "npm") == []


# ── Project detection (integration) ─────────────────────────────────


@pytest.mark.unit
class TestDetectProject:
    def test_node_pnpm_vite(self, tmp_path: Path):
        (tmp_path / "pnpm-lock.yaml").touch()
        (tmp_path / "vite.config.ts").touch()
        pkg = {"scripts": {"dev": "vite", "proxy": "node proxy.js"}}
        (tmp_path / "package.json").write_text(json.dumps(pkg))
        info = detect_project(str(tmp_path))
        assert info.pkg_manager == "pnpm"
        assert info.framework == "vite"
        assert len(info.services) == 2

    def test_nx_workspace(self, tmp_path: Path):
        (tmp_path / "package.json").write_text("{}")
        (tmp_path / "nx.json").write_text("{}")
        app_dir = tmp_path / "apps" / "web"
        app_dir.mkdir(parents=True)
        pj = {"name": "web", "targets": {"serve": {}}}
        (app_dir / "project.json").write_text(json.dumps(pj))
        info = detect_project(str(tmp_path))
        assert len(info.services) == 1
        assert info.services[0].name == "web"

    def test_python_project(self, tmp_path: Path):
        (tmp_path / "pyproject.toml").touch()
        info = detect_project(str(tmp_path))
        assert info.pkg_manager == "python"
        # Falls back to placeholder service
        assert len(info.services) == 1
        assert info.services[0].name == "app"

    def test_rust_project(self, tmp_path: Path):
        (tmp_path / "Cargo.toml").touch()
        info = detect_project(str(tmp_path))
        assert info.pkg_manager == "cargo"

    def test_go_project(self, tmp_path: Path):
        (tmp_path / "go.mod").touch()
        info = detect_project(str(tmp_path))
        assert info.pkg_manager == "go"

    def test_empty_dir_gets_placeholder(self, tmp_path: Path):
        info = detect_project(str(tmp_path))
        assert len(info.services) == 1
        assert info.services[0].name == "app"
        assert "TODO" in info.services[0].command

    def test_session_name_from_dir(self, tmp_path: Path):
        project = tmp_path / "My Cool App"
        project.mkdir()
        info = detect_project(str(project))
        assert info.name == "my-cool-app"


# ── Justfile generation ─────────────────────────────────────────────


@pytest.mark.unit
class TestGenerateJustfile:
    def _project(self, **kwargs):
        defaults = {
            "name": "my-app",
            "pkg_manager": "pnpm",
            "framework": "vite",
            "services": [
                Service(name="dev", label="Dev server", command="pnpm dev"),
                Service(name="proxy", label="Local proxy", command="pnpm proxy"),
            ],
        }
        defaults.update(kwargs)
        return ProjectInfo(**defaults)

    def test_header(self):
        out = generate_justfile(self._project())
        assert "cortex tmux justfile" in out
        assert "pnpm + vite" in out

    def test_session_variable(self):
        out = generate_justfile(self._project())
        assert 'env_var_or_default("TMUX_SESSION", "my-app")' in out

    def test_init_recipe(self):
        out = generate_justfile(self._project())
        assert "_svc-init:" in out
        assert "tmux has-session" in out
        assert "tmux new-session -d" in out

    def test_service_targets(self):
        out = generate_justfile(self._project())
        assert "svc-dev: _svc-init" in out
        assert "svc-proxy: _svc-init" in out
        assert "_svc_session" in out
        assert "_svc_cortex" in out
        assert 'send dev "pnpm dev"' in out
        assert 'send proxy "pnpm proxy"' in out

    def test_up_depends_on_services(self):
        out = generate_justfile(self._project())
        assert "svc-up: svc-dev svc-proxy" in out

    def test_status_target(self):
        out = generate_justfile(self._project())
        assert "svc-status:" in out
        assert "status dev" in out
        assert "status proxy" in out

    def test_stop_target(self):
        out = generate_justfile(self._project())
        assert "svc-stop:" in out
        assert "kill dev" in out
        assert "kill proxy" in out

    def test_restart_targets(self):
        out = generate_justfile(self._project())
        assert "svc-restart-dev:" in out
        assert "svc-restart-proxy:" in out
        assert "interrupt dev" in out
        assert "wait dev 5" in out

    def test_restart_all(self):
        out = generate_justfile(self._project())
        assert "svc-restart: svc-stop svc-up" in out

    def test_shell_target(self):
        out = generate_justfile(self._project())
        assert "svc-shell:" in out
        assert "tmux attach-session" in out

    def test_reset_target(self):
        out = generate_justfile(self._project())
        assert "svc-reset:" in out
        assert "tmux kill-session" in out
        assert "tmux new-session -d" in out

    def test_custom_prefix(self):
        out = generate_justfile(self._project(), prefix="app")
        assert "app-dev:" in out
        assert "app-up:" in out
        assert "app-stop:" in out
        assert "_app-init:" in out
        assert "_app_session" in out
        assert "_app_cortex" in out
        # No user-facing targets should use the default prefix
        assert "svc-dev" not in out
        assert "svc-up" not in out

    def test_single_service(self):
        proj = self._project(
            services=[Service(name="app", label="Application", command="pnpm dev")]
        )
        out = generate_justfile(proj)
        assert "svc-up: svc-app" in out
        assert "svc-restart-app:" in out

    def test_no_framework(self):
        proj = self._project(framework="")
        out = generate_justfile(proj)
        assert "Detected: pnpm" in out
        assert "+" not in out.splitlines()[2]


# ── Entry point ─────────────────────────────────────────────────────


@pytest.mark.unit
class TestTmuxJustfile:
    def test_returns_success(self, tmp_path: Path):
        (tmp_path / "package.json").write_text(
            json.dumps({"scripts": {"dev": "vite"}})
        )
        (tmp_path / "pnpm-lock.yaml").touch()
        code, content = tmux_justfile(directory=str(tmp_path))
        assert code == 0
        assert "svc-dev" in content
        assert "pnpm dev" in content


# ── CLI parsing and dispatch ────────────────────────────────────────


@pytest.mark.unit
class TestJustfileParsing:
    def test_defaults(self):
        ns = _parse(["tmux", "justfile"])
        assert ns.tmux_command == "justfile"
        assert ns.dir is None
        assert ns.prefix == "svc"

    def test_custom_dir(self):
        ns = _parse(["tmux", "justfile", "--dir", "/some/path"])
        assert ns.dir == "/some/path"

    def test_custom_prefix(self):
        ns = _parse(["tmux", "justfile", "--prefix", "app"])
        assert ns.prefix == "app"

    def test_short_flags(self):
        ns = _parse(["tmux", "justfile", "-d", "/path", "-p", "svc"])
        assert ns.dir == "/path"
        assert ns.prefix == "svc"


@pytest.mark.unit
class TestJustfileDispatch:
    @patch(f"{_TMUX}.tmux_justfile", return_value=(0, "# justfile content"))
    def test_dispatch(self, mock_fn):
        code = handle_tmux_command(_parse(["tmux", "justfile"]))
        assert code == 0
        mock_fn.assert_called_once_with(directory=None, prefix="svc")

    @patch(f"{_TMUX}.tmux_justfile", return_value=(0, "# content"))
    def test_dispatch_with_args(self, mock_fn):
        code = handle_tmux_command(
            _parse(["tmux", "justfile", "-d", "/proj", "-p", "app"])
        )
        assert code == 0
        mock_fn.assert_called_once_with(directory="/proj", prefix="app")
