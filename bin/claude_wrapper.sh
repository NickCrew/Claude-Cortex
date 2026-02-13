#!/usr/bin/env zsh
# Simple, elegant terminal title management for Claude

# Set terminal title
_set_title() { 
    print -Pn "\e]2;$1\a" 
}

# Claude wrapper with custom terminal title
cly() {
    local folder=${PWD:t}  # Just the current folder name
    
    # Set title to show we're running Claude
    _set_title "$folder — Claude"
    
    # Start a background process to continuously reset the title
    # (prevents Claude from changing it)
    (
        while true; do
            _set_title "$folder — Claude"
            sleep 0.5
        done
    ) &
    local title_pid=$!
    
    # Run Claude with dangerous permissions
    "$HOME/.local/bin/claude" --dangerously-skip-permissions "$@"
    local exit_code=$?
    
    # Kill the background title setter
    kill $title_pid 2>/dev/null
    wait $title_pid 2>/dev/null  # Clean up zombie process
    
    # Restore normal title
    _set_title "%~"
    
    # Return the original exit code
    return $exit_code
}

# Update terminal title before each prompt (using proper ZSH hooks)
_claude_precmd() {
    _set_title "%~"
}

# Add our precmd function to the array (doesn't overwrite existing hooks)
if [[ -z ${precmd_functions[(r)_claude_precmd]} ]]; then
    precmd_functions+=(_claude_precmd)
fi
