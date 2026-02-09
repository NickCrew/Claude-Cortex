#!/usr/bin/env bash
#
# test_test_review_request.sh — Tests for the test-review-request shell-out script
#
# Usage:
#   bash tests/integration/agents/test_test_review_request.sh
#
# Requires: bash 4+, runs from repo root

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
SCRIPT="$REPO_ROOT/agents/skills/test-review-request/scripts/test-review-request.sh"
MOCK_CLAUDE="$REPO_ROOT/tests/integration/agents/mock_claude.sh"

# --- Test infrastructure ---

PASS=0
FAIL=0
TMPDIR_BASE=""
SAVED_PATH=""

setup() {
    TMPDIR_BASE=$(mktemp -d /tmp/test-review-request-test.XXXXXX)

    # Create mock module structures
    mkdir -p "$TMPDIR_BASE/src/parser/tests"
    echo "# parser module" > "$TMPDIR_BASE/src/parser/mod.rs"
    echo "# parser tests" > "$TMPDIR_BASE/src/parser/tests/test_parse.rs"

    mkdir -p "$TMPDIR_BASE/tests/parser"
    echo "# sibling tests" > "$TMPDIR_BASE/tests/parser/test_parse.rs"

    mkdir -p "$TMPDIR_BASE/solo_module"
    echo "# no tests nearby" > "$TMPDIR_BASE/solo_module/lib.rs"

    mkdir -p "$TMPDIR_BASE/quick_test"
    echo "# a test file" > "$TMPDIR_BASE/quick_test/test_foo.py"

    # Put mock claude on PATH (ahead of real claude)
    mkdir -p "$TMPDIR_BASE/bin"
    cp "$MOCK_CLAUDE" "$TMPDIR_BASE/bin/claude"
    chmod +x "$TMPDIR_BASE/bin/claude"

    SAVED_PATH="$PATH"
    export PATH="$TMPDIR_BASE/bin:$PATH"
}

teardown() {
    export PATH="$SAVED_PATH"
    if [[ -n "$TMPDIR_BASE" && -d "$TMPDIR_BASE" ]]; then
        rm -rf "$TMPDIR_BASE"
    fi
}

pass() {
    PASS=$((PASS + 1))
    echo "  PASS: $1"
}

fail() {
    FAIL=$((FAIL + 1))
    echo "  FAIL: $1"
    if [[ -n "${2:-}" ]]; then
        echo "        $2"
    fi
}

assert_exit() {
    local expected="$1" actual="$2" label="$3"
    if [[ "$expected" == "$actual" ]]; then
        pass "$label"
    else
        fail "$label" "expected exit $expected, got $actual"
    fi
}

assert_contains() {
    local haystack="$1" needle="$2" label="$3"
    if echo "$haystack" | grep -qF "$needle"; then
        pass "$label"
    else
        fail "$label" "expected output to contain '$needle'"
    fi
}

assert_not_contains() {
    local haystack="$1" needle="$2" label="$3"
    if echo "$haystack" | grep -qF "$needle"; then
        fail "$label" "expected output NOT to contain '$needle'"
    else
        pass "$label"
    fi
}

assert_file_exists() {
    local path="$1" label="$2"
    if [[ -f "$path" ]]; then
        pass "$label"
    else
        fail "$label" "file not found: $path"
    fi
}

# --- Tests ---

test_missing_module_path() {
    echo "# Missing module path"
    local out rc=0
    out=$(bash "$SCRIPT" 2>&1) || rc=$?
    assert_exit 1 "$rc" "exits 1 when no module path given"
    assert_contains "$out" "Module path is required" "prints usage error"
}

test_nonexistent_module_path() {
    echo "# Non-existent module path"
    local out rc=0
    out=$(bash "$SCRIPT" "/no/such/path" 2>&1) || rc=$?
    assert_exit 1 "$rc" "exits 1 for non-existent path"
    assert_contains "$out" "Module path not found" "prints path error"
}

