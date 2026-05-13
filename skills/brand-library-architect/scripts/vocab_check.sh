#!/usr/bin/env bash
# Check brand documentation for don't-use vocabulary.
#
# Usage:
#     bash scripts/vocab_check.sh brand/
#     bash scripts/vocab_check.sh brand/FAQ.md
#
# Reports each occurrence with file:line context. Occurrences in explicit
# don't-use callouts (e.g., "❌ \"tailor\"") and "Avoid" example blocks are
# expected — review the report and confirm any positive uses are intentional.

set -euo pipefail

if [ $# -lt 1 ]; then
    echo "Usage: vocab_check.sh <path>" >&2
    exit 2
fi

TARGET="$1"

if [ ! -e "$TARGET" ]; then
    echo "Path not found: $TARGET" >&2
    exit 2
fi

# Default don't-use list (extend per product in brand/COPY.md)
WORDS=(
    "tailor"
    "career platform"
    "career journey"
    "stand out"
    "job seeker"
    "coach"
    "coaching"
    "optimize"
    "customize"
    "next-generation"
    "revolutionary"
    "game-changing"
    "AI-powered"
    "stand out from the crowd"
    "unleash your"
    "take.*next level"
)

echo "=== Vocabulary check on $TARGET ==="
echo ""

TOTAL=0
for word in "${WORDS[@]}"; do
    if [ -d "$TARGET" ]; then
        # Recurse into directory, only .md files
        hits=$(grep -rn -i "$word" --include="*.md" "$TARGET" 2>/dev/null || true)
    else
        hits=$(grep -n -i "$word" "$TARGET" 2>/dev/null || true)
    fi

    if [ -n "$hits" ]; then
        count=$(echo "$hits" | wc -l | tr -d ' ')
        echo "── '$word' ($count occurrences) ──"
        echo "$hits" | head -20
        echo ""
        TOTAL=$((TOTAL + count))
    fi
done

echo "Total occurrences: $TOTAL"
echo ""
echo "Review each — occurrences in don't-use callouts or Avoid examples are"
echo "expected; positive uses describing the product should be flagged for"
echo "rewrite."
