#!/usr/bin/env bash
# Comprehensive installation script for cortex
# Installs package, shell completions, and manpage

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Options
INSTALL_PACKAGE=true
INSTALL_COMPLETIONS=true
INSTALL_MANPAGE=true
EDITABLE_MODE=true
SHELL_TYPE=""
OS=$(uname | tr '[:upper:]' '[:lower:]')

#  Package manager (can be pip, pipx, or uv)
PKG_MGR="pip"

usage() {
    cat <<EOF
Usage: $0 [OPTIONS]

Install cortex with optional components.

OPTIONS:
    -h, --help              Show this help message

    # Select components
    --no-package            Skip Python package installation
    --no-completions        Skip shell completion installation
    --no-docs               Skip manpage and documentation installation
    --shell SHELL           Specify shell (bash, zsh, fish) for completions
    --all                   Install everything (default)

    # Alt. Installation modes
    [--system|--user]       Install package system-wide (requires sudo)
                            or for the current user only.
                            Default is editable mode for current user.

    # Package manger
    [--uv|--pipx]           Use 'uv' or 'pipx' as package manager
                            instead of pip

EXAMPLES:
    $0                      # Install only the package in editable mode
    $0 --shell zsh          # Install everything EXCEPT the package
    $0 --no-completions     # Install package and manpage only
    $0 --shell zsh          # Install with zsh completions only
    $0 --system-install     # Install system-wide (not editable)
    $0                      # Install package only in editable mode
    $0 --
    $0 --shell zsh   # Install in editable mode with all 
                              shell integrations, docs, etc.


NOTES:
    > The default installation mode is editable and 
      only links an executable to  ~/.local
    > The system (global) install mode  is NOT editable, 
      requires sudo privileges and installs to /usr/local
    > The user install mode is NOT editable and 
      installs to ~/.local
    > Any manpages, docs or shell integrations use the same
      base install path, e.g. ~/.local/man for user mode

EOF
}

log_info() {
    echo -e "${BLUE}==>${NC} $1"
}

log_success() {
    echo -e "${GREEN}✓${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1" >&2
}

detect_shell() {
    if [[ -n "${SHELL_TYPE}" ]]; then
        return
    fi

    if [[ -n "${SHELL}" ]]; then
        case "${SHELL}" in
            */bash) SHELL_TYPE="bash" ;;
            */zsh) SHELL_TYPE="zsh" ;;
            */fish) SHELL_TYPE="fish" ;;
            *) SHELL_TYPE="bash" ;;
        esac
    else
        SHELL_TYPE="bash"
    fi
}

check_path() {
  test -d "$1" && return 0

  # Check for automatic directory creation enabled
  if [[ "$MKDIRS" != "true" ]]; 
  then
    echo "$1 does not exist. Use --mkdirs to create automatically"
    return 1
  fi

  # Check if the user has permission to create the directory
  base_path=$(echo "$1" | cut -d '/' -f1-3)
  if [[  -w "$base_path" ]]; 
  then
    # User can write 
    mkdir -p "$1"
  else
    # Try with sudo
    echo "No permissions to write in ${base_path}."
    echo "Trying with sudo..."
    sudo mkdir -p "$1" 
  fi

  # Confirm creation
  test -d "$1" \
    && echo "Created directory $1" \
    && return 0 \
    || echo "Failed to create directory $1. "

  return 1
}

check_manpath() { 
  local target="$1"
  local rc_files=">> ${HOME}/.bashrc >> $ZDOTDIR/.zshrc >> ${CONFIG_DIR}/fish/config.fish"
  
  if manpath | grep -q "$target" ; then return 0; fi

  log_warn "$target not found in MANPATH"
  echo "Use the following command to add it to your shell configuration:"
  echo "    echo 'export MANPATH=\"\$MANPATH:${target}\"' ${rc_files} && eval "exec \$SHELL""
  return 1
}

print_dirs() {
  echo "---------[ Installation Directories ]----------------"
  echo "Base:          ${DATA_DIR}"
  echo "Docs:          ${DOC_DIR}"
  echo "Manpages:      ${MAN_DIR}"
  echo "-----------------------------------------------------"
}

set_install_paths() {

  if [[ "${OSTYPE}" == "darwin"* ]]; 
  then
    DATA_DIR="${HOME}/.local/share"
    DOC_DIR="${HOME}/Library/Documentation/cortex"
    MAN_DIR="${DATA_DIR}/man/man1"
    return 0
  fi
  
  [[ "${OSTYPE}" != "linux-gnu"* ]] && (log_error "Unsupported OS: $OSTYPE"; return 1)


  if [[ "${SYSTEM_INSTALL" == "true" ]]; then 
    DATA_DIR=/usr/local/share
    CONFIG_PATH="/etc/cortex"
  fi

  DOC_DIR="${DATA_DIR}/cortex/doc"
  MAN_DIR="${DATA_DIR}/man/man1"


  return 0
      
}

