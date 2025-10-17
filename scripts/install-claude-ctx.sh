#!/usr/bin/env bash
#
# Dead simple installer for claude scripts
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

INSTALL_DIR="${INSTALL_DIR:-${HOME}/.local/bin}"
[ -z "$1" ] || INSTALL_DIR="$1"

# Find all scripts in the current directory that start with 
# the PREFIX and do not end with install.sh
PREFIX=""
SCRIPTS=("$SCRIPT_DIR"/"$PREFIX"*)
SCRIPTS=("${SCRIPTS[@]//*install*.sh}")

# Install each script
mkdir -p "$INSTALL_DIR"
for script in "${SCRIPTS[@]}"; do
  script_name=$(basename "$script")
  target="$INSTALL_DIR/$script_name"
  echo "Installing $script_name to $target"
  cp "$script" "$target"
  chmod +x "$target"
done

# Ckeck if INSTALL_DIR is in the $PATH environment variable
if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
    echo "Warning: $INSTALL_DIR is not in your PATH environment variable."
    echo "You may want to add the following line to your shell profile (e.g., ~/.bashrc or ~/.zshrc):"
    echo "export PATH=\"\$PATH:$INSTALL_DIR\""
fi
