#!/usr/bin/env bash
# Render every *.mmd file in a report directory to themed *.svg + *.png via mmdc.
#
# Usage:
#   render.sh <report-dir> [--style blueprint|corporate] [--svg-only|--png-only|--both]
#                          [--themes light,dark]
#
# Walks each immediate subdirectory of the report dir, finds *.mmd files,
# and renders themed variants:
#   <name>.svg + <name>.png        — neutral PNG (PDF-friendly, light bg)
#   <name>-light.svg               — light theme (HTML viewing)
#   <name>-dark.svg                — dark theme (HTML viewing)
#
# The neutral PNG keeps compile-pdf.sh consumers happy. The themed SVGs
# are what compile-html.sh embeds, with light/dark swapping via CSS.
#
# Idempotent: re-running overwrites existing outputs.
#
# Bash-3.2 compatible (macOS default). Chrome headless shell must be
# installed for mmdc. First-time setup (if mmdc errors with "Could not
# find Chrome"):
#
#   cd /opt/homebrew/Cellar/mermaid-cli/*/libexec/lib/node_modules/@mermaid-js/mermaid-cli && \
#     npx puppeteer browsers install chrome-headless-shell

set -eo pipefail

MODE="both"
STYLE="corporate"
REPORT_DIR=""
THEMES="light,dark"

while (( $# > 0 )); do
  case "$1" in
    --svg-only) MODE="svg"; shift ;;
    --png-only) MODE="png"; shift ;;
    --both) MODE="both"; shift ;;
    --style) STYLE="${2:?--style requires a value}"; shift 2 ;;
    --themes) THEMES="${2:?--themes requires a value}"; shift 2 ;;
    -h|--help)
      sed -n '1,30p' "$0" >&2
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
  echo "usage: render.sh <report-dir> [--style blueprint|corporate] [--svg-only|--png-only|--both] [--themes light,dark]" >&2
  exit 2
fi

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

Diagrams are still authored as .mmd files; only the render step requires mmdc.
EOF
  exit 2
fi

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SKILL_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"
STYLE_DIR="$SKILL_DIR/assets/styles/$STYLE"

if [[ ! -d "$STYLE_DIR" ]]; then
  echo "error: unknown style '$STYLE'. Available styles:" >&2
  ls -1 "$SKILL_DIR/assets/styles" 2>/dev/null >&2 || echo "  (none found)" >&2
  exit 1
fi

rendered=0
skipped=0
failed=0

render_one() {
  local mmd="$1"
  local out="$2"
  local bg="$3"
  local config="$4"
  local is_png=0
  if [[ "${out##*.}" == "png" ]]; then is_png=1; fi

  if [[ -f "$out" && "$out" -nt "$mmd" ]]; then
    skipped=$((skipped + 1))
    return 0
  fi

  echo "render: $mmd → $out"
  local mmdc_args=(-i "$mmd" -o "$out" -b "$bg")
  if [[ -f "$config" ]]; then
    mmdc_args+=(-c "$config")
  fi
  if (( is_png )); then
    mmdc_args+=(-w 2400)
  fi

  if mmdc "${mmdc_args[@]}" 2>&1; then
    rendered=$((rendered + 1))
    # Mermaid's ER renderer derives row backgrounds from `primaryColor`
    # by clamping HSL lightness, ignoring `attributeBackgroundColor*`
    # tokens. For dark-theme SVGs that produces a white "odd" row that
    # makes ER attribute text unreadable. Patch by injecting a dark
    # row-rect override into the SVG's <style> block.
    if [[ "$out" == *-dark.svg ]] && grep -q 'row-rect-odd' "$out" 2>/dev/null; then
      patch_svg_dark_er_rows "$out"
    fi
  else
    echo "  failed: $mmd → $out" >&2
    failed=$((failed + 1))
  fi
}

# Inject CSS into a dark-variant SVG so ER attribute rows use dark fills
# instead of mermaid's auto-derived (often white) HSL clamp. Idempotent.
patch_svg_dark_er_rows() {
  local svg="$1"
  if grep -q '\.row-rect-odd path' "$svg"; then
    return 0  # already patched
  fi
  local css='#my-svg .row-rect-odd path,#my-svg .row-rect-odd > path:first-of-type{fill:#1c2438 !important;}#my-svg .row-rect-even path,#my-svg .row-rect-even > path:first-of-type{fill:#0f1421 !important;}'
  # Insert just before the closing </style> of the first style block.
  sed -i.bak "s|</style>|${css}</style>|" "$svg" 2>/dev/null && rm -f "$svg.bak"
}

# Render targets: themed SVGs (one per theme), one neutral PNG (light theme,
# white bg, the PDF-bound asset).
IFS=',' read -r -a THEME_LIST <<< "$THEMES"

while IFS= read -r -d '' mmd; do
  base="${mmd%.mmd}"

  if [[ "$MODE" == "svg" || "$MODE" == "both" ]]; then
    for theme in "${THEME_LIST[@]}"; do
      config="$STYLE_DIR/mermaid-$theme.json"
      # Per-style themed variant: <base>-<style>-<theme>.svg
      out="${base}-${STYLE}-${theme}.svg"
      render_one "$mmd" "$out" "transparent" "$config"
    done
  fi

  if [[ "$MODE" == "png" || "$MODE" == "both" ]]; then
    light_config="$STYLE_DIR/mermaid-light.json"
    # PDF-bound PNG is style-agnostic for now (PDF doesn't toggle).
    # Keep <base>.png as the canonical PDF asset.
    render_one "$mmd" "${base}.png" "white" "$light_config"
  fi
done < <(find "$REPORT_DIR" -maxdepth 3 -type f -name '*.mmd' -print0)

echo
echo "summary: style=$STYLE themes=${THEMES} rendered=$rendered skipped=$skipped failed=$failed mode=$MODE"

if (( failed > 0 )); then
  exit 1
fi
