#!/usr/bin/env bash
# Combine the synthesis README and all per-mode reports into a single
# self-contained HTML file with embedded SVGs and inline CSS.
#
# Usage:
#   compile-html.sh <report-dir> [options]
#
# Options:
#   --style <blueprint|corporate>   Visual style. Default: corporate.
#   --theme <light|dark>            Default theme baked at compile time.
#                                   Users can toggle at runtime; this just
#                                   sets the initial value. Default: light.
#   --banner <path>                 Path to a banner image (resolved
#                                   relative to --repo-root).
#   --repo-root <path>              Repo root (default: cwd).
#   --out <path>                    Output HTML path
#                                   (default: <report-dir>/<dirname>.html).
#
# Produces <report-dir>/<dirname>.html. The HTML is fully self-contained
# (images + CSS embedded) and ships a runtime light/dark toggle.
#
# Requires both light and dark SVG variants for each diagram. Run
# render.sh first; if only the legacy <name>.svg exists, compile-html
# falls back to using it for both themes (degrades gracefully).

set -eo pipefail

REPORT_DIR=""
BANNER=""
REPO_ROOT="$(pwd)"
OUT_PATH=""
STYLE="corporate"
THEME="light"

usage() {
  cat <<'EOF' >&2
usage: compile-html.sh <report-dir> [options]

Options:
  --style <blueprint|corporate>   Visual style (default: corporate)
  --theme <light|dark>            Initial theme (default: light)
  --banner <path>                 Banner image (resolved against --repo-root)
  --repo-root <path>              Repo root for banner resolution (default: cwd)
  --out <path>                    Output HTML path (default: <report-dir>/<date>.html)
  -h, --help                      Show this help.
EOF
}

while (( $# > 0 )); do
  case "$1" in
    -h|--help) usage; exit 0 ;;
    --banner)    BANNER="${2:?--banner requires a value}"; shift 2 ;;
    --repo-root) REPO_ROOT="${2:?--repo-root requires a value}"; shift 2 ;;
    --out)       OUT_PATH="${2:?--out requires a value}"; shift 2 ;;
    --style)     STYLE="${2:?--style requires a value}"; shift 2 ;;
    --theme)     THEME="${2:?--theme requires a value}"; shift 2 ;;
    --) shift; break ;;
    -*) echo "error: unknown option: $1" >&2; usage; exit 2 ;;
    *)
      if [[ -z "$REPORT_DIR" ]]; then
        REPORT_DIR="$1"
      else
        echo "error: unexpected argument: $1" >&2
        usage; exit 2
      fi
      shift
      ;;
  esac
done

if [[ -z "$REPORT_DIR" ]]; then usage; exit 2; fi
REPORT_DIR="${REPORT_DIR%/}"

if [[ ! -d "$REPORT_DIR" ]]; then
  echo "error: not a directory: $REPORT_DIR" >&2
  exit 1
fi

if [[ ! -f "$REPORT_DIR/README.md" ]]; then
  echo "error: missing $REPORT_DIR/README.md (run synthesis step first)" >&2
  exit 1
fi

case "$STYLE" in blueprint|corporate) ;; *) echo "error: --style must be 'blueprint' or 'corporate', got '$STYLE'" >&2; exit 2 ;; esac
case "$THEME" in light|dark) ;; *) echo "error: --theme must be 'light' or 'dark', got '$THEME'" >&2; exit 2 ;; esac

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
STYLE_DIR="$SKILL_DIR/assets/styles/$STYLE"
CSS_FILE="$STYLE_DIR/style.css"

if [[ ! -f "$TEMPLATE" ]]; then
  echo "error: template not found at $TEMPLATE" >&2
  exit 1
fi
if [[ ! -d "$STYLE_DIR" ]]; then
  echo "error: style '$STYLE' not found at $STYLE_DIR" >&2
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

# Mode markdown gets a class on its <h1> + raw-html dual-variant images.
# Originals are not modified; we work on copies in TMP_DIR.
TMP_DIR="$(mktemp -d -t arch-html-XXXXXX)"
trap 'rm -rf "$TMP_DIR"' EXIT

