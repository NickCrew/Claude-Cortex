#!/usr/bin/env bash
# Combine the synthesis README and all per-mode reports into a single PDF.
#
# Usage: compile-pdf.sh <report-dir> [--portrait]
#
# Produces <report-dir>/<date>.pdf where <date> is the dirname. Defaults to
# landscape — most architectural-analysis reports have wide tables (callout
# tables, cross-mode index, authoritative-docs table) and wide flow diagrams
# that get cut off in portrait. Pass --portrait to override.
#
# Requires pandoc and a PDF engine (weasyprint, wkhtmltopdf, or TeX). When
# weasyprint is available, applies a landscape CSS overlay with table-friendly
# line breaking. Embeds rendered SVGs/PNGs inline. Run render.sh first so
# diagrams exist (PNG preferred — see assets/mermaid-config.json).

set -euo pipefail

ORIENTATION="landscape"
REPORT_DIR=""

while (( $# > 0 )); do
  case "$1" in
    --portrait) ORIENTATION="portrait"; shift ;;
    --landscape) ORIENTATION="landscape"; shift ;;
    -h|--help)
      sed -n '1,15p' "$0" >&2
      exit 0
      ;;
    -*)
      echo "error: unknown flag: $1" >&2
      exit 2
      ;;
    *)
      if [[ -z "$REPORT_DIR" ]]; then
        REPORT_DIR="$1"
      else
        echo "error: unexpected argument: $1" >&2
        exit 2
      fi
      shift
      ;;
  esac
done

if [[ -z "$REPORT_DIR" ]]; then
  echo "usage: compile-pdf.sh <report-dir> [--portrait]" >&2
  exit 2
fi

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

# Resource path must include every mode subdir so per-mode reports'
# relative `![](foo.svg)` references resolve. The default --resource-path
# only adds the report dir, which works for the synthesis README but not
# for nested per-mode reports.
RESOURCE_PARTS=("$REPORT_DIR")
for mode in "${MODES[@]}"; do
  if [[ -d "$REPORT_DIR/$mode" ]]; then
    RESOURCE_PARTS+=("$REPORT_DIR/$mode")
  fi
done
RESOURCE_PATH=$(IFS=:; echo "${RESOURCE_PARTS[*]}")

# Pick a PDF engine. Prefer weasyprint — it's reliable on SVG/PNG embedding
# and respects @page CSS. wkhtmltopdf has better legacy SVG support but
# can't be installed on modern macOS. TeX fallback works but ignores the
# orientation overlay.
ENGINE_ARGS=()
ENGINE_NAME="default"
if command -v weasyprint >/dev/null 2>&1; then
  ENGINE_ARGS=(--pdf-engine=weasyprint)
  ENGINE_NAME="weasyprint"
elif command -v wkhtmltopdf >/dev/null 2>&1; then
  ENGINE_ARGS=(--pdf-engine=wkhtmltopdf)
  ENGINE_NAME="wkhtmltopdf"
fi

# Build a landscape CSS overlay for weasyprint. Tables get smaller font and
# allow word-break so long file paths in citation columns don't overflow.
# Skipped for non-weasyprint engines (they ignore @page CSS or use --orientation).
CSS_FLAGS=()
TMP_CSS=""
if [[ "$ENGINE_NAME" == "weasyprint" ]]; then
  TMP_CSS="$(mktemp -t compile-pdf-css.XXXXXX).css"
  trap 'rm -f "$TMP_CSS"' EXIT
  cat > "$TMP_CSS" <<EOF
@page {
  size: letter $ORIENTATION;
  margin: 0.4in;
}

body {
  font-size: 10pt;
  line-height: 1.35;
}

h1 { font-size: 18pt; page-break-before: always; }
h1:first-of-type { page-break-before: avoid; }
h2 { font-size: 14pt; }
h3 { font-size: 12pt; }

table {
  font-size: 8.5pt;
  border-collapse: collapse;
  width: 100%;
  table-layout: auto;
  page-break-inside: auto;
}
th, td {
  word-break: break-word;
  overflow-wrap: anywhere;
  padding: 3pt 5pt;
  vertical-align: top;
  border: 0.5pt solid #ccc;
}
th { background: #f0f0f0; }
tr { page-break-inside: avoid; }

code, pre {
  font-size: 8.5pt;
  word-break: break-all;
  overflow-wrap: anywhere;
}
pre {
  white-space: pre-wrap;
  page-break-inside: avoid;
}

img {
  max-width: 100%;
  height: auto;
  page-break-inside: avoid;
}
EOF
  CSS_FLAGS=(--css "$TMP_CSS")
fi

# wkhtmltopdf takes orientation as a flag, not CSS. Pipe it through.
if [[ "$ENGINE_NAME" == "wkhtmltopdf" ]]; then
  if [[ "$ORIENTATION" == "landscape" ]]; then
    ENGINE_ARGS+=(-V "papersize=letter" -V "geometry:landscape")
  fi
fi

echo "compiling $OUT_PDF from ${#INPUTS[@]} markdown files (${ORIENTATION}, engine=${ENGINE_NAME})…"

pandoc \
  "${INPUTS[@]}" \
  --resource-path="$RESOURCE_PATH" \
  --toc --toc-depth=2 \
  --metadata title="Architectural Analysis $DATE_STAMP" \
  "${ENGINE_ARGS[@]}" \
  "${CSS_FLAGS[@]}" \
  -o "$OUT_PDF"

echo "done: $OUT_PDF"
