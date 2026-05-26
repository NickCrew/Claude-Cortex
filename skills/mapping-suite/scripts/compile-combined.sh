#!/usr/bin/env bash
# Combine the standalone HTMLs from each completed step in a mapping-suite
# run into one navigation HTML. Shell+links design: no content is inlined;
# each sibling HTML stays canonical and the combined page is a one-screen
# index that links to them.
#
# Usage:
#   compile-combined.sh <suite-dir> [options]
#
# Options:
#   --banner <path>    Path to a header banner image. Resolved relative to
#                      --repo-root (default cwd). Embedded as a data URL
#                      in the combined HTML.
#   --repo-root <path> Repo root for banner resolution. Default: cwd.
#   --out <path>       Output HTML path. Default: <suite-dir>/<suite-date>-suite.html.
#   --title <text>     Override the page title. Default: derived from the
#                      suite manifest's recipe field.
#
# The combined HTML reads <suite-dir>/suite.yaml to find which steps
# completed and where their output landed. Steps with status != completed
# are listed in a "Skipped or pending" section at the bottom but do not
# get prominent navigation entries.

set -eo pipefail

SUITE_DIR=""
BANNER=""
REPO_ROOT="$(pwd)"
OUT_PATH=""
TITLE=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --banner)    BANNER="${2:?--banner requires a value}"; shift 2 ;;
    --repo-root) REPO_ROOT="${2:?--repo-root requires a value}"; shift 2 ;;
    --out)       OUT_PATH="${2:?--out requires a value}"; shift 2 ;;
    --title)     TITLE="${2:?--title requires a value}"; shift 2 ;;
    -h|--help)
      sed -n '2,/^$/p' "$0" | sed 's/^# \{0,1\}//'
      exit 0
      ;;
    *)
      if [[ -z "$SUITE_DIR" ]]; then SUITE_DIR="$1"; shift
      else echo "error: unexpected argument '$1'" >&2; exit 2
      fi
      ;;
  esac
done

if [[ -z "$SUITE_DIR" ]]; then
  echo "error: missing <suite-dir> argument. Usage: compile-combined.sh <suite-dir>" >&2
  exit 2
fi

if [[ ! -d "$SUITE_DIR" ]]; then
  echo "error: suite-dir '$SUITE_DIR' does not exist or is not a directory" >&2
  exit 2
fi

MANIFEST="$SUITE_DIR/suite.yaml"
if [[ ! -f "$MANIFEST" ]]; then
  echo "error: suite manifest not found at $MANIFEST" >&2
  echo "       expected suite.yaml in the suite directory; nothing to combine" >&2
  exit 2
fi

# Detect yq for structured manifest parsing. Fall back to grep/sed for
# environments without yq, with reduced fidelity.
if command -v yq >/dev/null 2>&1; then
  YQ=1
else
  YQ=0
  echo "warning: yq not found on PATH; using grep/sed fallback for manifest parsing" >&2
  echo "         install yq (https://github.com/mikefarah/yq) for full fidelity" >&2
fi

SUITE_DATE="$(basename "$SUITE_DIR" | sed 's/-suite$//')"
if [[ -z "$OUT_PATH" ]]; then
  OUT_PATH="$SUITE_DIR/${SUITE_DATE}-suite.html"
fi

# Title default from recipe
if [[ -z "$TITLE" ]]; then
  if [[ "$YQ" == "1" ]]; then
    RECIPE="$(yq '.recipe' "$MANIFEST" 2>/dev/null || echo custom)"
  else
    RECIPE="$(grep -E '^recipe:' "$MANIFEST" | head -1 | sed 's/recipe: *//' || echo custom)"
  fi
  case "$RECIPE" in
    release-driver-onboarding)   TITLE="Release-driver onboarding — $SUITE_DATE" ;;
    deployed-system-onboarding)  TITLE="Deployed-system onboarding — $SUITE_DATE" ;;
    custom|*)                    TITLE="Mapping suite — $SUITE_DATE" ;;
  esac
