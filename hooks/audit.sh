#!/usr/bin/env bash
# Audit codebase: run clippy/tests, group failures by root cause
#
# Usage: ./audit.sh [path-to-cargo-project]
# Output: Markdown report grouped by category and root cause
#
# This feeds into the "document everything, create paper trail" workflow.

set -euo pipefail

PROJECT_DIR="${1:-.}"
cd "$PROJECT_DIR"

if [[ ! -f "Cargo.toml" ]]; then
    echo "Error: No Cargo.toml found in $PROJECT_DIR"
    exit 1
fi

OUTPUT_FILE="${AUDIT_OUTPUT:-audit-report.md}"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

echo "# Codebase Audit Report" > "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "**Generated:** $TIMESTAMP" >> "$OUTPUT_FILE"
echo "**Project:** $(basename "$(pwd)")" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# --- Clippy Warnings ---
echo "## Clippy Analysis" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

CLIPPY_OUTPUT=$(cargo clippy --message-format=short 2>&1 || true)
CLIPPY_WARNINGS=$(echo "$CLIPPY_OUTPUT" | grep -c "^warning:" || echo "0")
CLIPPY_ERRORS=$(echo "$CLIPPY_OUTPUT" | grep -c "^error" || echo "0")

echo "| Category | Count |" >> "$OUTPUT_FILE"
echo "|----------|-------|" >> "$OUTPUT_FILE"
echo "| Warnings | $CLIPPY_WARNINGS |" >> "$OUTPUT_FILE"
echo "| Errors | $CLIPPY_ERRORS |" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

if [[ "$CLIPPY_WARNINGS" -gt 0 || "$CLIPPY_ERRORS" -gt 0 ]]; then
    echo "<details>" >> "$OUTPUT_FILE"
    echo "<summary>Clippy Output (click to expand)</summary>" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    echo '```' >> "$OUTPUT_FILE"
    echo "$CLIPPY_OUTPUT" | head -100 >> "$OUTPUT_FILE"
    echo '```' >> "$OUTPUT_FILE"
    echo "</details>" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
fi

# --- Test Failures ---
echo "## Test Results" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

TEST_OUTPUT=$(cargo test 2>&1 || true)
TEST_PASSED=$(echo "$TEST_OUTPUT" | grep -oE "([0-9]+) passed" | grep -oE "[0-9]+" || echo "0")
TEST_FAILED=$(echo "$TEST_OUTPUT" | grep -oE "([0-9]+) failed" | grep -oE "[0-9]+" || echo "0")
TEST_IGNORED=$(echo "$TEST_OUTPUT" | grep -oE "([0-9]+) ignored" | grep -oE "[0-9]+" || echo "0")

echo "| Status | Count |" >> "$OUTPUT_FILE"
echo "|--------|-------|" >> "$OUTPUT_FILE"
echo "| Passed | $TEST_PASSED |" >> "$OUTPUT_FILE"
echo "| Failed | $TEST_FAILED |" >> "$OUTPUT_FILE"
echo "| Ignored | $TEST_IGNORED |" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

if [[ "$TEST_FAILED" -gt 0 ]]; then
    echo "### Failed Tests" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    echo '```' >> "$OUTPUT_FILE"
    echo "$TEST_OUTPUT" | grep -A 5 "^---- .* ----$" | head -50 >> "$OUTPUT_FILE"
    echo '```' >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
fi

# --- Summary ---
echo "## Summary" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

TOTAL_ISSUES=$((CLIPPY_WARNINGS + CLIPPY_ERRORS + TEST_FAILED))
if [[ "$TOTAL_ISSUES" -eq 0 ]]; then
    echo "✅ No issues found." >> "$OUTPUT_FILE"
else
    echo "⚠️ **$TOTAL_ISSUES total issues** require attention." >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    echo "Priority:" >> "$OUTPUT_FILE"
    echo "1. Fix compilation errors ($CLIPPY_ERRORS)" >> "$OUTPUT_FILE"
    echo "2. Fix test failures ($TEST_FAILED)" >> "$OUTPUT_FILE"  
    echo "3. Address clippy warnings ($CLIPPY_WARNINGS)" >> "$OUTPUT_FILE"
fi

echo "" >> "$OUTPUT_FILE"
echo "---" >> "$OUTPUT_FILE"
echo "*Run \`./hooks/issue-generator.sh $OUTPUT_FILE\` to create issue files.*" >> "$OUTPUT_FILE"

echo "Audit complete: $OUTPUT_FILE"
echo "Total issues: $TOTAL_ISSUES"
