#!/usr/bin/env bash
#
# specialist-review.sh — Invoke a multi-perspective specialist review via Claude/Gemini CLI
#
# Usage:
#   specialist-review.sh [options] [-- path...]
#   specialist-review.sh <diff-file> [--output <dir>]
#   cat changes.diff | specialist-review.sh - [--output <dir>]
#
# Options:
#   --git [base-ref]       Diff against base-ref (default: HEAD~1)
#   --output <dir>         Output directory (default: .agents/reviews)
#   --prior-review <file>  Include previous review output for continuity across cycles
#   --provider <name>      auto (default), claude, or gemini
#   -- path...             Limit git diff to these paths (passed to git diff)
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
source "$SCRIPT_DIR/review-provider.sh"

PROMPT_TEMPLATE="$SKILL_DIR/references/review-prompt.md"
PERSPECTIVE_CATALOG="$SKILL_DIR/references/perspective-catalog.md"
VALIDATOR="$SCRIPT_DIR/validate-review-contract.py"

# Find repo root from caller's CWD (not SKILL_DIR, which follows symlinks
# to the skill's physical location — likely a different repo).
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || {
  echo "Error: Not inside a git repository. Run this from within the repo you want to review." >&2
  exit 1
}

# --- Argument parsing ---

DIFF_SOURCE="--git"
OUTPUT_DIR="$REPO_ROOT/.agents/reviews"
BASE_REF="HEAD~1"
CONTEXT_LINES="${REVIEW_CONTEXT:-15}"
PRIOR_REVIEW_FILE=""
PATH_FILTERS=()
REQUESTED_PROVIDER="${SPECIALIST_REVIEW_PROVIDER:-${AGENT_LOOPS_LLM_PROVIDER:-auto}}"

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
  --prior-review)
    shift
    PRIOR_REVIEW_FILE="${1:-}"
    if [[ -z "$PRIOR_REVIEW_FILE" || ! -f "$PRIOR_REVIEW_FILE" ]]; then
      echo "Error: --prior-review requires a valid file path" >&2
      exit 1
    fi
    shift
    ;;
  --output)
    shift
    OUTPUT_DIR="${1:-$REPO_ROOT/.agents/reviews}"
    shift
    ;;
  --provider)
    shift
    REQUESTED_PROVIDER="${1:-}"
    if [[ -z "$REQUESTED_PROVIDER" ]]; then
      echo "Error: --provider requires auto, claude, or gemini" >&2
      exit 1
    fi
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
  if ! git diff -U"$CONTEXT_LINES" "${GIT_DIFF_ARGS[@]}" >"$DIFF_FILE" 2>/dev/null; then
    # Fallback: staged + unstaged only (base-ref may not exist)
    if [[ ${#PATH_FILTERS[@]} -gt 0 ]]; then
      git diff -U"$CONTEXT_LINES" HEAD -- "${PATH_FILTERS[@]}" >"$DIFF_FILE" 2>/dev/null || \
        git diff -U"$CONTEXT_LINES" -- "${PATH_FILTERS[@]}" >"$DIFF_FILE"
    else
      git diff -U"$CONTEXT_LINES" HEAD >"$DIFF_FILE" 2>/dev/null || \
        git diff -U"$CONTEXT_LINES" >"$DIFF_FILE"
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

if ! mkdir -p "$OUTPUT_DIR" 2>/dev/null; then
  echo "Error: Cannot create output directory: $OUTPUT_DIR" >&2
  echo "Check permissions or use --output <dir> to specify an alternative." >&2
  exit 1
fi
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

# Inline the perspective catalog, diff, and prior review into the prompt
python3 -c "
import sys
with open(sys.argv[1], 'r') as f:
    template = f.read()
with open(sys.argv[2], 'r') as f:
    catalog = f.read()
with open(sys.argv[3], 'r') as f:
    diff = f.read()
prior = '_No prior review — this is the first review cycle._'
if len(sys.argv) > 5 and sys.argv[5]:
    with open(sys.argv[5], 'r') as f:
        prior = f.read()
result = template.replace('{{PERSPECTIVE_CATALOG}}', catalog) \
                 .replace('{{DIFF_CONTENT}}', diff) \
                 .replace('{{PRIOR_REVIEW}}', prior)
with open(sys.argv[4], 'w') as f:
    f.write(result)
" "$PROMPT_TEMPLATE" "$PERSPECTIVE_CATALOG" "$DIFF_FILE" "$PROMPT_FILE" "$PRIOR_REVIEW_FILE"

# --- Invoke provider CLI ---

# Environment variables:
#   AGENT_LOOPS_LLM_PROVIDER  — Default provider selection: auto|claude|gemini
#   SPECIALIST_REVIEW_PROVIDER — Override provider selection for this script only
#   CLAUDE_TIMEOUT            — Max seconds for Claude CLI (default: 300)
#   GEMINI_TIMEOUT            — Max seconds for Gemini CLI (default: 300)
#   CLAUDE_MAX_BUDGET         — Max USD budget per Claude invocation (default: 0.50)
#   GEMINI_MODEL              — Optional Gemini model override
#   REVIEW_CONTEXT            — Lines of diff context, passed as -U<n> to git diff (default: 15)
DEFAULT_TIMEOUT=300

PROMPT_SIZE=$(wc -c <"$PROMPT_FILE" | tr -d ' ')
echo "Starting specialist review ($DIFF_LINES lines, prompt ${PROMPT_SIZE} bytes)..." >&2
echo "Output: $OUTPUT_FILE" >&2
echo "Requested provider: $REQUESTED_PROVIDER" >&2

# --- Pre-flight checks ---

if [[ ! -s "$PROMPT_FILE" ]]; then
  echo "Error: Prompt file is empty after template substitution." >&2
  echo "Check that $PROMPT_TEMPLATE and $PERSPECTIVE_CATALOG exist." >&2
  exit 1
fi

mapfile -t PROVIDERS < <(review_provider_candidates "$REQUESTED_PROVIDER") || exit 1

AVAILABLE_PROVIDER_FOUND=0

for PROVIDER in "${PROVIDERS[@]}"; do
  if ! review_provider_is_available "$PROVIDER"; then
    if [[ "$REQUESTED_PROVIDER" == "auto" ]]; then
      echo "Provider '$PROVIDER' is not available in PATH; trying next fallback." >&2
      continue
    fi

    echo "Error: Requested provider '$PROVIDER' is not available in PATH." >&2
    echo "Install '$PROVIDER' or use --provider auto." >&2
    exit 1
  fi

  AVAILABLE_PROVIDER_FOUND=1
  STDERR_LOG="$OUTPUT_DIR/review-$TIMESTAMP.$PROVIDER.stderr.log"
  TIMEOUT_SECONDS="$(review_provider_timeout "$PROVIDER" "$DEFAULT_TIMEOUT")"

  echo "Trying provider: $(review_provider_display_name "$PROVIDER") (timeout ${TIMEOUT_SECONDS}s)" >&2
  if [[ "$PROVIDER" == "claude" ]]; then
    echo "Claude budget: \$${CLAUDE_MAX_BUDGET:-0.50}" >&2
  elif [[ -n "${GEMINI_MODEL:-}" ]]; then
    echo "Gemini model override: ${GEMINI_MODEL}" >&2
  fi

  rm -f "$OUTPUT_FILE"
  START_TIME=$(date +%s)

  if review_provider_run "$PROVIDER" "$PROMPT_FILE" "$OUTPUT_FILE" "$STDERR_LOG" "$TIMEOUT_SECONDS"; then
    ELAPSED=$(($(date +%s) - START_TIME))
    echo "$(review_provider_display_name "$PROVIDER") finished in ${ELAPSED}s" >&2

    if [[ -s "$OUTPUT_FILE" ]]; then
      if python3 "$VALIDATOR" code-review "$OUTPUT_FILE" >/dev/null 2>&1; then
        rm -f "$STDERR_LOG"
        python3 -m claude_ctx_py.review_parser "$OUTPUT_FILE" 2>/dev/null || true
        echo "$OUTPUT_FILE"
        exit 0
      fi

      echo "Error: $(review_provider_display_name "$PROVIDER") output did not match the code review contract." >&2
      python3 "$VALIDATOR" code-review "$OUTPUT_FILE" >&2 || true
      PARTIAL_OUTPUT="$OUTPUT_DIR/review-$TIMESTAMP.$PROVIDER.invalid.md"
      mv "$OUTPUT_FILE" "$PARTIAL_OUTPUT"
      echo "Invalid output saved to: $PARTIAL_OUTPUT" >&2
      if [[ "$REQUESTED_PROVIDER" == "auto" ]]; then
        echo "Trying next provider fallback..." >&2
        continue
      fi
      exit 1
    fi

    echo "Error: $(review_provider_display_name "$PROVIDER") completed (exit 0) but review file is empty." >&2
    echo "  Prompt size: ${PROMPT_SIZE} bytes" >&2
  else
    EXIT_CODE=$?
    ELAPSED=$(($(date +%s) - START_TIME))

    if [[ "$EXIT_CODE" -eq 124 ]]; then
      echo "Error: $(review_provider_display_name "$PROVIDER") timed out after ${ELAPSED}s (limit: ${TIMEOUT_SECONDS}s)" >&2
    else
      echo "Error: $(review_provider_display_name "$PROVIDER") invocation failed (exit $EXIT_CODE) after ${ELAPSED}s" >&2
    fi
  fi

  if [[ -s "$STDERR_LOG" ]]; then
    echo "  $(review_provider_display_name "$PROVIDER") stderr:" >&2
    sed 's/^/    /' "$STDERR_LOG" >&2
  fi

  if [[ -s "$OUTPUT_FILE" ]]; then
    PARTIAL_OUTPUT="$OUTPUT_DIR/review-$TIMESTAMP.$PROVIDER.partial.md"
    mv "$OUTPUT_FILE" "$PARTIAL_OUTPUT"
    echo "Partial output saved to: $PARTIAL_OUTPUT" >&2
  fi

  if [[ "$REQUESTED_PROVIDER" == "auto" ]]; then
    echo "Trying next provider fallback..." >&2
    continue
  fi

  exit 1
done

if [[ "$AVAILABLE_PROVIDER_FOUND" -eq 0 ]]; then
  echo "Error: No review providers are available in PATH. Install 'claude' or 'gemini', or use the fresh-context Codex fallback." >&2
else
  echo "Error: All review providers failed. Inspect stderr logs above or use the fresh-context Codex fallback." >&2
fi
exit 1
