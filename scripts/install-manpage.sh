#!/usr/bin/env bash
# Install the claude-ctx manpage to the system

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MANPAGE_SOURCE="${SCRIPT_DIR}/../docs/claude-ctx.1"
MANPAGE_NAME="claude-ctx.1"

# Determine installation directory
if [[ "${OSTYPE}" == "darwin"* ]]; then
    # macOS
    MAN_DIR="/usr/local/share/man/man1"
elif [[ "${OSTYPE}" == "linux-gnu"* ]]; then
    # Linux
    if [[ -d "/usr/local/man/man1" ]]; then
        MAN_DIR="/usr/local/man/man1"
    elif [[ -d "/usr/share/man/man1" ]]; then
        MAN_DIR="/usr/share/man/man1"
    else
        echo "Error: Cannot find standard man directory" >&2
        exit 1
    fi
else
    echo "Error: Unsupported operating system: ${OSTYPE}" >&2
    exit 1
fi

# Check if manpage source exists
if [[ ! -f "${MANPAGE_SOURCE}" ]]; then
    echo "Error: Manpage source not found at ${MANPAGE_SOURCE}" >&2
    exit 1
fi

# Check if we need sudo
if [[ ! -w "${MAN_DIR}" ]]; then
    echo "Installing manpage to ${MAN_DIR} (requires sudo)..."
    sudo install -m 644 "${MANPAGE_SOURCE}" "${MAN_DIR}/${MANPAGE_NAME}"
else
    echo "Installing manpage to ${MAN_DIR}..."
    install -m 644 "${MANPAGE_SOURCE}" "${MAN_DIR}/${MANPAGE_NAME}"
fi

# Update man database
echo "Updating man database..."
if command -v mandb &> /dev/null; then
    # Linux
    sudo mandb -q
elif command -v makewhatis &> /dev/null; then
    # macOS/BSD
    sudo makewhatis "${MAN_DIR}"
fi

echo "✓ Manpage installed successfully"
echo "  View with: man claude-ctx"
echo "  Location: ${MAN_DIR}/${MANPAGE_NAME}"
