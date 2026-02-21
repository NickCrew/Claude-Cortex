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
#   --output <dir>    Output directory (default: .agents/reviews)
#   --quick           Quick review mode (anti-patterns only, no full audit)
#   --debug           Save prompt and Claude output to log files for debugging
#
# Environment:
#   CLAUDE_TIMEOUT     Timeout in seconds (default: 300)
#   CLAUDE_MAX_BUDGET  Max spend in USD (default: 0.50)
#   CLAUDE_DEBUG=1     Same as --debug flag
#
# All source, test, and reference content is inlined into the prompt.
# Single-turn, no tools: Claude outputs the report to stdout.

set -euo pipefail

# Resolve physical paths to handle symlink invocation (e.g. ~/.codex/skills/...)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
SKILL_DIR="$(cd "$(dirname "$SCRIPT_DIR")" && pwd -P)"

# Find repo root from caller's CWD (not SKILL_DIR, which follows symlinks
# to the skill's physical location — likely a different repo).
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || {
  echo "Error: Not inside a git repository. Run this from within the repo you want to audit." >&2
  exit 1
}

PROMPT_TEMPLATE="$SKILL_DIR/references/audit-prompt.md"

# Reference files baked into the prompt (bundled in agent-loops/references/)
TESTING_STANDARDS="$SKILL_DIR/references/testing-standards.md"
AUDIT_WORKFLOW="$SKILL_DIR/references/audit-workflow.md"

# --- Argument parsing ---

MODULE_PATH=""
TEST_PATH=""
OUTPUT_DIR="$REPO_ROOT/.agents/reviews"
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

  if [[ "$MODE" == "quick" ]]; then
    TEST_PATH="$MODULE_PATH"
  fi

  if [[ -z "$TEST_PATH" ]]; then
    echo "Warning: Could not auto-discover test directory." >&2
    TEST_PATH="(none)"
  fi
fi

# --- Read all content for inlining ---

read_file_or_dir() {
  local path="$1"
  local label="$2"
  local content=""

  if [[ -f "$path" ]]; then
    content="### \`$path\`"$'\n\n'"\`\`\`"$'\n'"$(cat "$path")"$'\n'"\`\`\`"
  elif [[ -d "$path" ]]; then
    local found=0
    while IFS= read -r -d '' file; do
      if [[ -n "$content" ]]; then
        content="$content"$'\n\n'
      fi
      content="$content### \`$file\`"$'\n\n'"\`\`\`"$'\n'"$(cat "$file")"$'\n'"\`\`\`"
      found=$((found + 1))
    done < <(find "$path" -type f \( -name '*.py' -o -name '*.rs' -o -name '*.ts' -o -name '*.tsx' -o -name '*.js' -o -name '*.jsx' -o -name '*.go' -o -name '*.rb' -o -name '*.sh' -o -name '*.toml' -o -name '*.yaml' -o -name '*.yml' \) -print0 | sort -z)

    if [[ "$found" -eq 0 ]]; then
      content="*No source files found in \`$path\`*"
    else
      echo "  $label: $found files" >&2
    fi
  else
    content="*Path not found: \`$path\`*"
  fi

  echo "$content"
}

echo "Reading source files..." >&2
SOURCE_CONTENT=$(read_file_or_dir "$MODULE_PATH" "Source")

echo "Reading test files..." >&2
if [[ "$TEST_PATH" == "(none)" ]]; then
  TEST_CONTENT="*No test directory found. All behaviors should be marked Missing.*"
else
  TEST_CONTENT=$(read_file_or_dir "$TEST_PATH" "Tests")
fi

echo "Reading reference standards..." >&2
STANDARDS_CONTENT=""
if [[ -f "$TESTING_STANDARDS" ]]; then
  STANDARDS_CONTENT=$(cat "$TESTING_STANDARDS")
else
  echo "Warning: Testing standards not found at $TESTING_STANDARDS" >&2
fi

WORKFLOW_CONTENT=""
if [[ -f "$AUDIT_WORKFLOW" ]]; then
  WORKFLOW_CONTENT=$(cat "$AUDIT_WORKFLOW")
else
  echo "Warning: Audit workflow not found at $AUDIT_WORKFLOW" >&2
fi

# --- Prepare output ---

if ! mkdir -p "$OUTPUT_DIR" 2>/dev/null; then
  echo "Error: Cannot create output directory: $OUTPUT_DIR" >&2
  echo "Check permissions or use --output <dir> to specify an alternative." >&2
  exit 1
fi
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
OUTPUT_FILE="$OUTPUT_DIR/test-audit-$TIMESTAMP.md"