# transform_md <src> <dst> <slug-or-empty> <mode-dir-abs-or-empty>
#
# - Strips leading YAML frontmatter (only the first concatenated file
#   gets to keep its frontmatter for pandoc's metadata pipeline).
# - Tags the first H1 with a {.mode-<slug>} pandoc attribute so the
#   per-mode accent strip applies AND the heading appears in the TOC
#   with its h2 children nested correctly.
# - Wraps "receipts" sections (Callouts, Verification log, Synthesized
#   concepts, Open questions) in <details> blocks collapsed by default.
# - Rewrites `![alt](image.png|.svg)` to a raw-html dual-image pair so
#   the runtime light/dark toggle can show the matching variant.
transform_md() {
  local src="$1" dst="$2" slug="$3" mode_dir_abs="$4"

  awk -v slug="$slug" -v mode_dir="$mode_dir_abs" -v style="$STYLE" '
    function htmlescape(s) {
      gsub(/&/, "\\&amp;", s); gsub(/</, "\\&lt;", s); gsub(/>/, "\\&gt;", s)
      return s
    }
    function close_open_details() {
      if (in_details) {
        # Add a final blank line before </details> so the prior block ends.
        print ""
        print "</details>"
        print ""
        in_details = 0
      }
    }
    # Treat these h2 titles as collapsible "receipts" sections.
    function is_receipts(title,    t) {
      t = tolower(title)
      return (t ~ /^callouts?$/) ||
             (t ~ /^verification log$/) ||
             (t ~ /^synthesized concepts?$/) ||
             (t ~ /^open questions/) ||
             (t ~ /^cross-mode index$/) ||
             (t ~ /^verification summary$/)
    }
    BEGIN { h1_done = 0; in_frontmatter = 0; saw_first_line = 0; in_details = 0 }
    # Strip leading YAML frontmatter.
    !saw_first_line {
      saw_first_line = 1
      if ($0 == "---") { in_frontmatter = 1; next }
    }
    in_frontmatter {
      if ($0 == "---" || $0 == "...") { in_frontmatter = 0 }
      next
    }
    # First H1: tag with the mode class so it surfaces in the TOC.
    /^# / && !h1_done {
      close_open_details()
      title = substr($0, 3)
      gsub(/^[[:space:]]+|[[:space:]]+$/, "", title)
      if (slug != "") {
        print "# " title " {.mode-" slug "}"
      } else {
        print "# " title
      }
      h1_done = 1
      next
    }
    # Section headers (h2): close any open <details>, and if the new
    # section is a receipts section, open a new <details> around it.
    /^## / {
      close_open_details()
      title = substr($0, 4)
      gsub(/^[[:space:]]+|[[:space:]]+$/, "", title)
      if (is_receipts(title)) {
        print "<details class=\"receipts\">"
        print "<summary>" htmlescape(title) "</summary>"
        print ""
        in_details = 1
      } else {
        print
      }
      next
    }
    {
      line = $0
      output = ""
      while (match(line, /!\[[^]]*\]\([^)]+\.(png|svg)\)/)) {
        prefix = substr(line, 1, RSTART - 1)
        match_text = substr(line, RSTART, RLENGTH)
        rest = substr(line, RSTART + RLENGTH)

        match(match_text, /!\[([^]]*)\]/)
        alt = substr(match_text, RSTART + 2, RLENGTH - 3)

        match(match_text, /\(([^)]+)\)/)
        path_ext = substr(match_text, RSTART + 1, RLENGTH - 2)

        sub(/\.(png|svg)$/, "", path_ext)
        base = path_ext

        is_abs = (substr(base, 1, 1) == "/")
        if (!is_abs && mode_dir != "") base = mode_dir "/" base

        replacement = "<span class=\"diagram-pair\">"
        replacement = replacement "<img class=\"diagram-light\" src=\"" base "-" style "-light.svg\" alt=\"" htmlescape(alt) "\" />"
        replacement = replacement "<img class=\"diagram-dark\"  src=\"" base "-" style "-dark.svg\"  alt=\"" htmlescape(alt) "\" />"
        replacement = replacement "</span>"

        output = output prefix replacement
        line = rest
      }
      output = output line
      print output
    }
    END { close_open_details() }
  ' "$src" > "$dst"
}

transform_md "$REPORT_DIR/README.md" "$TMP_DIR/00-readme.md" "" "$( cd "$REPORT_DIR" && pwd )"

INPUTS=("$TMP_DIR/00-readme.md")
i=1
for mode in "${MODES[@]}"; do
  report="$REPORT_DIR/$mode/report.md"
  if [[ -f "$report" ]]; then
    transformed="$TMP_DIR/$(printf "%02d" "$i")-${mode}.md"
    mode_dir_abs="$( cd "$REPORT_DIR/$mode" && pwd )"
    transform_md "$report" "$transformed" "$mode" "$mode_dir_abs"
    INPUTS+=("$transformed")
    i=$((i + 1))
  fi
done

# Banner: resolve relative to repo-root.
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

# Determine pandoc embed flag.
EMBED_FLAGS=(--standalone)
if pandoc --help 2>&1 | grep -q -- '--embed-resources'; then
  EMBED_FLAGS+=(--embed-resources)
else
  EMBED_FLAGS+=(--self-contained)
fi

echo "compiling $OUT_PATH from ${#INPUTS[@]} markdown files (style=$STYLE theme=$THEME)…"
[[ -n "$BANNER" ]] && echo "  banner: $BANNER_RESOLVED"

pandoc \
  "${INPUTS[@]}" \
  --from=markdown+raw_html-tex_math_dollars-tex_math_single_backslash-tex_math_double_backslash-implicit_figures \
  --to=html5 \
  --template="$TEMPLATE" \
  --css="$CSS_FILE" \
  --resource-path="$REPORT_DIR:$REPO_ROOT:$STYLE_DIR:$SKILL_DIR/assets:." \
  --toc --toc-depth=2 \
  --metadata title="Architectural Analysis $DATE_STAMP" \
  --metadata date="$DATE_STAMP" \
  --metadata "style=$STYLE" \
  --metadata "theme=$THEME" \
  ${BANNER_META[@]+"${BANNER_META[@]}"} \
  "${EMBED_FLAGS[@]}" \
  -o "$OUT_PATH"

echo "done: $OUT_PATH"
echo
echo "open with: open '$OUT_PATH'  (macOS)  |  xdg-open '$OUT_PATH'  (Linux)"
