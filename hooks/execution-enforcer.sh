#!/usr/bin/env bash
# Minimal enforcement hook - reinforces execution-law.md
# Less is more. Claude ignores walls of text.

set -euo pipefail

user_prompt="${CLAUDE_HOOK_PROMPT:-${CLAUDE_USER_PROMPT:-}}"

# Only trigger on implementation-like prompts
if ! echo "$user_prompt" | grep -qiE "(implement|build|create|add|write|code|fix|refactor|feature|test)"; then
    exit 0
fi

# Short. Direct. Authoritative.
cat <<'EOF'

⚡ EXECUTION MODE

1. PARALLEL: Run independent work simultaneously
2. DISK: Write to files, verify with `ls -la`
3. REVIEW: Run `cortex review` before completion
4. SKILLS: If review lists skills, `cat` them first
5. PROOF: Show actual test output

EOF

exit 0
