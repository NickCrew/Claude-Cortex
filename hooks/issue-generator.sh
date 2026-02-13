#!/usr/bin/env bash
# Generate GitHub issue files from audit report
#
# Usage: ./issue-generator.sh [audit-report.md] [output-dir]
# Output: Individual markdown files ready for issue creation
#
# Creates timestamped issue files for paper trail documentation.

set -euo pipefail

AUDIT_FILE="${1:-audit-report.md}"
OUTPUT_DIR="${2:-./issues-pending}"
TIMESTAMP=$(date +"%Y%m%d-%H%M%S")

if [[ ! -f "$AUDIT_FILE" ]]; then
    echo "Error: Audit file not found: $AUDIT_FILE"
    echo "Run ./hooks/audit.sh first"
    exit 1
fi

mkdir -p "$OUTPUT_DIR"

# Parse clippy errors and create issues
parse_clippy_issues() {
    local content="$1"
    local issue_num=1
    
    # Extract error lines
    echo "$content" | grep -E "^error\[E[0-9]+\]:" | while read -r line; do
        local error_code=$(echo "$line" | grep -oE "E[0-9]+")
        local error_msg=$(echo "$line" | sed 's/^error\[E[0-9]*\]: //')
        
        local filename="$OUTPUT_DIR/${TIMESTAMP}-clippy-error-${error_code}-${issue_num}.md"
        
        cat > "$filename" << EOF
# Clippy Error: $error_code

## Description
$error_msg

## Category
- Type: Compilation Error
- Severity: HIGH
- Source: cargo clippy

## Detected
$(date -u +"%Y-%m-%dT%H:%M:%SZ")

## Suggested Fix
Review the error code documentation: https://doc.rust-lang.org/error_codes/${error_code}.html

## Status
- [ ] Investigated
- [ ] Fixed
- [ ] Verified
EOF
        
        echo "Created: $filename"
        ((issue_num++)) || true
    done
}

# Parse test failures and create issues
parse_test_failures() {
    local content="$1"
    local issue_num=1
    
    # Extract failed test names
    echo "$content" | grep -E "^---- .* ----$" | sed 's/---- //;s/ ----$//' | while read -r test_name; do
        local filename="$OUTPUT_DIR/${TIMESTAMP}-test-failure-${issue_num}.md"
        
        cat > "$filename" << EOF
# Test Failure: $test_name

## Description
Test \`$test_name\` is failing.

## Category
- Type: Test Failure
- Severity: HIGH
- Source: cargo test

## Detected
$(date -u +"%Y-%m-%dT%H:%M:%SZ")

## Investigation Steps
1. Run \`cargo test $test_name -- --nocapture\` for full output
2. Check if failure is due to test logic or implementation bug
3. Verify test assertions are correct

## Status
- [ ] Investigated
- [ ] Root cause identified
- [ ] Fixed
- [ ] Verified
EOF
        
        echo "Created: $filename"
        ((issue_num++)) || true
    done
}

# Parse clippy warnings and create issues
parse_clippy_warnings() {
    local content="$1"
    local issue_num=1
    
    # Extract warning lines (deduplicate by message)
    echo "$content" | grep -E "^warning:" | sort -u | head -20 | while read -r line; do
        local warning_msg=$(echo "$line" | sed 's/^warning: //')
        local safe_name=$(echo "$warning_msg" | tr -cs 'a-zA-Z0-9' '-' | head -c 30)
        
        local filename="$OUTPUT_DIR/${TIMESTAMP}-clippy-warning-${issue_num}.md"
        
        cat > "$filename" << EOF
# Clippy Warning

## Description
$warning_msg

## Category
- Type: Code Quality Warning
- Severity: MEDIUM
- Source: cargo clippy

## Detected
$(date -u +"%Y-%m-%dT%H:%M:%SZ")

## Status
- [ ] Investigated
- [ ] Fixed or Suppressed with justification
- [ ] Verified
EOF
        
        echo "Created: $filename"
        ((issue_num++)) || true
    done
}

# Read audit file content
AUDIT_CONTENT=$(cat "$AUDIT_FILE")

echo "Generating issues from: $AUDIT_FILE"
echo "Output directory: $OUTPUT_DIR"
echo ""

# Generate issues
parse_clippy_issues "$AUDIT_CONTENT"
parse_test_failures "$AUDIT_CONTENT"
parse_clippy_warnings "$AUDIT_CONTENT"

# Count generated files
ISSUE_COUNT=$(ls -1 "$OUTPUT_DIR"/${TIMESTAMP}-*.md 2>/dev/null | wc -l || echo "0")

echo ""
echo "Generated $ISSUE_COUNT issue files in $OUTPUT_DIR"
echo ""
echo "Next steps:"
echo "  1. Review generated issues"
echo "  2. Push to issue tracker with: gh issue create --title 'xxx' --body-file issues-pending/xxx.md"
echo "  3. Or batch create: for f in $OUTPUT_DIR/${TIMESTAMP}-*.md; do gh issue create --body-file \"\$f\"; done"
