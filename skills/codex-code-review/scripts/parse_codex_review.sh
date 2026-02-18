#!/usr/bin/env bash
#
# parse_codex_review.sh — Parse codex review markdown and extract key findings
#
# Usage:
#   parse_codex_review.sh <review-file>
#
# Output:
#   - Count of P0, P1, P2, P3 findings
#   - Verdict (APPROVE / REQUEST CHANGES / BLOCKED)
#   - List of findings by severity
#
# Example:
#   ./parse_codex_review.sh .agent/reviews/review-20260218-143021.md

set -euo pipefail

REVIEW_FILE="${1:-.}"

if [[ ! -f "$REVIEW_FILE" ]]; then
    echo "Error: Review file not found: $REVIEW_FILE" >&2
    exit 1
fi

echo "=== Codex Review Analysis ==="
echo ""
echo "File: $REVIEW_FILE"
echo ""

# Extract verdict
VERDICT=$(grep "^\*\*Verdict:\*\*" "$REVIEW_FILE" | sed 's/.*\*\*Verdict:\*\* //' || echo "UNKNOWN")
echo "Verdict: $VERDICT"
echo ""

# Extract iteration count
ITERATION=$(grep "^\*\*Iteration:\*\*" "$REVIEW_FILE" | sed 's/.*\*\*Iteration:\*\* //' || echo "UNKNOWN")
echo "Iteration: $ITERATION"
echo ""

# Count findings by severity
P0_COUNT=$(grep -c "^#### P0-" "$REVIEW_FILE" || echo "0")
P1_COUNT=$(grep -c "^#### P1-" "$REVIEW_FILE" || echo "0")
P2_COUNT=$(grep -c "^#### P2-" "$REVIEW_FILE" || echo "0")
P3_COUNT=$(grep -c "^#### P3-" "$REVIEW_FILE" || echo "0")

echo "=== Findings Summary ==="
echo "P0 (MUST fix): $P0_COUNT"
echo "P1 (MUST fix): $P1_COUNT"
echo "P2 (optional): $P2_COUNT"
echo "P3 (optional): $P3_COUNT"
echo ""

TOTAL_P0_P1=$((P0_COUNT + P1_COUNT))
if [[ $TOTAL_P0_P1 -eq 0 ]]; then
    echo "✅ All P0/P1 issues resolved. Safe to proceed."
else
    echo "⚠️  $TOTAL_P0_P1 P0/P1 issues found. Must remediate before exit."
fi
echo ""

# List findings by severity
echo "=== P0 Findings ==="
grep "^#### P0-" "$REVIEW_FILE" | sed 's/^#### //' || echo "(none)"
echo ""

echo "=== P1 Findings ==="
grep "^#### P1-" "$REVIEW_FILE" | sed 's/^#### //' || echo "(none)"
echo ""

echo "=== P2 Findings ==="
grep "^#### P2-" "$REVIEW_FILE" | sed 's/^#### //' || echo "(none)"
echo ""

echo "=== P3 Findings ==="
grep "^#### P3-" "$REVIEW_FILE" | sed 's/^#### //' || echo "(none)"