# --- Debug logging setup ---

if [[ "$DEBUG" == "1" ]]; then
  PROMPT_LOG="$OUTPUT_DIR/test-audit-$TIMESTAMP.prompt.md"
else
  PROMPT_LOG=""
fi

# --- Build the system prompt ---
#
# Use python3 for substitution since inlined content contains characters
# that break sed (backticks, slashes, regex metacharacters, etc.)

SYSTEM_PROMPT_FILE=$(mktemp /tmp/test-review-request-system.XXXXXX)
trap 'rm -f "$SYSTEM_PROMPT_FILE"' EXIT

export _STANDARDS_CONTENT="$STANDARDS_CONTENT"
export _WORKFLOW_CONTENT="$WORKFLOW_CONTENT"
export _SOURCE_CONTENT="$SOURCE_CONTENT"
export _TEST_CONTENT="$TEST_CONTENT"

python3 - "$PROMPT_TEMPLATE" "$SYSTEM_PROMPT_FILE" "$MODULE_PATH" "$TEST_PATH" "$MODE" <<'PYEOF'
import sys, os

template_path, output_path, module_path, test_path, mode = sys.argv[1:6]

with open(template_path) as f:
    template = f.read()

template = template.replace('{{MODULE_PATH}}', module_path)
template = template.replace('{{TEST_PATH}}', test_path)
template = template.replace('{{MODE}}', mode)
template = template.replace('{{TESTING_STANDARDS}}', os.environ.get('_STANDARDS_CONTENT', ''))
template = template.replace('{{AUDIT_WORKFLOW}}', os.environ.get('_WORKFLOW_CONTENT', ''))
template = template.replace('{{SOURCE_CONTENT}}', os.environ.get('_SOURCE_CONTENT', ''))
template = template.replace('{{TEST_CONTENT}}', os.environ.get('_TEST_CONTENT', ''))

with open(output_path, 'w') as f:
    f.write(template)
PYEOF

unset _STANDARDS_CONTENT _WORKFLOW_CONTENT _SOURCE_CONTENT _TEST_CONTENT

PROMPT_SIZE=$(wc -c <"$SYSTEM_PROMPT_FILE" | tr -d ' ')
echo "Prompt size: ${PROMPT_SIZE} bytes" >&2

# Save prompt to debug log
if [[ -n "$PROMPT_LOG" ]]; then
  cp "$SYSTEM_PROMPT_FILE" "$PROMPT_LOG"
  echo "Debug: prompt saved to $PROMPT_LOG" >&2
fi

# --- Invoke Claude CLI ---

TIMEOUT="${CLAUDE_TIMEOUT:-300}"
MAX_BUDGET="${CLAUDE_MAX_BUDGET:-0.50}"

echo "Starting test coverage audit ($MODE mode)..." >&2
echo "Module: $MODULE_PATH" >&2
echo "Tests: $TEST_PATH" >&2
echo "Output: $OUTPUT_FILE" >&2
echo "Timeout: ${TIMEOUT}s, Budget: \$${MAX_BUDGET}" >&2

START_TIME=$(date +%s)

# Single-turn, no tools: the audit report is output to stdout and captured directly.
# --tools "" disables all tools so claude outputs the report as text.
# --no-session-persistence avoids writing session state to disk.
# stdin from prompt file ensures clean EOF (no TTY hang).
if timeout "$TIMEOUT" claude --print \
  --no-session-persistence \
  --max-budget-usd "$MAX_BUDGET" \
  --tools "" \
  <"$SYSTEM_PROMPT_FILE" >"$OUTPUT_FILE"; then

  ELAPSED=$(($(date +%s) - START_TIME))
  echo "Claude finished in ${ELAPSED}s" >&2

  if [[ -s "$OUTPUT_FILE" ]]; then
    echo "$OUTPUT_FILE"
  else
    echo "Error: Claude completed but report file is empty" >&2
    exit 1
  fi
else
  EXIT_CODE=$?
  ELAPSED=$(($(date +%s) - START_TIME))

  if [[ "$EXIT_CODE" -eq 124 ]]; then
    echo "Error: Claude CLI timed out after ${ELAPSED}s (limit: ${TIMEOUT}s)" >&2
  else
    echo "Error: Claude CLI invocation failed (exit $EXIT_CODE) after ${ELAPSED}s" >&2
  fi

  # Preserve partial output if any
  if [[ -s "$OUTPUT_FILE" ]]; then
    echo "Partial output saved to: $OUTPUT_FILE" >&2
  fi
  exit 1
fi
