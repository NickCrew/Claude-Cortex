#!/usr/bin/env bash
# Combine the synthesis README and all per-mode reports into a single
# self-contained HTML file with embedded SVGs and CSS.
#
# Usage:
#   compile-html.sh <report-dir> [--banner <path-to-banner-image>]
#                                [--repo-root <path>]
#                                [--out <path>]
#
# Produces <report-dir>/<date>.html by default. The HTML is fully
# self-contained — images are embedded as base64 data URIs, CSS is
# inlined — so it can be emailed or moved without breaking.
#
# Banner is optional. If provided, the path is resolved relative to
# --repo-root (default: cwd) and the image is embedded into the HTML.
# For Cortex:
#   bash scripts/compile-html.sh docs/architecture/2026-05-10/ \
#       --banner docs/assets/images/cortex-banner.png

set -euo pipefail

REPORT_DIR=""
BANNER=""
REPO_ROOT="$(pwd)"
OUT_PATH=""

usage() {
  cat <<'EOF' >&2
usage: compile-html.sh <report-dir> [options]

Options:
  --banner <path>     Path to a banner image (resolved relative to --repo-root).
  --repo-root <path>  Repo root for resolving banner + report paths (default: cwd).
  --out <path>        Output HTML path (default: <report-dir>/<dirname>.html).
  -h, --help          Show this help.
EOF
}

# Positional + flag parsing.
while (( $# > 0 )); do
  case "$1" in
    -h|--help)
      usage
      exit 0
      ;;
    --banner)
      BANNER="${2:?--banner requires a value}"
      shift 2
      ;;
    --repo-root)
      REPO_ROOT="${2:?--repo-root requires a value}"
      shift 2
      ;;
    --out)
      OUT_PATH="${2:?--out requires a value}"
      shift 2
      ;;
    --)
      shift
      break
      ;;
    -*)
      echo "error: unknown option: $1" >&2
      usage
      exit 2
      ;;
    *)
      if [[ -z "$REPORT_DIR" ]]; then
        REPORT_DIR="$1"
      else
        echo "error: unexpected argument: $1" >&2
        usage
        exit 2
      fi
      shift
      ;;
  esac
done

if [[ -z "$REPORT_DIR" ]]; then
  usage
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

# Locate skill assets next to this script.
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SKILL_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"
TEMPLATE="$SKILL_DIR/assets/template.html"
CSS_FILE="$SKILL_DIR/assets/report.css"

if [[ ! -f "$TEMPLATE" ]]; then
  echo "error: template not found at $TEMPLATE" >&2
  exit 1
fi
if [[ ! -f "$CSS_FILE" ]]; then
  echo "error: stylesheet not found at $CSS_FILE" >&2
  exit 1
fi

DATE_STAMP="$(basename "$REPORT_DIR")"
if [[ -z "$OUT_PATH" ]]; then
  OUT_PATH="$REPORT_DIR/$DATE_STAMP.html"
fi

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

# Banner: if provided, resolve relative to repo-root and confirm it exists.
BANNER_META=()
if [[ -n "$BANNER" ]]; then
  if [[ "$BANNER" = /* ]]; then
    BANNER_RESOLVED="$BANNER"
  else
    BANNER_RESOLVED="$REPO_ROOT/$BANNER"
  fi
  if [[ ! -f "$BANNER_RESOLVED" ]]; then
    echo "error: banner not found at $BANNER_RESOLVED" >&2
    exit 1
  fi
  BANNER_META=(--metadata "banner=$BANNER_RESOLVED")
fi

# Determine pandoc embed flag — newer pandoc uses --embed-resources, older
# uses --self-contained. Try the newer flag first.
EMBED_FLAGS=(--standalone)
if pandoc --help 2>&1 | grep -q -- '--embed-resources'; then
  EMBED_FLAGS+=(--embed-resources)
else
  EMBED_FLAGS+=(--self-contained)
fi

echo "compiling $OUT_PATH from ${#INPUTS[@]} markdown files…"
[[ -n "$BANNER" ]] && echo "  banner: $BANNER_RESOLVED"

pandoc \
  "${INPUTS[@]}" \
  --from=gfm+yaml_metadata_block+raw_html \
  --to=html5 \
  --template="$TEMPLATE" \
  --css="$CSS_FILE" \
  --resource-path="$REPORT_DIR:$REPO_ROOT:$SKILL_DIR/assets:." \
  --toc --toc-depth=2 \
  --metadata title="Architectural Analysis $DATE_STAMP" \
  --metadata date="$DATE_STAMP" \
  "${BANNER_META[@]}" \
  "${EMBED_FLAGS[@]}" \
  -o "$OUT_PATH"

echo "done: $OUT_PATH"
echo
echo "open with: open '$OUT_PATH'  (macOS)  |  xdg-open '$OUT_PATH'  (Linux)"
