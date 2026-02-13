#!/usr/bin/env bash
#
# specialist-review.sh — Invoke a multi-perspective specialist review via Claude CLI
#
# Usage:
#   specialist-review.sh [options] [-- path...]
#   specialist-review.sh <diff-file> [--output <dir>]
#   cat changes.diff | specialist-review.sh - [--output <dir>]
#
# Options:
#   --git [base-ref]   Diff against base-ref (default: HEAD~1)
#   --output <dir>     Output directory (default: .agents/reviews)
#   -- path...         Limit git diff to these paths (passed to git diff)
#
# Examples:
#   # Review current changes vs last commit
#   specialist-review.sh --git
#
#   # Review only files you touched
#   specialist-review.sh --git -- src/parser/ src/auth.rs
#
#   # Review changes since a specific ref, scoped to a directory
#   specialist-review.sh --git origin/main -- claude_ctx_py/
#
#   # Pipe a diff in
#   git diff HEAD~3..HEAD -- src/ | specialist-review.sh -
#
#   # Review a diff file
#   specialist-review.sh /tmp/changes.diff
#
# Output:
#   Writes review to <output-dir>/review-<timestamp>.md
#   Prints the output file path to stdout on success.

set -euo pipefail

# Resolve physical paths to handle symlink invocation (e.g. ~/.codex/skills/...)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
SKILL_DIR="$(cd "$(dirname "$SCRIPT_DIR")" && pwd -P)"
PROMPT_TEMPLATE="$SKILL_DIR/references/review-prompt.md"
PERSPECTIVE_CATALOG="$SKILL_DIR/references/perspective-catalog.md"

# --- Argument parsing ---

DIFF_SOURCE="--git"
OUTPUT_DIR=".agents/reviews"
BASE_REF="HEAD~1"
PATH_FILTERS=()

while [[ $# -gt 0 ]]; do
  case "$1" in
  --git)
    DIFF_SOURCE="--git"
    shift
    # Next arg is base-ref if it doesn't start with -- or -
    if [[ $# -gt 0 && ! "$1" =~ ^- ]]; then
      BASE_REF="$1"
      shift
    fi
    ;;
  --output)
    shift
    OUTPUT_DIR="${1:-.agents/reviews}"
    shift
    ;;
  --)
    shift
    PATH_FILTERS=("$@")
    break
    ;;
  -)
    DIFF_SOURCE="-"
    shift
    ;;
  *)
    # Positional: treat as diff file
    DIFF_SOURCE="$1"
    shift
    ;;
  esac
done

# --- Resolve diff content ---

DIFF_FILE=$(mktemp /tmp/specialist-review-diff.XXXXXX)
PROMPT_FILE=$(mktemp /tmp/specialist-review-prompt.XXXXXX)
trap 'rm -f "$DIFF_FILE" "$PROMPT_FILE"' EXIT

if [[ "$DIFF_SOURCE" == "--git" ]]; then
  # Capture ALL changes vs base-ref: committed + staged + unstaged.
  # In a monorepo agents often have uncommitted work, so HEAD~1..HEAD alone
  # misses the code that actually needs review.
  GIT_DIFF_ARGS=("$BASE_REF")
  if [[ ${#PATH_FILTERS[@]} -gt 0 ]]; then
    GIT_DIFF_ARGS+=(-- "${PATH_FILTERS[@]}")
  fi
  if ! git diff "${GIT_DIFF_ARGS[@]}" >"$DIFF_FILE" 2>/dev/null; then
    # Fallback: staged + unstaged only (base-ref may not exist)
    if [[ ${#PATH_FILTERS[@]} -gt 0 ]]; then
      git diff HEAD -- "${PATH_FILTERS[@]}" >"$DIFF_FILE" 2>/dev/null || \
        git diff -- "${PATH_FILTERS[@]}" >"$DIFF_FILE"
    else
      git diff HEAD >"$DIFF_FILE" 2>/dev/null || \
        git diff >"$DIFF_FILE"
    fi
  fi
elif [[ "$DIFF_SOURCE" == "-" ]]; then
  cat >"$DIFF_FILE"
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

DIFF_LINES=$(wc -l <"$DIFF_FILE" | tr -d ' ')

# Truncate very large diffs
MAX_LINES=2000
if [[ "$DIFF_LINES" -gt "$MAX_LINES" ]]; then
  echo "Warning: Diff is $DIFF_LINES lines. Truncating to $MAX_LINES for review." >&2
  TRUNCATED_FILE=$(mktemp /tmp/specialist-review-trunc.XXXXXX)
  head -n "$MAX_LINES" "$DIFF_FILE" >"$TRUNCATED_FILE"
  printf '\n... [TRUNCATED: %s total lines, showing first %s] ...\n' "$DIFF_LINES" "$MAX_LINES" >>"$TRUNCATED_FILE"
  mv "$TRUNCATED_FILE" "$DIFF_FILE"
fi

# Inline the perspective catalog and diff into the prompt (no tool use needed)
python3 -c "
import sys
with open(sys.argv[1], 'r') as f:
    template = f.read()
with open(sys.argv[2], 'r') as f:
    catalog = f.read()
with open(sys.argv[3], 'r') as f:
    diff = f.read()
result = template.replace('{{PERSPECTIVE_CATALOG}}', catalog).replace('{{DIFF_CONTENT}}', diff)
with open(sys.argv[4], 'w') as f:
    f.write(result)
" "$PROMPT_TEMPLATE" "$PERSPECTIVE_CATALOG" "$DIFF_FILE" "$PROMPT_FILE"

# --- Invoke Claude CLI ---

TIMEOUT="${CLAUDE_TIMEOUT:-300}"
MAX_BUDGET="${CLAUDE_MAX_BUDGET:-0.50}"

echo "Starting specialist review ($DIFF_LINES lines)..." >&2
echo "Output: $OUTPUT_FILE" >&2

# Single-turn, no tools: the review is output to stdout and captured directly.
# --tools "" disables all tools so claude outputs the review as text.
# --no-session-persistence avoids writing session state to disk.
# stdin from prompt file ensures clean EOF (no TTY hang).
if timeout "$TIMEOUT" claude --print \
  --no-session-persistence \
  --max-budget-usd "$MAX_BUDGET" \
  --tools "" \
  <"$PROMPT_FILE" >"$OUTPUT_FILE"; then
  if [[ -s "$OUTPUT_FILE" ]]; then
    # Feed review outcomes into skill recommender (best-effort)
    python3 -m claude_ctx_py.review_parser "$OUTPUT_FILE" 2>/dev/null || true
    echo "$OUTPUT_FILE"
  else
    echo "Error: Claude completed but review file is empty" >&2
    exit 1
  fi
else
  EXIT_CODE=$?
  if [[ "$EXIT_CODE" -eq 124 ]]; then
    echo "Error: Claude CLI timed out after ${TIMEOUT}s" >&2
  else
    echo "Error: Claude CLI invocation failed (exit $EXIT_CODE)" >&2
  fi
  # Preserve partial output if any
  if [[ -s "$OUTPUT_FILE" ]]; then
    echo "Partial output saved to: $OUTPUT_FILE" >&2
  fi
  exit 1
fi
