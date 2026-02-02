#!/usr/bin/env bash
# Auto-activate reviewers on implementation prompts
#
# Hook event: UserPromptSubmit
# Silently activates context-appropriate agents without injecting instructions.

set -euo pipefail

prompt="${CLAUDE_HOOK_PROMPT:-}"

# Only trigger on implementation-like prompts
if ! echo "$prompt" | grep -qiE "(implement|build|create|add|write|code|fix|refactor|feature)"; then
    exit 0
fi

# Run AI auto-activate (silent, non-blocking)
cortex ai auto-activate >/dev/null 2>&1 || true

exit 0
