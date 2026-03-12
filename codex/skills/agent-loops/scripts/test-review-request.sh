#!/usr/bin/env bash
#
# test-review-request.sh — Invoke a test coverage audit via Claude/Gemini/Codex CLI
#
# Usage:
#   test-review-request.sh <module-path> [options]
#   test-review-request.sh --quick <test-file-path> [options]
#
# Options:
#   --tests <path>    Specify test directory (default: auto-discover)
#   --output <dir>    Output directory (default: .agents/reviews)
#   --quick           Quick review mode (anti-patterns only, no full audit)
#   --debug           Save prompt and provider output to log files for debugging
#   --provider <name> auto (default), claude, gemini, or codex
#
# Environment:
#   AGENT_LOOPS_LLM_PROVIDER Default provider selection: auto|claude|gemini|codex
#   TEST_REVIEW_PROVIDER     Override provider selection for this script only
#   CLAUDE_TIMEOUT           Timeout in seconds for Claude (default: 300)
#   GEMINI_TIMEOUT           Timeout in seconds for Gemini (default: 300)
#   CODEX_TIMEOUT            Timeout in seconds for Codex (default: 300)
#   CLAUDE_MAX_BUDGET        Max spend in USD per Claude invocation (default: 0.50)
#   CODEX_MODEL              Optional Codex model override
#   CLAUDE_DEBUG=1           Same as --debug flag
#
# All source, test, and reference content is inlined into the prompt.
# Single-turn, no tools: the selected provider outputs the report to stdout.

set -euo pipefail

# Resolve physical paths to handle symlink invocation (e.g. ~/.codex/skills/...)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
SKILL_DIR="$(cd "$(dirname "$SCRIPT_DIR")" && pwd -P)"
source "$SCRIPT_DIR/review-provider.sh"

CALLER_CWD="$(pwd -P)"
VALIDATOR="$SCRIPT_DIR/validate-review-contract.py"

# Resolve repo root from caller's CWD (best-effort). Unlike specialist-review,
# this script can still run without git metadata because it reads files directly.
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || true)"
if [[ -z "$REPO_ROOT" ]]; then
  REPO_ROOT="$CALLER_CWD"
fi

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
REQUESTED_PROVIDER="${TEST_REVIEW_PROVIDER:-${AGENT_LOOPS_LLM_PROVIDER:-auto}}"

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
  --provider)
    shift
    REQUESTED_PROVIDER="${1:-}"
    if [[ -z "$REQUESTED_PROVIDER" ]]; then
      echo "Error: --provider requires auto, claude, gemini, or codex" >&2
      exit 1
    fi
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

# Resolve module path relative to repo root if needed.
if [[ ! -e "$MODULE_PATH" && -e "$REPO_ROOT/$MODULE_PATH" ]]; then
  MODULE_PATH="$REPO_ROOT/$MODULE_PATH"
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

# Resolve explicit test path relative to repo root if needed.
if [[ "$TEST_PATH" != "(none)" && ! -e "$TEST_PATH" && -e "$REPO_ROOT/$TEST_PATH" ]]; then
  TEST_PATH="$REPO_ROOT/$TEST_PATH"
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

# --- Invoke provider CLI ---

DEFAULT_TIMEOUT=300

echo "Starting test coverage audit ($MODE mode)..." >&2
echo "Module: $MODULE_PATH" >&2
echo "Tests: $TEST_PATH" >&2
echo "Output: $OUTPUT_FILE" >&2
echo "Requested provider: $REQUESTED_PROVIDER" >&2

# --- Pre-flight checks ---

if [[ ! -s "$SYSTEM_PROMPT_FILE" ]]; then
  echo "Error: Prompt file is empty after template substitution." >&2
  echo "Check that $PROMPT_TEMPLATE exists and placeholders were resolved." >&2
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
  STDERR_LOG="$OUTPUT_DIR/test-audit-$TIMESTAMP.$PROVIDER.stderr.log"
  TIMEOUT_SECONDS="$(review_provider_timeout "$PROVIDER" "$DEFAULT_TIMEOUT")"

  echo "Trying provider: $(review_provider_display_name "$PROVIDER") (timeout ${TIMEOUT_SECONDS}s)" >&2
  if [[ "$PROVIDER" == "claude" ]]; then
    echo "Claude budget: \$${CLAUDE_MAX_BUDGET:-0.50}" >&2
  elif [[ -n "${GEMINI_MODEL:-}" ]]; then
    echo "Gemini model override: ${GEMINI_MODEL}" >&2
  elif [[ "$PROVIDER" == "codex" && -n "${CODEX_MODEL:-}" ]]; then
    echo "Codex model override: ${CODEX_MODEL}" >&2
  fi

  rm -f "$OUTPUT_FILE"
  START_TIME=$(date +%s)

  if review_provider_run "$PROVIDER" "$SYSTEM_PROMPT_FILE" "$OUTPUT_FILE" "$STDERR_LOG" "$TIMEOUT_SECONDS"; then
    ELAPSED=$(($(date +%s) - START_TIME))
    echo "$(review_provider_display_name "$PROVIDER") finished in ${ELAPSED}s" >&2

    if [[ -s "$OUTPUT_FILE" ]]; then
      if python3 "$VALIDATOR" test-audit "$OUTPUT_FILE" >/dev/null 2>&1; then
        if [[ "$DEBUG" != "1" ]]; then
          rm -f "$STDERR_LOG"
        fi
        echo "$OUTPUT_FILE"
        exit 0
      fi

      echo "Error: $(review_provider_display_name "$PROVIDER") output did not match the test audit contract." >&2
      python3 "$VALIDATOR" test-audit "$OUTPUT_FILE" >&2 || true
      PARTIAL_OUTPUT="$OUTPUT_DIR/test-audit-$TIMESTAMP.$PROVIDER.invalid.md"
      mv "$OUTPUT_FILE" "$PARTIAL_OUTPUT"
      echo "Invalid output saved to: $PARTIAL_OUTPUT" >&2
      if [[ "$REQUESTED_PROVIDER" == "auto" ]]; then
        echo "Trying next provider fallback..." >&2
        continue
      fi
      exit 1
    fi

    echo "Error: $(review_provider_display_name "$PROVIDER") completed (exit 0) but report file is empty." >&2
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
    PARTIAL_OUTPUT="$OUTPUT_DIR/test-audit-$TIMESTAMP.$PROVIDER.partial.md"
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
  echo "Error: No audit providers are available in PATH. Install 'claude', 'gemini', or 'codex', or use the fresh-context Codex fallback." >&2
else
  echo "Error: All audit providers failed. Inspect stderr logs above or use the fresh-context Codex fallback." >&2
fi
exit 1