test_full_audit_success() {
    echo "# Full audit — success"
    local outdir="$TMPDIR_BASE/out_full"
    local stdout stderr rc=0
    export MOCK_CLAUDE_MODE="success"

    # Capture stdout (report path) and stderr separately
    stderr_file="$TMPDIR_BASE/stderr_full"
    stdout=$(bash "$SCRIPT" "$TMPDIR_BASE/src/parser" --output "$outdir" 2>"$stderr_file") || rc=$?

    assert_exit 0 "$rc" "exits 0 on successful audit"

    if [[ -n "$stdout" ]]; then
        assert_file_exists "$stdout" "report file exists at stdout path"
        local content
        content=$(cat "$stdout")
        assert_contains "$content" "Test Coverage Audit Report" "report has expected content"
    else
        fail "stdout contains report path" "stdout was empty"
    fi
}

test_quick_mode() {
    echo "# Quick mode"
    local outdir="$TMPDIR_BASE/out_quick"
    local stderr_file="$TMPDIR_BASE/stderr_quick"
    local rc=0
    export MOCK_CLAUDE_MODE="success"
    bash "$SCRIPT" --quick "$TMPDIR_BASE/quick_test/test_foo.py" --output "$outdir" 2>"$stderr_file" 1>/dev/null || rc=$?
    local stderr
    stderr=$(cat "$stderr_file")
    assert_contains "$stderr" "quick mode" "stderr shows quick mode"
}

test_explicit_test_path() {
    echo "# Explicit --tests path"
    local outdir="$TMPDIR_BASE/out_explicit"
    local stderr_file="$TMPDIR_BASE/stderr_explicit"
    export MOCK_CLAUDE_MODE="success"
    bash "$SCRIPT" "$TMPDIR_BASE/src/parser" --tests "$TMPDIR_BASE/tests/parser" --output "$outdir" 2>"$stderr_file" 1>/dev/null || true
    local stderr
    stderr=$(cat "$stderr_file")
    assert_contains "$stderr" "Tests: $TMPDIR_BASE/tests/parser" "uses explicit test path"
}

test_auto_discover_nested_tests() {
    echo "# Auto-discover tests/ inside module"
    local outdir="$TMPDIR_BASE/out_discover"
    local stderr_file="$TMPDIR_BASE/stderr_discover"
    export MOCK_CLAUDE_MODE="success"
    bash "$SCRIPT" "$TMPDIR_BASE/src/parser" --output "$outdir" 2>"$stderr_file" 1>/dev/null || true
    local stderr
    stderr=$(cat "$stderr_file")
    assert_contains "$stderr" "Tests: $TMPDIR_BASE/src/parser/tests" "discovers tests/ inside module"
}

test_auto_discover_fallback() {
    echo "# Auto-discover fallback to (auto-discover)"
    local outdir="$TMPDIR_BASE/out_fallback"
    local stderr_file="$TMPDIR_BASE/stderr_fallback"
    export MOCK_CLAUDE_MODE="success"
    # solo_module has no test dirs — run from a dir with no tests/ either
    (cd "$TMPDIR_BASE/solo_module" && bash "$SCRIPT" "$TMPDIR_BASE/solo_module" --output "$outdir" 2>"$stderr_file" 1>/dev/null) || true
    local stderr
    stderr=$(cat "$stderr_file")
    assert_contains "$stderr" "auto-discover" "falls back to auto-discover warning"
}

test_claude_fails() {
    echo "# Claude CLI fails"
    local outdir="$TMPDIR_BASE/out_fail"
    local out rc=0
    export MOCK_CLAUDE_MODE="fail"
    out=$(bash "$SCRIPT" "$TMPDIR_BASE/src/parser" --output "$outdir" 2>&1) || rc=$?
    assert_exit 1 "$rc" "exits 1 when claude fails"
    assert_contains "$out" "Claude CLI invocation failed" "prints invocation error"
}

test_claude_succeeds_no_report() {
    echo "# Claude exits 0 but no report file"
    local outdir="$TMPDIR_BASE/out_noreport"
    local out rc=0
    export MOCK_CLAUDE_MODE="no_report"
    out=$(bash "$SCRIPT" "$TMPDIR_BASE/src/parser" --output "$outdir" 2>&1) || rc=$?
    assert_exit 1 "$rc" "exits 1 when report missing"
    assert_contains "$out" "report was not created" "prints missing report error"
}

