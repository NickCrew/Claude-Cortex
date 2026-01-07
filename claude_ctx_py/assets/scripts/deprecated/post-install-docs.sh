#!/usr/bin/env bash
# Post-installation script to copy architecture documentation to ~/.claude/docs/

set -euo pipefail

# Color output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}==>${NC} $1"
}

log_success() {
    echo -e "${GREEN}✓${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}Warning:${NC} $1"
}

# Determine project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${SCRIPT_DIR}/../.."

# Target directory
DOCS_TARGET="${HOME}/.claude/docs"

log_info "Installing architecture documentation..."

# Create target directory
mkdir -p "${DOCS_TARGET}"

# Source documentation files
DOCS_SOURCE="${PROJECT_ROOT}/docs/reference/architecture"

if [[ ! -d "${DOCS_SOURCE}" ]]; then
    log_warn "Architecture documentation not found at ${DOCS_SOURCE}"
    log_warn "Skipping documentation installation"
    exit 0
fi

# Copy documentation files
for file in architecture-diagrams.md quick-reference.md DIAGRAMS_README.md VISUAL_SUMMARY.txt README.md; do
    if [[ -f "${DOCS_SOURCE}/${file}" ]]; then
        cp "${DOCS_SOURCE}/${file}" "${DOCS_TARGET}/"
        log_success "Installed ${file}"
    else
        log_warn "Documentation file not found: ${file}"
    fi
done

log_success "Architecture documentation installed to ${DOCS_TARGET}/"
echo ""
log_info "View documentation:"
echo "  cat ${DOCS_TARGET}/VISUAL_SUMMARY.txt       # Quick ASCII overview"
echo "  cat ${DOCS_TARGET}/quick-reference.md       # One-page cheat sheet"
echo "  cat ${DOCS_TARGET}/architecture-diagrams.md # Comprehensive diagrams"
echo "  cat ${DOCS_TARGET}/DIAGRAMS_README.md       # Documentation guide"
echo ""
log_info "Or use the command:"
echo "  /docs:diagrams                               # View documentation"