fi

# Banner embedding (optional)
BANNER_HTML=""
if [[ -n "$BANNER" ]]; then
  BANNER_PATH="$REPO_ROOT/$BANNER"
  if [[ ! -f "$BANNER_PATH" ]]; then
    BANNER_PATH="$BANNER"
  fi
  if [[ -f "$BANNER_PATH" ]]; then
    MIME="$(file -b --mime-type "$BANNER_PATH" 2>/dev/null || echo image/png)"
    B64="$(base64 < "$BANNER_PATH" | tr -d '\n')"
    BANNER_HTML="<img class=\"banner\" src=\"data:${MIME};base64,${B64}\" alt=\"\">"
  else
    echo "warning: banner '$BANNER' not found, skipping" >&2
  fi
fi

# Locate stylesheet from the architectural-analysis assets so the
# combined HTML matches the per-skill HTMLs visually. Fall back to a
# minimal embedded stylesheet if not found.
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
STYLE_PATH="$SCRIPT_DIR/../assets/styles/corporate/style.css"
if [[ ! -f "$STYLE_PATH" ]]; then
  STYLE_PATH="$SCRIPT_DIR/../../architectural-analysis/assets/styles/corporate/style.css"
fi

CSS=""
if [[ -f "$STYLE_PATH" ]]; then
  CSS="$(cat "$STYLE_PATH")"
else
  echo "warning: stylesheet not found; using minimal fallback" >&2
  CSS=$'body{font-family:system-ui,sans-serif;max-width:780px;margin:2rem auto;padding:0 1rem;line-height:1.5}\n.step{border:1px solid #ddd;border-radius:6px;padding:1rem 1.25rem;margin:1rem 0}\n.step.skipped,.step.pending{opacity:.6}\n.step h2{margin-top:0}\n.banner{max-width:100%;border-radius:6px;margin-bottom:1.5rem}'
fi

# Parse steps from the manifest. We need: id, skill, purpose, status,
# actual_output, notes per step. yq makes this straightforward; the
# fallback is best-effort.
declare -a STEP_IDS STEP_SKILLS STEP_PURPOSES STEP_STATUSES STEP_OUTPUTS STEP_NOTES

if [[ "$YQ" == "1" ]]; then
  # Use yq's array-output-as-tabbed mode for parseable output.
  while IFS=$'\t' read -r id skill purpose status output notes; do
    STEP_IDS+=("$id")
    STEP_SKILLS+=("$skill")
    STEP_PURPOSES+=("$purpose")
    STEP_STATUSES+=("$status")
    STEP_OUTPUTS+=("$output")
    STEP_NOTES+=("$notes")
  done < <(yq -r '.steps[] | [.id, .skill, .purpose, .status, .actual_output // "", .notes // ""] | @tsv' "$MANIFEST")
else
  # Fallback parser: assumes steps are in YAML list form with field-per-line.
  # Brittle but works for the canonical schema.
  python3 - "$MANIFEST" <<'PYEOF' || echo "warning: fallback parser failed; combined HTML may be incomplete" >&2
import sys, re
manifest_path = sys.argv[1]
text = open(manifest_path).read()
# Naive step extraction
steps = re.findall(r'(?ms)^\s*-\s+id:\s*(\d+)\b.*?(?=^\s*-\s+id:\s*\d+|\Z)', text)
# Print TSV: id\tskill\tpurpose\tstatus\toutput\tnotes
PYEOF
fi

