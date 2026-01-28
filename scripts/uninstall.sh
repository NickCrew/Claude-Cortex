#!/bin/bash
# Uninstall script for claude-cortex plugin

set -e

RULES_TARGET="$HOME/.claude/rules/cortex"

echo "=== Cortex Uninstall ==="

# Remove rule symlinks
if [ -d "$RULES_TARGET" ]; then
  echo "Removing rule symlinks..."
  rm -rf "$RULES_TARGET"
  echo "  Removed: $RULES_TARGET"
else
  echo "No rule symlinks found."
fi

# Optionally uninstall Python package
if command -v pip &> /dev/null && pip show claude-cortex &> /dev/null 2>&1; then
  echo ""
  read -p "Uninstall Python CLI (claude-cortex)? [y/N] " -n 1 -r
  echo
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    pip uninstall -y claude-cortex
    echo "Python CLI uninstalled."
  fi
fi

echo ""
echo "=== Uninstall Complete ==="
