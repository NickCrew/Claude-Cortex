#!/usr/bin/env bash
#
# specialist-review.sh — Invoke a multi-perspective specialist review via Claude/Gemini/Codex CLI
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
#   --provider <name>      auto (default), claude, gemini, or codex
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

create_temp_markdown() {
  local prefix="$1"
  local base_path=""
  base_path="$(mktemp "${prefix}.XXXXXX")"
  local markdown_path="${base_path}.md"
  mv "$base_path" "$markdown_path"
  printf '%s\n' "$markdown_path"
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
      echo "Error: --provider requires auto, claude, gemini, or codex" >&2
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

# --- Reject test files in path filters ---
# specialist-review is for source files only. Test files belong in Loop 2
# via test-review-request.sh.
if [[ ${#PATH_FILTERS[@]} -gt 0 ]]; then
  TEST_FILES=()
  for pf in "${PATH_FILTERS[@]}"; do
    if [[ "$pf" =~ \.(test|spec)\. ]] || [[ "$pf" =~ /__tests__/ ]]; then
      TEST_FILES+=("$pf")
    fi
  done
  if [[ ${#TEST_FILES[@]} -gt 0 ]]; then
    echo "Error: Test files detected in path filter — specialist-review is for source files only." >&2
    echo "  Move these to Loop 2 (test-review-request.sh):" >&2
    for tf in "${TEST_FILES[@]}"; do
      echo "    $tf" >&2
    done
    exit 1
  fi
fi

# --- Resolve diff content ---

DIFF_FILE=$(mktemp /tmp/specialist-review-diff.XXXXXX)
PROMPT_FILE=$(mktemp /tmp/specialist-review-prompt.XXXXXX)
_HEARTBEAT_PID=""
trap '[[ -n "$_HEARTBEAT_PID" ]] && kill "$_HEARTBEAT_PID" 2>/dev/null; rm -f "$DIFF_FILE" "$PROMPT_FILE"' EXIT

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

  # Append untracked files as synthetic diffs so new files get reviewed too.
  # git diff only covers tracked files; brand-new files are invisible until staged.
  UNTRACKED_ARGS=(--others --exclude-standard)
  if [[ ${#PATH_FILTERS[@]} -gt 0 ]]; then
    UNTRACKED_ARGS+=(-- "${PATH_FILTERS[@]}")
  fi
  while IFS= read -r ufile; do
    [[ -z "$ufile" ]] && continue
    printf '\ndiff --git a/%s b/%s\nnew file mode 100644\n--- /dev/null\n+++ b/%s\n' "$ufile" "$ufile" "$ufile" >>"$DIFF_FILE"
    # Generate +line hunks from file content
    line_count=$(wc -l <"$ufile" | tr -d ' ')
    printf '@@ -0,0 +1,%s @@\n' "$line_count" >>"$DIFF_FILE"
    sed 's/^/+/' "$ufile" >>"$DIFF_FILE"
  done < <(git ls-files "${UNTRACKED_ARGS[@]}" 2>/dev/null || true)
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

# Enforce a hard size limit. Silent truncation would hand the reviewer a
# partial diff and produce a "clean" review that never saw half the code —
# worse than no review at all. Set AGENT_LOOPS_ALLOW_TRUNCATION=1 to opt
# into the legacy truncating behavior (not recommended).
MAX_LINES="${AGENT_LOOPS_MAX_DIFF_LINES:-2000}"
if [[ "$DIFF_LINES" -gt "$MAX_LINES" ]]; then
  if [[ "${AGENT_LOOPS_ALLOW_TRUNCATION:-0}" == "1" ]]; then
    echo "Warning: Diff is $DIFF_LINES lines. Truncating to $MAX_LINES (AGENT_LOOPS_ALLOW_TRUNCATION=1)." >&2
    TRUNCATED_FILE=$(mktemp /tmp/specialist-review-trunc.XXXXXX)
    head -n "$MAX_LINES" "$DIFF_FILE" >"$TRUNCATED_FILE"
    printf '\n... [TRUNCATED: %s total lines, showing first %s] ...\n' "$DIFF_LINES" "$MAX_LINES" >>"$TRUNCATED_FILE"
    mv "$TRUNCATED_FILE" "$DIFF_FILE"
  else
    cat >&2 <<EOF
Error: Diff is $DIFF_LINES lines (limit: $MAX_LINES). Review aborted.

A diff this large cannot be reviewed reliably in a single pass — the reviewer
would miss issues and you would get a falsely clean report. Split the work
into smaller, independently-reviewable chunks and invoke this script once per
chunk.

Ways to split:
  1. By path filter — scope each review to a subset of the tree:
       specialist-review.sh --git $BASE_REF -- path/to/module1
       specialist-review.sh --git $BASE_REF -- path/to/module2

  2. By ref range — review each commit (or commit pair) separately:
       specialist-review.sh --git HEAD~3
       specialist-review.sh --git HEAD~2
       specialist-review.sh --git HEAD~1

  3. By logical scope — if the change bundles unrelated concerns (bug fix
     + feature, refactor + behavior change), split the branch first. See
     "When to Split" in skills/agent-loops/SKILL.md.

Reduce diff context with REVIEW_CONTEXT=<n> (currently $CONTEXT_LINES) only
if the signal-to-noise ratio is the problem, not the scope.

To bypass this check (not recommended — produces unreliable reviews), set:
  AGENT_LOOPS_ALLOW_TRUNCATION=1
EOF
    exit 1
  fi
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
#   AGENT_LOOPS_LLM_PROVIDER   — Default provider selection: auto|claude|gemini|codex
#   AGENT_LOOPS_SELF_PROVIDER  — Current agent provider for self-last auto ordering
#                                 (auto-detects Codex/Gemini/Claude when session markers exist)
#   SPECIALIST_REVIEW_PROVIDER — Override provider selection for this script only
#   CLAUDE_TIMEOUT            — Max seconds for Claude CLI (default: 300)
#   GEMINI_TIMEOUT            — Max seconds for Gemini CLI (default: 300)
#   CODEX_TIMEOUT             — Max seconds for Codex CLI (default: 300)
#   CLAUDE_MAX_BUDGET         — Max USD budget per Claude invocation (default: 2.00)
#   CLAUDE_MODEL              — Optional Claude model override
#   GEMINI_MODEL              — Optional Gemini model override
#   CODEX_MODEL               — Optional Codex model override
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

SELF_PROVIDER="$(review_provider_detect_self)"
mapfile -t PROVIDERS < <(review_provider_candidates "$REQUESTED_PROVIDER" "$SELF_PROVIDER") || exit 1

if [[ "$REQUESTED_PROVIDER" == "auto" ]]; then
  if [[ -n "$SELF_PROVIDER" ]]; then
    echo "Self provider: $SELF_PROVIDER (kept last in auto order)" >&2
  else
    echo "Self provider: unknown (set AGENT_LOOPS_SELF_PROVIDER=claude|gemini|codex to keep same-model reviews last)" >&2
  fi
  echo "Auto provider order: ${PROVIDERS[*]}" >&2
fi

# Emit a structured failure summary to stdout so the calling agent can report
# diagnostics.  Stderr logs and partial outputs use the timestamped naming
# convention so we can glob for them without tracking state during the loop.
_emit_failure_summary() {
  local reason="${1:-unknown}"
  echo ""
  echo "[REVIEW FAILED] $reason"
  echo "Prompt size: ${PROMPT_SIZE} bytes"
  echo "Diff lines:  ${DIFF_LINES}"
  echo "Diff source: ${DIFF_SOURCE} (base: ${BASE_REF})"
  if [[ ${#PATH_FILTERS[@]} -gt 0 ]]; then
    echo "Path filters: ${PATH_FILTERS[*]}"
  fi
  echo "Provider:    ${REQUESTED_PROVIDER}"
  echo "Output dir:  ${OUTPUT_DIR}"
  echo ""
  local found_log=0
  for log in "$OUTPUT_DIR"/review-"$TIMESTAMP".*.stderr.log; do
    [[ -f "$log" ]] || continue
    found_log=1
    echo "Stderr log: $log"
  done
  for partial in "$OUTPUT_DIR"/review-"$TIMESTAMP".*.partial.md "$OUTPUT_DIR"/review-"$TIMESTAMP".*.invalid.md; do
    [[ -f "$partial" ]] || continue
    echo "Artifact:   $partial"
  done
  if [[ "$found_log" -eq 0 ]]; then
    echo "Stderr logs: (none — providers may have been unavailable)"
  fi
}

# Emit periodic progress so calling agents don't time out during long provider runs.
_heartbeat_start() {
  local display_name="$1" start_time="$2"
  (while true; do
    sleep 15
    echo "  [$display_name] Waiting for response ($(($(date +%s) - start_time))s elapsed)..." >&2
  done) &
  _HEARTBEAT_PID=$!
}
_heartbeat_stop() {
  if [[ -n "${_HEARTBEAT_PID:-}" ]]; then
    kill "$_HEARTBEAT_PID" 2>/dev/null
    wait "$_HEARTBEAT_PID" 2>/dev/null || true
    _HEARTBEAT_PID=""
  fi
}

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
    echo "Claude budget: \$${CLAUDE_MAX_BUDGET:-2.00}" >&2
    if [[ -n "${CLAUDE_MODEL:-}" ]]; then
      echo "Claude model override: ${CLAUDE_MODEL}" >&2
    fi
  elif [[ -n "${GEMINI_MODEL:-}" ]]; then
    echo "Gemini model override: ${GEMINI_MODEL}" >&2
  elif [[ "$PROVIDER" == "codex" && -n "${CODEX_MODEL:-}" ]]; then
    echo "Codex model override: ${CODEX_MODEL}" >&2
  fi

  rm -f "$OUTPUT_FILE"
  START_TIME=$(date +%s)
  _heartbeat_start "$(review_provider_display_name "$PROVIDER")" "$START_TIME"

  if review_provider_run "$PROVIDER" "$PROMPT_FILE" "$OUTPUT_FILE" "$STDERR_LOG" "$TIMEOUT_SECONDS"; then
    _heartbeat_stop
    ELAPSED=$(($(date +%s) - START_TIME))
    echo "$(review_provider_display_name "$PROVIDER") finished in ${ELAPSED}s" >&2

    if [[ -s "$OUTPUT_FILE" ]]; then
      if python3 "$VALIDATOR" code-review "$OUTPUT_FILE" >/dev/null 2>&1; then
        rm -f "$STDERR_LOG"
        python3 -m claude_ctx_py.review_parser "$OUTPUT_FILE" 2>/dev/null || true
        echo "$OUTPUT_FILE"
        exit 0
      fi

      NORMALIZED_OUTPUT="$(create_temp_markdown "${OUTPUT_DIR}/review-${TIMESTAMP}.${PROVIDER}.normalized")"
      NORMALIZATION_FAILED=0
      if ! python3 "$VALIDATOR" normalize-code-review "$OUTPUT_FILE" >"$NORMALIZED_OUTPUT" 2>>"$STDERR_LOG"; then
        NORMALIZATION_FAILED=1
      elif python3 "$VALIDATOR" code-review "$NORMALIZED_OUTPUT" >/dev/null 2>&1; then
        if ! cmp -s "$OUTPUT_FILE" "$NORMALIZED_OUTPUT"; then
          RAW_OUTPUT="$OUTPUT_DIR/review-$TIMESTAMP.$PROVIDER.raw.md"
          mv "$OUTPUT_FILE" "$RAW_OUTPUT"
          mv "$NORMALIZED_OUTPUT" "$OUTPUT_FILE"
          echo "Normalized $(review_provider_display_name "$PROVIDER") output to the review contract." >&2
          echo "Raw provider output saved to: $RAW_OUTPUT" >&2
        else
          rm -f "$NORMALIZED_OUTPUT"
        fi
        rm -f "$STDERR_LOG"
        python3 -m claude_ctx_py.review_parser "$OUTPUT_FILE" 2>/dev/null || true
        echo "$OUTPUT_FILE"
        exit 0
      fi
      rm -f "$NORMALIZED_OUTPUT"
      if [[ "$NORMALIZATION_FAILED" -eq 1 ]]; then
        echo "Warning: $(review_provider_display_name "$PROVIDER") output could not be normalized; preserving raw artifact as invalid." >&2
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
      _emit_failure_summary "Contract validation failed ($PROVIDER)"
      exit 1
    fi

    echo "Error: $(review_provider_display_name "$PROVIDER") completed (exit 0) but review file is empty." >&2
    echo "  Prompt size: ${PROMPT_SIZE} bytes" >&2
    echo "  Diff lines: ${DIFF_LINES}" >&2
    echo "  Prompt head:" >&2
    head -3 "$PROMPT_FILE" | sed 's/^/    /' >&2
    echo "  Prompt tail:" >&2
    tail -3 "$PROMPT_FILE" | sed 's/^/    /' >&2
  else
    EXIT_CODE=$?
    _heartbeat_stop
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

  _emit_failure_summary "Provider $PROVIDER failed (exit ${EXIT_CODE:-1})"
  exit 1
done

if [[ "$AVAILABLE_PROVIDER_FOUND" -eq 0 ]]; then
  echo "Error: No review providers are available in PATH. Install 'claude', 'gemini', or 'codex', or use the fresh-context Codex fallback." >&2
  _emit_failure_summary "No providers available"
else
  echo "Error: All review providers failed. Inspect stderr logs above or use the fresh-context Codex fallback." >&2
  _emit_failure_summary "All providers failed"
fi
exit 1
