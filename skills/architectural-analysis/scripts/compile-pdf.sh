#!/usr/bin/env bash
# Combine the synthesis README and all per-mode reports into a single PDF.
#
# Usage: compile-pdf.sh <report-dir>
#
# Produces <report-dir>/<date>.pdf where <date> is the dirname.
# Requires pandoc and a PDF engine (wkhtmltopdf, weasyprint, or a TeX
# distribution). Embeds rendered SVGs inline. Run render.sh first so SVGs
# exist.

set -euo pipefail

REPORT_DIR="${1:?usage: compile-pdf.sh <report-dir>}"
REPORT_DIR="${REPORT_DIR%/}"

if [[ ! -d "$REPORT_DIR" ]]; then
  echo "error: not a directory: $REPORT_DIR" >&2
  exit 1
fi

if [[ ! -f "$REPORT_DIR/README.md" ]]; then
  echo "error: missing $REPORT_DIR/README.md (run synthesis step first)" >&2
  exit 1
fi

if ! command -v pandoc >/dev/null 2>&1; then
  cat >&2 <<'EOF'
error: pandoc is not installed.

Install with one of:
  brew install pandoc
  apt install pandoc
  See https://pandoc.org/installing.html
EOF
  exit 2
fi

DATE_STAMP="$(basename "$REPORT_DIR")"
OUT_PDF="$REPORT_DIR/$DATE_STAMP.pdf"

# Mode order matches the synthesis README's expected reading flow.
MODES=(
  information
  data-model
  data-flow
  integrations
  ui-surfaces
  interaction-patterns
  control-flow
  failure-modes
)

INPUTS=("$REPORT_DIR/README.md")
for mode in "${MODES[@]}"; do
  report="$REPORT_DIR/$mode/report.md"
  if [[ -f "$report" ]]; then
    INPUTS+=("$report")
  fi
done

# Pick a PDF engine that's actually installed. Prefer wkhtmltopdf for
# better SVG support; fall back to weasyprint, then default (TeX).
ENGINE_ARGS=()
if command -v wkhtmltopdf >/dev/null 2>&1; then
  ENGINE_ARGS=(--pdf-engine=wkhtmltopdf)
elif command -v weasyprint >/dev/null 2>&1; then
  ENGINE_ARGS=(--pdf-engine=weasyprint)
fi

echo "compiling $OUT_PDF from ${#INPUTS[@]} markdown files…"

pandoc \
  "${INPUTS[@]}" \
  --resource-path="$REPORT_DIR" \
  --toc --toc-depth=2 \
  --metadata title="Architectural Analysis $DATE_STAMP" \
  "${ENGINE_ARGS[@]}" \
  -o "$OUT_PDF"

echo "done: $OUT_PDF"
