#!/usr/bin/env bash
#
# specialist-review.sh — Invoke a multi-perspective specialist review via Claude CLI
#
# Usage:
#   specialist-review.sh <diff-file> [output-dir]
#   specialist-review.sh --git [base-ref] [output-dir]
#   cat changes.diff | specialist-review.sh - [output-dir]
#
# Examples:
#   # Review a diff file
#   specialist-review.sh /tmp/changes.diff
#
#   # Review current uncommitted changes
#   specialist-review.sh --git
#
#   # Review changes since a specific ref
#   specialist-review.sh --git origin/main
#
#   # Pipe a diff in
#   git diff HEAD~3..HEAD | specialist-review.sh -
#
#   # Specify output directory
#   specialist-review.sh /tmp/changes.diff .beads/reviews
#
# Output:
#   Writes review to <output-dir>/review-<timestamp>.md
#   Prints the output file path to stdout on success.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
PROMPT_TEMPLATE="$SKILL_DIR/references/review-prompt.md"

# --- Argument parsing ---

DIFF_SOURCE="${1:---git}"
OUTPUT_DIR=""
BASE_REF=""

if [[ "$DIFF_SOURCE" == "--git" ]]; then
    BASE_REF="${2:-HEAD~1}"
    OUTPUT_DIR="${3:-.beads/reviews}"
elif [[ "$DIFF_SOURCE" == "-" ]]; then
    OUTPUT_DIR="${2:-.beads/reviews}"
else
    OUTPUT_DIR="${2:-.beads/reviews}"
fi

# --- Resolve diff content ---

DIFF_FILE=$(mktemp /tmp/specialist-review-diff.XXXXXX)
PROMPT_FILE=$(mktemp /tmp/specialist-review-prompt.XXXXXX)
trap 'rm -f "$DIFF_FILE" "$PROMPT_FILE"' EXIT

if [[ "$DIFF_SOURCE" == "--git" ]]; then
    if ! git diff "$BASE_REF"..HEAD > "$DIFF_FILE" 2>/dev/null; then
        git diff > "$DIFF_FILE"
    fi
    git diff --cached >> "$DIFF_FILE" 2>/dev/null || true
elif [[ "$DIFF_SOURCE" == "-" ]]; then
    cat > "$DIFF_FILE"
else
    if [[ ! -f "$DIFF_SOURCE" ]]; then
        echo "Error: Diff file not found: $DIFF_SOURCE" >&2
        exit 1
    fi
    cp "$DIFF_SOURCE" "$DIFF_FILE"
fi

if [[ ! -s "$DIFF_FILE" ]]; then
    echo "Error: Diff is empty. Nothing to review." >&2
    exit 1
fi

# --- Prepare output ---

mkdir -p "$OUTPUT_DIR"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
OUTPUT_FILE="$OUTPUT_DIR/review-$TIMESTAMP.md"

# --- Build the prompt ---

DIFF_LINES=$(wc -l < "$DIFF_FILE" | tr -d ' ')

# Truncate very large diffs
MAX_LINES=2000
if [[ "$DIFF_LINES" -gt "$MAX_LINES" ]]; then
    echo "Warning: Diff is $DIFF_LINES lines. Truncating to $MAX_LINES for review." >&2
    TRUNCATED_FILE=$(mktemp /tmp/specialist-review-trunc.XXXXXX)
    head -n "$MAX_LINES" "$DIFF_FILE" > "$TRUNCATED_FILE"
    printf '\n... [TRUNCATED: %s total lines, showing first %s] ...\n' "$DIFF_LINES" "$MAX_LINES" >> "$TRUNCATED_FILE"
    mv "$TRUNCATED_FILE" "$DIFF_FILE"
fi

DIFF_CONTENT=$(cat "$DIFF_FILE")

# Read the prompt template and substitute placeholders
sed \
    -e "s|{{SKILL_DIR}}|$SKILL_DIR|g" \
    -e "s|{{OUTPUT_FILE}}|$OUTPUT_FILE|g" \
    "$PROMPT_TEMPLATE" > "$PROMPT_FILE"

# Replace the diff content placeholder (use a different approach since diff can contain sed metacharacters)
python3 -c "
import sys
with open(sys.argv[1], 'r') as f:
    template = f.read()
with open(sys.argv[2], 'r') as f:
    diff = f.read()
result = template.replace('{{DIFF_CONTENT}}', diff)
with open(sys.argv[1], 'w') as f:
    f.write(result)
" "$PROMPT_FILE" "$DIFF_FILE"

PROMPT=$(cat "$PROMPT_FILE")

# --- Invoke Claude CLI ---

TIMEOUT="${CLAUDE_TIMEOUT:-300}"
MAX_TURNS="${CLAUDE_MAX_TURNS:-25}"

echo "Starting specialist review ($DIFF_LINES lines)..." >&2
echo "Output: $OUTPUT_FILE" >&2
echo "Timeout: ${TIMEOUT}s, Max turns: $MAX_TURNS" >&2

if timeout "$TIMEOUT" claude --print --dangerously-skip-permissions --max-turns "$MAX_TURNS" "$PROMPT" > /dev/null 2>&1; then
    if [[ -f "$OUTPUT_FILE" ]]; then
        echo "$OUTPUT_FILE"
    else
        echo "Error: Claude completed but review file was not created at $OUTPUT_FILE" >&2
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