test_prompt_substitution() {
    echo "# Prompt template substitution"
    local outdir="$TMPDIR_BASE/out_prompt"
    local prompt_dump="$TMPDIR_BASE/captured_prompt.txt"
    export MOCK_CLAUDE_MODE="fail"
    export MOCK_CLAUDE_PROMPT_DUMP="$prompt_dump"

    bash "$SCRIPT" "$TMPDIR_BASE/src/parser" --tests "$TMPDIR_BASE/tests/parser" --output "$outdir" 2>/dev/null || true

    unset MOCK_CLAUDE_PROMPT_DUMP

    if [[ -f "$prompt_dump" ]]; then
        local prompt
        prompt=$(cat "$prompt_dump")
        assert_not_contains "$prompt" '{{MODULE_PATH}}' "MODULE_PATH placeholder replaced"
        assert_not_contains "$prompt" '{{TEST_PATH}}' "TEST_PATH placeholder replaced"
        assert_not_contains "$prompt" '{{OUTPUT_FILE}}' "OUTPUT_FILE placeholder replaced"
        assert_not_contains "$prompt" '{{MODE}}' "MODE placeholder replaced"
        assert_contains "$prompt" "$TMPDIR_BASE/src/parser" "prompt contains actual module path"
        assert_contains "$prompt" "$TMPDIR_BASE/tests/parser" "prompt contains actual test path"
        assert_contains "$prompt" "full" "prompt contains mode value"
    else
        fail "prompt captured" "dump file not found at $prompt_dump"
    fi
}

test_output_dir_created() {
    echo "# Output directory auto-created"
    local outdir="$TMPDIR_BASE/nested/deep/output"
    export MOCK_CLAUDE_MODE="success"
    bash "$SCRIPT" "$TMPDIR_BASE/src/parser" --output "$outdir" 2>/dev/null 1>/dev/null || true
    if [[ -d "$outdir" ]]; then
        pass "nested output directory created"
    else
        fail "nested output directory created" "directory not found: $outdir"
    fi
}

test_timeout() {
    echo "# Claude CLI timeout"
    local outdir="$TMPDIR_BASE/out_timeout"
    local out rc=0
    export MOCK_CLAUDE_MODE="hang"
    export CLAUDE_TIMEOUT=2
    out=$(bash "$SCRIPT" "$TMPDIR_BASE/src/parser" --output "$outdir" 2>&1) || rc=$?
    unset CLAUDE_TIMEOUT
    assert_exit 1 "$rc" "exits 1 on timeout"
    assert_contains "$out" "timed out" "prints timeout error"
}

test_temp_file_cleanup() {
    echo "# Temp prompt file cleaned up"
    # Count existing temp files before
    local before after
    before=$(ls /tmp/test-review-request-prompt.* 2>/dev/null | wc -l || echo 0)
    export MOCK_CLAUDE_MODE="fail"
    bash "$SCRIPT" "$TMPDIR_BASE/src/parser" --output "$TMPDIR_BASE/out_cleanup" 2>/dev/null || true
    after=$(ls /tmp/test-review-request-prompt.* 2>/dev/null | wc -l || echo 0)
    if [[ "$after" -le "$before" ]]; then
        pass "temp file cleaned up after failure"
    else
        fail "temp file cleaned up after failure" "found leftover temp files ($before before, $after after)"
    fi
}

# --- Runner ---

main() {
    echo "=== test-review-request.sh tests ==="
    echo ""

    setup
    trap teardown EXIT

    test_missing_module_path
    echo ""
    test_nonexistent_module_path
    echo ""
    test_full_audit_success
    echo ""
    test_quick_mode
    echo ""
    test_explicit_test_path
    echo ""
    test_auto_discover_nested_tests
    echo ""
    test_auto_discover_fallback
    echo ""
    test_claude_fails
    echo ""
    test_claude_succeeds_no_report
    echo ""
    test_prompt_substitution
    echo ""
    test_output_dir_created
    echo ""
    test_timeout
    echo ""
    test_temp_file_cleanup

    echo ""
    echo "=== Results: $PASS passed, $FAIL failed ==="

    if [[ "$FAIL" -gt 0 ]]; then
        exit 1
    fi
}

main "$@"
