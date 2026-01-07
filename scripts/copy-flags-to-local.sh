#!/bin/bash
# Copy all flag files from plugin to local .claude directory

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get script directory (cortex-plugin root)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PLUGIN_ROOT="$(dirname "$SCRIPT_DIR")"

# Source flags directory (in plugin)
SOURCE_FLAGS_DIR="$PLUGIN_ROOT/flags"

# Target flags directory (current project's .claude)
TARGET_FLAGS_DIR="$(pwd)/.claude/flags"

echo "📋 Flag Copy Utility"
echo "===================="
echo ""
echo "Source: $SOURCE_FLAGS_DIR"
echo "Target: $TARGET_FLAGS_DIR"
echo ""

# Check if source exists
if [ ! -d "$SOURCE_FLAGS_DIR" ]; then
    echo "❌ Error: Source flags directory not found: $SOURCE_FLAGS_DIR"
    exit 1
fi

# Count flags in source
FLAG_COUNT=$(find "$SOURCE_FLAGS_DIR" -name "*.md" ! -name "README.md" | wc -l | tr -d ' ')
echo "Found $FLAG_COUNT flag files in plugin"
echo ""

# Create target directory if it doesn't exist
if [ ! -d "$TARGET_FLAGS_DIR" ]; then
    echo "Creating target directory: $TARGET_FLAGS_DIR"
    mkdir -p "$TARGET_FLAGS_DIR"
fi

# Copy all flag files
echo "Copying flags..."
COPIED=0
SKIPPED=0

for flag_file in "$SOURCE_FLAGS_DIR"/*.md; do
    filename=$(basename "$flag_file")

    # Skip README
    if [ "$filename" = "README.md" ]; then
        continue
    fi

    target_file="$TARGET_FLAGS_DIR/$filename"

    # Check if file exists and is identical
    if [ -f "$target_file" ]; then
        if cmp -s "$flag_file" "$target_file"; then
            echo "  ${GREEN}✓${NC} $filename (already up-to-date)"
            SKIPPED=$((SKIPPED + 1))
        else
            echo "  ${YELLOW}⚠${NC} $filename (overwriting different version)"
            cp "$flag_file" "$target_file"
            COPIED=$((COPIED + 1))
        fi
    else
        echo "  ${GREEN}+${NC} $filename (new)"
        cp "$flag_file" "$target_file"
        COPIED=$((COPIED + 1))
    fi
done

echo ""
echo "===================="
echo "✅ Complete!"
echo ""
echo "  Copied: $COPIED files"
echo "  Skipped: $SKIPPED files (already up-to-date)"
echo "  Total: $FLAG_COUNT flag files"
echo ""
echo "Next steps:"
echo "1. Edit .claude/CLAUDE.md to enable/disable flags"
echo "2. Use cortex tui → Press Ctrl+G for flag manager"
echo "3. Or use profiles: cortex profile apply <profile>"