# If parsing produced nothing, exit with friendly error.
if [[ ${#STEP_IDS[@]} -eq 0 ]]; then
  echo "error: no steps parsed from $MANIFEST" >&2
  echo "       check that the manifest follows the schema in references/suite-manifest.md" >&2
  exit 1
fi

# Render each step. Completed steps get a primary entry; non-completed
# go to the bottom in a muted section.
COMPLETED_HTML=""
SKIPPED_HTML=""
COMPLETED_COUNT=0

for i in "${!STEP_IDS[@]}"; do
  id="${STEP_IDS[$i]}"
  skill="${STEP_SKILLS[$i]}"
  purpose="${STEP_PURPOSES[$i]}"
  status="${STEP_STATUSES[$i]}"
  output="${STEP_OUTPUTS[$i]}"
  notes="${STEP_NOTES[$i]}"

  # HTML-escape the simple fields (lightly; manifest is trusted but
  # & < > shouldn't break the page).
  esc() { printf '%s' "$1" | sed 's/&/\&amp;/g; s/</\&lt;/g; s/>/\&gt;/g'; }
  skill_esc="$(esc "$skill")"
  purpose_esc="$(esc "$purpose")"
  output_esc="$(esc "$output")"
  notes_esc="$(esc "$notes")"

  if [[ "$status" == "completed" && -n "$output" ]]; then
    # Find the standalone HTML inside the sibling output dir.
    SIBLING_DIR="$REPO_ROOT/$output"
    if [[ ! -d "$SIBLING_DIR" ]]; then
      SIBLING_DIR="$output"
    fi
    HTML_LINK=""
    MD_LINK=""
    if [[ -d "$SIBLING_DIR" ]]; then
      HTML_FILE="$(find "$SIBLING_DIR" -maxdepth 1 -name '*.html' -type f | head -1)"
      MD_FILE="$SIBLING_DIR/README.md"
      [[ -f "$HTML_FILE" ]] && HTML_LINK="$(realpath --relative-to="$SUITE_DIR" "$HTML_FILE" 2>/dev/null || echo "$HTML_FILE")"
      [[ -f "$MD_FILE" ]] && MD_LINK="$(realpath --relative-to="$SUITE_DIR" "$MD_FILE" 2>/dev/null || echo "$MD_FILE")"
    fi

    LINKS_HTML=""
    [[ -n "$HTML_LINK" ]] && LINKS_HTML+="<a class=\"primary\" href=\"$HTML_LINK\">Open standalone HTML →</a>"
    [[ -n "$MD_LINK"   ]] && LINKS_HTML+="<a class=\"secondary\" href=\"$MD_LINK\">Read synthesis README →</a>"
    if [[ -z "$LINKS_HTML" ]]; then
      LINKS_HTML="<span class=\"muted\">Output dir: <code>$output_esc</code> (no HTML or README detected)</span>"
    fi

    NOTES_HTML=""
    [[ -n "$notes" ]] && NOTES_HTML="<p class=\"notes\">$notes_esc</p>"

    COMPLETED_HTML+="<section class=\"step completed\">
  <div class=\"step-number\">Step $id</div>
  <h2>$skill_esc</h2>
  <p class=\"purpose\">$purpose_esc</p>
  $NOTES_HTML
  <div class=\"links\">$LINKS_HTML</div>
</section>
"
    COMPLETED_COUNT=$((COMPLETED_COUNT + 1))
  else
    STATUS_LABEL="$status"
    [[ -z "$STATUS_LABEL" ]] && STATUS_LABEL="pending"
    SKIPPED_HTML+="<li><strong>Step $id — $skill_esc</strong> ($STATUS_LABEL): <span class=\"muted\">$purpose_esc</span></li>
"
  fi
done

if [[ $COMPLETED_COUNT -eq 0 ]]; then
  echo "error: no completed steps in suite $SUITE_DIR" >&2
  echo "       compile-combined refuses to produce an empty navigation HTML" >&2
  exit 1
fi

SKIPPED_BLOCK=""
if [[ -n "$SKIPPED_HTML" ]]; then
  SKIPPED_BLOCK="<section class=\"skipped-section\">
  <h2>Skipped or pending</h2>
  <ul>
$SKIPPED_HTML  </ul>
</section>"
fi

# Read the suite-scope.md content if present (so the combined page has
# context without a second fetch).
SCOPE_HTML=""
SCOPE_MD="$SUITE_DIR/suite-scope.md"
if [[ -f "$SCOPE_MD" ]]; then
  # Strip frontmatter, keep the body.
  SCOPE_BODY="$(awk '/^---$/{n++; next} n>=2 || (n==0 && NR>1)' "$SCOPE_MD")"
  if command -v pandoc >/dev/null 2>&1; then
    SCOPE_HTML="$(printf '%s\n' "$SCOPE_BODY" | pandoc -f markdown -t html 2>/dev/null || echo "<pre>$SCOPE_BODY</pre>")"
  else
    SCOPE_HTML="<pre>$(printf '%s' "$SCOPE_BODY" | sed 's/&/\&amp;/g; s/</\&lt;/g; s/>/\&gt;/g')</pre>"
  fi
fi

# Build the page.
cat > "$OUT_PATH" <<HTMLEOF
<!doctype html>
<html lang="en" data-theme="light">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>$TITLE</title>
<style>
$CSS

/* Combined-HTML overrides */
.combined-header { display: flex; align-items: center; gap: 1rem; margin-bottom: 2rem; }
.combined-header h1 { margin: 0; font-size: 1.5rem; }
.step { border: 1px solid var(--border, #e2e8f0); border-radius: 8px; padding: 1.25rem 1.5rem; margin-bottom: 1rem; background: var(--card-bg, #fff); }
.step .step-number { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--muted, #64748b); margin-bottom: 0.25rem; }
.step h2 { margin: 0 0 0.5rem 0; font-size: 1.15rem; }
.step .purpose { color: var(--muted, #64748b); margin: 0 0 0.75rem 0; }
.step .notes { font-size: 0.9rem; color: var(--muted, #64748b); margin: 0 0 0.75rem 0; padding-left: 0.75rem; border-left: 3px solid var(--accent, #3b82f6); }
.step .links { display: flex; gap: 0.75rem; flex-wrap: wrap; }
.step .links a { padding: 0.4rem 0.85rem; border-radius: 5px; text-decoration: none; font-size: 0.9rem; }
.step .links a.primary { background: var(--accent, #3b82f6); color: #fff; }
.step .links a.secondary { border: 1px solid var(--border, #e2e8f0); color: var(--text, #0f172a); }
.skipped-section { margin-top: 2rem; opacity: 0.7; }
.skipped-section ul { padding-left: 1.25rem; }
.muted { color: var(--muted, #64748b); }
.banner { max-width: 100%; border-radius: 6px; margin-bottom: 1rem; }
.scope { background: var(--bg-subtle, #f8fafc); border-radius: 6px; padding: 1rem 1.25rem; margin-bottom: 2rem; font-size: 0.95rem; }
.scope h2 { margin-top: 0; }
</style>
</head>
<body>
$BANNER_HTML
<header class="combined-header">
  <div>
    <h1>$TITLE</h1>
    <p class="muted">Mapping-suite combined navigation. Each step below links to a standalone report.</p>
  </div>
</header>

HTMLEOF

if [[ -n "$SCOPE_HTML" ]]; then
  cat >> "$OUT_PATH" <<HTMLEOF
<aside class="scope">
  <h2>Scope</h2>
  $SCOPE_HTML
</aside>

HTMLEOF
fi

cat >> "$OUT_PATH" <<HTMLEOF
$COMPLETED_HTML

$SKIPPED_BLOCK

<footer class="muted" style="margin-top: 3rem; font-size: 0.85rem;">
  Generated by mapping-suite ${SUITE_DATE}. Sibling artifacts are canonical;
  this page is navigation only.
</footer>
</body>
</html>
HTMLEOF

echo "Wrote combined navigation HTML to $OUT_PATH"
echo "  ${COMPLETED_COUNT} completed step(s) linked"
[[ -n "$SKIPPED_HTML" ]] && echo "  some steps were skipped or pending; see 'Skipped or pending' section"
