#!/usr/bin/env bash
#
# test-review-request.sh — Invoke a test coverage audit via Claude CLI
#
# Usage:
#   test-review-request.sh <module-path> [options]
#   test-review-request.sh --quick <test-file-path> [options]
#
# Options:
#   --tests <path>    Specify test directory (default: auto-discover)
#   --output <dir>    Output directory (default: .beads/reviews)
#   --quick           Quick review mode (anti-patterns only, no full audit)
#
# Examples:
#   # Full audit of a module
#   test-review-request.sh src/parser
#
#   # Full audit with explicit test path
#   test-review-request.sh src/parser --tests tests/parser
#
#   # Quick review of specific test files
#   test-review-request.sh --quick tests/test_parser.py
#
#   # Custom output directory
#   test-review-request.sh src/parser --output ./reports
#
# Output:
#   Writes gap report to <output-dir>/test-audit-<timestamp>.md
#   Prints the output file path to stdout on success.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
PROMPT_TEMPLATE="$SKILL_DIR/references/audit-prompt.md"

# --- Argument parsing ---

MODULE_PATH=""
TEST_PATH=""
OUTPUT_DIR=".beads/reviews"
MODE="full"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --quick)
            MODE="quick"
            shift
            if [[ $# -gt 0 && ! "$1" =~ ^-- ]]; then
                MODULE_PATH="$1"
                shift
            fi
            ;;
        --tests)
            shift
            TEST_PATH="${1:-}"
            shift
            ;;
        --output)
            shift
            OUTPUT_DIR="${1:-$OUTPUT_DIR}"
            shift
            ;;
        *)
            MODULE_PATH="$1"
            shift
            ;;
    esac
done

if [[ -z "$MODULE_PATH" ]]; then
    echo "Error: Module path is required." >&2
    echo "Usage: test-review-request.sh <module-path> [--tests <path>] [--output <dir>]" >&2
    echo "       test-review-request.sh --quick <test-file> [--output <dir>]" >&2
    exit 1
fi

if [[ ! -e "$MODULE_PATH" ]]; then
    echo "Error: Module path not found: $MODULE_PATH" >&2
    exit 1
fi

# --- Auto-discover test path if not specified ---

if [[ -z "$TEST_PATH" ]]; then
    # Common test directory patterns
    MODULE_BASE=$(basename "$MODULE_PATH")
    MODULE_PARENT=$(dirname "$MODULE_PATH")

    for candidate in \
        "${MODULE_PATH}/tests" \
        "${MODULE_PATH}/test" \
        "${MODULE_PARENT}/tests/${MODULE_BASE}" \
        "${MODULE_PARENT}/test/${MODULE_BASE}" \
        "tests/${MODULE_BASE}" \
        "tests" \
        "test"; do
        if [[ -d "$candidate" ]]; then
            TEST_PATH="$candidate"
            break
        fi
    done

    # For quick mode, the module path IS the test path
    if [[ "$MODE" == "quick" ]]; then
        TEST_PATH="$MODULE_PATH"
    fi

    if [[ -z "$TEST_PATH" ]]; then
        echo "Warning: Could not auto-discover test directory. Claude will search for tests." >&2
        TEST_PATH="(auto-discover)"
    fi
fi

# --- Prepare output ---

mkdir -p "$OUTPUT_DIR"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
OUTPUT_FILE="$OUTPUT_DIR/test-audit-$TIMESTAMP.md"

# --- Build the prompt ---

PROMPT_FILE=$(mktemp /tmp/test-review-request-prompt.XXXXXX)
trap 'rm -f "$PROMPT_FILE"' EXIT

# Substitute placeholders
sed \
    -e "s|{{MODULE_PATH}}|$MODULE_PATH|g" \
    -e "s|{{TEST_PATH}}|$TEST_PATH|g" \
    -e "s|{{OUTPUT_FILE}}|$OUTPUT_FILE|g" \
    -e "s|{{MODE}}|$MODE|g" \
    "$PROMPT_TEMPLATE" > "$PROMPT_FILE"

PROMPT=$(cat "$PROMPT_FILE")

# --- Invoke Claude CLI ---

TIMEOUT="${CLAUDE_TIMEOUT:-300}"
MAX_TURNS="${CLAUDE_MAX_TURNS:-25}"

echo "Starting test coverage audit ($MODE mode)..." >&2
echo "Module: $MODULE_PATH" >&2
echo "Tests: $TEST_PATH" >&2
echo "Output: $OUTPUT_FILE" >&2
echo "Timeout: ${TIMEOUT}s, Max turns: $MAX_TURNS" >&2

if timeout "$TIMEOUT" claude --print --dangerously-skip-permissions --max-turns "$MAX_TURNS" "$PROMPT" > /dev/null 2>&1; then
    if [[ -f "$OUTPUT_FILE" ]]; then
        echo "$OUTPUT_FILE"
    else
        echo "Error: Claude completed but report was not created at $OUTPUT_FILE" >&2
        exit 1
    fi
else
    EXIT_CODE=$?
    if [[ "$EXIT_CODE" -eq 124 ]]; then
        echo "Error: Claude CLI timed out after ${TIMEOUT}s" >&2
    else
        echo "Error: Claude CLI invocation failed (exit $EXIT_CODE)" >&2
    fi
    exit 1
fi
