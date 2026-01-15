#!/bin/bash
# Launch the NEW Textual TUI with command palette support

echo "🚀 Launching Textual TUI with Command Palette..."
echo ""
echo "Keyboard shortcuts:"
echo "  Ctrl+P : Open Command Palette (search for 'agent' to see agent commands)"
echo "  1-7    : Switch views"
echo "  Space  : Toggle selected item"
echo "  R      : Refresh view"
echo "  Q      : Quit"
echo ""
echo "Press Ctrl+C to exit at any time"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

uv run python -m claude_ctx_py.tui_textual
