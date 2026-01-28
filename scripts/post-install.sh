#!/bin/bash
# Post-install script for claude-cortex plugin
# This runs after `claude install` completes

set -e

PLUGIN_DIR="$(cd "$(dirname "$0")/.." && pwd)"
RULES_TARGET="$HOME/.claude/rules/cortex"

echo "=== Cortex Post-Install ==="
echo "Plugin directory: $PLUGIN_DIR"

# 1. Create rules symlinks
echo ""
echo "Setting up rule symlinks..."
mkdir -p "$RULES_TARGET"

count=0
for rule in "$PLUGIN_DIR/rules"/*.md; do
  if [ -f "$rule" ]; then
    name=$(basename "$rule")
    target="$RULES_TARGET/$name"

    # Remove existing symlink if present
    [ -L "$target" ] && rm "$target"

    # Create new symlink
    ln -s "$rule" "$target"
    echo "  Linked: $name"
    count=$((count + 1))
  fi
done

echo "  Total: $count rules linked"

# 2. Add rules directory to .gitignore
GITIGNORE="$HOME/.claude/.gitignore"
ENTRY="rules/cortex/"
if [ -f "$GITIGNORE" ]; then
  if ! grep -q "^$ENTRY$" "$GITIGNORE" 2>/dev/null; then
    echo "$ENTRY" >> "$GITIGNORE"
    echo "Updated .gitignore"
  fi
else
  mkdir -p "$(dirname "$GITIGNORE")"
  echo "$ENTRY" > "$GITIGNORE"
  echo "Created .gitignore"
fi

# 3. Optional: Install Python CLI
echo ""
echo "=== Optional: Python CLI ==="

if command -v pip &> /dev/null || command -v pip3 &> /dev/null; then
  echo "Python detected. The cortex CLI provides additional features:"
  echo "  - Agent/skill/rule management (cortex agent list, etc.)"
  echo "  - TUI dashboard (cortex tui)"
  echo "  - AI-powered recommendations (cortex ai recommend)"
  echo ""
  echo "To install: pip install claude-cortex"
  echo "Or from this plugin: pip install -e '$PLUGIN_DIR'"
else
  echo "Python not detected. Skipping CLI installation prompt."
fi

echo ""
echo "=== Setup Complete ==="
echo "Rules symlinked to: $RULES_TARGET"
echo "Run 'claude' to start using Cortex agents and skills."
