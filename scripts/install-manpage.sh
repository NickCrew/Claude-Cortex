#!/usr/bin/env bash
# Install the claude-ctx manpage to the system

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
shopt -s nullglob
MANPAGE_SOURCES=("${SCRIPT_DIR}/../docs/reference"/*.1)
shopt -u nullglob

if [[ ${#MANPAGE_SOURCES[@]} -eq 0 ]]; then
    echo "Error: No manpage sources found under docs/reference" >&2
    exit 1
fi

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

# Install each manpage
for manpage_source in "${MANPAGE_SOURCES[@]}"; do
    manpage_name="$(basename "${manpage_source}")"

    if [[ ! -w "${MAN_DIR}" ]]; then
        echo "Installing ${manpage_name} to ${MAN_DIR} (requires sudo)..."
        sudo install -m 644 "${manpage_source}" "${MAN_DIR}/${manpage_name}"
    else
        echo "Installing ${manpage_name} to ${MAN_DIR}..."
        install -m 644 "${manpage_source}" "${MAN_DIR}/${manpage_name}"
    fi
done

# Update man database
echo "Updating man database..."
if command -v mandb &> /dev/null; then
    # Linux
    sudo mandb -q
elif command -v makewhatis &> /dev/null; then
    # macOS/BSD
    sudo makewhatis "${MAN_DIR}"
fi

echo "✓ Installed ${#MANPAGE_SOURCES[@]} manpage(s) into ${MAN_DIR}"
echo "  Primary entry point: man claude-ctx"
