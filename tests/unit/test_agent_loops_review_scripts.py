from __future__ import annotations

import os
import stat
import subprocess
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
SPECIALIST_REVIEW = (
    REPO_ROOT / "codex/skills/agent-loops/scripts/specialist-review.sh"
)
TEST_REVIEW = (
    REPO_ROOT / "codex/skills/agent-loops/scripts/test-review-request.sh"
)


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


@pytest.mark.unit
def test_specialist_review_falls_back_to_gemini_when_claude_fails(tmp_path: Path) -> None:
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
