#!/usr/bin/env bash
# Sanity check over a wiring-audit report's citations.
#
# Usage: verify-findings.sh <report.md> [<repo-root>]
#
# Extracts every path:line citation from the report and confirms:
#   - the path exists relative to repo-root (default: cwd)
#   - the line number is within the file's line count
#
# Coarse check, not full verification. Does NOT confirm that the cited
# line content matches the finding's evidence string. Use as a fast gate;
# the orchestrator's verification protocol is still required for
# trustworthy findings.

set -euo pipefail

REPORT="${1:?usage: verify-findings.sh <report.md> [<repo-root>]}"
REPO_ROOT="${2:-.}"

if [[ ! -f "$REPORT" ]]; then
  echo "error: report not found: $REPORT" >&2
  exit 1
fi

if [[ ! -d "$REPO_ROOT" ]]; then
  echo "error: repo root not a directory: $REPO_ROOT" >&2
  exit 1
fi

ok=0
missing=0
oob=0

# Extract path:line patterns. Path must contain at least one slash and a
# file extension (so URLs and bare words don't match).
mapfile -t citations < <(
  python3 - "$REPORT" <<'PY'
import re, sys, pathlib
report = pathlib.Path(sys.argv[1])
text = report.read_text()
seen = set()
pat = re.compile(r'([A-Za-z0-9_./\-]+\.[A-Za-z0-9]+):([0-9]+)')
for m in pat.finditer(text):
    path, line = m.group(1), m.group(2)
    if '/' not in path:
        continue
    key = f"{path}:{line}"
    if key in seen:
        continue
    seen.add(key)
    print(key)
PY
)

if (( ${#citations[@]} == 0 )); then
  echo "warn: no citations found in $REPORT" >&2
  exit 0
fi

for cite in "${citations[@]}"; do
  path="${cite%:*}"
  line="${cite##*:}"
  full="$REPO_ROOT/$path"

  if [[ ! -f "$full" ]]; then
    echo "  MISSING: $cite (file not found at $full)"
    missing=$((missing + 1))
    continue
  fi

  total_lines=$(wc -l < "$full" | tr -d ' ')
  if (( line > total_lines + 1 )); then
    echo "  OUT-OF-BOUNDS: $cite (file has $total_lines lines)"
    oob=$((oob + 1))
    continue
  fi

  ok=$((ok + 1))
done

echo
echo "summary: ok=$ok missing=$missing out-of-bounds=$oob (total=${#citations[@]})"

if (( missing > 0 || oob > 0 )); then
  exit 1
fi
