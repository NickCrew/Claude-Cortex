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
#   --debug           Save prompt and Claude output to log files for debugging
#
# Environment:
#   CLAUDE_TIMEOUT     Timeout in seconds (default: 600)
#   CLAUDE_MAX_TURNS   Max agent turns (default: 40)
#   CLAUDE_DEBUG=1     Same as --debug flag
#
# Examples:
#   # Full audit of a module
#   test-review-request.sh src/parser
#
#   # Debug mode — saves logs next to the report
#   test-review-request.sh src/parser --debug
#
#   # Quick review of specific test files
#   test-review-request.sh --quick tests/test_parser.py
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
DEBUG="${CLAUDE_DEBUG:-0}"

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
        --debug)
            DEBUG=1
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

# --- Debug logging setup ---

if [[ "$DEBUG" == "1" ]]; then
    PROMPT_LOG="$OUTPUT_DIR/test-audit-$TIMESTAMP.prompt.md"
    CLAUDE_LOG="$OUTPUT_DIR/test-audit-$TIMESTAMP.claude.log"
else
    PROMPT_LOG=""
    CLAUDE_LOG=""
fi

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

# Save prompt to debug log
if [[ -n "$PROMPT_LOG" ]]; then
    cp "$PROMPT_FILE" "$PROMPT_LOG"
    echo "Debug: prompt saved to $PROMPT_LOG" >&2
fi

# --- Invoke Claude CLI ---

TIMEOUT="${CLAUDE_TIMEOUT:-600}"
MAX_TURNS="${CLAUDE_MAX_TURNS:-40}"

echo "Starting test coverage audit ($MODE mode)..." >&2
echo "Module: $MODULE_PATH" >&2
echo "Tests: $TEST_PATH" >&2
echo "Output: $OUTPUT_FILE" >&2
echo "Timeout: ${TIMEOUT}s, Max turns: $MAX_TURNS" >&2
if [[ "$DEBUG" == "1" ]]; then
    echo "Debug: claude output → $CLAUDE_LOG" >&2
fi

# Route Claude output to log file in debug mode, /dev/null otherwise
if [[ -n "$CLAUDE_LOG" ]]; then
    CLAUDE_STDOUT="$CLAUDE_LOG"
else
    CLAUDE_STDOUT="/dev/null"
fi

START_TIME=$(date +%s)

if timeout "$TIMEOUT" claude --print --dangerously-skip-permissions --max-turns "$MAX_TURNS" "$PROMPT" > "$CLAUDE_STDOUT" 2>&1; then
    ELAPSED=$(( $(date +%s) - START_TIME ))
    echo "Claude finished in ${ELAPSED}s" >&2

    if [[ -f "$OUTPUT_FILE" ]]; then
        echo "$OUTPUT_FILE"
    else
        echo "Error: Claude completed but report was not created at $OUTPUT_FILE" >&2
        if [[ -n "$CLAUDE_LOG" ]]; then
            echo "Debug: check Claude output at $CLAUDE_LOG" >&2
        fi
        exit 1
    fi
else
    EXIT_CODE=$?
    ELAPSED=$(( $(date +%s) - START_TIME ))

    if [[ "$EXIT_CODE" -eq 124 ]]; then
        echo "Error: Claude CLI timed out after ${ELAPSED}s (limit: ${TIMEOUT}s)" >&2
    else
        echo "Error: Claude CLI invocation failed (exit $EXIT_CODE) after ${ELAPSED}s" >&2
    fi

    if [[ -n "$CLAUDE_LOG" ]]; then
        echo "Debug: check Claude output at $CLAUDE_LOG" >&2
        # Show the tail of Claude's output for quick diagnosis
        if [[ -f "$CLAUDE_LOG" && -s "$CLAUDE_LOG" ]]; then
            echo "Debug: last 20 lines of Claude output:" >&2
            tail -20 "$CLAUDE_LOG" >&2
        else
            echo "Debug: Claude produced no output" >&2
        fi
    fi
    exit 1
fi
