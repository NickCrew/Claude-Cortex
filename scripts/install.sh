#!/usr/bin/env bash
# Comprehensive installation script for claude-ctx
# Installs package, shell completions, and manpage

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${SCRIPT_DIR}/.."

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

usage() {
    cat <<EOF
Usage: $0 [OPTIONS]

Install claude-ctx with optional components.

OPTIONS:
    -h, --help              Show this help message
    --no-package            Skip package installation
    --no-completions        Skip shell completion installation
    --no-manpage            Skip manpage installation
    --system-install        Install package system-wide (not editable)
    --shell SHELL           Specify shell (bash, zsh, fish) for completions
    --all                   Install everything (default)

EXAMPLES:
    $0                      # Install everything in editable mode
    $0 --no-completions     # Install package and manpage only
    $0 --shell zsh          # Install with zsh completions only
    $0 --system-install     # Install system-wide (not editable)

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

install_package() {
    log_info "Installing claude-ctx Python package..."

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

    # Ensure claude-ctx is available
    if ! command -v claude-ctx &> /dev/null; then
        log_error "claude-ctx command not found. Install package first."
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
    local completion_dir="${HOME}/.local/share/bash-completion/completions"
    local completion_file="${completion_dir}/claude-ctx"

    # Create directory if it doesn't exist
    mkdir -p "${completion_dir}"

    # Generate completion script
    register-python-argcomplete claude-ctx > "${completion_file}" || {
        log_error "Failed to generate bash completions"
        return 1
    }

    log_success "Bash completions installed to ${completion_file}"
    log_info "Add this to your ~/.bashrc to enable completions:"
    echo "    source ${completion_file}"

    # Check if already sourced in .bashrc
    if [[ -f "${HOME}/.bashrc" ]] && grep -q "claude-ctx" "${HOME}/.bashrc"; then
        log_info "Completions already configured in ~/.bashrc"
    else
        log_warn "To enable now, run: source ${completion_file}"
    fi
}

install_zsh_completions() {
    local completion_dir="${HOME}/.local/share/zsh/site-functions"
    local completion_file="${completion_dir}/_claude-ctx"

    # Create directory if it doesn't exist
    mkdir -p "${completion_dir}"

    # Generate completion script
    register-python-argcomplete --shell zsh claude-ctx > "${completion_file}" || {
        log_error "Failed to generate zsh completions"
        return 1
    }

    log_success "Zsh completions installed to ${completion_file}"

    # Check if directory is in fpath
    if [[ ":${FPATH}:" != *":${completion_dir}:"* ]]; then
        log_info "Add this to your ~/.zshrc before compinit:"
        echo "    fpath=(${completion_dir} \$fpath)"
        echo "    autoload -Uz compinit && compinit"
    fi

    log_warn "Restart your shell or run: exec zsh"
}

install_fish_completions() {
    local completion_dir="${HOME}/.config/fish/completions"
    local completion_file="${completion_dir}/claude-ctx.fish"

    # Create directory if it doesn't exist
    mkdir -p "${completion_dir}"

    # Generate completion script
    register-python-argcomplete --shell fish claude-ctx > "${completion_file}" || {
        log_error "Failed to generate fish completions"
        return 1
    }

    log_success "Fish completions installed to ${completion_file}"
    log_warn "Completions will be available in new fish shells"
}

install_manpage() {
    log_info "Generating manpages..."
    
    # Generate fresh manpages from CLI definitions
    python3 "${SCRIPT_DIR}/generate-manpages.py" || {
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
        MAN_DIR="/usr/local/share/man/man1"
    elif [[ "${OSTYPE}" == "linux-gnu"* ]]; then
        # Linux
        if [[ -d "/usr/local/man/man1" ]]; then
            MAN_DIR="/usr/local/man/man1"
        elif [[ -d "/usr/share/man/man1" ]]; then
            MAN_DIR="/usr/share/man/man1"
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
    log_info "Primary entry point: man claude-ctx"
}

verify_installation() {
    log_info "Verifying installation..."

    local all_good=true

    # Check command
    if command -v claude-ctx &> /dev/null; then
        log_success "claude-ctx command available"
        claude-ctx --help > /dev/null 2>&1 && log_success "claude-ctx runs correctly"
    else
        log_error "claude-ctx command not found"
        all_good=false
    fi

    # Check manpage
    if man -w claude-ctx &> /dev/null; then
        log_success "Manpage installed and accessible"
    else
        log_warn "Manpage not accessible via 'man claude-ctx'"
    fi

    # Check completions
    case "${SHELL_TYPE}" in
        bash)
            if [[ -f "${HOME}/.local/share/bash-completion/completions/claude-ctx" ]]; then
                log_success "Bash completions installed"
            fi
            ;;
        zsh)
            if [[ -f "${HOME}/.local/share/zsh/site-functions/_claude-ctx" ]]; then
                log_success "Zsh completions installed"
            fi
            ;;
        fish)
            if [[ -f "${HOME}/.config/fish/completions/claude-ctx.fish" ]]; then
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
        echo "  2. Try: claude-ctx status"
        echo "  3. View docs: man claude-ctx"
        echo "  4. Test completions: claude-ctx <TAB><TAB>"
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
