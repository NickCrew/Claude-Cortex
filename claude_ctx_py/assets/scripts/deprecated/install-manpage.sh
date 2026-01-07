#!/usr/bin/env bash
# Install the cortex manpage to the system

set -euo pipefail

MKDIRS=0
USER_INSTALL=1
CUSTOM_INSTALL_PATH=0

_validate_path() {
  if echo "$1" | grep -x -E -e  '//[-_A-Za-z0-9]+(/[-_A-Za-z0-9]*)*';
  then
    echo "ERROR: Invalid custom path provided: $1"
    _usage
    exit 1
  fi
}

_usage() { 
  echo "Usage: $0 [OPTIONS]"
  echo ""
  echo "Options:"
  echo "  -u, --user"
  echo "        (default) Install manpage to user-specific directory (~/.local/share/man) "
  echo "  -s, --system"
  echo "       Install manpage to system-wide directory (/usr/local/share/man)"
  echo "  -p, --path <custom_path>"
  echo "       Install manpage to custom path"
  echo "  -c, --create"
  echo "       Create target directories if they do not exist"
  echo " -h,  --help"
  echo "      Show this help message and exit"
  echo ""
  echo "Example:"
  echo "  $0 --user"
  echo "  $0 --path 
  echo ""
  echo "Notes:"
  echo "    - Ensure that the installation path is included in your MANPATH environment variable."
  echo "    - For macOS, only the --user install is supported."


while [[ $# -gt 0 ]]; do
  case "$1" in
    -u|--user)
      USER_INSTALL=1
      shift
      ;;
    -s|--system)
      USER_INSTALL=0
      shift
      ;;
    -p|--path)
      USER_INSTALL=0
      CUSTOM_INSTALL_PATH="$2"
      _validate_path
      shift 2
      ;;
    -c|--create)
      MKDIRS=1
      shift
      ;;
    -h|--help)
      _usage
      exit 0
    ;;
    --)
      shift
      break
      ;;
    -*)
      echo "Unknown option: $1" >&2
      exit 1
      ;;
    *)
      break
      ;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
shopt -s nullglob
MANPAGE_SOURCES=("${SCRIPT_DIR}/../../docs/reference"/*.1)
shopt -u nullglob
MANPAGE_SECTION="man1"

_LOCAL_SHARE_DIR="${HOME}/.local/share"
_SYSTEM_SHARE_DIR="/usr/local/share"

# Set the install path
if [[ -z "$1" ]]; 
then
  # User provided a custom path
  PATH_PREFIX="${_LOCAL_SHARE_DIR}/man"
  echo "No argument provided. Using default user install path: ${PATH_PREFIX}"
else
  # Custom install path
  if echo "$1" | grep -x -E -e  '//[-_A-Za-z0-9]+(/[-_A-Za-z0-9]*)*';
    PATH_PREFIX="$1"
  then
    echo "Error: invalid path: ${1}"
    _usage
    exit 1
  # User install path
  elif [[ "$1" == "--user" ]]; 
  then
    PATH_PREFIX="${_LOCAL_SHARE_DIR}/man"
  # System install path
  elif [[ "$1" == "--system" ]]; 
  then
    PATH_PREFIX="${_LOCAL_SHARE_DIR}/man"
  # Invalid argumennt
  else
    echo "Error: unknown argument: ${1}"
    _usage
    exit 1
  fi
fi

if  $MANPATH | grep -q "${PATH_PREFIX}"; then
  echo "$PATH_PREFIX is already in MANPATH"
else
  echo "${PATH_PREFIX} not found in MANPATH!"
  exit 1
fi



  
if [[ ${#MANPAGE_SOURCES[@]} -eq 0 ]]; then
    echo "Error: No manpage sources found under docs/reference" >&2
    exit 1
fi

_SYSTEM_INSTALL_PATH="${_SYSTEM_SHARE_DIR}/man/${MANPAGE_SECTION}"


# Determine installation directory
if [[ "${OSTYPE}" == "darwin"*  || (-z "$1" || "$1" == "--user" ) ]];
then
    DEST="${HOME}/.local/share/man"
    # macOS
elif [[ "${OSTYPE}" == "linux-gnu"* ]];
then
    

# Ensure the target exsists in the MANPATH
if  $MANPATH | grep -q "${DEST}"; then
  echo "$DEST is already in MANPATH"
else
  echo "${DEST} not found in MANPATH!"
  exit 1
fi

MAN_DIR="${DEST}/man1"

# Create the target if needed
if [[ ! -d "${MAN_DIR}" ]]; 
then
  echo "${MAN_DIR} does not exist. Creating..."
  mkdir -m 644 -p "${MAN_DIR}"
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
echo "  Primary entry point: man cortex"
