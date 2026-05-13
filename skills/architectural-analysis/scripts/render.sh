#!/usr/bin/env bash
# Render every *.mmd file in a report directory to *.svg via mmdc.
#
# Usage: render.sh <report-dir>
#
# Walks each immediate subdirectory of the report dir, finds *.mmd files,
# and runs mmdc on each producing a sibling *.svg. Idempotent — re-running
# overwrites existing SVGs. Skips files where the SVG is newer than the
# source.

set -euo pipefail

REPORT_DIR="${1:?usage: render.sh <report-dir>}"

if [[ ! -d "$REPORT_DIR" ]]; then
  echo "error: not a directory: $REPORT_DIR" >&2
  exit 1
fi

if ! command -v mmdc >/dev/null 2>&1; then
  cat >&2 <<'EOF'
error: mmdc (mermaid CLI) is not installed.

Install with one of:
  npm install -g @mermaid-js/mermaid-cli
  pnpm add -g @mermaid-js/mermaid-cli
  brew install mermaid-cli

Diagrams are still authored as .mmd files; only the SVG render step requires mmdc.
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
done < <(find "$REPORT_DIR" -maxdepth 3 -type f -name '*.mmd' -print0)

echo
echo "summary: rendered=$rendered skipped=$skipped failed=$failed"

if (( failed > 0 )); then
  exit 1
fi
