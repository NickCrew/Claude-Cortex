#!/usr/bin/env bash
# Run type checks after Rust/TypeScript file edits
#
# Hook event: PostToolUse
# Matcher: Edit, Write, Create (file operations)
# Catches type errors immediately before they compound.

set -euo pipefail

file_path="${CLAUDE_FILE_PATH:-}"

# --- Rust files ---
if [[ "$file_path" =~ \.rs$ ]]; then
    # Find the Cargo.toml directory (walk up from file)
    dir=$(dirname "$file_path")
    while [[ "$dir" != "/" ]]; do
        if [[ -f "$dir/Cargo.toml" ]]; then
            cd "$dir"
            break
        fi
        dir=$(dirname "$dir")
    done

    # If Cargo.toml found, run check
    if [[ -f "Cargo.toml" ]]; then
        echo "--- cargo check (post-edit) ---"
        cargo check --message-format=short 2>&1 | head -20 || true
    fi
    exit 0
fi

# --- TypeScript files ---
if [[ "$file_path" =~ \.(ts|tsx)$ ]]; then
    # Find the tsconfig.json or package.json directory (walk up from file)
    dir=$(dirname "$file_path")
    while [[ "$dir" != "/" ]]; do
        if [[ -f "$dir/tsconfig.json" ]]; then
            cd "$dir"
            break
        fi
        dir=$(dirname "$dir")
    done

    # If tsconfig.json found, run tsc
    if [[ -f "tsconfig.json" ]]; then
        echo "--- tsc --noEmit (post-edit) ---"
        npx tsc --noEmit --pretty 2>&1 | head -20 || true
    fi
    exit 0
fi

# Not a recognized file type
exit 0
