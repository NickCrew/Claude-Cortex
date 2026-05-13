#!/usr/bin/env bash
# Render every *.mmd file in an audit directory to *.svg via mmdc.
#
# Usage: render.sh <audit-dir>
#
# Walks the audit directory and any immediate subdirectories, finds *.mmd
# files, and runs mmdc on each producing a sibling *.svg. Idempotent —
# re-running overwrites existing SVGs. Skips files where the SVG is newer
# than the source.

set -euo pipefail

AUDIT_DIR="${1:?usage: render.sh <audit-dir>}"

if [[ ! -d "$AUDIT_DIR" ]]; then
  echo "error: not a directory: $AUDIT_DIR" >&2
  exit 1
fi

if ! command -v mmdc >/dev/null 2>&1; then
  cat >&2 <<'EOF'
error: mmdc (mermaid CLI) is not installed.

Install with one of:
  npm install -g @mermaid-js/mermaid-cli
  pnpm add -g @mermaid-js/mermaid-cli
  brew install mermaid-cli

The wiring graph is optional; the audit report is still valid without
SVG rendering. Skip this step if mmdc is unavailable.
EOF
  exit 2
fi

shopt -s nullglob globstar

rendered=0
skipped=0
failed=0

while IFS= read -r -d '' mmd; do
  svg="${mmd%.mmd}.svg"

  if [[ -f "$svg" && "$svg" -nt "$mmd" ]]; then
    skipped=$((skipped + 1))
    continue
  fi

  echo "render: $mmd → $svg"
  if mmdc -i "$mmd" -o "$svg" -b transparent 2>&1; then
    rendered=$((rendered + 1))
  else
    echo "  failed: $mmd" >&2
    failed=$((failed + 1))
  fi
done < <(find "$AUDIT_DIR" -maxdepth 2 -type f -name '*.mmd' -print0)

echo
echo "summary: rendered=$rendered skipped=$skipped failed=$failed"

if (( failed > 0 )); then
  exit 1
fi