install_package() {
    log_info "Installing cortex Python package..."

    cd "${PROJECT_ROOT}"

    if [[ "${EDITABLE_MODE}" == "true" ]]; then
        log_info "Installing in editable mode with dev dependencies..."
        python3 -m pip install -e ".[dev]" || {
            log_error "Failed to install package"
            return 1
        }
        log_success "Package installed in editable mode"
    else
        log_info "Installing system-wide..."
        python3 -m pip install . || {
            log_error "Failed to install package"
            return 1
        }
        log_success "Package installed system-wide"
    fi
}

install_completions() {
    log_info "Installing shell completions for ${SHELL_TYPE}..."

    # Check if argcomplete is installed
    if ! python3 -c "import argcomplete" 2>/dev/null; then
        log_warn "argcomplete not found. Installing..."
        python3 -m pip install argcomplete || {
            log_error "Failed to install argcomplete"
            return 1
        }
    fi

    # Ensure cortex is available
    if ! command -v cortex &> /dev/null; then
        log_error "cortex command not found. Install package first."
        return 1
    fi

    # Generate completion script
    case "${SHELL_TYPE}" in
        bash)
            install_bash_completions
            ;;
        zsh)
            install_zsh_completions
            ;;
        fish)
            install_fish_completions
            ;;
        *)
            log_error "Unsupported shell: ${SHELL_TYPE}"
            return 1
            ;;
    esac
}

install_bash_completions() {
    local completion_dir="${DATA_DIR}/bash-completion/completions"
    local completion_file="${completion_dir}/cortex"

    # Create directory if it doesn't exist
    mkdir -p "${completion_dir}"

    # Generate completion script
    register-python-argcomplete cortex > "${completion_file}" || {
        log_error "Failed to generate bash completions"
        return 1
    }

    log_success "Bash completions installed to ${completion_file}"
    log_info "Add this to your ~/.bashrc to enable completions:"
    echo "    source ${completion_file}"

    # Check if already sourced in .bashrc
    if [[ -f "${HOME}/.bashrc" ]] && grep -q "cortex" "${HOME}/.bashrc"; then
        log_info "Completions already configured in ~/.bashrc"
    else
        log_warn "To enable now, run: source ${completion_file}"
    fi
}

install_zsh_completions() {
    local completion_dir="${DATA_DIR}/zsh/site-functions"
    local completion_file="${completion_dir}/_cortex"

    # Create directory if it doesn't exist
    mkdir -p "${completion_dir}"

    # Generate completion script
    register-python-argcomplete --shell zsh cortex > "${completion_file}" || {
        log_error "Failed to generate zsh completions"
        return 1
    }

    log_success "Zsh completions installed to ${completion_file}"

    # Check if directory is in fpath
    if zsh -c 'echo $fpath' | grep -q "${completion_dir}"; then
      log_info "Completion directory already in fpath"
    else
        log_warn "Add this to your ~/.zshrc before compinit:"
        echo "    fpath=(${completion_dir} \$fpath)"
        echo "    autoload -Uz compinit && compinit"
    fi

    log_warn "Restart your shell or run: exec zsh"
}

install_fish_completions() {
    local completion_dir="${CONFIG_DIR}/fish/completions"
    local completion_file="${completion_dir}/cortex.fish"

    # Create directory if it doesn't exist
    mkdir -p "${completion_dir}"

    # Generate completion script
    register-python-argcomplete --shell fish cortex > "${completion_file}" || {
        log_error "Failed to generate fish completions"
        return 1
    }

    log_success "Fish completions installed to ${completion_file}"
    log_warn "Completions will be available in new fish shells"
}

