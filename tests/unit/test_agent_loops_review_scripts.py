from __future__ import annotations

import os
import stat
import subprocess
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
SPECIALIST_REVIEW = REPO_ROOT / "skills/agent-loops/scripts/specialist-review.sh"
TEST_REVIEW = REPO_ROOT / "skills/agent-loops/scripts/diff-test-audit.sh"
SYNTHESIZE_REVIEW = (
    REPO_ROOT / "skills/agent-loops/scripts/synthesize-review-artifacts.py"
)
VALIDATE_REVIEW = REPO_ROOT / "skills/agent-loops/scripts/validate-review-contract.py"


def _write_executable(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


def _run(
    args: list[str],
    cwd: Path,
    env: dict[str, str],
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=cwd,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def _run_provider_helper(
    command: str,
    cwd: Path,
    env: dict[str, str],
) -> subprocess.CompletedProcess[str]:
    return _run(
        [
            "bash",
            "-lc",
            f"source '{REPO_ROOT / 'skills/agent-loops/scripts/review-provider.sh'}' && {command}",
        ],
        cwd,
        env,
    )


@pytest.mark.unit
def test_synthesized_test_audit_preserves_primary_metadata_when_args_empty(
    tmp_path: Path,
) -> None:
    primary = tmp_path / "primary.md"
    secondary = tmp_path / "secondary.md"
    output = tmp_path / "synthesized.md"
    primary_text = """## Test Gap Report: primary audit

**Module:** `module/feature.py`
**Tests:** `tests/test_feature.py`
**Mode:** full

### Behavior Inventory

|Behavior|Coverage|Evidence
|----------|----------|----------
| greet(name) returns greeting | Covered | Verified by test_greet

### Prioritized Gaps
_No prioritized gaps._

### Summary
- Covered: 1
- Shallow: 0
- Missing: 0
- P0: 0
- P1: 0
- P2: 0
"""
    primary.write_text(
        primary_text.replace(
            "### Behavior Inventory\n", "### Behavior Inventory   \n"
        ).replace("### Prioritized Gaps\n", "### Prioritized Gaps   \n"),
        encoding="utf-8",
    )

    secondary_text = """## Test Gap Report: secondary audit

**Module:** `module/feature.py`
**Tests:** `tests/test_feature.py`
**Mode:** full

### Behavior Inventory

|Behavior|Coverage|Evidence|
|:---------|:--------:|---------:
| empty name handling | Missing | No assertion covers empty input |

### Prioritized Gaps
- P1: module/feature.py should test empty name handling.

### Summary
- Covered: 0
- Shallow: 0
- Missing: 1
- P0: 0
- P1: 1
- P2: 0
"""
    secondary.write_text(
        secondary_text.replace(
            "### Behavior Inventory\n", "### Behavior Inventory   \n"
        ).replace("### Prioritized Gaps\n", "### Prioritized Gaps   \n"),
        encoding="utf-8",
    )

    result = _run(
        [
            sys.executable,
            str(SYNTHESIZE_REVIEW),
            "test-audit",
            "--primary",
            str(primary),
            "--secondary",
            str(secondary),
            "--primary-provider",
            "gemini",
            "--secondary-provider",
            "codex",
            "--tests",
            "",
        ],
        tmp_path,
        os.environ.copy(),
    )

    assert result.returncode == 0, result.stderr
    output.write_text(result.stdout, encoding="utf-8")
    synthesized = output.read_text(encoding="utf-8")
    assert "**Tests:** `tests/test_feature.py`" in synthesized
    assert "test_greet (gemini)" in synthesized
    assert "|Behavior|Coverage" not in synthesized
    assert ":--------:" not in synthesized

    validation = _run(
        [sys.executable, str(VALIDATE_REVIEW), "test-audit", str(output)],
        tmp_path,
        os.environ.copy(),
    )
    assert validation.returncode == 0, validation.stderr


@pytest.mark.unit
def test_synthesized_test_audit_uses_fallback_rows_for_empty_inventory(
    tmp_path: Path,
) -> None:
    primary = tmp_path / "primary-empty.md"
    secondary = tmp_path / "secondary-empty.md"
    output = tmp_path / "synthesized-empty.md"
    artifact_text = """## Test Gap Report: empty audit

**Module:** `module/feature.py`
**Tests:** `tests/test_feature.py`
**Mode:** full

### Behavior Inventory

| Behavior | Coverage | Evidence |
|----------|----------|----------|

### Prioritized Gaps
_No prioritized gaps._

### Summary
- Covered: 0
- Shallow: 0
- Missing: 0
- P0: 0
- P1: 0
- P2: 0
"""
    primary.write_text(artifact_text, encoding="utf-8")
    secondary.write_text(artifact_text, encoding="utf-8")

    result = _run(
        [
            sys.executable,
            str(SYNTHESIZE_REVIEW),
            "test-audit",
            "--primary",
            str(primary),
            "--secondary",
            str(secondary),
            "--primary-provider",
            "gemini",
            "--secondary-provider",
            "codex",
        ],
        tmp_path,
        os.environ.copy(),
    )

    assert result.returncode == 0, result.stderr
    output.write_text(result.stdout, encoding="utf-8")
    synthesized = output.read_text(encoding="utf-8")
    assert "| Primary audit artifact | Covered |" in synthesized
    assert "| Secondary audit artifact | Covered |" in synthesized

    validation = _run(
        [sys.executable, str(VALIDATE_REVIEW), "test-audit", str(output)],
        tmp_path,
        os.environ.copy(),
    )
    assert validation.returncode == 0, validation.stderr


@pytest.mark.unit
def test_synthesized_code_review_escalates_blocked_verdict(tmp_path: Path) -> None:
    primary = tmp_path / "primary.md"
    secondary = tmp_path / "secondary.md"
    output = tmp_path / "synthesized.md"
    primary.write_text(
        """## Code Review: primary review

**Files reviewed:** src/app.py
**Iteration:** 1 of 3

### Findings
_No findings._

### Summary
- P0: 0 findings (MUST fix)
- P1: 0 findings (MUST fix)
- P2: 0 findings (file issues)
- P3: 0 findings (file issues)
- **Verdict:** CLEAN
""",
        encoding="utf-8",
    )
    secondary.write_text(
        """## Code Review: secondary review

**Files reviewed:** src/app.py
**Iteration:** 1 of 3

### Findings
- P1: src/app.py:1 should not regress critical behavior.

### Summary
- P0: 0 findings (MUST fix)
- P1: 1 findings (MUST fix)
- P2: 0 findings (file issues)
- P3: 0 findings (file issues)
- **Verdict:** BLOCKED
""",
        encoding="utf-8",
    )

    result = _run(
        [
            sys.executable,
            str(SYNTHESIZE_REVIEW),
            "code-review",
            "--primary",
            str(primary),
            "--secondary",
            str(secondary),
            "--primary-provider",
            "gemini",
            "--secondary-provider",
            "codex",
        ],
        tmp_path,
        os.environ.copy(),
    )

    assert result.returncode == 0, result.stderr
    output.write_text(result.stdout, encoding="utf-8")
    synthesized = output.read_text(encoding="utf-8")
    assert "- P1: 1 findings (MUST fix)" in synthesized
    assert "- **Verdict:** BLOCKED" in synthesized

    validation = _run(
        [sys.executable, str(VALIDATE_REVIEW), "code-review", str(output)],
        tmp_path,
        os.environ.copy(),
    )
    assert validation.returncode == 0, validation.stderr


@pytest.mark.unit
def test_review_provider_detect_self_uses_gemini_cli_env_markers(
    tmp_path: Path,
) -> None:
    env = os.environ.copy()
    env["GEMINI_CLI_NO_RELAUNCH"] = "true"
    env.pop("AGENT_LOOPS_SELF_PROVIDER", None)
    env.pop("CODEX_THREAD_ID", None)
    env.pop("CODEX_MANAGED_BY_NPM", None)
    env.pop("CLAUDECODE", None)

    result = _run_provider_helper("review_provider_detect_self", tmp_path, env)

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "gemini"


@pytest.mark.unit
def test_review_provider_detect_self_uses_codex_cli_env_markers(
    tmp_path: Path,
) -> None:
    env = os.environ.copy()
    env["CODEX_THREAD_ID"] = "thread-123"
    env.pop("AGENT_LOOPS_SELF_PROVIDER", None)
    env.pop("CODEX_MANAGED_BY_NPM", None)
    env.pop("GEMINI_CLI_NO_RELAUNCH", None)
    env.pop("GEMINI_CLI_ACTIVITY_LOG_TARGET", None)
    env.pop("CLAUDECODE", None)

    result = _run_provider_helper("review_provider_detect_self", tmp_path, env)

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "codex"


@pytest.mark.unit
def test_review_provider_detect_self_uses_claude_cli_env_markers(
    tmp_path: Path,
) -> None:
    env = os.environ.copy()
    env["CLAUDECODE"] = "1"
    env.pop("AGENT_LOOPS_SELF_PROVIDER", None)
    env.pop("CODEX_THREAD_ID", None)
    env.pop("CODEX_MANAGED_BY_NPM", None)
    env.pop("GEMINI_CLI_NO_RELAUNCH", None)
    env.pop("GEMINI_CLI_ACTIVITY_LOG_TARGET", None)

    result = _run_provider_helper("review_provider_detect_self", tmp_path, env)

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "claude"


@pytest.mark.unit
def test_review_provider_run_honors_gemini_model_env(tmp_path: Path) -> None:
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    gemini_log = tmp_path / "gemini.log"
    prompt = tmp_path / "prompt.md"
    output = tmp_path / "output.md"
    stderr_log = tmp_path / "stderr.log"
    prompt.write_text("review this\n", encoding="utf-8")

    _write_executable(
        fake_bin / "gemini",
        f"""#!/usr/bin/env bash
echo "$@" > "{gemini_log}"
echo "gemini output"
""",
    )

    env = os.environ.copy()
    env["PATH"] = f"{fake_bin}:{env['PATH']}"
    env["GEMINI_MODEL"] = "gemini-test"

    result = _run_provider_helper(
        f"PATH='{fake_bin}':\"$PATH\"; review_provider_run gemini '{prompt}' '{output}' '{stderr_log}' 5",
        tmp_path,
        env,
    )

    assert result.returncode == 0, result.stderr
    assert "--model gemini-test" in gemini_log.read_text(encoding="utf-8")


@pytest.mark.unit
def test_review_provider_run_honors_codex_model_env(tmp_path: Path) -> None:
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    codex_log = tmp_path / "codex.log"
    prompt = tmp_path / "prompt.md"
    output = tmp_path / "output.md"
    stderr_log = tmp_path / "stderr.log"
    prompt.write_text("review this\n", encoding="utf-8")

    _write_executable(
        fake_bin / "codex",
        f"""#!/usr/bin/env bash
echo "$@" > "{codex_log}"
out_file=""
prev=""
for arg in "$@"; do
  if [[ "$prev" == "-o" ]]; then
    out_file="$arg"
  fi
  prev="$arg"
done
echo "codex output" > "$out_file"
""",
    )

    env = os.environ.copy()
    env["PATH"] = f"{fake_bin}:{env['PATH']}"
    env["CODEX_MODEL"] = "codex-test"

    result = _run_provider_helper(
        f"PATH='{fake_bin}':\"$PATH\"; review_provider_run codex '{prompt}' '{output}' '{stderr_log}' 5",
        tmp_path,
        env,
    )

    assert result.returncode == 0, result.stderr
    assert "-m codex-test" in codex_log.read_text(encoding="utf-8")


@pytest.mark.unit
def test_specialist_review_falls_back_to_gemini_when_claude_fails(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    _run(["git", "init"], repo, os.environ.copy())
    _run(["git", "config", "user.email", "test@example.com"], repo, os.environ.copy())
    _run(["git", "config", "user.name", "Test User"], repo, os.environ.copy())

    src_dir = repo / "src"
    src_dir.mkdir()
    source_file = src_dir / "app.py"
    source_file.write_text("print('before')\n", encoding="utf-8")
    _run(["git", "add", "src/app.py"], repo, os.environ.copy())
    _run(["git", "commit", "-m", "init"], repo, os.environ.copy())
    source_file.write_text("print('after')\n", encoding="utf-8")

    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    claude_log = tmp_path / "claude.log"
    gemini_log = tmp_path / "gemini.log"

    _write_executable(
        fake_bin / "claude",
        f"""#!/usr/bin/env bash
# Handle auth status probe (added by keychain auth fix)
if [[ "$1" == "auth" && "$2" == "status" ]]; then
  echo '{{"loggedIn": true}}'
  exit 0
fi
echo "$@" > "{claude_log}"
echo "claude failed intentionally" >&2
exit 1
""",
    )
    _write_executable(
        fake_bin / "gemini",
        f"""#!/usr/bin/env bash
echo "$@" > "{gemini_log}"
cat >/dev/null
cat <<'EOF'
## Code Review: fallback review

**Files reviewed:** [src/app.py]
**Iteration:** 1 of 3

### Findings

### Summary
- P0: 0 findings (MUST fix)
- P1: 0 findings (MUST fix)
- P2: 0 findings (file issues)
- P3: 0 findings (file issues)
- **Verdict:** CLEAN
EOF
""",
    )

    env = os.environ.copy()
    env["PATH"] = f"{fake_bin}:{env['PATH']}"
    env["PYTHONPATH"] = str(REPO_ROOT)
    # Pin self provider so the auto order is deterministic regardless of
    # whichever CLI env markers leaked in from os.environ (CLAUDECODE,
    # CODEX_THREAD_ID, GEMINI_CLI_*). With self=codex, the order becomes
    # claude, gemini, codex — claude is tried first (fails as designed),
    # gemini is the fallback (succeeds), matching this test's intent.
    env["AGENT_LOOPS_SELF_PROVIDER"] = "codex"

    result = _run(
        [
            str(SPECIALIST_REVIEW),
            "--git",
            "--output",
            str(repo / ".agents/reviews"),
            "--",
            "src/app.py",
        ],
        repo,
        env,
    )

    assert result.returncode == 0, result.stderr
    review_path = Path(result.stdout.strip())
    assert review_path.exists()
    assert "fallback review" in review_path.read_text(encoding="utf-8")
    assert "--print" in claude_log.read_text(encoding="utf-8")

    gemini_args = gemini_log.read_text(encoding="utf-8")
    assert "--approval-mode" in gemini_args
    assert "plan" in gemini_args
    assert "--output-format" in gemini_args
    assert "text" in gemini_args


@pytest.mark.unit
def test_specialist_review_treats_whitespace_only_claude_output_as_empty(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    _run(["git", "init"], repo, os.environ.copy())
    _run(["git", "config", "user.email", "test@example.com"], repo, os.environ.copy())
    _run(["git", "config", "user.name", "Test User"], repo, os.environ.copy())

    src_dir = repo / "src"
    src_dir.mkdir()
    source_file = src_dir / "app.py"
    source_file.write_text("print('before')\n", encoding="utf-8")
    _run(["git", "add", "src/app.py"], repo, os.environ.copy())
    _run(["git", "commit", "-m", "init"], repo, os.environ.copy())
    source_file.write_text("print('after')\n", encoding="utf-8")

    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()

    _write_executable(
        fake_bin / "claude",
        """#!/usr/bin/env bash
if [[ "$1" == "auth" && "$2" == "status" ]]; then
  echo '{"loggedIn": true}'
  exit 0
fi
cat >/dev/null
printf '\\n'
""",
    )
    _write_executable(
        fake_bin / "gemini",
        """#!/usr/bin/env bash
cat >/dev/null
cat <<'EOF'
## Code Review: fallback review

**Files reviewed:** [src/app.py]
**Iteration:** 1 of 3

### Findings

### Summary
- P0: 0 findings (MUST fix)
- P1: 0 findings (MUST fix)
- P2: 0 findings (file issues)
- P3: 0 findings (file issues)
- **Verdict:** CLEAN
EOF
""",
    )

    env = os.environ.copy()
    env["PATH"] = f"{fake_bin}:{env['PATH']}"
    env["PYTHONPATH"] = str(REPO_ROOT)
    env["AGENT_LOOPS_SELF_PROVIDER"] = "codex"

    result = _run(
        [
            str(SPECIALIST_REVIEW),
            "--git",
            "--output",
            str(repo / ".agents/reviews"),
            "--",
            "src/app.py",
        ],
        repo,
        env,
    )

    assert result.returncode == 0, result.stderr
    assert "empty or whitespace-only" in result.stderr
    assert "Invalid output saved to:" not in result.stderr
    assert "Partial output saved to:" not in result.stderr
    assert not list((repo / ".agents/reviews").glob("*.claude.invalid.md"))
    assert not list((repo / ".agents/reviews").glob("*.claude.partial.md"))
    assert "fallback review" in Path(result.stdout.strip()).read_text(encoding="utf-8")


@pytest.mark.unit
def test_specialist_review_auto_keeps_self_provider_last(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    _run(["git", "init"], repo, os.environ.copy())
    _run(["git", "config", "user.email", "test@example.com"], repo, os.environ.copy())
    _run(["git", "config", "user.name", "Test User"], repo, os.environ.copy())

    src_dir = repo / "src"
    src_dir.mkdir()
    source_file = src_dir / "app.py"
    source_file.write_text("print('before')\n", encoding="utf-8")
    _run(["git", "add", "src/app.py"], repo, os.environ.copy())
    _run(["git", "commit", "-m", "init"], repo, os.environ.copy())
    source_file.write_text("print('after')\n", encoding="utf-8")

    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    claude_log = tmp_path / "auto-claude.log"
    codex_log = tmp_path / "codex.log"
    gemini_log = tmp_path / "gemini.log"

    _write_executable(
        fake_bin / "claude",
        f"""#!/usr/bin/env bash
echo "$@" > "{claude_log}"
echo "claude failed intentionally" >&2
exit 1
""",
    )
    _write_executable(
        fake_bin / "codex",
        f"""#!/usr/bin/env bash
echo "$@" > "{codex_log}"
out_file=""
prev=""
for arg in "$@"; do
  if [[ "$prev" == "-o" ]]; then
    out_file="$arg"
  fi
  prev="$arg"
done
cat >/dev/null
cat <<'EOF' > "$out_file"
## Code Review: codex fallback review

**Files reviewed:** src/app.py
**Iteration:** 1 of 3

### Findings
_No findings._

### Summary
- P0: 0 findings (MUST fix)
- P1: 0 findings (MUST fix)
- P2: 0 findings (file issues)
- P3: 0 findings (file issues)
- **Verdict:** CLEAN
EOF
""",
    )
    _write_executable(
        fake_bin / "gemini",
        f"""#!/usr/bin/env bash
echo "$@" > "{gemini_log}"
echo "gemini should not be invoked before codex" >&2
exit 1
""",
    )

    env = os.environ.copy()
    env["PATH"] = f"{fake_bin}:{env['PATH']}"
    env["PYTHONPATH"] = str(REPO_ROOT)
    env["AGENT_LOOPS_SELF_PROVIDER"] = "gemini"

    result = _run(
        [
            str(SPECIALIST_REVIEW),
            "--git",
            "--output",
            str(repo / ".agents/reviews"),
            "--",
            "src/app.py",
        ],
        repo,
        env,
    )

    assert result.returncode == 0, result.stderr
    review_path = Path(result.stdout.strip())
    assert review_path.exists()
    assert "codex fallback review" in review_path.read_text(encoding="utf-8")
    assert claude_log.exists()
    assert codex_log.exists()
    assert not gemini_log.exists()


@pytest.mark.unit
def test_specialist_review_auto_detects_gemini_self_provider_from_cli_env(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    _run(["git", "init"], repo, os.environ.copy())
    _run(["git", "config", "user.email", "test@example.com"], repo, os.environ.copy())
    _run(["git", "config", "user.name", "Test User"], repo, os.environ.copy())

    src_dir = repo / "src"
    src_dir.mkdir()
    source_file = src_dir / "app.py"
    source_file.write_text("print('before')\n", encoding="utf-8")
    _run(["git", "add", "src/app.py"], repo, os.environ.copy())
    _run(["git", "commit", "-m", "init"], repo, os.environ.copy())
    source_file.write_text("print('after')\n", encoding="utf-8")

    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    claude_log = tmp_path / "auto-gemini-env-claude.log"
    codex_log = tmp_path / "auto-gemini-env-codex.log"
    gemini_log = tmp_path / "auto-gemini-env-gemini.log"

    _write_executable(
        fake_bin / "claude",
        f"""#!/usr/bin/env bash
echo "$@" > "{claude_log}"
echo "claude failed intentionally" >&2
exit 1
""",
    )
    _write_executable(
        fake_bin / "codex",
        f"""#!/usr/bin/env bash
echo "$@" > "{codex_log}"
out_file=""
prev=""
for arg in "$@"; do
  if [[ "$prev" == "-o" ]]; then
    out_file="$arg"
  fi
  prev="$arg"
done
cat >/dev/null
cat <<'EOF' > "$out_file"
## Code Review: codex fallback review

**Files reviewed:** src/app.py
**Iteration:** 1 of 3

### Findings
_No findings._

### Summary
- P0: 0 findings (MUST fix)
- P1: 0 findings (MUST fix)
- P2: 0 findings (file issues)
- P3: 0 findings (file issues)
- **Verdict:** CLEAN
EOF
""",
    )
    _write_executable(
        fake_bin / "gemini",
        f"""#!/usr/bin/env bash
echo "$@" > "{gemini_log}"
echo "gemini should not be invoked before codex" >&2
exit 1
""",
    )

    env = os.environ.copy()
    env["PATH"] = f"{fake_bin}:{env['PATH']}"
    env["PYTHONPATH"] = str(REPO_ROOT)
    env.pop("AGENT_LOOPS_SELF_PROVIDER", None)
    env.pop("CODEX_THREAD_ID", None)
    env.pop("CODEX_MANAGED_BY_NPM", None)
    env.pop("CLAUDECODE", None)
    env["GEMINI_CLI_NO_RELAUNCH"] = "true"

    result = _run(
        [
            str(SPECIALIST_REVIEW),
            "--git",
            "--output",
            str(repo / ".agents/reviews"),
            "--",
            "src/app.py",
        ],
        repo,
        env,
    )

    assert result.returncode == 0, result.stderr
    review_path = Path(result.stdout.strip())
    assert review_path.exists()
    assert "codex fallback review" in review_path.read_text(encoding="utf-8")
    assert claude_log.exists()
    assert codex_log.exists()
    assert not gemini_log.exists()


@pytest.mark.unit
def test_test_review_request_supports_explicit_gemini_provider(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()

    module_dir = project / "module"
    tests_dir = project / "tests"
    module_dir.mkdir()
    tests_dir.mkdir()
    (module_dir / "feature.py").write_text(
        "def greet(name: str) -> str:\n    return f'Hello, {name}'\n",
        encoding="utf-8",
    )
    (tests_dir / "test_feature.py").write_text(
        "from module.feature import greet\n\n\ndef test_greet():\n    assert greet('A') == 'Hello, A'\n",
        encoding="utf-8",
    )

    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    gemini_log = tmp_path / "audit-gemini.log"

    _write_executable(
        fake_bin / "gemini",
        f"""#!/usr/bin/env bash
echo "$@" > "{gemini_log}"
cat >/dev/null
cat <<'EOF'
## Test Gap Report: feature

**Module:** `module/feature.py`
**Tests:** `tests/test_feature.py`
**Mode:** full

### Behavior Inventory

| Behavior | Coverage | Evidence |
|----------|----------|----------|
| greet(name) returns greeting | Covered | Verified by test_greet |

### Prioritized Gaps
_No prioritized gaps._

### Summary
- Covered: 1
- Shallow: 0
- Missing: 0
- P0: 0
- P1: 0
- P2: 0
EOF
""",
    )

    env = os.environ.copy()
    env["PATH"] = f"{fake_bin}:{env['PATH']}"

    result = _run(
        [
            str(TEST_REVIEW),
            "--provider",
            "gemini",
            str(module_dir),
            "--tests",
            str(tests_dir),
            "--output",
            str(project / ".agents/reviews"),
        ],
        project,
        env,
    )

    assert result.returncode == 0, result.stderr
    report_path = Path(result.stdout.strip())
    assert report_path.exists()
    assert "Test Gap Report: feature" in report_path.read_text(encoding="utf-8")

    gemini_args = gemini_log.read_text(encoding="utf-8")
    assert "--approval-mode" in gemini_args
    assert "plan" in gemini_args


@pytest.mark.unit
def test_test_review_treats_whitespace_only_claude_output_as_empty(
    tmp_path: Path,
) -> None:
    project = tmp_path / "project"
    project.mkdir()

    module_dir = project / "module"
    tests_dir = project / "tests"
    module_dir.mkdir()
    tests_dir.mkdir()
    (module_dir / "feature.py").write_text(
        "def greet(name: str) -> str:\n    return f'Hello, {name}'\n",
        encoding="utf-8",
    )
    (tests_dir / "test_feature.py").write_text(
        "from module.feature import greet\n\n\ndef test_greet():\n    assert greet('A') == 'Hello, A'\n",
        encoding="utf-8",
    )

    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()

    _write_executable(
        fake_bin / "claude",
        """#!/usr/bin/env bash
if [[ "$1" == "auth" && "$2" == "status" ]]; then
  echo '{"loggedIn": true}'
  exit 0
fi
cat >/dev/null
printf '\\n'
""",
    )
    _write_executable(
        fake_bin / "gemini",
        """#!/usr/bin/env bash
cat >/dev/null
cat <<'EOF'
## Test Gap Report: feature

**Module:** `module/feature.py`
**Tests:** `tests/test_feature.py`
**Mode:** full

### Behavior Inventory

| Behavior | Coverage | Evidence |
|----------|----------|----------|
| greet(name) returns greeting | Covered | Verified by test_greet |

### Prioritized Gaps
_No prioritized gaps._

### Summary
- Covered: 1
- Shallow: 0
- Missing: 0
- P0: 0
- P1: 0
- P2: 0
EOF
""",
    )

    env = os.environ.copy()
    env["PATH"] = f"{fake_bin}:{env['PATH']}"
    env["AGENT_LOOPS_SELF_PROVIDER"] = "codex"

    result = _run(
        [
            str(TEST_REVIEW),
            str(module_dir),
            "--tests",
            str(tests_dir),
            "--output",
            str(project / ".agents/reviews"),
        ],
        project,
        env,
    )

    assert result.returncode == 0, result.stderr
    assert "empty or whitespace-only" in result.stderr
    assert "Invalid output saved to:" not in result.stderr
    assert "Partial output saved to:" not in result.stderr
    assert not list((project / ".agents/reviews").glob("*.claude.invalid.md"))
    assert not list((project / ".agents/reviews").glob("*.claude.partial.md"))
    assert "Test Gap Report: feature" in Path(result.stdout.strip()).read_text(
        encoding="utf-8"
    )


@pytest.mark.unit
def test_specialist_review_removes_whitespace_only_output_without_fallback(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    _run(["git", "init"], repo, os.environ.copy())
    _run(["git", "config", "user.email", "test@example.com"], repo, os.environ.copy())
    _run(["git", "config", "user.name", "Test User"], repo, os.environ.copy())

    src_dir = repo / "src"
    src_dir.mkdir()
    source_file = src_dir / "app.py"
    source_file.write_text("print('before')\n", encoding="utf-8")
    _run(["git", "add", "src/app.py"], repo, os.environ.copy())
    _run(["git", "commit", "-m", "init"], repo, os.environ.copy())
    source_file.write_text("print('after')\n", encoding="utf-8")

    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    _write_executable(
        fake_bin / "claude",
        """#!/usr/bin/env bash
if [[ "$1" == "auth" && "$2" == "status" ]]; then
  echo '{"loggedIn": true}'
  exit 0
fi
cat >/dev/null
printf '\\n'
""",
    )

    env = os.environ.copy()
    env["PATH"] = f"{fake_bin}:{env['PATH']}"
    env["PYTHONPATH"] = str(REPO_ROOT)

    output_dir = repo / ".agents/reviews"
    result = _run(
        [
            str(SPECIALIST_REVIEW),
            "--provider",
            "claude",
            "--git",
            "--output",
            str(output_dir),
            "--",
            "src/app.py",
        ],
        repo,
        env,
    )

    assert result.returncode == 1
    assert "empty or whitespace-only" in result.stderr
    assert "Partial output saved to:" not in result.stderr
    assert not list(output_dir.glob("*.claude.partial.md"))
    final_artifacts = [
        path for path in output_dir.glob("review-*.md") if ".claude." not in path.name
    ]
    assert final_artifacts == []


@pytest.mark.unit
def test_test_review_git_mode_includes_tracked_and_untracked_files(
    tmp_path: Path,
) -> None:
    project = tmp_path / "project"
    project.mkdir()

    _run(["git", "init"], project, os.environ.copy())
    _run(
        ["git", "config", "user.email", "test@example.com"], project, os.environ.copy()
    )
    _run(["git", "config", "user.name", "Test User"], project, os.environ.copy())

    module_dir = project / "module"
    tests_dir = project / "tests"
    module_dir.mkdir()
    tests_dir.mkdir()
    feature_file = module_dir / "feature.py"
    feature_file.write_text(
        "def greet(name: str) -> str:\n    return f'Hello, {name}'\n",
        encoding="utf-8",
    )
    (tests_dir / "test_feature.py").write_text(
        "from module.feature import greet\n\n\ndef test_greet():\n    assert greet('A') == 'Hello, A'\n",
        encoding="utf-8",
    )
    _run(
        ["git", "add", "module/feature.py", "tests/test_feature.py"],
        project,
        os.environ.copy(),
    )
    _run(["git", "commit", "-m", "init"], project, os.environ.copy())

    feature_file.write_text(
        "def greet(name: str) -> str:\n    return f'Hello there, {name}'\n",
        encoding="utf-8",
    )
    (module_dir / "new_feature.py").write_text(
        "def farewell(name: str) -> str:\n    return f'Bye, {name}'\n",
        encoding="utf-8",
    )

    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    prompt_log = tmp_path / "audit-prompt.md"
    _write_executable(
        fake_bin / "gemini",
        f"""#!/usr/bin/env bash
cat > "{prompt_log}"
cat <<'EOF'
## Test Gap Report: feature

**Module:** `module`
**Tests:** `tests`
**Mode:** diff

### Behavior Inventory

| Behavior | Coverage | Evidence |
|----------|----------|----------|
| git diff includes tracked and untracked files | Covered | Prompt inspection |

### Prioritized Gaps
_No prioritized gaps._

### Summary
- Covered: 1
- Shallow: 0
- Missing: 0
- P0: 0
- P1: 0
- P2: 0
EOF
""",
    )

    env = os.environ.copy()
    env["PATH"] = f"{fake_bin}:{env['PATH']}"

    result = _run(
        [
            str(TEST_REVIEW),
            "--provider",
            "gemini",
            "--git",
            "HEAD",
            "module",
            "--tests",
            "tests",
            "--output",
            str(project / ".agents/reviews"),
        ],
        project,
        env,
    )

    assert result.returncode == 0, result.stderr
    prompt = prompt_log.read_text(encoding="utf-8")
    assert "diff --git a/module/feature.py b/module/feature.py" in prompt
    assert "diff --git a/module/new_feature.py b/module/new_feature.py" in prompt
    assert "@@ -0,0 +1,2 @@" in prompt
    assert "Hello there" in prompt
    assert "farewell" in prompt


@pytest.mark.unit
def test_test_review_removes_whitespace_only_output_without_fallback(
    tmp_path: Path,
) -> None:
    project = tmp_path / "project"
    project.mkdir()

    module_dir = project / "module"
    tests_dir = project / "tests"
    module_dir.mkdir()
    tests_dir.mkdir()
    (module_dir / "feature.py").write_text(
        "def greet(name: str) -> str:\n    return f'Hello, {name}'\n",
        encoding="utf-8",
    )
    (tests_dir / "test_feature.py").write_text(
        "from module.feature import greet\n\n\ndef test_greet():\n    assert greet('A') == 'Hello, A'\n",
        encoding="utf-8",
    )

    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    _write_executable(
        fake_bin / "claude",
        """#!/usr/bin/env bash
if [[ "$1" == "auth" && "$2" == "status" ]]; then
  echo '{"loggedIn": true}'
  exit 0
fi
cat >/dev/null
printf '\\n'
""",
    )

    env = os.environ.copy()
    env["PATH"] = f"{fake_bin}:{env['PATH']}"

    output_dir = project / ".agents/reviews"
    result = _run(
        [
            str(TEST_REVIEW),
            "--provider",
            "claude",
            str(module_dir),
            "--tests",
            str(tests_dir),
            "--output",
            str(output_dir),
        ],
        project,
        env,
    )

    assert result.returncode == 1
    assert "empty or whitespace-only" in result.stderr
    assert "Partial output saved to:" not in result.stderr
    assert not list(output_dir.glob("*.claude.partial.md"))
    final_artifacts = [
        path
        for path in output_dir.glob("test-audit-*.md")
        if ".claude." not in path.name
    ]
    assert final_artifacts == []


@pytest.mark.unit
def test_test_review_request_auto_keeps_self_provider_last(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()

    module_dir = project / "module"
    tests_dir = project / "tests"
    module_dir.mkdir()
    tests_dir.mkdir()
    (module_dir / "feature.py").write_text(
        "def greet(name: str) -> str:\n    return f'Hello, {name}'\n",
        encoding="utf-8",
    )
    (tests_dir / "test_feature.py").write_text(
        "from module.feature import greet\n\n\ndef test_greet():\n    assert greet('A') == 'Hello, A'\n",
        encoding="utf-8",
    )

    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    claude_log = tmp_path / "audit-claude.log"
    codex_log = tmp_path / "audit-codex.log"
    gemini_log = tmp_path / "audit-gemini.log"

    _write_executable(
        fake_bin / "claude",
        f"""#!/usr/bin/env bash
echo "$@" > "{claude_log}"
echo "claude failed intentionally" >&2
exit 1
""",
    )
    _write_executable(
        fake_bin / "codex",
        f"""#!/usr/bin/env bash
echo "$@" > "{codex_log}"
out_file=""
prev=""
for arg in "$@"; do
  if [[ "$prev" == "-o" ]]; then
    out_file="$arg"
  fi
  prev="$arg"
done
cat >/dev/null
cat <<'EOF' > "$out_file"
## Test Gap Report: feature

**Module:** `module/feature.py`
**Tests:** `tests/test_feature.py`
**Mode:** full

### Behavior Inventory

| Behavior | Coverage | Evidence |
|----------|----------|----------|
| greet(name) returns greeting | Covered | Verified by test_greet |

### Prioritized Gaps
_No prioritized gaps._

### Summary
- Covered: 1
- Shallow: 0
- Missing: 0
- P0: 0
- P1: 0
- P2: 0
EOF
""",
    )
    _write_executable(
        fake_bin / "gemini",
        f"""#!/usr/bin/env bash
echo "$@" > "{gemini_log}"
echo "gemini should not be invoked before codex" >&2
exit 1
""",
    )

    env = os.environ.copy()
    env["PATH"] = f"{fake_bin}:{env['PATH']}"
    env["AGENT_LOOPS_SELF_PROVIDER"] = "gemini"

    result = _run(
        [
            str(TEST_REVIEW),
            str(module_dir),
            "--tests",
            str(tests_dir),
            "--output",
            str(project / ".agents/reviews"),
        ],
        project,
        env,
    )

    assert result.returncode == 0, result.stderr
    report_path = Path(result.stdout.strip())
    assert report_path.exists()
    assert "Test Gap Report: feature" in report_path.read_text(encoding="utf-8")
    assert claude_log.exists()
    assert codex_log.exists()
    assert not gemini_log.exists()


@pytest.mark.unit
def test_test_review_request_auto_detects_gemini_self_provider_from_cli_env(
    tmp_path: Path,
) -> None:
    project = tmp_path / "project"
    project.mkdir()

    module_dir = project / "module"
    tests_dir = project / "tests"
    module_dir.mkdir()
    tests_dir.mkdir()
    (module_dir / "feature.py").write_text(
        "def greet(name: str) -> str:\n    return f'Hello, {name}'\n",
        encoding="utf-8",
    )
    (tests_dir / "test_feature.py").write_text(
        "from module.feature import greet\n\n\ndef test_greet():\n    assert greet('A') == 'Hello, A'\n",
        encoding="utf-8",
    )

    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    claude_log = tmp_path / "audit-gemini-env-claude.log"
    codex_log = tmp_path / "audit-gemini-env-codex.log"
    gemini_log = tmp_path / "audit-gemini-env-gemini.log"

    _write_executable(
        fake_bin / "claude",
        f"""#!/usr/bin/env bash
echo "$@" > "{claude_log}"
echo "claude failed intentionally" >&2
exit 1
""",
    )
    _write_executable(
        fake_bin / "codex",
        f"""#!/usr/bin/env bash
echo "$@" > "{codex_log}"
out_file=""
prev=""
for arg in "$@"; do
  if [[ "$prev" == "-o" ]]; then
    out_file="$arg"
  fi
  prev="$arg"
done
cat >/dev/null
cat <<'EOF' > "$out_file"
## Test Gap Report: feature

**Module:** `module/feature.py`
**Tests:** `tests/test_feature.py`
**Mode:** full

### Behavior Inventory

| Behavior | Coverage | Evidence |
|----------|----------|----------|
| greet(name) returns greeting | Covered | Verified by test_greet |

### Prioritized Gaps
_No prioritized gaps._

### Summary
- Covered: 1
- Shallow: 0
- Missing: 0
- P0: 0
- P1: 0
- P2: 0
EOF
""",
    )
    _write_executable(
        fake_bin / "gemini",
        f"""#!/usr/bin/env bash
echo "$@" > "{gemini_log}"
echo "gemini should not be invoked before codex" >&2
exit 1
""",
    )

    env = os.environ.copy()
    env["PATH"] = f"{fake_bin}:{env['PATH']}"
    env.pop("AGENT_LOOPS_SELF_PROVIDER", None)
    env.pop("CODEX_THREAD_ID", None)
    env.pop("CODEX_MANAGED_BY_NPM", None)
    env.pop("CLAUDECODE", None)
    env["GEMINI_CLI_NO_RELAUNCH"] = "true"

    result = _run(
        [
            str(TEST_REVIEW),
            str(module_dir),
            "--tests",
            str(tests_dir),
            "--output",
            str(project / ".agents/reviews"),
        ],
        project,
        env,
    )

    assert result.returncode == 0, result.stderr
    report_path = Path(result.stdout.strip())
    assert report_path.exists()
    assert "Test Gap Report: feature" in report_path.read_text(encoding="utf-8")
    assert claude_log.exists()
    assert codex_log.exists()
    assert not gemini_log.exists()


@pytest.mark.unit
def test_specialist_review_supports_explicit_codex_provider(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    _run(["git", "init"], repo, os.environ.copy())
    _run(["git", "config", "user.email", "test@example.com"], repo, os.environ.copy())
    _run(["git", "config", "user.name", "Test User"], repo, os.environ.copy())

    src_dir = repo / "src"
    src_dir.mkdir()
    source_file = src_dir / "app.py"
    source_file.write_text("print('before')\n", encoding="utf-8")
    _run(["git", "add", "src/app.py"], repo, os.environ.copy())
    _run(["git", "commit", "-m", "init"], repo, os.environ.copy())
    source_file.write_text("print('after')\n", encoding="utf-8")

    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    codex_log = tmp_path / "codex.log"

    _write_executable(
        fake_bin / "codex",
        f"""#!/usr/bin/env bash
echo "$@" > "{codex_log}"
out_file=""
prev=""
for arg in "$@"; do
  if [[ "$prev" == "-o" ]]; then
    out_file="$arg"
  fi
  prev="$arg"
done
cat >/dev/null
cat <<'EOF' > "$out_file"
## Code Review: codex review

**Files reviewed:** src/app.py
**Iteration:** 1 of 3

### Findings
_No findings._

### Summary
- P0: 0 findings (MUST fix)
- P1: 0 findings (MUST fix)
- P2: 0 findings (file issues)
- P3: 0 findings (file issues)
- **Verdict:** CLEAN
EOF
""",
    )

    env = os.environ.copy()
    env["PATH"] = f"{fake_bin}:{env['PATH']}"
    env["PYTHONPATH"] = str(REPO_ROOT)

    result = _run(
        [
            str(SPECIALIST_REVIEW),
            "--provider",
            "codex",
            "--git",
            "--output",
            str(repo / ".agents/reviews"),
            "--",
            "src/app.py",
        ],
        repo,
        env,
    )

    assert result.returncode == 0, result.stderr
    review_path = Path(result.stdout.strip())
    assert review_path.exists()
    assert "codex review" in review_path.read_text(encoding="utf-8")

    codex_args = codex_log.read_text(encoding="utf-8")
    assert "exec" in codex_args
    assert "--ephemeral" in codex_args
    assert "--skip-git-repo-check" in codex_args
    assert "-o" in codex_args


@pytest.mark.unit
def test_specialist_review_honors_claude_model_override(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    _run(["git", "init"], repo, os.environ.copy())
    _run(["git", "config", "user.email", "test@example.com"], repo, os.environ.copy())
    _run(["git", "config", "user.name", "Test User"], repo, os.environ.copy())

    src_dir = repo / "src"
    src_dir.mkdir()
    source_file = src_dir / "app.py"
    source_file.write_text("print('before')\n", encoding="utf-8")
    _run(["git", "add", "src/app.py"], repo, os.environ.copy())
    _run(["git", "commit", "-m", "init"], repo, os.environ.copy())
    source_file.write_text("print('after')\n", encoding="utf-8")

    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    claude_log = tmp_path / "claude.log"

    _write_executable(
        fake_bin / "claude",
        f"""#!/usr/bin/env bash
if [[ "${{1:-}}" == "auth" && "${{2:-}}" == "status" ]]; then
  echo '{{"loggedIn": true}}'
  exit 0
fi
echo "$@" > "{claude_log}"
cat >/dev/null
cat <<'EOF'
## Code Review: claude review

**Files reviewed:** src/app.py
**Iteration:** 1 of 3

### Findings
_No findings._

### Summary
- P0: 0 findings (MUST fix)
- P1: 0 findings (MUST fix)
- P2: 0 findings (file issues)
- P3: 0 findings (file issues)
- **Verdict:** CLEAN
EOF
""",
    )

    env = os.environ.copy()
    env["PATH"] = f"{fake_bin}:{env['PATH']}"
    env["CLAUDE_MODEL"] = "sonnet"
    env["PYTHONPATH"] = str(REPO_ROOT)

    result = _run(
        [
            str(SPECIALIST_REVIEW),
            "--provider",
            "claude",
            "--git",
            "--output",
            str(repo / ".agents/reviews"),
            "--",
            "src/app.py",
        ],
        repo,
        env,
    )

    assert result.returncode == 0, result.stderr
    review_path = Path(result.stdout.strip())
    assert review_path.exists()

    claude_args = claude_log.read_text(encoding="utf-8")
    assert "--model sonnet" in claude_args


@pytest.mark.unit
def test_specialist_review_secondary_provider_synthesizes_artifact(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    _run(["git", "init"], repo, os.environ.copy())
    _run(["git", "config", "user.email", "test@example.com"], repo, os.environ.copy())
    _run(["git", "config", "user.name", "Test User"], repo, os.environ.copy())

    src_dir = repo / "src"
    src_dir.mkdir()
    source_file = src_dir / "app.py"
    source_file.write_text("print('before')\n", encoding="utf-8")
    _run(["git", "add", "src/app.py"], repo, os.environ.copy())
    _run(["git", "commit", "-m", "init"], repo, os.environ.copy())
    source_file.write_text("print('after')\n", encoding="utf-8")

    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    codex_log = tmp_path / "secondary-codex.log"

    _write_executable(
        fake_bin / "gemini",
        """#!/usr/bin/env bash
cat >/dev/null
cat <<'EOF'
## Code Review: primary review

**Files reviewed:** src/app.py
**Iteration:** 1 of 3

### Findings
_No findings._

### Summary
- P0: 0 findings (MUST fix)
- P1: 0 findings (MUST fix)
- P2: 0 findings (file issues)
- P3: 0 findings (file issues)
- **Verdict:** CLEAN
EOF
""",
    )
    _write_executable(
        fake_bin / "codex",
        f"""#!/usr/bin/env bash
echo "$@" > "{codex_log}"
out_file=""
prev=""
for arg in "$@"; do
  if [[ "$prev" == "-o" ]]; then
    out_file="$arg"
  fi
  prev="$arg"
done
cat >/dev/null
cat <<'EOF' > "$out_file"
MCP diagnostics from nested provider.
## Code Review: secondary review

**Files reviewed:** src/app.py
**Iteration:** 1 of 3

### Issues
- P2: src/app.py:1 should be covered by a focused assertion.

### Summary
- P0: 0 findings (MUST fix)
- P1: 0 findings (MUST fix)
- P2: 1 findings (file issues)
- P3: 0 findings (file issues)
- **Verdict:** PASS WITH ISSUES
EOF
""",
    )

    env = os.environ.copy()
    env["PATH"] = f"{fake_bin}:{env['PATH']}"
    env["PYTHONPATH"] = str(REPO_ROOT)
    env["SPECIALIST_REVIEW_SECONDARY_PROVIDER"] = "codex"
    env["SPECIALIST_REVIEW_SECONDARY_MODEL"] = "gpt-review"

    result = _run(
        [
            str(SPECIALIST_REVIEW),
            "--provider",
            "gemini",
            "--git",
            "--output",
            str(repo / ".agents/reviews"),
            "--",
            "src/app.py",
        ],
        repo,
        env,
    )

    assert result.returncode == 0, result.stderr
    review_path = Path(result.stdout.strip())
    review_text = review_path.read_text(encoding="utf-8")
    assert "Code Review: dual reviewer synthesis" in review_text
    assert (
        "Secondary Codex output normalized to the code review contract."
        in result.stderr
    )
    assert "Primary Review (gemini)" in review_text
    assert "Secondary Review (codex)" in review_text
    assert "- P2: 1 findings (file issues)" in review_text
    assert "- **Verdict:** PASS WITH ISSUES" in review_text

    raw_artifacts = {path.name for path in review_path.parent.glob("review-*.md")}
    assert any(".primary-gemini.md" in name for name in raw_artifacts)
    assert any(".secondary-codex.md" in name for name in raw_artifacts)

    codex_args = codex_log.read_text(encoding="utf-8")
    assert "-m gpt-review" in codex_args


@pytest.mark.unit
def test_specialist_review_secondary_provider_invalid_output_fails_with_summary(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    _run(["git", "init"], repo, os.environ.copy())
    _run(["git", "config", "user.email", "test@example.com"], repo, os.environ.copy())
    _run(["git", "config", "user.name", "Test User"], repo, os.environ.copy())

    src_dir = repo / "src"
    src_dir.mkdir()
    source_file = src_dir / "app.py"
    source_file.write_text("print('before')\n", encoding="utf-8")
    _run(["git", "add", "src/app.py"], repo, os.environ.copy())
    _run(["git", "commit", "-m", "init"], repo, os.environ.copy())
    source_file.write_text("print('after')\n", encoding="utf-8")

    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()

    _write_executable(
        fake_bin / "gemini",
        """#!/usr/bin/env bash
cat >/dev/null
cat <<'EOF'
## Code Review: primary review

**Files reviewed:** src/app.py
**Iteration:** 1 of 3

### Findings
_No findings._

### Summary
- P0: 0 findings (MUST fix)
- P1: 0 findings (MUST fix)
- P2: 0 findings (file issues)
- P3: 0 findings (file issues)
- **Verdict:** CLEAN
EOF
""",
    )
    _write_executable(
        fake_bin / "codex",
        """#!/usr/bin/env bash
out_file=""
prev=""
for arg in "$@"; do
  if [[ "$prev" == "-o" ]]; then
    out_file="$arg"
  fi
  prev="$arg"
done
cat >/dev/null
echo "not a code review artifact" > "$out_file"
""",
    )

    env = os.environ.copy()
    env["PATH"] = f"{fake_bin}:{env['PATH']}"
    env["PYTHONPATH"] = str(REPO_ROOT)
    env["SPECIALIST_REVIEW_SECONDARY_PROVIDER"] = "codex"

    result = _run(
        [
            str(SPECIALIST_REVIEW),
            "--provider",
            "gemini",
            "--git",
            "--output",
            str(repo / ".agents/reviews"),
            "--",
            "src/app.py",
        ],
        repo,
        env,
    )

    assert result.returncode == 1
    assert (
        "[REVIEW FAILED] Secondary contract validation failed (codex)" in result.stdout
    )
    assert (
        "Secondary Codex output did not match the code review contract" in result.stderr
    )


@pytest.mark.unit
def test_specialist_review_secondary_provider_exit_failure_fails_with_summary(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    _run(["git", "init"], repo, os.environ.copy())
    _run(["git", "config", "user.email", "test@example.com"], repo, os.environ.copy())
    _run(["git", "config", "user.name", "Test User"], repo, os.environ.copy())

    src_dir = repo / "src"
    src_dir.mkdir()
    source_file = src_dir / "app.py"
    source_file.write_text("print('before')\n", encoding="utf-8")
    _run(["git", "add", "src/app.py"], repo, os.environ.copy())
    _run(["git", "commit", "-m", "init"], repo, os.environ.copy())
    source_file.write_text("print('after')\n", encoding="utf-8")

    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()

    _write_executable(
        fake_bin / "gemini",
        """#!/usr/bin/env bash
cat >/dev/null
cat <<'EOF'
## Code Review: primary review

**Files reviewed:** src/app.py
**Iteration:** 1 of 3

### Findings
_No findings._

### Summary
- P0: 0 findings (MUST fix)
- P1: 0 findings (MUST fix)
- P2: 0 findings (file issues)
- P3: 0 findings (file issues)
- **Verdict:** CLEAN
EOF
""",
    )
    _write_executable(
        fake_bin / "codex",
        """#!/usr/bin/env bash
cat >/dev/null
echo "secondary failed intentionally" >&2
exit 1
""",
    )

    env = os.environ.copy()
    env["PATH"] = f"{fake_bin}:{env['PATH']}"
    env["PYTHONPATH"] = str(REPO_ROOT)
    env["SPECIALIST_REVIEW_SECONDARY_PROVIDER"] = "codex"

    result = _run(
        [
            str(SPECIALIST_REVIEW),
            "--provider",
            "gemini",
            "--git",
            "--output",
            str(repo / ".agents/reviews"),
            "--",
            "src/app.py",
        ],
        repo,
        env,
    )

    assert result.returncode == 1
    assert "[REVIEW FAILED] Secondary provider failed (codex)" in result.stdout
    assert "Secondary Codex invocation failed (exit 1)" in result.stderr


@pytest.mark.unit
def test_test_review_request_supports_explicit_codex_provider(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()

    module_dir = project / "module"
    tests_dir = project / "tests"
    module_dir.mkdir()
    tests_dir.mkdir()
    (module_dir / "feature.py").write_text(
        "def greet(name: str) -> str:\n    return f'Hello, {name}'\n",
        encoding="utf-8",
    )
    (tests_dir / "test_feature.py").write_text(
        "from module.feature import greet\n\n\ndef test_greet():\n    assert greet('A') == 'Hello, A'\n",
        encoding="utf-8",
    )

    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    codex_log = tmp_path / "audit-codex.log"

    _write_executable(
        fake_bin / "codex",
        f"""#!/usr/bin/env bash
echo "$@" > "{codex_log}"
out_file=""
prev=""
for arg in "$@"; do
  if [[ "$prev" == "-o" ]]; then
    out_file="$arg"
  fi
  prev="$arg"
done
cat >/dev/null
cat <<'EOF' > "$out_file"
## Test Gap Report: feature

**Module:** `module/feature.py`
**Tests:** `tests/test_feature.py`
**Mode:** full

### Behavior Inventory

| Behavior | Coverage | Evidence |
|----------|----------|----------|
| greet(name) returns greeting | Covered | Verified by test_greet |

### Prioritized Gaps
_No prioritized gaps._

### Summary
- Covered: 1
- Shallow: 0
- Missing: 0
- P0: 0
- P1: 0
- P2: 0
EOF
""",
    )

    env = os.environ.copy()
    env["PATH"] = f"{fake_bin}:{env['PATH']}"

    result = _run(
        [
            str(TEST_REVIEW),
            "--provider",
            "codex",
            str(module_dir),
            "--tests",
            str(tests_dir),
            "--output",
            str(project / ".agents/reviews"),
        ],
        project,
        env,
    )

    assert result.returncode == 0, result.stderr
    report_path = Path(result.stdout.strip())
    assert report_path.exists()
    assert "Test Gap Report: feature" in report_path.read_text(encoding="utf-8")

    codex_args = codex_log.read_text(encoding="utf-8")
    assert "exec" in codex_args
    assert "--ephemeral" in codex_args
    assert "--skip-git-repo-check" in codex_args
    assert "-o" in codex_args


@pytest.mark.unit
def test_test_review_secondary_provider_synthesizes_artifact(
    tmp_path: Path,
) -> None:
    project = tmp_path / "project"
    project.mkdir()

    module_dir = project / "module"
    tests_dir = project / "tests"
    module_dir.mkdir()
    tests_dir.mkdir()
    (module_dir / "feature.py").write_text(
        "def greet(name: str) -> str:\n    return f'Hello, {name}'\n",
        encoding="utf-8",
    )
    (tests_dir / "test_feature.py").write_text(
        "from module.feature import greet\n\n\ndef test_greet():\n    assert greet('A') == 'Hello, A'\n",
        encoding="utf-8",
    )

    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    codex_log = tmp_path / "secondary-audit-codex.log"

    _write_executable(
        fake_bin / "gemini",
        """#!/usr/bin/env bash
cat >/dev/null
cat <<'EOF'
## Test Gap Report: primary audit

**Module:** `module/feature.py`
**Tests:** `tests/test_feature.py`
**Mode:** full

### Behavior Inventory

| Behavior | Coverage | Evidence |
|----------|----------|----------|
| greet(name) returns greeting | Covered | Verified by test_greet |

### Prioritized Gaps
_No prioritized gaps._

### Summary
- Covered: 1
- Shallow: 0
- Missing: 0
- P0: 0
- P1: 0
- P2: 0
EOF
""",
    )
    _write_executable(
        fake_bin / "codex",
        f"""#!/usr/bin/env bash
echo "$@" > "{codex_log}"
out_file=""
prev=""
for arg in "$@"; do
  if [[ "$prev" == "-o" ]]; then
    out_file="$arg"
  fi
  prev="$arg"
done
cat >/dev/null
cat <<'EOF' > "$out_file"
Provider diagnostics before artifact.
## Test Gap Report: secondary audit

**Module:** `module/feature.py`
**Tests:** `tests/test_feature.py`
**Mode:** full

### Behavior Inventory

| Behavior | Coverage | Evidence |
|:---------|:--------:|---------:|
| empty name handling | Missing | No assertion covers empty input |

### Findings
- P1: module/feature.py should test empty name handling.

### Summary
- Covered: 0
- Shallow: 0
- Missing: 1
- P0: 0
- P1: 1
- P2: 0
EOF
""",
    )

    env = os.environ.copy()
    env["PATH"] = f"{fake_bin}:{env['PATH']}"
    env["PYTHONPATH"] = str(REPO_ROOT)
    env["TEST_REVIEW_SECONDARY_PROVIDER"] = "codex"
    env["TEST_REVIEW_SECONDARY_MODEL"] = "gpt-audit"

    result = _run(
        [
            str(TEST_REVIEW),
            "--provider",
            "gemini",
            str(module_dir),
            "--tests",
            str(tests_dir),
            "--output",
            str(project / ".agents/reviews"),
        ],
        project,
        env,
    )

    assert result.returncode == 0, result.stderr
    report_path = Path(result.stdout.strip())
    report_text = report_path.read_text(encoding="utf-8")
    assert "Test Gap Report: dual reviewer synthesis" in report_text
    assert (
        "Secondary Codex output normalized to the test audit contract." in result.stderr
    )
    assert "Primary Audit (gemini)" in report_text
    assert "Secondary Audit (codex)" in report_text
    assert "- Missing: 1" in report_text
    assert "- P1: 1" in report_text
    assert ":--------:" not in report_text

    raw_artifacts = {path.name for path in report_path.parent.glob("test-audit-*.md")}
    assert any(".primary-gemini.md" in name for name in raw_artifacts)
    assert any(".secondary-codex.md" in name for name in raw_artifacts)

    codex_args = codex_log.read_text(encoding="utf-8")
    assert "-m gpt-audit" in codex_args


@pytest.mark.unit
def test_test_review_secondary_provider_invalid_output_fails_with_summary(
    tmp_path: Path,
) -> None:
    project = tmp_path / "project"
    project.mkdir()

    module_dir = project / "module"
    tests_dir = project / "tests"
    module_dir.mkdir()
    tests_dir.mkdir()
    (module_dir / "feature.py").write_text(
        "def greet(name: str) -> str:\n    return f'Hello, {name}'\n",
        encoding="utf-8",
    )
    (tests_dir / "test_feature.py").write_text(
        "from module.feature import greet\n\n\ndef test_greet():\n    assert greet('A') == 'Hello, A'\n",
        encoding="utf-8",
    )

    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()

    _write_executable(
        fake_bin / "gemini",
        """#!/usr/bin/env bash
cat >/dev/null
cat <<'EOF'
## Test Gap Report: primary audit

**Module:** `module/feature.py`
**Tests:** `tests/test_feature.py`
**Mode:** full

### Behavior Inventory

| Behavior | Coverage | Evidence |
|----------|----------|----------|
| greet(name) returns greeting | Covered | Verified by test_greet |

### Prioritized Gaps
_No prioritized gaps._

### Summary
- Covered: 1
- Shallow: 0
- Missing: 0
- P0: 0
- P1: 0
- P2: 0
EOF
""",
    )
    _write_executable(
        fake_bin / "codex",
        """#!/usr/bin/env bash
out_file=""
prev=""
for arg in "$@"; do
  if [[ "$prev" == "-o" ]]; then
    out_file="$arg"
  fi
  prev="$arg"
done
cat >/dev/null
echo "not a test audit artifact" > "$out_file"
""",
    )

    env = os.environ.copy()
    env["PATH"] = f"{fake_bin}:{env['PATH']}"
    env["PYTHONPATH"] = str(REPO_ROOT)
    env["TEST_REVIEW_SECONDARY_PROVIDER"] = "codex"

    result = _run(
        [
            str(TEST_REVIEW),
            "--provider",
            "gemini",
            str(module_dir),
            "--tests",
            str(tests_dir),
            "--output",
            str(project / ".agents/reviews"),
        ],
        project,
        env,
    )

    assert result.returncode == 1
    assert (
        "[AUDIT FAILED] Secondary contract validation failed (codex)" in result.stdout
    )
    assert (
        "Secondary Codex output did not match the test audit contract" in result.stderr
    )


@pytest.mark.unit
def test_test_review_secondary_provider_unavailable_fails_fast(
    tmp_path: Path,
) -> None:
    project = tmp_path / "project"
    project.mkdir()

    module_dir = project / "module"
    tests_dir = project / "tests"
    module_dir.mkdir()
    tests_dir.mkdir()
    (module_dir / "feature.py").write_text(
        "def greet(name: str) -> str:\n    return f'Hello, {name}'\n",
        encoding="utf-8",
    )
    (tests_dir / "test_feature.py").write_text(
        "from module.feature import greet\n\n\ndef test_greet():\n    assert greet('A') == 'Hello, A'\n",
        encoding="utf-8",
    )

    env = os.environ.copy()
    env["TEST_REVIEW_SECONDARY_PROVIDER"] = "missing-secondary-provider"

    result = _run(
        [
            str(TEST_REVIEW),
            "--provider",
            "gemini",
            str(module_dir),
            "--tests",
            str(tests_dir),
            "--output",
            str(project / ".agents/reviews"),
        ],
        project,
        env,
    )

    assert result.returncode == 1
    assert (
        "Secondary provider 'missing-secondary-provider' is not available in PATH."
        in result.stderr
    )


@pytest.mark.unit
def test_test_review_secondary_provider_exit_failure_fails_with_summary(
    tmp_path: Path,
) -> None:
    project = tmp_path / "project"
    project.mkdir()

    module_dir = project / "module"
    tests_dir = project / "tests"
    module_dir.mkdir()
    tests_dir.mkdir()
    (module_dir / "feature.py").write_text(
        "def greet(name: str) -> str:\n    return f'Hello, {name}'\n",
        encoding="utf-8",
    )
    (tests_dir / "test_feature.py").write_text(
        "from module.feature import greet\n\n\ndef test_greet():\n    assert greet('A') == 'Hello, A'\n",
        encoding="utf-8",
    )

    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()

    _write_executable(
        fake_bin / "gemini",
        """#!/usr/bin/env bash
cat >/dev/null
cat <<'EOF'
## Test Gap Report: primary audit

**Module:** `module/feature.py`
**Tests:** `tests/test_feature.py`
**Mode:** full

### Behavior Inventory

| Behavior | Coverage | Evidence |
|----------|----------|----------|
| greet(name) returns greeting | Covered | Verified by test_greet |

### Prioritized Gaps
_No prioritized gaps._

### Summary
- Covered: 1
- Shallow: 0
- Missing: 0
- P0: 0
- P1: 0
- P2: 0
EOF
""",
    )
    _write_executable(
        fake_bin / "codex",
        """#!/usr/bin/env bash
cat >/dev/null
echo "secondary audit failed intentionally" >&2
exit 1
""",
    )

    env = os.environ.copy()
    env["PATH"] = f"{fake_bin}:{env['PATH']}"
    env["PYTHONPATH"] = str(REPO_ROOT)
    env["TEST_REVIEW_SECONDARY_PROVIDER"] = "codex"

    result = _run(
        [
            str(TEST_REVIEW),
            "--provider",
            "gemini",
            str(module_dir),
            "--tests",
            str(tests_dir),
            "--output",
            str(project / ".agents/reviews"),
        ],
        project,
        env,
    )

    assert result.returncode == 1
    assert "[AUDIT FAILED] Secondary provider failed (codex)" in result.stdout
    assert "Secondary Codex invocation failed (exit 1)" in result.stderr


@pytest.mark.unit
def test_test_review_secondary_provider_whitespace_output_fails_with_summary(
    tmp_path: Path,
) -> None:
    project = tmp_path / "project"
    project.mkdir()

    module_dir = project / "module"
    tests_dir = project / "tests"
    module_dir.mkdir()
    tests_dir.mkdir()
    (module_dir / "feature.py").write_text(
        "def greet(name: str) -> str:\n    return f'Hello, {name}'\n",
        encoding="utf-8",
    )
    (tests_dir / "test_feature.py").write_text(
        "from module.feature import greet\n\n\ndef test_greet():\n    assert greet('A') == 'Hello, A'\n",
        encoding="utf-8",
    )

    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()

    _write_executable(
        fake_bin / "gemini",
        """#!/usr/bin/env bash
cat >/dev/null
cat <<'EOF'
## Test Gap Report: primary audit

**Module:** `module/feature.py`
**Tests:** `tests/test_feature.py`
**Mode:** full

### Behavior Inventory

| Behavior | Coverage | Evidence |
|----------|----------|----------|
| greet(name) returns greeting | Covered | Verified by test_greet |

### Prioritized Gaps
_No prioritized gaps._

### Summary
- Covered: 1
- Shallow: 0
- Missing: 0
- P0: 0
- P1: 0
- P2: 0
EOF
""",
    )
    _write_executable(
        fake_bin / "codex",
        """#!/usr/bin/env bash
out_file=""
prev=""
for arg in "$@"; do
  if [[ "$prev" == "-o" ]]; then
    out_file="$arg"
  fi
  prev="$arg"
done
cat >/dev/null
printf '   \n' > "$out_file"
""",
    )

    env = os.environ.copy()
    env["PATH"] = f"{fake_bin}:{env['PATH']}"
    env["PYTHONPATH"] = str(REPO_ROOT)
    env["TEST_REVIEW_SECONDARY_PROVIDER"] = "codex"

    result = _run(
        [
            str(TEST_REVIEW),
            "--provider",
            "gemini",
            str(module_dir),
            "--tests",
            str(tests_dir),
            "--output",
            str(project / ".agents/reviews"),
        ],
        project,
        env,
    )

    assert result.returncode == 1
    assert (
        "[AUDIT FAILED] Secondary provider returned empty output (codex)"
        in result.stdout
    )
    assert "completed but report file is empty or whitespace-only" in result.stderr


@pytest.mark.unit
def test_test_review_request_normalizes_provider_preamble_and_section_aliases(
    tmp_path: Path,
) -> None:
    project = tmp_path / "project"
    project.mkdir()

    module_dir = project / "module"
    tests_dir = project / "tests"
    module_dir.mkdir()
    tests_dir.mkdir()
    (module_dir / "feature.py").write_text(
        "def greet(name: str) -> str:\n    return f'Hello, {name}'\n",
        encoding="utf-8",
    )
    (tests_dir / "test_feature.py").write_text(
        "from module.feature import greet\n\n\ndef test_greet():\n    assert greet('A') == 'Hello, A'\n",
        encoding="utf-8",
    )

    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    gemini_log = tmp_path / "normalized-audit-gemini.log"

    _write_executable(
        fake_bin / "gemini",
        f"""#!/usr/bin/env bash
echo "$@" > "{gemini_log}"
cat >/dev/null
cat <<'EOF'
MCP issues detected. Run /mcp list for status.## Test Gap Report: feature

**Module:** `module/feature.py`
**Tests:** `tests/test_feature.py`
**Mode:** full

### Behavior Inventory

| Behavior | Coverage | Evidence |
|----------|----------|----------|
| greet(name) returns greeting | Covered | Verified by test_greet |

### Findings
_No prioritized gaps._

### Summary
- Covered: 1
- Shallow: 0
- Missing: 0
- P0: 0
- P1: 0
- P2: 0
EOF
""",
    )

    env = os.environ.copy()
    env["PATH"] = f"{fake_bin}:{env['PATH']}"

    result = _run(
        [
            str(TEST_REVIEW),
            "--provider",
            "gemini",
            str(module_dir),
            "--tests",
            str(tests_dir),
            "--output",
            str(project / ".agents/reviews"),
        ],
        project,
        env,
    )

    assert result.returncode == 0, result.stderr
    report_path = Path(result.stdout.strip())
    assert report_path.exists()
    report_text = report_path.read_text(encoding="utf-8")
    assert report_text.startswith("## Test Gap Report:")
    assert "### Prioritized Gaps" in report_text
    assert "MCP issues detected" not in report_text

    raw_artifacts = list((project / ".agents/reviews").glob("*.gemini.raw.md"))
    assert len(raw_artifacts) == 1
    assert "MCP issues detected" in raw_artifacts[0].read_text(encoding="utf-8")


@pytest.mark.unit
def test_specialist_review_normalizes_provider_preamble(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    _run(["git", "init"], repo, os.environ.copy())
    _run(["git", "config", "user.email", "test@example.com"], repo, os.environ.copy())
    _run(["git", "config", "user.name", "Test User"], repo, os.environ.copy())

    src_dir = repo / "src"
    src_dir.mkdir()
    source_file = src_dir / "app.py"
    source_file.write_text("print('before')\n", encoding="utf-8")
    _run(["git", "add", "src/app.py"], repo, os.environ.copy())
    _run(["git", "commit", "-m", "init"], repo, os.environ.copy())
    source_file.write_text("print('after')\n", encoding="utf-8")

    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()

    _write_executable(
        fake_bin / "gemini",
        """#!/usr/bin/env bash
cat >/dev/null
cat <<'EOF'
MCP issues detected. Run /mcp list for status.## Code Review: normalized review

**Files reviewed:** src/app.py
**Iteration:** 1 of 3

### Findings
_No findings._

### Summary
- P0: 0 findings (MUST fix)
- P1: 0 findings (MUST fix)
- P2: 0 findings (file issues)
- P3: 0 findings (file issues)
- **Verdict:** CLEAN
EOF
""",
    )

    env = os.environ.copy()
    env["PATH"] = f"{fake_bin}:{env['PATH']}"
    env["PYTHONPATH"] = str(REPO_ROOT)

    result = _run(
        [
            str(SPECIALIST_REVIEW),
            "--provider",
            "gemini",
            "--git",
            "--output",
            str(repo / ".agents/reviews"),
            "--",
            "src/app.py",
        ],
        repo,
        env,
    )

    assert result.returncode == 0, result.stderr
    review_path = Path(result.stdout.strip())
    assert review_path.exists()
    review_text = review_path.read_text(encoding="utf-8")
    assert review_text.startswith("## Code Review:")
    assert "MCP issues detected" not in review_text

    raw_artifacts = list((repo / ".agents/reviews").glob("*.gemini.raw.md"))
    assert len(raw_artifacts) == 1
    assert "MCP issues detected" in raw_artifacts[0].read_text(encoding="utf-8")


@pytest.mark.unit
def test_specialist_review_normalizes_code_review_section_aliases(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    _run(["git", "init"], repo, os.environ.copy())
    _run(["git", "config", "user.email", "test@example.com"], repo, os.environ.copy())
    _run(["git", "config", "user.name", "Test User"], repo, os.environ.copy())

    src_dir = repo / "src"
    src_dir.mkdir()
    source_file = src_dir / "app.py"
    source_file.write_text("print('before')\n", encoding="utf-8")
    _run(["git", "add", "src/app.py"], repo, os.environ.copy())
    _run(["git", "commit", "-m", "init"], repo, os.environ.copy())
    source_file.write_text("print('after')\n", encoding="utf-8")

    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()

    _write_executable(
        fake_bin / "gemini",
        """#!/usr/bin/env bash
cat >/dev/null
cat <<'EOF'
## Code Review: alias normalized review

**Files reviewed:** src/app.py
**Iteration:** 1 of 3

### Issues
_No findings._

### Summary
- P0: 0 findings (MUST fix)
- P1: 0 findings (MUST fix)
- P2: 0 findings (file issues)
- P3: 0 findings (file issues)
- **Verdict:** CLEAN
EOF
""",
    )

    env = os.environ.copy()
    env["PATH"] = f"{fake_bin}:{env['PATH']}"
    env["PYTHONPATH"] = str(REPO_ROOT)

    result = _run(
        [
            str(SPECIALIST_REVIEW),
            "--provider",
            "gemini",
            "--git",
            "--output",
            str(repo / ".agents/reviews"),
            "--",
            "src/app.py",
        ],
        repo,
        env,
    )

    assert result.returncode == 0, result.stderr
    review_path = Path(result.stdout.strip())
    review_text = review_path.read_text(encoding="utf-8")
    assert "### Findings" in review_text
    assert "### Issues" not in review_text

    raw_artifacts = list((repo / ".agents/reviews").glob("*.gemini.raw.md"))
    assert len(raw_artifacts) == 1
    assert "### Issues" in raw_artifacts[0].read_text(encoding="utf-8")


@pytest.mark.unit
def test_test_review_request_preserves_invalid_artifact_when_normalization_fails(
    tmp_path: Path,
) -> None:
    project = tmp_path / "project"
    project.mkdir()

    module_dir = project / "module"
    tests_dir = project / "tests"
    module_dir.mkdir()
    tests_dir.mkdir()
    (module_dir / "feature.py").write_text(
        "def greet(name: str) -> str:\n    return f'Hello, {name}'\n",
        encoding="utf-8",
    )
    (tests_dir / "test_feature.py").write_text(
        "from module.feature import greet\n\n\ndef test_greet():\n    assert greet('A') == 'Hello, A'\n",
        encoding="utf-8",
    )

    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()

    _write_executable(
        fake_bin / "gemini",
        """#!/usr/bin/env bash
cat >/dev/null
python3 - <<'PY'
import sys
sys.stdout.buffer.write(b"\\xff\\xfe")
PY
""",
    )

    env = os.environ.copy()
    env["PATH"] = f"{fake_bin}:{env['PATH']}"

    result = _run(
        [
            str(TEST_REVIEW),
            "--provider",
            "gemini",
            str(module_dir),
            "--tests",
            str(tests_dir),
            "--output",
            str(project / ".agents/reviews"),
        ],
        project,
        env,
    )

    assert result.returncode == 1
    assert "could not be normalized" in result.stderr
    assert "Invalid output saved to:" in result.stderr

    invalid_artifacts = list((project / ".agents/reviews").glob("*.gemini.invalid.md"))
    assert len(invalid_artifacts) == 1
    assert invalid_artifacts[0].read_bytes() == b"\xff\xfe"


@pytest.mark.unit
def test_specialist_review_reports_claude_provider_diagnostics(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    _run(["git", "init"], repo, os.environ.copy())
    _run(["git", "config", "user.email", "test@example.com"], repo, os.environ.copy())
    _run(["git", "config", "user.name", "Test User"], repo, os.environ.copy())

    src_dir = repo / "src"
    src_dir.mkdir()
    source_file = src_dir / "app.py"
    source_file.write_text("print('before')\n", encoding="utf-8")
    _run(["git", "add", "src/app.py"], repo, os.environ.copy())
    _run(["git", "commit", "-m", "init"], repo, os.environ.copy())
    source_file.write_text("print('after')\n", encoding="utf-8")

    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    claude_log = tmp_path / "claude-diagnostics.log"

    _write_executable(
        fake_bin / "claude",
        f"""#!/usr/bin/env bash
if [[ "${{1:-}}" == "auth" && "${{2:-}}" == "status" ]]; then
  echo '{{"loggedIn": true}}'
  exit 0
fi
echo "$@" > "{claude_log}"
cat >/dev/null
cat <<'EOF'
## Code Review: claude review

**Files reviewed:** src/app.py
**Iteration:** 1 of 3

### Findings
_No findings._

### Summary
- P0: 0 findings (MUST fix)
- P1: 0 findings (MUST fix)
- P2: 0 findings (file issues)
- P3: 0 findings (file issues)
- **Verdict:** CLEAN
EOF
""",
    )

    env = os.environ.copy()
    env["PATH"] = f"{fake_bin}:{env['PATH']}"
    env["CLAUDE_MODEL"] = "sonnet"
    env["GEMINI_MODEL"] = "gemini-diag"
    env["CODEX_MODEL"] = "codex-diag"
    env["PYTHONPATH"] = str(REPO_ROOT)

    result = _run(
        [
            str(SPECIALIST_REVIEW),
            "--provider",
            "claude",
            "--git",
            "--output",
            str(repo / ".agents/reviews"),
            "--",
            "src/app.py",
        ],
        repo,
        env,
    )

    assert result.returncode == 0, result.stderr
    assert "Trying provider: Claude" in result.stderr
    assert "Claude budget: $2.00" in result.stderr
    assert "Claude model override: sonnet" in result.stderr
    assert "Gemini model override:" not in result.stderr
    assert "Codex model override:" not in result.stderr
    assert "--model sonnet" in claude_log.read_text(encoding="utf-8")


@pytest.mark.unit
def test_specialist_review_reports_gemini_provider_diagnostics(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    _run(["git", "init"], repo, os.environ.copy())
    _run(["git", "config", "user.email", "test@example.com"], repo, os.environ.copy())
    _run(["git", "config", "user.name", "Test User"], repo, os.environ.copy())

    src_dir = repo / "src"
    src_dir.mkdir()
    source_file = src_dir / "app.py"
    source_file.write_text("print('before')\n", encoding="utf-8")
    _run(["git", "add", "src/app.py"], repo, os.environ.copy())
    _run(["git", "commit", "-m", "init"], repo, os.environ.copy())
    source_file.write_text("print('after')\n", encoding="utf-8")

    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    gemini_log = tmp_path / "gemini-diagnostics.log"

    _write_executable(
        fake_bin / "gemini",
        f"""#!/usr/bin/env bash
echo "$@" > "{gemini_log}"
cat >/dev/null
cat <<'EOF'
## Code Review: gemini review

**Files reviewed:** src/app.py
**Iteration:** 1 of 3

### Findings
_No findings._

### Summary
- P0: 0 findings (MUST fix)
- P1: 0 findings (MUST fix)
- P2: 0 findings (file issues)
- P3: 0 findings (file issues)
- **Verdict:** CLEAN
EOF
""",
    )

    env = os.environ.copy()
    env["PATH"] = f"{fake_bin}:{env['PATH']}"
    env["GEMINI_MODEL"] = "gemini-diag"
    env["CLAUDE_MODEL"] = "sonnet"
    env["CODEX_MODEL"] = "codex-diag"
    env["PYTHONPATH"] = str(REPO_ROOT)

    result = _run(
        [
            str(SPECIALIST_REVIEW),
            "--provider",
            "gemini",
            "--git",
            "--output",
            str(repo / ".agents/reviews"),
            "--",
            "src/app.py",
        ],
        repo,
        env,
    )

    assert result.returncode == 0, result.stderr
    assert "Trying provider: Gemini" in result.stderr
    assert "Gemini model override: gemini-diag" in result.stderr
    assert "Claude budget:" not in result.stderr
    assert "Claude model override:" not in result.stderr
    assert "Codex model override:" not in result.stderr


@pytest.mark.unit
def test_test_review_reports_claude_provider_diagnostics(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()

    module_dir = project / "module"
    tests_dir = project / "tests"
    module_dir.mkdir()
    tests_dir.mkdir()
    (module_dir / "feature.py").write_text(
        "def greet(name: str) -> str:\n    return f'Hello, {name}'\n",
        encoding="utf-8",
    )
    (tests_dir / "test_feature.py").write_text(
        "from module.feature import greet\n\n\ndef test_greet():\n    assert greet('A') == 'Hello, A'\n",
        encoding="utf-8",
    )

    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    claude_log = tmp_path / "audit-claude-diagnostics.log"

    _write_executable(
        fake_bin / "claude",
        f"""#!/usr/bin/env bash
if [[ "${{1:-}}" == "auth" && "${{2:-}}" == "status" ]]; then
  echo '{{"loggedIn": true}}'
  exit 0
fi
echo "$@" > "{claude_log}"
cat >/dev/null
cat <<'EOF'
## Test Gap Report: feature

**Module:** `module/feature.py`
**Tests:** `tests/test_feature.py`
**Mode:** full

### Behavior Inventory

| Behavior | Coverage | Evidence |
|----------|----------|----------|
| greet(name) returns greeting | Covered | Verified by test_greet |

### Prioritized Gaps
_No prioritized gaps._

### Summary
- Covered: 1
- Shallow: 0
- Missing: 0
- P0: 0
- P1: 0
- P2: 0
EOF
""",
    )

    env = os.environ.copy()
    env["PATH"] = f"{fake_bin}:{env['PATH']}"
    env["CLAUDE_MODEL"] = "sonnet"
    env["GEMINI_MODEL"] = "gemini-diag"
    env["CODEX_MODEL"] = "codex-diag"

    result = _run(
        [
            str(TEST_REVIEW),
            "--provider",
            "claude",
            str(module_dir),
            "--tests",
            str(tests_dir),
            "--output",
            str(project / ".agents/reviews"),
        ],
        project,
        env,
    )

    assert result.returncode == 0, result.stderr
    assert "Trying provider: Claude" in result.stderr
    assert "Claude budget: $2.00" in result.stderr
    assert "Claude model override: sonnet" in result.stderr
    assert "Gemini model override:" not in result.stderr
    assert "Codex model override:" not in result.stderr
    assert "--model sonnet" in claude_log.read_text(encoding="utf-8")


@pytest.mark.unit
def test_test_review_reports_gemini_provider_diagnostics(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()

    module_dir = project / "module"
    tests_dir = project / "tests"
    module_dir.mkdir()
    tests_dir.mkdir()
    (module_dir / "feature.py").write_text(
        "def greet(name: str) -> str:\n    return f'Hello, {name}'\n",
        encoding="utf-8",
    )
    (tests_dir / "test_feature.py").write_text(
        "from module.feature import greet\n\n\ndef test_greet():\n    assert greet('A') == 'Hello, A'\n",
        encoding="utf-8",
    )

    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    gemini_log = tmp_path / "audit-gemini-diagnostics.log"

    _write_executable(
        fake_bin / "gemini",
        f"""#!/usr/bin/env bash
echo "$@" > "{gemini_log}"
cat >/dev/null
cat <<'EOF'
## Test Gap Report: feature

**Module:** `module/feature.py`
**Tests:** `tests/test_feature.py`
**Mode:** full

### Behavior Inventory

| Behavior | Coverage | Evidence |
|----------|----------|----------|
| greet(name) returns greeting | Covered | Verified by test_greet |

### Prioritized Gaps
_No prioritized gaps._

### Summary
- Covered: 1
- Shallow: 0
- Missing: 0
- P0: 0
- P1: 0
- P2: 0
EOF
""",
    )

    env = os.environ.copy()
    env["PATH"] = f"{fake_bin}:{env['PATH']}"
    env["GEMINI_MODEL"] = "gemini-diag"
    env["CLAUDE_MODEL"] = "sonnet"
    env["CODEX_MODEL"] = "codex-diag"

    result = _run(
        [
            str(TEST_REVIEW),
            "--provider",
            "gemini",
            str(module_dir),
            "--tests",
            str(tests_dir),
            "--output",
            str(project / ".agents/reviews"),
        ],
        project,
        env,
    )

    assert result.returncode == 0, result.stderr
    assert "Trying provider: Gemini" in result.stderr
    assert "Gemini model override: gemini-diag" in result.stderr
    assert "Claude budget:" not in result.stderr
    assert "Claude model override:" not in result.stderr
    assert "Codex model override:" not in result.stderr