install_manpage() {
    log_info "Generating manpages..."
    
    # Generate fresh manpages from CLI definitions
    python3 "${SCRIPT_DIR}/../generate-manpages.py" || {
        log_warn "Manpage generation failed, using existing manpages"
    }
    
    log_info "Installing manpage(s)..."

    local manpage_dir="${PROJECT_ROOT}/docs/reference"
    local manpage_sources=("${manpage_dir}"/*.1)

    if [[ ${#manpage_sources[@]} -eq 0 ]]; then
        log_error "No manpage sources found under ${manpage_dir}"
        return 1
    fi

    # Determine installation directory
    if [[ "${OSTYPE}" == "darwin"* ]]; then
        # macOS
        MAN_DIR="${DATA_DIR}/man/man1"
    elif [[ "${OSTYPE}" == "linux-gnu"* ]]; then
        # Linux
        if [[ -d "${DATA_DIR}/man/man1" ]]; then
            MAN_DIR="${DATA_DIR}/man/man1"
        else
            log_error "Cannot find standard man directory"
            return 1
        fi
    else
        log_error "Unsupported operating system: ${OSTYPE}"
        return 1
    fi

    for manpage_source in "${manpage_sources[@]}"; do
        local manpage_name
        manpage_name="$(basename "${manpage_source}")"

        if [[ ! -w "${MAN_DIR}" ]]; then
            log_info "Installing ${manpage_name} to ${MAN_DIR} (requires sudo)..."
            sudo install -m 644 "${manpage_source}" "${MAN_DIR}/${manpage_name}" || {
                log_error "Failed to install ${manpage_name}"
                return 1
            }
        else
            install -m 644 "${manpage_source}" "${MAN_DIR}/${manpage_name}" || {
                log_error "Failed to install ${manpage_name}"
                return 1
            }
        fi
    done

    # Update man database
    log_info "Updating man database..."
    if command -v mandb &> /dev/null; then
        # Linux
        sudo mandb -q 2>/dev/null || true
    elif command -v makewhatis &> /dev/null; then
        # macOS/BSD
        sudo makewhatis "${MAN_DIR}" 2>/dev/null || true
    fi

    log_success "Installed ${#manpage_sources[@]} manpage(s) to ${MAN_DIR}"
    log_info "Primary entry point: man cortex"
}

verify_installation() {
    log_info "Verifying installation..."

    local all_good=true

    # Check command
    if command -v cortex &> /dev/null; then
        log_success "cortex command available"
        cortex --help > /dev/null 2>&1 && log_success "cortex runs correctly"
    else
        log_error "cortex command not found"
        all_good=false
    fi

    # Check manpage
    if man -w cortex &> /dev/null; then
        log_success "Manpage installed and accessible"
    else
        log_warn "Manpage not accessible via 'man cortex'"
    fi

    # Check completions
    case "${SHELL_TYPE}" in
        bash)
            if [[ -f "${DATA_DIR}/ash-completion/completions/cortex" ]]; then
                log_success "Bash completions installed"
            fi
            ;;
        zsh)
            if [[ -f "${DATA_DIR}/zsh/site-functions/_cortex" ]]; then
                log_success "Zsh completions installed"
            fi
            ;;
        fish)
            if [[ -f "${HOME}/.config/fish/completions/cortex.fish" ]]; then
                log_success "Fish completions installed"
            fi
            ;;
    esac

    if [[ "${all_good}" == "true" ]]; then
        echo ""
        log_success "Installation complete!"
        echo ""
        log_info "Next steps:"
        echo "  1. Restart your shell or source your shell config"
        echo "  2. Try: cortex status"
        echo "  3. View docs: man cortex"
        echo "  4. Test completions: cortex <TAB><TAB>"
    fi
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            usage
            exit 0
            ;;
        --no-package)
            INSTALL_PACKAGE=false
            shift
            ;;
        --no-completions)
            INSTALL_COMPLETIONS=false
            shift
            ;;
        --no-manpage)
            INSTALL_MANPAGE=false
            shift
            ;;
        --system-install)
            EDITABLE_MODE=false
            if [[ "$OS" != "darwin" ]]; then 
              DATA_DIR="/usr/local/share"
            fi
            shift
            ;;
        --user-install)
            EDITABLE_MODE=false
            DATA_DIR="${XDG_DATA_HOME:-$HOME/.local/share}"
            shift
            ;;
        --shell)
            SHELL_TYPE="$2"
            shift 2
            ;;
        --all)
            INSTALL_PACKAGE=true
            INSTALL_COMPLETIONS=true
            INSTALL_MANPAGE=true
            shift
            ;;
        *)
            log_error "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Main installation flow
echo ""
log_info "Cortex Installation Script"
echo ""



[[ "${OSTYPE}" == "linux-gnu"* || "${OSTYPE}" == "darwin"* ]] \
  || (log_error "Unsupported OS: ${OSTYPE}"; exit 1)

echo "Prepping the installation paths..."

MAN_DIR="${DATA_DIR}/man/man1"
DOC_DIR="${DATA_DIR}/cortex/doc"

[[ "${OSTYPE}" == "darwin"* ]] \
  && DOC_DIR="${HOME}/Library/Documentation/cortex"

print_dirs

check_path "${DATA_DIR}"
check_path "${DOC_DIR}"
check_path "${MAN_DIR}"
check_manpath "${MAN_DIR}"


detect_shell

if [[ "${INSTALL_PACKAGE}" == "true" ]]; then
    install_package || exit 1
    echo ""

    # Install architecture documentation
    if [[ -f "${SCRIPT_DIR}/post-install-docs.sh" ]]; then
        log_info "Installing architecture documentation..."
        "${SCRIPT_DIR}/post-install-docs.sh" || log_warn "Documentation installation failed (non-fatal)"
        echo ""
    fi
fi

if [[ "${INSTALL_COMPLETIONS}" == "true" ]]; then
    install_completions || log_warn "Completion installation failed (non-fatal)"
    echo ""
fi

if [[ "${INSTALL_MANPAGE}" == "true" ]]; then
    install_manpage || log_warn "Manpage installation failed (non-fatal)"
    echo ""
fi

verify_installation
